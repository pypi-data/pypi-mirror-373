# sage_setup: distribution = sagemath-categories
# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'passagemath_categories.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch
from sage.all__sagemath_objects import *

try:
    # For doctesting
    from sage.all__sagemath_repl import *
except ImportError:
    pass

from sage.categories.all import *
from sage.rings.all__sagemath_categories import *
from sage.sets.all import *
from sage.combinat.all__sagemath_categories import *
from sage.arith.all import *
from sage.data_structures.all import *
from sage.databases.all__sagemath_categories import *
from sage.ext.all__sagemath_categories import *
from sage.groups.all__sagemath_categories import *
from sage.interfaces.all import *
from sage.misc.all__sagemath_categories import *
from sage.typeset.all import *
from sage.schemes.all__sagemath_categories import *

from sage.calculus.all__sagemath_categories import *
from sage.functions.all import *

from sage.parallel.all import *
