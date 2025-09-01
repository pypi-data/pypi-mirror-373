import math
from rthon import dnorm, pnorm, qnorm, rnorm

def almost(a, b, tol=1e-10): return abs(a-b) < tol or (math.isinf(a) and math.isinf(b))

def test_pnorm_basic():
    assert almost(pnorm(0.0), 0.5)
    assert almost(pnorm(1.96), 0.9750021048517796, 1e-12)

def test_qnorm_basic():
    assert almost(qnorm(0.5), 0.0)
    assert almost(qnorm(0.975), 1.959963984540054, 5e-7)  # bisection tol

def test_lower_tail_and_log():
    p = pnorm(1.0, lower_tail=False)
    assert almost(p, 1 - pnorm(1.0))
    logp = pnorm(1.0, log=True)
    assert almost(math.exp(logp), pnorm(1.0))

def test_dnorm_basic():
    assert almost(dnorm(0.0), 1.0 / math.sqrt(2*math.pi))
    assert almost(dnorm(0.0, log=True), math.log(1.0 / math.sqrt(2*math.pi)))

def test_rnorm_shape():
    xs = rnorm(5)
    assert len(xs) == 5

if __name__ == "__main__":
    print("Running normal distribution tests...")
    
    test_pnorm_basic()
    print("✓ test_pnorm_basic passed")
    
    test_qnorm_basic()
    print("✓ test_qnorm_basic passed")
    
    test_lower_tail_and_log()
    print("✓ test_lower_tail_and_log passed")
    
    test_dnorm_basic()
    print("✓ test_dnorm_basic passed")
    
    test_rnorm_shape()
    print("✓ test_rnorm_shape passed")
    
    print("\n🎉 All normal distribution tests passed!")
