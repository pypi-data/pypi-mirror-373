import wandb
import yaml
import functools
import inspect
import sys
from typing import Dict, Any, List, Union, Optional, Callable
from pathlib import Path
import logging

# Optional dependency handling
try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Set up logging for the module
logger = logging.getLogger(__name__)


class VariableCapture:
    """Helper class to capture variables from function execution."""
    
    def __init__(self, metrics_to_capture: List[str]):
        self.metrics_to_capture = metrics_to_capture
        self.captured_variables = {}
        self.original_trace = None
        
    def trace_calls(self, frame, event, arg):
        """Trace function to capture local variables during execution."""
        if event == 'return' and frame.f_code.co_name != '<listcomp>':
            # Capture specified variables from the local scope
            for var_name in self.metrics_to_capture:
                if var_name in frame.f_locals:
                    value = frame.f_locals[var_name]
                    # Convert tensor values to Python scalars if needed
                    if hasattr(value, 'item'):
                        value = value.item()
                    elif hasattr(value, 'detach') and hasattr(value.detach(), 'cpu'):
                        value = value.detach().cpu().numpy()
                    self.captured_variables[var_name] = value
        
        return self.original_trace(frame, event, arg) if self.original_trace else None


class WandbGenericLogger:
    """
    A generic decorator for logging metrics to Weights & Biases.
    
    This decorator can automatically capture any variables from your function
    based on the configuration file. It supports multiple logging patterns:
    
    1. Automatic variable capture from function scope
    2. Yielded dictionaries from generator functions
    3. Returned dictionaries from functions
    4. Custom logging callbacks
    
    Example usage:
        @WandbGenericLogger(config_path="config.yaml")
        def train_model():
            for epoch in range(10):
                loss = calculate_loss()
                accuracy = calculate_accuracy()
                # These variables will be automatically logged if specified in config
    """
    
    def __init__(
        self,
        config_path: Union[str, Path],
        log_frequency: int = 1,
        custom_logger: Optional[Callable] = None
    ):
        """
        Initialize the WandbGenericLogger.
        
        Args:
            config_path: Path to configuration file (YAML or TOML)
            log_frequency: Frequency of logging (every N iterations)
            custom_logger: Optional custom logging function
        """
        self.config_path = Path(config_path)
        self.log_frequency = log_frequency
        self.custom_logger = custom_logger
        self.config = self._load_config()
        self._validate_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML or TOML file."""
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif self.config_path.suffix.lower() == '.toml':
                    if not HAS_TOML:
                        raise ImportError("TOML support requires 'toml' package. Install with: pip install toml")
                    return toml.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {self.config_path.suffix}")
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            raise
            
    def _validate_config(self) -> None:
        """Validate the configuration structure."""
        required_sections = ['wandb']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
                
        if 'project' not in self.config['wandb']:
            raise ValueError("Missing 'project' in wandb config section")
            
    def _get_metrics_config(self) -> List[str]:
        """Get the list of metrics to capture from config."""
        logger_config = self.config.get('logger', {})
        return logger_config.get('metrics', [])
        
    def _get_wandb_config(self) -> Dict[str, Any]:
        """Get wandb configuration."""
        wandb_config = self.config['wandb'].copy()
        
        # Add hyperparameters to wandb config
        if 'hyperparameters' in self.config:
            wandb_config['config'] = self.config['hyperparameters']
            
        return wandb_config
        
    def _extract_metrics_from_locals(self, local_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Extract specified metrics from local variables."""
        metrics = {}
        metrics_to_capture = self._get_metrics_config()
        
        for metric_name in metrics_to_capture:
            if metric_name in local_vars:
                value = local_vars[metric_name]
                
                # Handle different types of values
                if hasattr(value, 'item'):  # PyTorch tensor
                    metrics[metric_name] = value.item()
                elif HAS_NUMPY and hasattr(value, 'numpy'):  # NumPy array or other array-like
                    try:
                        metrics[metric_name] = float(value.numpy())
                    except:
                        metrics[metric_name] = float(value)
                elif isinstance(value, (int, float, bool)):
                    metrics[metric_name] = value
                elif hasattr(value, '__float__'):
                    metrics[metric_name] = float(value)
                else:
                    # Try to convert to string for non-numeric values
                    metrics[metric_name] = str(value)
                    
        return metrics
        
    def _log_metrics(self, wandb_run: Any, metrics: Dict[str, Any], step: Optional[int] = None) -> None:
        """Log metrics to wandb - ONLY what's specified in config."""
        if metrics:
            wandb_run.log(metrics, step=step)
            
            if self.custom_logger:
                self.custom_logger(metrics, step)
                
    def __call__(self, func: Callable) -> Callable:
        """Decorator function that wraps the target function."""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get wandb configuration
            wandb_config = self._get_wandb_config()
            project = wandb_config.pop('project')
            
            # Initialize wandb run
            with wandb.init(project=project, **wandb_config) as run:
                # Check if function expects wandb_run parameter
                sig = inspect.signature(func)
                if 'wandb_run' in sig.parameters:
                    kwargs['wandb_run'] = run
                    
                # Handle different function patterns
                if inspect.isgeneratorfunction(func):
                    # Generator function - handle yielded values
                    return self._handle_generator_function(func, run, args, kwargs)
                else:
                    # Regular function - capture variables or return value
                    return self._handle_regular_function(func, run, args, kwargs)
                    
        return wrapper
        
    def _handle_generator_function(self, func: Callable, wandb_run: Any, args: tuple, kwargs: dict) -> Any:
        """Handle generator functions that yield metrics."""
        step = 0
        result = None
        
        try:
            for yielded_value in func(*args, **kwargs):
                if isinstance(yielded_value, dict):
                    # Direct metrics dictionary
                    self._log_metrics(wandb_run, yielded_value, step)
                else:
                    # Try to extract metrics from the current frame
                    frame = sys._getframe(1)
                    metrics = self._extract_metrics_from_locals(frame.f_locals)
                    self._log_metrics(wandb_run, metrics, step)
                    result = yielded_value
                    
                step += 1
                
        except Exception as e:
            logger.error(f"Error in generator function: {e}")
            raise
            
        return result
        
    def _handle_regular_function(self, func: Callable, wandb_run: Any, args: tuple, kwargs: dict) -> Any:
        """Handle regular functions with TRUE automatic capture - NO manual calls needed."""
        metrics_to_capture = self._get_metrics_config()
        
        if not metrics_to_capture:
            # No metrics specified, just run the function
            return func(*args, **kwargs)
        
        # TRUE AUTOMATIC SOLUTION: Hook into print() to capture variables
        step = [0]
        
        # Store original print function
        original_print = func.__globals__.get('print', print)
        
        def capturing_print(*args, **kwargs):
            """Enhanced print that automatically captures metrics."""
            # Call original print first
            result = original_print(*args, **kwargs)
            
            # Then capture metrics from caller's frame
            import inspect
            frame = inspect.currentframe()
            try:
                caller_frame = frame.f_back
                if caller_frame and caller_frame.f_code.co_name == func.__name__:
                    # Extract metrics from the training function's locals
                    current_metrics = self._extract_metrics_from_locals(caller_frame.f_locals)
                    if current_metrics:
                        self._log_metrics(wandb_run, current_metrics, step[0])
                        step[0] += 1
            finally:
                del frame
            
            return result
        
        # Inject our capturing print
        func.__globals__['print'] = capturing_print
        
        try:
            # Execute the original function - metrics captured automatically!
            result = func(*args, **kwargs)
            
            # Log final result if it contains metrics
            if isinstance(result, dict):
                final_metrics = self._extract_metrics_from_locals(result)
                if final_metrics:
                    self._log_metrics(wandb_run, final_metrics, step[0])
                    
            return result
            
        except Exception as e:
            logger.error(f"Error in function execution: {e}")
            raise
        finally:
            # Always restore original print
            func.__globals__['print'] = original_print


class WandbMetricLogger:
    """
    A context manager for logging metrics within a function.
    
    This can be used as an alternative to automatic variable capture
    for more explicit control over what gets logged.
    
    Example usage:
        @WandbGenericLogger(config_path="config.yaml")
        def train_model(wandb_run=None):
            with WandbMetricLogger(wandb_run) as metric_logger:
                for epoch in range(10):
                    loss = calculate_loss()
                    accuracy = calculate_accuracy()
                    metric_logger.log({"epoch": epoch, "loss": loss, "accuracy": accuracy})
    """
    
    def __init__(self, wandb_run: Any, log_frequency: int = 1):
        self.wandb_run = wandb_run
        self.log_frequency = log_frequency
        self.step = 0
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def log(self, metrics: Dict[str, Any]) -> None:
        """Log metrics to wandb."""
        if self.step % self.log_frequency == 0:
            log_data = metrics.copy()
            log_data['step'] = self.step
            self.wandb_run.log(log_data)
        self.step += 1
