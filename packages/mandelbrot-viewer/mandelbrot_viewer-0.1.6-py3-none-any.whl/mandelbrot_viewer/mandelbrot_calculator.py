# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 22:06:57 2025

@author: balazs
"""

import taichi as ti

@ti.func
def complex_sqr(z):
    return ti.Vector([z[0] * z[0] - z[1] * z[1], 2 * z[0] * z[1]], ti.float64)


@ti.kernel
def compute(x0: ti.float64,
            y0: ti.float64,
            x1: ti.float64,
            y1: ti.float64,
            m0: ti.int32,
            n0: ti.int32,
            img: ti.types.ndarray(ti.f32, 2),
            iter_depth: ti.int32):
    x = x1-x0
    y = y1-y0
    
    m, n = m0, n0
    
    if img.shape[0] < m0 or img.shape[1] < n0:
        m, n = img.shape
    
    for i, j in ti.ndrange(m, n):
        c = ti.Vector([x0 + j/n*x, y0 + i/m*y], ti.float64)
        iterations = 0
        z = ti.Vector([0, 0], ti.float64)
        while z.norm() < 4 and iterations < iter_depth:
            z = complex_sqr(z) + c
            iterations += 1
        val = iterations/iter_depth
        img[i, j] = val

    
    
if __name__ == '__main__':
    ti.init(arch=ti.vulkan)  # Ensure you're using OpenGL backend
    
    mod = ti.aot.Module(ti.vulkan)
    mod.add_kernel(compute)
    mod.save("shaders.tcm")  # Saves shaders in a folder