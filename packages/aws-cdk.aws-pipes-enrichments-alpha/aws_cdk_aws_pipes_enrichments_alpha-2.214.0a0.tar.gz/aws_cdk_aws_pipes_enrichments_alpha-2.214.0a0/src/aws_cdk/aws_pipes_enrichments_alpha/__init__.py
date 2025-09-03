r'''
# Amazon EventBridge Pipes Enrichments Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

EventBridge Pipes Enrichments let you create enrichments for an EventBridge Pipe.

For more details see the service documentation:

[Documentation](https://docs.aws.amazon.com/eventbridge/latest/userguide/pipes-enrichment.html)

## Pipe sources

Pipe enrichments are invoked prior to sending the events to a target of a EventBridge Pipe.

### Lambda function

A Lambda function can be used to enrich events of a pipe.

```python
# source_queue: sqs.Queue
# target_queue: sqs.Queue

# enrichment_function: lambda.Function


enrichment = enrichments.LambdaEnrichment(enrichment_function)

pipe = pipes.Pipe(self, "Pipe",
    source=SomeSource(source_queue),
    enrichment=enrichment,
    target=SomeTarget(target_queue)
)
```

### Step Functions state machine

Step Functions state machine can be used to enrich events of a pipe.

**Note:** EventBridge Pipes only supports Express workflows invoked synchronously.

> Visit [Amazon EventBridge Pipes event enrichment](https://docs.aws.amazon.com/eventbridge/latest/userguide/pipes-enrichment.html) for more details.

```python
# source_queue: sqs.Queue
# target_queue: sqs.Queue

# enrichment_state_machine: stepfunctions.StateMachine


enrichment = enrichments.StepFunctionsEnrichment(enrichment_state_machine)

pipe = pipes.Pipe(self, "Pipe",
    source=SomeSource(source_queue),
    enrichment=enrichment,
    target=SomeTarget(target_queue)
)
```

### API destination

API destination can be used to enrich events of a pipe.

```python
# source_queue: sqs.Queue
# target_queue: sqs.Queue

# api_destination: events.ApiDestination


enrichment = enrichments.ApiDestinationEnrichment(api_destination)

pipe = pipes.Pipe(self, "Pipe",
    source=SomeSource(source_queue),
    enrichment=enrichment,
    target=SomeTarget(target_queue)
)
```

### API Gateway (REST API)

API Gateway can be used to enrich events of a pipe.
Pipes only supports API Gateway REST APIs. HTTP APIs are not supported.

```python
# source_queue: sqs.Queue
# target_queue: sqs.Queue

# rest_api: apigateway.RestApi


enrichment = enrichments.ApiGatewayEnrichment(rest_api)

pipe = pipes.Pipe(self, "Pipe",
    source=SomeSource(source_queue),
    enrichment=enrichment,
    target=SomeTarget(target_queue)
)
```
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_pipes_alpha as _aws_cdk_aws_pipes_alpha_c8863edb
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d


@jsii.implements(_aws_cdk_aws_pipes_alpha_c8863edb.IEnrichment)
class ApiDestinationEnrichment(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.ApiDestinationEnrichment",
):
    '''(experimental) An API Destination enrichment for a pipe.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # source_queue: sqs.Queue
        # target_queue: sqs.Queue
        
        # api_destination: events.ApiDestination
        
        
        enrichment = enrichments.ApiDestinationEnrichment(api_destination)
        
        pipe = pipes.Pipe(self, "Pipe",
            source=SomeSource(source_queue),
            enrichment=enrichment,
            target=SomeTarget(target_queue)
        )
    '''

    def __init__(
        self,
        destination: _aws_cdk_aws_events_ceddda9d.IApiDestination,
        *,
        header_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
        path_parameter_values: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_string_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param destination: -
        :param header_parameters: (experimental) The headers that need to be sent as part of request invoking the EventBridge ApiDestination. Default: - none
        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None
        :param path_parameter_values: (experimental) The path parameter values used to populate the EventBridge API destination path wildcards ("*"). Default: - none
        :param query_string_parameters: (experimental) The query string keys/values that need to be sent as part of request invoking the EventBridge API destination. Default: - none

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dcd241391ce08f777848746423d8cdcf7c941d6ca0cd52d3f3fbf0bf5a6f736)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        props = ApiDestinationEnrichmentProps(
            header_parameters=header_parameters,
            input_transformation=input_transformation,
            path_parameter_values=path_parameter_values,
            query_string_parameters=query_string_parameters,
        )

        jsii.create(self.__class__, self, [destination, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
    ) -> _aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig:
        '''(experimental) Bind this enrichment to a pipe.

        :param pipe: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a92cd23cedbff27872021b088628eb149f1991ba3ce7d8de0dc3914e90122a9b)
            check_type(argname="argument pipe", value=pipe, expected_type=type_hints["pipe"])
        return typing.cast(_aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig, jsii.invoke(self, "bind", [pipe]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(self, pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''(experimental) Grant the pipes role to invoke the enrichment.

        :param pipe_role: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d4a693911460344af7a8b0f67e39e29494f2fb628677387435586f6dc7b36b9)
            check_type(argname="argument pipe_role", value=pipe_role, expected_type=type_hints["pipe_role"])
        return typing.cast(None, jsii.invoke(self, "grantInvoke", [pipe_role]))

    @builtins.property
    @jsii.member(jsii_name="enrichmentArn")
    def enrichment_arn(self) -> builtins.str:
        '''(experimental) The ARN of the enrichment resource.

        Length Constraints: Minimum length of 0. Maximum length of 1600.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "enrichmentArn"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.ApiDestinationEnrichmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "header_parameters": "headerParameters",
        "input_transformation": "inputTransformation",
        "path_parameter_values": "pathParameterValues",
        "query_string_parameters": "queryStringParameters",
    },
)
class ApiDestinationEnrichmentProps:
    def __init__(
        self,
        *,
        header_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
        path_parameter_values: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_string_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for a ApiDestinationEnrichment.

        :param header_parameters: (experimental) The headers that need to be sent as part of request invoking the EventBridge ApiDestination. Default: - none
        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None
        :param path_parameter_values: (experimental) The path parameter values used to populate the EventBridge API destination path wildcards ("*"). Default: - none
        :param query_string_parameters: (experimental) The query string keys/values that need to be sent as part of request invoking the EventBridge API destination. Default: - none

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_pipes_alpha as pipes_alpha
            import aws_cdk.aws_pipes_enrichments_alpha as pipes_enrichments_alpha
            
            # input_transformation: pipes_alpha.InputTransformation
            
            api_destination_enrichment_props = pipes_enrichments_alpha.ApiDestinationEnrichmentProps(
                header_parameters={
                    "header_parameters_key": "headerParameters"
                },
                input_transformation=input_transformation,
                path_parameter_values=["pathParameterValues"],
                query_string_parameters={
                    "query_string_parameters_key": "queryStringParameters"
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f20aff382efa59afd47408f68215831acfef53d180bb4d8903025f951834f04)
            check_type(argname="argument header_parameters", value=header_parameters, expected_type=type_hints["header_parameters"])
            check_type(argname="argument input_transformation", value=input_transformation, expected_type=type_hints["input_transformation"])
            check_type(argname="argument path_parameter_values", value=path_parameter_values, expected_type=type_hints["path_parameter_values"])
            check_type(argname="argument query_string_parameters", value=query_string_parameters, expected_type=type_hints["query_string_parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if header_parameters is not None:
            self._values["header_parameters"] = header_parameters
        if input_transformation is not None:
            self._values["input_transformation"] = input_transformation
        if path_parameter_values is not None:
            self._values["path_parameter_values"] = path_parameter_values
        if query_string_parameters is not None:
            self._values["query_string_parameters"] = query_string_parameters

    @builtins.property
    def header_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The headers that need to be sent as part of request invoking the EventBridge ApiDestination.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("header_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def input_transformation(
        self,
    ) -> typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation]:
        '''(experimental) The input transformation for the enrichment.

        :default: - None

        :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-input-transformation.html
        :stability: experimental
        '''
        result = self._values.get("input_transformation")
        return typing.cast(typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation], result)

    @builtins.property
    def path_parameter_values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The path parameter values used to populate the EventBridge API destination path wildcards ("*").

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("path_parameter_values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_string_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The query string keys/values that need to be sent as part of request invoking the EventBridge API destination.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("query_string_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiDestinationEnrichmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_pipes_alpha_c8863edb.IEnrichment)
class ApiGatewayEnrichment(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.ApiGatewayEnrichment",
):
    '''(experimental) An API Gateway enrichment for a pipe.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # source_queue: sqs.Queue
        # target_queue: sqs.Queue
        
        # rest_api: apigateway.RestApi
        
        
        enrichment = enrichments.ApiGatewayEnrichment(rest_api)
        
        pipe = pipes.Pipe(self, "Pipe",
            source=SomeSource(source_queue),
            enrichment=enrichment,
            target=SomeTarget(target_queue)
        )
    '''

    def __init__(
        self,
        rest_api: _aws_cdk_aws_apigateway_ceddda9d.IRestApi,
        *,
        header_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
        method: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        path_parameter_values: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_string_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param rest_api: -
        :param header_parameters: (experimental) The headers that need to be sent as part of request invoking the API Gateway REST API. Default: - none
        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None
        :param method: (experimental) The method for API Gateway resource. Default: '*' - ANY
        :param path: (experimental) The path for the API Gateway resource. Default: '/'
        :param path_parameter_values: (experimental) The path parameter values used to populate the API Gateway REST API path wildcards ("*"). Default: - none
        :param query_string_parameters: (experimental) The query string keys/values that need to be sent as part of request invoking the EventBridge API destination. Default: - none
        :param stage: (experimental) The deployment stage for the API Gateway resource. Default: - the value of ``deploymentStage.stageName`` of target API Gateway resource.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19b531905ef701cc1a27a876e0f761c3dc9cbc8410ff21c184c041704afb5902)
            check_type(argname="argument rest_api", value=rest_api, expected_type=type_hints["rest_api"])
        props = ApiGatewayEnrichmentProps(
            header_parameters=header_parameters,
            input_transformation=input_transformation,
            method=method,
            path=path,
            path_parameter_values=path_parameter_values,
            query_string_parameters=query_string_parameters,
            stage=stage,
        )

        jsii.create(self.__class__, self, [rest_api, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
    ) -> _aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig:
        '''(experimental) Bind this enrichment to a pipe.

        :param pipe: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__165d23ba761ec4d6f02a2a75c6175bf975dac80f38e447281144eb57bd2cad0e)
            check_type(argname="argument pipe", value=pipe, expected_type=type_hints["pipe"])
        return typing.cast(_aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig, jsii.invoke(self, "bind", [pipe]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(self, pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''(experimental) Grant the pipes role to invoke the enrichment.

        :param pipe_role: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__946a64e99b420009f877f6074c2c5d82c51f8c606324df88a07d32e276a8af77)
            check_type(argname="argument pipe_role", value=pipe_role, expected_type=type_hints["pipe_role"])
        return typing.cast(None, jsii.invoke(self, "grantInvoke", [pipe_role]))

    @builtins.property
    @jsii.member(jsii_name="enrichmentArn")
    def enrichment_arn(self) -> builtins.str:
        '''(experimental) The ARN of the enrichment resource.

        Length Constraints: Minimum length of 0. Maximum length of 1600.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "enrichmentArn"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.ApiGatewayEnrichmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "header_parameters": "headerParameters",
        "input_transformation": "inputTransformation",
        "method": "method",
        "path": "path",
        "path_parameter_values": "pathParameterValues",
        "query_string_parameters": "queryStringParameters",
        "stage": "stage",
    },
)
class ApiGatewayEnrichmentProps:
    def __init__(
        self,
        *,
        header_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
        method: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        path_parameter_values: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_string_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a ApiGatewayEnrichment.

        :param header_parameters: (experimental) The headers that need to be sent as part of request invoking the API Gateway REST API. Default: - none
        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None
        :param method: (experimental) The method for API Gateway resource. Default: '*' - ANY
        :param path: (experimental) The path for the API Gateway resource. Default: '/'
        :param path_parameter_values: (experimental) The path parameter values used to populate the API Gateway REST API path wildcards ("*"). Default: - none
        :param query_string_parameters: (experimental) The query string keys/values that need to be sent as part of request invoking the EventBridge API destination. Default: - none
        :param stage: (experimental) The deployment stage for the API Gateway resource. Default: - the value of ``deploymentStage.stageName`` of target API Gateway resource.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_pipes_alpha as pipes_alpha
            import aws_cdk.aws_pipes_enrichments_alpha as pipes_enrichments_alpha
            
            # input_transformation: pipes_alpha.InputTransformation
            
            api_gateway_enrichment_props = pipes_enrichments_alpha.ApiGatewayEnrichmentProps(
                header_parameters={
                    "header_parameters_key": "headerParameters"
                },
                input_transformation=input_transformation,
                method="method",
                path="path",
                path_parameter_values=["pathParameterValues"],
                query_string_parameters={
                    "query_string_parameters_key": "queryStringParameters"
                },
                stage="stage"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12e7f6bd129f0602c1137a98ced07eb91cb5c42ac6815fdeea3789ef3565e0cc)
            check_type(argname="argument header_parameters", value=header_parameters, expected_type=type_hints["header_parameters"])
            check_type(argname="argument input_transformation", value=input_transformation, expected_type=type_hints["input_transformation"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument path_parameter_values", value=path_parameter_values, expected_type=type_hints["path_parameter_values"])
            check_type(argname="argument query_string_parameters", value=query_string_parameters, expected_type=type_hints["query_string_parameters"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if header_parameters is not None:
            self._values["header_parameters"] = header_parameters
        if input_transformation is not None:
            self._values["input_transformation"] = input_transformation
        if method is not None:
            self._values["method"] = method
        if path is not None:
            self._values["path"] = path
        if path_parameter_values is not None:
            self._values["path_parameter_values"] = path_parameter_values
        if query_string_parameters is not None:
            self._values["query_string_parameters"] = query_string_parameters
        if stage is not None:
            self._values["stage"] = stage

    @builtins.property
    def header_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The headers that need to be sent as part of request invoking the API Gateway REST API.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("header_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def input_transformation(
        self,
    ) -> typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation]:
        '''(experimental) The input transformation for the enrichment.

        :default: - None

        :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-input-transformation.html
        :stability: experimental
        '''
        result = self._values.get("input_transformation")
        return typing.cast(typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation], result)

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''(experimental) The method for API Gateway resource.

        :default: '*' - ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''(experimental) The path for the API Gateway resource.

        :default: '/'

        :stability: experimental
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_parameter_values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The path parameter values used to populate the API Gateway REST API path wildcards ("*").

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("path_parameter_values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_string_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The query string keys/values that need to be sent as part of request invoking the EventBridge API destination.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("query_string_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''(experimental) The deployment stage for the API Gateway resource.

        :default: - the value of ``deploymentStage.stageName`` of target API Gateway resource.

        :stability: experimental
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayEnrichmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_pipes_alpha_c8863edb.IEnrichment)
class LambdaEnrichment(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.LambdaEnrichment",
):
    '''(experimental) A Lambda enrichment for a pipe.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # source_queue: sqs.Queue
        # target_queue: sqs.Queue
        
        # enrichment_function: lambda.Function
        
        
        enrichment = enrichments.LambdaEnrichment(enrichment_function)
        
        pipe = pipes.Pipe(self, "Pipe",
            source=SomeSource(source_queue),
            enrichment=enrichment,
            target=SomeTarget(target_queue)
        )
    '''

    def __init__(
        self,
        lambda_: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        *,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    ) -> None:
        '''
        :param lambda_: -
        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c2328454e32118c406277a3396e86d7e20c1075eafcd353a83b1b8a42f43a27)
            check_type(argname="argument lambda_", value=lambda_, expected_type=type_hints["lambda_"])
        props = LambdaEnrichmentProps(input_transformation=input_transformation)

        jsii.create(self.__class__, self, [lambda_, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
    ) -> _aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig:
        '''(experimental) Bind this enrichment to a pipe.

        :param pipe: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59a728fcc4d8aca29008023d9b63f1c246d2a8e4ef68377f172c94a926580caf)
            check_type(argname="argument pipe", value=pipe, expected_type=type_hints["pipe"])
        return typing.cast(_aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig, jsii.invoke(self, "bind", [pipe]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(self, pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''(experimental) Grant the pipes role to invoke the enrichment.

        :param pipe_role: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d57f0a30006838ea06d202d63caf797ab47ca4c8aea6da9133fcb5c7e7ce1d72)
            check_type(argname="argument pipe_role", value=pipe_role, expected_type=type_hints["pipe_role"])
        return typing.cast(None, jsii.invoke(self, "grantInvoke", [pipe_role]))

    @builtins.property
    @jsii.member(jsii_name="enrichmentArn")
    def enrichment_arn(self) -> builtins.str:
        '''(experimental) The ARN of the enrichment resource.

        Length Constraints: Minimum length of 0. Maximum length of 1600.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "enrichmentArn"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.LambdaEnrichmentProps",
    jsii_struct_bases=[],
    name_mapping={"input_transformation": "inputTransformation"},
)
class LambdaEnrichmentProps:
    def __init__(
        self,
        *,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    ) -> None:
        '''(experimental) Properties for a LambdaEnrichment.

        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_pipes_alpha as pipes_alpha
            import aws_cdk.aws_pipes_enrichments_alpha as pipes_enrichments_alpha
            
            # input_transformation: pipes_alpha.InputTransformation
            
            lambda_enrichment_props = pipes_enrichments_alpha.LambdaEnrichmentProps(
                input_transformation=input_transformation
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45d24844f53d2bf42f2facaf64d0c1ac127817605aaf6017892ba404b8d6d437)
            check_type(argname="argument input_transformation", value=input_transformation, expected_type=type_hints["input_transformation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if input_transformation is not None:
            self._values["input_transformation"] = input_transformation

    @builtins.property
    def input_transformation(
        self,
    ) -> typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation]:
        '''(experimental) The input transformation for the enrichment.

        :default: - None

        :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-input-transformation.html
        :stability: experimental
        '''
        result = self._values.get("input_transformation")
        return typing.cast(typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaEnrichmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_pipes_alpha_c8863edb.IEnrichment)
class StepFunctionsEnrichment(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.StepFunctionsEnrichment",
):
    '''(experimental) A StepFunctions enrichment for a pipe.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # source_queue: sqs.Queue
        # target_queue: sqs.Queue
        
        # enrichment_state_machine: stepfunctions.StateMachine
        
        
        enrichment = enrichments.StepFunctionsEnrichment(enrichment_state_machine)
        
        pipe = pipes.Pipe(self, "Pipe",
            source=SomeSource(source_queue),
            enrichment=enrichment,
            target=SomeTarget(target_queue)
        )
    '''

    def __init__(
        self,
        state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
        *,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    ) -> None:
        '''
        :param state_machine: -
        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b78ec22b769ae4ea4b8a9b6b5356bb8ea06b44dd261eb6527de12cd3c4e2d9e2)
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
        props = StepFunctionsEnrichmentProps(input_transformation=input_transformation)

        jsii.create(self.__class__, self, [state_machine, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
    ) -> _aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig:
        '''(experimental) Bind this enrichment to a pipe.

        :param pipe: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34003f48d16d57c4bbcf1ff2b5fd9331e4d90951cced65c28bf38ae7808d5b61)
            check_type(argname="argument pipe", value=pipe, expected_type=type_hints["pipe"])
        return typing.cast(_aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig, jsii.invoke(self, "bind", [pipe]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(self, pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''(experimental) Grant the pipes role to invoke the enrichment.

        :param pipe_role: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ceff6af4637270f94096032d84462d56b144467150440a06dad4e6f9acfb84f)
            check_type(argname="argument pipe_role", value=pipe_role, expected_type=type_hints["pipe_role"])
        return typing.cast(None, jsii.invoke(self, "grantInvoke", [pipe_role]))

    @builtins.property
    @jsii.member(jsii_name="enrichmentArn")
    def enrichment_arn(self) -> builtins.str:
        '''(experimental) The ARN of the enrichment resource.

        Length Constraints: Minimum length of 0. Maximum length of 1600.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "enrichmentArn"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.StepFunctionsEnrichmentProps",
    jsii_struct_bases=[],
    name_mapping={"input_transformation": "inputTransformation"},
)
class StepFunctionsEnrichmentProps:
    def __init__(
        self,
        *,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    ) -> None:
        '''(experimental) Properties for a StepFunctionsEnrichment.

        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_pipes_alpha as pipes_alpha
            import aws_cdk.aws_pipes_enrichments_alpha as pipes_enrichments_alpha
            
            # input_transformation: pipes_alpha.InputTransformation
            
            step_functions_enrichment_props = pipes_enrichments_alpha.StepFunctionsEnrichmentProps(
                input_transformation=input_transformation
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78adaa41426268b0a38dac23376b95fa24c159b27536bb33baf7630b0d7be448)
            check_type(argname="argument input_transformation", value=input_transformation, expected_type=type_hints["input_transformation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if input_transformation is not None:
            self._values["input_transformation"] = input_transformation

    @builtins.property
    def input_transformation(
        self,
    ) -> typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation]:
        '''(experimental) The input transformation for the enrichment.

        :default: - None

        :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-input-transformation.html
        :stability: experimental
        '''
        result = self._values.get("input_transformation")
        return typing.cast(typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StepFunctionsEnrichmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiDestinationEnrichment",
    "ApiDestinationEnrichmentProps",
    "ApiGatewayEnrichment",
    "ApiGatewayEnrichmentProps",
    "LambdaEnrichment",
    "LambdaEnrichmentProps",
    "StepFunctionsEnrichment",
    "StepFunctionsEnrichmentProps",
]

publication.publish()

def _typecheckingstub__2dcd241391ce08f777848746423d8cdcf7c941d6ca0cd52d3f3fbf0bf5a6f736(
    destination: _aws_cdk_aws_events_ceddda9d.IApiDestination,
    *,
    header_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    path_parameter_values: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_string_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a92cd23cedbff27872021b088628eb149f1991ba3ce7d8de0dc3914e90122a9b(
    pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d4a693911460344af7a8b0f67e39e29494f2fb628677387435586f6dc7b36b9(
    pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f20aff382efa59afd47408f68215831acfef53d180bb4d8903025f951834f04(
    *,
    header_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    path_parameter_values: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_string_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19b531905ef701cc1a27a876e0f761c3dc9cbc8410ff21c184c041704afb5902(
    rest_api: _aws_cdk_aws_apigateway_ceddda9d.IRestApi,
    *,
    header_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    method: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    path_parameter_values: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_string_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    stage: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__165d23ba761ec4d6f02a2a75c6175bf975dac80f38e447281144eb57bd2cad0e(
    pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__946a64e99b420009f877f6074c2c5d82c51f8c606324df88a07d32e276a8af77(
    pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12e7f6bd129f0602c1137a98ced07eb91cb5c42ac6815fdeea3789ef3565e0cc(
    *,
    header_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    method: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    path_parameter_values: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_string_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    stage: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c2328454e32118c406277a3396e86d7e20c1075eafcd353a83b1b8a42f43a27(
    lambda_: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    *,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59a728fcc4d8aca29008023d9b63f1c246d2a8e4ef68377f172c94a926580caf(
    pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d57f0a30006838ea06d202d63caf797ab47ca4c8aea6da9133fcb5c7e7ce1d72(
    pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45d24844f53d2bf42f2facaf64d0c1ac127817605aaf6017892ba404b8d6d437(
    *,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b78ec22b769ae4ea4b8a9b6b5356bb8ea06b44dd261eb6527de12cd3c4e2d9e2(
    state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
    *,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34003f48d16d57c4bbcf1ff2b5fd9331e4d90951cced65c28bf38ae7808d5b61(
    pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ceff6af4637270f94096032d84462d56b144467150440a06dad4e6f9acfb84f(
    pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78adaa41426268b0a38dac23376b95fa24c159b27536bb33baf7630b0d7be448(
    *,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
) -> None:
    """Type checking stubs"""
    pass
