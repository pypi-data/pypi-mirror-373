import ctypes
import os

dll_path = os.path.join(os.path.dirname(__file__), "calculator.dll")
lib = ctypes.CDLL(dll_path)

def add(a, b): return lib.Add(a, b)
def sub(a, b): return lib.Sub(a, b)
def mul(a, b): return lib.Mul(a, b)
def div(a, b): return lib.Div(a, b)
