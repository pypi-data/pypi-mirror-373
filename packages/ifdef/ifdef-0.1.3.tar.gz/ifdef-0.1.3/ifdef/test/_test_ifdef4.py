import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

print(f"4.1) __name__=='{__name__}' __file__=='{__file__}'")

from ifdef import preprocessor
preprocessor.define("DEBUG")
preprocessor.parse(__name__, __file__)



print(f"4.2) __name__=='{__name__}' __file__=='{__file__}'")






def proc4():
    #ifdef DEBUG
    #D# print("DEBUG4.1")
    #D# print("DEBUG4.2")
    #else
    print("RELEASE4.1")
    print("RELEASE4.2")
    #endif
    pass










print(f"4.3) __name__='{__name__}' __file__='{__file__}'")

def main():
    print(f"4.4) __name__='{__name__}' __file__='{__file__}'")
    proc4()

if __name__ == '__main__':
    main()
    print("Mission acomplished")

