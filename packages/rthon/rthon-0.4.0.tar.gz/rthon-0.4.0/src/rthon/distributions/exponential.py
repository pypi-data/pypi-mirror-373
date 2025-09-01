from __future__ import annotations
import math
import random
from typing import Iterable, List, Union

Number = Union[int, float]

def _to_list(x: Union[Number, Iterable[Number]]) -> List[Number]:
    if isinstance(x, (int, float)):
        return [x]
    return list(x)

def dexp(x: Union[Number, Iterable[Number]], rate: Number = 1.0, log: bool = False):
    xs = _to_list(x)
    if rate <= 0:
        raise ValueError("rate must be > 0")
    
    def _dexp_single(xi: Number) -> float:
        if xi < 0:
            return -math.inf if log else 0.0
        
        log_pdf = math.log(rate) - rate * xi
        return log_pdf if log else math.exp(log_pdf)
    
    vals = [_dexp_single(xi) for xi in xs]
    return vals[0] if isinstance(x, (int, float)) else vals

def pexp(q: Union[Number, Iterable[Number]], rate: Number = 1.0,
         lower_tail: bool = True, log: bool = False):
    qs = _to_list(q)
    if rate <= 0:
        raise ValueError("rate must be > 0")
    
    def _pexp_single(qi: Number) -> float:
        if qi <= 0:
            p = 0.0
        else:
            p = 1.0 - math.exp(-rate * qi)
        
        if not lower_tail:
            p = 1.0 - p
        
        if log:
            return -math.inf if p == 0.0 else math.log(p)
        else:
            return p
    
    vals = [_pexp_single(qi) for qi in qs]
    return vals[0] if isinstance(q, (int, float)) else vals

def qexp(p: Union[Number, Iterable[Number]], rate: Number = 1.0,
         lower_tail: bool = True, log: bool = False):
    ps = _to_list(p)
    if rate <= 0:
        raise ValueError("rate must be > 0")
    
    def to_prob(pp: float) -> float:
        if log:
            pp = math.exp(pp)
        return pp if lower_tail else 1.0 - pp
    
    def _qexp_single(pp: Number) -> float:
        prob = to_prob(pp)
        if prob < 0.0 or prob > 1.0:
            return math.nan
        if prob == 0.0:
            return 0.0
        if prob == 1.0:
            return math.inf
        
        return -math.log(1.0 - prob) / rate
    
    vals = [_qexp_single(pp) for pp in ps]
    return vals[0] if isinstance(p, (int, float)) else vals

def rexp(n: int, rate: Number = 1.0):
    if n < 0:
        raise ValueError("n must be >= 0")
    if rate <= 0:
        raise ValueError("rate must be > 0")
    
    return [-math.log(random.random()) / rate for _ in range(n)]