# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 16:30:59 2025

@author: balazs
"""


from kivy.app import App
from kivy.uix.scatter import ScatterPlane
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.graphics.texture import Texture
from kivy.uix.slider import Slider
from kivy.uix.label import Label
import kivy
from mandelbrot_viewer.shared_memory_handler import create_shared_memory, safe_cleanup
from multiprocessing.connection import Listener, Client
import gc

import sympy as s

kivy.require('2.2.1')

import numpy as np
import taichi as ti

from mandelbrot_viewer.mandelbrot_calculator import compute as compute64

import matplotlib

import threading as thr
import subprocess
from time import sleep, perf_counter
import sys
from random import randint

import os
path = '\\'.join(__file__.split('\\')[:-1])
path = os.path.join(path, 'ti_bigfloat_compute_server.py')

cmap = matplotlib.colormaps['viridis']
ranges = [3, 5]
curr_max_n = [ranges[1]]

try:
    ti.init(ti.gpu)
except:
    ti.init()

ADDRESS = ('localhost', 6011)
authkey = b'secretpassword'
name = f'shared_buffer_{randint(0, 1000)}'
do_sync = []
synced = []
subprocesses = []
has_started = []
server_ask_threads = []
connections = []
server_subprocess_threads = []

def ask_server_started(conn, i):
    msg = conn.recv()
    if msg == 'started':
        has_started[i] = True
    else:
        raise RuntimeError(f"didn't get 'started' response from server {i}")
    

flag = [True]
def wait_connections():
    while flag[0]:
        conn = listener.accept()
        connections.append(conn)
        do_sync.append(False)
        synced.append(False)
        has_started.append(False)
        
        t = thr.Thread(target=ask_server_started, args = (conn, len(has_started)-1))
        t.start()
        server_ask_threads.append(t)
        
def stop_wait():
    flag[0] = False
    with Client(ADDRESS, authkey=authkey) as conn:
        pass

def pipe_reader(proc):
    for line in proc.stdout:
        sys.stdout.write(line)
        if line.startswith('compute_progress'):
            _, curr, _, full = line.split()
            r = float(curr)/float(full)
            app.update_progress(r)

def start_servers():
    for i in range(ranges[0], ranges[1]):
        p = subprocess.Popen(['python', '-u', path, str(i)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)#, creationflags=subprocess.CREATE_NEW_CONSOLE)#
        subprocesses.append(p)
        ts = thr.Thread(target=pipe_reader, args=(p, ))
        ts.start()
        server_subprocess_threads.append(ts)
        sleep(2)

def compute(f, x0, y0, x1, y1, m, n, img, iter_depth):
    if f == compute64:
        return compute64(float(x0), float(y0), float(x1), float(y1), m, n, img, iter_depth)
    else:
        i = f - ranges[0]
        connections[i].send(f'compute {str(x0.evalf(f*10))} {str(y0.evalf(f*10))} {str(x1.evalf(f*10))} {str(y1.evalf(f*10))} {m} {n} {iter_depth}')
        msg = connections[i].recv()
        if msg == 'okay':
            return

def choose_compute(x0, x1, y0, y1, m, n):
    dx = (x1 - x0)/m
    dy = (y1 - y0)/n 
    
    eps = min(dx, dy)
    
    bits = -s.log(eps, 10)*10/3 # 2**10 = 1024 \approx 1000 = 10**3
    
    print(float(eps), float(bits))
    
    if bits < 53:
        return compute64 
    for i in range(ranges[0], ranges[0]+sum(has_started)):#curr_max_n[0]):
        if bits < (i-1)*32:
            print(i)
            return i
    if has_started[0]:
        return ranges[0]+sum(has_started)-1
    else:
        return compute64

def allocate_img(shape):
    size = 4*shape[0]*shape[1]
    shm = create_shared_memory(name, size)
    
    for i in range(len(connections)):
        if do_sync[i] and has_started[i]:
            connections[i].send(f'allocate {name} {shape[0]} {shape[1]}')
            msg = connections[i].recv()
            
            synced[i] = True
        
    img = np.frombuffer(shm.buf, np.float32, shape[0]*shape[1]).reshape(shape)
    
    return shm, img

def deallocate_img(self):
    shm = self.shm
    self.img = None
    gc.collect()
    for i in range(len(connections)):
        if synced[i]:
            connections[i].send('deallocate')
            msg = connections[i].recv()
            synced[i] = False
            
    safe_cleanup(shm)
    

class APTransform:
    def __init__(self, mat = None):
        if mat:
            self.mat = mat
        else:
            self.mat = s.Matrix([[s.Float(1, dps = 16), 0, 0, 0],
                                 [0, s.Float(1, dps = 16), 0, 0],
                                 [0, 0, s.Float(1, dps = 16), 0],
                                 [0, 0, 0, s.Float(1, dps = 16)]])
    def __repr__(self):
        return self.mat.__repr__()
            
    def identity(self):
        return APTransform(s.Matrix.eye())

    def inverse(self):
        return APTransform(self.mat.inv())

    def transpose(self):
        return APTransform(self.mat.T)

    def multiply(self, mb):
        return APTransform(mb.mat @ self.mat)
    
    def scale(self, x, y, z):
        ret = APTransform()
        ret.mat[0,0] = x
        ret.mat[1,1] = y
        ret.mat[2,2] = z
        return ret

    def translate(self, x, y, z):
        ret = APTransform()
        ret.mat[3,0] = x
        ret.mat[3,1] = y
        ret.mat[3,2] = z
        return ret

    def rotate(self,
               angle, x, y, z):
        sn = s.sin(angle)
        cs = s.cos(angle)
        
        u_x = s.Matrix([[0, -z, y, 0],
                        [z, 0, -x, 0],
                        [-y, x, 0, 0],
                        [0,  0, 0, 0]])
        u = s.Matrix([x, y, z, 0])@s.Matrix([x, y, z, 0]).T
        
        I = s.Matrix.eye(4)
        
        return APTransform(cs*I + (1-cs)*u + sn*u_x)

class InteractiveCanvas(Widget):   
    transform = ObjectProperty(APTransform())
    transform1 = ObjectProperty(Matrix())
    transform2 = ObjectProperty(Matrix())
    resolution_multiplier = NumericProperty(0.3)
    iter_depth = NumericProperty(1024)
    zoom = StringProperty('1')
    zoom_center = ObjectProperty((0,0))
    curr_FPS = NumericProperty(0)
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n, self.m = self.size
        self.n = int(self.n*self.resolution_multiplier)
        self.m = int(self.m*self.resolution_multiplier)
        
        self.texture = Texture.create(size = (self.n, self.m), colorfmt = 'rgba', bufferfmt = 'float')
        self.shm, self.img = allocate_img((self.m, self.n))#np.zeros((self.m, self.n), dtype = np.float32)
        #self.texture.mag_filter = 'nearest'
        
        self.x0 = 0
        self.y0 = 0
        self.x1 = self.n
        self.y1 = self.m
        
        self.zoom_center = (self.n/2, self.m/2)
        self.zoom = '1'
        
        compute(compute64, self.x0, self.y0, self.x1, self.y1, self.m, self.n, self.img, self.iter_depth)
        
        self.texture.blit_buffer(cmap(self.img)[:, :, :].ravel().astype(np.float32), colorfmt = 'rgba', bufferfmt = 'float')
        
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size, texture = self.texture)

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.canvas.ask_update()
        
        self.server_busy = False
        self.server_ready = False
        self.next_texture_ready = False
        self.reallocate_finished = False
        
        self.next_texture_in_compute_old = False
        self.next_texture_ready_old = False
        
        self.compute_thread = None
        self.reallocate_thread = None
        
        self.ask_reallocate = False
        self.ask_update_texture = False
        self.force_update = False
        self.old_transform = None
        self.ask_update_transform = False
        self.schedule_compute = False
        self.make_new_texture = False
        self.texture_empty = True
        self.compute_args = None
        
        self.t1 = 0
        self.t2 = perf_counter()
        
        Clock.schedule_once(lambda dt: self.canvas.ask_update(), 0.01)
        Clock.schedule_interval(self.manual_mainloop, 0)
    
    def reallocate(self):
        self.server_busy = True
        deallocate_img(self)
        self.shm, self.img = allocate_img((self.m, self.n))
        self.server_busy = False
        self.server_ready = True
        self.reallocate_finished = True
        self.next_texture_ready = False
        
    
    def manual_mainloop(self, dt):
        if self.reallocate_finished:
            self.reallocate_thread.join()
        
        if self.ask_update_transform:
            self.compute_args = self.on_transform_work(self, self.transform)
            self.ask_update_transform = False
        
        if self.ask_reallocate and not self.server_busy:
            self.reallocate_finished = False
            self.reallocate_thread = thr.Thread(target=self.reallocate)
            self.reallocate_thread.start()
            self.ask_reallocate = False
        
        if self.make_new_texture:
            self.texture = Texture.create(size = (self.n, self.m), colorfmt = 'rgba', bufferfmt = 'float')
            self.texture_empty = True
            self.make_new_texture = False
        
        if self.ask_update_texture and not self.texture_empty:
            self.rect.texture = self.texture
            self.canvas.ask_update()
            self.ask_update_texture = False
        
        if self.next_texture_ready and not self.server_busy:
            self.compute_thread.join()
            
            if self.texture.size == self.img.shape[::-1]: 
                self.texture.blit_buffer(cmap(self.img).ravel().astype(np.float32) , colorfmt = 'rgba', bufferfmt = 'float')
                self.texture_empty = False
                print('texture filled')
                
                self.canvas.ask_update()
                
                root = App.get_running_app().root
                root.ids.mt_scatter.transform1 = self.transform2
                
                self.transform1 = self.transform2
                
            self.on_transform(self, self.transform)
            
            self.next_texture_ready = False   
        
        if self.schedule_compute and not self.server_busy and self.server_ready:
            self.compute_args = self.on_transform_work(self, self.transform)
            self.launch_compute()
            self.schedule_compute = False
        
        self.t1 = perf_counter()
        diff = self.t1-self.t2
        self.t2 = self.t1
        
        w = 0.001
        self.curr_FPS = (w/diff + (1-w)*self.curr_FPS)
        
        if diff > 30e-3:
            pass

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        # self.rect.texture = self.texture
        self.ask_update_texture = True
    
    def on_size(self, instance, value):
        self.n, self.m = self.size
        self.n = int(self.n*self.resolution_multiplier)
        self.m = int(self.m*self.resolution_multiplier)
        
        self.make_new_texture = True
        
        self.ask_reallocate = True
        self.server_ready = False
        
        self.x0 = 0
        self.y0 = 0
        self.x1 = self.n
        self.y1 = self.m
        
        self.ask_update_texture = True
        
        self.force_update = True
        self.on_transform(instance, self.transform)
    
    def on_resolution_multiplier(self, instance, value):
        self.n, self.m = self.size
        self.n = int(self.n*self.resolution_multiplier)
        self.m = int(self.m*self.resolution_multiplier)
        
        self.make_new_texture = True
        
        self.ask_reallocate = True
        self.server_ready = False
        
        self.x0 = 0
        self.y0 = 0
        self.x1 = self.n
        self.y1 = self.m
        
        self.ask_update_texture = True
        
        self.force_update = True
        self.on_transform(instance, self.transform)
    
    def on_iter_depth(self, instance, value):
        self.force_update = True
        self.on_transform(instance, self.transform)
        try:
            root = App.get_running_app().root
            root.ids.info_label3.text = f'Iterations: {self.iter_depth}'
        except Exception as e:
            print(e)
        
    def on_zoom(self, instance, value):
        try:
            root = App.get_running_app().root
            root.ids.info_label1.text = f'Zoom: {self.zoom}'
        except Exception as e:
            print(e)
    
    def on_zoom_center(self, instance, value):
        try:
            root = App.get_running_app().root
            root.ids.info_label2.text = f'Center: x={self.zoom_center[0].evalf(5)} y={self.zoom_center[1].evalf(5)}'
        except Exception as e:
            print(e)
    
    def transform_tex_coords(self, trans):
        # Extract scatter's transform matrix (4x4 in kivy, we use 2D part)
        mat = np.array(trans.inverse().tolist(), dtype=float).ravel().reshape(4, 4)
        # Original texture coordinates (unit square)
        tex = np.array([
            [0, 0, 0, 1],  # bottom-left
            [self.width, 0, 0, 1],  # bottom-right
            [self.width, self.height, 0, 1],  # top-right
            [0, self.height, 0, 1],  # top-left
        ], dtype=float)

        # Apply scatter transformation
        transformed = tex @ mat
        transformed[:, 0] /= self.width
        transformed[:, 1] /= self.height
        tex_coords = transformed[:, :2].flatten()

        return tex_coords.tolist()
    
    def compute(self, f, x0, y0, x1, y1):
        self.server_busy = True
        compute(f, x0, y0, x1, y1, self.m, self.n, self.img, self.iter_depth)
        self.server_busy = False
        self.next_texture_ready = True
        
    
    def launch_compute(self):
        if self.compute_args:
            self.compute_thread = thr.Thread(target=self.compute, args = self.compute_args)
            self.compute_thread.start()
            self.compute_args = None
        
            root = App.get_running_app().root
            root.ids.mt_scatter.transform2 = Matrix()
            
            self.transform2 = Matrix()
            
        else:
            self.on_transform(self, self.transform)
    
    def check_next_texture_ready(self, instance, value):
        
        if value:
            self.compute_thread.join()
            if self.texture.size == self.img.shape[::-1]: 
                self.texture.blit_buffer(cmap(self.img).ravel().astype(np.float32) , colorfmt = 'rgba', bufferfmt = 'float')
            else:
                self.on_transform(instance, self.transform)
                return
            
            if self.ask_update_texture:
                self.rect.texture = self.texture
                self.ask_update_texture = False
            
            self.canvas.ask_update()
            
            root = App.get_running_app().root
            root.ids.mt_scatter.transform1 = self.transform2
            
            self.transform1 = self.transform2
            self.next_texture_ready = False
            
            self.on_transform(instance, self.transform)
    
    def on_transform1(self, instance, value):
        tex_coords = self.transform_tex_coords(value)
        self.rect.tex_coords = tex_coords
        self.canvas.ask_update()
    
    def on_transform(self, instance, value):
        self.ask_update_transform = True

    def on_transform_work(self, instance, value):
        v0 = s.Matrix([0, 0, 0, 1])
        v1 = s.Matrix([*self.size, 0, 1])
        mat = value.inverse().mat.T
        
        v0 = mat@v0
        v1 = mat@v1
        
        x0, y0 = v0[:2]
        x1, y1 = v1[:2]
        
        self.zoom_center = ((x0 + x1)/2, (y0 + y1)/2)
        self.zoom = str(value.mat[0].evalf(5))
        
        f = choose_compute(x0, x1, y0, y1, self.m, self.n)
        if f != compute64:
            i = f - ranges[0]
            if not do_sync[i]:
                do_sync[i] = True
                
                p = subprocess.Popen(['python', '-u', path, str(curr_max_n[0])], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)#, creationflags=subprocess.CREATE_NEW_CONSOLE)#
                subprocesses.append(p)
                
                ts = thr.Thread(target=pipe_reader, args=(p, ))
                ts.start()
                server_subprocess_threads.append(ts)
                
                self.transform.mat @= s.Matrix([[s.Float(1, dps = int(f*10)), 0, 0, 0],
                                                [0, s.Float(1, dps = int(f*10)), 0, 0],
                                                [0, 0, s.Float(1, dps = int(f*10)), 0],
                                                [0, 0, 0, s.Float(1, dps = int(f*10))]])
                
                curr_max_n[0] += 1 
                
                self.ask_reallocate = True
                self.server_ready = False
        if self.needs_update():
            self.schedule_compute = True
        self.force_update = False
        self.old_transform = value
        return f, x0, y0, x1, y1
    
    def needs_update(self):
        if self.force_update:
            return True
        if self.transform == self.old_transform and self.transform1.tolist() == Matrix().tolist():
            return False            
        return True


class ResolutionSlider(Slider):
    def on_value(self, instance, value):
        try:
            root = App.get_running_app().root
            root.ids.interactive_canvas.resolution_multiplier = value/100
        except Exception as e:
            print(e)

class DepthSlider(Slider):
    def on_value(self, instance, value):
        try:
            root = App.get_running_app().root
            root.ids.interactive_canvas.iter_depth = int(2**value)
        except Exception as e:
            print(e)

class TransparentWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            Color(0, 0, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class APScatterPlane(ScatterPlane):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.AP_transform = APTransform()
        self.transform1 = Matrix()
        self.transform2 = Matrix()
    
    def apply_AP_transform(self, trans, post_multiply=False, anchor=(0, 0)):
        t = APTransform().translate(anchor[0], anchor[1], 0)
        t = t.multiply(trans)
        t = t.multiply(APTransform().translate(-anchor[0], -anchor[1], 0))

        if post_multiply:
            self.AP_transform = self.AP_transform.multiply(t)
        else:
            self.AP_transform = t.multiply(self.AP_transform)
    
    def apply_simple_transform(self, trans, post_multiply=False, anchor=(0, 0)):
        t = Matrix().translate(anchor[0], anchor[1], 0)
        t = t.multiply(trans)
        t = t.multiply(Matrix().translate(-anchor[0], -anchor[1], 0))

        if post_multiply:
            self.transform1 = self.transform1.multiply(t)
            self.transform2 = self.transform2.multiply(t)
        else:
            self.transform1 = t.multiply(self.transform1)
            self.transform2 = t.multiply(self.transform2)
    
    def apply_transform(self, trans, post_multiply=False, anchor=(0, 0)):
        aptrans = APTransform(s.Matrix(trans.tolist()))
        self.apply_AP_transform(aptrans, post_multiply, anchor)
        self.apply_simple_transform(trans, post_multiply, anchor)
    

class MultiTouchScatter(APScatterPlane):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        def fnc(dt):
            print('kv post++++++++++++++++++++++++++++++++++++++++++++++++++++++', self.parent.children[0].m, self.parent.children[0])#self.parent.children)
            init_trans = Matrix().scale(self.parent.children[0].m, self.parent.children[0].m, self.parent.children[0].m).translate(self.parent.children[0].n*2, self.parent.children[0].m*2, 0)
            self.apply_transform(init_trans)
            self.parent.children[0].transform = self.AP_transform
            self.parent.children[0].on_transform(self.parent.children[0], self.AP_transform)
        Clock.schedule_once(fnc, 0.1)#lambda dt: [self.parent.children[0].on_transform(None, self.transform), print('==================================kv post++++++++++++++++++++++++++++++++++++++++++++++++++++++')], timeout = 0.5)
    
    def on_touch_down(self, touch):
        if touch.button in ['scrollup', 'scrolldown']:
            # print(touch.button, touch.x, touch.y)
            self.scroll(touch, touch.button)
        ret = super().on_touch_down(touch)
        try:
            root = App.get_running_app().root
            root.ids.interactive_canvas.transform = self.AP_transform
            root.ids.interactive_canvas.transform1 = self.transform1
            root.ids.interactive_canvas.transform2 = self.transform2
        except Exception as e:
            print(e)
        return ret
    
    def on_touch_move(self, touch):
        ret = super().on_touch_move(touch)
        try:
            root = App.get_running_app().root
            root.ids.interactive_canvas.transform = self.AP_transform
            root.ids.interactive_canvas.transform1 = self.transform1
            root.ids.interactive_canvas.transform2 = self.transform2
        except Exception as e:
            print(e)
        return ret
    
    def scroll(self, touch, scroll_t):
        scale = 0.8 if scroll_t == 'scrollup' else 1/0.8
        
        tr = Matrix().scale(scale, scale, scale)
        self.apply_transform(tr, anchor=(touch.x, touch.y))
    
    def collide_point(self, x, y):
        return self.parent.collide_point(x, y)
        
class Mandelbrotwiever(App):
    def on_start(self):
        print('##################################################################')
        print('on_start called ...')
        print('##################################################################')
    
    def on_stop(self):
        print('##################################################################')
        print('on_stop called ...')
        
        if self.root.ids.interactive_canvas.compute_thread:
            self.root.ids.interactive_canvas.compute_thread.join(timeout = 1)
        th = thr.Thread(target = deallocate_img, args = (self.root.children[0].children[1], ))
        th.start()
        th.join(timeout=1)
        # deallocate_img(self.root.children[0])
        print('##################################################################')
    
    def interrupt(self):
        try:
            canvas = self.root.ids.interactive_canvas
            canvas.shm.buf[canvas.img.nbytes] = 1 
        except Exception as e:
            print(e)
    
    def update_progress(self, ratio):
        self.root.ids.progbar.value = ratio * 100
        self.root.ids.progbar_txt.text = f"Progress: {int(ratio * 100)}%"



def main():
    try:
        listener = Listener(ADDRESS, authkey=authkey)
        print("Server: Waiting for connection...")
            
        
        listener_thr = thr.Thread(target=wait_connections)
        listener_thr.start()
        
        
        start_servers_thr = thr.Thread(target=start_servers)
        start_servers_thr.start()
        
        
        app = Mandelbrotwiever()
        app.run()
    
        
    finally:
        for conn in connections:
            conn.close()
        
        try:
            start_servers_thr.join()
        except:
            pass
        
        stop_wait()
        listener_thr.join()
        listener.close()
        
        for sa in server_ask_threads:
            sa.join()
        
        
        for ts in server_ask_threads:
            ts.join()

