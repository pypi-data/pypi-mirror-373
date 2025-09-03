"""
Lazy import utilities for heavy dependencies.
"""

# Lazy import functions to prevent startup hangs
_pandas = None
_numpy = None
_matplotlib = None
_seaborn = None

def get_pandas():
    """Lazy import pandas."""
    global _pandas
    if _pandas is None:
        import pandas as pd
        _pandas = pd
    return _pandas

def get_numpy():
    """Lazy import numpy."""
    global _numpy
    if _numpy is None:
        import numpy as np
        _numpy = np
    return _numpy

def get_matplotlib():
    """Lazy import matplotlib.pyplot."""
    global _matplotlib
    if _matplotlib is None:
        import matplotlib.pyplot as plt
        _matplotlib = plt
    return _matplotlib

def get_seaborn():
    """Lazy import seaborn."""
    global _seaborn
    if _seaborn is None:
        import seaborn as sns
        _seaborn = sns
    return _seaborn
