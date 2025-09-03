import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

print(f"1.1) __name__='{__name__}' __file__='{__file__}'")

from ifdef import preprocessor
preprocessor.define("DEBUG")
preprocessor.parse(__name__, __file__)

import os, sys

print(f"1.2) __name__='{__name__}' __file__='{__file__}'")

try:
    import _test_ifdef2
except Exception as ex:
    pass

def proc1():
    # #define DEBUG
    #ifdef DEBUG
    #D# print("DEBUG1.1")
    #D# print("DEBUG1.2")
    #ifdef DEBUG
    #D# print("DEBUG1.3")
    #ifndef DEBUG2
    #D# print("DEBUG1.4")
    #endif
    #endif
    #else
    print("RELEASE1.1")
    print("RELEASE1.2")
    #endif
    _test_ifdef2.proc2()



print(f"1.3) __name__='{__name__}' __file__='{__file__}'")

def main():
    print(f"1.4) __name__='{__name__}' __file__='{__file__}'")
    proc1()

if __name__ == '__main__':
    main()
    print("Mission acomplished")

