# sage_setup: distribution = sagemath-graphs
# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'passagemath_graphs.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch
r"""
Top level of the distribution package sagemath-graphs

This distribution makes the following feature available::

    sage: from sage.features.sagemath import *
    sage: sage__graphs().is_present()
    FeatureTestResult('sage.graphs', True)
"""

from .all__sagemath_categories import *

try:  # extra
    from sage.all__sagemath_gap import *
except ImportError:
    pass

try:  # extra
    from sage.all__sagemath_modules import *
except ImportError:
    pass

try:  # extra
    from sage.all__sagemath_polyhedra import *
except ImportError:
    pass

from sage.graphs.all import *

from sage.topology.all import *

from sage.combinat.all__sagemath_graphs import *

from sage.databases.all__sagemath_graphs import *

from sage.sandpiles.all import *

from sage.knots.all import *
