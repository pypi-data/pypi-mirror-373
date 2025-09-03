"""Tests for wandb-generic with scikit-learn integration."""

import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_sklearn_integration():
    """Test that the generic logger works with scikit-learn."""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
    except ImportError:
        pytest.skip("scikit-learn not available")
    
    from wandb_generic import WandbGenericLogger
    
    # Create test config
    config_content = """
wandb:
  project: test-sklearn
  mode: disabled

logger:
  metrics:
    - n_estimators
    - train_accuracy
    - val_accuracy
    - feature_importance_mean
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        # Generate test data
        X, y = make_classification(n_samples=100, n_features=10, n_classes=2, random_state=42)
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=42)
        
        @WandbGenericLogger(config_path=config_path)
        def train_sklearn_model(wandb_run=None):
            model = RandomForestClassifier(random_state=42)
            
            for n_estimators in [10, 20]:
                model.set_params(n_estimators=n_estimators)
                model.fit(X_train, y_train)
                
                # Variables that should be captured
                n_estimators = n_estimators
                train_accuracy = accuracy_score(y_train, model.predict(X_train))
                val_accuracy = accuracy_score(y_val, model.predict(X_val))
                feature_importance_mean = model.feature_importances_.mean()
            
            return model
        
        # Should work without errors
        result = train_sklearn_model()
        assert result is not None
        assert hasattr(result, 'predict')
        
    finally:
        os.unlink(config_path)


def test_sklearn_checkpointing():
    """Test that sklearn models can be checkpointed."""
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.datasets import make_classification
    except ImportError:
        pytest.skip("scikit-learn not available")
    
    from wandb_generic import WandbGenericCheckpoint
    
    config_content = """
wandb:
  project: test-sklearn-checkpoint
  mode: disabled

checkpoint:
  name: sklearn-model
  type: model
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        X, y = make_classification(n_samples=50, n_features=5, random_state=42)
        
        @WandbGenericCheckpoint(config_path=config_path)
        def train_sklearn_model():
            model = LogisticRegression(random_state=42)
            model.fit(X, y)
            return model
        
        # Should work without errors (wandb mode disabled so no actual logging)
        result = train_sklearn_model()
        assert result is not None
        
    finally:
        os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 