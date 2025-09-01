from __future__ import annotations
import math
import random
from typing import Iterable, List, Union

Number = Union[int, float]

def _to_list(x: Union[Number, Iterable[Number]]) -> List[Number]:
    if isinstance(x, (int, float)):
        return [x]
    return list(x)

def _incomplete_gamma_lower(a: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if a <= 0:
        return 1.0
    
    if x < a + 1:
        sum_term = 1.0
        term = 1.0
        k = 1
        while abs(term) > 1e-15 and k < 1000:
            term *= x / (a + k - 1)
            sum_term += term
            k += 1
        return math.exp(-x + a * math.log(x) - math.lgamma(a)) * sum_term
    else:
        b = x + 1.0 - a
        c = 1e30
        d = 1.0 / b
        h = d
        
        for i in range(1, 1001):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            del_h = d * c
            h *= del_h
            if abs(del_h - 1.0) < 1e-15:
                break
        
        gamma_cf = math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
        return 1.0 - gamma_cf

def dgamma(x: Union[Number, Iterable[Number]], shape: Number, rate: Number = 1.0, 
           scale: Number = None, log: bool = False):
    xs = _to_list(x)
    if shape <= 0:
        raise ValueError("shape must be > 0")
    if scale is not None:
        if scale <= 0:
            raise ValueError("scale must be > 0")
        rate = 1.0 / scale
    if rate <= 0:
        raise ValueError("rate must be > 0")
    
    def _dgamma_single(xi: Number) -> float:
        if xi <= 0:
            return -math.inf if log else 0.0
        
        log_pdf = (shape - 1) * math.log(xi) - rate * xi + shape * math.log(rate) - math.lgamma(shape)
        return log_pdf if log else math.exp(log_pdf)
    
    vals = [_dgamma_single(xi) for xi in xs]
    return vals[0] if isinstance(x, (int, float)) else vals

def pgamma(q: Union[Number, Iterable[Number]], shape: Number, rate: Number = 1.0,
           scale: Number = None, lower_tail: bool = True, log: bool = False):
    qs = _to_list(q)
    if shape <= 0:
        raise ValueError("shape must be > 0")
    if scale is not None:
        if scale <= 0:
            raise ValueError("scale must be > 0")
        rate = 1.0 / scale
    if rate <= 0:
        raise ValueError("rate must be > 0")
    
    def _pgamma_single(qi: Number) -> float:
        if qi <= 0:
            p = 0.0
        else:
            p = _incomplete_gamma_lower(shape, rate * qi)
        
        if not lower_tail:
            p = 1.0 - p
        
        if log:
            return -math.inf if p == 0.0 else math.log(p)
        else:
            return p
    
    vals = [_pgamma_single(qi) for qi in qs]
    return vals[0] if isinstance(q, (int, float)) else vals

def qgamma(p: Union[Number, Iterable[Number]], shape: Number, rate: Number = 1.0,
           scale: Number = None, lower_tail: bool = True, log: bool = False):
    ps = _to_list(p)
    if shape <= 0:
        raise ValueError("shape must be > 0")
    if scale is not None:
        if scale <= 0:
            raise ValueError("scale must be > 0")
        rate = 1.0 / scale
    if rate <= 0:
        raise ValueError("rate must be > 0")
    
    def to_prob(pp: float) -> float:
        if log:
            pp = math.exp(pp)
        return pp if lower_tail else 1.0 - pp
    
    def _qgamma_single(pp: Number) -> float:
        target_prob = to_prob(pp)
        if target_prob < 0.0 or target_prob > 1.0:
            return math.nan
        if target_prob == 0.0:
            return 0.0
        if target_prob == 1.0:
            return math.inf
        
        if shape < 1:
            x = math.pow(target_prob * math.gamma(shape + 1), 1.0/shape)
        else:
            x = shape - 1.0 + math.sqrt(shape) * (-1.0 + 2.0*target_prob)
        
        for _ in range(100):
            current_p = _incomplete_gamma_lower(shape, rate * x)
            if abs(current_p - target_prob) < 1e-12:
                break
            
            pdf = math.exp((shape - 1) * math.log(x) - rate * x + shape * math.log(rate) - math.lgamma(shape))
            if pdf == 0:
                break
            
            x += (target_prob - current_p) / (pdf * rate)
            if x <= 0:
                x = 1e-10
        
        return x / rate if scale is None else x
    
    vals = [_qgamma_single(pp) for pp in ps]
    return vals[0] if isinstance(p, (int, float)) else vals

def rgamma(n: int, shape: Number, rate: Number = 1.0, scale: Number = None):
    if n < 0:
        raise ValueError("n must be >= 0")
    if shape <= 0:
        raise ValueError("shape must be > 0")
    if scale is not None:
        if scale <= 0:
            raise ValueError("scale must be > 0")
        rate = 1.0 / scale
    if rate <= 0:
        raise ValueError("rate must be > 0")
    
    def _rgamma_single() -> float:
        if shape < 1:
            c = (1.0 / shape - 1.0) / (math.e - 1.0)
            while True:
                u = random.random()
                w = c * u
                if w <= 1:
                    x = math.pow(w, 1.0/shape)
                    if random.random() <= math.exp(-x):
                        return x / rate
                else:
                    x = -math.log((1.0 - w) / shape)
                    if random.random() <= math.pow(x, shape - 1):
                        return x / rate
        else:
            d = shape - 1.0/3.0
            c = 1.0 / math.sqrt(9.0 * d)
            
            while True:
                while True:
                    x = random.gauss(0, 1)
                    v = 1.0 + c * x
                    if v > 0:
                        break
                
                v = v * v * v
                u = random.random()
                
                if u < 1.0 - 0.0331 * x * x * x * x:
                    return d * v / rate
                
                if math.log(u) < 0.5 * x * x + d * (1.0 - v + math.log(v)):
                    return d * v / rate
    
    return [_rgamma_single() for _ in range(n)]