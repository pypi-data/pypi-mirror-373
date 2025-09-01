from __future__ import annotations
import math
import random
from typing import Iterable, List, Union

Number = Union[int, float]

def _to_list(x: Union[Number, Iterable[Number]]) -> List[Number]:
    if isinstance(x, (int, float)):
        return [x]
    return list(x)

def _log_factorial(n: int) -> float:
    if n < 0:
        return -math.inf
    if n <= 1:
        return 0.0
    return sum(math.log(i) for i in range(2, n + 1))

def dpois(x: Union[Number, Iterable[Number]], lambda_: Number, log: bool = False):
    xs = _to_list(x)
    if lambda_ < 0:
        raise ValueError("lambda must be >= 0")
    
    def _dpois_single(xi: Number) -> float:
        if not isinstance(xi, int) or xi < 0:
            return -math.inf if log else 0.0
        
        if lambda_ == 0.0:
            return 0.0 if xi > 0 else (0.0 if log else 1.0)
        
        log_pmf = xi * math.log(lambda_) - lambda_ - _log_factorial(xi)
        return log_pmf if log else math.exp(log_pmf)
    
    vals = [_dpois_single(xi) for xi in xs]
    return vals[0] if isinstance(x, (int, float)) else vals

def ppois(q: Union[Number, Iterable[Number]], lambda_: Number,
          lower_tail: bool = True, log: bool = False):
    qs = _to_list(q)
    if lambda_ < 0:
        raise ValueError("lambda must be >= 0")
    
    def _incomplete_gamma_lower(a: float, x: float) -> float:
        if x <= 0:
            return 0.0
        if a <= 0:
            return 1.0
        
        sum_term = 0.0
        term = math.exp(-x + a * math.log(x) - math.lgamma(a))
        k = 0
        while term > 1e-15 and k < 1000:
            sum_term += term
            k += 1
            term *= x / (a + k - 1)
        return sum_term
    
    def _ppois_single(qi: Number) -> float:
        if qi < 0:
            p = 0.0
        else:
            k = int(math.floor(qi))
            if lambda_ == 0.0:
                p = 1.0
            else:
                p = 1.0 - _incomplete_gamma_lower(k + 1, lambda_)
        
        if not lower_tail:
            p = 1.0 - p
        
        if log:
            return -math.inf if p == 0.0 else math.log(p)
        else:
            return p
    
    vals = [_ppois_single(qi) for qi in qs]
    return vals[0] if isinstance(q, (int, float)) else vals

def qpois(p: Union[Number, Iterable[Number]], lambda_: Number,
          lower_tail: bool = True, log: bool = False):
    ps = _to_list(p)
    if lambda_ < 0:
        raise ValueError("lambda must be >= 0")
    
    def to_prob(pp: float) -> float:
        if log:
            pp = math.exp(pp)
        return pp if lower_tail else 1.0 - pp
    
    def _qpois_single(pp: Number) -> float:
        target_prob = to_prob(pp)
        if target_prob < 0.0 or target_prob > 1.0:
            return math.nan
        
        if target_prob == 0.0:
            return 0.0
        if lambda_ == 0.0:
            return 0.0
        
        cum_prob = 0.0
        k = 0
        max_k = int(lambda_ + 10 * math.sqrt(lambda_) + 100)
        
        while k <= max_k:
            pmf = math.exp(k * math.log(lambda_) - lambda_ - _log_factorial(k))
            cum_prob += pmf
            if cum_prob >= target_prob:
                return float(k)
            k += 1
        
        return float(k)
    
    vals = [_qpois_single(pp) for pp in ps]
    return vals[0] if isinstance(p, (int, float)) else vals

def rpois(n: int, lambda_: Number):
    if n < 0:
        raise ValueError("n must be >= 0")
    if lambda_ < 0:
        raise ValueError("lambda must be >= 0")
    
    def _rpois_single() -> int:
        if lambda_ == 0.0:
            return 0
        if lambda_ < 30.0:
            l = math.exp(-lambda_)
            k = 0
            p = 1.0
            while p > l:
                k += 1
                p *= random.random()
            return k - 1
        else:
            c = 7.0/8.0
            beta = math.pi / math.sqrt(3.0 * lambda_)
            alpha = beta * lambda_
            k = int(math.log(c) - lambda_ - math.log(beta))
            
            while True:
                u = random.random()
                if u == 0.0:
                    continue
                
                x = (alpha - math.log((1.0 - u) / u)) / beta
                n = int(math.floor(x + 0.5))
                if n < 0:
                    continue
                
                v = random.random()
                y = alpha - beta * x
                temp = 1.0 + math.exp(y)
                lhs = y + math.log(v / (temp * temp))
                rhs = k + n * math.log(lambda_) - lambda_ - _log_factorial(n)
                
                if lhs <= rhs:
                    return n
    
    return [_rpois_single() for _ in range(n)]