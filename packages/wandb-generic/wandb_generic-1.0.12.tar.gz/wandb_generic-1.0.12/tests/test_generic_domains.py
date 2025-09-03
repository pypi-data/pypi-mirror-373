"""Tests for wandb-generic with various non-ML domains."""

import pytest
import sys
import os
import tempfile
import random
import time
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_data_processing_pipeline():
    """Test generic logger with data processing workflows."""
    from wandb_generic import WandbGenericLogger
    
    config_content = """
wandb:
  project: test-data-processing
  mode: disabled

logger:
  metrics:
    - batch_number
    - records_processed
    - processing_rate
    - error_rate
    - memory_usage
    - processing_time
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        @WandbGenericLogger(config_path=config_path)
        def process_data_pipeline(wandb_run=None):
            total_records = 0
            total_errors = 0
            
            for batch_number in range(5):
                start_time = time.time()
                
                # Simulate data processing
                batch_size = random.randint(100, 1000)
                errors_in_batch = random.randint(0, 10)
                
                # Simulate processing
                time.sleep(0.01)  # Simulate work
                
                # Calculate metrics
                records_processed = batch_size
                total_records += records_processed
                total_errors += errors_in_batch
                
                processing_time = time.time() - start_time
                processing_rate = records_processed / processing_time if processing_time > 0 else 0
                error_rate = errors_in_batch / records_processed if records_processed > 0 else 0
                memory_usage = random.uniform(50, 95)  # Mock memory percentage
                
                # Variables to be captured
                batch_number = batch_number
                records_processed = records_processed
                processing_rate = processing_rate
                error_rate = error_rate
                memory_usage = memory_usage
                processing_time = processing_time
            
            return {
                'total_records': total_records,
                'total_errors': total_errors,
                'overall_error_rate': total_errors / total_records if total_records > 0 else 0
            }
        
        result = process_data_pipeline()
        assert result is not None
        assert result['total_records'] > 0
        
    finally:
        os.unlink(config_path)


def test_optimization_algorithm():
    """Test generic logger with optimization algorithms."""
    from wandb_generic import WandbGenericLogger
    import math
    
    config_content = """
wandb:
  project: test-optimization
  mode: disabled

logger:
  metrics:
    - iteration
    - objective_value
    - gradient_norm
    - step_size
    - convergence_rate
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        @WandbGenericLogger(config_path=config_path)
        def optimize_function(wandb_run=None):
            # Optimize a simple quadratic function: f(x) = (x - 3)^2 + 1
            x = 0.0  # Starting point
            step_size = 0.1
            prev_objective = float('inf')
            
            for iteration in range(10):
                # Calculate objective and gradient
                objective_value = (x - 3)**2 + 1
                gradient = 2 * (x - 3)
                gradient_norm = abs(gradient)
                
                # Update x using gradient descent
                x = x - step_size * gradient
                
                # Calculate convergence rate
                convergence_rate = abs(prev_objective - objective_value) if prev_objective != float('inf') else 0
                prev_objective = objective_value
                
                # Variables to be captured
                iteration = iteration
                objective_value = objective_value
                gradient_norm = gradient_norm
                step_size = step_size
                convergence_rate = convergence_rate
            
            return {'optimal_x': x, 'final_objective': objective_value}
        
        result = optimize_function()
        assert result is not None
        assert abs(result['optimal_x'] - 3.0) < 0.5  # Should converge toward x=3
        
    finally:
        os.unlink(config_path)


def test_ab_testing_analysis():
    """Test generic logger with A/B testing analysis."""
    from wandb_generic import WandbGenericLogger
    import random
    
    config_content = """
wandb:
  project: test-ab-testing
  mode: disabled

logger:
  metrics:
    - test_day
    - conversion_rate_a
    - conversion_rate_b
    - statistical_significance
    - sample_size_a
    - sample_size_b
    - lift_percentage
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        @WandbGenericLogger(config_path=config_path)
        def analyze_ab_test(wandb_run=None):
            for test_day in range(7):
                # Simulate A/B test data
                sample_size_a = random.randint(500, 1000)
                sample_size_b = random.randint(500, 1000)
                
                conversions_a = random.randint(int(sample_size_a * 0.05), int(sample_size_a * 0.15))
                conversions_b = random.randint(int(sample_size_b * 0.07), int(sample_size_b * 0.18))
                
                # Calculate metrics
                conversion_rate_a = conversions_a / sample_size_a
                conversion_rate_b = conversions_b / sample_size_b
                lift_percentage = ((conversion_rate_b - conversion_rate_a) / conversion_rate_a) * 100
                
                # Mock statistical significance calculation
                statistical_significance = min(0.95, 0.5 + test_day * 0.1)
                
                # Variables to be captured
                test_day = test_day
                conversion_rate_a = conversion_rate_a
                conversion_rate_b = conversion_rate_b
                statistical_significance = statistical_significance
                sample_size_a = sample_size_a
                sample_size_b = sample_size_b
                lift_percentage = lift_percentage
            
            return {
                'winner': 'B' if conversion_rate_b > conversion_rate_a else 'A',
                'final_lift': lift_percentage
            }
        
        result = analyze_ab_test()
        assert result is not None
        assert 'winner' in result
        
    finally:
        os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 