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
