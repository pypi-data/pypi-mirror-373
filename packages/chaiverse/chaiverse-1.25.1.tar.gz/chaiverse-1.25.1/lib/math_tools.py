import numpy as np

def sigfig(x, precision = 4):
    return float(np.format_float_positional(x, precision=precision, unique=False, fractional=False, trim='k'))
