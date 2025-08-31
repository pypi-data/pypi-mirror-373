# -*- coding: utf-8 -*-

import warnings
from math import fabs

from numpy import fmax


def require(condition, exception, msg=""):
    if not condition:
        raise exception(msg)
    return 0


def ensureRaise(exception, msg=""):
    raise exception(msg)


def warning(condition, warn_type, msg=""):
    if not condition:
        warnings.warn(msg, warn_type)
    return 0


def isClose(a, b=0., rel_tol=1e-09, abs_tol=1e-12):
    return fabs(a - b) <= fmax(rel_tol * fmax(fabs(a), fabs(b)), abs_tol)
