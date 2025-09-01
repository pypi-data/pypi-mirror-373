from __future__ import annotations
import math
import random
from typing import Iterable, List, Union

Number = Union[int, float]

def _to_list(x: Union[Number, Iterable[Number]]) -> List[Number]:
    if isinstance(x, (int, float)):
        return [x]
    return list(x)

def dunif(x: Union[Number, Iterable[Number]], min: Number = 0.0, max: Number = 1.0, log: bool = False):
    xs = _to_list(x)
    if min >= max:
        raise ValueError("min must be < max")
    
    width = max - min
    log_pdf = -math.log(width)
    
    def _dunif_single(xi: Number) -> float:
        if min <= xi <= max:
            return log_pdf if log else (1.0 / width)
        else:
            return -math.inf if log else 0.0
    
    vals = [_dunif_single(xi) for xi in xs]
    return vals[0] if isinstance(x, (int, float)) else vals

def punif(q: Union[Number, Iterable[Number]], min: Number = 0.0, max: Number = 1.0,
          lower_tail: bool = True, log: bool = False):
    qs = _to_list(q)
    if min >= max:
        raise ValueError("min must be < max")
    
    def _punif_single(qi: Number) -> float:
        if qi <= min:
            p = 0.0
        elif qi >= max:
            p = 1.0
        else:
            p = (qi - min) / (max - min)
        
        if not lower_tail:
            p = 1.0 - p
        
        if log:
            return -math.inf if p == 0.0 else math.log(p)
        else:
            return p
    
    vals = [_punif_single(qi) for qi in qs]
    return vals[0] if isinstance(q, (int, float)) else vals

def qunif(p: Union[Number, Iterable[Number]], min: Number = 0.0, max: Number = 1.0,
          lower_tail: bool = True, log: bool = False):
    ps = _to_list(p)
    if min >= max:
        raise ValueError("min must be < max")
    
    def to_prob(pp: float) -> float:
        if log:
            pp = math.exp(pp)
        return pp if lower_tail else 1.0 - pp
    
    def _qunif_single(pp: Number) -> float:
        prob = to_prob(pp)
        if prob < 0.0 or prob > 1.0:
            return math.nan
        return min + prob * (max - min)
    
    vals = [_qunif_single(pp) for pp in ps]
    return vals[0] if isinstance(p, (int, float)) else vals

def runif(n: int, min: Number = 0.0, max: Number = 1.0):
    if n < 0:
        raise ValueError("n must be >= 0")
    if min >= max:
        raise ValueError("min must be < max")
    
    return [random.uniform(min, max) for _ in range(n)]