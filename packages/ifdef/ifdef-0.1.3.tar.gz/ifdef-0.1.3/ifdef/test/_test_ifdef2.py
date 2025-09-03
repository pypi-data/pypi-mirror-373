import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

print(f"2.1) __name__='{__name__}' __file__='{__file__}'")

from ifdef import preprocessor
preprocessor.define("DEBUG")
preprocessor.parse(__name__, __file__)



print(f"2.2) __name__='{__name__}' __file__='{__file__}'")

from _test_ifdef3 import *




def proc2():
    #ifdef DEBUG
    #D# print("DEBUG2.1")
    #D# print("DEBUG2.2")
    #else
    print("RELEASE2.1")
    print("RELEASE2.2")
    #endif
    proc3()










print(f"2.3) __name__='{__name__}' __file__='{__file__}'")

def main():
    print(f"2.4) __name__='{__name__}' __file__='{__file__}'")
    proc2()

if __name__ == '__main__':
    main()
    print("Mission acomplished")

