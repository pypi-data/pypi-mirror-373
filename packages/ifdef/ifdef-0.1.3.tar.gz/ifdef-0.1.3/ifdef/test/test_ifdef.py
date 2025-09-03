import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

from ifdef import ProcessedModuleIsLoaded
try:
    import _test_ifdef1
except ProcessedModuleIsLoaded as _module:
    globals()[_module.name] = _module.loaded

def test_main():
    _test_ifdef1.main()

if __name__ == '__main__':
    test_main()
    print("Mission acomplished")

