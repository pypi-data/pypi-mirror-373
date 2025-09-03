import pytest
import os

test1_file = f'{os.path.dirname(__file__)}/test1.yaml'

import cloudformation_loader

def test_syntaxerror():
    with pytest.raises(SyntaxError):
        cloudformation_loader.import_from_cloudformation(test1_file, 'cfn1', 'SyntaxError')

def test_nonexistantlambda():
    with pytest.raises(Exception):
        cloudformation_loader.import_from_cloudformation(test1_file, 'cfn1', 'NoLambda')

def test_nonexistantfile():
    with pytest.raises(Exception):
        cloudformation_loader.import_from_cloudformation('nonexistantfile.yaml', 'cfn1', 'Lambda')
