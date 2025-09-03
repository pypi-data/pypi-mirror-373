import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

from ifdef import ProcessedModuleIsLoaded

try:
    from _test_ifdef1 import main as main1
except ProcessedModuleIsLoaded as _module:
    for _name, _asname in [('main', 'main1')]:
        if hasattr(_module.loaded, _name):
            globals()[_asname] = getattr(_module.loaded, _name)
main1()

try:
    from _test_ifdef2 import main as main2
except ProcessedModuleIsLoaded as _module:
    for _name, _asname in [('main', 'main2')]:
        if hasattr(_module.loaded, _name):
            globals()[_asname] = getattr(_module.loaded, _name)
main2()

try:
    from _test_ifdef3 import main as main3
except ProcessedModuleIsLoaded as _module:
    for _name, _asname in [('main', 'main3')]:
        if hasattr(_module.loaded, _name):
            globals()[_asname] = getattr(_module.loaded, _name)
main3()

try:
    from _test_ifdef4 import main as main4
except ProcessedModuleIsLoaded as _module:
    for _name, _asname in [('main', 'main4')]:
        if hasattr(_module.loaded, _name):
            globals()[_asname] = getattr(_module.loaded, _name)
main4()

