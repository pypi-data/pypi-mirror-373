# https://github.com/py552/ifdef
__author__ = 'py552'
# based on https://github.com/interpreters/pypreprocessor
__coauthor__ = 'Hendi O L, Epikem, Laurent Pinson, Evan Plaice, rherault-pro, tcumby, ThomasZecha, elrandira'
__version__ = '0.1.2'

import sys
import os
import types
try:
    # for python >= 3.11
    from collections.abc import Sequence as collections__Sequence
except ImportError:
    # for python <= 3.10
    from collections import Sequence as collections__Sequence

import re
import typing

import ast
if hasattr(ast, "unparse"):
    ast_unparse = lambda node: ast.unparse(node)
else:
    # for python <= 3.8
    import astor
    ast_unparse = lambda node: astor.to_source(node).strip()

    def patched_visit_alias(self, node):
        self.write(node.name)
        self.conditional_write(' as ', getattr(node, "asname", None)) # Safe access to `asname`. Original: self.conditional_write(' as ', node.asname)
    # Replace method with patched_visit_alias
    astor.code_gen.SourceGenerator.visit_alias = patched_visit_alias  # # # astor.code_gen.CodeGenerator.visit_alias = patched_visit_alias


from .import_wrapper import ImportWrapper, ProcessedModuleIsLoaded


class Preprocessor:
    __defines = {}
    __delete_lines_containing = set()

    def __init__(
        self,
        input_file_path=sys.argv[0],
        output_file_path='',
        defines={},
        remove_meta=False,
        save=False,
        quiet=False,
        input_encoding=sys.stdin.encoding,
        output_encoding=sys.stdout.encoding,
        delete_lines_containing=set()
    ):
        # public variables
        if isinstance(defines, collections__Sequence):
            for x in defines:
                self.define(*x.split(':'))
        else:
            for x,y in defines.items():
                self.define(x,y)

        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.remove_meta = remove_meta
        self.save = save
        self.quiet = quiet
        self.input_encoding = input_encoding
        self.output_encoding = output_encoding
        self.delete_lines_containing = delete_lines_containing

        # private variables
        self.__reset_internal()

    @property
    def delete_lines_containing(self):
        return self.__delete_lines_containing
    @delete_lines_containing.setter
    def delete_lines_containing(self, delete_lines_containing: set):
        self.__delete_lines_containing = delete_lines_containing

    def __reset_internal(self):
        self.__linenum = 0
        self.__excludeblock = False
        # contains the evaluated if conditions
        # due to the introduction of #elif, elements of __ifblocks are duos of boolean
        # the 1st is the evaluation of the current #if or #elif or #else
        # the 2nd indicates if at least one #if or #elif was True in the whole #if/#endif block
        self.__ifblocks = []
        # contains the if conditions
        self.__ifconditions = []

    def define(self, name, val=True):
        """
            Adds variable definition to the store as expected from a #define directive.
            The directive can contains no value as it would be tested with a #ifdef directive or
            with a value for an evaluation as in an #if directive.

        :params
            name (str): definition name

            val (str): definition value when it exists. Default is None
        """
        # try conversion for number else evaluate() might fail
        try:
            val = int(val)
        except:
            # assume val is string
            pass
        self.__defines[name]=val

    def undefine(self, define):
        """
            Removes variable definition from store as expected from an #undef directive

        :params
            define (str): definition name

        """
        self.__defines.pop(define, None)

    def __is_defined(self, define):
        """
            Checks variable is defined as used in #ifdef, #ifnotdef & #elseif directives

        :params
            define (str): definition name

        """
        return define in self.__defines

    def __evaluate_if(self, line: str) -> bool:
        """
            Evaluate the content of a #if, #elseif, #elif directive

        :params
            line (str): definition name

        """
        try:
            # line = line.replace('&&', 'and').replace('||', 'or').replace('!','not ') # replace C-style bool format by Python's
            return eval(line, self.__defines) or False
        except BaseException as e:
            print(str(e))
            self.exit_error('#if')

    def __validate_ifs(self):
        """
            Evaluate if the successive #ifs block are validated for the current position

        :return
            ifs (bool): True if all ifs condition are validated

        """
        # no ifs mean we pass else check all ifs are True
        return not self.__ifblocks or all(x[0] for x in self.__ifblocks)

    def __is_directive(
        self,
        line: str,
        directive: typing.Union[str, list, tuple],
        *possible_elements
    ) -> bool:
        """
            Checks the `line` is a `directive` and , if `possible_elements` is provided, checks its number of
            elements is amongst the list of allowed `possible_elements`

        :params:
            line (str): line to check

            directive (str): directive to be found in the `line`

            *possible_elements (int): list of allowed number of elements to compose the directive. Can be empty

        """
        if isinstance(directive, str):
            directive = (directive,) # convert to tuple

        line_splitted = line.split()
        if next((_directive for _directive in directive if line_splitted[0] == _directive), None):
            if possible_elements and len(line_splitted) not in possible_elements:
                self.exit_error(_directive)
            return True
        return False


    def lexer(self, line: str) -> int:
        """
            Analyse the `line`. This method attempts to find a known directive and, when found, to
            understand it and to perform appropriate action.

        :params
            line (str): line of code to analyse

        :return
            exclude: should the line be excluded in the final output?
                0   == normal line -- leave as is
                100 == include by condition
                500 == exclude by condition
                599 == exclude by #exclude
                900 == metadata: line is directive #ifdef/#else/#endif and etc
                999 == metadata: line is directive preprocessor.parse(..)

        """
        line = line.strip()

        if not (self.__ifblocks or self.__excludeblock) and line.startswith("preprocessor.parse("):
            return 999

        transform = 0
        if self.__excludeblock:
            # we are in an exclude block
            # elif transform >= 500:  # excluded blocks by condition
            transform = 599
        elif not self.__ifblocks:
            # leave as is, possible will be >= 900
            # if transform >= 900:    # preprocessor.parse(..)/#define/#ifdef and etc
            transform = 0
        elif self.__validate_ifs():
            # elif transform >= 100:  # included blocks by condition
            transform = 100
        else:
            # ifs are not validated
            # elif transform >= 500:  # excluded blocks by condition
            transform = 500


        if not line.startswith('#'): #No directive
            if line.startswith(tuple(self.delete_lines_containing)):
                transform = 555 # delete_lines_containing
            return transform


        if self.__is_directive(line, '#define', 2,3):
            self.define(*line.split()[1:])

        elif self.__is_directive(line, '#undef', 2):
            self.undefine(line.split()[1])

        elif self.__is_directive(line, '#exclude', 1):
            self.__excludeblock = True

        elif self.__is_directive(line, '#endexclude', 1):
            self.__excludeblock = False

        # #ifnotdef sounds better than #ifdefnot..
        elif self.__is_directive(line, ('#ifdefnot', '#ifnotdef', '#ifndef'), 2):
            _check = not self.__is_defined(line.split()[1])
            self.__ifblocks.append([ _check, _check])
            self.__ifconditions.append(line.split()[1])

        elif self.__is_directive(line, '#ifdef', 2):
            _check = self.__is_defined(line.split()[1])
            self.__ifblocks.append([ _check, _check])
            self.__ifconditions.append(line.split()[1])

        elif self.__is_directive(line, '#if'):
            _check = self.__evaluate_if(' '.join(line.split()[1:]))
            self.__ifblocks.append([ _check, _check])
            self.__ifconditions.append(' '.join(line.split()[1:]))

        # since in version <=0.7.7, it didn't handle #if it should be #elseifdef instead.
        # kept elseif with 2 elements for retro-compatibility (equivalent to #elseifdef).
        elif self.__is_directive(line, '#elseif') or \
        self.__is_directive(line, '#elif'):
            _cur, _whole = self.__ifblocks[-1]
            if len(line.split()) == 2:
                #old behaviour
                _check = self.__is_defined(line.split()[1])
            else:
                #new behaviour
                _check = self.__evaluate_if(' '.join(line.split()[1:]))
            self.__ifblocks[-1]=[ not _whole and _check, _whole or _check ]
            self.__ifconditions[-1]=' '.join(line.split()[1:])

        elif self.__is_directive(line, '#elseifdef', 2):
            _cur, _whole = self.__ifblocks[-1]
            _check = self.__is_defined(line.split()[1])
            self.__ifblocks[-1]=[ not _whole and _check, _whole or _check ]
            self.__ifconditions[-1]=' '.join(line.split()[1:])

        elif self.__is_directive(line, '#else', 1):
            _cur, _whole = self.__ifblocks[-1]
            self.__ifblocks[-1] = [not _whole, not _whole] #opposite of the whole if/elif block

        elif self.__is_directive(line, '#endififdef', 2):
            # do endif
            if len(self.__ifconditions) >= 1:
                self.__ifblocks.pop(-1)
                self.__ifconditions.pop(-1)
            # do ifdef
            self.__ifblocks.append(self.__is_defined(line.split()[1]))
            self.__ifconditions.append(line.split()[1])

        elif self.__is_directive(line, '#endifall', 1):
            self.__ifblocks = []
            self.__ifconditions = []

        # handle #endif and #endif<numb> directives
        elif self.__is_directive(line, '#endif', 1):
            try:
                number = int(line[6:])
            except ValueError as VE:
                number = 1

            try:
                while number:
                    self.__ifblocks.pop(-1)
                    self.__ifconditions.pop(-1)
                    number-=1
            except:
                if not self.quiet:
                    print('Warning trying to remove more blocks than present', self.input_file_path, self.__linenum)

        elif self.__is_directive(line, '#error'):
            if self.__validate_ifs():
                print('File: "' + self.input_file_path + '", line ' + str(self.__linenum + 1))
                print('Error directive reached')
                sys.exit(1)

        else:
            # starts with '#' but not recognized like command, so
            # 0   == normal line -- leave as is
            return transform

        # 900 == metadata: line is directive #ifdef/#else/#endif and etc
        return 900

    # error handling
    def exit_error(self, directive):
        """
            Prints error and interrupts execution

        :params
            directive (str): faulty directive

        """
        print('File: "' + self.input_file_path + '", line ' + str(self.__linenum + 1))
        print('SyntaxError: Invalid ' + directive + ' directive')
        sys.exit(-1)

    def parse(self, module_name: str, file_path: str, **kwargs):
        """
            Main method:
            - reset internal counters/values
            - check & warn about deprecation
            - starts the parsing of the input file
            - warn of unclosed #ifdef blocks if any
            - trigger post-process activities
        """

        self.input_file_path = os.path.join(file_path)
        buffer_processed_module = ''
        self.__reset_internal()

        # open the input file
        try:
            with open(self.input_file_path, "rt", encoding=self.input_encoding) as input_file:
                for self.__linenum, line in enumerate(input_file):
                    transform = self.lexer(line)

                    if transform >= 900:    # preprocessor.parse(..)/#define/#ifdef and etc
                        if not self.remove_meta:
                            buffer_processed_module += "#M# " + line
                    elif transform == 555:  # delete_lines_containing
                        indent_len = len(line) - len(line.lstrip(" \t"))
                        buffer_processed_module += f"{line[:indent_len]}pass # line contains # {line[indent_len:]}"
                    elif transform >= 500:  # excluded blocks by condition
                        buffer_processed_module += "#E# " + line
                    elif transform >= 100:  # included blocks by condition
                        __sign = next(
                            (
                                __sign if __sign in line else None
                                for __sign in ("#D# ","#I# ")
                            ),
                            None
                        ) # for compatibility with python 3.7
                        if __sign:
                            buffer_processed_module += ''.join(line.split(__sign, 1))
                        else:
                            buffer_processed_module += line
                    else:
                        buffer_processed_module += line
        finally:
            if self.__ifblocks:
                error_msg = f"{len(self.__ifblocks)} unclosed Ifdefblocks in {self.input_file_path}:\n"
                for i, item in enumerate(self.__ifconditions):
                    if (item in self.__defines) != self.__ifblocks[i]:
                        cond = ' else '
                    else:
                        cond = ' if '
                    error_msg += f"Block: {item} is in condition: {cond}"
                raise SyntaxError(error_msg)

        if self.save:
            self.output_file_path = self.input_file_path + ".proce$$ed1"
            with open(self.output_file_path, "wt", encoding=self.output_encoding) as output_file:
                output_file.write(buffer_processed_module)

        ##########################################

        tree = ast.parse(buffer_processed_module)

        # Add parent references to check try
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

        transformer = ImportWrapper()
        new_tree = transformer.visit(tree)

        # add to the first line: from ifdef import ProcessedModuleIsLoaded
        new_tree.body.insert(
            0,
            ast.ImportFrom(module=__name__, names=[ast.alias(name="ProcessedModuleIsLoaded")], level=0)
        )

        ast.fix_missing_locations(new_tree)
        buffer_processed_module = ast_unparse(new_tree)

        if self.save:
            self.output_file_path = self.input_file_path + ".proce$$ed2"
            with open(self.output_file_path, "wt", encoding=self.output_encoding) as output_file:
                output_file.write(buffer_processed_module)

        ##########################################

        if module_name != '__main__':
            del sys.modules[module_name]

        loaded_module = types.ModuleType(module_name)
        loaded_module.__file__ = self.output_file_path or self.input_file_path
        compiled_processed_module = compile(buffer_processed_module, f"<{self.input_file_path}> processed by ifdef", 'exec')
        exec(compiled_processed_module, loaded_module.__dict__ )
        sys.modules[module_name] = loaded_module

        if module_name == '__main__':
            sys.exit(0)
        else:
            raise ProcessedModuleIsLoaded(module_name, loaded_module)


preprocessor = Preprocessor()
