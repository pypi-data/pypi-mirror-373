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

from .._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import constructs as _constructs_77d1e7e8
from ..types import LambdaConfiguration as _LambdaConfiguration_9f8afc24


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.AlarmConfig",
    jsii_struct_bases=[],
    name_mapping={
        "comparison_operator": "comparisonOperator",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "metric_name": "metricName",
        "period": "period",
        "statistic": "statistic",
        "threshold": "threshold",
    },
)
class AlarmConfig:
    def __init__(
        self,
        *,
        comparison_operator: _aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator,
        datapoints_to_alarm: jsii.Number,
        evaluation_periods: jsii.Number,
        metric_name: "Ec2AutomatedShutdown.Ec2MetricName",
        period: _aws_cdk_ceddda9d.Duration,
        statistic: builtins.str,
        threshold: jsii.Number,
    ) -> None:
        '''(experimental) Optional custom metric configuration for CloudWatch Alarms.

        If not provided, defaults to CPU utilization with a 5% threshold.

        :param comparison_operator: (experimental) The comparison operator to use for the alarm. Default: = ComparisonOperator.LESS_THAN_THRESHOLD
        :param datapoints_to_alarm: (experimental) The number of datapoints that must go past/below the threshold to trigger the alarm. Default: = 2
        :param evaluation_periods: (experimental) The number of periods over which data is compared to the specified threshold. Default: = 3
        :param metric_name: (experimental) The name of the CloudWatch metric to monitor. Default: = CPUUtilization
        :param period: (experimental) The period over which the metric is measured. Default: = 1 minute
        :param statistic: (experimental) The CloudWatch metric statistic to use. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Default: = 'Average'
        :param threshold: (experimental) The threshold value for the alarm. Default: = 5%

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39e80c1625a9aebade1607b9063a75a5e101289462594aab3e82799e39c067ab)
            check_type(argname="argument comparison_operator", value=comparison_operator, expected_type=type_hints["comparison_operator"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "comparison_operator": comparison_operator,
            "datapoints_to_alarm": datapoints_to_alarm,
            "evaluation_periods": evaluation_periods,
            "metric_name": metric_name,
            "period": period,
            "statistic": statistic,
            "threshold": threshold,
        }

    @builtins.property
    def comparison_operator(
        self,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator:
        '''(experimental) The comparison operator to use for the alarm.

        :default: = ComparisonOperator.LESS_THAN_THRESHOLD

        :stability: experimental
        '''
        result = self._values.get("comparison_operator")
        assert result is not None, "Required property 'comparison_operator' is missing"
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator, result)

    @builtins.property
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints that must go past/below the threshold to trigger the alarm.

        :default: = 2

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        assert result is not None, "Required property 'datapoints_to_alarm' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of periods over which data is compared to the specified threshold.

        :default: = 3

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        assert result is not None, "Required property 'evaluation_periods' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def metric_name(self) -> "Ec2AutomatedShutdown.Ec2MetricName":
        '''(experimental) The name of the CloudWatch metric to monitor.

        :default: = CPUUtilization

        :stability: experimental
        '''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast("Ec2AutomatedShutdown.Ec2MetricName", result)

    @builtins.property
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period over which the metric is measured.

        :default: = 1 minute

        :stability: experimental
        '''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Duration, result)

    @builtins.property
    def statistic(self) -> builtins.str:
        '''(experimental) The CloudWatch metric statistic to use.

        Use the ``aws_cloudwatch.Stats`` helper class to construct valid input
        strings.

        :default: = 'Average'

        :stability: experimental
        '''
        result = self._values.get("statistic")
        assert result is not None, "Required property 'statistic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''(experimental) The threshold value for the alarm.

        :default: = 5%

        :stability: experimental
        '''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlarmConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class ApplyRemovalPolicy(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.ApplyRemovalPolicy",
):
    '''(experimental) Sets a user specified Removal Policy to all resources that the aspect applies to.

    This Aspect is useful if you want to enforce a specified removal policy on
    resources. For example, you could ensure that your removal policy is always
    set to RETAIN or DESTROY.

    :stability: experimental

    Example::

        import { App, Aspects, RemovalPolicy } from 'aws-cdk-lib';
        import { ApplyRemovalPolicy } from '@cdklabs/cdk-proserve-lib/aspects';
        
        const app = new App();
        
        Aspects.of(app).add(
          new ApplyRemovalPolicy({ removalPolicy: RemovalPolicy.DESTROY })
        );
    '''

    def __init__(self, *, removal_policy: _aws_cdk_ceddda9d.RemovalPolicy) -> None:
        '''(experimental) Creates a new instance of SetRemovalPolicy.

        :param removal_policy: (experimental) The removal policy to apply to the resource.

        :stability: experimental
        '''
        props = ApplyRemovalPolicyProps(removal_policy=removal_policy)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) Visits a construct and applies the removal policy.

        :param node: The construct being visited.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8ce1ca35633c77f43304cf7f1782f1ebf1496f151645dca582fc865fe0fe866)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.ApplyRemovalPolicyProps",
    jsii_struct_bases=[],
    name_mapping={"removal_policy": "removalPolicy"},
)
class ApplyRemovalPolicyProps:
    def __init__(self, *, removal_policy: _aws_cdk_ceddda9d.RemovalPolicy) -> None:
        '''(experimental) Properties for configuring the removal policy settings.

        :param removal_policy: (experimental) The removal policy to apply to the resource.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__858f2996365d3ec27b04534ec073a42ea6b65c3aa7cc1fa650e2765c14c83528)
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "removal_policy": removal_policy,
        }

    @builtins.property
    def removal_policy(self) -> _aws_cdk_ceddda9d.RemovalPolicy:
        '''(experimental) The removal policy to apply to the resource.

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        assert result is not None, "Required property 'removal_policy' is missing"
        return typing.cast(_aws_cdk_ceddda9d.RemovalPolicy, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplyRemovalPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class CreateLambdaLogGroup(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.CreateLambdaLogGroup",
):
    '''(experimental) Ensures that Lambda log groups are created for all Lambda functions that the aspect applies to.

    :stability: experimental

    Example::

        import { App, Aspects } from 'aws-cdk-lib';
        import { CreateLambdaLogGroup } from '@cdklabs/cdk-proserve-lib/aspects';
        
        const app = new App();
        
        Aspects.of(app).add(new CreateLambdaLogGroup());
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) Visits a construct and creates a log group if the construct is a Lambda function.

        :param node: The construct being visited.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa6b301934b30a296211f1f67b29307771270f03bbb136c1415e30d55396295a)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class Ec2AutomatedShutdown(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.Ec2AutomatedShutdown",
):
    '''(experimental) Automatically shut down EC2 instances when an alarm is triggered based off of a provided metric.

    🚩 If you are applying this Aspect to multiple EC2 instances, you
    will need to configure the CDK context variable flag
    ``@aws-cdk/aws-cloudwatch-actions:changeLambdaPermissionLogicalIdForLambdaAction``
    set to ``true``. If this is not configured, applying this Aspect to multiple
    EC2 instances will result in a CDK synth error.

    Allows for cost optimization and the reduction of resources not being
    actively used. When the EC2 alarm is triggered for a given EC2 instance, it
    will automatically trigger a Lambda function to shutdown the instance.

    :stability: experimental

    Example::

        import { App, Aspects, Duration, Stack } from 'aws-cdk-lib';
        import { ComparisonOperator, Stats } from 'aws-cdk-lib/aws-cloudwatch';
        import { Instance } from 'aws-cdk-lib/aws-ec2';
        import { Ec2AutomatedShutdown } from './src/aspects/ec2-automated-shutdown';
        
        const app = new App({
            context: {
                '@aws-cdk/aws-cloudwatch-actions:changeLambdaPermissionLogicalIdForLambdaAction':
                    true
            }
        });
        const stack = new Stack(app, 'MyStack');
        
        // Create your EC2 instance(s)
        const instance = new Instance(stack, 'MyInstance', {
            // instance properties
        });
        
        // Apply the aspect to automatically shut down the EC2 instance when underutilized
        Aspects.of(stack).add(new Ec2AutomatedShutdown());
        
        // Or with custom configuration
        Aspects.of(stack).add(
            new Ec2AutomatedShutdown({
                alarmConfig: {
                    metricName: Ec2AutomatedShutdown.Ec2MetricName.NETWORK_IN,
                    period: Duration.minutes(5),
                    statistic: Stats.AVERAGE,
                    threshold: 100, // 100 bytes
                    evaluationPeriods: 6,
                    datapointsToAlarm: 5,
                    comparisonOperator: ComparisonOperator.LESS_THAN_THRESHOLD
                }
            })
        );
    '''

    def __init__(
        self,
        *,
        alarm_config: typing.Optional[typing.Union[AlarmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param alarm_config: (experimental) Optional custom metric configuration. If not provided, defaults to CPU utilization with a 5% threshold.
        :param encryption: (experimental) Optional KMS Encryption Key to use for encrypting resources.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        props = Ec2AutomatedShutdownProps(
            alarm_config=alarm_config,
            encryption=encryption,
            lambda_configuration=lambda_configuration,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) All aspects can visit an IConstruct.

        :param node: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5994fe93c71f1c46730fa11383aefb416e003558c08ffb0724aa66546df71bf)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @jsii.enum(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.Ec2AutomatedShutdown.Ec2MetricName"
    )
    class Ec2MetricName(enum.Enum):
        '''(experimental) CloudWatch Alarm Metric Names.

        :stability: experimental
        '''

        CPU_UTILIZATION = "CPU_UTILIZATION"
        '''
        :stability: experimental
        '''
        DISK_READ_OPS = "DISK_READ_OPS"
        '''
        :stability: experimental
        '''
        DISK_WRITE_OPS = "DISK_WRITE_OPS"
        '''
        :stability: experimental
        '''
        DISK_READ_BYTES = "DISK_READ_BYTES"
        '''
        :stability: experimental
        '''
        DISK_WRITE_BYTES = "DISK_WRITE_BYTES"
        '''
        :stability: experimental
        '''
        NETWORK_IN = "NETWORK_IN"
        '''
        :stability: experimental
        '''
        NETWORK_OUT = "NETWORK_OUT"
        '''
        :stability: experimental
        '''
        NETWORK_PACKETS_IN = "NETWORK_PACKETS_IN"
        '''
        :stability: experimental
        '''
        NETWORK_PACKETS_OUT = "NETWORK_PACKETS_OUT"
        '''
        :stability: experimental
        '''
        STATUS_CHECK_FAILED = "STATUS_CHECK_FAILED"
        '''
        :stability: experimental
        '''
        STATUS_CHECK_FAILED_INSTANCE = "STATUS_CHECK_FAILED_INSTANCE"
        '''
        :stability: experimental
        '''
        STATUS_CHECK_FAILED_SYSTEM = "STATUS_CHECK_FAILED_SYSTEM"
        '''
        :stability: experimental
        '''
        METADATA_NO_TOKEN = "METADATA_NO_TOKEN"
        '''
        :stability: experimental
        '''
        CPU_CREDIT_USAGE = "CPU_CREDIT_USAGE"
        '''
        :stability: experimental
        '''
        CPU_CREDIT_BALANCE = "CPU_CREDIT_BALANCE"
        '''
        :stability: experimental
        '''
        CPU_SURPLUS_CREDIT_BALANCE = "CPU_SURPLUS_CREDIT_BALANCE"
        '''
        :stability: experimental
        '''
        CPU_SURPLUS_CREDITS_CHARGED = "CPU_SURPLUS_CREDITS_CHARGED"
        '''
        :stability: experimental
        '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.Ec2AutomatedShutdownProps",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_config": "alarmConfig",
        "encryption": "encryption",
        "lambda_configuration": "lambdaConfiguration",
    },
)
class Ec2AutomatedShutdownProps:
    def __init__(
        self,
        *,
        alarm_config: typing.Optional[typing.Union[AlarmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param alarm_config: (experimental) Optional custom metric configuration. If not provided, defaults to CPU utilization with a 5% threshold.
        :param encryption: (experimental) Optional KMS Encryption Key to use for encrypting resources.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if isinstance(alarm_config, dict):
            alarm_config = AlarmConfig(**alarm_config)
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83540f2382d64c8555b218f2ff30272931154c2fa9cc6a7208052b6295a558dc)
            check_type(argname="argument alarm_config", value=alarm_config, expected_type=type_hints["alarm_config"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alarm_config is not None:
            self._values["alarm_config"] = alarm_config
        if encryption is not None:
            self._values["encryption"] = encryption
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration

    @builtins.property
    def alarm_config(self) -> typing.Optional[AlarmConfig]:
        '''(experimental) Optional custom metric configuration.

        If not provided, defaults to CPU utilization with a 5% threshold.

        :stability: experimental
        '''
        result = self._values.get("alarm_config")
        return typing.cast(typing.Optional[AlarmConfig], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Optional KMS Encryption Key to use for encrypting resources.

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def lambda_configuration(self) -> typing.Optional[_LambdaConfiguration_9f8afc24]:
        '''(experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_LambdaConfiguration_9f8afc24], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ec2AutomatedShutdownProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class SecureSageMakerNotebook(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecureSageMakerNotebook",
):
    '''(experimental) Aspect that enforces security controls on SageMaker Notebook Instances by requiring VPC placement, disabling direct internet access, and preventing root access to the notebook environment.

    This Aspect enforces these settings through a combination of setting
    the CloudFormation properties on the Notebook resource and attaching a
    DENY policy to the role that is used by the notebook. The policy will enforce
    that the following API actions contain the correct properties to ensure
    network isolation and that the VPC subnets are set:

    - 'sagemaker:CreateTrainingJob',
    - 'sagemaker:CreateHyperParameterTuningJob',
    - 'sagemaker:CreateModel',
    - 'sagemaker:CreateProcessingJob'

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        allowed_launch_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
        notebook_subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
        direct_internet_access: typing.Optional[builtins.bool] = None,
        root_access: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param allowed_launch_subnets: (experimental) Sets the VPC Subnets that the SageMaker Notebook Instance is allowed to launch training and inference jobs into. This is enforced by adding DENY statements to the existing role that the Notebook Instance is using.
        :param notebook_subnet: (experimental) Sets the VPC Subnet for the Sagemaker Notebook Instance. This ensures the notebook is locked down to a specific VPC/subnet.
        :param direct_internet_access: (experimental) Sets the ``directInternetAccess`` property on the SageMaker Notebooks. By default, this is set to false to disable internet access on any SageMaker Notebook Instance that this aspect is applied to. Default: false
        :param root_access: (experimental) Sets the ``rootAccess`` property on the SageMaker Notebooks. By default, this is set to false to disable root access on any SageMaker Notebook Instance that this aspect is applied to. Default: false

        :stability: experimental
        '''
        props = SecureSageMakerNotebookProps(
            allowed_launch_subnets=allowed_launch_subnets,
            notebook_subnet=notebook_subnet,
            direct_internet_access=direct_internet_access,
            root_access=root_access,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) All aspects can visit an IConstruct.

        :param node: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a464b02c9d6c229339c86791c1baab1f5ba38ab5169541c238b05bf23a2fd388)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecureSageMakerNotebookProps",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_launch_subnets": "allowedLaunchSubnets",
        "notebook_subnet": "notebookSubnet",
        "direct_internet_access": "directInternetAccess",
        "root_access": "rootAccess",
    },
)
class SecureSageMakerNotebookProps:
    def __init__(
        self,
        *,
        allowed_launch_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
        notebook_subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
        direct_internet_access: typing.Optional[builtins.bool] = None,
        root_access: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param allowed_launch_subnets: (experimental) Sets the VPC Subnets that the SageMaker Notebook Instance is allowed to launch training and inference jobs into. This is enforced by adding DENY statements to the existing role that the Notebook Instance is using.
        :param notebook_subnet: (experimental) Sets the VPC Subnet for the Sagemaker Notebook Instance. This ensures the notebook is locked down to a specific VPC/subnet.
        :param direct_internet_access: (experimental) Sets the ``directInternetAccess`` property on the SageMaker Notebooks. By default, this is set to false to disable internet access on any SageMaker Notebook Instance that this aspect is applied to. Default: false
        :param root_access: (experimental) Sets the ``rootAccess`` property on the SageMaker Notebooks. By default, this is set to false to disable root access on any SageMaker Notebook Instance that this aspect is applied to. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0197024255c2663b7f9595b48f375b3bd3bb1aad713992f2d1205a74c784028)
            check_type(argname="argument allowed_launch_subnets", value=allowed_launch_subnets, expected_type=type_hints["allowed_launch_subnets"])
            check_type(argname="argument notebook_subnet", value=notebook_subnet, expected_type=type_hints["notebook_subnet"])
            check_type(argname="argument direct_internet_access", value=direct_internet_access, expected_type=type_hints["direct_internet_access"])
            check_type(argname="argument root_access", value=root_access, expected_type=type_hints["root_access"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allowed_launch_subnets": allowed_launch_subnets,
            "notebook_subnet": notebook_subnet,
        }
        if direct_internet_access is not None:
            self._values["direct_internet_access"] = direct_internet_access
        if root_access is not None:
            self._values["root_access"] = root_access

    @builtins.property
    def allowed_launch_subnets(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
        '''(experimental) Sets the VPC Subnets that the SageMaker Notebook Instance is allowed to launch training and inference jobs into.

        This is enforced by adding
        DENY statements to the existing role that the Notebook Instance is using.

        :stability: experimental
        '''
        result = self._values.get("allowed_launch_subnets")
        assert result is not None, "Required property 'allowed_launch_subnets' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet], result)

    @builtins.property
    def notebook_subnet(self) -> _aws_cdk_aws_ec2_ceddda9d.ISubnet:
        '''(experimental) Sets the VPC Subnet for the Sagemaker Notebook Instance.

        This ensures the
        notebook is locked down to a specific VPC/subnet.

        :stability: experimental
        '''
        result = self._values.get("notebook_subnet")
        assert result is not None, "Required property 'notebook_subnet' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISubnet, result)

    @builtins.property
    def direct_internet_access(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Sets the ``directInternetAccess`` property on the SageMaker Notebooks.

        By default, this is set to false to disable internet access on any
        SageMaker Notebook Instance that this aspect is applied to.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("direct_internet_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def root_access(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Sets the ``rootAccess`` property on the SageMaker Notebooks.

        By default, this is set to false to disable root access on any
        SageMaker Notebook Instance that this aspect is applied to.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("root_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecureSageMakerNotebookProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class SecurityCompliance(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance",
):
    '''(experimental) Applies best practice security settings to be in compliance with security tools such as CDK Nag.

    This aspect automatically implements AWS security best practices and compliance
    requirements for various AWS services used in your CDK applications.
    It can be configured with custom settings and supports suppressing specific
    CDK Nag warnings with proper justification.

    :stability: experimental

    Example::

        import { App, Stack, Aspects } from 'aws-cdk-lib';
        import { Function, Runtime, Code } from 'aws-cdk-lib/aws-lambda';
        import { Bucket } from 'aws-cdk-lib/aws-s3';
        import { SecurityCompliance } from '../../../src/aspects/security-compliance';
        
        const app = new App();
        const stack = new Stack(app, 'MySecureStack');
        
        // Create resources
        const myBucket = new Bucket(stack, 'MyBucket');
        const myFunction = new Function(stack, 'MyFunction', {
            runtime: Runtime.NODEJS_18_X,
            handler: 'index.handler',
            code: Code.fromInline(
                'exports.handler = async () => { return { statusCode: 200 }; }'
            )
        });
        
        // Apply the SecurityCompliance aspect with custom settings
        const securityAspect = new SecurityCompliance({
            settings: {
                s3: {
                    serverAccessLogs: {
                        destinationBucketName: 'my-access-logs-bucket'
                    },
                    versioning: {
                        disabled: false
                    }
                },
                lambda: {
                    reservedConcurrentExecutions: {
                        concurrentExecutionCount: 5
                    }
                }
            },
            suppressions: {
                lambdaNotInVpc:
                    'This is a development environment where VPC is not required',
                iamNoInlinePolicies: 'Inline policies are acceptable for this use case'
            }
        });
        
        // Apply the aspect to the stack
        Aspects.of(app).add(securityAspect);
    '''

    def __init__(
        self,
        *,
        settings: typing.Optional[typing.Union["SecurityCompliance.Settings", typing.Dict[builtins.str, typing.Any]]] = None,
        suppressions: typing.Optional[typing.Union["SecurityCompliance.Suppressions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param settings: (experimental) Settings for the aspect.
        :param suppressions: (experimental) Suppressions to add for CDK Nag. You must add your own reasoning to each suppression. These helpers have been created for common nag suppression use-cases. It is recommended to review the suppressions that are added and ensure that they adhere to your organizational level of acceptance. Each suppression must be supplied with a reason for the suppression as a string to each suppression property. If you are not using CDK Nag or do not want to use any suppressions, you can ignore this property.

        :stability: experimental
        '''
        props = SecurityComplianceProps(settings=settings, suppressions=suppressions)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) Apply the aspect to the node.

        :param node: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db05dff640339d35745e9f941ea908a28824062de10fca4bd043936cb1e938cc)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.ApiGatewaySettings",
        jsii_struct_bases=[],
        name_mapping={"stage_method_logging": "stageMethodLogging"},
    )
    class ApiGatewaySettings:
        def __init__(
            self,
            *,
            stage_method_logging: typing.Optional[typing.Union["SecurityCompliance.StageMethodLogging", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''
            :param stage_method_logging: (experimental) Enable or disable CloudWatch logging for API Gateway stages. Resolves: - AwsSolutions-APIG6 Defaults to log all errors if not specified or disabled.

            :stability: experimental
            '''
            if isinstance(stage_method_logging, dict):
                stage_method_logging = SecurityCompliance.StageMethodLogging(**stage_method_logging)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__6c1dcc9c785279827d9e9f8e2df96f3964a9ade7f2cc4a5ff0844ac8ca6b4f09)
                check_type(argname="argument stage_method_logging", value=stage_method_logging, expected_type=type_hints["stage_method_logging"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if stage_method_logging is not None:
                self._values["stage_method_logging"] = stage_method_logging

        @builtins.property
        def stage_method_logging(
            self,
        ) -> typing.Optional["SecurityCompliance.StageMethodLogging"]:
            '''(experimental) Enable or disable CloudWatch logging for API Gateway stages.

            Resolves:

            - AwsSolutions-APIG6

            Defaults to log all errors if not specified or disabled.

            :stability: experimental
            '''
            result = self._values.get("stage_method_logging")
            return typing.cast(typing.Optional["SecurityCompliance.StageMethodLogging"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ApiGatewaySettings(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.DisableableSetting",
        jsii_struct_bases=[],
        name_mapping={"disabled": "disabled"},
    )
    class DisableableSetting:
        def __init__(self, *, disabled: typing.Optional[builtins.bool] = None) -> None:
            '''
            :param disabled: (experimental) Sets the setting to disabled. This does not actually make an impact on the setting itself, it just stops this aspect from making changes to the specific setting.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__33fa35466b85ee83692c7e6f2df89f4abe99fcb23f6f88ac91150f21359e8362)
                check_type(argname="argument disabled", value=disabled, expected_type=type_hints["disabled"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if disabled is not None:
                self._values["disabled"] = disabled

        @builtins.property
        def disabled(self) -> typing.Optional[builtins.bool]:
            '''(experimental) Sets the setting to disabled.

            This does not actually make an impact on
            the setting itself, it just stops this aspect from making changes to
            the specific setting.

            :stability: experimental
            '''
            result = self._values.get("disabled")
            return typing.cast(typing.Optional[builtins.bool], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DisableableSetting(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.DynamoDbSettings",
        jsii_struct_bases=[],
        name_mapping={"point_in_time_recovery": "pointInTimeRecovery"},
    )
    class DynamoDbSettings:
        def __init__(
            self,
            *,
            point_in_time_recovery: typing.Optional[typing.Union["SecurityCompliance.DisableableSetting", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''
            :param point_in_time_recovery: (experimental) Enables Point-in-Time Recovery for DynamoDB tables. Resolves: - AwsSolutions-DDB3 Defaults to true if not disabled.

            :stability: experimental
            '''
            if isinstance(point_in_time_recovery, dict):
                point_in_time_recovery = SecurityCompliance.DisableableSetting(**point_in_time_recovery)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__e8b4316bf128bad602db4e8b3d981ed5c0530fc64c7ce5925f4e6cd8aa10071b)
                check_type(argname="argument point_in_time_recovery", value=point_in_time_recovery, expected_type=type_hints["point_in_time_recovery"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if point_in_time_recovery is not None:
                self._values["point_in_time_recovery"] = point_in_time_recovery

        @builtins.property
        def point_in_time_recovery(
            self,
        ) -> typing.Optional["SecurityCompliance.DisableableSetting"]:
            '''(experimental) Enables Point-in-Time Recovery for DynamoDB tables.

            Resolves:

            - AwsSolutions-DDB3

            Defaults to true if not disabled.

            :stability: experimental
            '''
            result = self._values.get("point_in_time_recovery")
            return typing.cast(typing.Optional["SecurityCompliance.DisableableSetting"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DynamoDbSettings(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.EcsSettings",
        jsii_struct_bases=[],
        name_mapping={"cluster_container_insights": "clusterContainerInsights"},
    )
    class EcsSettings:
        def __init__(
            self,
            *,
            cluster_container_insights: typing.Optional[typing.Union["SecurityCompliance.DisableableSetting", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''
            :param cluster_container_insights: (experimental) Enables container insights for ECS clusters. Resolves: - AwsSolutions-ECS4 Defaults to ContainerInsights.ENABLED if not disabled.

            :stability: experimental
            '''
            if isinstance(cluster_container_insights, dict):
                cluster_container_insights = SecurityCompliance.DisableableSetting(**cluster_container_insights)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__63d69f82b44bc7c20da8cc479e9cb7f2172c89b2d90f25268371ee7ede09f441)
                check_type(argname="argument cluster_container_insights", value=cluster_container_insights, expected_type=type_hints["cluster_container_insights"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if cluster_container_insights is not None:
                self._values["cluster_container_insights"] = cluster_container_insights

        @builtins.property
        def cluster_container_insights(
            self,
        ) -> typing.Optional["SecurityCompliance.DisableableSetting"]:
            '''(experimental) Enables container insights for ECS clusters.

            Resolves:

            - AwsSolutions-ECS4

            Defaults to ContainerInsights.ENABLED if not disabled.

            :stability: experimental
            '''
            result = self._values.get("cluster_container_insights")
            return typing.cast(typing.Optional["SecurityCompliance.DisableableSetting"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EcsSettings(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.LambdaSettings",
        jsii_struct_bases=[],
        name_mapping={
            "reserved_concurrent_executions": "reservedConcurrentExecutions",
        },
    )
    class LambdaSettings:
        def __init__(
            self,
            *,
            reserved_concurrent_executions: typing.Optional[typing.Union["SecurityCompliance.ReservedConcurrentSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''
            :param reserved_concurrent_executions: (experimental) Enables reserved concurrent executions for Lambda Functions. Resolves: - NIST.800.53.R5-LambdaConcurrency Defaults to 1 if not disabled or set.

            :stability: experimental
            '''
            if isinstance(reserved_concurrent_executions, dict):
                reserved_concurrent_executions = SecurityCompliance.ReservedConcurrentSettings(**reserved_concurrent_executions)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b1cd9d50ff6a41d6034a149512591e2d5d04c6e36c450548742d82df4e44daae)
                check_type(argname="argument reserved_concurrent_executions", value=reserved_concurrent_executions, expected_type=type_hints["reserved_concurrent_executions"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if reserved_concurrent_executions is not None:
                self._values["reserved_concurrent_executions"] = reserved_concurrent_executions

        @builtins.property
        def reserved_concurrent_executions(
            self,
        ) -> typing.Optional["SecurityCompliance.ReservedConcurrentSettings"]:
            '''(experimental) Enables reserved concurrent executions for Lambda Functions.

            Resolves:

            - NIST.800.53.R5-LambdaConcurrency

            Defaults to 1 if not disabled or set.

            :stability: experimental
            '''
            result = self._values.get("reserved_concurrent_executions")
            return typing.cast(typing.Optional["SecurityCompliance.ReservedConcurrentSettings"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LambdaSettings(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.ReservedConcurrentSettings",
        jsii_struct_bases=[SecurityCompliance.DisableableSetting],
        name_mapping={
            "disabled": "disabled",
            "concurrent_execution_count": "concurrentExecutionCount",
        },
    )
    class ReservedConcurrentSettings(SecurityCompliance.DisableableSetting):
        def __init__(
            self,
            *,
            disabled: typing.Optional[builtins.bool] = None,
            concurrent_execution_count: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param disabled: (experimental) Sets the setting to disabled. This does not actually make an impact on the setting itself, it just stops this aspect from making changes to the specific setting.
            :param concurrent_execution_count: (experimental) The number of reserved concurrency executions. Resolves: - NIST.800.53.R5-LambdaConcurrency Defaults to 1 if not specified.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__265b360b46c03cdbde6b37aa39520a9bcd1fe769d7409f108e93219356623ea6)
                check_type(argname="argument disabled", value=disabled, expected_type=type_hints["disabled"])
                check_type(argname="argument concurrent_execution_count", value=concurrent_execution_count, expected_type=type_hints["concurrent_execution_count"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if disabled is not None:
                self._values["disabled"] = disabled
            if concurrent_execution_count is not None:
                self._values["concurrent_execution_count"] = concurrent_execution_count

        @builtins.property
        def disabled(self) -> typing.Optional[builtins.bool]:
            '''(experimental) Sets the setting to disabled.

            This does not actually make an impact on
            the setting itself, it just stops this aspect from making changes to
            the specific setting.

            :stability: experimental
            '''
            result = self._values.get("disabled")
            return typing.cast(typing.Optional[builtins.bool], result)

        @builtins.property
        def concurrent_execution_count(self) -> typing.Optional[jsii.Number]:
            '''(experimental) The number of reserved concurrency executions.

            Resolves:

            - NIST.800.53.R5-LambdaConcurrency

            Defaults to 1 if not specified.

            :stability: experimental
            '''
            result = self._values.get("concurrent_execution_count")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ReservedConcurrentSettings(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.S3Settings",
        jsii_struct_bases=[],
        name_mapping={
            "server_access_logs": "serverAccessLogs",
            "versioning": "versioning",
        },
    )
    class S3Settings:
        def __init__(
            self,
            *,
            server_access_logs: typing.Optional[typing.Union["SecurityCompliance.ServerAccessLogsSettings", typing.Dict[builtins.str, typing.Any]]] = None,
            versioning: typing.Optional[typing.Union["SecurityCompliance.DisableableSetting", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''
            :param server_access_logs: (experimental) Enable server access logs to a destination S3 bucket. Since this requires a destination S3 bucket, it is not set by default. You must set a target S3 bucket to enable access logs. Resolves: - AwsSolutions-S1 - NIST.800.53.R5-S3BucketLoggingEnabled
            :param versioning: (experimental) Enables versioning for S3 buckets. Resolves: - NIST.800.53.R5-S3BucketVersioningEnabled Defaults to true if not disabled.

            :stability: experimental
            '''
            if isinstance(server_access_logs, dict):
                server_access_logs = SecurityCompliance.ServerAccessLogsSettings(**server_access_logs)
            if isinstance(versioning, dict):
                versioning = SecurityCompliance.DisableableSetting(**versioning)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__18697aa80dc4cc4e2d1e4c083fc58e564e837fe76559f0b8c3101a4ead7e983d)
                check_type(argname="argument server_access_logs", value=server_access_logs, expected_type=type_hints["server_access_logs"])
                check_type(argname="argument versioning", value=versioning, expected_type=type_hints["versioning"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if server_access_logs is not None:
                self._values["server_access_logs"] = server_access_logs
            if versioning is not None:
                self._values["versioning"] = versioning

        @builtins.property
        def server_access_logs(
            self,
        ) -> typing.Optional["SecurityCompliance.ServerAccessLogsSettings"]:
            '''(experimental) Enable server access logs to a destination S3 bucket.

            Since this requires
            a destination S3 bucket, it is not set by default. You must set a target
            S3 bucket to enable access logs.

            Resolves:

            - AwsSolutions-S1
            - NIST.800.53.R5-S3BucketLoggingEnabled

            :stability: experimental
            '''
            result = self._values.get("server_access_logs")
            return typing.cast(typing.Optional["SecurityCompliance.ServerAccessLogsSettings"], result)

        @builtins.property
        def versioning(
            self,
        ) -> typing.Optional["SecurityCompliance.DisableableSetting"]:
            '''(experimental) Enables versioning for S3 buckets.

            Resolves:

            - NIST.800.53.R5-S3BucketVersioningEnabled

            Defaults to true if not disabled.

            :stability: experimental
            '''
            result = self._values.get("versioning")
            return typing.cast(typing.Optional["SecurityCompliance.DisableableSetting"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3Settings(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.ServerAccessLogsSettings",
        jsii_struct_bases=[],
        name_mapping={"destination_bucket_name": "destinationBucketName"},
    )
    class ServerAccessLogsSettings:
        def __init__(self, *, destination_bucket_name: builtins.str) -> None:
            '''
            :param destination_bucket_name: (experimental) The bucket where server access logs will be sent. This must be configured with the correct permissions to allow the target bucket to receive logs. If not specified, server access logs will not be enabled.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__31139829f4f9dd9f0214c3d840ec3f975aa6c8cb4476bf0a7db3beca0fc61914)
                check_type(argname="argument destination_bucket_name", value=destination_bucket_name, expected_type=type_hints["destination_bucket_name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "destination_bucket_name": destination_bucket_name,
            }

        @builtins.property
        def destination_bucket_name(self) -> builtins.str:
            '''(experimental) The bucket where server access logs will be sent.

            This must be configured
            with the correct permissions to allow the target bucket to receive logs.

            If not specified, server access logs will not be enabled.

            :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html
            :stability: experimental
            '''
            result = self._values.get("destination_bucket_name")
            assert result is not None, "Required property 'destination_bucket_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ServerAccessLogsSettings(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.Settings",
        jsii_struct_bases=[],
        name_mapping={
            "api_gateway": "apiGateway",
            "dynamo_db": "dynamoDb",
            "ecs": "ecs",
            "lambda_": "lambda",
            "s3": "s3",
            "step_functions": "stepFunctions",
        },
    )
    class Settings:
        def __init__(
            self,
            *,
            api_gateway: typing.Optional[typing.Union["SecurityCompliance.ApiGatewaySettings", typing.Dict[builtins.str, typing.Any]]] = None,
            dynamo_db: typing.Optional[typing.Union["SecurityCompliance.DynamoDbSettings", typing.Dict[builtins.str, typing.Any]]] = None,
            ecs: typing.Optional[typing.Union["SecurityCompliance.EcsSettings", typing.Dict[builtins.str, typing.Any]]] = None,
            lambda_: typing.Optional[typing.Union["SecurityCompliance.LambdaSettings", typing.Dict[builtins.str, typing.Any]]] = None,
            s3: typing.Optional[typing.Union["SecurityCompliance.S3Settings", typing.Dict[builtins.str, typing.Any]]] = None,
            step_functions: typing.Optional[typing.Union["SecurityCompliance.StepFunctionsSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''(experimental) Configuration settings for the security-compliance aspect.

            This interface provides a centralized way to configure security and compliance
            settings for various AWS resources. Each property corresponds to a specific
            AWS service and contains settings that help ensure resources comply with
            security best practices and compliance requirements.

            By default, most security settings are enabled unless explicitly disabled.
            Some settings may require additional configuration to be effective.

            :param api_gateway: (experimental) Security and compliance settings for API Gateway resources. Controls settings like method logging to ensure proper monitoring and auditability of API usage.
            :param dynamo_db: (experimental) Security and compliance settings for DynamoDB tables. Configures features like Point-in-Time Recovery to improve data durability and recoverability.
            :param ecs: (experimental) Security and compliance settings for ECS clusters and services. Enables features like Container Insights for better monitoring and observability.
            :param lambda_: (experimental) Security and compliance settings for Lambda functions. Controls execution limits and other settings to improve the security posture of Lambda functions.
            :param s3: (experimental) Security and compliance settings for S3 buckets. Configures features like versioning and server access logging to improve data protection and meet compliance requirements.
            :param step_functions: (experimental) Security and compliance settings for Step Functions state machines. Controls settings like X-Ray tracing to improve observability and debugging capabilities.

            :stability: experimental

            Example::

                const securitySettings: Settings = {
                  lambda: {
                    reservedConcurrentExecutions: {
                      concurrentExecutionCount: 5
                    }
                  },
                  s3: {
                    serverAccessLogs: {
                      destinationBucketName: 'access-logs-bucket'
                    }
                  }
                };
            '''
            if isinstance(api_gateway, dict):
                api_gateway = SecurityCompliance.ApiGatewaySettings(**api_gateway)
            if isinstance(dynamo_db, dict):
                dynamo_db = SecurityCompliance.DynamoDbSettings(**dynamo_db)
            if isinstance(ecs, dict):
                ecs = SecurityCompliance.EcsSettings(**ecs)
            if isinstance(lambda_, dict):
                lambda_ = SecurityCompliance.LambdaSettings(**lambda_)
            if isinstance(s3, dict):
                s3 = SecurityCompliance.S3Settings(**s3)
            if isinstance(step_functions, dict):
                step_functions = SecurityCompliance.StepFunctionsSettings(**step_functions)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__7711615081579aea2190660ca8b49b463c0de1b90ebbd9185321202898544a12)
                check_type(argname="argument api_gateway", value=api_gateway, expected_type=type_hints["api_gateway"])
                check_type(argname="argument dynamo_db", value=dynamo_db, expected_type=type_hints["dynamo_db"])
                check_type(argname="argument ecs", value=ecs, expected_type=type_hints["ecs"])
                check_type(argname="argument lambda_", value=lambda_, expected_type=type_hints["lambda_"])
                check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
                check_type(argname="argument step_functions", value=step_functions, expected_type=type_hints["step_functions"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if api_gateway is not None:
                self._values["api_gateway"] = api_gateway
            if dynamo_db is not None:
                self._values["dynamo_db"] = dynamo_db
            if ecs is not None:
                self._values["ecs"] = ecs
            if lambda_ is not None:
                self._values["lambda_"] = lambda_
            if s3 is not None:
                self._values["s3"] = s3
            if step_functions is not None:
                self._values["step_functions"] = step_functions

        @builtins.property
        def api_gateway(
            self,
        ) -> typing.Optional["SecurityCompliance.ApiGatewaySettings"]:
            '''(experimental) Security and compliance settings for API Gateway resources.

            Controls settings like method logging to ensure proper monitoring
            and auditability of API usage.

            :stability: experimental
            '''
            result = self._values.get("api_gateway")
            return typing.cast(typing.Optional["SecurityCompliance.ApiGatewaySettings"], result)

        @builtins.property
        def dynamo_db(self) -> typing.Optional["SecurityCompliance.DynamoDbSettings"]:
            '''(experimental) Security and compliance settings for DynamoDB tables.

            Configures features like Point-in-Time Recovery to improve
            data durability and recoverability.

            :stability: experimental
            '''
            result = self._values.get("dynamo_db")
            return typing.cast(typing.Optional["SecurityCompliance.DynamoDbSettings"], result)

        @builtins.property
        def ecs(self) -> typing.Optional["SecurityCompliance.EcsSettings"]:
            '''(experimental) Security and compliance settings for ECS clusters and services.

            Enables features like Container Insights for better
            monitoring and observability.

            :stability: experimental
            '''
            result = self._values.get("ecs")
            return typing.cast(typing.Optional["SecurityCompliance.EcsSettings"], result)

        @builtins.property
        def lambda_(self) -> typing.Optional["SecurityCompliance.LambdaSettings"]:
            '''(experimental) Security and compliance settings for Lambda functions.

            Controls execution limits and other settings to improve
            the security posture of Lambda functions.

            :stability: experimental
            '''
            result = self._values.get("lambda_")
            return typing.cast(typing.Optional["SecurityCompliance.LambdaSettings"], result)

        @builtins.property
        def s3(self) -> typing.Optional["SecurityCompliance.S3Settings"]:
            '''(experimental) Security and compliance settings for S3 buckets.

            Configures features like versioning and server access logging
            to improve data protection and meet compliance requirements.

            :stability: experimental
            '''
            result = self._values.get("s3")
            return typing.cast(typing.Optional["SecurityCompliance.S3Settings"], result)

        @builtins.property
        def step_functions(
            self,
        ) -> typing.Optional["SecurityCompliance.StepFunctionsSettings"]:
            '''(experimental) Security and compliance settings for Step Functions state machines.

            Controls settings like X-Ray tracing to improve
            observability and debugging capabilities.

            :stability: experimental
            '''
            result = self._values.get("step_functions")
            return typing.cast(typing.Optional["SecurityCompliance.StepFunctionsSettings"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "Settings(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.StageMethodLogging",
        jsii_struct_bases=[SecurityCompliance.DisableableSetting],
        name_mapping={"disabled": "disabled", "logging_level": "loggingLevel"},
    )
    class StageMethodLogging(SecurityCompliance.DisableableSetting):
        def __init__(
            self,
            *,
            disabled: typing.Optional[builtins.bool] = None,
            logging_level: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodLoggingLevel] = None,
        ) -> None:
            '''
            :param disabled: (experimental) Sets the setting to disabled. This does not actually make an impact on the setting itself, it just stops this aspect from making changes to the specific setting.
            :param logging_level: (experimental) The logging level to use for the stage method logging. This applies to all resources and methods in all stages. Defaults to MethodLoggingLevel.ERROR if not specified.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__7ddb2f67429fe5292f54c87f7b2d23ea314f582033cb8e9b3e3dc95ffcd84774)
                check_type(argname="argument disabled", value=disabled, expected_type=type_hints["disabled"])
                check_type(argname="argument logging_level", value=logging_level, expected_type=type_hints["logging_level"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if disabled is not None:
                self._values["disabled"] = disabled
            if logging_level is not None:
                self._values["logging_level"] = logging_level

        @builtins.property
        def disabled(self) -> typing.Optional[builtins.bool]:
            '''(experimental) Sets the setting to disabled.

            This does not actually make an impact on
            the setting itself, it just stops this aspect from making changes to
            the specific setting.

            :stability: experimental
            '''
            result = self._values.get("disabled")
            return typing.cast(typing.Optional[builtins.bool], result)

        @builtins.property
        def logging_level(
            self,
        ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodLoggingLevel]:
            '''(experimental) The logging level to use for the stage method logging. This applies to all resources and methods in all stages.

            Defaults to MethodLoggingLevel.ERROR if not specified.

            :stability: experimental
            '''
            result = self._values.get("logging_level")
            return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodLoggingLevel], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StageMethodLogging(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.StepFunctionsSettings",
        jsii_struct_bases=[],
        name_mapping={"tracing": "tracing"},
    )
    class StepFunctionsSettings:
        def __init__(
            self,
            *,
            tracing: typing.Optional[typing.Union["SecurityCompliance.DisableableSetting", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''
            :param tracing: (experimental) Enable or disable X-Ray tracing. Resolves: - AwsSolutions-SF2 Defaults to true if not disabled.

            :stability: experimental
            '''
            if isinstance(tracing, dict):
                tracing = SecurityCompliance.DisableableSetting(**tracing)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__98bfbe22e4349e668fb1b9ce268cf64e5978c7166650dcb2ba543a1e7a458d08)
                check_type(argname="argument tracing", value=tracing, expected_type=type_hints["tracing"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if tracing is not None:
                self._values["tracing"] = tracing

        @builtins.property
        def tracing(self) -> typing.Optional["SecurityCompliance.DisableableSetting"]:
            '''(experimental) Enable or disable X-Ray tracing.

            Resolves:

            - AwsSolutions-SF2

            Defaults to true if not disabled.

            :stability: experimental
            '''
            result = self._values.get("tracing")
            return typing.cast(typing.Optional["SecurityCompliance.DisableableSetting"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StepFunctionsSettings(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityCompliance.Suppressions",
        jsii_struct_bases=[],
        name_mapping={
            "cdk_common_grants": "cdkCommonGrants",
            "cdk_generated_resources": "cdkGeneratedResources",
            "iam_no_inline_policies": "iamNoInlinePolicies",
            "lambda_no_dlq": "lambdaNoDlq",
            "lambda_not_in_vpc": "lambdaNotInVpc",
            "s3_bucket_replication": "s3BucketReplication",
        },
    )
    class Suppressions:
        def __init__(
            self,
            *,
            cdk_common_grants: typing.Optional[builtins.str] = None,
            cdk_generated_resources: typing.Optional[builtins.str] = None,
            iam_no_inline_policies: typing.Optional[builtins.str] = None,
            lambda_no_dlq: typing.Optional[builtins.str] = None,
            lambda_not_in_vpc: typing.Optional[builtins.str] = None,
            s3_bucket_replication: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param cdk_common_grants: (experimental) Suppressions to add for CDK Nag on CDK generated policies. If enabled this will add a stack suppression for ``AwsSolutions-IAM5`` on the actions that CDK commonly generates when using ``.grant(...)`` methods.
            :param cdk_generated_resources: (experimental) Suppressions to add for CDK Nag on CDK generated resources. If enabled this will suppress ``AwsSolutions-IAM5`` on the policies that are created by CDK Generated Lambda functions, as well as other CDK generated resources such as Log Groups and Step Functions that support CDK generated custom resources. This only applies to resources that are created by the underlying CDK. - Policy suppression: AwsSolutions-IAM5 - Log Group suppression: NIST.800.53.R5-CloudWatchLogGroupEncrypted - Step Function suppression: AwsSolutions-SF1
            :param iam_no_inline_policies: (experimental) Adds a stack suppression for ``NIST.800.53.R5-IAMNoInlinePolicy``. CDK commonly uses inline policies when adding permissions.
            :param lambda_no_dlq: (experimental) Adds a stack suppression for ``NIST.800.53.R5-LambdaDLQ``.
            :param lambda_not_in_vpc: (experimental) Adds a stack suppression for ``NIST.800.53.R5-LambdaInsideVPC``.
            :param s3_bucket_replication: (experimental) Adds a stack suppression for ``NIST.800.53.R5-S3BucketReplicationEnabled``.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__5794bd7a1b8dd2948f03071fa77248d38b9a0115453d8c77307d3c4df8aa9ba1)
                check_type(argname="argument cdk_common_grants", value=cdk_common_grants, expected_type=type_hints["cdk_common_grants"])
                check_type(argname="argument cdk_generated_resources", value=cdk_generated_resources, expected_type=type_hints["cdk_generated_resources"])
                check_type(argname="argument iam_no_inline_policies", value=iam_no_inline_policies, expected_type=type_hints["iam_no_inline_policies"])
                check_type(argname="argument lambda_no_dlq", value=lambda_no_dlq, expected_type=type_hints["lambda_no_dlq"])
                check_type(argname="argument lambda_not_in_vpc", value=lambda_not_in_vpc, expected_type=type_hints["lambda_not_in_vpc"])
                check_type(argname="argument s3_bucket_replication", value=s3_bucket_replication, expected_type=type_hints["s3_bucket_replication"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if cdk_common_grants is not None:
                self._values["cdk_common_grants"] = cdk_common_grants
            if cdk_generated_resources is not None:
                self._values["cdk_generated_resources"] = cdk_generated_resources
            if iam_no_inline_policies is not None:
                self._values["iam_no_inline_policies"] = iam_no_inline_policies
            if lambda_no_dlq is not None:
                self._values["lambda_no_dlq"] = lambda_no_dlq
            if lambda_not_in_vpc is not None:
                self._values["lambda_not_in_vpc"] = lambda_not_in_vpc
            if s3_bucket_replication is not None:
                self._values["s3_bucket_replication"] = s3_bucket_replication

        @builtins.property
        def cdk_common_grants(self) -> typing.Optional[builtins.str]:
            '''(experimental) Suppressions to add for CDK Nag on CDK generated policies.

            If enabled
            this will add a stack suppression for ``AwsSolutions-IAM5`` on the actions
            that CDK commonly generates when using ``.grant(...)`` methods.

            :stability: experimental
            '''
            result = self._values.get("cdk_common_grants")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def cdk_generated_resources(self) -> typing.Optional[builtins.str]:
            '''(experimental) Suppressions to add for CDK Nag on CDK generated resources.

            If enabled
            this will suppress ``AwsSolutions-IAM5`` on the policies that are
            created by CDK Generated Lambda functions, as well as other CDK generated
            resources such as Log Groups and Step Functions that support CDK
            generated custom resources. This only applies to resources that are
            created by the underlying CDK.

            - Policy suppression: AwsSolutions-IAM5
            - Log Group suppression: NIST.800.53.R5-CloudWatchLogGroupEncrypted
            - Step Function suppression: AwsSolutions-SF1

            :stability: experimental
            '''
            result = self._values.get("cdk_generated_resources")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def iam_no_inline_policies(self) -> typing.Optional[builtins.str]:
            '''(experimental) Adds a stack suppression for ``NIST.800.53.R5-IAMNoInlinePolicy``. CDK commonly uses inline policies when adding permissions.

            :stability: experimental
            '''
            result = self._values.get("iam_no_inline_policies")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def lambda_no_dlq(self) -> typing.Optional[builtins.str]:
            '''(experimental) Adds a stack suppression for ``NIST.800.53.R5-LambdaDLQ``.

            :stability: experimental
            '''
            result = self._values.get("lambda_no_dlq")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def lambda_not_in_vpc(self) -> typing.Optional[builtins.str]:
            '''(experimental) Adds a stack suppression for ``NIST.800.53.R5-LambdaInsideVPC``.

            :stability: experimental
            '''
            result = self._values.get("lambda_not_in_vpc")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def s3_bucket_replication(self) -> typing.Optional[builtins.str]:
            '''(experimental) Adds a stack suppression for ``NIST.800.53.R5-S3BucketReplicationEnabled``.

            :stability: experimental
            '''
            result = self._values.get("s3_bucket_replication")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "Suppressions(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.SecurityComplianceProps",
    jsii_struct_bases=[],
    name_mapping={"settings": "settings", "suppressions": "suppressions"},
)
class SecurityComplianceProps:
    def __init__(
        self,
        *,
        settings: typing.Optional[typing.Union[SecurityCompliance.Settings, typing.Dict[builtins.str, typing.Any]]] = None,
        suppressions: typing.Optional[typing.Union[SecurityCompliance.Suppressions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param settings: (experimental) Settings for the aspect.
        :param suppressions: (experimental) Suppressions to add for CDK Nag. You must add your own reasoning to each suppression. These helpers have been created for common nag suppression use-cases. It is recommended to review the suppressions that are added and ensure that they adhere to your organizational level of acceptance. Each suppression must be supplied with a reason for the suppression as a string to each suppression property. If you are not using CDK Nag or do not want to use any suppressions, you can ignore this property.

        :stability: experimental
        '''
        if isinstance(settings, dict):
            settings = SecurityCompliance.Settings(**settings)
        if isinstance(suppressions, dict):
            suppressions = SecurityCompliance.Suppressions(**suppressions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a022c8c21b87b78e68747a930ed3f5bac35bfeff561172bbeea6bdce1047d988)
            check_type(argname="argument settings", value=settings, expected_type=type_hints["settings"])
            check_type(argname="argument suppressions", value=suppressions, expected_type=type_hints["suppressions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if settings is not None:
            self._values["settings"] = settings
        if suppressions is not None:
            self._values["suppressions"] = suppressions

    @builtins.property
    def settings(self) -> typing.Optional[SecurityCompliance.Settings]:
        '''(experimental) Settings for the aspect.

        :stability: experimental
        '''
        result = self._values.get("settings")
        return typing.cast(typing.Optional[SecurityCompliance.Settings], result)

    @builtins.property
    def suppressions(self) -> typing.Optional[SecurityCompliance.Suppressions]:
        '''(experimental) Suppressions to add for CDK Nag.

        You must add your own reasoning to each
        suppression. These helpers have been created for common nag suppression
        use-cases. It is recommended to review the suppressions that are added
        and ensure that they adhere to your organizational level of acceptance.
        Each suppression must be supplied with a reason for the suppression as
        a string to each suppression property.

        If you are not using CDK Nag or do not want to use any suppressions, you
        can ignore this property.

        :stability: experimental
        '''
        result = self._values.get("suppressions")
        return typing.cast(typing.Optional[SecurityCompliance.Suppressions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityComplianceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class SetLogRetention(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.SetLogRetention",
):
    '''(experimental) Aspect that sets the log retention period for CloudWatch log groups to a user-supplied retention period.

    :stability: experimental

    Example::

        import { App, Aspects } from 'aws-cdk-lib';
        import { RetentionDays } from 'aws-cdk-lib/aws-logs';
        import { SetLogRetention } from '@cdklabs/cdk-proserve-lib/aspects';
        
        const app = new App();
        
        Aspects.of(app).add(
          new SetLogRetention({ period: RetentionDays.EIGHTEEN_MONTHS })
        );
    '''

    def __init__(self, *, period: _aws_cdk_aws_logs_ceddda9d.RetentionDays) -> None:
        '''(experimental) Creates a new instance of SetLogRetention.

        :param period: (experimental) The retention period for the logs.

        :stability: experimental
        '''
        props = SetLogRetentionProps(period=period)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) Visits a construct and sets log retention if applicable.

        :param node: The construct being visited.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7918d457f7130a0f58324294dfa0117ad91d007dd1efe356a28e1e7b14078104)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.SetLogRetentionProps",
    jsii_struct_bases=[],
    name_mapping={"period": "period"},
)
class SetLogRetentionProps:
    def __init__(self, *, period: _aws_cdk_aws_logs_ceddda9d.RetentionDays) -> None:
        '''(experimental) Properties for configuring log retention settings.

        :param period: (experimental) The retention period for the logs.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72586255662d60e597233cf4d140d0e0bbb27e128c37bd403552be4906e4252b)
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "period": period,
        }

    @builtins.property
    def period(self) -> _aws_cdk_aws_logs_ceddda9d.RetentionDays:
        '''(experimental) The retention period for the logs.

        :stability: experimental
        '''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.RetentionDays, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SetLogRetentionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class SqsRequireSsl(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.aspects.SqsRequireSsl",
):
    '''(experimental) Enforces SSL/TLS requirements on Simple Queue Service (SQS) for all resources that the aspect applies to.

    This is accomplished by adding a resource policy to any SQS queue that denies
    all actions when the request is not made over a secure transport.

    :stability: experimental

    Example::

        import { App, Aspects } from 'aws-cdk-lib';
        import { SqsRequireSsl } from '@cdklabs/cdk-proserve-lib/aspects';
        
        const app = new App();
        
        Aspects.of(app).add(new SqsRequireSsl());
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''(experimental) Visits a construct and adds SSL/TLS requirement policy if it's an SQS queue.

        :param node: The construct being visited.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a88c2c2ac86ce27464fcccd4cd5509db7184536f595cf22451890aac8b865258)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


__all__ = [
    "AlarmConfig",
    "ApplyRemovalPolicy",
    "ApplyRemovalPolicyProps",
    "CreateLambdaLogGroup",
    "Ec2AutomatedShutdown",
    "Ec2AutomatedShutdownProps",
    "SecureSageMakerNotebook",
    "SecureSageMakerNotebookProps",
    "SecurityCompliance",
    "SecurityComplianceProps",
    "SetLogRetention",
    "SetLogRetentionProps",
    "SqsRequireSsl",
]

publication.publish()

def _typecheckingstub__39e80c1625a9aebade1607b9063a75a5e101289462594aab3e82799e39c067ab(
    *,
    comparison_operator: _aws_cdk_aws_cloudwatch_ceddda9d.ComparisonOperator,
    datapoints_to_alarm: jsii.Number,
    evaluation_periods: jsii.Number,
    metric_name: Ec2AutomatedShutdown.Ec2MetricName,
    period: _aws_cdk_ceddda9d.Duration,
    statistic: builtins.str,
    threshold: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8ce1ca35633c77f43304cf7f1782f1ebf1496f151645dca582fc865fe0fe866(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__858f2996365d3ec27b04534ec073a42ea6b65c3aa7cc1fa650e2765c14c83528(
    *,
    removal_policy: _aws_cdk_ceddda9d.RemovalPolicy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa6b301934b30a296211f1f67b29307771270f03bbb136c1415e30d55396295a(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5994fe93c71f1c46730fa11383aefb416e003558c08ffb0724aa66546df71bf(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83540f2382d64c8555b218f2ff30272931154c2fa9cc6a7208052b6295a558dc(
    *,
    alarm_config: typing.Optional[typing.Union[AlarmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a464b02c9d6c229339c86791c1baab1f5ba38ab5169541c238b05bf23a2fd388(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0197024255c2663b7f9595b48f375b3bd3bb1aad713992f2d1205a74c784028(
    *,
    allowed_launch_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
    notebook_subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
    direct_internet_access: typing.Optional[builtins.bool] = None,
    root_access: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db05dff640339d35745e9f941ea908a28824062de10fca4bd043936cb1e938cc(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c1dcc9c785279827d9e9f8e2df96f3964a9ade7f2cc4a5ff0844ac8ca6b4f09(
    *,
    stage_method_logging: typing.Optional[typing.Union[SecurityCompliance.StageMethodLogging, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33fa35466b85ee83692c7e6f2df89f4abe99fcb23f6f88ac91150f21359e8362(
    *,
    disabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8b4316bf128bad602db4e8b3d981ed5c0530fc64c7ce5925f4e6cd8aa10071b(
    *,
    point_in_time_recovery: typing.Optional[typing.Union[SecurityCompliance.DisableableSetting, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63d69f82b44bc7c20da8cc479e9cb7f2172c89b2d90f25268371ee7ede09f441(
    *,
    cluster_container_insights: typing.Optional[typing.Union[SecurityCompliance.DisableableSetting, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1cd9d50ff6a41d6034a149512591e2d5d04c6e36c450548742d82df4e44daae(
    *,
    reserved_concurrent_executions: typing.Optional[typing.Union[SecurityCompliance.ReservedConcurrentSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__265b360b46c03cdbde6b37aa39520a9bcd1fe769d7409f108e93219356623ea6(
    *,
    disabled: typing.Optional[builtins.bool] = None,
    concurrent_execution_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18697aa80dc4cc4e2d1e4c083fc58e564e837fe76559f0b8c3101a4ead7e983d(
    *,
    server_access_logs: typing.Optional[typing.Union[SecurityCompliance.ServerAccessLogsSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    versioning: typing.Optional[typing.Union[SecurityCompliance.DisableableSetting, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31139829f4f9dd9f0214c3d840ec3f975aa6c8cb4476bf0a7db3beca0fc61914(
    *,
    destination_bucket_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7711615081579aea2190660ca8b49b463c0de1b90ebbd9185321202898544a12(
    *,
    api_gateway: typing.Optional[typing.Union[SecurityCompliance.ApiGatewaySettings, typing.Dict[builtins.str, typing.Any]]] = None,
    dynamo_db: typing.Optional[typing.Union[SecurityCompliance.DynamoDbSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    ecs: typing.Optional[typing.Union[SecurityCompliance.EcsSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_: typing.Optional[typing.Union[SecurityCompliance.LambdaSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    s3: typing.Optional[typing.Union[SecurityCompliance.S3Settings, typing.Dict[builtins.str, typing.Any]]] = None,
    step_functions: typing.Optional[typing.Union[SecurityCompliance.StepFunctionsSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ddb2f67429fe5292f54c87f7b2d23ea314f582033cb8e9b3e3dc95ffcd84774(
    *,
    disabled: typing.Optional[builtins.bool] = None,
    logging_level: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodLoggingLevel] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98bfbe22e4349e668fb1b9ce268cf64e5978c7166650dcb2ba543a1e7a458d08(
    *,
    tracing: typing.Optional[typing.Union[SecurityCompliance.DisableableSetting, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5794bd7a1b8dd2948f03071fa77248d38b9a0115453d8c77307d3c4df8aa9ba1(
    *,
    cdk_common_grants: typing.Optional[builtins.str] = None,
    cdk_generated_resources: typing.Optional[builtins.str] = None,
    iam_no_inline_policies: typing.Optional[builtins.str] = None,
    lambda_no_dlq: typing.Optional[builtins.str] = None,
    lambda_not_in_vpc: typing.Optional[builtins.str] = None,
    s3_bucket_replication: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a022c8c21b87b78e68747a930ed3f5bac35bfeff561172bbeea6bdce1047d988(
    *,
    settings: typing.Optional[typing.Union[SecurityCompliance.Settings, typing.Dict[builtins.str, typing.Any]]] = None,
    suppressions: typing.Optional[typing.Union[SecurityCompliance.Suppressions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7918d457f7130a0f58324294dfa0117ad91d007dd1efe356a28e1e7b14078104(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72586255662d60e597233cf4d140d0e0bbb27e128c37bd403552be4906e4252b(
    *,
    period: _aws_cdk_aws_logs_ceddda9d.RetentionDays,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a88c2c2ac86ce27464fcccd4cd5509db7184536f595cf22451890aac8b865258(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass
