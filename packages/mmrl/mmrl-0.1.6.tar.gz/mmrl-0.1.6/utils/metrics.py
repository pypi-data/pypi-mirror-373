import numpy as np
from typing import Tuple, Optional, Dict, Any
import pandas as pd


def sharpe(returns: np.ndarray, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Calculate the Sharpe ratio (annualized).
    
    Args:
        returns: Array of returns
        risk_free: Risk-free rate (annualized)
        periods_per_year: Number of periods per year (252 for daily, 12 for monthly)
    
    Returns:
        Annualized Sharpe ratio
    """
    returns = np.asarray(returns)
    if returns.size == 0:
        return 0.0
    
    # Handle single value case
    if returns.size == 1:
        return 0.0
    
    excess = returns - (risk_free / periods_per_year)
    std = excess.std(ddof=1)
    if std == 0:
        return 0.0
    
    # Annualize
    sharpe_ratio = (excess.mean() / std) * np.sqrt(periods_per_year)
    return float(sharpe_ratio)


def sortino(returns: np.ndarray, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Calculate the Sortino ratio (annualized).
    
    Args:
        returns: Array of returns
        risk_free: Risk-free rate (annualized)
        periods_per_year: Number of periods per year
    
    Returns:
        Annualized Sortino ratio
    """
    returns = np.asarray(returns)
    if returns.size == 0:
        return 0.0
    
    # Handle single value case
    if returns.size == 1:
        return 0.0
    
    excess = returns - (risk_free / periods_per_year)
    # Only consider downside deviations
    downside_returns = excess[excess < 0]
    
    if downside_returns.size == 0:
        return float('inf') if excess.mean() > 0 else 0.0
    
    downside_std = downside_returns.std(ddof=1)
    if downside_std == 0:
        return 0.0
    
    # Annualize
    sortino_ratio = (excess.mean() / downside_std) * np.sqrt(periods_per_year)
    return float(sortino_ratio)


def max_drawdown(equity_curve: np.ndarray) -> float:
    """
    Calculate maximum drawdown as a percentage.
    
    Args:
        equity_curve: Array of cumulative equity values
    
    Returns:
        Maximum drawdown as a percentage (negative value)
    """
    equity = np.asarray(equity_curve)
    if equity.size == 0:
        return 0.0
    
    # Handle single value case
    if equity.size == 1:
        return 0.0
    
    running_max = np.maximum.accumulate(equity)
    # Avoid division by zero
    denom = np.where(running_max == 0, 1.0, running_max)
    drawdowns = (equity - running_max) / denom
    return float(drawdowns.min())


def max_drawdown_duration(equity_curve: np.ndarray) -> int:
    """
    Calculate the duration of the maximum drawdown in periods.
    
    Args:
        equity_curve: Array of cumulative equity values
    
    Returns:
        Duration of maximum drawdown in periods
    """
    equity = np.asarray(equity_curve)
    if equity.size == 0:
        return 0
    
    running_max = np.maximum.accumulate(equity)
    drawdown_periods = equity < running_max
    
    if not np.any(drawdown_periods):
        return 0
    
    # Find longest consecutive drawdown period
    max_duration = 0
    current_duration = 0
    
    for in_drawdown in drawdown_periods:
        if in_drawdown:
            current_duration += 1
            max_duration = max(max_duration, current_duration)
        else:
            current_duration = 0
    
    return max_duration


def hit_rate(returns: np.ndarray) -> float:
    """
    Calculate the win rate (percentage of positive returns).
    
    Args:
        returns: Array of returns
    
    Returns:
        Win rate as a percentage
    """
    returns = np.asarray(returns)
    if returns.size == 0:
        return 0.0
    return float((returns > 0).mean())


def profit_factor(returns: np.ndarray) -> float:
    """
    Calculate the profit factor (gross profit / gross loss).
    
    Args:
        returns: Array of returns
    
    Returns:
        Profit factor (ratio of gross profit to gross loss)
    """
    returns = np.asarray(returns)
    if returns.size == 0:
        return 0.0
    
    gross_profit = returns[returns > 0].sum()
    gross_loss = abs(returns[returns < 0].sum())
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    return float(gross_profit / gross_loss)


def calmar_ratio(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """
    Calculate the Calmar ratio (annualized return / maximum drawdown).
    
    Args:
        returns: Array of returns
        periods_per_year: Number of periods per year
    
    Returns:
        Calmar ratio
    """
    returns = np.asarray(returns)
    if returns.size == 0:
        return 0.0
    
    # Calculate cumulative equity curve
    equity_curve = np.cumprod(1 + returns)
    max_dd = abs(max_drawdown(equity_curve))
    
    if max_dd == 0:
        return 0.0
    
    # Annualized return
    total_return = (equity_curve[-1] / equity_curve[0]) - 1
    annualized_return = (1 + total_return) ** (periods_per_year / len(returns)) - 1
    
    return float(annualized_return / max_dd)


def var(returns: np.ndarray, confidence_level: float = 0.05) -> float:
    """
    Calculate Value at Risk (VaR) at specified confidence level.
    
    Args:
        returns: Array of returns
        confidence_level: Confidence level (e.g., 0.05 for 95% VaR)
    
    Returns:
        VaR as a percentage (negative value)
    """
    returns = np.asarray(returns)
    if returns.size == 0:
        return 0.0
    
    return float(np.percentile(returns, confidence_level * 100))


def cvar(returns: np.ndarray, confidence_level: float = 0.05) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) at specified confidence level.
    
    Args:
        returns: Array of returns
        confidence_level: Confidence level (e.g., 0.05 for 95% CVaR)
    
    Returns:
        CVaR as a percentage (negative value)
    """
    returns = np.asarray(returns)
    if returns.size == 0:
        return 0.0
    
    var_threshold = var(returns, confidence_level)
    tail_returns = returns[returns <= var_threshold]
    
    if tail_returns.size == 0:
        return 0.0
    
    return float(tail_returns.mean())


def volatility(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """
    Calculate annualized volatility.
    
    Args:
        returns: Array of returns
        periods_per_year: Number of periods per year
    
    Returns:
        Annualized volatility as a percentage
    """
    returns = np.asarray(returns)
    if returns.size == 0:
        return 0.0
    
    # Handle single value case
    if returns.size == 1:
        return 0.0
    
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year))


def skewness(returns: np.ndarray) -> float:
    """
    Calculate the skewness of returns.
    
    Args:
        returns: Array of returns
    
    Returns:
        Skewness measure
    """
    returns = np.asarray(returns)
    if returns.size < 3:
        return 0.0
    
    mean = returns.mean()
    std = returns.std(ddof=1)
    if std == 0:
        return 0.0
    
    skew = np.mean(((returns - mean) / std) ** 3)
    return float(skew)


def kurtosis(returns: np.ndarray) -> float:
    """
    Calculate the kurtosis of returns.
    
    Args:
        returns: Array of returns
    
    Returns:
        Kurtosis measure
    """
    returns = np.asarray(returns)
    if returns.size < 4:
        return 0.0
    
    mean = returns.mean()
    std = returns.std(ddof=1)
    if std == 0:
        return 0.0
    
    kurt = np.mean(((returns - mean) / std) ** 4) - 3  # Excess kurtosis
    return float(kurt)


def calculate_all_metrics(returns: np.ndarray, 
                         equity_curve: Optional[np.ndarray] = None,
                         risk_free_rate: float = 0.02,
                         periods_per_year: int = 252) -> Dict[str, float]:
    """
    Calculate all performance metrics for a given return series.
    
    Args:
        returns: Array of returns
        equity_curve: Optional cumulative equity curve (if not provided, will be calculated)
        risk_free_rate: Annual risk-free rate (default: 2%)
        periods_per_year: Number of periods per year (default: 252 for daily)
    
    Returns:
        Dictionary containing all calculated metrics
    """
    returns = np.asarray(returns)
    if returns.size == 0:
        return {}
    
    # Calculate equity curve if not provided
    if equity_curve is None:
        equity_curve = np.cumprod(1 + returns)
    
    metrics = {
        'total_return': float((equity_curve[-1] / equity_curve[0]) - 1),
        'annualized_return': float((1 + (equity_curve[-1] / equity_curve[0] - 1)) ** (periods_per_year / len(returns)) - 1),
        'volatility': volatility(returns, periods_per_year),
        'sharpe_ratio': sharpe(returns, risk_free_rate, periods_per_year),
        'sortino_ratio': sortino(returns, risk_free_rate, periods_per_year),
        'max_drawdown': max_drawdown(equity_curve),
        'max_drawdown_duration': max_drawdown_duration(equity_curve),
        'hit_rate': hit_rate(returns),
        'profit_factor': profit_factor(returns),
        'calmar_ratio': calmar_ratio(returns, periods_per_year),
        'var_95': var(returns, 0.05),
        'cvar_95': cvar(returns, 0.05),
        'skewness': skewness(returns),
        'kurtosis': kurtosis(returns),
        'num_periods': len(returns),
        'positive_periods': int((returns > 0).sum()),
        'negative_periods': int((returns < 0).sum()),
        'zero_periods': int((returns == 0).sum())
    }
    
    return metrics


def calculate_rolling_metrics(returns: np.ndarray, 
                             window: int = 252,
                             periods_per_year: int = 252) -> pd.DataFrame:
    """
    Calculate rolling performance metrics over a specified window.
    
    Args:
        returns: Array of returns
        window: Rolling window size in periods
        periods_per_year: Number of periods per year
    
    Returns:
        DataFrame with rolling metrics
    """
    returns = pd.Series(returns)
    
    rolling_metrics = pd.DataFrame()
    
    # Rolling Sharpe ratio
    rolling_metrics['rolling_sharpe'] = returns.rolling(window).apply(
        lambda x: sharpe(x.values, periods_per_year=periods_per_year)
    )
    
    # Rolling volatility
    rolling_metrics['rolling_volatility'] = returns.rolling(window).apply(
        lambda x: volatility(x.values, periods_per_year=periods_per_year)
    )
    
    # Rolling max drawdown (requires equity curve)
    equity_curve = (1 + returns).cumprod()
    rolling_metrics['rolling_max_dd'] = equity_curve.rolling(window).apply(
        lambda x: max_drawdown(x.values)
    )
    
    return rolling_metrics


def print_metrics_summary(metrics: Dict[str, float]) -> None:
    """
    Print a formatted summary of performance metrics.
    
    Args:
        metrics: Dictionary of metrics from calculate_all_metrics
    """
    if not metrics:
        print("No metrics available.")
        return
    
    print("\n" + "="*60)
    print("PERFORMANCE METRICS SUMMARY")
    print("="*60)
    
    # Returns
    print(f"{'Total Return:':<25} {metrics.get('total_return', 0):>8.2%}")
    print(f"{'Annualized Return:':<25} {metrics.get('annualized_return', 0):>8.2%}")
    print(f"{'Volatility:':<25} {metrics.get('volatility', 0):>8.2%}")
    
    # Risk-adjusted returns
    print(f"\n{'RISK-ADJUSTED RETURNS'}")
    print("-" * 40)
    print(f"{'Sharpe Ratio:':<25} {metrics.get('sharpe_ratio', 0):>8.2f}")
    print(f"{'Sortino Ratio:':<25} {metrics.get('sortino_ratio', 0):>8.2f}")
    print(f"{'Calmar Ratio:':<25} {metrics.get('calmar_ratio', 0):>8.2f}")
    
    # Risk metrics
    print(f"\n{'RISK METRICS'}")
    print("-" * 40)
    print(f"{'Max Drawdown:':<25} {metrics.get('max_drawdown', 0):>8.2%}")
    print(f"{'Max DD Duration:':<25} {metrics.get('max_drawdown_duration', 0):>8} periods")
    print(f"{'VaR (95%):':<25} {metrics.get('var_95', 0):>8.2%}")
    print(f"{'CVaR (95%):':<25} {metrics.get('cvar_95', 0):>8.2%}")
    
    # Trading metrics
    print(f"\n{'TRADING METRICS'}")
    print("-" * 40)
    print(f"{'Hit Rate:':<25} {metrics.get('hit_rate', 0):>8.2%}")
    print(f"{'Profit Factor:':<25} {metrics.get('profit_factor', 0):>8.2f}")
    
    # Distribution metrics
    print(f"\n{'DISTRIBUTION'}")
    print("-" * 40)
    print(f"{'Skewness:':<25} {metrics.get('skewness', 0):>8.2f}")
    print(f"{'Kurtosis:':<25} {metrics.get('kurtosis', 0):>8.2f}")
    
    # Summary
    print(f"\n{'SUMMARY'}")
    print("-" * 40)
    print(f"{'Total Periods:':<25} {metrics.get('num_periods', 0):>8}")
    print(f"{'Positive Periods:':<25} {metrics.get('positive_periods', 0):>8}")
    print(f"{'Negative Periods:':<25} {metrics.get('negative_periods', 0):>8}")
    print("="*60)

