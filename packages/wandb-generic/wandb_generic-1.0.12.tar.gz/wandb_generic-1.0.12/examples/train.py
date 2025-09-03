"""
Simple examples showing WandbGenericLogger capabilities.

This demonstrates:
1. Basic usage with traditional variable names
2. Custom variable names (x, y) - answering the original question
3. Any domain flexibility (ML and beyond)
"""

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

import numpy as np
from wandb_generic import WandbGenericLogger, WandbGenericCheckpoint, WandbGenericSweep


# Define a simple model
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.linear = nn.Linear(10, 1)

    def forward(self, x):
        return self.linear(x)


# Example 1: Traditional training (your original example)
@WandbGenericSweep(config_path="examples/config.yaml")
@WandbGenericLogger(config_path="examples/config.yaml")
@WandbGenericCheckpoint(config_path="examples/config.yaml")
def train_traditional(wandb_run=None):
    """Traditional PyTorch training with standard variable names."""
    # Create dummy data
    X_train = torch.randn(100, 10)
    y_train = torch.randn(100, 1)

    # Initialize model, loss, and optimizer
    model = SimpleModel()
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=wandb_run.config.learning_rate)

    # Training loop
    for epoch in range(wandb_run.config.epochs):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss_tensor = criterion(outputs, y_train)
        loss_tensor.backward()
        optimizer.step()

        # Traditional variable names - automatically logged
        loss = loss_tensor.item()
        accuracy = np.random.random()  # Dummy accuracy
        learning_rate = optimizer.param_groups[0]['lr']
    
    return model


# Example 2: Custom variable names (x, y) - YOUR ORIGINAL QUESTION!
@WandbGenericLogger(config_path="examples/config.yaml")
def train_with_xy_variables(wandb_run=None):
    """
    Training with custom variable names 'x' and 'y'.
    This directly answers your original question!
    """
    model = SimpleModel()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=wandb_run.config.learning_rate)
    
    X_train = torch.randn(100, 10)
    y_train = torch.randn(100, 1)

    for ep in range(wandb_run.config.epochs):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss_tensor = criterion(outputs, y_train)
        loss_tensor.backward()
        optimizer.step()

        # Using YOUR variable names!
        x = loss_tensor.item()  # Loss stored in 'x'
        y = ep                  # Epoch stored in 'y'
        
        # These are automatically logged based on config.yaml!
        # No manual wandb.log() calls needed
    
    return model


# Example 3: Non-ML domain (showing true genericity)
@WandbGenericLogger(config_path="examples/config.yaml")
def analyze_data_processing(wandb_run=None):
    """
    Example showing the logger works for ANY domain, not just ML.
    This simulates a data processing pipeline.
    """
    total_records = 1000
    
    for batch_num in range(wandb_run.config.epochs):
        # Simulate data processing metrics
        records_processed = np.random.randint(50, 100)
        processing_time = np.random.uniform(0.1, 0.5)
        error_rate = np.random.uniform(0.01, 0.05)
        
        # Use any variable names that make sense for your domain
        loss_value = error_rate  # Error rate as "loss"
        epoch_num = batch_num    # Batch number as "epoch"
        x = processing_time      # Processing time as "x"
        y = records_processed    # Records as "y"
        accuracy = 1.0 - error_rate  # Success rate as "accuracy"
        
        # All automatically logged!
    
    return {
        'total_processed': total_records,
        'final_error_rate': error_rate
    }


def main():
    """Run the examples to demonstrate flexibility."""
    print("🚀 WandB Generic Logger Examples")
    print("=" * 40)
    
    if not HAS_TORCH:
        print("⚠️  PyTorch not available. Install with: pip install torch")
        print("    Running non-ML example only...")
        
        print("\n🔧 Non-ML domain (data processing)...")
        try:
            result3 = analyze_data_processing()
            print("✅ Data processing example completed!")
            print(f"   📈 Final error rate: {result3.get('final_error_rate', 0):.3%}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        return
    
    print("1. 📊 Traditional training (loss, epoch variables)...")
    try:
        model1 = train_traditional()
        print("✅ Traditional training completed!")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n2. 🎯 Custom variables (x, y) - YOUR ORIGINAL QUESTION...")
    try:
        model2 = train_with_xy_variables()
        print("✅ Custom x/y variables logged successfully!")
        print("   📊 Check WandB - you'll see 'x' and 'y' metrics logged!")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n3. 🔧 Non-ML domain (data processing)...")
    try:
        result3 = analyze_data_processing()
        print("✅ Data processing example completed!")
        print(f"   📈 Final error rate: {result3.get('final_error_rate', 0):.3%}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n🎉 All examples completed!")
    print("\n💡 Key Takeaway:")
    print("   You can use ANY variable names in your functions:")
    print("   - Traditional: loss, epoch, accuracy")
    print("   - Custom: x, y, z, custom_metric")
    print("   - Domain-specific: portfolio_return, error_rate, processing_time")
    print("   Just list them in your config.yaml file! 🚀")


if __name__ == "__main__":
    main()
