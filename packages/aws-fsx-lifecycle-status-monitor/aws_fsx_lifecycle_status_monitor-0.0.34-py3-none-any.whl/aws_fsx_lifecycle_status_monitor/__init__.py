r'''
# AWS FSx Life Cycle Status Monitor

The documentation is available [here](https://stefanfreitag.github.io/AWS-FSx-Lifecycle-Status-Monitor/).

## How to run

### Tests

* Execute the unit tests under `./test`

  ```shell
  yarn test
  ```
* Execute integration tests under `.integ-tests`

  ```shell
  yarn integ-runner --directory ./integ-tests  --update-on-failed --parallel-regions eu-central-1
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

import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


class FsxLifecycleStatusMonitor(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-fsx-lifecycle-status-monitor.FsxLifecycleStatusMonitor",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        log_retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''(experimental) Creates an instance of FsxLifecycleStatusMonitor.

        :param scope: - parent construct.
        :param id: - unique id.
        :param log_retention_days: (experimental) The log retention days for the FSx Lifecycle Status Monitor. Default: logs.RetentionDays.ONE_YEAR
        :param schedule: (experimental) The schedule for the FSx Lifecycle Status Monitor. Default: "events.Schedule.cron({ minute: '0/10', hour: '*', day: '*', month: '*', year: '*' })"

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor - class instance
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b81cd38fb38b316d1be164277c3405c07340ac222fdb134c62c28d69a33d4354)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FsxLifecycleStatusMonitorProps(
            log_retention_days=log_retention_days, schedule=schedule
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createIamPolicy")
    def create_iam_policy(self) -> _aws_cdk_aws_iam_ceddda9d.Policy:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Policy, jsii.invoke(self, "createIamPolicy", []))

    @jsii.member(jsii_name="createLambdaFunction")
    def create_lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        '''
        :return: {lambda.Function}

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.invoke(self, "createLambdaFunction", []))

    @jsii.member(jsii_name="createSNSTopic")
    def create_sns_topic(self) -> _aws_cdk_aws_sns_ceddda9d.Topic:
        '''(experimental) Topic linked to the Lambda function.

        :return: {sns.Topic} - sns topic

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor - class instance
        '''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.Topic, jsii.invoke(self, "createSNSTopic", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_LOG_RETENTION_PERIOD")
    def DEFAULT_LOG_RETENTION_PERIOD(cls) -> _aws_cdk_aws_logs_ceddda9d.RetentionDays:
        '''(experimental) Default log retention for the FSx Lifecycle Status Monitor.

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor
        :static: true
        '''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.RetentionDays, jsii.sget(cls, "DEFAULT_LOG_RETENTION_PERIOD"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_SCHEDULE")
    def DEFAULT_SCHEDULE(cls) -> _aws_cdk_aws_events_ceddda9d.Schedule:
        '''(experimental) Default schedule for the FSx Lifecycle Status Monitor.

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor
        :static: true
        '''
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Schedule, jsii.sget(cls, "DEFAULT_SCHEDULE"))

    @builtins.property
    @jsii.member(jsii_name="fn")
    def fn(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        '''(experimental) The Lambda function that will be triggered by the CloudWatch event.

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor
        :type: {lambda.Function}
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "fn"))

    @fn.setter
    def fn(self, value: _aws_cdk_aws_lambda_ceddda9d.Function) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8b4032180c59ac1c1c0df56b2db93e26a474dc0966a18b6fe0df00ea86e84e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        '''(experimental) Log group for the Lambda function.

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor
        :type: {logs.LogGroup}
        '''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "logGroup"))

    @log_group.setter
    def log_group(self, value: _aws_cdk_aws_logs_ceddda9d.LogGroup) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__024af8e4ffc64c7d71a3f94ccc80cee7d7dfb3945d61d0999266633b62ed2439)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> _aws_cdk_aws_iam_ceddda9d.Policy:
        '''(experimental) The IAM policy that will be attached to the Lambda function.

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor
        :type: {iam.Policy}
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Policy, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: _aws_cdk_aws_iam_ceddda9d.Policy) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02a1148af1bfc2f0583587e22e7db7e7e8748ffaba4d54835e19a8bf66b5b136)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rule")
    def rule(self) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''(experimental) The CloudWatch event rule that will trigger the Lambda function.

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor
        :type: {events.Rule}
        '''
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.get(self, "rule"))

    @rule.setter
    def rule(self, value: _aws_cdk_aws_events_ceddda9d.Rule) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23c10cd73da7a12439f1a5d36cb378b2bb0455726c883157646552ce5281d1cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topic")
    def topic(self) -> _aws_cdk_aws_sns_ceddda9d.Topic:
        '''(experimental) Topic linked to the Lambda function.

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitor
        :type: {sns.Topic}
        '''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.Topic, jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: _aws_cdk_aws_sns_ceddda9d.Topic) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c8971392deb4f782b22feab8db090bb4d67e2fb89e84bbd0ac0da200604a66c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topic", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="aws-fsx-lifecycle-status-monitor.FsxLifecycleStatusMonitorProps",
    jsii_struct_bases=[],
    name_mapping={"log_retention_days": "logRetentionDays", "schedule": "schedule"},
)
class FsxLifecycleStatusMonitorProps:
    def __init__(
        self,
        *,
        log_retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''(experimental) Configuration properties for the FSx Lifecycle Status Monitor.

        :param log_retention_days: (experimental) The log retention days for the FSx Lifecycle Status Monitor. Default: logs.RetentionDays.ONE_YEAR
        :param schedule: (experimental) The schedule for the FSx Lifecycle Status Monitor. Default: "events.Schedule.cron({ minute: '0/10', hour: '*', day: '*', month: '*', year: '*' })"

        :stability: experimental
        :export: true
        :interface: FsxLifecycleStatusMonitorProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed85d95b85def793f715df77d38ad651d2df87abc06c2ddb33b2e3ec9da39b8b)
            check_type(argname="argument log_retention_days", value=log_retention_days, expected_type=type_hints["log_retention_days"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_retention_days is not None:
            self._values["log_retention_days"] = log_retention_days
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def log_retention_days(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''(experimental) The log retention days for the FSx Lifecycle Status Monitor.

        :default: logs.RetentionDays.ONE_YEAR

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitorProps
        :type: {logs.RetentionDays}

        Example::

            this.monitor = new FsxLifecycleStatusMonitor(this, "monitor",{
              logRetentionDays: logs.RetentionDays.ONE_MONTH
            });
        '''
        result = self._values.get("log_retention_days")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''(experimental) The schedule for the FSx Lifecycle Status Monitor.

        :default: "events.Schedule.cron({ minute: '0/10', hour: '*', day: '*', month: '*', year: '*' })"

        :stability: experimental
        :memberof: FsxLifecycleStatusMonitorProps
        :type: {events.Schedule}

        Example::

            this.monitor = new FsxLifecycleStatusMonitor(this, "monitor",{
              logRetentionDays: logs.RetentionDays.ONE_MONTH,
              schedule: events.Schedule.rate(cdk.Duration.hours(1)),
            });
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxLifecycleStatusMonitorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "FsxLifecycleStatusMonitor",
    "FsxLifecycleStatusMonitorProps",
]

publication.publish()

def _typecheckingstub__b81cd38fb38b316d1be164277c3405c07340ac222fdb134c62c28d69a33d4354(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    log_retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8b4032180c59ac1c1c0df56b2db93e26a474dc0966a18b6fe0df00ea86e84e8(
    value: _aws_cdk_aws_lambda_ceddda9d.Function,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__024af8e4ffc64c7d71a3f94ccc80cee7d7dfb3945d61d0999266633b62ed2439(
    value: _aws_cdk_aws_logs_ceddda9d.LogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02a1148af1bfc2f0583587e22e7db7e7e8748ffaba4d54835e19a8bf66b5b136(
    value: _aws_cdk_aws_iam_ceddda9d.Policy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23c10cd73da7a12439f1a5d36cb378b2bb0455726c883157646552ce5281d1cf(
    value: _aws_cdk_aws_events_ceddda9d.Rule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c8971392deb4f782b22feab8db090bb4d67e2fb89e84bbd0ac0da200604a66c(
    value: _aws_cdk_aws_sns_ceddda9d.Topic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed85d95b85def793f715df77d38ad651d2df87abc06c2ddb33b2e3ec9da39b8b(
    *,
    log_retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass
