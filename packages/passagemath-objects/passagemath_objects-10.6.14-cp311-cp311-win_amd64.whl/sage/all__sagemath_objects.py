# sage_setup: distribution = sagemath-objects
# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'passagemath_objects.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch
import os
import sys
import operator
import math

import warnings

# TODO: More to be moved from all.py

# This import also sets up the interrupt handler
from cysignals.signals import (AlarmInterrupt, SignalError,
                               sig_on_reset as sig_on_count)

from time import sleep

from sage.misc.all__sagemath_objects import *
from sage.structure.all import *
from sage.arith.power import generic_power as power
from sage.categories.all__sagemath_objects import *

from sage.cpython.all import *

if sys.platform != 'win32':
    from cysignals.alarm import alarm, cancel_alarm

from copy import copy, deepcopy

true = True
false = False


# For doctesting. These are overwritten later

Integer = int
RealNumber = float
