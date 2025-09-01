"""
Statistical utilities for linear regression.
Uses the probability distributions from the parent package.
"""

from __future__ import annotations
import math
from typing import List, Tuple, Dict, Any, Optional

# Import our probability functions
from ..distributions import pnorm, qnorm

Vector = List[float]
Matrix = List[List[float]]

def mean(x: Vector) -> float:
    """Calculate the mean of a vector."""
    return sum(x) / len(x) if x else 0.0

def variance(x: Vector, ddof: int = 1) -> float:
    """Calculate the sample variance of a vector."""
    if len(x) <= ddof:
        return 0.0
    
    x_mean = mean(x)
    return sum((xi - x_mean) ** 2 for xi in x) / (len(x) - ddof)

def standard_deviation(x: Vector, ddof: int = 1) -> float:
    """Calculate the sample standard deviation of a vector."""
    return math.sqrt(variance(x, ddof))

def sum_of_squares_total(y: Vector) -> float:
    """Calculate total sum of squares (TSS)."""
    y_mean = mean(y)
    return sum((yi - y_mean) ** 2 for yi in y)

def sum_of_squares_residual(residuals: Vector) -> float:
    """Calculate residual sum of squares (RSS)."""
    return sum(r * r for r in residuals)

def sum_of_squares_regression(y: Vector, fitted: Vector) -> float:
    """Calculate regression sum of squares (ESS)."""
    y_mean = mean(y)
    return sum((fi - y_mean) ** 2 for fi in fitted)

def r_squared(y: Vector, fitted: Vector) -> float:
    """Calculate R-squared (coefficient of determination)."""
    tss = sum_of_squares_total(y)
    residuals = [y[i] - fitted[i] for i in range(len(y))]
    rss = sum_of_squares_residual(residuals)
    
    if tss == 0:
        return 1.0
    
    return 1.0 - (rss / tss)

def adjusted_r_squared(y: Vector, fitted: Vector, p: int) -> float:
    """
    Calculate adjusted R-squared.
    p = number of parameters (including intercept)
    """
    n = len(y)
    r2 = r_squared(y, fitted)
    
    if n <= p:
        return 0.0
    
    return 1.0 - (1.0 - r2) * (n - 1) / (n - p)

def residual_standard_error(residuals: Vector, df_residual: int) -> float:
    """Calculate residual standard error."""
    if df_residual <= 0:
        return 0.0
    
    rss = sum_of_squares_residual(residuals)
    return math.sqrt(rss / df_residual)

def standard_errors(X_t_X_inv: Matrix) -> Vector:
    """
    Calculate standard errors of coefficients.
    X_t_X_inv should be (X^T X)^(-1) * sigma^2
    """
    return [math.sqrt(X_t_X_inv[i][i]) for i in range(len(X_t_X_inv))]

def t_statistics(coefficients: Vector, std_errors: Vector) -> Vector:
    """Calculate t-statistics for coefficients."""
    return [coef / se if se != 0 else 0.0 for coef, se in zip(coefficients, std_errors)]

def p_values_t(t_stats: Vector, df: int) -> Vector:
    """
    Calculate two-tailed p-values from t-statistics.
    Note: We'll need to implement pt() function in distributions
    """
    p_vals = []
    for t in t_stats:
        if df <= 0:
            p_vals.append(1.0)
        else:
            # Two-tailed test: P(|T| > |t|) = 2 * P(T > |t|)
            # For now, use normal approximation for large df
            if df >= 30:
                # Use normal approximation
                p = 2.0 * (1.0 - pnorm(abs(t)))
            else:
                # For small df, we need t-distribution
                # This is a simplified approximation - we should implement pt()
                p = 2.0 * (1.0 - pnorm(abs(t)))
            p_vals.append(p)
    
    return p_vals

def confidence_intervals(coefficients: Vector, std_errors: Vector, 
                        df: int, alpha: float = 0.05) -> List[Tuple[float, float]]:
    """
    Calculate confidence intervals for coefficients.
    alpha = significance level (0.05 for 95% CI)
    """
    # Critical t-value
    if df >= 30:
        # Use normal approximation
        t_crit = qnorm(1 - alpha/2)
    else:
        # Should use qt() when available
        t_crit = qnorm(1 - alpha/2)  # Normal approximation for now
    
    intervals = []
    for coef, se in zip(coefficients, std_errors):
        margin = t_crit * se
        intervals.append((coef - margin, coef + margin))
    
    return intervals

def anova_table(y: Vector, fitted: Vector, residuals: Vector, 
                p: int) -> Dict[str, Any]:
    """
    Create ANOVA table for regression.
    p = number of parameters (including intercept)
    """
    n = len(y)
    df_model = p - 1  # Degrees of freedom for model (excluding intercept)
    df_residual = n - p  # Degrees of freedom for residuals
    df_total = n - 1  # Total degrees of freedom
    
    # Sum of squares
    tss = sum_of_squares_total(y)
    ess = sum_of_squares_regression(y, fitted)
    rss = sum_of_squares_residual(residuals)
    
    # Mean squares
    mse_model = ess / df_model if df_model > 0 else 0.0
    mse_residual = rss / df_residual if df_residual > 0 else 0.0
    
    # F-statistic
    f_stat = mse_model / mse_residual if mse_residual != 0 else 0.0
    
    # F p-value (simplified - should use F-distribution)
    # For now, this is a placeholder
    f_p_value = 0.0 if f_stat > 10 else 0.1  # Simplified
    
    return {
        'df_model': df_model,
        'df_residual': df_residual, 
        'df_total': df_total,
        'ss_model': ess,
        'ss_residual': rss,
        'ss_total': tss,
        'ms_model': mse_model,
        'ms_residual': mse_residual,
        'f_statistic': f_stat,
        'f_p_value': f_p_value
    }

def cook_distance(residuals: Vector, leverage: Vector, 
                 mse: float, p: int) -> Vector:
    """
    Calculate Cook's distance for outlier detection.
    """
    cooks_d = []
    for i, (resid, h) in enumerate(zip(residuals, leverage)):
        if 1 - h != 0 and mse != 0:
            d = (resid ** 2 / (p * mse)) * (h / (1 - h) ** 2)
            cooks_d.append(d)
        else:
            cooks_d.append(0.0)
    
    return cooks_d

def leverage_values(X: Matrix) -> Vector:
    """
    Calculate leverage values (hat matrix diagonal).
    This requires computing H = X(X'X)^(-1)X'
    This is a simplified version.
    """
    # This is a placeholder - proper implementation requires
    # the hat matrix calculation
    n = len(X)
    p = len(X[0]) if X else 0
    
    # Average leverage is p/n
    avg_leverage = p / n if n > 0 else 0.0
    
    # Return uniform leverage for now (should be calculated properly)
    return [avg_leverage] * n

def studentized_residuals(residuals: Vector, leverage: Vector, 
                         mse: float) -> Vector:
    """Calculate studentized residuals."""
    studentized = []
    for resid, h in zip(residuals, leverage):
        if 1 - h > 0 and mse > 0:
            sr = resid / math.sqrt(mse * (1 - h))
            studentized.append(sr)
        else:
            studentized.append(0.0)
    
    return studentized

def durbin_watson_statistic(residuals: Vector) -> float:
    """
    Calculate Durbin-Watson statistic for autocorrelation.
    """
    if len(residuals) < 2:
        return 0.0
    
    numerator = sum((residuals[i] - residuals[i-1]) ** 2 
                   for i in range(1, len(residuals)))
    denominator = sum(r ** 2 for r in residuals)
    
    return numerator / denominator if denominator != 0 else 0.0