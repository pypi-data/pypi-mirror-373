# rthon

R-style probability functions for Python, providing familiar statistical distribution functions with R-compatible interfaces.

## Features

Currently supports these probability distributions:

- **Normal Distribution**: `dnorm`, `pnorm`, `qnorm`, `rnorm`
- **Uniform Distribution**: `dunif`, `punif`, `qunif`, `runif`
- **Binomial Distribution**: `dbinom`, `pbinom`, `qbinom`, `rbinom`
- **Poisson Distribution**: `dpois`, `ppois`, `qpois`, `rpois`
- **Exponential Distribution**: `dexp`, `pexp`, `qexp`, `rexp`
- **Gamma Distribution**: `dgamma`, `pgamma`, `qgamma`, `rgamma`

### TODO:
- Implement the lm() function, which uses the QR decomposition (WIP)
    - It does something, but is very wrong. Maybe look into using basic numpy functions
    - or vibe code some C/C++ functions, starting with very basic building blocks

## Installation

```bash
pip install rthon
```

## Quick Start

```python
from rprob import dnorm, pnorm, qnorm, rnorm

# Normal distribution examples
dnorm(0)        # PDF at x=0
pnorm(1.96)     # CDF at x=1.96
qnorm(0.975)    # Quantile for p=0.975
rnorm(10)       # 10 random samples

# All functions support R-style parameters
pnorm(1.96, lower_tail=False, log=True)
dnorm([0, 1, 2], mean=1, sd=2)
```

## License

MIT License 