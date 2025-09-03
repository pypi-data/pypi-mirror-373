import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

print(f"3.1) __name__=='{__name__}' __file__=='{__file__}'")

from ifdef import preprocessor
preprocessor.define("DEBUG")
preprocessor.parse(__name__, __file__)



print(f"3.2) __name__=='{__name__}' __file__=='{__file__}'")

from _test_ifdef4 import proc4, proc4 as proc004




def proc3():
    #ifdef DEBUG
    #D# print("DEBUG3.1")
    #D# print("DEBUG3.2")
    #else
    print("RELEASE3.1")
    print("RELEASE3.2")
    #endif
    proc4()
    proc004()









print(f"3.3) __name__='{__name__}' __file__='{__file__}'")

def main():
    print(f"3.4) __name__='{__name__}' __file__='{__file__}'")
    proc3()

if __name__ == '__main__':
    main()
    print("Mission acomplished")

