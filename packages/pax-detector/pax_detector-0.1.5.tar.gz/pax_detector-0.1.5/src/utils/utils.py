
import yaml
import json 
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def parse_config_yaml(config_file):
  if not config_file:
    raise FileNotFoundError(f'File do not exist {config_file}')

  with open(config_file, 'r') as stream:
    data = yaml.safe_load(stream)
  return data

