# coding: utf-8
# cython: boundscheck=False, cdivision=True, wraparound=False, initializedcheck=False, language_level=3str
import numpy as np
from cython.parallel import prange
from scipy import sparse
from multiprocessing import cpu_count

cdef int ncpu = cpu_count()

def spmul(sp, d):
    result = np.zeros(sp.data.shape[0], dtype='f4')
    spmul_core(sp.indices, sp.data, d, result)
    return sparse.csc_matrix((result, sp.indices, sp.indptr), shape=sp.shape)

def spmul_core(int[:] indices, float[:] data, float[:] vdata, float[:] result_view):
    cdef int i
    for i in prange(result_view.shape[0], nogil=True, num_threads=ncpu):
        result_view[i] = data[i]*vdata[indices[i]]
