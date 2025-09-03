# WandB Generic Logger 🚀

[![PyPI version](https://img.shields.io/pypi/v/wandb-generic.svg)](https://pypi.org/project/wandb-generic/)
[![Python](https://img.shields.io/pypi/pyversions/wandb-generic.svg)](https://pypi.org/project/wandb-generic/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/wandb-generic)](https://pypi.org/project/wandb-generic/)
[![PyPI - Status](https://img.shields.io/pypi/status/wandb-generic)](https://pypi.org/project/wandb-generic/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/MayukhSobo/wandb-generic/actions/workflows/test.yml/badge.svg)](https://github.com/MayukhSobo/wandb-generic/actions/workflows/test.yml)
[![GitHub issues](https://img.shields.io/github/issues/MayukhSobo/wandb-generic)](https://github.com/MayukhSobo/wandb-generic/issues)
[![GitHub stars](https://img.shields.io/github/stars/MayukhSobo/wandb-generic)](https://github.com/MayukhSobo/wandb-generic/stargazers)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A **truly generic** and professional Python package that brings Weights & Biases experiment tracking to any ML/DL library or long-running function. No more manual logging - just specify what variables you want to track in a config file and let the magic happen!

## ✨ Key Features

- **🔧 Framework Agnostic**: Works with PyTorch, TensorFlow, scikit-learn, or any Python function
- **📝 Flexible Variable Logging**: Log ANY variables from your function by name - no hardcoded metrics
- **🎯 Multiple Logging Patterns**: Automatic capture, generator functions, context managers
- **🧪 Beyond ML**: Use for finance, physics, optimization, data processing - any domain
- **🔄 Hyperparameter Sweeps**: Built-in WandB sweep integration
- **💾 Model Checkpointing**: Automatic artifact logging
- **🚦 Professional**: Error handling, type hints, comprehensive validation

## 🚀 Quick Start

### Installation

```bash
pip install wandb-generic
```

### Basic Usage

1. **Create a config file** (`config.yaml`):

```yaml
wandb:
  project: "my-awesome-project"

hyperparameters:
  learning_rate: 0.01
  epochs: 10

logger:
  metrics:
    - loss        # ANY variable name from your function  
    - epoch       # Traditional names work
    - accuracy    # Descriptive names work
    - x           # Short names work (single letters)
    - y           # Any variables you create
```

2. **Add the decorator** to your function:

```python
from wandb_generic import WandbGenericLogger

@WandbGenericLogger(config_path="config.yaml")
def train_model(wandb_run=None):
    model = create_model()
    optimizer = torch.optim.Adam(model.parameters(), lr=wandb_run.config.learning_rate)
    
    for epoch in range(wandb_run.config.epochs):
        # Use ANY variable names you want!
        loss = train_one_epoch(model, optimizer)
        accuracy = validate_model(model)
        x = loss      # Custom names work too!
        y = epoch     # Any variable names
        
        # These variables are automatically logged! ✨
        # No manual wandb.log() calls needed
    
    return model

# Run your training
trained_model = train_model()
```

That's it! The decorator automatically captures and logs the variables specified in your config.

## 🎯 Framework Examples

### PyTorch

```python
@WandbGenericLogger(config_path="config.yaml")
def train_pytorch_model(wandb_run=None):
    model = torch.nn.Sequential(...)
    optimizer = torch.optim.Adam(model.parameters())
    
    for epoch in range(wandb_run.config.epochs):
        train_loss = train_one_epoch(model, optimizer)
        val_accuracy = validate_model(model)
        learning_rate = optimizer.param_groups[0]['lr']
        # Auto-logged based on config
```

### TensorFlow/Keras

```python
@WandbGenericLogger(config_path="config.yaml")
def train_tf_model(wandb_run=None):
    model = tf.keras.Sequential([...])
    
    for epoch in range(wandb_run.config.epochs):
        history = model.fit(x_train, y_train, validation_data=(x_val, y_val))
        train_loss = history.history['loss'][0]
        val_loss = history.history['val_loss'][0]
        val_accuracy = history.history['val_accuracy'][0]
        # Auto-logged based on config
```

### Scikit-learn

```python
@WandbGenericLogger(config_path="config.yaml")  
def train_sklearn_model(wandb_run=None):
    model = RandomForestClassifier()
    
    for n_estimators in [10, 50, 100, 200]:
        model.set_params(n_estimators=n_estimators)
        model.fit(X_train, y_train)
        
        train_score = model.score(X_train, y_train)
        val_score = model.score(X_val, y_val)
        feature_importance = model.feature_importances_.mean()
        # Auto-logged based on config
```

## 🧪 Beyond Machine Learning

This package works for ANY domain:

### Financial Analysis

```python
@WandbGenericLogger(config_path="config.yaml")
def analyze_trading_strategy(wandb_run=None):
    for trading_day in range(wandb_run.config.epochs):
        portfolio_return = execute_trading_strategy()
        sharpe_ratio = calculate_sharpe_ratio()
        max_drawdown = calculate_drawdown()
        volatility = calculate_volatility()
        # All metrics logged automatically
```

### Scientific Computing

```python
@WandbGenericLogger(config_path="config.yaml")
def simulate_physics(wandb_run=None):
    for time_step in range(wandb_run.config.epochs):
        kinetic_energy = calculate_kinetic_energy()
        potential_energy = calculate_potential_energy()
        total_energy = kinetic_energy + potential_energy
        system_temperature = calculate_temperature()
        # Physics metrics logged automatically
```

## 📁 Configuration Reference

### Complete YAML Configuration

```yaml
wandb:
  project: "project-name"           # Required
  entity: "your-entity"             # Optional
  tags: ["tag1", "tag2"]           # Optional
  notes: "Experiment description"   # Optional

hyperparameters:
  learning_rate: 0.01              # Any hyperparameters you want
  batch_size: 32
  epochs: 100

sweep:
  method: "bayes"                   # random, grid, bayes
  metric:
    name: "loss"                    # Any metric name from your function
    goal: "minimize"                # minimize or maximize
  parameters:
    learning_rate:
      values: [0.1, 0.01, 0.001]
    batch_size:
      values: [16, 32, 64]

logger:
  metrics:                          # List ANY variable names to log
    - loss
    - accuracy
    - epoch
    - custom_metric
    - processing_time
  log_frequency: 1                  # Log every N iterations

checkpoint:
  name: "my-model"
  type: "model"
  save_frequency: 5                 # Save every N epochs
```

## 🔄 Supported Logging Patterns

### 1. Automatic Variable Capture (Recommended)

```python
@WandbGenericLogger(config_path="config.yaml")
def my_function(wandb_run=None):
    for iteration in range(10):
        metric_value = compute_metric()
        loss_score = compute_loss()
        # Variables automatically logged if in config
```

### 2. Generator Functions

```python
@WandbGenericLogger(config_path="config.yaml")
def training_generator(wandb_run=None):
    for epoch in range(10):
        loss = train_epoch()
        yield {"loss": loss, "epoch": epoch}
```

### 3. Context Manager

```python
from wandb_generic import WandbMetricLogger

@WandbGenericLogger(config_path="config.yaml")
def explicit_logging(wandb_run=None):
    with WandbMetricLogger(wandb_run) as logger:
        for i in range(10):
            metric = compute_metric()
            logger.log({"iteration": i, "metric": metric})
```

## 🔧 Advanced Features

### Custom Logging Function

```python
def my_custom_logger(metrics, step):
    print(f"Step {step}: {metrics}")

@WandbGenericLogger(
    config_path="config.yaml",
    log_frequency=5,  # Log every 5 iterations
    custom_logger=my_custom_logger
)
def my_function(wandb_run=None):
    # Your code here
    pass
```

### Error Handling

The package includes comprehensive error handling:
- Validates config file structure
- Handles missing metrics gracefully  
- Converts tensor types automatically (PyTorch, NumPy)
- Provides helpful error messages

### Type Safety

Full type hints for better IDE support:

```python
from typing import Dict, Any, List
from wandb_generic import WandbGenericLogger, WandbMetricLogger
```

## 🚀 Migration from Manual Logging

**Before (Manual logging):**
```python
def train_model():
    wandb.init(project="my-project")
    
    for epoch in range(10):
        loss = train_epoch()
        acc = validate()
        
        wandb.log({
            "loss": loss,
            "accuracy": acc,
            "epoch": epoch
        })
```

**After (Generic logging):**
```python
@WandbGenericLogger(config_path="config.yaml")
def train_model(wandb_run=None):
    for epoch in range(wandb_run.config.epochs):
        loss = train_epoch()
        accuracy = validate()
        # That's it! No manual logging needed
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- 📖 **Documentation**: Complete examples in the `examples/` directory
- 🐛 **Issues**: Report bugs on our GitHub issues page
- 💬 **Discussions**: Join our community discussions

---

**Ready to make your experiment tracking effortless and truly generic? Install wandb-generic today!** 🚀
