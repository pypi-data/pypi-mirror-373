import os
import setuptools

_version = '0.00.00'
my_dir = os.path.dirname(os.path.realpath(__file__))
my_version_file = my_dir + "/VERSION"
if os.path.exists(my_version_file):
    with open(my_version_file, "rt") as input_file:
        _version=input_file.readline().strip()
else:
    pkg_info_files = (my_dir + "/PKG-INFO", my_dir + "/ifdef.egg-info/PKG-INFO")
    for pkg_info_file in pkg_info_files:
        if os.path.exists(pkg_info_file):
            with open(pkg_info_file) as input_file:
                pkg_info=dict([line.strip().split(": ",1) for line in input_file.readlines()])    
                if "Version" in pkg_info:
                    _version = pkg_info.get("Version")
                else:
                    raise ModuleNotFoundError("Version is not found in " + pkg_info_file + ":\n" + str(pkg_info))
            break
    else:
        full_list_of_dirs_where_we_search = [my_version_file]
        full_list_of_dirs_where_we_search.extend(pkg_info_files)
        print("Impossible to find and load any of below files: %s" % (str(full_list_of_dirs_where_we_search)))
print(_version)

with open("requirements.txt", "rt") as input_file:
    install_requires = input_file.readlines()

setuptools.setup(
    name = "ifdef",
    version = _version,
    description = "A ifdef/else/endif macro preprocessor for standalone python scripts and importable modules",
    author = "py552",
    author_email = "pythonist552@gmail.com",
    long_description = "A ifdef/else/endif macro preprocessor for standalone python scripts and importable modules",
    long_description_content_type="text/markdown",    
    url = "https://github.com/py552/ifdef/",
    license = 'ASL',
    packages = setuptools.find_packages(),
    platforms = ["any"],
    classifiers = [
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    test_suite = "tests",
    python_requires = ">=3.7",
    install_requires = install_requires,
    zip_safe = False,
)
