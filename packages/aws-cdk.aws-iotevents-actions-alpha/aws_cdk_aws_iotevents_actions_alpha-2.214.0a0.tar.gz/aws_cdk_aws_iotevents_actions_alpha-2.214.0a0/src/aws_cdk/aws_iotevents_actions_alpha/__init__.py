r'''
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_iotevents_alpha as _aws_cdk_aws_iotevents_alpha_39cbd76e
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d


@jsii.implements(_aws_cdk_aws_iotevents_alpha_39cbd76e.IAction)
class ClearTimerAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-actions-alpha.ClearTimerAction",
):
    '''(experimental) The action to delete an existing timer.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_iotevents_actions_alpha as iotevents_actions_alpha
        
        clear_timer_action = iotevents_actions_alpha.ClearTimerAction("timerName")
    '''

    def __init__(self, timer_name: builtins.str) -> None:
        '''
        :param timer_name: the name of the timer.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89c06b115e6024db71bf3032e1040021b7ff8939dcdb94d059056353538b623c)
            check_type(argname="argument timer_name", value=timer_name, expected_type=type_hints["timer_name"])
        jsii.create(self.__class__, self, [timer_name])


@jsii.implements(_aws_cdk_aws_iotevents_alpha_39cbd76e.IAction)
class LambdaInvokeAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-actions-alpha.LambdaInvokeAction",
):
    '''(experimental) The action to write the data to an AWS Lambda function.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_iotevents_alpha as iotevents
        import aws_cdk.aws_iotevents_actions_alpha as actions
        import aws_cdk.aws_lambda as lambda_
        
        # func: lambda.IFunction
        
        
        input = iotevents.Input(self, "MyInput",
            input_name="my_input",  # optional
            attribute_json_paths=["payload.deviceId", "payload.temperature"]
        )
        
        warm_state = iotevents.State(
            state_name="warm",
            on_enter=[iotevents.Event(
                event_name="test-enter-event",
                condition=iotevents.Expression.current_input(input),
                actions=[actions.LambdaInvokeAction(func)]
            )],
            on_input=[iotevents.Event( # optional
                event_name="test-input-event",
                actions=[actions.LambdaInvokeAction(func)])],
            on_exit=[iotevents.Event( # optional
                event_name="test-exit-event",
                actions=[actions.LambdaInvokeAction(func)])]
        )
        cold_state = iotevents.State(
            state_name="cold"
        )
        
        # transit to coldState when temperature is less than 15
        warm_state.transition_to(cold_state,
            event_name="to_coldState",  # optional property, default by combining the names of the States
            when=iotevents.Expression.lt(
                iotevents.Expression.input_attribute(input, "payload.temperature"),
                iotevents.Expression.from_string("15")),
            executing=[actions.LambdaInvokeAction(func)]
        )
        # transit to warmState when temperature is greater than or equal to 15
        cold_state.transition_to(warm_state,
            when=iotevents.Expression.gte(
                iotevents.Expression.input_attribute(input, "payload.temperature"),
                iotevents.Expression.from_string("15"))
        )
        
        iotevents.DetectorModel(self, "MyDetectorModel",
            detector_model_name="test-detector-model",  # optional
            description="test-detector-model-description",  # optional property, default is none
            evaluation_method=iotevents.EventEvaluation.SERIAL,  # optional property, default is iotevents.EventEvaluation.BATCH
            detector_key="payload.deviceId",  # optional property, default is none and single detector instance will be created and all inputs will be routed to it
            initial_state=warm_state
        )
    '''

    def __init__(self, func: _aws_cdk_aws_lambda_ceddda9d.IFunction) -> None:
        '''
        :param func: the AWS Lambda function to be invoked by this action.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__266a664aeb34853383a04b394f13739b7eaa06bd13dcc99d905efae7c35594e0)
            check_type(argname="argument func", value=func, expected_type=type_hints["func"])
        jsii.create(self.__class__, self, [func])


@jsii.implements(_aws_cdk_aws_iotevents_alpha_39cbd76e.IAction)
class ResetTimerAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-actions-alpha.ResetTimerAction",
):
    '''(experimental) The action to reset an existing timer.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_iotevents_actions_alpha as iotevents_actions_alpha
        
        reset_timer_action = iotevents_actions_alpha.ResetTimerAction("timerName")
    '''

    def __init__(self, timer_name: builtins.str) -> None:
        '''
        :param timer_name: the name of the timer.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f9e728c1fb0e584abe4917c0b1f390cbbb4883c01638883f185cf0592cc78a0)
            check_type(argname="argument timer_name", value=timer_name, expected_type=type_hints["timer_name"])
        jsii.create(self.__class__, self, [timer_name])


@jsii.implements(_aws_cdk_aws_iotevents_alpha_39cbd76e.IAction)
class SetTimerAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-actions-alpha.SetTimerAction",
):
    '''(experimental) The action to create a timer with duration in seconds.

    :stability: experimental
    :exampleMetadata: infused

    Example::

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
    '''

    def __init__(
        self,
        timer_name: builtins.str,
        timer_duration: "TimerDuration",
    ) -> None:
        '''
        :param timer_name: the name of the timer.
        :param timer_duration: the duration of the timer.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1f85532488b48d4d835ddca351c106b4f308293d005085e31a0fa471d25fdc4)
            check_type(argname="argument timer_name", value=timer_name, expected_type=type_hints["timer_name"])
            check_type(argname="argument timer_duration", value=timer_duration, expected_type=type_hints["timer_duration"])
        jsii.create(self.__class__, self, [timer_name, timer_duration])


@jsii.implements(_aws_cdk_aws_iotevents_alpha_39cbd76e.IAction)
class SetVariableAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-actions-alpha.SetVariableAction",
):
    '''(experimental) The action to create a variable with a specified value.

    :stability: experimental
    :exampleMetadata: infused

    Example::

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
    '''

    def __init__(
        self,
        variable_name: builtins.str,
        value: _aws_cdk_aws_iotevents_alpha_39cbd76e.Expression,
    ) -> None:
        '''
        :param variable_name: the name of the variable.
        :param value: the new value of the variable.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cbc7986a81719bd49426951c8f3a75c9df87d696a10b01da37381eb2b6488b1)
            check_type(argname="argument variable_name", value=variable_name, expected_type=type_hints["variable_name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.create(self.__class__, self, [variable_name, value])


class TimerDuration(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-iotevents-actions-alpha.TimerDuration",
):
    '''(experimental) The duration of the timer.

    :stability: experimental
    :exampleMetadata: infused

    Example::

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
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromDuration")
    @builtins.classmethod
    def from_duration(cls, duration: _aws_cdk_ceddda9d.Duration) -> "TimerDuration":
        '''(experimental) Create a timer-duration from Duration.

        The range of the duration is 60-31622400 seconds.
        The evaluated result of the duration expression is rounded down to the nearest whole number.
        For example, if you set the timer to 60.99 seconds, the evaluated result of the duration expression is 60 seconds.

        :param duration: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ff0ed7358aad4abd7cb83e471408e86c0f022cdfb81bb2f85ebf8624f4d9ca8)
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
        return typing.cast("TimerDuration", jsii.sinvoke(cls, "fromDuration", [duration]))

    @jsii.member(jsii_name="fromExpression")
    @builtins.classmethod
    def from_expression(
        cls,
        expression: _aws_cdk_aws_iotevents_alpha_39cbd76e.Expression,
    ) -> "TimerDuration":
        '''(experimental) Create a timer-duration from Expression.

        You can use a string expression that includes numbers, variables ($variable.),
        and input values ($input..) as the duration.

        The range of the duration is 60-31622400 seconds.
        The evaluated result of the duration expression is rounded down to the nearest whole number.
        For example, if you set the timer to 60.99 seconds, the evaluated result of the duration expression is 60 seconds.

        :param expression: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a24af86ee885e0669596143375363dff6b69740ca4322d2ba8b21438e94aa36)
            check_type(argname="argument expression", value=expression, expected_type=type_hints["expression"])
        return typing.cast("TimerDuration", jsii.sinvoke(cls, "fromExpression", [expression]))


class _TimerDurationProxy(TimerDuration):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, TimerDuration).__jsii_proxy_class__ = lambda : _TimerDurationProxy


__all__ = [
    "ClearTimerAction",
    "LambdaInvokeAction",
    "ResetTimerAction",
    "SetTimerAction",
    "SetVariableAction",
    "TimerDuration",
]

publication.publish()

def _typecheckingstub__89c06b115e6024db71bf3032e1040021b7ff8939dcdb94d059056353538b623c(
    timer_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__266a664aeb34853383a04b394f13739b7eaa06bd13dcc99d905efae7c35594e0(
    func: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f9e728c1fb0e584abe4917c0b1f390cbbb4883c01638883f185cf0592cc78a0(
    timer_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1f85532488b48d4d835ddca351c106b4f308293d005085e31a0fa471d25fdc4(
    timer_name: builtins.str,
    timer_duration: TimerDuration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cbc7986a81719bd49426951c8f3a75c9df87d696a10b01da37381eb2b6488b1(
    variable_name: builtins.str,
    value: _aws_cdk_aws_iotevents_alpha_39cbd76e.Expression,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ff0ed7358aad4abd7cb83e471408e86c0f022cdfb81bb2f85ebf8624f4d9ca8(
    duration: _aws_cdk_ceddda9d.Duration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a24af86ee885e0669596143375363dff6b69740ca4322d2ba8b21438e94aa36(
    expression: _aws_cdk_aws_iotevents_alpha_39cbd76e.Expression,
) -> None:
    """Type checking stubs"""
    pass
