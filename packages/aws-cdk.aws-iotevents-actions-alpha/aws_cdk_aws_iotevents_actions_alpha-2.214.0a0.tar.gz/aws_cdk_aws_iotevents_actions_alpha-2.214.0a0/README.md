# Actions for AWS::IoTEvents Detector Model

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This library contains integration classes to specify actions of state events of Detector Model in `@aws-cdk/aws-iotevents-alpha`.
Instances of these classes should be passed to `State` defined in `@aws-cdk/aws-iotevents-alpha`
You can define built-in actions to use a timer or set a variable, or send data to other AWS resources.

This library contains integration classes to use a timer or set a variable, or send data to other AWS resources.
AWS IoT Events can trigger actions when it detects a specified event or transition event.

Currently supported are:

* Use timer
* Set variable to detector instance
* Invoke a Lambda function

## Use timer

The code snippet below creates an Action that creates the timer with duration in seconds.

```python
# Example automatically generated from non-compiling source. May contain errors.
import aws_cdk.aws_iotevents_alpha as iotevents
import aws_cdk.aws_iotevents_actions_alpha as actions

# input: iotevents.IInput

state = iotevents.State(
    state_name="MyState",
    on_enter=[iotevents.Event(
        event_name="test-event",
        condition=iotevents.Expression.current_input(input),
        actions=[
            actions.SetTimerAction("MyTimer", {
                "duration": cdk.Duration.seconds(60)
            })
        ]
    )]
)
```

Setting duration by [IoT Events Expression](https://docs.aws.amazon.com/iotevents/latest/developerguide/iotevents-expressions.html):

```python
# Example automatically generated from non-compiling source. May contain errors.
actions.SetTimerAction("MyTimer",
    duration_expression=iotevents.Expression.input_attribute(input, "payload.durationSeconds")
)
```

And the timer can be reset and cleared. Below is an example of general
[Device HeartBeat](https://docs.aws.amazon.com/iotevents/latest/developerguide/iotevents-examples-dhb.html)
Detector Model:

```python
# Example automatically generated from non-compiling source. May contain errors.
online = iotevents.State(
    state_name="Online",
    on_enter=[{
        "event_name": "enter-event",
        "condition": iotevents.Expression.current_input(input),
        "actions": [
            actions.SetTimerAction("MyTimer",
                duration=cdk.Duration.seconds(60)
            )
        ]
    }],
    on_input=[{
        "event_name": "input-event",
        "condition": iotevents.Expression.current_input(input),
        "actions": [
            actions.ResetTimerAction("MyTimer")
        ]
    }],
    on_exit=[{
        "event_name": "exit-event",
        "actions": [
            actions.ClearTimerAction("MyTimer")
        ]
    }]
)
offline = iotevents.State(state_name="Offline")

online.transition_to(offline, when=iotevents.Expression.timeout("MyTimer"))
offline.transition_to(online, when=iotevents.Expression.current_input(input))
```

## Set variable to detector instance

The code snippet below creates an Action that set variable to detector instance
when it is triggered.

```python
import aws_cdk.aws_iotevents_alpha as iotevents
import aws_cdk.aws_iotevents_actions_alpha as actions

# input: iotevents.IInput

state = iotevents.State(
    state_name="MyState",
    on_enter=[iotevents.Event(
        event_name="test-event",
        condition=iotevents.Expression.current_input(input),
        actions=[
            actions.SetVariableAction("MyVariable",
                iotevents.Expression.input_attribute(input, "payload.temperature"))
        ]
    )]
)
```

## Invoke a Lambda function

The code snippet below creates an Action that invoke a Lambda function
when it is triggered.

```python
import aws_cdk.aws_iotevents_alpha as iotevents
import aws_cdk.aws_iotevents_actions_alpha as actions
import aws_cdk.aws_lambda as lambda_

# input: iotevents.IInput
# func: lambda.IFunction

state = iotevents.State(
    state_name="MyState",
    on_enter=[iotevents.Event(
        event_name="test-event",
        condition=iotevents.Expression.current_input(input),
        actions=[actions.LambdaInvokeAction(func)]
    )]
)
```
