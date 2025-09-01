"""
Tests for enhanced performance metrics.
"""

import numpy as np
import pytest
from utils.metrics import (
    sharpe, sortino, max_drawdown, max_drawdown_duration,
    hit_rate, profit_factor, calmar_ratio, var, cvar,
    volatility, skewness, kurtosis, calculate_all_metrics,
    calculate_rolling_metrics, print_metrics_summary
)


class TestEnhancedMetrics:
    """Test class for enhanced performance metrics."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        self.returns = np.random.normal(0.001, 0.02, 1000)  # 1000 daily returns
        self.equity_curve = np.cumprod(1 + self.returns)
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        sharpe_val = sharpe(self.returns, risk_free=0.02, periods_per_year=252)
        assert isinstance(sharpe_val, float)
        assert not np.isnan(sharpe_val)
        assert not np.isinf(sharpe_val)
    
    def test_sortino_ratio(self):
        """Test Sortino ratio calculation."""
        sortino_val = sortino(self.returns, risk_free=0.02, periods_per_year=252)
        assert isinstance(sortino_val, float)
        assert not np.isnan(sortino_val)
        assert not np.isinf(sortino_val)
    
    def test_max_drawdown(self):
        """Test maximum drawdown calculation."""
        max_dd = max_drawdown(self.equity_curve)
        assert isinstance(max_dd, float)
        assert max_dd <= 0  # Drawdown should be negative or zero
        assert not np.isnan(max_dd)
    
    def test_max_drawdown_duration(self):
        """Test maximum drawdown duration calculation."""
        duration = max_drawdown_duration(self.equity_curve)
        assert isinstance(duration, int)
        assert duration >= 0
        assert duration <= len(self.returns)
    
    def test_hit_rate(self):
        """Test hit rate calculation."""
        hit_rate_val = hit_rate(self.returns)
        assert isinstance(hit_rate_val, float)
        assert 0 <= hit_rate_val <= 1
        assert not np.isnan(hit_rate_val)
    
    def test_profit_factor(self):
        """Test profit factor calculation."""
        pf = profit_factor(self.returns)
        assert isinstance(pf, float)
        assert pf >= 0
        assert not np.isnan(pf)
    
    def test_calmar_ratio(self):
        """Test Calmar ratio calculation."""
        calmar = calmar_ratio(self.returns, periods_per_year=252)
        assert isinstance(calmar, float)
        assert not np.isnan(calmar)
    
    def test_var(self):
        """Test Value at Risk calculation."""
        var_95 = var(self.returns, confidence_level=0.05)
        assert isinstance(var_95, float)
        assert not np.isnan(var_95)
    
    def test_cvar(self):
        """Test Conditional Value at Risk calculation."""
        cvar_95 = cvar(self.returns, confidence_level=0.05)
        assert isinstance(cvar_95, float)
        assert not np.isnan(cvar_95)
        assert cvar_95 <= var(self.returns, 0.05)  # CVaR should be <= VaR
    
    def test_volatility(self):
        """Test volatility calculation."""
        vol = volatility(self.returns, periods_per_year=252)
        assert isinstance(vol, float)
        assert vol >= 0
        assert not np.isnan(vol)
    
    def test_skewness(self):
        """Test skewness calculation."""
        skew = skewness(self.returns)
        assert isinstance(skew, float)
        assert not np.isnan(skew)
    
    def test_kurtosis(self):
        """Test kurtosis calculation."""
        kurt = kurtosis(self.returns)
        assert isinstance(kurt, float)
        assert not np.isnan(kurt)
    
    def test_calculate_all_metrics(self):
        """Test comprehensive metrics calculation."""
        metrics = calculate_all_metrics(
            self.returns, 
            equity_curve=self.equity_curve,
            risk_free_rate=0.02,
            periods_per_year=252
        )
        
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
        
        # Check that all expected keys are present
        expected_keys = [
            'total_return', 'annualized_return', 'volatility', 'sharpe_ratio',
            'sortino_ratio', 'max_drawdown', 'max_drawdown_duration', 'hit_rate',
            'profit_factor', 'calmar_ratio', 'var_95', 'cvar_95', 'skewness',
            'kurtosis', 'num_periods', 'positive_periods', 'negative_periods'
        ]
        
        for key in expected_keys:
            assert key in metrics
            assert not np.isnan(metrics[key])
    
    def test_calculate_rolling_metrics(self):
        """Test rolling metrics calculation."""
        rolling_metrics = calculate_rolling_metrics(self.returns, window=60)
        
        assert isinstance(rolling_metrics, np.ndarray) or hasattr(rolling_metrics, 'shape')
        assert len(rolling_metrics) > 0
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Empty array
        empty_returns = np.array([])
        assert sharpe(empty_returns) == 0.0
        assert max_drawdown(empty_returns) == 0.0
        assert hit_rate(empty_returns) == 0.0
        
        # Single value
        single_return = np.array([0.01])
        assert not np.isnan(sharpe(single_return))
        assert not np.isnan(max_drawdown(np.array([1.0, 1.01])))
        
        # All zeros
        zero_returns = np.zeros(100)
        assert sharpe(zero_returns) == 0.0
        assert max_drawdown(np.ones(100)) == 0.0
    
    def test_metrics_consistency(self):
        """Test that metrics are internally consistent."""
        metrics = calculate_all_metrics(self.returns, periods_per_year=252)
        
        # Check that positive + negative + zero periods equals total
        total_periods = metrics['positive_periods'] + metrics['negative_periods'] + metrics['zero_periods']
        assert total_periods == metrics['num_periods']
        
        # Check that hit rate matches positive periods
        expected_hit_rate = metrics['positive_periods'] / metrics['num_periods']
        assert abs(metrics['hit_rate'] - expected_hit_rate) < 1e-10
    
    def test_print_metrics_summary(self):
        """Test that print_metrics_summary doesn't crash."""
        metrics = calculate_all_metrics(self.returns)
        
        # This should not raise an exception
        try:
            print_metrics_summary(metrics)
        except Exception as e:
            pytest.fail(f"print_metrics_summary raised an exception: {e}")


if __name__ == "__main__":
    pytest.main([__file__]) 