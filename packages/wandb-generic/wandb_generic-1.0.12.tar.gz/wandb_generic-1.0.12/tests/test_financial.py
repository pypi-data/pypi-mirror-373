"""Tests for wandb-generic with financial analysis - proving it works beyond ML."""

import pytest
import sys
import os
import tempfile
import random
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_financial_analysis():
    """Test that the generic logger works for financial analysis."""
    from wandb_generic import WandbGenericLogger
    
    config_content = """
wandb:
  project: test-financial
  mode: disabled

logger:
  metrics:
    - trading_day
    - portfolio_return
    - sharpe_ratio
    - max_drawdown
    - volatility
    - total_pnl
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        @WandbGenericLogger(config_path=config_path)
        def analyze_trading_strategy(wandb_run=None):
            initial_capital = 10000
            portfolio_value = initial_capital
            daily_returns = []
            
            for trading_day in range(5):
                # Simulate trading strategy
                daily_return = random.uniform(-0.05, 0.08)  # -5% to +8%
                portfolio_value *= (1 + daily_return)
                daily_returns.append(daily_return)
                
                # Calculate financial metrics
                portfolio_return = (portfolio_value - initial_capital) / initial_capital
                
                # Calculate Sharpe ratio (simplified)
                if len(daily_returns) > 1:
                    import statistics
                    avg_return = statistics.mean(daily_returns)
                    std_return = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0.01
                    sharpe_ratio = avg_return / std_return if std_return > 0 else 0
                else:
                    sharpe_ratio = 0
                
                # Calculate max drawdown
                peak_value = max(portfolio_value, initial_capital)
                max_drawdown = (peak_value - portfolio_value) / peak_value
                
                # Calculate volatility
                volatility = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0
                
                # Total P&L
                total_pnl = portfolio_value - initial_capital
                
                # Variables to be captured (matching config)
                trading_day = trading_day
                portfolio_return = portfolio_return
                sharpe_ratio = sharpe_ratio
                max_drawdown = max_drawdown
                volatility = volatility
                total_pnl = total_pnl
            
            return {
                'final_portfolio_value': portfolio_value,
                'total_return': portfolio_return,
                'sharpe': sharpe_ratio
            }
        
        # Should work without errors
        result = analyze_trading_strategy()
        assert result is not None
        assert 'final_portfolio_value' in result
        assert 'total_return' in result
        
    finally:
        os.unlink(config_path)


def test_physics_simulation():
    """Test that the generic logger works for physics/scientific computing."""
    from wandb_generic import WandbGenericLogger
    import math
    
    config_content = """
wandb:
  project: test-physics
  mode: disabled

logger:
  metrics:
    - time_step
    - kinetic_energy
    - potential_energy
    - total_energy
    - temperature
    - momentum
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        @WandbGenericLogger(config_path=config_path)
        def simulate_physics(wandb_run=None):
            mass = 1.0
            position = 0.0
            velocity = 1.0
            k_spring = 0.1  # Spring constant
            
            for time_step in range(10):
                dt = 0.1
                
                # Simple harmonic oscillator simulation
                force = -k_spring * position
                acceleration = force / mass
                velocity += acceleration * dt
                position += velocity * dt
                
                # Calculate physics metrics
                kinetic_energy = 0.5 * mass * velocity**2
                potential_energy = 0.5 * k_spring * position**2
                total_energy = kinetic_energy + potential_energy
                temperature = abs(kinetic_energy * 100)  # Mock temperature
                momentum = mass * velocity
                
                # Variables to be captured
                time_step = time_step
                kinetic_energy = kinetic_energy
                potential_energy = potential_energy
                total_energy = total_energy
                temperature = temperature
                momentum = momentum
            
            return {'final_position': position, 'final_velocity': velocity}
        
        result = simulate_physics()
        assert result is not None
        assert 'final_position' in result
        
    finally:
        os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 