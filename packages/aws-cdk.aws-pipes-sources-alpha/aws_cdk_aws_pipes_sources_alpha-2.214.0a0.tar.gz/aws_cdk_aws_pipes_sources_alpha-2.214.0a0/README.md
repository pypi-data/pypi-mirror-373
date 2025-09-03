# Amazon EventBridge Pipes Sources Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

EventBridge Pipes Sources let you create a source for a EventBridge Pipe.

For more details see the service documentation:

[Documentation](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-event-source.html)

## Pipe sources

Pipe sources are the starting point of a EventBridge Pipe. They are the source of the events that are sent to the pipe.

### Amazon SQS

A SQS message queue can be used as a source for a pipe. The queue will be polled for new messages and the messages will be sent to the pipe.

```python
# source_queue: sqs.Queue
# target_queue: sqs.Queue


pipe_source = sources.SqsSource(source_queue)

pipe = pipes.Pipe(self, "Pipe",
    source=pipe_source,
    target=SqsTarget(target_queue)
)
```

The polling configuration can be customized:

```python
# source_queue: sqs.Queue
# target_queue: sqs.Queue


pipe_source = sources.SqsSource(source_queue,
    batch_size=10,
    maximum_batching_window=cdk.Duration.seconds(10)
)

pipe = pipes.Pipe(self, "Pipe",
    source=pipe_source,
    target=SqsTarget(target_queue)
)
```

### Amazon Kinesis

A Kinesis stream can be used as a source for a pipe. The stream will be polled for new messages and the messages will be sent to the pipe.

```python
# source_stream: kinesis.Stream
# target_queue: sqs.Queue


pipe_source = sources.KinesisSource(source_stream,
    starting_position=sources.KinesisStartingPosition.LATEST
)

pipe = pipes.Pipe(self, "Pipe",
    source=pipe_source,
    target=SqsTarget(target_queue)
)
```

### Amazon DynamoDB

A DynamoDB stream can be used as a source for a pipe. The stream will be polled for new messages and the messages will be sent to the pipe.

```python
# target_queue: sqs.Queue
table = ddb.TableV2(self, "MyTable",
    partition_key=ddb.Attribute(
        name="id",
        type=ddb.AttributeType.STRING
    ),
    dynamo_stream=ddb.StreamViewType.NEW_IMAGE
)

pipe_source = sources.DynamoDBSource(table,
    starting_position=sources.DynamoDBStartingPosition.LATEST
)

pipe = pipes.Pipe(self, "Pipe",
    source=pipe_source,
    target=SqsTarget(target_queue)
)
```
