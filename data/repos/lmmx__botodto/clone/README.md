# botodto

Pydantic model codegen from AWS OpenAPI schemas generated from the AWS JS/TS SDK (v3)

## Installation

Requires Python 3.9+

```sh
pip install botodto
```

To develop this library see [DEVELOP.md](https://github.com/lmmx/botodto/tree/master/DEVELOP.md)

## Usage

Swap out `boto3.client` for `botodto.client` and all your responses and errors will be ingested as
Pydantic data models.

```py
import botodto

client = botodto.client("stepfunctions")
client._namespace.print_v3_bonus_shape_members()
```
⇣
```py
ActivityDoesNotExist         {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
ActivityLimitExceeded        {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
ActivityWorkerLimitExceeded  {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
ExecutionAlreadyExists       {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
ExecutionDoesNotExist        {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
ExecutionLimitExceeded       {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
InvalidArn                   {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
InvalidDefinition            {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
InvalidExecutionInput        {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
InvalidLoggingConfiguration  {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
InvalidName                  {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
InvalidOutput                {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
InvalidToken                 {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
InvalidTracingConfiguration  {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
MissingRequiredParameter     {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
ResourceNotFound             {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}, 'resourceName': {'target': 'com.amazonaws.sfn#Arn'}}
StateMachineAlreadyExists    {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
StateMachineDeleting         {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
StateMachineDoesNotExist     {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
StateMachineLimitExceeded    {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
StateMachineTypeNotSupported {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
TaskDoesNotExist             {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
TaskTimedOut                 {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}}
TooManyTags                  {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}, 'resourceName': {'target': 'com.amazonaws.sfn#Arn'}}
ValidationException          {'message': {'target': 'com.amazonaws.sfn#ErrorMessage'}, 'reason': {'target': 'com.amazonaws.sfn#ValidationExceptionReason', 'traits': {}}}
```

These names are passed in a "Code" key of the JSON response, but are raised to errors as
`botocore.errorfactory` subclasses.

For example, running a request for an invalid ARN gives an error response with a `Code` value of "InvalidArn":

```py
import botodto

client = botodto.client("stepfunctions")
client.list_executions(stateMachineArn="abc")
```
⇣
```py
InvalidArn(__root__={'Message': "Invalid Arn: 'Invalid ARN prefix: abc'"})
```

The response we get is an object (rather than an error being raised), specifically a Pydantic model
of type `botodto.sdk.stepfunctions.InvalidArn`.

Note that this is still a work in progress: the model currently has an `Any`-typed root, which is
not much use at all! However the normal output responses **do** have proper data models,
and the error types will soon get them too by amending the OpenAPI schemas before running DTO model codegen.
