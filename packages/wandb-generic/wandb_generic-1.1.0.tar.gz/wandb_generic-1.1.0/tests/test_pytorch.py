"""Tests for wandb-generic with PyTorch integration."""

import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

pytest_plugins = []

def test_pytorch_integration():
    """Test that the generic logger works with PyTorch."""
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
    except ImportError:
        pytest.skip("PyTorch not available")
    
    from wandb_generic import WandbGenericLogger
    
    # Create a test config
    config_content = """
wandb:
  project: test-pytorch
  mode: disabled  # Don't actually log to wandb in tests

logger:
  metrics:
    - epoch
    - loss_value
    - accuracy_score
    - learning_rate
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        # Test PyTorch model training simulation
        @WandbGenericLogger(config_path=config_path)
        def train_pytorch_model(wandb_run=None):
            model = nn.Linear(10, 1)
            optimizer = optim.Adam(model.parameters(), lr=0.001)
            
            for epoch in range(3):
                # Simulate training
                x = torch.randn(32, 10)
                y = torch.randn(32, 1)
                
                optimizer.zero_grad()
                output = model(x)
                loss = nn.MSELoss()(output, y)
                loss.backward()
                optimizer.step()
                
                # Variables that should be captured
                epoch = epoch
                loss_value = loss.item()
                accuracy_score = 0.85 + epoch * 0.05  # Mock accuracy
                learning_rate = optimizer.param_groups[0]['lr']
            
            return model
        
        # This should work without errors
        result = train_pytorch_model()
        assert result is not None
        assert isinstance(result, nn.Module)
        
    finally:
        os.unlink(config_path)


def test_pytorch_tensor_conversion():
    """Test that PyTorch tensors are properly converted for logging."""
    try:
        import torch
    except ImportError:
        pytest.skip("PyTorch not available")
    
    from wandb_generic.loggers import VariableCapture
    
    # Test tensor conversion
    capture = VariableCapture(['tensor_value', 'scalar_value'])
    
    # Simulate capturing a PyTorch tensor
    tensor_value = torch.tensor(3.14)
    scalar_value = 42
    
    # Mock frame object for testing
    class MockFrame:
        def __init__(self):
            self.f_locals = {
                'tensor_value': tensor_value,
                'scalar_value': scalar_value
            }
            self.f_code = type('obj', (object,), {'co_name': 'test_function'})()
    
    frame = MockFrame()
    
    # Test the capture mechanism
    capture.trace_calls(frame, 'return', None)
    
    # Check that tensor was converted to Python scalar
    assert isinstance(capture.captured_variables['tensor_value'], (int, float))
    assert capture.captured_variables['scalar_value'] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 