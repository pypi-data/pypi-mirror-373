# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 12:30:28 2025

@author: balazs
"""

from multiprocessing import shared_memory
import time
import random

def create_shared_memory(name: str, size: int):
    """
    Creates or resizes a shared memory segment. If a shared memory object
    already exists with the same name, it will be closed and unlinked first.
    """
    try:
        # Check if it exists already
        existing = shared_memory.SharedMemory(name=name)
        safe_cleanup(existing)
        raise Exception('existing shared memory can only be safely closed from the context it was created, you will most likely have to shut down any process connected to it')
    except FileNotFoundError:
        print(f"[INFO] No existing shared memory '{name}' found.")

    # Create new shared memory
    shm = shared_memory.SharedMemory(name=name, create=True, size=size+1)
    shm.buf[size] = 0
    print(f"[INFO] Created shared memory '{name}' with size {size}.")
    return shm

def connect_to_shared_memory(name: str, size: int):
    try:
        # Check if it exists already
        shm = shared_memory.SharedMemory(name=name, size=size+1)
        print(f"[INFO] Existing shared memory '{name}' found. Connecting.")
        return shm
    except FileNotFoundError:
        print(f"[INFO] No existing shared memory '{name}' found.")
    

def safe_cleanup(shm: shared_memory.SharedMemory):
    try:
        shm.close()
        shm.unlink()
        print(f"[INFO] Cleaned up shared memory '{shm.name}'.")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[WARN] Failed to clean up shared memory: {e}")

if __name__ == '__main__':
    for _ in range(1000):
        size = random.randint(10_000, 20_000)
        shm = create_shared_memory('mybuffer_0', size)
        buffer = shm.buf
        buffer[-4:] = b'test'
        
        existing = connect_to_shared_memory('mybuffer_0', size)
        print(''.join([chr(i) for i in existing.buf[-4+size:size]]), existing.size - shm.size, len(existing.buf) - len(shm.buf))
        # existing.close()
        # existing.unlink()
        safe_cleanup(existing)
        # time.sleep(0.05)
        
        safe_cleanup(shm)
    
    # Resize
    
    shm = create_shared_memory('mybuffer_0', 2048)
    buffer = shm.buf
    buffer[-4:] = b'done'
    safe_cleanup(shm)

