"""Basic tests for wandb-generic package."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_package_import():
    """Test that the main package can be imported."""
    import wandb_generic
    assert hasattr(wandb_generic, "__version__")
    assert hasattr(wandb_generic, "WandbGenericLogger")
    assert hasattr(wandb_generic, "WandbMetricLogger")


# def test_version():
#     """Test that version is accessible."""
#     import wandb_generic
#     assert wandb_generic.__version__ == "1.0.6"


def test_logger_classes_exist():
    """Test that main classes can be imported."""
    from wandb_generic import WandbGenericLogger, WandbMetricLogger
    from wandb_generic import WandbGenericCheckpoint, WandbGenericSweep
    
    # These should be callable classes
    assert callable(WandbGenericLogger)
    assert callable(WandbMetricLogger)
    assert callable(WandbGenericCheckpoint)
    assert callable(WandbGenericSweep)


if __name__ == "__main__":
    pytest.main([__file__]) 