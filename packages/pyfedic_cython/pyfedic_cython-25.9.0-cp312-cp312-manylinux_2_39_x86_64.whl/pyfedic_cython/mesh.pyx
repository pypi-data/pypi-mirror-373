# coding: utf-8
# cython: boundscheck=False, cdivision=True, wraparound=False, initializedcheck=False, language_level=3str
import numpy as np
from cython.parallel import prange, threadid
from libc.math cimport floor, ceil
from libc.stdio cimport printf, fflush, stdout
from libc.stdlib cimport malloc, free, realloc

from scipy import sparse

from openmp cimport omp_lock_t, omp_set_lock, omp_unset_lock, omp_init_lock, omp_destroy_lock

from multiprocessing import cpu_count

cdef int n_cpu = cpu_count()

def compute_N_by_type(points, nodes, cells, T, indp, indn, val, done, indni, iii, n_thread=-1):
    indni = Compute_N(points, nodes, cells, T, indp, indn, val, done, indni, iii, n_thread).get_indni()
    iii = iii+len(cells)
    return iii, indni

cdef class Compute_N:
    #
    cdef bint is_linear
    cdef double EPSILON

    cdef double[:,:] N_data, dNdr_data, dNds_data, dNdt_data, N_data_linear

    cdef int ndim, n_thread, n_nodes, order, n_nodes_linear
    cdef long dimz, dimy, dimx, startz, starty, startx
    cdef long n_points, n_cells, indni, iii

    cdef double[:,:] nodes
    cdef long[:,:] cells
    cdef double[:,:] points

    cdef int[:] indp, indn, done
    cdef float[:] val

    cdef omp_lock_t lock, lock_done

    def get_indni(self):
        return self.indni

    def __init__(self, points, nodes, cells, cell_type, int[:] indp, int[:] indn, float[:] val, int[:] done, long indni, long iii, int n_thread=-1):
        #
        self.indp = indp
        self.indn = indn
        self.val = val
        self.done = done

        self.EPSILON = cell_type.EPSILON
        self.ndim = cell_type.ndim
        self.order = cell_type.order
        self.nodes = nodes
        self.cells = cells

        if cell_type.order == 1:
            self.N_data_linear = cell_type._N_data
            self.n_nodes_linear = cell_type.n_nodes
        else:
            self.N_data_linear = cell_type._linear._N_data
            self.n_nodes_linear = cell_type._linear.n_nodes

        self.N_data = cell_type._N_data
        self.dNdr_data = cell_type._dN_data[0]
        self.dNds_data = cell_type._dN_data[1]
        if self.ndim == 3:
            self.dNdt_data = cell_type._dN_data[2]

        self.n_nodes = cell_type.n_nodes
        self.n_cells = len(cells)

        self.is_linear = cell_type.is_linear

        if n_thread < 0:
            n_thread = n_cpu

        if self.n_cells > 10:
            self.n_thread = min(n_thread, self.n_cells)
        else:
            self.n_thread = 1

        self.indni = indni
        self.iii = iii

        cdef long i_cell, i_point, zi, yi, xi
        cdef bint grid = 0

        if isinstance(points, np.ndarray):
            self.n_points = len(points)
            self.points = points
        else:
            grid = 1
            if self.ndim == 2:
                self.startz, self.starty, self.startx = (0,) + points.roi.offset
                self.dimz, self.dimy, self.dimx = (1, ) + points.roi.shape
            else:
                self.startz, self.starty, self.startx = points.roi.offset
                self.dimz, self.dimy, self.dimx = points.roi.shape
            self.n_points = self.dimx*self.dimy*self.dimz
            self.points = np.zeros((self.n_points, 3), dtype='f8')
            i_point = 0
            for zi in xrange(self.startz, self.startz+self.dimz):
                for yi in xrange(self.starty, self.starty+self.dimy):
                    for xi in xrange(self.startx, self.startx+self.dimx):
                        self.points[i_point,0] = <double> xi
                        self.points[i_point,1] = <double> yi
                        self.points[i_point,2] = <double> zi
                        i_point += 1

        omp_init_lock(&self.lock)
        omp_init_lock(&self.lock_done)

        for i_cell in prange(self.n_cells, nogil=True, num_threads=self.n_thread):
            if grid:
                self.compute_grid_thread(i_cell)
            else:
                self.compute_ugrid_thread(i_cell)

        omp_destroy_lock(&self.lock)
        omp_destroy_lock(&self.lock_done)

    cdef void compute_grid_thread(self, long i_cell) noexcept nogil:
        #
        cdef long zzmin, zzmax, yymin, yymax, xxmin, xxmax
        cdef long zi, xi, yi
        cdef long i_node = 0
        cdef long i_todo, n_todo

        xxmin = <long>  ceil(self.nodes[self.cells[i_cell,i_node],0])
        xxmax = <long> floor(self.nodes[self.cells[i_cell,i_node],0]) + 1
        yymin = <long>  ceil(self.nodes[self.cells[i_cell,i_node],1])
        yymax = <long> floor(self.nodes[self.cells[i_cell,i_node],1]) + 1
        zzmin = <long>  ceil(self.nodes[self.cells[i_cell,i_node],2])
        zzmax = <long> floor(self.nodes[self.cells[i_cell,i_node],2]) + 1

        for i_node in xrange(1, self.n_nodes):
            if xxmin > self.nodes[self.cells[i_cell,i_node],0]:
                xxmin = <long>  ceil(self.nodes[self.cells[i_cell,i_node],0])
            if xxmax < self.nodes[self.cells[i_cell,i_node],0]:
                xxmax = <long> floor(self.nodes[self.cells[i_cell,i_node],0]) + 1
            if yymin > self.nodes[self.cells[i_cell,i_node],1]:
                yymin = <long>  ceil(self.nodes[self.cells[i_cell,i_node],1])
            if yymax < self.nodes[self.cells[i_cell,i_node],1]:
                yymax = <long> floor(self.nodes[self.cells[i_cell,i_node],1]) + 1
            if zzmin > self.nodes[self.cells[i_cell,i_node],2]:
                zzmin = <long>  ceil(self.nodes[self.cells[i_cell,i_node],2])
            if zzmax < self.nodes[self.cells[i_cell,i_node],2]:
                zzmax = <long> floor(self.nodes[self.cells[i_cell,i_node],2]) + 1

        if zzmax < zzmin + 1:
            zzmax = zzmin + 1

        if yymax < yymin + 1:
            yymax = yymin + 1

        if xxmax < xxmin + 1:
            xxmax = xxmin + 1

        n_todo = (zzmax-zzmin) * (yymax-yymin) * (xxmax-xxmin)
        to_do = <long*> malloc(n_todo * sizeof(long))

        i_todo = 0
        for zi in xrange(zzmin, zzmax):
            for yi in xrange(yymin, yymax):
                for xi in xrange(xxmin, xxmax):
                    to_do[i_todo] = (zi-self.startz)*self.dimx*self.dimy + (yi-self.starty)*self.dimx + (xi-self.startx)
                    i_todo += 1

        if n_todo:
            self.compute_thread(i_cell, to_do, n_todo)

        free(to_do)

    cdef void compute_ugrid_thread(self, long i_cell) noexcept nogil:
        #
        cdef double zzmin, zzmax, yymin, yymax, xxmin, xxmax
        cdef long i_point
        cdef long i_node = 0
        cdef long n_todo, n_todo_max, i_todo

        xxmin = self.nodes[self.cells[i_cell,i_node],0]
        xxmax = self.nodes[self.cells[i_cell,i_node],0]
        yymin = self.nodes[self.cells[i_cell,i_node],1]
        yymax = self.nodes[self.cells[i_cell,i_node],1]
        zzmin = self.nodes[self.cells[i_cell,i_node],2]
        zzmax = self.nodes[self.cells[i_cell,i_node],2]

        for i_node in xrange(1, self.n_nodes):
            if xxmin > self.nodes[self.cells[i_cell,i_node],0]:
                xxmin = self.nodes[self.cells[i_cell,i_node],0]
            if xxmax < self.nodes[self.cells[i_cell,i_node],0]:
                xxmax = self.nodes[self.cells[i_cell,i_node],0]
            if yymin > self.nodes[self.cells[i_cell,i_node],1]:
                yymin = self.nodes[self.cells[i_cell,i_node],1]
            if yymax < self.nodes[self.cells[i_cell,i_node],1]:
                yymax = self.nodes[self.cells[i_cell,i_node],1]
            if zzmin > self.nodes[self.cells[i_cell,i_node],2]:
                zzmin = self.nodes[self.cells[i_cell,i_node],2]
            if zzmax < self.nodes[self.cells[i_cell,i_node],2]:
                zzmax = self.nodes[self.cells[i_cell,i_node],2]

        n_todo = 1000
        to_do = <long*> malloc(n_todo * sizeof(long))

        i_todo = 0
        for i_point in xrange(self.n_points):
            if ((self.points[i_point,0] >= xxmin) and (self.points[i_point,0] <= xxmax) and
                (self.points[i_point,1] >= yymin) and (self.points[i_point,1] <= yymax) and
                (self.points[i_point,2] >= zzmin) and (self.points[i_point,2] <= zzmax)):
                to_do[i_todo] = i_point
                i_todo += 1
                if i_todo == n_todo:
                    n_todo += 1000
                    to_do = <long*> realloc(to_do, n_todo * sizeof(long))

        n_todo = i_todo
        to_do = <long*> realloc(to_do, n_todo * sizeof(long))

        if n_todo:
            self.compute_thread(i_cell, to_do, n_todo)

        free(to_do)

    cdef void compute_thread(self, long i_cell, long* to_do, long n_todo) noexcept nogil:
        #
        cdef long indni, i_node, i_point, i_todo, i_tmp
        cdef double** g_points

        if self.ndim == 2:
            g_points = get_param_coordinate_2d(i_cell, to_do, n_todo, self.nodes, self.cells, self.n_nodes, self.order, self.N_data, self.dNdr_data, self.dNds_data, self.points, self.is_linear)
        else:
            g_points = get_param_coordinate_3d(i_cell, to_do, n_todo, self.nodes, self.cells, self.n_nodes, self.order, self.N_data, self.dNdr_data, self.dNds_data, self.dNdt_data, self.points, self.is_linear)

        cdef double* N = <double*> malloc(self.n_nodes * sizeof(double))
        cdef double* N_linear = <double*> malloc(self.n_nodes_linear * sizeof(double))

        for i_todo in xrange(n_todo):
            if g_points[i_todo][0] != 2:
                if self.order == 1:
                    if self.ndim == 2:
                        N2D(N, g_points[i_todo], self.N_data, self.n_nodes)
                    else:
                        N3D(N, g_points[i_todo], self.N_data, self.n_nodes)
                    for i_node in xrange(self.n_nodes):
                        N_linear[i_node] = N[i_node]
                else:
                    if self.ndim == 2:
                        N2D_quad(N, g_points[i_todo], self.N_data, self.n_nodes)
                    else:
                        N3D_quad(N, g_points[i_todo], self.N_data, self.n_nodes)
                    if self.ndim == 2:
                        N2D(N_linear, g_points[i_todo], self.N_data_linear, self.n_nodes_linear)
                    else:
                        N3D(N_linear, g_points[i_todo], self.N_data_linear, self.n_nodes_linear)
                for i_node in xrange(self.n_nodes_linear):
                    if N_linear[i_node] < -self.EPSILON:
                        g_points[i_todo][0] = 2
                        break
                if g_points[i_todo][0] == 2:
                    free(g_points[i_todo])
                    continue
                i_point = to_do[i_todo]
                omp_set_lock(&self.lock_done)
                if self.done[i_point] > 0:
                    omp_unset_lock(&self.lock_done)
                    free(g_points[i_todo])
                    continue
                else:
                    self.done[i_point] = 1+i_cell+self.iii
                    omp_unset_lock(&self.lock_done)
                for i_node in xrange(self.n_nodes):
                    omp_set_lock(&self.lock)
                    indni = self.indni
                    self.indni += 1
                    omp_unset_lock(&self.lock)
                    self.indp[indni] = i_point
                    self.indn[indni] = self.cells[i_cell,i_node]
                    self.val[indni] = N[i_node]
            free(g_points[i_todo])
        free(g_points)
        free(N)
        free(N_linear)

cdef double** get_param_coordinate_2d(long i_cell, long* to_do, long n_todo, double[:,:] nodes, long[:,:] cells, int n_nodes, int order, double[:,:] N_data, double[:,:] dNdr_data, double[:,:] dNds_data, double[:,:] points, bint is_linear) noexcept nogil:
    #
    cdef double res, dxg, dyg, detJ, dxdr, dydr, dxds, dyds, xpix_xp, ypix_yp, invJ0, invJ1, invJ2, invJ3, idetJ

    cdef long niter, i_todo, i_node

    cdef double* N = <double*> malloc(n_nodes * sizeof(double))
    cdef double* dNdr = <double*> malloc(n_nodes * sizeof(double))
    cdef double* dNds = <double*> malloc(n_nodes * sizeof(double))
    cdef double** g_points = <double**> malloc(n_todo * sizeof(double*))

    for i_todo in xrange(n_todo):

        g_points[i_todo] = <double*> malloc(2 * sizeof(double))

        res = 1
        niter = 0
        detJ = 1

        g_points[i_todo][0] = 0
        g_points[i_todo][1] = 0

        while res > 1e-12 and detJ > 0 and niter < 1000:

            niter += 1

            if order == 1:
                N2D(N, g_points[i_todo], N_data, n_nodes)
                N2D(dNdr, g_points[i_todo], dNdr_data, n_nodes)
                N2D(dNds, g_points[i_todo], dNds_data, n_nodes)
            else:
                N2D_quad(N, g_points[i_todo], N_data, n_nodes)
                N2D_quad(dNdr, g_points[i_todo], dNdr_data, n_nodes)
                N2D_quad(dNds, g_points[i_todo], dNds_data, n_nodes)

            dxdr = 0
            dydr = 0
            dxds = 0
            dyds = 0

            for i_node in xrange(n_nodes):
                dxdr += dNdr[i_node]*nodes[cells[i_cell,i_node],0]
                dydr += dNdr[i_node]*nodes[cells[i_cell,i_node],1]
                dxds += dNds[i_node]*nodes[cells[i_cell,i_node],0]
                dyds += dNds[i_node]*nodes[cells[i_cell,i_node],1]

            detJ = dxdr*dyds - dydr*dxds

            if detJ > 0:

                idetJ = 1/detJ

                invJ0 =  dyds
                invJ1 = -dxds
                invJ2 = -dydr
                invJ3 =  dxdr

                xpix_xp = points[to_do[i_todo],0]
                ypix_yp = points[to_do[i_todo],1]

                for i_node in xrange(n_nodes):
                    xpix_xp -= N[i_node]*nodes[cells[i_cell,i_node],0]
                    ypix_yp -= N[i_node]*nodes[cells[i_cell,i_node],1]

                dxg = (invJ0*(xpix_xp)+invJ1*(ypix_yp))*idetJ
                dyg = (invJ2*(xpix_xp)+invJ3*(ypix_yp))*idetJ
                res = dxg*dxg + dyg*dyg

                g_points[i_todo][0] += dxg
                g_points[i_todo][1] += dyg

            else:
                g_points[i_todo][0] = 2
                g_points[i_todo][1] = 2

            if is_linear:
                break

    free(N)
    free(dNdr)
    free(dNds)

    return g_points

cdef double** get_param_coordinate_3d(long i_cell, long* to_do, long n_todo, double[:,:] nodes, long[:,:] cells, int n_nodes, int order, double[:,:] N_data, double[:,:] dNdr_data, double[:,:] dNds_data, double[:,:] dNdt_data, double[:,:] points, bint is_linear) noexcept nogil:
    #
    cdef double res, dxg, dyg, detJ, dxdr, dydr, dxds, dyds, xpix_xp, ypix_yp, invJ0, invJ1, invJ2, invJ3, idetJ
    cdef double dzg, dzdr, dzds, dxdt, dydt, dzdt, zpix_zp, invJ4, invJ5, invJ6, invJ7, invJ8

    cdef long niter, i_todo, i_node

    cdef double* N = <double*> malloc(n_nodes * sizeof(double))
    cdef double* dNdr = <double*> malloc(n_nodes * sizeof(double))
    cdef double* dNds = <double*> malloc(n_nodes * sizeof(double))
    cdef double* dNdt = <double*> malloc(n_nodes * sizeof(double))
    cdef double** g_points = <double**> malloc(n_todo * sizeof(double*))

    for i_todo in xrange(n_todo):

        g_points[i_todo] = <double*> malloc(3 * sizeof(double))

        res = 1
        niter = 0
        detJ = 1

        g_points[i_todo][0] = 0
        g_points[i_todo][1] = 0
        g_points[i_todo][2] = 0

        while res > 1e-12 and detJ > 0 and niter < 1000:

            niter += 1

            if order == 1:
                N3D(N, g_points[i_todo], N_data, n_nodes)
                N3D(dNdr, g_points[i_todo], dNdr_data, n_nodes)
                N3D(dNds, g_points[i_todo], dNds_data, n_nodes)
                N3D(dNdt, g_points[i_todo], dNdt_data, n_nodes)
            else:
                N3D_quad(N, g_points[i_todo], N_data, n_nodes)
                N3D_quad(dNdr, g_points[i_todo], dNdr_data, n_nodes)
                N3D_quad(dNds, g_points[i_todo], dNds_data, n_nodes)
                N3D_quad(dNdt, g_points[i_todo], dNdt_data, n_nodes)

            dxdr = 0
            dydr = 0
            dxds = 0
            dyds = 0
            dxdt = 0
            dydt = 0
            dzdr = 0
            dzds = 0
            dzdt = 0

            for i_node in xrange(n_nodes):
                dxdr += dNdr[i_node]*nodes[cells[i_cell,i_node],0]
                dxds += dNds[i_node]*nodes[cells[i_cell,i_node],0]
                dxdt += dNdt[i_node]*nodes[cells[i_cell,i_node],0]
                dydr += dNdr[i_node]*nodes[cells[i_cell,i_node],1]
                dyds += dNds[i_node]*nodes[cells[i_cell,i_node],1]
                dydt += dNdt[i_node]*nodes[cells[i_cell,i_node],1]
                dzdr += dNdr[i_node]*nodes[cells[i_cell,i_node],2]
                dzds += dNds[i_node]*nodes[cells[i_cell,i_node],2]
                dzdt += dNdt[i_node]*nodes[cells[i_cell,i_node],2]

            detJ = (dxdr*dyds*dzdt +
                    dxdt*dydr*dzds +
                    dxds*dydt*dzdr -
                    dxdt*dyds*dzdr -
                    dxdr*dydt*dzds -
                    dxds*dydr*dzdt)

            if detJ > 0:
                idetJ = 1./detJ

                invJ0 =  (dyds*dzdt - dydt*dzds)
                invJ1 = -(dxds*dzdt - dxdt*dzds)
                invJ2 =  (dxds*dydt - dxdt*dyds)
                invJ3 = -(dydr*dzdt - dydt*dzdr)
                invJ4 =  (dxdr*dzdt - dxdt*dzdr)
                invJ5 = -(dxdr*dydt - dxdt*dydr)
                invJ6 =  (dydr*dzds - dyds*dzdr)
                invJ7 = -(dxdr*dzds - dxds*dzdr)
                invJ8 =  (dxdr*dyds - dxds*dydr)

                xpix_xp = points[to_do[i_todo],0]
                ypix_yp = points[to_do[i_todo],1]
                zpix_zp = points[to_do[i_todo],2]

                for i_node in xrange(n_nodes):
                    xpix_xp -= N[i_node]*nodes[cells[i_cell,i_node],0]
                    ypix_yp -= N[i_node]*nodes[cells[i_cell,i_node],1]
                    zpix_zp -= N[i_node]*nodes[cells[i_cell,i_node],2]

                dxg = (invJ0*(xpix_xp)+invJ1*(ypix_yp)+invJ2*(zpix_zp))*idetJ
                dyg = (invJ3*(xpix_xp)+invJ4*(ypix_yp)+invJ5*(zpix_zp))*idetJ
                dzg = (invJ6*(xpix_xp)+invJ7*(ypix_yp)+invJ8*(zpix_zp))*idetJ
                res = dxg*dxg + dyg*dyg + dzg*dzg

                g_points[i_todo][0] += dxg
                g_points[i_todo][1] += dyg
                g_points[i_todo][2] += dzg

            else:
                g_points[i_todo][0] = 2
                g_points[i_todo][1] = 2
                g_points[i_todo][2] = 2

            if is_linear:
                break

    free(N)
    free(dNdr)
    free(dNds)
    free(dNdt)

    return g_points

cdef void N2D(double* result, double* g_point, double[:,:] N_data, int n_nodes) noexcept nogil:
    cdef int i_node
    for i_node in xrange(n_nodes):
        result[i_node] = (
            N_data[i_node,0b00] +
            N_data[i_node,0b01]*g_point[1] +
            N_data[i_node,0b10]*g_point[0] +
            N_data[i_node,0b11]*g_point[0]*g_point[1]
        )

cdef void N2D_quad(double* result, double* g_point, double[:,:] N_data, int n_nodes) noexcept nogil:
    cdef int i_node
    for i_node in xrange(n_nodes):
        result[i_node] = (
            N_data[i_node,0] +                                           # 00
            N_data[i_node,1]*g_point[1] +                                # 01
            N_data[i_node,2]*g_point[1]*g_point[1] +                     # 02
            N_data[i_node,3]*g_point[0] +                                # 10
            N_data[i_node,4]*g_point[0]*g_point[1] +                     # 11
            N_data[i_node,5]*g_point[0]*g_point[1]*g_point[1] +          # 12
            N_data[i_node,6]*g_point[0]*g_point[0] +                     # 20
            N_data[i_node,7]*g_point[0]*g_point[0]*g_point[1] +          # 21
            N_data[i_node,8]*g_point[0]*g_point[0]*g_point[1]*g_point[1] # 22
        )

cdef void N3D(double* result, double* g_point, double[:,:] N_data, int n_nodes) noexcept nogil:
    cdef int i_node
    for i_node in xrange(n_nodes):
        result[i_node] = (
            N_data[i_node,0b000] +
            N_data[i_node,0b001]*g_point[2] +
            N_data[i_node,0b010]*g_point[1] +
            N_data[i_node,0b011]*g_point[1]*g_point[2] +
            N_data[i_node,0b100]*g_point[0] +
            N_data[i_node,0b101]*g_point[0]*g_point[2] +
            N_data[i_node,0b110]*g_point[0]*g_point[1] +
            N_data[i_node,0b111]*g_point[0]*g_point[1]*g_point[2]
        )

cdef void N3D_quad(double* result, double* g_point, double[:,:] N_data, int n_nodes) noexcept nogil:
    cdef int i_node
    for i_node in xrange(n_nodes):
        result[i_node] = (
            N_data[i_node,0] +                                                                  # 000
            N_data[i_node,1]*g_point[2] +                                                       # 001
            N_data[i_node,2]*g_point[2]*g_point[2] +                                            # 002
            N_data[i_node,3]*g_point[1] +                                                       # 010
            N_data[i_node,4]*g_point[1]*g_point[2] +                                            # 011
            N_data[i_node,5]*g_point[1]*g_point[2]*g_point[2] +                                 # 012
            N_data[i_node,6]*g_point[1]*g_point[1] +                                            # 020
            N_data[i_node,7]*g_point[1]*g_point[1]*g_point[2] +                                 # 021
            N_data[i_node,8]*g_point[1]*g_point[1]*g_point[2]*g_point[2] +                      # 022
            N_data[i_node,9]*g_point[0] +                                                       # 100
            N_data[i_node,10]*g_point[0]*g_point[2] +                                           # 101
            N_data[i_node,11]*g_point[0]*g_point[2]*g_point[2] +                                # 102
            N_data[i_node,12]*g_point[0]*g_point[1] +                                           # 110
            N_data[i_node,13]*g_point[0]*g_point[1]*g_point[2] +                                # 111
            N_data[i_node,14]*g_point[0]*g_point[1]*g_point[2]*g_point[2] +                     # 112
            N_data[i_node,15]*g_point[0]*g_point[1]*g_point[1] +                                # 120
            N_data[i_node,16]*g_point[0]*g_point[1]*g_point[1]*g_point[2] +                     # 121
            N_data[i_node,17]*g_point[0]*g_point[1]*g_point[1]*g_point[2]*g_point[2] +          # 122
            N_data[i_node,18]*g_point[0]*g_point[0] +                                           # 200
            N_data[i_node,19]*g_point[0]*g_point[0]*g_point[2] +                                # 201
            N_data[i_node,20]*g_point[0]*g_point[0]*g_point[2]*g_point[2] +                     # 202
            N_data[i_node,21]*g_point[0]*g_point[0]*g_point[1] +                                # 210
            N_data[i_node,22]*g_point[0]*g_point[0]*g_point[1]*g_point[2] +                     # 211
            N_data[i_node,23]*g_point[0]*g_point[0]*g_point[1]*g_point[2]*g_point[2] +          # 212
            N_data[i_node,24]*g_point[0]*g_point[0]*g_point[1]*g_point[1] +                     # 220
            N_data[i_node,25]*g_point[0]*g_point[0]*g_point[1]*g_point[1]*g_point[2] +          # 221
            N_data[i_node,26]*g_point[0]*g_point[0]*g_point[1]*g_point[1]*g_point[2]*g_point[2] # 222
        )

