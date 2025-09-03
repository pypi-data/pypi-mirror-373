import pytest
import os

test1_file = f'{os.path.dirname(__file__)}/test1.yaml'

import cloudformation_loader
cloudformation_loader.import_from_cloudformation(test1_file, 'cfn1', 'Test1')

import cfn1

def test_call_functions():
  # call and use the code inside the Lambda Function
  assert cfn1.get_sum(39, 3) == 42

  # call the handler
  assert cfn1.handler({ }, {}) == { 'my': { 'lambda': 'return' } }
