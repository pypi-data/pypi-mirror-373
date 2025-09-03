import ctypes
import os

lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "calculator.dll"))

def add(a, b): return lib.Add(a, b)
def sub(a, b): return lib.Sub(a, b)
def mul(a, b): return lib.Mul(a, b)
def div(a, b): return lib.Div(a, b)
