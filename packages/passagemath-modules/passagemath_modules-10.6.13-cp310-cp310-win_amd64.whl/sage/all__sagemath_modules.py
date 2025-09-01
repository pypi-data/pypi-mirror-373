# sage_setup: distribution = sagemath-modules
# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'passagemath_modules.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch
r"""
Top level of the distribution package sagemath-modules

This distribution makes the following features available::

    sage: from sage.features.sagemath import *
    sage: sage__modules().is_present()
    FeatureTestResult('sage.modules', True)
    sage: sage__rings__real_mpfr().is_present()
    FeatureTestResult('sage.rings.real_mpfr', True)
    sage: sage__rings__complex_double().is_present()
    FeatureTestResult('sage.rings.complex_double', True)
"""

from .all__sagemath_categories import *

try:  # extra
    from sage.all__sagemath_linbox import *
except ImportError:
    pass

try:  # extra
    from sage.all__sagemath_flint import *
except ImportError:
    pass

try:  # extra
    from sage.all__sagemath_ntl import *
except ImportError:
    pass

try:  # extra
    from sage.all__sagemath_pari import *
except ImportError:
    pass

from sage.misc.all__sagemath_modules import *
from sage.rings.all__sagemath_modules import *
from sage.combinat.all__sagemath_modules import *
from sage.algebras.all__sagemath_modules import *
from sage.modules.all import *
from sage.matrix.all import *
from sage.groups.all__sagemath_modules import *
from sage.geometry.all__sagemath_modules import *
from sage.homology.all__sagemath_modules import *
from sage.tensor.all import *
from sage.matroids.all import *
from sage.quadratic_forms.all__sagemath_modules import *
from sage.coding.all import *
from sage.crypto.all import *
from sage.stats.all import *
from sage.probability.all import *
from sage.calculus.all__sagemath_modules import *
from sage.numerical.all__sagemath_modules import *

import sage.crypto.mq as mq
import sage.stats.all as stats

true = True
false = False
