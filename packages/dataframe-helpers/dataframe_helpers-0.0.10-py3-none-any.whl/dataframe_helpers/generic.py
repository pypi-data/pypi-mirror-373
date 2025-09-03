
import numpy as np
import pandas as pd
from collections.abc import Iterable

def to_array(var):
    if isinstance(var, str):
        return [x for x in var.split(",")]
    elif isinstance(var, (list, tuple, set, np.ndarray, pd.Series)):
        return var
    else:
        raise TypeError(f"Invalid type: {type(var)}. Expected a string or an array-like object.")