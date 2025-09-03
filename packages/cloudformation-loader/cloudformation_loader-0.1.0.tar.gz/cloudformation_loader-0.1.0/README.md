# cloudformation-loader

Import Python code embedded in CloudFormation Templates without hassle

## Description

When you author Lambda Functions inside CloudFormation templates you often have the choice of inlining the 
code or maintaining the code externally.

Maintaining the Lambda code separate from the CloudFormation Template forces you to use a solution that packages and uploads the code for you (SAM, CDK, etc). It makes testing very easy, since we can import our Lambda code as any other Python file via imports, but it is often a hassle because you have to have utilities installed in your environment.

Inlining the code is very convenient because you don't have to worry about multiple files or external utilities, but it makes testing almost impossible (since the code is "locked" inside the CloudFormation Template). Until now.

## Usage

```
import cloudformation_loader
cloudformation_loader.import_from_cloudformation('mycloudformation.yaml', 'module_name', 'LambdaLogicalId')

import module_name

# call and use the code inside the Lambda Function
module_name.my_function('test')

# you can even call the handler
module_name.handler({ 'testing': 'me' })

# or use pytest
import pytest
assert module_name.my_function('test') == 42
```

## Contributions

Thanks to Yuriy Kurylyak for ideas and feedback.

The CloudFormation YAML loading code was taken from https://github.com/awslabs/aws-cfn-template-flip

Contributions are more than welcome.

The source code is located here: https://github.com/pplu/cloudformation-loader

Issuses can be opened here: https://github.com/pplu/cloudformation-loader/issues

## Author

Jose Luis Martinez Torres (pplusdomain@gmail.com)

## Copyright and License

Copyright (c) 2025 by Jose Luis Martinez Torres

This project is Apache-2.0
