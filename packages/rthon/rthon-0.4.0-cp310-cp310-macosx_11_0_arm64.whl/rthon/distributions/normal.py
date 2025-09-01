from __future__ import annotations
import math
import random
from typing import Iterable, List, Union

Number = Union[int, float]

_TAU = 2.0 * math.pi
_SQRT2 = math.sqrt(2.0)

def _to_list(x: Union[Number, Iterable[Number]]) -> List[Number]:
    if isinstance(x, (int, float)):
        return [x]
    return list(x)

def dnorm(x: Union[Number, Iterable[Number]], mean: Number = 0.0, sd: Number = 1.0, log: bool = False):
    xs = _to_list(x)
    if sd <= 0:
        raise ValueError("sd must be > 0")
    z2s = [((xi - mean) / sd) ** 2 for xi in xs]
    log_pdf = [-(0.5 * z2) - (math.log(sd) + 0.5 * math.log(_TAU)) for z2 in z2s]
    vals = log_pdf if log else [math.exp(v) for v in log_pdf]
    return vals[0] if isinstance(x, (int, float)) else vals

def pnorm(q: Union[Number, Iterable[Number]], mean: Number = 0.0, sd: Number = 1.0,
          lower_tail: bool = True, log: bool = False):
    qs = _to_list(q)
    if sd <= 0:
        raise ValueError("sd must be > 0")
    z = [((qi - mean) / sd) for qi in qs]
    # Phi(z) = 0.5 * [1 + erf(z / sqrt(2))]
    base = [(0.5 * (1.0 + math.erf(zi / _SQRT2))) for zi in z]
    p = base if lower_tail else [1.0 - b for b in base]
    if log:
        # Match R’s log.p semantics (log of probability, not log10)
        out = [(-math.inf if v == 0.0 else math.log(v)) for v in p]
    else:
        out = p
    return out[0] if isinstance(q, (int, float)) else out

def _pnorm_scalar(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / _SQRT2))

def qnorm(p: Union[Number, Iterable[Number]], mean: Number = 0.0, sd: Number = 1.0,
          lower_tail: bool = True, log: bool = False, tol: float = 1e-12, max_iter: int = 200):
    ps = _to_list(p)

    def to_prob(pp: float) -> float:
        if log:
            pp = math.exp(pp)
        return pp if lower_tail else 1.0 - pp

    def inv_phi(prob: float) -> float:
        # Robust bracketed solve (bisection) with no external deps.
        if prob <= 0.0:  return -math.inf
        if prob >= 1.0:  return  math.inf
        lo, hi = -10.0, 10.0  # ~covers doubles for normal tail
        for _ in range(max_iter):
            mid = 0.5 * (lo + hi)
            pmid = _pnorm_scalar(mid)
            if abs(pmid - prob) < tol:
                return mid
            if pmid < prob:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    zs = [inv_phi(to_prob(pp)) for pp in ps]
    out = [mean + sd * zi for zi in zs]
    return out[0] if isinstance(p, (int, float)) else out

def rnorm(n: int, mean: Number = 0.0, sd: Number = 1.0):
    if n < 0:
        raise ValueError("n must be >= 0")
    if sd <= 0:
        raise ValueError("sd must be > 0")
    return [mean + sd * random.gauss(0.0, 1.0) for _ in range(n)]
