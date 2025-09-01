# cython: binding=True, embedsignature=True, c_string_type=unicode, c_string_encoding=utf8

from qlat_utils.all cimport *
from . cimport everything as cc

from cpython cimport Py_buffer
from cpython.buffer cimport PyBUF_FORMAT

import cqlat as c
import qlat_utils as q
import numpy as np

obtained_lock_history_list = []

@q.timer
def release_lock():
    cc.release_lock()

@q.timer
def obtain_lock(const cc.std_string& path):
    b = cc.obtain_lock(path)
    if b:
        obtained_lock_history_list.append(path)
    return b

def qquit(const cc.std_string& msg):
    """
    clean python cache and then call cc.qquit(msg) (which clear all the C++ level cache and then quit)
    """
    q.clean_cache()
    return cc.qquit(msg)

@q.timer
def check_time_limit(budget=None):
    if budget is None:
        budget = q.get_time_budget()
    return cc.check_time_limit(budget)

@q.timer
def check_stop(fn="stop.txt"):
    return cc.check_stop(fn)
