import importlib.util
import sys
import os

import yaml
import types

from .yaml_loader import CfnYamlLoader
from .odict import ODict

def _get_cloudformation(file_path):
  with open(file_path, 'r') as stream:
    cfn = yaml.load(stream, Loader = CfnYamlLoader)
  return cfn

def extract_lambda_code(file_path, lambda_name):
  cfn = _get_cloudformation(file_path)
  return cfn['Resources'][ lambda_name ]['Properties']['Code']['ZipFile']

def get_environment(file_path, lambda_name):
  cfn = _get_cloudformation(file_path)
  return cfn['Resources'][ lambda_name ]['Properties']['Environment']['Variables']

def import_from_cloudformation(file_path, module_name, lambda_name = 'Lambda', env = None):
  python_code = extract_lambda_code(file_path, lambda_name)

  if env is not None:
    for k, v in env.items():
      os.environ[k] = v

  compiled_code = compile(python_code, 'In CloudFormation', 'exec')
  module = types.ModuleType(module_name)
  exec(compiled_code, module.__dict__)
  sys.modules[module_name] = module

  return module

if __name__ == '__main__':
  op = sys.argv[1]
  if op == 'get_code':
    print(extract_lambda_code(sys.argv[2], sys.argv[3]))
  else:
    print('unkown op')
