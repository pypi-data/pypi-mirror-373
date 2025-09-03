"""Tests for wandb-generic with TensorFlow/Keras integration."""

import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_tensorflow_integration():
    """Test that the generic logger works with TensorFlow/Keras."""
    try:
        import tensorflow as tf
        import numpy as np
        # Disable GPU for testing
        tf.config.set_visible_devices([], 'GPU')
    except ImportError:
        pytest.skip("TensorFlow not available")
    
    from wandb_generic import WandbGenericLogger
    
    config_content = """
wandb:
  project: test-tensorflow
  mode: disabled

logger:
  metrics:
    - epoch
    - train_loss
    - val_loss
    - val_accuracy
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        # Generate test data
        X_train = np.random.randn(100, 10)
        y_train = np.random.randint(0, 2, (100, 1))
        X_val = np.random.randn(30, 10)
        y_val = np.random.randint(0, 2, (30, 1))
        
        @WandbGenericLogger(config_path=config_path)
        def train_tensorflow_model(wandb_run=None):
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            for epoch in range(2):
                # Simulate training
                history = model.fit(
                    X_train, y_train,
                    validation_data=(X_val, y_val),
                    epochs=1,
                    verbose=0
                )
                
                # Variables that should be captured
                epoch = epoch
                train_loss = history.history['loss'][0]
                val_loss = history.history['val_loss'][0]
                val_accuracy = history.history['val_accuracy'][0]
            
            return model
        
        # Should work without errors
        result = train_tensorflow_model()
        assert result is not None
        assert hasattr(result, 'predict')
        
    finally:
        os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 