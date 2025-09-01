from __future__ import annotations
import math
import random
from typing import Iterable, List, Union

Number = Union[int, float]

def _to_list(x: Union[Number, Iterable[Number]]) -> List[Number]:
    if isinstance(x, (int, float)):
        return [x]
    return list(x)

def _log_choose(n: int, k: int) -> float:
    if k < 0 or k > n:
        return -math.inf
    if k == 0 or k == n:
        return 0.0
    k = min(k, n - k)
    result = 0.0
    for i in range(k):
        result += math.log(n - i) - math.log(i + 1)
    return result

def dbinom(x: Union[Number, Iterable[Number]], size: int, prob: Number, log: bool = False):
    xs = _to_list(x)
    if size < 0:
        raise ValueError("size must be >= 0")
    if prob < 0.0 or prob > 1.0:
        raise ValueError("prob must be between 0 and 1")
    
    def _dbinom_single(xi: Number) -> float:
        if not isinstance(xi, int) or xi < 0 or xi > size:
            return -math.inf if log else 0.0
        
        if prob == 0.0:
            return 0.0 if xi > 0 else (0.0 if log else 1.0)
        if prob == 1.0:
            return 0.0 if xi < size else (0.0 if log else 1.0)
        
        log_pmf = _log_choose(size, xi) + xi * math.log(prob) + (size - xi) * math.log(1.0 - prob)
        return log_pmf if log else math.exp(log_pmf)
    
    vals = [_dbinom_single(xi) for xi in xs]
    return vals[0] if isinstance(x, (int, float)) else vals

def pbinom(q: Union[Number, Iterable[Number]], size: int, prob: Number,
           lower_tail: bool = True, log: bool = False):
    qs = _to_list(q)
    if size < 0:
        raise ValueError("size must be >= 0")
    if prob < 0.0 or prob > 1.0:
        raise ValueError("prob must be between 0 and 1")
    
    def _pbinom_single(qi: Number) -> float:
        if qi < 0:
            p = 0.0
        elif qi >= size:
            p = 1.0
        else:
            k = int(math.floor(qi))
            p = 0.0
            for i in range(k + 1):
                p += math.exp(_log_choose(size, i) + i * math.log(prob) + (size - i) * math.log(1.0 - prob))
        
        if not lower_tail:
            p = 1.0 - p
        
        if log:
            return -math.inf if p == 0.0 else math.log(p)
        else:
            return p
    
    vals = [_pbinom_single(qi) for qi in qs]
    return vals[0] if isinstance(q, (int, float)) else vals

def qbinom(p: Union[Number, Iterable[Number]], size: int, prob: Number,
           lower_tail: bool = True, log: bool = False):
    ps = _to_list(p)
    if size < 0:
        raise ValueError("size must be >= 0")
    if prob < 0.0 or prob > 1.0:
        raise ValueError("prob must be between 0 and 1")
    
    def to_prob(pp: float) -> float:
        if log:
            pp = math.exp(pp)
        return pp if lower_tail else 1.0 - pp
    
    def _qbinom_single(pp: Number) -> float:
        target_prob = to_prob(pp)
        if target_prob < 0.0 or target_prob > 1.0:
            return math.nan
        
        if target_prob == 0.0:
            return 0.0
        if target_prob == 1.0:
            return float(size)
        
        cum_prob = 0.0
        for k in range(size + 1):
            pmf = math.exp(_log_choose(size, k) + k * math.log(prob) + (size - k) * math.log(1.0 - prob))
            cum_prob += pmf
            if cum_prob >= target_prob:
                return float(k)
        
        return float(size)
    
    vals = [_qbinom_single(pp) for pp in ps]
    return vals[0] if isinstance(p, (int, float)) else vals

def rbinom(n: int, size: int, prob: Number):
    if n < 0:
        raise ValueError("n must be >= 0")
    if size < 0:
        raise ValueError("size must be >= 0")
    if prob < 0.0 or prob > 1.0:
        raise ValueError("prob must be between 0 and 1")
    
    return [sum(1 for _ in range(size) if random.random() < prob) for _ in range(n)]