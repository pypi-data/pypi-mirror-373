import sys

if hasattr(sys, "stdlib_module_names"):
    # for python >= 3.10
    stdlib_modules = sys.stdlib_module_names
else:
    # for python <= 3.9
    import os
    import sysconfig

    stdlib_path = sysconfig.get_path("stdlib")      # always "C:\Python37-32\Lib
    stdlib_modules = {
        name.split(".")[0]
        for name in os.listdir(stdlib_path)
        if name.endswith(".py") \
        or (
            os.path.isdir(os.path.join(stdlib_path, name))
            and os.path.exists(os.path.join(stdlib_path, name, "__init__.py"))
        )
    }
    stdlib_modules |= set(sys.builtin_module_names) # builtin modules (C-modules)

do_not_wrap_modules = stdlib_modules | {__name__.split('.')[0]}
