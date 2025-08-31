# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 15:16:45 2025

@author: balazs
"""

from multiprocessing.connection import Client
from mandelbrot_viewer.shared_memory_handler import connect_to_shared_memory, safe_cleanup
import sympy as s
import numpy as np
import gc
import taichi as ti
import time

import sys
sys.tracebacklimit=0

try:
    ti.init(ti.gpu)
except:
    ti.init()

ADDRESS = ('localhost', 6011)
authkey = b'secretpassword'

N = int(sys.argv[1])
print(N)

import taichi as ti
from taichi_big_float import supports_bigfloat, make_float_t

bigfloat = make_float_t(N)
float_t = bigfloat.float_t
i32_to_float = bigfloat.i32_to_float
str_to_float = bigfloat.str_to_float
float_to_f32 = bigfloat.float_to_f32

@ti.func
@supports_bigfloat(globals(), verbose=False, n = N)
def complex_sqr_x(x: float_t, y: float_t) -> float_t:
    return x*x - y*y#ti.Vector([z[0] * z[0] - z[1] * z[1], 2 * z[0] * z[1]], ti.float64)

@ti.func
@supports_bigfloat(globals(), verbose=False, n = N)
def complex_sqr_y(x: float_t, y: float_t) -> float_t:
    two = i32_to_float(2)#ti.Vector([0, 0, 0, ti.u32(2147483648), 0, ti.u32(2147483522)], ti.u32)
    return two * x*y#ti.Vector([z[0] * z[0] - z[1] * z[1], 2 * z[0] * z[1]], ti.float64)

@ti.func
@supports_bigfloat(globals(), verbose=False, n = N)
def complex_sqr(x: float_t, y: float_t) -> [float_t, float_t]:
    two = i32_to_float(2)
    return [x*x - y*y, two * x*y]#ti.Vector([z[0] * z[0] - z[1] * z[1], 2 * z[0] * z[1]], ti.float64)

@ti.kernel
@supports_bigfloat(globals(), verbose=False, n = N)
def compute(x0: float_t,
            y0: float_t,
            x1: float_t,
            y1: float_t,
            m0: ti.int32,
            n0: ti.int32,
            img: ti.types.ndarray(ti.f32, 2),
            iter_depth: ti.int32,
            start_row: ti.i32,
            row_count: ti.i32):
    x = x1-x0
    y = y1-y0
    
    m, n = m0, n0
    
    if img.shape[0] < m0 or img.shape[1] < n0:
        m, n = img.shape
    
    for k, j in ti.ndrange(row_count, n):
        i = start_row + k 
        
        cx = x0 + i32_to_float(j)/i32_to_float(n)*x
        cy = y0 + i32_to_float(i)/i32_to_float(m)*y
        iterations = 0
        zx = i32_to_float(0)
        zy = i32_to_float(0)
        
        while zx*zx + zy*zy < i32_to_float(4) and iterations < iter_depth:
            zx_old, zy_old = zx, zy
            zx = complex_sqr_x(zx_old, zy_old) + cx
            zy = complex_sqr_y(zx_old, zy_old) + cy
            iterations += 1
            # print(f192_to_f32(zx*zx + zy*zy))
        val = iterations/iter_depth
        # print(iterations)
        img[i, j] = val

def compute_func(x0, y0, x1, y1, m, n, img, iter_depth, start_row, row_count):
    return compute(str_to_float(str(x0.evalf(100))), str_to_float(str(y0.evalf(100))), str_to_float(str(x1.evalf(100))), str_to_float(str(y1.evalf(100))), m, n, img, iter_depth, start_row, row_count)

def estimate_compute_time(m, n, iter_depth, time_estimate_base):    
    return m*n*iter_depth*0.5*time_estimate_base
    

with Client(ADDRESS, authkey=authkey) as conn:
    img_ = np.empty((100, 100), dtype = np.float32)
    
    compute_func(s.Float(0), s.Float(0), s.Float(1), s.Float(1), 1, 1, img_, 1, 0, 1)
    print(img_[0,0])
    
    t0 = time.perf_counter()
    compute_func(s.Float(0), s.Float(0), s.Float(1), s.Float(1), 100, 100, img_, 100, 0, 100)
    print(img_[0,0])
    t1 = time.perf_counter()
    
    time_estimate_base = (t1 - t0)*0.01/np.sum(img_[~np.isnan(img_)])
    print(f"Server {N}: time estimate base: {time_estimate_base}")
    
    conn.send('started')
    while True:
        msg = conn.recv()
        
        command = msg.strip().split()[0]
        
        print(f"Server {N}: recieved: {command}")
        
        match command:
            case 'allocate':
                _, name, m, n = msg.strip().split()
                m, n = int(m), int(n)
                
                shm = connect_to_shared_memory(name, m*n*4)
                
                img = np.frombuffer(shm.buf, np.float32, m*n).reshape((m, n))
                
                conn.send('okay')
                print(f'Server {N}: allocated: {name}, {(m, n)}')
                
            case 'deallocate':
                try:
                    del img
                    gc.collect()
                    safe_cleanup(shm)
                except Exception as e:
                    print(e)
                conn.send('okay')
                
                print(f'Server {N}: deallocated img and freed shm')
                
            case 'compile':
                img_ = np.empty((10, 10), dtype = np.float32)
                compute_func(s.Float(0), s.Float(0), s.Float(1), s.Float(1), 1, 1, img_, 1)
            
            case 'compute':
                try:
                    _, x0, y0, x1, y1, m, n, iter_depth = msg.strip().split()
                    m, n, iter_depth = int(m), int(n), int(iter_depth)
                    
                    time_estimate = estimate_compute_time(m, n, iter_depth, time_estimate_base)
                    num_chunks = int(time_estimate/0.5+1)
                    row_count = m//num_chunks
                    start_row = 0
                    
                    shm.buf[4*m*n] = 0
                    
                    t0 = time.perf_counter()
                    while not shm.buf[4*m*n]:
                        print(f'compute_progress_Server_{N}:', start_row, min(row_count, m-start_row-1), m)
                        compute(str_to_float(x0), str_to_float(y0), str_to_float(x1), str_to_float(y1), m, n, img, iter_depth, start_row, min(row_count, m-start_row))
                        start_row += row_count
                        if start_row >= m:
                            print(f'compute_progress_Server_{N}:', m, min(row_count, m-start_row-1), m)
                            break
                    t1 = time.perf_counter()
                    
                    shm.buf[4*m*n] = 0
                    print(f'Server {N}: Estimated time: {time_estimate:.2f} s, Wall time: {t1-t0:.2f} s')
                except Exception as e:
                    print(e)
                    
                conn.send('okay')
            
