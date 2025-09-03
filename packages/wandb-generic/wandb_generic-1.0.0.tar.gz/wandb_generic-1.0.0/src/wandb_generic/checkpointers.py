import wandb
import yaml
import functools
from typing import Optional, Any

# Optional dependency handling
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

class WandbGenericCheckpoint:
    def __init__(self, config_path):
        self.config_path = config_path

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            model = func(*args, **kwargs)

            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            if 'checkpoint' in config and wandb.run is not None:
                checkpoint_config = config['checkpoint']
                artifact = wandb.Artifact(checkpoint_config['name'], type=checkpoint_config['type'])
                
                # Handle PyTorch models if PyTorch is available
                if HAS_TORCH and hasattr(model, 'state_dict'):
                    torch.save(model.state_dict(), "model.pth")
                    artifact.add_file("model.pth")
                # Handle other model types (scikit-learn, etc.)
                elif hasattr(model, '__dict__'):
                    import pickle
                    with open("model.pkl", "wb") as f:
                        pickle.dump(model, f)
                    artifact.add_file("model.pkl")
                else:
                    # Generic fallback - log model as artifact metadata
                    print(f"Warning: Could not serialize model of type {type(model)}. Logging metadata only.")
                
                wandb.log_artifact(artifact)

            return model

        return wrapper
