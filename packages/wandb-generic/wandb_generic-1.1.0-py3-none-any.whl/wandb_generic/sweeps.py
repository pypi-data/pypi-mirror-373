import wandb
import yaml
import functools

class WandbGenericSweep:
    def __init__(self, config_path):
        self.config_path = config_path

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            if 'sweep' in config:
                sweep_config = config['sweep']
                sweep_id = wandb.sweep(sweep_config, project=config['wandb']['project'])
                wandb.agent(sweep_id, function=lambda: func(*args, **kwargs), count=5)
            else:
                func(*args, **kwargs)

        return wrapper
