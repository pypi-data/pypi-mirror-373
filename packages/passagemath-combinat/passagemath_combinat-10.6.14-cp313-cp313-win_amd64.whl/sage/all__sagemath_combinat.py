# sage_setup: distribution = sagemath-combinat
# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'passagemath_combinat.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch
r"""
Top level of the distribution package sagemath-combinat

This distribution makes the following features available::

    sage: from sage.features.sagemath import *
    sage: sage__combinat().is_present()
    FeatureTestResult('sage.combinat', True)
    sage: sage__sat().is_present()
    FeatureTestResult('sage.sat', True)
"""

from .all__sagemath_categories import *

try:  # extra
    from sage.all__sagemath_graphs import *
except ImportError:
    pass

from sage.algebras.all__sagemath_combinat import *
from sage.combinat.all__sagemath_combinat import *
from sage.databases.all__sagemath_combinat import *
from sage.dynamics.all__sagemath_combinat import *
from sage.libs.all__sagemath_combinat import *
from sage.rings.all__sagemath_combinat import *
from sage.monoids.all import *
from sage.games.all import *
from sage.sat.all import *

try:  # extra, goes last so that the correct RR definition wins
    from sage.all__sagemath_modules import *
except ImportError:
    pass
