# import sys
# import os
# import pkgutil
import ast
from .global_vars import do_not_wrap_modules


class ProcessedModuleIsLoaded(ImportWarning):
    def __init__(self, name, loaded):
        self.name = name
        self.loaded = loaded


class ImportWrapper(ast.NodeTransformer):
    def __init__(self):
        super().__init__()

    def construct_try_except(self, node, except_body):
        """ Construct try-except block """
        return ast.Try(
            body=[node],
            handlers=[
                ast.ExceptHandler(
                    type=ast.Name(id="ProcessedModuleIsLoaded", ctx=ast.Load()),
                    name="_module",
                    body=except_body
                )
            ],
            orelse=[],
            finalbody=[]
        )

    def import_module_except_block(self):
        """
        Generate except block:
            ```
            except ProcessedModuleIsLoaded as _module:
                globals()[_module.name] = _module.loaded
            ```
        for:
            ```
            try:
                import module
            ```
        """

        return [
            ast.Assign(
                targets=[
                    ast.Subscript(
                        value=ast.Call(
                            func=ast.Name(id="globals", ctx=ast.Load()),
                            args=[],
                            keywords=[]
                        ),
                        slice=ast.Attribute(
                            value=ast.Name(id="_module", ctx=ast.Load()),
                            attr="name",
                            ctx=ast.Load()
                        ),
                        ctx=ast.Store()
                    )
                ],
                value=ast.Attribute(
                    value=ast.Name(id="_module", ctx=ast.Load()),
                    attr="loaded",
                    ctx=ast.Load()
                )
            )
        ]

    def visit_Import(self, node):
        if all(
                node_names.name in do_not_wrap_modules
                for node_names in node.names
        ):
            # known modules, so they have not code manipulation inside, so wrapping is not required
            return node

        # split `import module1, module2` into `import module1` and `import module2`
        # and wrap each of them if it is not standard module
        new_nodes = []
        for alias in node.names:
            new_node = ast.Import(names=[alias])
            if alias.name not in do_not_wrap_modules:
                new_node = self.construct_try_except(new_node, self.import_module_except_block())
            new_nodes.append(new_node)
        return new_nodes


    ###########################################################

    def from_module_import_star_except_block(self):
        """
        Generate except block:
            ```
            except ProcessedModuleIsLoaded as _module:
                for _name in dir(_module.loaded):
                    if not _name.startswith('__'):
                        globals()[_name] = getattr(_module.loaded, _name)
            ```
        for:
            ```
            try:
                from module import *
            ```
        """
        return [
            ast.For(
                target=ast.Name(id="_name", ctx=ast.Store()),
                iter=ast.Call(
                    func=ast.Name(id="dir", ctx=ast.Load()),
                    args=[
                        ast.Attribute(
                            value=ast.Name(id="_module", ctx=ast.Load()),
                            attr="loaded",
                            ctx=ast.Load()
                        )
                    ],
                    keywords=[]
                ),
                body=[
                    ast.If(
                        test=ast.UnaryOp(
                            op=ast.Not(),
                            operand=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="_name", ctx=ast.Load()),
                                    attr="startswith",
                                    ctx=ast.Load()
                                ),
                                args=[ast.Constant(value="__")],
                                keywords=[]
                            )
                        ),
                        body=[
                            ast.Assign(
                                targets=[ast.Subscript(
                                    value=ast.Call(
                                        func=ast.Name(id="globals", ctx=ast.Load()),
                                        args=[],
                                        keywords=[]
                                    ),
                                    slice=ast.Name(id="_name", ctx=ast.Load()),
                                    ctx=ast.Store()
                                )],
                                value=ast.Call(
                                    func=ast.Name(id="getattr", ctx=ast.Load()),
                                    args=[
                                        ast.Attribute(
                                            value=ast.Name(id="_module", ctx=ast.Load()),
                                            attr="loaded",
                                            ctx=ast.Load()
                                        ),
                                        ast.Name(id="_name", ctx=ast.Load())
                                    ],
                                    keywords=[]
                                )
                            )
                        ],
                        orelse=[]
                    )
                ],
                orelse=[]
            )
        ]

    def from_module_import_names_except_block(self, node):
        """
        Generate except block:
            ```
            except ProcessedModuleIsLoaded as _module:
                for _name, _asname in [('name1', 'name1'), ('name2', 'name2'), ('name3', 'name03')]:
                    if hasattr(_module.loaded, _name):
                        globals()[_asname] = getattr(_module.loaded, _name)
            ```
        for:
            ```
            try:
                from module import name1,name2,name3 as name03
            ```
        """
        pairs = [(alias.name, alias.asname or alias.name) for alias in node.names]
        # pairs = [(alias.name, alias.asname if alias.asname is not None else alias.name) for alias in node.names]
        return [
            ast.For(
                target=ast.Tuple(
                    elts=[
                        ast.Name(id="_name", ctx=ast.Store()),
                        ast.Name(id="_asname", ctx=ast.Store())
                    ],
                    ctx=ast.Store()
                ),
                iter=ast.List(
                    elts=[
                        ast.Tuple(elts=[ast.Constant(value=src), ast.Constant(value=dst)])
                        for src, dst in pairs
                    ],
                    ctx=ast.Load()
                ),
                body=[
                    ast.If(
                        test=ast.Call(
                            func=ast.Name(id="hasattr", ctx=ast.Load()),
                            args=[
                                ast.Attribute(
                                    value=ast.Name(
                                        id="_module",
                                        ctx=ast.Load()
                                    ),
                                    attr="loaded",
                                    ctx=ast.Load()
                                ),
                                ast.Name(id="_name", ctx=ast.Load())
                            ],
                            keywords=[]
                        ),
                        body=[
                            ast.Assign(
                                targets=[
                                    ast.Subscript(
                                        value=ast.Call(
                                            func=ast.Name(id="globals", ctx=ast.Load()),
                                            args=[],
                                            keywords=[]
                                        ),
                                        slice=ast.Name(id="_asname", ctx=ast.Load()),
                                        ctx=ast.Store()
                                    )
                                ],
                                value=ast.Call(
                                    func=ast.Name(id="getattr", ctx=ast.Load()),
                                    args=[
                                        ast.Attribute(
                                            value=ast.Name(id="_module", ctx=ast.Load()),
                                            attr="loaded",
                                            ctx=ast.Load()
                                        ),
                                        ast.Name(id="_name", ctx=ast.Load())
                                    ],
                                    keywords=[]
                                )
                            )
                        ],
                        orelse=[]
                    )
                ],
                orelse=[]
            )
        ]

    def visit_ImportFrom(self, node):
        if node.names[0].name in do_not_wrap_modules:
            # known modules, so they have not code manipulation inside, so wrapping is not required
            return node

        if node.names[0].name == "*":
            # Wrap 'from module import *' with try-except
            return self.construct_try_except(node, self.from_module_import_star_except_block())
        # Wrap 'from module import name1,name2,name3 as name03' with try-except
        return self.construct_try_except(node, self.from_module_import_names_except_block(node))

