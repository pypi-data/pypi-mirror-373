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

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.types.AwsCustomResourceLambdaConfiguration",
    jsii_struct_bases=[],
    name_mapping={"subnets": "subnets", "vpc": "vpc"},
)
class AwsCustomResourceLambdaConfiguration:
    def __init__(
        self,
        *,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param subnets: (experimental) Optional subnet selection for the Lambda functions.
        :param vpc: (experimental) VPC where the Lambda functions will be deployed.

        :stability: experimental
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94c5cee93e244643d0253938483ebf4729a03d1dbc4432b65477c09475f2f439)
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Optional subnet selection for the Lambda functions.

        :stability: experimental
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) VPC where the Lambda functions will be deployed.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsCustomResourceLambdaConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AwsManagedPolicy(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.types.AwsManagedPolicy",
):
    '''(experimental) AWS Managed Policy.

    :stability: experimental
    '''

    @jsii.python.classproperty
    @jsii.member(jsii_name="ADMINISTRATOR_ACCESS")
    def ADMINISTRATOR_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ADMINISTRATOR_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ADMINISTRATOR_ACCESS_AMPLIFY")
    def ADMINISTRATOR_ACCESS_AMPLIFY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ADMINISTRATOR_ACCESS_AMPLIFY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ADMINISTRATOR_ACCESS_AWS_ELASTIC_BEANSTALK")
    def ADMINISTRATOR_ACCESS_AWS_ELASTIC_BEANSTALK(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ADMINISTRATOR_ACCESS_AWS_ELASTIC_BEANSTALK"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI_OPS_ASSISTANT_POLICY")
    def AI_OPS_ASSISTANT_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AI_OPS_ASSISTANT_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI_OPS_CONSOLE_ADMIN_POLICY")
    def AI_OPS_CONSOLE_ADMIN_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AI_OPS_CONSOLE_ADMIN_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI_OPS_OPERATOR_ACCESS")
    def AI_OPS_OPERATOR_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AI_OPS_OPERATOR_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI_OPS_READ_ONLY_ACCESS")
    def AI_OPS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AI_OPS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ALEXA_FOR_BUSINESS_DEVICE_SETUP")
    def ALEXA_FOR_BUSINESS_DEVICE_SETUP(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ALEXA_FOR_BUSINESS_DEVICE_SETUP"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ALEXA_FOR_BUSINESS_FULL_ACCESS")
    def ALEXA_FOR_BUSINESS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ALEXA_FOR_BUSINESS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ALEXA_FOR_BUSINESS_GATEWAY_EXECUTION")
    def ALEXA_FOR_BUSINESS_GATEWAY_EXECUTION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ALEXA_FOR_BUSINESS_GATEWAY_EXECUTION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ALEXA_FOR_BUSINESS_LIFESIZE_DELEGATED_ACCESS_POLICY")
    def ALEXA_FOR_BUSINESS_LIFESIZE_DELEGATED_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ALEXA_FOR_BUSINESS_LIFESIZE_DELEGATED_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ALEXA_FOR_BUSINESS_POLY_DELEGATED_ACCESS_POLICY")
    def ALEXA_FOR_BUSINESS_POLY_DELEGATED_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ALEXA_FOR_BUSINESS_POLY_DELEGATED_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ALEXA_FOR_BUSINESS_READ_ONLY_ACCESS")
    def ALEXA_FOR_BUSINESS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ALEXA_FOR_BUSINESS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_API_GATEWAY_ADMINISTRATOR")
    def AMAZON_API_GATEWAY_ADMINISTRATOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_API_GATEWAY_ADMINISTRATOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_API_GATEWAY_INVOKE_FULL_ACCESS")
    def AMAZON_API_GATEWAY_INVOKE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_API_GATEWAY_INVOKE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_APP_FLOW_FULL_ACCESS")
    def AMAZON_APP_FLOW_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_APP_FLOW_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_APP_FLOW_READ_ONLY_ACCESS")
    def AMAZON_APP_FLOW_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_APP_FLOW_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_APP_STREAM_FULL_ACCESS")
    def AMAZON_APP_STREAM_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_APP_STREAM_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_APP_STREAM_READ_ONLY_ACCESS")
    def AMAZON_APP_STREAM_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_APP_STREAM_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ATHENA_FULL_ACCESS")
    def AMAZON_ATHENA_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ATHENA_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_AUGMENTED_AI_FULL_ACCESS")
    def AMAZON_AUGMENTED_AI_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_AUGMENTED_AI_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_AUGMENTED_AI_HUMAN_LOOP_FULL_ACCESS")
    def AMAZON_AUGMENTED_AI_HUMAN_LOOP_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_AUGMENTED_AI_HUMAN_LOOP_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_AUGMENTED_AI_INTEGRATED_API_ACCESS")
    def AMAZON_AUGMENTED_AI_INTEGRATED_API_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_AUGMENTED_AI_INTEGRATED_API_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_AURORA_DSQL_CONSOLE_FULL_ACCESS")
    def AMAZON_AURORA_DSQL_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_AURORA_DSQL_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_AURORA_DSQL_FULL_ACCESS")
    def AMAZON_AURORA_DSQL_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_AURORA_DSQL_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_AURORA_DSQL_READ_ONLY_ACCESS")
    def AMAZON_AURORA_DSQL_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_AURORA_DSQL_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_BEDROCK_FULL_ACCESS")
    def AMAZON_BEDROCK_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_BEDROCK_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_BEDROCK_READ_ONLY")
    def AMAZON_BEDROCK_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_BEDROCK_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_BEDROCK_STUDIO_PERMISSIONS_BOUNDARY")
    def AMAZON_BEDROCK_STUDIO_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_BEDROCK_STUDIO_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_BRAKET_FULL_ACCESS")
    def AMAZON_BRAKET_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_BRAKET_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_BRAKET_JOBS_EXECUTION_POLICY")
    def AMAZON_BRAKET_JOBS_EXECUTION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_BRAKET_JOBS_EXECUTION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CHIME_FULL_ACCESS")
    def AMAZON_CHIME_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CHIME_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CHIME_READ_ONLY")
    def AMAZON_CHIME_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CHIME_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CHIME_SDK")
    def AMAZON_CHIME_SDK(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CHIME_SDK"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CHIME_USER_MANAGEMENT")
    def AMAZON_CHIME_USER_MANAGEMENT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CHIME_USER_MANAGEMENT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CLOUD_DIRECTORY_FULL_ACCESS")
    def AMAZON_CLOUD_DIRECTORY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CLOUD_DIRECTORY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CLOUD_DIRECTORY_READ_ONLY_ACCESS")
    def AMAZON_CLOUD_DIRECTORY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CLOUD_DIRECTORY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CLOUD_WATCH_EVIDENTLY_FULL_ACCESS")
    def AMAZON_CLOUD_WATCH_EVIDENTLY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CLOUD_WATCH_EVIDENTLY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CLOUD_WATCH_EVIDENTLY_READ_ONLY_ACCESS")
    def AMAZON_CLOUD_WATCH_EVIDENTLY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CLOUD_WATCH_EVIDENTLY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CLOUD_WATCH_RUM_FULL_ACCESS")
    def AMAZON_CLOUD_WATCH_RUM_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CLOUD_WATCH_RUM_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CLOUD_WATCH_RUM_READ_ONLY_ACCESS")
    def AMAZON_CLOUD_WATCH_RUM_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CLOUD_WATCH_RUM_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CODE_CATALYST_FULL_ACCESS")
    def AMAZON_CODE_CATALYST_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CODE_CATALYST_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CODE_CATALYST_READ_ONLY_ACCESS")
    def AMAZON_CODE_CATALYST_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CODE_CATALYST_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CODE_GURU_PROFILER_AGENT_ACCESS")
    def AMAZON_CODE_GURU_PROFILER_AGENT_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CODE_GURU_PROFILER_AGENT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CODE_GURU_PROFILER_FULL_ACCESS")
    def AMAZON_CODE_GURU_PROFILER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CODE_GURU_PROFILER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CODE_GURU_PROFILER_READ_ONLY_ACCESS")
    def AMAZON_CODE_GURU_PROFILER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CODE_GURU_PROFILER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CODE_GURU_REVIEWER_FULL_ACCESS")
    def AMAZON_CODE_GURU_REVIEWER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CODE_GURU_REVIEWER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CODE_GURU_REVIEWER_READ_ONLY_ACCESS")
    def AMAZON_CODE_GURU_REVIEWER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CODE_GURU_REVIEWER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CODE_GURU_SECURITY_FULL_ACCESS")
    def AMAZON_CODE_GURU_SECURITY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CODE_GURU_SECURITY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CODE_GURU_SECURITY_SCAN_ACCESS")
    def AMAZON_CODE_GURU_SECURITY_SCAN_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CODE_GURU_SECURITY_SCAN_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_COGNITO_DEVELOPER_AUTHENTICATED_IDENTITIES")
    def AMAZON_COGNITO_DEVELOPER_AUTHENTICATED_IDENTITIES(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_COGNITO_DEVELOPER_AUTHENTICATED_IDENTITIES"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_COGNITO_POWER_USER")
    def AMAZON_COGNITO_POWER_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_COGNITO_POWER_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_COGNITO_READ_ONLY")
    def AMAZON_COGNITO_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_COGNITO_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_COGNITO_UN_AUTHED_IDENTITIES_SESSION_POLICY")
    def AMAZON_COGNITO_UN_AUTHED_IDENTITIES_SESSION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_COGNITO_UN_AUTHED_IDENTITIES_SESSION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_COGNITO_UNAUTHENTICATED_IDENTITIES")
    def AMAZON_COGNITO_UNAUTHENTICATED_IDENTITIES(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_COGNITO_UNAUTHENTICATED_IDENTITIES"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CONNECT_FULL_ACCESS")
    def AMAZON_CONNECT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CONNECT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CONNECT_READ_ONLY_ACCESS")
    def AMAZON_CONNECT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CONNECT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_CONNECT_VOICE_ID_FULL_ACCESS")
    def AMAZON_CONNECT_VOICE_ID_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_CONNECT_VOICE_ID_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DATA_ZONE_ENVIRONMENT_ROLE_PERMISSIONS_BOUNDARY")
    def AMAZON_DATA_ZONE_ENVIRONMENT_ROLE_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DATA_ZONE_ENVIRONMENT_ROLE_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DATA_ZONE_FULL_ACCESS")
    def AMAZON_DATA_ZONE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DATA_ZONE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DATA_ZONE_FULL_USER_ACCESS")
    def AMAZON_DATA_ZONE_FULL_USER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DATA_ZONE_FULL_USER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DATA_ZONE_REDSHIFT_GLUE_PROVISIONING_POLICY")
    def AMAZON_DATA_ZONE_REDSHIFT_GLUE_PROVISIONING_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DATA_ZONE_REDSHIFT_GLUE_PROVISIONING_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DATA_ZONE_SAGE_MAKER_ENVIRONMENT_ROLE_PERMISSIONS_BOUNDARY")
    def AMAZON_DATA_ZONE_SAGE_MAKER_ENVIRONMENT_ROLE_PERMISSIONS_BOUNDARY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DATA_ZONE_SAGE_MAKER_ENVIRONMENT_ROLE_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DATA_ZONE_SAGE_MAKER_MANAGE_ACCESS_ROLE_POLICY")
    def AMAZON_DATA_ZONE_SAGE_MAKER_MANAGE_ACCESS_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DATA_ZONE_SAGE_MAKER_MANAGE_ACCESS_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DATA_ZONE_SAGE_MAKER_PROVISIONING_ROLE_POLICY")
    def AMAZON_DATA_ZONE_SAGE_MAKER_PROVISIONING_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DATA_ZONE_SAGE_MAKER_PROVISIONING_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DETECTIVE_FULL_ACCESS")
    def AMAZON_DETECTIVE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DETECTIVE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DETECTIVE_INVESTIGATOR_ACCESS")
    def AMAZON_DETECTIVE_INVESTIGATOR_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DETECTIVE_INVESTIGATOR_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DETECTIVE_MEMBER_ACCESS")
    def AMAZON_DETECTIVE_MEMBER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DETECTIVE_MEMBER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DETECTIVE_ORGANIZATIONS_ACCESS")
    def AMAZON_DETECTIVE_ORGANIZATIONS_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DETECTIVE_ORGANIZATIONS_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DEV_OPS_GURU_CONSOLE_FULL_ACCESS")
    def AMAZON_DEV_OPS_GURU_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DEV_OPS_GURU_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DEV_OPS_GURU_FULL_ACCESS")
    def AMAZON_DEV_OPS_GURU_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DEV_OPS_GURU_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DEV_OPS_GURU_ORGANIZATIONS_ACCESS")
    def AMAZON_DEV_OPS_GURU_ORGANIZATIONS_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DEV_OPS_GURU_ORGANIZATIONS_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DEV_OPS_GURU_READ_ONLY_ACCESS")
    def AMAZON_DEV_OPS_GURU_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DEV_OPS_GURU_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DOC_DB_CONSOLE_FULL_ACCESS")
    def AMAZON_DOC_DB_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DOC_DB_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DOC_DB_ELASTIC_FULL_ACCESS")
    def AMAZON_DOC_DB_ELASTIC_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DOC_DB_ELASTIC_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DOC_DB_ELASTIC_READ_ONLY_ACCESS")
    def AMAZON_DOC_DB_ELASTIC_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DOC_DB_ELASTIC_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DOC_DB_FULL_ACCESS")
    def AMAZON_DOC_DB_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DOC_DB_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DOC_DB_READ_ONLY_ACCESS")
    def AMAZON_DOC_DB_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DOC_DB_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DRSVPC_MANAGEMENT")
    def AMAZON_DRSVPC_MANAGEMENT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DRSVPC_MANAGEMENT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DYNAMO_DB_FULL_ACCESS")
    def AMAZON_DYNAMO_DB_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DYNAMO_DB_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DYNAMO_DB_FULL_ACCESSWITH_DATA_PIPELINE")
    def AMAZON_DYNAMO_DB_FULL_ACCESSWITH_DATA_PIPELINE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DYNAMO_DB_FULL_ACCESSWITH_DATA_PIPELINE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_DYNAMO_DB_READ_ONLY_ACCESS")
    def AMAZON_DYNAMO_DB_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_DYNAMO_DB_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EC2_CONTAINER_REGISTRY_FULL_ACCESS")
    def AMAZON_EC2_CONTAINER_REGISTRY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EC2_CONTAINER_REGISTRY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EC2_CONTAINER_REGISTRY_POWER_USER")
    def AMAZON_EC2_CONTAINER_REGISTRY_POWER_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EC2_CONTAINER_REGISTRY_POWER_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EC2_CONTAINER_REGISTRY_PULL_ONLY")
    def AMAZON_EC2_CONTAINER_REGISTRY_PULL_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EC2_CONTAINER_REGISTRY_PULL_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EC2_CONTAINER_REGISTRY_READ_ONLY")
    def AMAZON_EC2_CONTAINER_REGISTRY_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EC2_CONTAINER_REGISTRY_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EC2_FULL_ACCESS")
    def AMAZON_EC2_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EC2_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EC2_READ_ONLY_ACCESS")
    def AMAZON_EC2_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EC2_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EC2_ROLE_POLICY_FOR_LAUNCH_WIZARD")
    def AMAZON_EC2_ROLE_POLICY_FOR_LAUNCH_WIZARD(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EC2_ROLE_POLICY_FOR_LAUNCH_WIZARD"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ECS_FULL_ACCESS")
    def AMAZON_ECS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ECS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ECS_INFRASTRUCTURE_ROLE_POLICY_FOR_VPC_LATTICE")
    def AMAZON_ECS_INFRASTRUCTURE_ROLE_POLICY_FOR_VPC_LATTICE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ECS_INFRASTRUCTURE_ROLE_POLICY_FOR_VPC_LATTICE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_BLOCK_STORAGE_POLICY")
    def AMAZON_EKS_BLOCK_STORAGE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_BLOCK_STORAGE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_CLUSTER_POLICY")
    def AMAZON_EKS_CLUSTER_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_CLUSTER_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_CNI_POLICY")
    def AMAZON_EKS_CNI_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_CNI_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_COMPUTE_POLICY")
    def AMAZON_EKS_COMPUTE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_COMPUTE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_FARGATE_POD_EXECUTION_ROLE_POLICY")
    def AMAZON_EKS_FARGATE_POD_EXECUTION_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_FARGATE_POD_EXECUTION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_LOAD_BALANCING_POLICY")
    def AMAZON_EKS_LOAD_BALANCING_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_LOAD_BALANCING_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_LOCAL_OUTPOST_CLUSTER_POLICY")
    def AMAZON_EKS_LOCAL_OUTPOST_CLUSTER_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_LOCAL_OUTPOST_CLUSTER_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_NETWORKING_POLICY")
    def AMAZON_EKS_NETWORKING_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_NETWORKING_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_SERVICE_POLICY")
    def AMAZON_EKS_SERVICE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_SERVICE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_WORKER_NODE_MINIMAL_POLICY")
    def AMAZON_EKS_WORKER_NODE_MINIMAL_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_WORKER_NODE_MINIMAL_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_WORKER_NODE_POLICY")
    def AMAZON_EKS_WORKER_NODE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKS_WORKER_NODE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKSVPC_RESOURCE_CONTROLLER")
    def AMAZON_EKSVPC_RESOURCE_CONTROLLER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EKSVPC_RESOURCE_CONTROLLER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTI_CACHE_FULL_ACCESS")
    def AMAZON_ELASTI_CACHE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTI_CACHE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTI_CACHE_READ_ONLY_ACCESS")
    def AMAZON_ELASTI_CACHE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTI_CACHE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_FULL_ACCESS")
    def AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_POWER_USER")
    def AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_POWER_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_POWER_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_READ_ONLY")
    def AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_FULL_ACCESS")
    def AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_ONLY_ACCESS")
    def AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_WRITE_ACCESS")
    def AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_WRITE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_WRITE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_FILE_SYSTEM_FULL_ACCESS")
    def AMAZON_ELASTIC_FILE_SYSTEM_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_FILE_SYSTEM_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_FILE_SYSTEM_READ_ONLY_ACCESS")
    def AMAZON_ELASTIC_FILE_SYSTEM_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_FILE_SYSTEM_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_FILE_SYSTEMS_UTILS")
    def AMAZON_ELASTIC_FILE_SYSTEMS_UTILS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_FILE_SYSTEMS_UTILS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_MAP_REDUCE_FULL_ACCESS")
    def AMAZON_ELASTIC_MAP_REDUCE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_MAP_REDUCE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_MAP_REDUCE_PLACEMENT_GROUP_POLICY")
    def AMAZON_ELASTIC_MAP_REDUCE_PLACEMENT_GROUP_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_MAP_REDUCE_PLACEMENT_GROUP_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_MAP_REDUCE_READ_ONLY_ACCESS")
    def AMAZON_ELASTIC_MAP_REDUCE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_MAP_REDUCE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_TRANSCODER_FULL_ACCESS")
    def AMAZON_ELASTIC_TRANSCODER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_TRANSCODER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_TRANSCODER_JOBS_SUBMITTER")
    def AMAZON_ELASTIC_TRANSCODER_JOBS_SUBMITTER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_TRANSCODER_JOBS_SUBMITTER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ELASTIC_TRANSCODER_READ_ONLY_ACCESS")
    def AMAZON_ELASTIC_TRANSCODER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ELASTIC_TRANSCODER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EMR_FULL_ACCESS_POLICY_V2")
    def AMAZON_EMR_FULL_ACCESS_POLICY_V2(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EMR_FULL_ACCESS_POLICY_V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EMR_READ_ONLY_ACCESS_POLICY_V2")
    def AMAZON_EMR_READ_ONLY_ACCESS_POLICY_V2(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EMR_READ_ONLY_ACCESS_POLICY_V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ES_COGNITO_ACCESS")
    def AMAZON_ES_COGNITO_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ES_COGNITO_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ES_FULL_ACCESS")
    def AMAZON_ES_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ES_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ES_READ_ONLY_ACCESS")
    def AMAZON_ES_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ES_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EVENT_BRIDGE_FULL_ACCESS")
    def AMAZON_EVENT_BRIDGE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EVENT_BRIDGE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EVENT_BRIDGE_PIPES_FULL_ACCESS")
    def AMAZON_EVENT_BRIDGE_PIPES_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EVENT_BRIDGE_PIPES_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EVENT_BRIDGE_PIPES_OPERATOR_ACCESS")
    def AMAZON_EVENT_BRIDGE_PIPES_OPERATOR_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EVENT_BRIDGE_PIPES_OPERATOR_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EVENT_BRIDGE_PIPES_READ_ONLY_ACCESS")
    def AMAZON_EVENT_BRIDGE_PIPES_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EVENT_BRIDGE_PIPES_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EVENT_BRIDGE_READ_ONLY_ACCESS")
    def AMAZON_EVENT_BRIDGE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EVENT_BRIDGE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EVENT_BRIDGE_SCHEDULER_FULL_ACCESS")
    def AMAZON_EVENT_BRIDGE_SCHEDULER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EVENT_BRIDGE_SCHEDULER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EVENT_BRIDGE_SCHEDULER_READ_ONLY_ACCESS")
    def AMAZON_EVENT_BRIDGE_SCHEDULER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EVENT_BRIDGE_SCHEDULER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EVENT_BRIDGE_SCHEMAS_FULL_ACCESS")
    def AMAZON_EVENT_BRIDGE_SCHEMAS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EVENT_BRIDGE_SCHEMAS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EVENT_BRIDGE_SCHEMAS_READ_ONLY_ACCESS")
    def AMAZON_EVENT_BRIDGE_SCHEMAS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_EVENT_BRIDGE_SCHEMAS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_F_SX_CONSOLE_FULL_ACCESS")
    def AMAZON_F_SX_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_F_SX_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_F_SX_CONSOLE_READ_ONLY_ACCESS")
    def AMAZON_F_SX_CONSOLE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_F_SX_CONSOLE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_F_SX_FULL_ACCESS")
    def AMAZON_F_SX_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_F_SX_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_F_SX_READ_ONLY_ACCESS")
    def AMAZON_F_SX_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_F_SX_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_FORECAST_FULL_ACCESS")
    def AMAZON_FORECAST_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_FORECAST_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_FRAUD_DETECTOR_FULL_ACCESS_POLICY")
    def AMAZON_FRAUD_DETECTOR_FULL_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_FRAUD_DETECTOR_FULL_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_FREE_RTOS_FULL_ACCESS")
    def AMAZON_FREE_RTOS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_FREE_RTOS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_GLACIER_FULL_ACCESS")
    def AMAZON_GLACIER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_GLACIER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_GLACIER_READ_ONLY_ACCESS")
    def AMAZON_GLACIER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_GLACIER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_GUARD_DUTY_FULL_ACCESS")
    def AMAZON_GUARD_DUTY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_GUARD_DUTY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_GUARD_DUTY_READ_ONLY_ACCESS")
    def AMAZON_GUARD_DUTY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_GUARD_DUTY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_HEALTH_LAKE_FULL_ACCESS")
    def AMAZON_HEALTH_LAKE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_HEALTH_LAKE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_HEALTH_LAKE_READ_ONLY_ACCESS")
    def AMAZON_HEALTH_LAKE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_HEALTH_LAKE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_HONEYCODE_FULL_ACCESS")
    def AMAZON_HONEYCODE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_HONEYCODE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_HONEYCODE_READ_ONLY_ACCESS")
    def AMAZON_HONEYCODE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_HONEYCODE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_HONEYCODE_TEAM_ASSOCIATION_FULL_ACCESS")
    def AMAZON_HONEYCODE_TEAM_ASSOCIATION_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_HONEYCODE_TEAM_ASSOCIATION_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_HONEYCODE_TEAM_ASSOCIATION_READ_ONLY_ACCESS")
    def AMAZON_HONEYCODE_TEAM_ASSOCIATION_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_HONEYCODE_TEAM_ASSOCIATION_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_HONEYCODE_WORKBOOK_FULL_ACCESS")
    def AMAZON_HONEYCODE_WORKBOOK_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_HONEYCODE_WORKBOOK_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_HONEYCODE_WORKBOOK_READ_ONLY_ACCESS")
    def AMAZON_HONEYCODE_WORKBOOK_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_HONEYCODE_WORKBOOK_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_INSPECTOR_FULL_ACCESS")
    def AMAZON_INSPECTOR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_INSPECTOR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_INSPECTOR_READ_ONLY_ACCESS")
    def AMAZON_INSPECTOR_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_INSPECTOR_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_INSPECTOR2_FULL_ACCESS")
    def AMAZON_INSPECTOR2_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_INSPECTOR2_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_INSPECTOR2_MANAGED_CIS_POLICY")
    def AMAZON_INSPECTOR2_MANAGED_CIS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_INSPECTOR2_MANAGED_CIS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_INSPECTOR2_READ_ONLY_ACCESS")
    def AMAZON_INSPECTOR2_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_INSPECTOR2_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KENDRA_FULL_ACCESS")
    def AMAZON_KENDRA_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KENDRA_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KENDRA_READ_ONLY_ACCESS")
    def AMAZON_KENDRA_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KENDRA_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KEYSPACES_FULL_ACCESS")
    def AMAZON_KEYSPACES_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KEYSPACES_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KEYSPACES_READ_ONLY_ACCESS")
    def AMAZON_KEYSPACES_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KEYSPACES_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KEYSPACES_READ_ONLY_ACCESS_V2")
    def AMAZON_KEYSPACES_READ_ONLY_ACCESS_V2(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KEYSPACES_READ_ONLY_ACCESS_V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KINESIS_ANALYTICS_FULL_ACCESS")
    def AMAZON_KINESIS_ANALYTICS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KINESIS_ANALYTICS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KINESIS_ANALYTICS_READ_ONLY")
    def AMAZON_KINESIS_ANALYTICS_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KINESIS_ANALYTICS_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KINESIS_FIREHOSE_FULL_ACCESS")
    def AMAZON_KINESIS_FIREHOSE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KINESIS_FIREHOSE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KINESIS_FIREHOSE_READ_ONLY_ACCESS")
    def AMAZON_KINESIS_FIREHOSE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KINESIS_FIREHOSE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KINESIS_FULL_ACCESS")
    def AMAZON_KINESIS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KINESIS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KINESIS_READ_ONLY_ACCESS")
    def AMAZON_KINESIS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KINESIS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KINESIS_VIDEO_STREAMS_FULL_ACCESS")
    def AMAZON_KINESIS_VIDEO_STREAMS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KINESIS_VIDEO_STREAMS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_KINESIS_VIDEO_STREAMS_READ_ONLY_ACCESS")
    def AMAZON_KINESIS_VIDEO_STREAMS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_KINESIS_VIDEO_STREAMS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LAUNCH_WIZARD_FULL_ACCESS_V2")
    def AMAZON_LAUNCH_WIZARD_FULL_ACCESS_V2(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LAUNCH_WIZARD_FULL_ACCESS_V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LEX_FULL_ACCESS")
    def AMAZON_LEX_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LEX_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LEX_READ_ONLY")
    def AMAZON_LEX_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LEX_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LEX_RUN_BOTS_ONLY")
    def AMAZON_LEX_RUN_BOTS_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LEX_RUN_BOTS_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LOOKOUT_EQUIPMENT_FULL_ACCESS")
    def AMAZON_LOOKOUT_EQUIPMENT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LOOKOUT_EQUIPMENT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LOOKOUT_EQUIPMENT_READ_ONLY_ACCESS")
    def AMAZON_LOOKOUT_EQUIPMENT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LOOKOUT_EQUIPMENT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LOOKOUT_METRICS_FULL_ACCESS")
    def AMAZON_LOOKOUT_METRICS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LOOKOUT_METRICS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LOOKOUT_METRICS_READ_ONLY_ACCESS")
    def AMAZON_LOOKOUT_METRICS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LOOKOUT_METRICS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LOOKOUT_VISION_CONSOLE_FULL_ACCESS")
    def AMAZON_LOOKOUT_VISION_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LOOKOUT_VISION_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LOOKOUT_VISION_CONSOLE_READ_ONLY_ACCESS")
    def AMAZON_LOOKOUT_VISION_CONSOLE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LOOKOUT_VISION_CONSOLE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LOOKOUT_VISION_FULL_ACCESS")
    def AMAZON_LOOKOUT_VISION_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LOOKOUT_VISION_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LOOKOUT_VISION_READ_ONLY_ACCESS")
    def AMAZON_LOOKOUT_VISION_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_LOOKOUT_VISION_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MACHINE_LEARNING_BATCH_PREDICTIONS_ACCESS")
    def AMAZON_MACHINE_LEARNING_BATCH_PREDICTIONS_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MACHINE_LEARNING_BATCH_PREDICTIONS_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MACHINE_LEARNING_CREATE_ONLY_ACCESS")
    def AMAZON_MACHINE_LEARNING_CREATE_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MACHINE_LEARNING_CREATE_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MACHINE_LEARNING_FULL_ACCESS")
    def AMAZON_MACHINE_LEARNING_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MACHINE_LEARNING_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MACHINE_LEARNING_MANAGE_REAL_TIME_ENDPOINT_ONLY_ACCESS")
    def AMAZON_MACHINE_LEARNING_MANAGE_REAL_TIME_ENDPOINT_ONLY_ACCESS(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MACHINE_LEARNING_MANAGE_REAL_TIME_ENDPOINT_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MACHINE_LEARNING_READ_ONLY_ACCESS")
    def AMAZON_MACHINE_LEARNING_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MACHINE_LEARNING_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MACHINE_LEARNING_REAL_TIME_PREDICTION_ONLY_ACCESS")
    def AMAZON_MACHINE_LEARNING_REAL_TIME_PREDICTION_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MACHINE_LEARNING_REAL_TIME_PREDICTION_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MACIE_FULL_ACCESS")
    def AMAZON_MACIE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MACIE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MACIE_READ_ONLY_ACCESS")
    def AMAZON_MACIE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MACIE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MANAGED_BLOCKCHAIN_CONSOLE_FULL_ACCESS")
    def AMAZON_MANAGED_BLOCKCHAIN_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MANAGED_BLOCKCHAIN_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MANAGED_BLOCKCHAIN_FULL_ACCESS")
    def AMAZON_MANAGED_BLOCKCHAIN_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MANAGED_BLOCKCHAIN_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MANAGED_BLOCKCHAIN_READ_ONLY_ACCESS")
    def AMAZON_MANAGED_BLOCKCHAIN_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MANAGED_BLOCKCHAIN_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MCS_FULL_ACCESS")
    def AMAZON_MCS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MCS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MCS_READ_ONLY_ACCESS")
    def AMAZON_MCS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MCS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MECHANICAL_TURK_FULL_ACCESS")
    def AMAZON_MECHANICAL_TURK_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MECHANICAL_TURK_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MECHANICAL_TURK_READ_ONLY")
    def AMAZON_MECHANICAL_TURK_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MECHANICAL_TURK_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MEMORY_DB_FULL_ACCESS")
    def AMAZON_MEMORY_DB_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MEMORY_DB_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MEMORY_DB_READ_ONLY_ACCESS")
    def AMAZON_MEMORY_DB_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MEMORY_DB_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MOBILE_ANALYTICS_FINANCIAL_REPORT_ACCESS")
    def AMAZON_MOBILE_ANALYTICS_FINANCIAL_REPORT_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MOBILE_ANALYTICS_FINANCIAL_REPORT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MOBILE_ANALYTICS_FULL_ACCESS")
    def AMAZON_MOBILE_ANALYTICS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MOBILE_ANALYTICS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MOBILE_ANALYTICS_NON_FINANCIAL_REPORT_ACCESS")
    def AMAZON_MOBILE_ANALYTICS_NON_FINANCIAL_REPORT_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MOBILE_ANALYTICS_NON_FINANCIAL_REPORT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MOBILE_ANALYTICS_WRITE_ONLY_ACCESS")
    def AMAZON_MOBILE_ANALYTICS_WRITE_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MOBILE_ANALYTICS_WRITE_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MONITRON_FULL_ACCESS")
    def AMAZON_MONITRON_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MONITRON_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MQ_API_FULL_ACCESS")
    def AMAZON_MQ_API_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MQ_API_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MQ_API_READ_ONLY_ACCESS")
    def AMAZON_MQ_API_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MQ_API_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MQ_FULL_ACCESS")
    def AMAZON_MQ_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MQ_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MQ_READ_ONLY_ACCESS")
    def AMAZON_MQ_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MQ_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MSK_CONNECT_READ_ONLY_ACCESS")
    def AMAZON_MSK_CONNECT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MSK_CONNECT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MSK_FULL_ACCESS")
    def AMAZON_MSK_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MSK_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_MSK_READ_ONLY_ACCESS")
    def AMAZON_MSK_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_MSK_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_NIMBLE_STUDIO_LAUNCH_PROFILE_WORKER")
    def AMAZON_NIMBLE_STUDIO_LAUNCH_PROFILE_WORKER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_NIMBLE_STUDIO_LAUNCH_PROFILE_WORKER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_NIMBLE_STUDIO_STUDIO_ADMIN")
    def AMAZON_NIMBLE_STUDIO_STUDIO_ADMIN(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_NIMBLE_STUDIO_STUDIO_ADMIN"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_NIMBLE_STUDIO_STUDIO_USER")
    def AMAZON_NIMBLE_STUDIO_STUDIO_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_NIMBLE_STUDIO_STUDIO_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_OMICS_FULL_ACCESS")
    def AMAZON_OMICS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_OMICS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_OMICS_READ_ONLY_ACCESS")
    def AMAZON_OMICS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_OMICS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ONE_ENTERPRISE_FULL_ACCESS")
    def AMAZON_ONE_ENTERPRISE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ONE_ENTERPRISE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ONE_ENTERPRISE_INSTALLER_ACCESS")
    def AMAZON_ONE_ENTERPRISE_INSTALLER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ONE_ENTERPRISE_INSTALLER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ONE_ENTERPRISE_READ_ONLY_ACCESS")
    def AMAZON_ONE_ENTERPRISE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ONE_ENTERPRISE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_OPEN_SEARCH_DIRECT_QUERY_GLUE_CREATE_ACCESS")
    def AMAZON_OPEN_SEARCH_DIRECT_QUERY_GLUE_CREATE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_OPEN_SEARCH_DIRECT_QUERY_GLUE_CREATE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_OPEN_SEARCH_INGESTION_FULL_ACCESS")
    def AMAZON_OPEN_SEARCH_INGESTION_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_OPEN_SEARCH_INGESTION_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_OPEN_SEARCH_INGESTION_READ_ONLY_ACCESS")
    def AMAZON_OPEN_SEARCH_INGESTION_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_OPEN_SEARCH_INGESTION_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_OPEN_SEARCH_SERVICE_COGNITO_ACCESS")
    def AMAZON_OPEN_SEARCH_SERVICE_COGNITO_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_OPEN_SEARCH_SERVICE_COGNITO_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_OPEN_SEARCH_SERVICE_FULL_ACCESS")
    def AMAZON_OPEN_SEARCH_SERVICE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_OPEN_SEARCH_SERVICE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_OPEN_SEARCH_SERVICE_READ_ONLY_ACCESS")
    def AMAZON_OPEN_SEARCH_SERVICE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_OPEN_SEARCH_SERVICE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_POLLY_FULL_ACCESS")
    def AMAZON_POLLY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_POLLY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_POLLY_READ_ONLY_ACCESS")
    def AMAZON_POLLY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_POLLY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_PROMETHEUS_CONSOLE_FULL_ACCESS")
    def AMAZON_PROMETHEUS_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_PROMETHEUS_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_PROMETHEUS_FULL_ACCESS")
    def AMAZON_PROMETHEUS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_PROMETHEUS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_PROMETHEUS_QUERY_ACCESS")
    def AMAZON_PROMETHEUS_QUERY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_PROMETHEUS_QUERY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_PROMETHEUS_REMOTE_WRITE_ACCESS")
    def AMAZON_PROMETHEUS_REMOTE_WRITE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_PROMETHEUS_REMOTE_WRITE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_Q_DEVELOPER_ACCESS")
    def AMAZON_Q_DEVELOPER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_Q_DEVELOPER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_Q_FULL_ACCESS")
    def AMAZON_Q_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_Q_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_QLDB_CONSOLE_FULL_ACCESS")
    def AMAZON_QLDB_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_QLDB_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_QLDB_FULL_ACCESS")
    def AMAZON_QLDB_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_QLDB_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_QLDB_READ_ONLY")
    def AMAZON_QLDB_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_QLDB_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_RDS_CUSTOM_INSTANCE_PROFILE_ROLE_POLICY")
    def AMAZON_RDS_CUSTOM_INSTANCE_PROFILE_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_RDS_CUSTOM_INSTANCE_PROFILE_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_RDS_DATA_FULL_ACCESS")
    def AMAZON_RDS_DATA_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_RDS_DATA_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_RDS_FULL_ACCESS")
    def AMAZON_RDS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_RDS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_RDS_PERFORMANCE_INSIGHTS_FULL_ACCESS")
    def AMAZON_RDS_PERFORMANCE_INSIGHTS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_RDS_PERFORMANCE_INSIGHTS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_RDS_PERFORMANCE_INSIGHTS_READ_ONLY")
    def AMAZON_RDS_PERFORMANCE_INSIGHTS_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_RDS_PERFORMANCE_INSIGHTS_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_RDS_READ_ONLY_ACCESS")
    def AMAZON_RDS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_RDS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REDSHIFT_ALL_COMMANDS_FULL_ACCESS")
    def AMAZON_REDSHIFT_ALL_COMMANDS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REDSHIFT_ALL_COMMANDS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REDSHIFT_DATA_FULL_ACCESS")
    def AMAZON_REDSHIFT_DATA_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REDSHIFT_DATA_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REDSHIFT_FULL_ACCESS")
    def AMAZON_REDSHIFT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REDSHIFT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REDSHIFT_QUERY_EDITOR")
    def AMAZON_REDSHIFT_QUERY_EDITOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REDSHIFT_QUERY_EDITOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REDSHIFT_QUERY_EDITOR_V2_FULL_ACCESS")
    def AMAZON_REDSHIFT_QUERY_EDITOR_V2_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REDSHIFT_QUERY_EDITOR_V2_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REDSHIFT_QUERY_EDITOR_V2_NO_SHARING")
    def AMAZON_REDSHIFT_QUERY_EDITOR_V2_NO_SHARING(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REDSHIFT_QUERY_EDITOR_V2_NO_SHARING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_SHARING")
    def AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_SHARING(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_SHARING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_WRITE_SHARING")
    def AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_WRITE_SHARING(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_WRITE_SHARING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REDSHIFT_READ_ONLY_ACCESS")
    def AMAZON_REDSHIFT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REDSHIFT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REKOGNITION_CUSTOM_LABELS_FULL_ACCESS")
    def AMAZON_REKOGNITION_CUSTOM_LABELS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REKOGNITION_CUSTOM_LABELS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REKOGNITION_FULL_ACCESS")
    def AMAZON_REKOGNITION_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REKOGNITION_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_REKOGNITION_READ_ONLY_ACCESS")
    def AMAZON_REKOGNITION_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_REKOGNITION_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_AUTO_NAMING_FULL_ACCESS")
    def AMAZON_ROUTE53_AUTO_NAMING_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_AUTO_NAMING_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_AUTO_NAMING_READ_ONLY_ACCESS")
    def AMAZON_ROUTE53_AUTO_NAMING_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_AUTO_NAMING_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_AUTO_NAMING_REGISTRANT_ACCESS")
    def AMAZON_ROUTE53_AUTO_NAMING_REGISTRANT_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_AUTO_NAMING_REGISTRANT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_DOMAINS_FULL_ACCESS")
    def AMAZON_ROUTE53_DOMAINS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_DOMAINS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_DOMAINS_READ_ONLY_ACCESS")
    def AMAZON_ROUTE53_DOMAINS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_DOMAINS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_FULL_ACCESS")
    def AMAZON_ROUTE53_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_PROFILES_FULL_ACCESS")
    def AMAZON_ROUTE53_PROFILES_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_PROFILES_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_PROFILES_READ_ONLY_ACCESS")
    def AMAZON_ROUTE53_PROFILES_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_PROFILES_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_READ_ONLY_ACCESS")
    def AMAZON_ROUTE53_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_RECOVERY_CLUSTER_FULL_ACCESS")
    def AMAZON_ROUTE53_RECOVERY_CLUSTER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_RECOVERY_CLUSTER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_RECOVERY_CLUSTER_READ_ONLY_ACCESS")
    def AMAZON_ROUTE53_RECOVERY_CLUSTER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_RECOVERY_CLUSTER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_FULL_ACCESS")
    def AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_READ_ONLY_ACCESS")
    def AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_RECOVERY_READINESS_FULL_ACCESS")
    def AMAZON_ROUTE53_RECOVERY_READINESS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_RECOVERY_READINESS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_RECOVERY_READINESS_READ_ONLY_ACCESS")
    def AMAZON_ROUTE53_RECOVERY_READINESS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_RECOVERY_READINESS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_RESOLVER_FULL_ACCESS")
    def AMAZON_ROUTE53_RESOLVER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_RESOLVER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ROUTE53_RESOLVER_READ_ONLY_ACCESS")
    def AMAZON_ROUTE53_RESOLVER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ROUTE53_RESOLVER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_S3_FULL_ACCESS")
    def AMAZON_S3_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_S3_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_S3_OUTPOSTS_FULL_ACCESS")
    def AMAZON_S3_OUTPOSTS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_S3_OUTPOSTS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_S3_OUTPOSTS_READ_ONLY_ACCESS")
    def AMAZON_S3_OUTPOSTS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_S3_OUTPOSTS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_S3_READ_ONLY_ACCESS")
    def AMAZON_S3_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_S3_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_S3_TABLES_FULL_ACCESS")
    def AMAZON_S3_TABLES_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_S3_TABLES_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_S3_TABLES_READ_ONLY_ACCESS")
    def AMAZON_S3_TABLES_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_S3_TABLES_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_ADMIN_SERVICE_CATALOG_PRODUCTS_SERVICE_ROLE_POLICY")
    def AMAZON_SAGE_MAKER_ADMIN_SERVICE_CATALOG_PRODUCTS_SERVICE_ROLE_POLICY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_ADMIN_SERVICE_CATALOG_PRODUCTS_SERVICE_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_CANVAS_AI_SERVICES_ACCESS")
    def AMAZON_SAGE_MAKER_CANVAS_AI_SERVICES_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_CANVAS_AI_SERVICES_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_CANVAS_BEDROCK_ACCESS")
    def AMAZON_SAGE_MAKER_CANVAS_BEDROCK_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_CANVAS_BEDROCK_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_CANVAS_DATA_PREP_FULL_ACCESS")
    def AMAZON_SAGE_MAKER_CANVAS_DATA_PREP_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_CANVAS_DATA_PREP_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_CANVAS_EMR_SERVERLESS_EXECUTION_ROLE_POLICY")
    def AMAZON_SAGE_MAKER_CANVAS_EMR_SERVERLESS_EXECUTION_ROLE_POLICY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_CANVAS_EMR_SERVERLESS_EXECUTION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_CANVAS_FULL_ACCESS")
    def AMAZON_SAGE_MAKER_CANVAS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_CANVAS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_CANVAS_SM_DATA_SCIENCE_ASSISTANT_ACCESS")
    def AMAZON_SAGE_MAKER_CANVAS_SM_DATA_SCIENCE_ASSISTANT_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_CANVAS_SM_DATA_SCIENCE_ASSISTANT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_CLUSTER_INSTANCE_ROLE_POLICY")
    def AMAZON_SAGE_MAKER_CLUSTER_INSTANCE_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_CLUSTER_INSTANCE_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_FEATURE_STORE_ACCESS")
    def AMAZON_SAGE_MAKER_FEATURE_STORE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_FEATURE_STORE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_FULL_ACCESS")
    def AMAZON_SAGE_MAKER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_GROUND_TRUTH_EXECUTION")
    def AMAZON_SAGE_MAKER_GROUND_TRUTH_EXECUTION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_GROUND_TRUTH_EXECUTION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_MECHANICAL_TURK_ACCESS")
    def AMAZON_SAGE_MAKER_MECHANICAL_TURK_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_MECHANICAL_TURK_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_MODEL_GOVERNANCE_USE_ACCESS")
    def AMAZON_SAGE_MAKER_MODEL_GOVERNANCE_USE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_MODEL_GOVERNANCE_USE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_MODEL_REGISTRY_FULL_ACCESS")
    def AMAZON_SAGE_MAKER_MODEL_REGISTRY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_MODEL_REGISTRY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_PARTNER_APPS_FULL_ACCESS")
    def AMAZON_SAGE_MAKER_PARTNER_APPS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_PARTNER_APPS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_PIPELINES_INTEGRATIONS")
    def AMAZON_SAGE_MAKER_PIPELINES_INTEGRATIONS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_PIPELINES_INTEGRATIONS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_READ_ONLY")
    def AMAZON_SAGE_MAKER_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_SERVICE_CATALOG_PRODUCTS_CODE_BUILD_SERVICE_ROLE_POLICY")
    def AMAZON_SAGE_MAKER_SERVICE_CATALOG_PRODUCTS_CODE_BUILD_SERVICE_ROLE_POLICY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_SERVICE_CATALOG_PRODUCTS_CODE_BUILD_SERVICE_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SAGE_MAKER_TRAINING_PLAN_CREATE_ACCESS")
    def AMAZON_SAGE_MAKER_TRAINING_PLAN_CREATE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SAGE_MAKER_TRAINING_PLAN_CREATE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SECURITY_LAKE_ADMINISTRATOR")
    def AMAZON_SECURITY_LAKE_ADMINISTRATOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SECURITY_LAKE_ADMINISTRATOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SECURITY_LAKE_PERMISSIONS_BOUNDARY")
    def AMAZON_SECURITY_LAKE_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SECURITY_LAKE_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SES_FULL_ACCESS")
    def AMAZON_SES_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SES_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SES_READ_ONLY_ACCESS")
    def AMAZON_SES_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SES_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SNS_FULL_ACCESS")
    def AMAZON_SNS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SNS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SNS_READ_ONLY_ACCESS")
    def AMAZON_SNS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SNS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SQS_FULL_ACCESS")
    def AMAZON_SQS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SQS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SQS_READ_ONLY_ACCESS")
    def AMAZON_SQS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SQS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SSM_AUTOMATION_APPROVER_ACCESS")
    def AMAZON_SSM_AUTOMATION_APPROVER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SSM_AUTOMATION_APPROVER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SSM_DIRECTORY_SERVICE_ACCESS")
    def AMAZON_SSM_DIRECTORY_SERVICE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SSM_DIRECTORY_SERVICE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SSM_FULL_ACCESS")
    def AMAZON_SSM_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SSM_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SSM_MANAGED_EC2_INSTANCE_DEFAULT_POLICY")
    def AMAZON_SSM_MANAGED_EC2_INSTANCE_DEFAULT_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SSM_MANAGED_EC2_INSTANCE_DEFAULT_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SSM_MANAGED_INSTANCE_CORE")
    def AMAZON_SSM_MANAGED_INSTANCE_CORE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SSM_MANAGED_INSTANCE_CORE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SSM_PATCH_ASSOCIATION")
    def AMAZON_SSM_PATCH_ASSOCIATION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SSM_PATCH_ASSOCIATION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_SSM_READ_ONLY_ACCESS")
    def AMAZON_SSM_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_SSM_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TEXTRACT_FULL_ACCESS")
    def AMAZON_TEXTRACT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_TEXTRACT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TIMESTREAM_CONSOLE_FULL_ACCESS")
    def AMAZON_TIMESTREAM_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_TIMESTREAM_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TIMESTREAM_FULL_ACCESS")
    def AMAZON_TIMESTREAM_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_TIMESTREAM_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TIMESTREAM_INFLUX_DB_FULL_ACCESS")
    def AMAZON_TIMESTREAM_INFLUX_DB_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_TIMESTREAM_INFLUX_DB_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TIMESTREAM_READ_ONLY_ACCESS")
    def AMAZON_TIMESTREAM_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_TIMESTREAM_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TRANSCRIBE_FULL_ACCESS")
    def AMAZON_TRANSCRIBE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_TRANSCRIBE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TRANSCRIBE_READ_ONLY_ACCESS")
    def AMAZON_TRANSCRIBE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_TRANSCRIBE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_VERIFIED_PERMISSIONS_FULL_ACCESS")
    def AMAZON_VERIFIED_PERMISSIONS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_VERIFIED_PERMISSIONS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_VERIFIED_PERMISSIONS_READ_ONLY_ACCESS")
    def AMAZON_VERIFIED_PERMISSIONS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_VERIFIED_PERMISSIONS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_VPC_CROSS_ACCOUNT_NETWORK_INTERFACE_OPERATIONS")
    def AMAZON_VPC_CROSS_ACCOUNT_NETWORK_INTERFACE_OPERATIONS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_VPC_CROSS_ACCOUNT_NETWORK_INTERFACE_OPERATIONS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_VPC_FULL_ACCESS")
    def AMAZON_VPC_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_VPC_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_VPC_NETWORK_ACCESS_ANALYZER_FULL_ACCESS_POLICY")
    def AMAZON_VPC_NETWORK_ACCESS_ANALYZER_FULL_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_VPC_NETWORK_ACCESS_ANALYZER_FULL_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_VPC_REACHABILITY_ANALYZER_FULL_ACCESS_POLICY")
    def AMAZON_VPC_REACHABILITY_ANALYZER_FULL_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_VPC_REACHABILITY_ANALYZER_FULL_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_VPC_REACHABILITY_ANALYZER_PATH_COMPONENT_READ_POLICY")
    def AMAZON_VPC_REACHABILITY_ANALYZER_PATH_COMPONENT_READ_POLICY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_VPC_REACHABILITY_ANALYZER_PATH_COMPONENT_READ_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_VPC_READ_ONLY_ACCESS")
    def AMAZON_VPC_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_VPC_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_DOCS_FULL_ACCESS")
    def AMAZON_WORK_DOCS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_DOCS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_DOCS_READ_ONLY_ACCESS")
    def AMAZON_WORK_DOCS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_DOCS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_MAIL_FULL_ACCESS")
    def AMAZON_WORK_MAIL_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_MAIL_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_MAIL_MESSAGE_FLOW_FULL_ACCESS")
    def AMAZON_WORK_MAIL_MESSAGE_FLOW_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_MAIL_MESSAGE_FLOW_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_MAIL_MESSAGE_FLOW_READ_ONLY_ACCESS")
    def AMAZON_WORK_MAIL_MESSAGE_FLOW_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_MAIL_MESSAGE_FLOW_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_MAIL_READ_ONLY_ACCESS")
    def AMAZON_WORK_MAIL_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_MAIL_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_SPACES_ADMIN")
    def AMAZON_WORK_SPACES_ADMIN(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_SPACES_ADMIN"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_SPACES_APPLICATION_MANAGER_ADMIN_ACCESS")
    def AMAZON_WORK_SPACES_APPLICATION_MANAGER_ADMIN_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_SPACES_APPLICATION_MANAGER_ADMIN_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_SPACES_POOL_SERVICE_ACCESS")
    def AMAZON_WORK_SPACES_POOL_SERVICE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_SPACES_POOL_SERVICE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_SPACES_SECURE_BROWSER_READ_ONLY")
    def AMAZON_WORK_SPACES_SECURE_BROWSER_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_SPACES_SECURE_BROWSER_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_SPACES_SELF_SERVICE_ACCESS")
    def AMAZON_WORK_SPACES_SELF_SERVICE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_SPACES_SELF_SERVICE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_SPACES_SERVICE_ACCESS")
    def AMAZON_WORK_SPACES_SERVICE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_SPACES_SERVICE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_SPACES_THIN_CLIENT_FULL_ACCESS")
    def AMAZON_WORK_SPACES_THIN_CLIENT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_SPACES_THIN_CLIENT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_SPACES_THIN_CLIENT_READ_ONLY_ACCESS")
    def AMAZON_WORK_SPACES_THIN_CLIENT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_SPACES_THIN_CLIENT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORK_SPACES_WEB_READ_ONLY")
    def AMAZON_WORK_SPACES_WEB_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORK_SPACES_WEB_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_WORKSPACES_PCA_ACCESS")
    def AMAZON_WORKSPACES_PCA_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_WORKSPACES_PCA_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ZOCALO_FULL_ACCESS")
    def AMAZON_ZOCALO_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ZOCALO_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_ZOCALO_READ_ONLY_ACCESS")
    def AMAZON_ZOCALO_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AMAZON_ZOCALO_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AUTO_SCALING_CONSOLE_FULL_ACCESS")
    def AUTO_SCALING_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AUTO_SCALING_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AUTO_SCALING_CONSOLE_READ_ONLY_ACCESS")
    def AUTO_SCALING_CONSOLE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AUTO_SCALING_CONSOLE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AUTO_SCALING_FULL_ACCESS")
    def AUTO_SCALING_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AUTO_SCALING_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AUTO_SCALING_READ_ONLY_ACCESS")
    def AUTO_SCALING_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AUTO_SCALING_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ACCOUNT_ACTIVITY_ACCESS")
    def AWS_ACCOUNT_ACTIVITY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ACCOUNT_ACTIVITY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ACCOUNT_MANAGEMENT_FULL_ACCESS")
    def AWS_ACCOUNT_MANAGEMENT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ACCOUNT_MANAGEMENT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ACCOUNT_MANAGEMENT_READ_ONLY_ACCESS")
    def AWS_ACCOUNT_MANAGEMENT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ACCOUNT_MANAGEMENT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ACCOUNT_USAGE_REPORT_ACCESS")
    def AWS_ACCOUNT_USAGE_REPORT_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ACCOUNT_USAGE_REPORT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_AGENTLESS_DISCOVERY_SERVICE")
    def AWS_AGENTLESS_DISCOVERY_SERVICE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_AGENTLESS_DISCOVERY_SERVICE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_FABRIC_FULL_ACCESS")
    def AWS_APP_FABRIC_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_FABRIC_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_FABRIC_READ_ONLY_ACCESS")
    def AWS_APP_FABRIC_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_FABRIC_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_MESH_ENVOY_ACCESS")
    def AWS_APP_MESH_ENVOY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_MESH_ENVOY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_MESH_FULL_ACCESS")
    def AWS_APP_MESH_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_MESH_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_MESH_PREVIEW_ENVOY_ACCESS")
    def AWS_APP_MESH_PREVIEW_ENVOY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_MESH_PREVIEW_ENVOY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_MESH_READ_ONLY")
    def AWS_APP_MESH_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_MESH_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_RUNNER_FULL_ACCESS")
    def AWS_APP_RUNNER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_RUNNER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_RUNNER_READ_ONLY_ACCESS")
    def AWS_APP_RUNNER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_RUNNER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_SYNC_ADMINISTRATOR")
    def AWS_APP_SYNC_ADMINISTRATOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_SYNC_ADMINISTRATOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_SYNC_INVOKE_FULL_ACCESS")
    def AWS_APP_SYNC_INVOKE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_SYNC_INVOKE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APP_SYNC_SCHEMA_AUTHOR")
    def AWS_APP_SYNC_SCHEMA_AUTHOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APP_SYNC_SCHEMA_AUTHOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_DISCOVERY_AGENT_ACCESS")
    def AWS_APPLICATION_DISCOVERY_AGENT_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_DISCOVERY_AGENT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_DISCOVERY_AGENTLESS_COLLECTOR_ACCESS")
    def AWS_APPLICATION_DISCOVERY_AGENTLESS_COLLECTOR_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_DISCOVERY_AGENTLESS_COLLECTOR_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_DISCOVERY_SERVICE_FULL_ACCESS")
    def AWS_APPLICATION_DISCOVERY_SERVICE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_DISCOVERY_SERVICE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_MIGRATION_AGENT_INSTALLATION_POLICY")
    def AWS_APPLICATION_MIGRATION_AGENT_INSTALLATION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_MIGRATION_AGENT_INSTALLATION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_MIGRATION_AGENT_POLICY")
    def AWS_APPLICATION_MIGRATION_AGENT_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_MIGRATION_AGENT_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_MIGRATION_EC2_ACCESS")
    def AWS_APPLICATION_MIGRATION_EC2_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_MIGRATION_EC2_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_MIGRATION_FULL_ACCESS")
    def AWS_APPLICATION_MIGRATION_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_MIGRATION_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_MIGRATION_READ_ONLY_ACCESS")
    def AWS_APPLICATION_MIGRATION_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_MIGRATION_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_MIGRATION_SERVICE_EC2_INSTANCE_POLICY")
    def AWS_APPLICATION_MIGRATION_SERVICE_EC2_INSTANCE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_MIGRATION_SERVICE_EC2_INSTANCE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_MIGRATION_SSM_ACCESS")
    def AWS_APPLICATION_MIGRATION_SSM_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_MIGRATION_SSM_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_APPLICATION_MIGRATION_V_CENTER_CLIENT_POLICY")
    def AWS_APPLICATION_MIGRATION_V_CENTER_CLIENT_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_APPLICATION_MIGRATION_V_CENTER_CLIENT_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ARTIFACT_AGREEMENTS_FULL_ACCESS")
    def AWS_ARTIFACT_AGREEMENTS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ARTIFACT_AGREEMENTS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ARTIFACT_AGREEMENTS_READ_ONLY_ACCESS")
    def AWS_ARTIFACT_AGREEMENTS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ARTIFACT_AGREEMENTS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ARTIFACT_REPORTS_READ_ONLY_ACCESS")
    def AWS_ARTIFACT_REPORTS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ARTIFACT_REPORTS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_AUDIT_MANAGER_ADMINISTRATOR_ACCESS")
    def AWS_AUDIT_MANAGER_ADMINISTRATOR_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_AUDIT_MANAGER_ADMINISTRATOR_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_AUDIT_ACCESS")
    def AWS_BACKUP_AUDIT_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_AUDIT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_DATA_TRANSFER_ACCESS")
    def AWS_BACKUP_DATA_TRANSFER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_DATA_TRANSFER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_FULL_ACCESS")
    def AWS_BACKUP_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_OPERATOR_ACCESS")
    def AWS_BACKUP_OPERATOR_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_OPERATOR_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_ORGANIZATION_ADMIN_ACCESS")
    def AWS_BACKUP_ORGANIZATION_ADMIN_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_ORGANIZATION_ADMIN_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_RESTORE_ACCESS_FOR_SAPHANA")
    def AWS_BACKUP_RESTORE_ACCESS_FOR_SAPHANA(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_RESTORE_ACCESS_FOR_SAPHANA"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_INDEXING")
    def AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_INDEXING(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_INDEXING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_ITEM_RESTORES")
    def AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_ITEM_RESTORES(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_ITEM_RESTORES"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_S3_BACKUP")
    def AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_S3_BACKUP(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_S3_BACKUP"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_S3_RESTORE")
    def AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_S3_RESTORE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BACKUP_SERVICE_ROLE_POLICY_FOR_S3_RESTORE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BATCH_FULL_ACCESS")
    def AWS_BATCH_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BATCH_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BILLING_CONDUCTOR_FULL_ACCESS")
    def AWS_BILLING_CONDUCTOR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BILLING_CONDUCTOR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BILLING_CONDUCTOR_READ_ONLY_ACCESS")
    def AWS_BILLING_CONDUCTOR_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BILLING_CONDUCTOR_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BILLING_READ_ONLY_ACCESS")
    def AWS_BILLING_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BILLING_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BUDGETS_ACTIONS_ROLE_POLICY_FOR_RESOURCE_ADMINISTRATION_WITH_SSM")
    def AWS_BUDGETS_ACTIONS_ROLE_POLICY_FOR_RESOURCE_ADMINISTRATION_WITH_SSM(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BUDGETS_ACTIONS_ROLE_POLICY_FOR_RESOURCE_ADMINISTRATION_WITH_SSM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BUDGETS_ACTIONS_WITH_AWS_RESOURCE_CONTROL_ACCESS")
    def AWS_BUDGETS_ACTIONS_WITH_AWS_RESOURCE_CONTROL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BUDGETS_ACTIONS_WITH_AWS_RESOURCE_CONTROL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BUDGETS_READ_ONLY_ACCESS")
    def AWS_BUDGETS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BUDGETS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BUG_BUST_FULL_ACCESS")
    def AWS_BUG_BUST_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BUG_BUST_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_BUG_BUST_PLAYER_ACCESS")
    def AWS_BUG_BUST_PLAYER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_BUG_BUST_PLAYER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CERTIFICATE_MANAGER_FULL_ACCESS")
    def AWS_CERTIFICATE_MANAGER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CERTIFICATE_MANAGER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CERTIFICATE_MANAGER_PRIVATE_CA_AUDITOR")
    def AWS_CERTIFICATE_MANAGER_PRIVATE_CA_AUDITOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CERTIFICATE_MANAGER_PRIVATE_CA_AUDITOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CERTIFICATE_MANAGER_PRIVATE_CA_FULL_ACCESS")
    def AWS_CERTIFICATE_MANAGER_PRIVATE_CA_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CERTIFICATE_MANAGER_PRIVATE_CA_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CERTIFICATE_MANAGER_PRIVATE_CA_PRIVILEGED_USER")
    def AWS_CERTIFICATE_MANAGER_PRIVATE_CA_PRIVILEGED_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CERTIFICATE_MANAGER_PRIVATE_CA_PRIVILEGED_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CERTIFICATE_MANAGER_PRIVATE_CA_READ_ONLY")
    def AWS_CERTIFICATE_MANAGER_PRIVATE_CA_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CERTIFICATE_MANAGER_PRIVATE_CA_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CERTIFICATE_MANAGER_PRIVATE_CA_USER")
    def AWS_CERTIFICATE_MANAGER_PRIVATE_CA_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CERTIFICATE_MANAGER_PRIVATE_CA_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CERTIFICATE_MANAGER_READ_ONLY")
    def AWS_CERTIFICATE_MANAGER_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CERTIFICATE_MANAGER_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLEAN_ROOMS_FULL_ACCESS")
    def AWS_CLEAN_ROOMS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLEAN_ROOMS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLEAN_ROOMS_FULL_ACCESS_NO_QUERYING")
    def AWS_CLEAN_ROOMS_FULL_ACCESS_NO_QUERYING(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLEAN_ROOMS_FULL_ACCESS_NO_QUERYING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLEAN_ROOMS_ML_FULL_ACCESS")
    def AWS_CLEAN_ROOMS_ML_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLEAN_ROOMS_ML_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLEAN_ROOMS_ML_READ_ONLY_ACCESS")
    def AWS_CLEAN_ROOMS_ML_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLEAN_ROOMS_ML_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLEAN_ROOMS_READ_ONLY_ACCESS")
    def AWS_CLEAN_ROOMS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLEAN_ROOMS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_FORMATION_FULL_ACCESS")
    def AWS_CLOUD_FORMATION_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_FORMATION_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_FORMATION_READ_ONLY_ACCESS")
    def AWS_CLOUD_FORMATION_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_FORMATION_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_HSM_FULL_ACCESS")
    def AWS_CLOUD_HSM_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_HSM_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_HSM_READ_ONLY_ACCESS")
    def AWS_CLOUD_HSM_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_HSM_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_MAP_DISCOVER_INSTANCE_ACCESS")
    def AWS_CLOUD_MAP_DISCOVER_INSTANCE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_MAP_DISCOVER_INSTANCE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_MAP_FULL_ACCESS")
    def AWS_CLOUD_MAP_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_MAP_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_MAP_READ_ONLY_ACCESS")
    def AWS_CLOUD_MAP_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_MAP_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_MAP_REGISTER_INSTANCE_ACCESS")
    def AWS_CLOUD_MAP_REGISTER_INSTANCE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_MAP_REGISTER_INSTANCE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_SHELL_FULL_ACCESS")
    def AWS_CLOUD_SHELL_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_SHELL_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_TRAIL_FULL_ACCESS")
    def AWS_CLOUD_TRAIL_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_TRAIL_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD_TRAIL_READ_ONLY_ACCESS")
    def AWS_CLOUD_TRAIL_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD_TRAIL_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD9_ADMINISTRATOR")
    def AWS_CLOUD9_ADMINISTRATOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD9_ADMINISTRATOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD9_ENVIRONMENT_MEMBER")
    def AWS_CLOUD9_ENVIRONMENT_MEMBER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD9_ENVIRONMENT_MEMBER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD9_SSM_INSTANCE_PROFILE")
    def AWS_CLOUD9_SSM_INSTANCE_PROFILE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD9_SSM_INSTANCE_PROFILE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CLOUD9_USER")
    def AWS_CLOUD9_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CLOUD9_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_ARTIFACT_ADMIN_ACCESS")
    def AWS_CODE_ARTIFACT_ADMIN_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_ARTIFACT_ADMIN_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_ARTIFACT_READ_ONLY_ACCESS")
    def AWS_CODE_ARTIFACT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_ARTIFACT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_BUILD_ADMIN_ACCESS")
    def AWS_CODE_BUILD_ADMIN_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_BUILD_ADMIN_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_BUILD_DEVELOPER_ACCESS")
    def AWS_CODE_BUILD_DEVELOPER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_BUILD_DEVELOPER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_BUILD_READ_ONLY_ACCESS")
    def AWS_CODE_BUILD_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_BUILD_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_COMMIT_FULL_ACCESS")
    def AWS_CODE_COMMIT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_COMMIT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_COMMIT_POWER_USER")
    def AWS_CODE_COMMIT_POWER_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_COMMIT_POWER_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_COMMIT_READ_ONLY")
    def AWS_CODE_COMMIT_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_COMMIT_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_DEPLOY_DEPLOYER_ACCESS")
    def AWS_CODE_DEPLOY_DEPLOYER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_DEPLOY_DEPLOYER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_DEPLOY_FULL_ACCESS")
    def AWS_CODE_DEPLOY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_DEPLOY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_DEPLOY_READ_ONLY_ACCESS")
    def AWS_CODE_DEPLOY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_DEPLOY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_DEPLOY_ROLE_FOR_ECS")
    def AWS_CODE_DEPLOY_ROLE_FOR_ECS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_DEPLOY_ROLE_FOR_ECS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_DEPLOY_ROLE_FOR_ECS_LIMITED")
    def AWS_CODE_DEPLOY_ROLE_FOR_ECS_LIMITED(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_DEPLOY_ROLE_FOR_ECS_LIMITED"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_PIPELINE_APPROVER_ACCESS")
    def AWS_CODE_PIPELINE_APPROVER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_PIPELINE_APPROVER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_PIPELINE_CUSTOM_ACTION_ACCESS")
    def AWS_CODE_PIPELINE_CUSTOM_ACTION_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_PIPELINE_CUSTOM_ACTION_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_PIPELINE_FULL_ACCESS")
    def AWS_CODE_PIPELINE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_PIPELINE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_PIPELINE_READ_ONLY_ACCESS")
    def AWS_CODE_PIPELINE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_PIPELINE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CODE_STAR_FULL_ACCESS")
    def AWS_CODE_STAR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CODE_STAR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_COMPROMISED_KEY_QUARANTINE")
    def AWS_COMPROMISED_KEY_QUARANTINE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_COMPROMISED_KEY_QUARANTINE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_COMPROMISED_KEY_QUARANTINE_V2")
    def AWS_COMPROMISED_KEY_QUARANTINE_V2(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_COMPROMISED_KEY_QUARANTINE_V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_COMPROMISED_KEY_QUARANTINE_V3")
    def AWS_COMPROMISED_KEY_QUARANTINE_V3(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_COMPROMISED_KEY_QUARANTINE_V3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CONFIG_USER_ACCESS")
    def AWS_CONFIG_USER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CONFIG_USER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_CONNECTOR")
    def AWS_CONNECTOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_CONNECTOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_EXCHANGE_DATA_GRANT_OWNER_FULL_ACCESS")
    def AWS_DATA_EXCHANGE_DATA_GRANT_OWNER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_EXCHANGE_DATA_GRANT_OWNER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_EXCHANGE_DATA_GRANT_RECEIVER_FULL_ACCESS")
    def AWS_DATA_EXCHANGE_DATA_GRANT_RECEIVER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_EXCHANGE_DATA_GRANT_RECEIVER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_EXCHANGE_FULL_ACCESS")
    def AWS_DATA_EXCHANGE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_EXCHANGE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_EXCHANGE_PROVIDER_FULL_ACCESS")
    def AWS_DATA_EXCHANGE_PROVIDER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_EXCHANGE_PROVIDER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_EXCHANGE_READ_ONLY")
    def AWS_DATA_EXCHANGE_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_EXCHANGE_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_EXCHANGE_SUBSCRIBER_FULL_ACCESS")
    def AWS_DATA_EXCHANGE_SUBSCRIBER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_EXCHANGE_SUBSCRIBER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_PIPELINE_FULL_ACCESS")
    def AWS_DATA_PIPELINE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_PIPELINE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_PIPELINE_POWER_USER")
    def AWS_DATA_PIPELINE_POWER_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_PIPELINE_POWER_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_SYNC_FULL_ACCESS")
    def AWS_DATA_SYNC_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_SYNC_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DATA_SYNC_READ_ONLY_ACCESS")
    def AWS_DATA_SYNC_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DATA_SYNC_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEADLINE_CLOUD_FLEET_WORKER")
    def AWS_DEADLINE_CLOUD_FLEET_WORKER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEADLINE_CLOUD_FLEET_WORKER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEADLINE_CLOUD_USER_ACCESS_FARMS")
    def AWS_DEADLINE_CLOUD_USER_ACCESS_FARMS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEADLINE_CLOUD_USER_ACCESS_FARMS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEADLINE_CLOUD_USER_ACCESS_FLEETS")
    def AWS_DEADLINE_CLOUD_USER_ACCESS_FLEETS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEADLINE_CLOUD_USER_ACCESS_FLEETS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEADLINE_CLOUD_USER_ACCESS_JOBS")
    def AWS_DEADLINE_CLOUD_USER_ACCESS_JOBS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEADLINE_CLOUD_USER_ACCESS_JOBS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEADLINE_CLOUD_USER_ACCESS_QUEUES")
    def AWS_DEADLINE_CLOUD_USER_ACCESS_QUEUES(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEADLINE_CLOUD_USER_ACCESS_QUEUES"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEADLINE_CLOUD_WORKER_HOST")
    def AWS_DEADLINE_CLOUD_WORKER_HOST(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEADLINE_CLOUD_WORKER_HOST"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEEP_LENS_LAMBDA_FUNCTION_ACCESS_POLICY")
    def AWS_DEEP_LENS_LAMBDA_FUNCTION_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEEP_LENS_LAMBDA_FUNCTION_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEEP_RACER_ACCOUNT_ADMIN_ACCESS")
    def AWS_DEEP_RACER_ACCOUNT_ADMIN_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEEP_RACER_ACCOUNT_ADMIN_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEEP_RACER_CLOUD_FORMATION_ACCESS_POLICY")
    def AWS_DEEP_RACER_CLOUD_FORMATION_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEEP_RACER_CLOUD_FORMATION_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEEP_RACER_DEFAULT_MULTI_USER_ACCESS")
    def AWS_DEEP_RACER_DEFAULT_MULTI_USER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEEP_RACER_DEFAULT_MULTI_USER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEEP_RACER_FULL_ACCESS")
    def AWS_DEEP_RACER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEEP_RACER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEEP_RACER_ROBO_MAKER_ACCESS_POLICY")
    def AWS_DEEP_RACER_ROBO_MAKER_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEEP_RACER_ROBO_MAKER_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DENY_ALL")
    def AWS_DENY_ALL(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DENY_ALL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DEVICE_FARM_FULL_ACCESS")
    def AWS_DEVICE_FARM_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DEVICE_FARM_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DIRECT_CONNECT_FULL_ACCESS")
    def AWS_DIRECT_CONNECT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DIRECT_CONNECT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DIRECT_CONNECT_READ_ONLY_ACCESS")
    def AWS_DIRECT_CONNECT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DIRECT_CONNECT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DIRECTORY_SERVICE_DATA_FULL_ACCESS")
    def AWS_DIRECTORY_SERVICE_DATA_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DIRECTORY_SERVICE_DATA_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DIRECTORY_SERVICE_DATA_READ_ONLY_ACCESS")
    def AWS_DIRECTORY_SERVICE_DATA_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DIRECTORY_SERVICE_DATA_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DIRECTORY_SERVICE_FULL_ACCESS")
    def AWS_DIRECTORY_SERVICE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DIRECTORY_SERVICE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DIRECTORY_SERVICE_READ_ONLY_ACCESS")
    def AWS_DIRECTORY_SERVICE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DIRECTORY_SERVICE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_DISCOVERY_CONTINUOUS_EXPORT_FIREHOSE_POLICY")
    def AWS_DISCOVERY_CONTINUOUS_EXPORT_FIREHOSE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_DISCOVERY_CONTINUOUS_EXPORT_FIREHOSE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_EC2_VSS_SNAPSHOT_POLICY")
    def AWS_EC2_VSS_SNAPSHOT_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_EC2_VSS_SNAPSHOT_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_BEANSTALK_CUSTOM_PLATFORMFOR_EC2_ROLE")
    def AWS_ELASTIC_BEANSTALK_CUSTOM_PLATFORMFOR_EC2_ROLE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_BEANSTALK_CUSTOM_PLATFORMFOR_EC2_ROLE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_BEANSTALK_MANAGED_UPDATES_CUSTOMER_ROLE_POLICY")
    def AWS_ELASTIC_BEANSTALK_MANAGED_UPDATES_CUSTOMER_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_BEANSTALK_MANAGED_UPDATES_CUSTOMER_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_BEANSTALK_MULTICONTAINER_DOCKER")
    def AWS_ELASTIC_BEANSTALK_MULTICONTAINER_DOCKER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_BEANSTALK_MULTICONTAINER_DOCKER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_BEANSTALK_READ_ONLY")
    def AWS_ELASTIC_BEANSTALK_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_BEANSTALK_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_BEANSTALK_WEB_TIER")
    def AWS_ELASTIC_BEANSTALK_WEB_TIER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_BEANSTALK_WEB_TIER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_BEANSTALK_WORKER_TIER")
    def AWS_ELASTIC_BEANSTALK_WORKER_TIER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_BEANSTALK_WORKER_TIER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_DISASTER_RECOVERY_AGENT_INSTALLATION_POLICY")
    def AWS_ELASTIC_DISASTER_RECOVERY_AGENT_INSTALLATION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_DISASTER_RECOVERY_AGENT_INSTALLATION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_DISASTER_RECOVERY_CONSOLE_FULL_ACCESS")
    def AWS_ELASTIC_DISASTER_RECOVERY_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_DISASTER_RECOVERY_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_DISASTER_RECOVERY_CONSOLE_FULL_ACCESS_V2")
    def AWS_ELASTIC_DISASTER_RECOVERY_CONSOLE_FULL_ACCESS_V2(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_DISASTER_RECOVERY_CONSOLE_FULL_ACCESS_V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_DISASTER_RECOVERY_FAILBACK_INSTALLATION_POLICY")
    def AWS_ELASTIC_DISASTER_RECOVERY_FAILBACK_INSTALLATION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_DISASTER_RECOVERY_FAILBACK_INSTALLATION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_DISASTER_RECOVERY_LAUNCH_ACTIONS_POLICY")
    def AWS_ELASTIC_DISASTER_RECOVERY_LAUNCH_ACTIONS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_DISASTER_RECOVERY_LAUNCH_ACTIONS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELASTIC_DISASTER_RECOVERY_READ_ONLY_ACCESS")
    def AWS_ELASTIC_DISASTER_RECOVERY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELASTIC_DISASTER_RECOVERY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_CONVERT_FULL_ACCESS")
    def AWS_ELEMENTAL_MEDIA_CONVERT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_CONVERT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_CONVERT_READ_ONLY")
    def AWS_ELEMENTAL_MEDIA_CONVERT_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_CONVERT_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_LIVE_FULL_ACCESS")
    def AWS_ELEMENTAL_MEDIA_LIVE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_LIVE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_LIVE_READ_ONLY")
    def AWS_ELEMENTAL_MEDIA_LIVE_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_LIVE_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_PACKAGE_FULL_ACCESS")
    def AWS_ELEMENTAL_MEDIA_PACKAGE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_PACKAGE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_PACKAGE_READ_ONLY")
    def AWS_ELEMENTAL_MEDIA_PACKAGE_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_PACKAGE_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_PACKAGE_V2_FULL_ACCESS")
    def AWS_ELEMENTAL_MEDIA_PACKAGE_V2_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_PACKAGE_V2_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_PACKAGE_V2_READ_ONLY")
    def AWS_ELEMENTAL_MEDIA_PACKAGE_V2_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_PACKAGE_V2_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_STORE_FULL_ACCESS")
    def AWS_ELEMENTAL_MEDIA_STORE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_STORE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_STORE_READ_ONLY")
    def AWS_ELEMENTAL_MEDIA_STORE_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_STORE_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_TAILOR_FULL_ACCESS")
    def AWS_ELEMENTAL_MEDIA_TAILOR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_TAILOR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ELEMENTAL_MEDIA_TAILOR_READ_ONLY")
    def AWS_ELEMENTAL_MEDIA_TAILOR_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ELEMENTAL_MEDIA_TAILOR_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ENTITY_RESOLUTION_CONSOLE_FULL_ACCESS")
    def AWS_ENTITY_RESOLUTION_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ENTITY_RESOLUTION_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ENTITY_RESOLUTION_CONSOLE_READ_ONLY_ACCESS")
    def AWS_ENTITY_RESOLUTION_CONSOLE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ENTITY_RESOLUTION_CONSOLE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_FM_ADMIN_FULL_ACCESS")
    def AWS_FM_ADMIN_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_FM_ADMIN_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_FM_ADMIN_READ_ONLY_ACCESS")
    def AWS_FM_ADMIN_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_FM_ADMIN_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_FM_MEMBER_READ_ONLY_ACCESS")
    def AWS_FM_MEMBER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_FM_MEMBER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_FOR_WORD_PRESS_PLUGIN_POLICY")
    def AWS_FOR_WORD_PRESS_PLUGIN_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_FOR_WORD_PRESS_PLUGIN_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GLUE_CONSOLE_FULL_ACCESS")
    def AWS_GLUE_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GLUE_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GLUE_CONSOLE_SAGE_MAKER_NOTEBOOK_FULL_ACCESS")
    def AWS_GLUE_CONSOLE_SAGE_MAKER_NOTEBOOK_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GLUE_CONSOLE_SAGE_MAKER_NOTEBOOK_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GLUE_DATA_BREW_FULL_ACCESS_POLICY")
    def AWS_GLUE_DATA_BREW_FULL_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GLUE_DATA_BREW_FULL_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GLUE_SCHEMA_REGISTRY_FULL_ACCESS")
    def AWS_GLUE_SCHEMA_REGISTRY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GLUE_SCHEMA_REGISTRY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GLUE_SCHEMA_REGISTRY_READONLY_ACCESS")
    def AWS_GLUE_SCHEMA_REGISTRY_READONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GLUE_SCHEMA_REGISTRY_READONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GLUE_SESSION_USER_RESTRICTED_NOTEBOOK_POLICY")
    def AWS_GLUE_SESSION_USER_RESTRICTED_NOTEBOOK_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GLUE_SESSION_USER_RESTRICTED_NOTEBOOK_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GLUE_SESSION_USER_RESTRICTED_POLICY")
    def AWS_GLUE_SESSION_USER_RESTRICTED_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GLUE_SESSION_USER_RESTRICTED_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GRAFANA_ACCOUNT_ADMINISTRATOR")
    def AWS_GRAFANA_ACCOUNT_ADMINISTRATOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GRAFANA_ACCOUNT_ADMINISTRATOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GRAFANA_CONSOLE_READ_ONLY_ACCESS")
    def AWS_GRAFANA_CONSOLE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GRAFANA_CONSOLE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GRAFANA_WORKSPACE_PERMISSION_MANAGEMENT")
    def AWS_GRAFANA_WORKSPACE_PERMISSION_MANAGEMENT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GRAFANA_WORKSPACE_PERMISSION_MANAGEMENT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GRAFANA_WORKSPACE_PERMISSION_MANAGEMENT_V2")
    def AWS_GRAFANA_WORKSPACE_PERMISSION_MANAGEMENT_V2(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GRAFANA_WORKSPACE_PERMISSION_MANAGEMENT_V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GREENGRASS_FULL_ACCESS")
    def AWS_GREENGRASS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GREENGRASS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GREENGRASS_READ_ONLY_ACCESS")
    def AWS_GREENGRASS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GREENGRASS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_GROUND_STATION_AGENT_INSTANCE_POLICY")
    def AWS_GROUND_STATION_AGENT_INSTANCE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_GROUND_STATION_AGENT_INSTANCE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_HEALTH_FULL_ACCESS")
    def AWS_HEALTH_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_HEALTH_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_HEALTH_IMAGING_FULL_ACCESS")
    def AWS_HEALTH_IMAGING_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_HEALTH_IMAGING_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_HEALTH_IMAGING_READ_ONLY_ACCESS")
    def AWS_HEALTH_IMAGING_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_HEALTH_IMAGING_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IAM_IDENTITY_CENTER_ALLOW_LIST_FOR_IDENTITY_CONTEXT")
    def AWS_IAM_IDENTITY_CENTER_ALLOW_LIST_FOR_IDENTITY_CONTEXT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IAM_IDENTITY_CENTER_ALLOW_LIST_FOR_IDENTITY_CONTEXT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IDENTITY_SYNC_FULL_ACCESS")
    def AWS_IDENTITY_SYNC_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IDENTITY_SYNC_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IDENTITY_SYNC_READ_ONLY_ACCESS")
    def AWS_IDENTITY_SYNC_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IDENTITY_SYNC_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IMAGE_BUILDER_FULL_ACCESS")
    def AWS_IMAGE_BUILDER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IMAGE_BUILDER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IMAGE_BUILDER_READ_ONLY_ACCESS")
    def AWS_IMAGE_BUILDER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IMAGE_BUILDER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IMPORT_EXPORT_FULL_ACCESS")
    def AWS_IMPORT_EXPORT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IMPORT_EXPORT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IMPORT_EXPORT_READ_ONLY_ACCESS")
    def AWS_IMPORT_EXPORT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IMPORT_EXPORT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_INCIDENT_MANAGER_INCIDENT_ACCESS_SERVICE_ROLE_POLICY")
    def AWS_INCIDENT_MANAGER_INCIDENT_ACCESS_SERVICE_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_INCIDENT_MANAGER_INCIDENT_ACCESS_SERVICE_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_INCIDENT_MANAGER_RESOLVER_ACCESS")
    def AWS_INCIDENT_MANAGER_RESOLVER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_INCIDENT_MANAGER_RESOLVER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_ANALYTICS_FULL_ACCESS")
    def AWS_IO_T_ANALYTICS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_ANALYTICS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_ANALYTICS_READ_ONLY_ACCESS")
    def AWS_IO_T_ANALYTICS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_ANALYTICS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_CONFIG_ACCESS")
    def AWS_IO_T_CONFIG_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_CONFIG_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_CONFIG_READ_ONLY_ACCESS")
    def AWS_IO_T_CONFIG_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_CONFIG_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_DATA_ACCESS")
    def AWS_IO_T_DATA_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_DATA_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_DEVICE_TESTER_FOR_FREE_RTOS_FULL_ACCESS")
    def AWS_IO_T_DEVICE_TESTER_FOR_FREE_RTOS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_DEVICE_TESTER_FOR_FREE_RTOS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_DEVICE_TESTER_FOR_GREENGRASS_FULL_ACCESS")
    def AWS_IO_T_DEVICE_TESTER_FOR_GREENGRASS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_DEVICE_TESTER_FOR_GREENGRASS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_EVENTS_FULL_ACCESS")
    def AWS_IO_T_EVENTS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_EVENTS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_EVENTS_READ_ONLY_ACCESS")
    def AWS_IO_T_EVENTS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_EVENTS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_FULL_ACCESS")
    def AWS_IO_T_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_SITE_WISE_CONSOLE_FULL_ACCESS")
    def AWS_IO_T_SITE_WISE_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_SITE_WISE_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_SITE_WISE_FULL_ACCESS")
    def AWS_IO_T_SITE_WISE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_SITE_WISE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_SITE_WISE_READ_ONLY_ACCESS")
    def AWS_IO_T_SITE_WISE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_SITE_WISE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_WIRELESS_DATA_ACCESS")
    def AWS_IO_T_WIRELESS_DATA_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_WIRELESS_DATA_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_WIRELESS_FULL_ACCESS")
    def AWS_IO_T_WIRELESS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_WIRELESS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_WIRELESS_FULL_PUBLISH_ACCESS")
    def AWS_IO_T_WIRELESS_FULL_PUBLISH_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_WIRELESS_FULL_PUBLISH_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_WIRELESS_GATEWAY_CERT_MANAGER")
    def AWS_IO_T_WIRELESS_GATEWAY_CERT_MANAGER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_WIRELESS_GATEWAY_CERT_MANAGER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_WIRELESS_LOGGING")
    def AWS_IO_T_WIRELESS_LOGGING(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_WIRELESS_LOGGING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T_WIRELESS_READ_ONLY_ACCESS")
    def AWS_IO_T_WIRELESS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T_WIRELESS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T1_CLICK_FULL_ACCESS")
    def AWS_IO_T1_CLICK_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T1_CLICK_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IO_T1_CLICK_READ_ONLY_ACCESS")
    def AWS_IO_T1_CLICK_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IO_T1_CLICK_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_IQ_FULL_ACCESS")
    def AWS_IQ_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_IQ_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_KEY_MANAGEMENT_SERVICE_POWER_USER")
    def AWS_KEY_MANAGEMENT_SERVICE_POWER_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_KEY_MANAGEMENT_SERVICE_POWER_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_LAKE_FORMATION_CROSS_ACCOUNT_MANAGER")
    def AWS_LAKE_FORMATION_CROSS_ACCOUNT_MANAGER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_LAKE_FORMATION_CROSS_ACCOUNT_MANAGER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_LAKE_FORMATION_DATA_ADMIN")
    def AWS_LAKE_FORMATION_DATA_ADMIN(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_LAKE_FORMATION_DATA_ADMIN"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_LAMBDA_EXECUTE")
    def AWS_LAMBDA_EXECUTE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_LAMBDA_EXECUTE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_LAMBDA_FULL_ACCESS")
    def AWS_LAMBDA_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_LAMBDA_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_LAMBDA_INVOCATION_DYNAMO_DB")
    def AWS_LAMBDA_INVOCATION_DYNAMO_DB(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_LAMBDA_INVOCATION_DYNAMO_DB"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_LAMBDA_READ_ONLY_ACCESS")
    def AWS_LAMBDA_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_LAMBDA_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_AMI_INGESTION")
    def AWS_MARKETPLACE_AMI_INGESTION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_AMI_INGESTION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_FULL_ACCESS")
    def AWS_MARKETPLACE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_GET_ENTITLEMENTS")
    def AWS_MARKETPLACE_GET_ENTITLEMENTS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_GET_ENTITLEMENTS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_IMAGE_BUILD_FULL_ACCESS")
    def AWS_MARKETPLACE_IMAGE_BUILD_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_IMAGE_BUILD_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_MANAGE_SUBSCRIPTIONS")
    def AWS_MARKETPLACE_MANAGE_SUBSCRIPTIONS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_MANAGE_SUBSCRIPTIONS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_METERING_FULL_ACCESS")
    def AWS_MARKETPLACE_METERING_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_METERING_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_METERING_REGISTER_USAGE")
    def AWS_MARKETPLACE_METERING_REGISTER_USAGE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_METERING_REGISTER_USAGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_PROCUREMENT_SYSTEM_ADMIN_FULL_ACCESS")
    def AWS_MARKETPLACE_PROCUREMENT_SYSTEM_ADMIN_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_PROCUREMENT_SYSTEM_ADMIN_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_READ_ONLY")
    def AWS_MARKETPLACE_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_SELLER_FULL_ACCESS")
    def AWS_MARKETPLACE_SELLER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_SELLER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_SELLER_OFFER_MANAGEMENT")
    def AWS_MARKETPLACE_SELLER_OFFER_MANAGEMENT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_SELLER_OFFER_MANAGEMENT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_SELLER_PRODUCTS_FULL_ACCESS")
    def AWS_MARKETPLACE_SELLER_PRODUCTS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_SELLER_PRODUCTS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MARKETPLACE_SELLER_PRODUCTS_READ_ONLY")
    def AWS_MARKETPLACE_SELLER_PRODUCTS_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MARKETPLACE_SELLER_PRODUCTS_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MIGRATION_HUB_FULL_ACCESS")
    def AWS_MIGRATION_HUB_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MIGRATION_HUB_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MIGRATION_HUB_ORCHESTRATOR_CONSOLE_FULL_ACCESS")
    def AWS_MIGRATION_HUB_ORCHESTRATOR_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MIGRATION_HUB_ORCHESTRATOR_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MIGRATION_HUB_ORCHESTRATOR_INSTANCE_ROLE_POLICY")
    def AWS_MIGRATION_HUB_ORCHESTRATOR_INSTANCE_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MIGRATION_HUB_ORCHESTRATOR_INSTANCE_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MIGRATION_HUB_ORCHESTRATOR_PLUGIN")
    def AWS_MIGRATION_HUB_ORCHESTRATOR_PLUGIN(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MIGRATION_HUB_ORCHESTRATOR_PLUGIN"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MIGRATION_HUB_REFACTOR_SPACES_ENVIRONMENTS_WITHOUT_BRIDGES_FULL_ACCESS")
    def AWS_MIGRATION_HUB_REFACTOR_SPACES_ENVIRONMENTS_WITHOUT_BRIDGES_FULL_ACCESS(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MIGRATION_HUB_REFACTOR_SPACES_ENVIRONMENTS_WITHOUT_BRIDGES_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MIGRATION_HUB_REFACTOR_SPACES_FULL_ACCESS")
    def AWS_MIGRATION_HUB_REFACTOR_SPACES_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MIGRATION_HUB_REFACTOR_SPACES_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MIGRATION_HUB_STRATEGY_COLLECTOR")
    def AWS_MIGRATION_HUB_STRATEGY_COLLECTOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MIGRATION_HUB_STRATEGY_COLLECTOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_MIGRATION_HUB_STRATEGY_CONSOLE_FULL_ACCESS")
    def AWS_MIGRATION_HUB_STRATEGY_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_MIGRATION_HUB_STRATEGY_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_NETWORK_MANAGER_FULL_ACCESS")
    def AWS_NETWORK_MANAGER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_NETWORK_MANAGER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_NETWORK_MANAGER_READ_ONLY_ACCESS")
    def AWS_NETWORK_MANAGER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_NETWORK_MANAGER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_OPS_WORKS_CLOUD_WATCH_LOGS")
    def AWS_OPS_WORKS_CLOUD_WATCH_LOGS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_OPS_WORKS_CLOUD_WATCH_LOGS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_OPS_WORKS_CM_INSTANCE_PROFILE_ROLE")
    def AWS_OPS_WORKS_CM_INSTANCE_PROFILE_ROLE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_OPS_WORKS_CM_INSTANCE_PROFILE_ROLE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_OPS_WORKS_FULL_ACCESS")
    def AWS_OPS_WORKS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_OPS_WORKS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_OPS_WORKS_INSTANCE_REGISTRATION")
    def AWS_OPS_WORKS_INSTANCE_REGISTRATION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_OPS_WORKS_INSTANCE_REGISTRATION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_OPS_WORKS_REGISTER_CLI_EC2")
    def AWS_OPS_WORKS_REGISTER_CLI_EC2(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_OPS_WORKS_REGISTER_CLI_EC2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_OPS_WORKS_REGISTER_CLI_ON_PREMISES")
    def AWS_OPS_WORKS_REGISTER_CLI_ON_PREMISES(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_OPS_WORKS_REGISTER_CLI_ON_PREMISES"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ORGANIZATIONS_FULL_ACCESS")
    def AWS_ORGANIZATIONS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ORGANIZATIONS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ORGANIZATIONS_READ_ONLY_ACCESS")
    def AWS_ORGANIZATIONS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ORGANIZATIONS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_OUTPOSTS_AUTHORIZE_SERVER_POLICY")
    def AWS_OUTPOSTS_AUTHORIZE_SERVER_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_OUTPOSTS_AUTHORIZE_SERVER_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PANORAMA_FULL_ACCESS")
    def AWS_PANORAMA_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PANORAMA_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PARTNER_CENTRAL_FULL_ACCESS")
    def AWS_PARTNER_CENTRAL_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PARTNER_CENTRAL_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PARTNER_CENTRAL_OPPORTUNITY_MANAGEMENT")
    def AWS_PARTNER_CENTRAL_OPPORTUNITY_MANAGEMENT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PARTNER_CENTRAL_OPPORTUNITY_MANAGEMENT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PARTNER_CENTRAL_SANDBOX_FULL_ACCESS")
    def AWS_PARTNER_CENTRAL_SANDBOX_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PARTNER_CENTRAL_SANDBOX_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PARTNER_CENTRAL_SELLING_RESOURCE_SNAPSHOT_JOB_EXECUTION_ROLE_POLICY")
    def AWS_PARTNER_CENTRAL_SELLING_RESOURCE_SNAPSHOT_JOB_EXECUTION_ROLE_POLICY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PARTNER_CENTRAL_SELLING_RESOURCE_SNAPSHOT_JOB_EXECUTION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PARTNER_LED_SUPPORT_READ_ONLY_ACCESS")
    def AWS_PARTNER_LED_SUPPORT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PARTNER_LED_SUPPORT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PRICE_LIST_SERVICE_FULL_ACCESS")
    def AWS_PRICE_LIST_SERVICE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PRICE_LIST_SERVICE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PRIVATE_CA_AUDITOR")
    def AWS_PRIVATE_CA_AUDITOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PRIVATE_CA_AUDITOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PRIVATE_CA_FULL_ACCESS")
    def AWS_PRIVATE_CA_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PRIVATE_CA_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PRIVATE_CA_PRIVILEGED_USER")
    def AWS_PRIVATE_CA_PRIVILEGED_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PRIVATE_CA_PRIVILEGED_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PRIVATE_CA_READ_ONLY")
    def AWS_PRIVATE_CA_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PRIVATE_CA_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PRIVATE_CA_USER")
    def AWS_PRIVATE_CA_USER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PRIVATE_CA_USER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PRIVATE_MARKETPLACE_ADMIN_FULL_ACCESS")
    def AWS_PRIVATE_MARKETPLACE_ADMIN_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PRIVATE_MARKETPLACE_ADMIN_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PRIVATE_MARKETPLACE_REQUESTS")
    def AWS_PRIVATE_MARKETPLACE_REQUESTS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PRIVATE_MARKETPLACE_REQUESTS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PROTON_CODE_BUILD_PROVISIONING_BASIC_ACCESS")
    def AWS_PROTON_CODE_BUILD_PROVISIONING_BASIC_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PROTON_CODE_BUILD_PROVISIONING_BASIC_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PROTON_DEVELOPER_ACCESS")
    def AWS_PROTON_DEVELOPER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PROTON_DEVELOPER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PROTON_FULL_ACCESS")
    def AWS_PROTON_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PROTON_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PROTON_READ_ONLY_ACCESS")
    def AWS_PROTON_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PROTON_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_PURCHASE_ORDERS_SERVICE_ROLE_POLICY")
    def AWS_PURCHASE_ORDERS_SERVICE_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_PURCHASE_ORDERS_SERVICE_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_CFGC_PACKS_PERMISSIONS_BOUNDARY")
    def AWS_QUICK_SETUP_CFGC_PACKS_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_CFGC_PACKS_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_DEPLOYMENT_ROLE_POLICY")
    def AWS_QUICK_SETUP_DEPLOYMENT_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_DEPLOYMENT_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_DEV_OPS_GURU_PERMISSIONS_BOUNDARY")
    def AWS_QUICK_SETUP_DEV_OPS_GURU_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_DEV_OPS_GURU_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_DISTRIBUTOR_PERMISSIONS_BOUNDARY")
    def AWS_QUICK_SETUP_DISTRIBUTOR_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_DISTRIBUTOR_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_ENABLE_AREX_EXECUTION_POLICY")
    def AWS_QUICK_SETUP_ENABLE_AREX_EXECUTION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_ENABLE_AREX_EXECUTION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_ENABLE_DHMC_EXECUTION_POLICY")
    def AWS_QUICK_SETUP_ENABLE_DHMC_EXECUTION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_ENABLE_DHMC_EXECUTION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_MANAGED_INSTANCE_PROFILE_EXECUTION_POLICY")
    def AWS_QUICK_SETUP_MANAGED_INSTANCE_PROFILE_EXECUTION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_MANAGED_INSTANCE_PROFILE_EXECUTION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_PATCH_POLICY_BASELINE_ACCESS")
    def AWS_QUICK_SETUP_PATCH_POLICY_BASELINE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_PATCH_POLICY_BASELINE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_PATCH_POLICY_DEPLOYMENT_ROLE_POLICY")
    def AWS_QUICK_SETUP_PATCH_POLICY_DEPLOYMENT_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_PATCH_POLICY_DEPLOYMENT_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_PATCH_POLICY_PERMISSIONS_BOUNDARY")
    def AWS_QUICK_SETUP_PATCH_POLICY_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_PATCH_POLICY_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_SCHEDULER_PERMISSIONS_BOUNDARY")
    def AWS_QUICK_SETUP_SCHEDULER_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_SCHEDULER_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_SSM_DEPLOYMENT_ROLE_POLICY")
    def AWS_QUICK_SETUP_SSM_DEPLOYMENT_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_SSM_DEPLOYMENT_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_SSM_DEPLOYMENT_S3_BUCKET_ROLE_POLICY")
    def AWS_QUICK_SETUP_SSM_DEPLOYMENT_S3_BUCKET_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_SSM_DEPLOYMENT_S3_BUCKET_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_SSM_HOST_MGMT_PERMISSIONS_BOUNDARY")
    def AWS_QUICK_SETUP_SSM_HOST_MGMT_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_SSM_HOST_MGMT_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_SSM_LIFECYCLE_MANAGEMENT_EXECUTION_POLICY")
    def AWS_QUICK_SETUP_SSM_LIFECYCLE_MANAGEMENT_EXECUTION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_SSM_LIFECYCLE_MANAGEMENT_EXECUTION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SETUP_SSM_MANAGE_RESOURCES_EXECUTION_POLICY")
    def AWS_QUICK_SETUP_SSM_MANAGE_RESOURCES_EXECUTION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SETUP_SSM_MANAGE_RESOURCES_EXECUTION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SIGHT_ASSET_BUNDLE_EXPORT_POLICY")
    def AWS_QUICK_SIGHT_ASSET_BUNDLE_EXPORT_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SIGHT_ASSET_BUNDLE_EXPORT_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SIGHT_ASSET_BUNDLE_IMPORT_POLICY")
    def AWS_QUICK_SIGHT_ASSET_BUNDLE_IMPORT_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SIGHT_ASSET_BUNDLE_IMPORT_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_QUICK_SIGHT_IO_T_ANALYTICS_ACCESS")
    def AWS_QUICK_SIGHT_IO_T_ANALYTICS_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_QUICK_SIGHT_IO_T_ANALYTICS_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_REFACTORING_TOOLKIT_FULL_ACCESS")
    def AWS_REFACTORING_TOOLKIT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_REFACTORING_TOOLKIT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_REFACTORING_TOOLKIT_SIDECAR_POLICY")
    def AWS_REFACTORING_TOOLKIT_SIDECAR_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_REFACTORING_TOOLKIT_SIDECAR_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_REPOST_SPACE_SUPPORT_OPERATIONS_POLICY")
    def AWS_REPOST_SPACE_SUPPORT_OPERATIONS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_REPOST_SPACE_SUPPORT_OPERATIONS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_RESILIENCE_HUB_ASSSESSMENT_EXECUTION_POLICY")
    def AWS_RESILIENCE_HUB_ASSSESSMENT_EXECUTION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_RESILIENCE_HUB_ASSSESSMENT_EXECUTION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_RESOURCE_ACCESS_MANAGER_FULL_ACCESS")
    def AWS_RESOURCE_ACCESS_MANAGER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_RESOURCE_ACCESS_MANAGER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_RESOURCE_ACCESS_MANAGER_READ_ONLY_ACCESS")
    def AWS_RESOURCE_ACCESS_MANAGER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_RESOURCE_ACCESS_MANAGER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_RESOURCE_ACCESS_MANAGER_RESOURCE_SHARE_PARTICIPANT_ACCESS")
    def AWS_RESOURCE_ACCESS_MANAGER_RESOURCE_SHARE_PARTICIPANT_ACCESS(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_RESOURCE_ACCESS_MANAGER_RESOURCE_SHARE_PARTICIPANT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_RESOURCE_EXPLORER_FULL_ACCESS")
    def AWS_RESOURCE_EXPLORER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_RESOURCE_EXPLORER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_RESOURCE_EXPLORER_ORGANIZATIONS_ACCESS")
    def AWS_RESOURCE_EXPLORER_ORGANIZATIONS_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_RESOURCE_EXPLORER_ORGANIZATIONS_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_RESOURCE_EXPLORER_READ_ONLY_ACCESS")
    def AWS_RESOURCE_EXPLORER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_RESOURCE_EXPLORER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_RESOURCE_GROUPS_READ_ONLY_ACCESS")
    def AWS_RESOURCE_GROUPS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_RESOURCE_GROUPS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ROBO_MAKER_FULL_ACCESS")
    def AWS_ROBO_MAKER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ROBO_MAKER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ROBO_MAKER_READ_ONLY_ACCESS")
    def AWS_ROBO_MAKER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ROBO_MAKER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_ROBO_MAKER_SERVICE_ROLE_POLICY")
    def AWS_ROBO_MAKER_SERVICE_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_ROBO_MAKER_SERVICE_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SAVINGS_PLANS_FULL_ACCESS")
    def AWS_SAVINGS_PLANS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SAVINGS_PLANS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SAVINGS_PLANS_READ_ONLY_ACCESS")
    def AWS_SAVINGS_PLANS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SAVINGS_PLANS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SECURITY_HUB_FULL_ACCESS")
    def AWS_SECURITY_HUB_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SECURITY_HUB_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SECURITY_HUB_ORGANIZATIONS_ACCESS")
    def AWS_SECURITY_HUB_ORGANIZATIONS_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SECURITY_HUB_ORGANIZATIONS_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SECURITY_HUB_READ_ONLY_ACCESS")
    def AWS_SECURITY_HUB_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SECURITY_HUB_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SECURITY_INCIDENT_RESPONSE_CASE_FULL_ACCESS")
    def AWS_SECURITY_INCIDENT_RESPONSE_CASE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SECURITY_INCIDENT_RESPONSE_CASE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SECURITY_INCIDENT_RESPONSE_FULL_ACCESS")
    def AWS_SECURITY_INCIDENT_RESPONSE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SECURITY_INCIDENT_RESPONSE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SECURITY_INCIDENT_RESPONSE_READ_ONLY_ACCESS")
    def AWS_SECURITY_INCIDENT_RESPONSE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SECURITY_INCIDENT_RESPONSE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SERVICE_CATALOG_ADMIN_FULL_ACCESS")
    def AWS_SERVICE_CATALOG_ADMIN_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SERVICE_CATALOG_ADMIN_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SERVICE_CATALOG_ADMIN_READ_ONLY_ACCESS")
    def AWS_SERVICE_CATALOG_ADMIN_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SERVICE_CATALOG_ADMIN_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SERVICE_CATALOG_APP_REGISTRY_FULL_ACCESS")
    def AWS_SERVICE_CATALOG_APP_REGISTRY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SERVICE_CATALOG_APP_REGISTRY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SERVICE_CATALOG_APP_REGISTRY_READ_ONLY_ACCESS")
    def AWS_SERVICE_CATALOG_APP_REGISTRY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SERVICE_CATALOG_APP_REGISTRY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SERVICE_CATALOG_END_USER_FULL_ACCESS")
    def AWS_SERVICE_CATALOG_END_USER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SERVICE_CATALOG_END_USER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SERVICE_CATALOG_END_USER_READ_ONLY_ACCESS")
    def AWS_SERVICE_CATALOG_END_USER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SERVICE_CATALOG_END_USER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSM_AUTOMATION_DIAGNOSIS_BUCKET_POLICY")
    def AWS_SSM_AUTOMATION_DIAGNOSIS_BUCKET_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSM_AUTOMATION_DIAGNOSIS_BUCKET_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSM_DIAGNOSIS_AUTOMATION_ADMINISTRATION_ROLE_POLICY")
    def AWS_SSM_DIAGNOSIS_AUTOMATION_ADMINISTRATION_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSM_DIAGNOSIS_AUTOMATION_ADMINISTRATION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSM_DIAGNOSIS_AUTOMATION_EXECUTION_ROLE_POLICY")
    def AWS_SSM_DIAGNOSIS_AUTOMATION_EXECUTION_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSM_DIAGNOSIS_AUTOMATION_EXECUTION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSM_DIAGNOSIS_AUTOMATION_OPERATIONAL_ACCOUNT_ADMINISTRATION_ROLE_POLICY")
    def AWS_SSM_DIAGNOSIS_AUTOMATION_OPERATIONAL_ACCOUNT_ADMINISTRATION_ROLE_POLICY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSM_DIAGNOSIS_AUTOMATION_OPERATIONAL_ACCOUNT_ADMINISTRATION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSM_REMEDIATION_AUTOMATION_ADMINISTRATION_ROLE_POLICY")
    def AWS_SSM_REMEDIATION_AUTOMATION_ADMINISTRATION_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSM_REMEDIATION_AUTOMATION_ADMINISTRATION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSM_REMEDIATION_AUTOMATION_EXECUTION_ROLE_POLICY")
    def AWS_SSM_REMEDIATION_AUTOMATION_EXECUTION_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSM_REMEDIATION_AUTOMATION_EXECUTION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSM_REMEDIATION_AUTOMATION_OPERATIONAL_ACCOUNT_ADMINISTRATION_ROLE_POLICY")
    def AWS_SSM_REMEDIATION_AUTOMATION_OPERATIONAL_ACCOUNT_ADMINISTRATION_ROLE_POLICY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSM_REMEDIATION_AUTOMATION_OPERATIONAL_ACCOUNT_ADMINISTRATION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSO_DIRECTORY_ADMINISTRATOR")
    def AWS_SSO_DIRECTORY_ADMINISTRATOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSO_DIRECTORY_ADMINISTRATOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSO_DIRECTORY_READ_ONLY")
    def AWS_SSO_DIRECTORY_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSO_DIRECTORY_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSO_MASTER_ACCOUNT_ADMINISTRATOR")
    def AWS_SSO_MASTER_ACCOUNT_ADMINISTRATOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSO_MASTER_ACCOUNT_ADMINISTRATOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSO_MEMBER_ACCOUNT_ADMINISTRATOR")
    def AWS_SSO_MEMBER_ACCOUNT_ADMINISTRATOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSO_MEMBER_ACCOUNT_ADMINISTRATOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SSO_READ_ONLY")
    def AWS_SSO_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SSO_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_STEP_FUNCTIONS_CONSOLE_FULL_ACCESS")
    def AWS_STEP_FUNCTIONS_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_STEP_FUNCTIONS_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_STEP_FUNCTIONS_FULL_ACCESS")
    def AWS_STEP_FUNCTIONS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_STEP_FUNCTIONS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_STEP_FUNCTIONS_READ_ONLY_ACCESS")
    def AWS_STEP_FUNCTIONS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_STEP_FUNCTIONS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_STORAGE_GATEWAY_FULL_ACCESS")
    def AWS_STORAGE_GATEWAY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_STORAGE_GATEWAY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_STORAGE_GATEWAY_READ_ONLY_ACCESS")
    def AWS_STORAGE_GATEWAY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_STORAGE_GATEWAY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SUPPORT_ACCESS")
    def AWS_SUPPORT_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SUPPORT_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SUPPORT_APP_FULL_ACCESS")
    def AWS_SUPPORT_APP_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SUPPORT_APP_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SUPPORT_APP_READ_ONLY_ACCESS")
    def AWS_SUPPORT_APP_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SUPPORT_APP_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SUPPORT_PLANS_FULL_ACCESS")
    def AWS_SUPPORT_PLANS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SUPPORT_PLANS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SUPPORT_PLANS_READ_ONLY_ACCESS")
    def AWS_SUPPORT_PLANS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SUPPORT_PLANS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SYSTEMS_MANAGER_ENABLE_CONFIG_RECORDING_EXECUTION_POLICY")
    def AWS_SYSTEMS_MANAGER_ENABLE_CONFIG_RECORDING_EXECUTION_POLICY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SYSTEMS_MANAGER_ENABLE_CONFIG_RECORDING_EXECUTION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SYSTEMS_MANAGER_ENABLE_EXPLORER_EXECUTION_POLICY")
    def AWS_SYSTEMS_MANAGER_ENABLE_EXPLORER_EXECUTION_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SYSTEMS_MANAGER_ENABLE_EXPLORER_EXECUTION_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SYSTEMS_MANAGER_FOR_SAP_FULL_ACCESS")
    def AWS_SYSTEMS_MANAGER_FOR_SAP_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SYSTEMS_MANAGER_FOR_SAP_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_SYSTEMS_MANAGER_FOR_SAP_READ_ONLY_ACCESS")
    def AWS_SYSTEMS_MANAGER_FOR_SAP_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_SYSTEMS_MANAGER_FOR_SAP_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_THINKBOX_ASSET_SERVER_POLICY")
    def AWS_THINKBOX_ASSET_SERVER_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_THINKBOX_ASSET_SERVER_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_THINKBOX_AWS_PORTAL_ADMIN_POLICY")
    def AWS_THINKBOX_AWS_PORTAL_ADMIN_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_THINKBOX_AWS_PORTAL_ADMIN_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_THINKBOX_AWS_PORTAL_GATEWAY_POLICY")
    def AWS_THINKBOX_AWS_PORTAL_GATEWAY_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_THINKBOX_AWS_PORTAL_GATEWAY_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_THINKBOX_AWS_PORTAL_WORKER_POLICY")
    def AWS_THINKBOX_AWS_PORTAL_WORKER_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_THINKBOX_AWS_PORTAL_WORKER_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_THINKBOX_DEADLINE_RESOURCE_TRACKER_ACCESS_POLICY")
    def AWS_THINKBOX_DEADLINE_RESOURCE_TRACKER_ACCESS_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_THINKBOX_DEADLINE_RESOURCE_TRACKER_ACCESS_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_THINKBOX_DEADLINE_RESOURCE_TRACKER_ADMIN_POLICY")
    def AWS_THINKBOX_DEADLINE_RESOURCE_TRACKER_ADMIN_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_THINKBOX_DEADLINE_RESOURCE_TRACKER_ADMIN_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_THINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_ADMIN_POLICY")
    def AWS_THINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_ADMIN_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_THINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_ADMIN_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_THINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_WORKER_POLICY")
    def AWS_THINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_WORKER_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_THINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_WORKER_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_TRANSFER_CONSOLE_FULL_ACCESS")
    def AWS_TRANSFER_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_TRANSFER_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_TRANSFER_FULL_ACCESS")
    def AWS_TRANSFER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_TRANSFER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_TRANSFER_READ_ONLY_ACCESS")
    def AWS_TRANSFER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_TRANSFER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_TRUSTED_ADVISOR_PRIORITY_FULL_ACCESS")
    def AWS_TRUSTED_ADVISOR_PRIORITY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_TRUSTED_ADVISOR_PRIORITY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_TRUSTED_ADVISOR_PRIORITY_READ_ONLY_ACCESS")
    def AWS_TRUSTED_ADVISOR_PRIORITY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_TRUSTED_ADVISOR_PRIORITY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_VENDOR_INSIGHTS_ASSESSOR_FULL_ACCESS")
    def AWS_VENDOR_INSIGHTS_ASSESSOR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_VENDOR_INSIGHTS_ASSESSOR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_VENDOR_INSIGHTS_ASSESSOR_READ_ONLY")
    def AWS_VENDOR_INSIGHTS_ASSESSOR_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_VENDOR_INSIGHTS_ASSESSOR_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_VENDOR_INSIGHTS_VENDOR_FULL_ACCESS")
    def AWS_VENDOR_INSIGHTS_VENDOR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_VENDOR_INSIGHTS_VENDOR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_VENDOR_INSIGHTS_VENDOR_READ_ONLY")
    def AWS_VENDOR_INSIGHTS_VENDOR_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_VENDOR_INSIGHTS_VENDOR_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_WAF_CONSOLE_FULL_ACCESS")
    def AWS_WAF_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_WAF_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_WAF_CONSOLE_READ_ONLY_ACCESS")
    def AWS_WAF_CONSOLE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_WAF_CONSOLE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_WAF_FULL_ACCESS")
    def AWS_WAF_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_WAF_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_WAF_READ_ONLY_ACCESS")
    def AWS_WAF_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_WAF_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_WICKR_FULL_ACCESS")
    def AWS_WICKR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_WICKR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_X_RAY_DAEMON_WRITE_ACCESS")
    def AWS_X_RAY_DAEMON_WRITE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_X_RAY_DAEMON_WRITE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_XRAY_CROSS_ACCOUNT_SHARING_CONFIGURATION")
    def AWS_XRAY_CROSS_ACCOUNT_SHARING_CONFIGURATION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_XRAY_CROSS_ACCOUNT_SHARING_CONFIGURATION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_XRAY_FULL_ACCESS")
    def AWS_XRAY_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_XRAY_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_XRAY_READ_ONLY_ACCESS")
    def AWS_XRAY_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_XRAY_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AWS_XRAY_WRITE_ONLY_ACCESS")
    def AWS_XRAY_WRITE_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "AWS_XRAY_WRITE_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_FRONT_FULL_ACCESS")
    def CLOUD_FRONT_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_FRONT_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_FRONT_READ_ONLY_ACCESS")
    def CLOUD_FRONT_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_FRONT_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_SEARCH_FULL_ACCESS")
    def CLOUD_SEARCH_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_SEARCH_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_SEARCH_READ_ONLY_ACCESS")
    def CLOUD_SEARCH_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_SEARCH_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_ACTIONS_EC2_ACCESS")
    def CLOUD_WATCH_ACTIONS_EC2_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_ACTIONS_EC2_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_AGENT_ADMIN_POLICY")
    def CLOUD_WATCH_AGENT_ADMIN_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_AGENT_ADMIN_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_AGENT_SERVER_POLICY")
    def CLOUD_WATCH_AGENT_SERVER_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_AGENT_SERVER_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_APPLICATION_INSIGHTS_FULL_ACCESS")
    def CLOUD_WATCH_APPLICATION_INSIGHTS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_APPLICATION_INSIGHTS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_APPLICATION_INSIGHTS_READ_ONLY_ACCESS")
    def CLOUD_WATCH_APPLICATION_INSIGHTS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_APPLICATION_INSIGHTS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_APPLICATION_SIGNALS_FULL_ACCESS")
    def CLOUD_WATCH_APPLICATION_SIGNALS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_APPLICATION_SIGNALS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_APPLICATION_SIGNALS_READ_ONLY_ACCESS")
    def CLOUD_WATCH_APPLICATION_SIGNALS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_APPLICATION_SIGNALS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_AUTOMATIC_DASHBOARDS_ACCESS")
    def CLOUD_WATCH_AUTOMATIC_DASHBOARDS_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_AUTOMATIC_DASHBOARDS_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_CROSS_ACCOUNT_SHARING_CONFIGURATION")
    def CLOUD_WATCH_CROSS_ACCOUNT_SHARING_CONFIGURATION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_CROSS_ACCOUNT_SHARING_CONFIGURATION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_EVENTS_FULL_ACCESS")
    def CLOUD_WATCH_EVENTS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_EVENTS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_EVENTS_READ_ONLY_ACCESS")
    def CLOUD_WATCH_EVENTS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_EVENTS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_FULL_ACCESS")
    def CLOUD_WATCH_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_FULL_ACCESS_V2")
    def CLOUD_WATCH_FULL_ACCESS_V2(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_FULL_ACCESS_V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_INTERNET_MONITOR_FULL_ACCESS")
    def CLOUD_WATCH_INTERNET_MONITOR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_INTERNET_MONITOR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_INTERNET_MONITOR_READ_ONLY_ACCESS")
    def CLOUD_WATCH_INTERNET_MONITOR_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_INTERNET_MONITOR_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_LAMBDA_APPLICATION_SIGNALS_EXECUTION_ROLE_POLICY")
    def CLOUD_WATCH_LAMBDA_APPLICATION_SIGNALS_EXECUTION_ROLE_POLICY(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_LAMBDA_APPLICATION_SIGNALS_EXECUTION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_LAMBDA_INSIGHTS_EXECUTION_ROLE_POLICY")
    def CLOUD_WATCH_LAMBDA_INSIGHTS_EXECUTION_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_LAMBDA_INSIGHTS_EXECUTION_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_LOGS_CROSS_ACCOUNT_SHARING_CONFIGURATION")
    def CLOUD_WATCH_LOGS_CROSS_ACCOUNT_SHARING_CONFIGURATION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_LOGS_CROSS_ACCOUNT_SHARING_CONFIGURATION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_LOGS_FULL_ACCESS")
    def CLOUD_WATCH_LOGS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_LOGS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_LOGS_READ_ONLY_ACCESS")
    def CLOUD_WATCH_LOGS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_LOGS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_NETWORK_FLOW_MONITOR_AGENT_PUBLISH_POLICY")
    def CLOUD_WATCH_NETWORK_FLOW_MONITOR_AGENT_PUBLISH_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_NETWORK_FLOW_MONITOR_AGENT_PUBLISH_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_OPEN_SEARCH_DASHBOARD_ACCESS")
    def CLOUD_WATCH_OPEN_SEARCH_DASHBOARD_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_OPEN_SEARCH_DASHBOARD_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_OPEN_SEARCH_DASHBOARDS_FULL_ACCESS")
    def CLOUD_WATCH_OPEN_SEARCH_DASHBOARDS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_OPEN_SEARCH_DASHBOARDS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_READ_ONLY_ACCESS")
    def CLOUD_WATCH_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_SYNTHETICS_FULL_ACCESS")
    def CLOUD_WATCH_SYNTHETICS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_SYNTHETICS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUD_WATCH_SYNTHETICS_READ_ONLY_ACCESS")
    def CLOUD_WATCH_SYNTHETICS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUD_WATCH_SYNTHETICS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COMPREHEND_FULL_ACCESS")
    def COMPREHEND_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "COMPREHEND_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COMPREHEND_MEDICAL_FULL_ACCESS")
    def COMPREHEND_MEDICAL_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "COMPREHEND_MEDICAL_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COMPREHEND_READ_ONLY")
    def COMPREHEND_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "COMPREHEND_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COMPUTE_OPTIMIZER_READ_ONLY_ACCESS")
    def COMPUTE_OPTIMIZER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "COMPUTE_OPTIMIZER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COST_OPTIMIZATION_HUB_ADMIN_ACCESS")
    def COST_OPTIMIZATION_HUB_ADMIN_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "COST_OPTIMIZATION_HUB_ADMIN_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COST_OPTIMIZATION_HUB_READ_ONLY_ACCESS")
    def COST_OPTIMIZATION_HUB_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "COST_OPTIMIZATION_HUB_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EC2_FAST_LAUNCH_FULL_ACCESS")
    def EC2_FAST_LAUNCH_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "EC2_FAST_LAUNCH_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EC2_IMAGE_BUILDER_CROSS_ACCOUNT_DISTRIBUTION_ACCESS")
    def EC2_IMAGE_BUILDER_CROSS_ACCOUNT_DISTRIBUTION_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "EC2_IMAGE_BUILDER_CROSS_ACCOUNT_DISTRIBUTION_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EC2_INSTANCE_CONNECT")
    def EC2_INSTANCE_CONNECT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "EC2_INSTANCE_CONNECT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER")
    def EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER_ECR_CONTAINER_BUILDS")
    def EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER_ECR_CONTAINER_BUILDS(
        cls,
    ) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER_ECR_CONTAINER_BUILDS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ELASTIC_LOAD_BALANCING_FULL_ACCESS")
    def ELASTIC_LOAD_BALANCING_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ELASTIC_LOAD_BALANCING_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ELASTIC_LOAD_BALANCING_READ_ONLY")
    def ELASTIC_LOAD_BALANCING_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ELASTIC_LOAD_BALANCING_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ELEMENTAL_ACTIVATIONS_DOWNLOAD_SOFTWARE_ACCESS")
    def ELEMENTAL_ACTIVATIONS_DOWNLOAD_SOFTWARE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ELEMENTAL_ACTIVATIONS_DOWNLOAD_SOFTWARE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ELEMENTAL_ACTIVATIONS_FULL_ACCESS")
    def ELEMENTAL_ACTIVATIONS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ELEMENTAL_ACTIVATIONS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ELEMENTAL_ACTIVATIONS_GENERATE_LICENSES")
    def ELEMENTAL_ACTIVATIONS_GENERATE_LICENSES(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ELEMENTAL_ACTIVATIONS_GENERATE_LICENSES"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ELEMENTAL_ACTIVATIONS_READ_ONLY_ACCESS")
    def ELEMENTAL_ACTIVATIONS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ELEMENTAL_ACTIVATIONS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ELEMENTAL_APPLIANCES_SOFTWARE_FULL_ACCESS")
    def ELEMENTAL_APPLIANCES_SOFTWARE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ELEMENTAL_APPLIANCES_SOFTWARE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ELEMENTAL_APPLIANCES_SOFTWARE_READ_ONLY_ACCESS")
    def ELEMENTAL_APPLIANCES_SOFTWARE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ELEMENTAL_APPLIANCES_SOFTWARE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ELEMENTAL_SUPPORT_CENTER_FULL_ACCESS")
    def ELEMENTAL_SUPPORT_CENTER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ELEMENTAL_SUPPORT_CENTER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GAME_LIFT_CONTAINER_FLEET_POLICY")
    def GAME_LIFT_CONTAINER_FLEET_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GAME_LIFT_CONTAINER_FLEET_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GAME_LIFT_GAME_SERVER_GROUP_POLICY")
    def GAME_LIFT_GAME_SERVER_GROUP_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GAME_LIFT_GAME_SERVER_GROUP_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GLOBAL_ACCELERATOR_FULL_ACCESS")
    def GLOBAL_ACCELERATOR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GLOBAL_ACCELERATOR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GLOBAL_ACCELERATOR_READ_ONLY_ACCESS")
    def GLOBAL_ACCELERATOR_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GLOBAL_ACCELERATOR_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GROUND_TRUTH_SYNTHETIC_CONSOLE_FULL_ACCESS")
    def GROUND_TRUTH_SYNTHETIC_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GROUND_TRUTH_SYNTHETIC_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GROUND_TRUTH_SYNTHETIC_CONSOLE_READ_ONLY_ACCESS")
    def GROUND_TRUTH_SYNTHETIC_CONSOLE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GROUND_TRUTH_SYNTHETIC_CONSOLE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IAM_ACCESS_ADVISOR_READ_ONLY")
    def IAM_ACCESS_ADVISOR_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IAM_ACCESS_ADVISOR_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IAM_ACCESS_ANALYZER_FULL_ACCESS")
    def IAM_ACCESS_ANALYZER_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IAM_ACCESS_ANALYZER_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IAM_ACCESS_ANALYZER_READ_ONLY_ACCESS")
    def IAM_ACCESS_ANALYZER_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IAM_ACCESS_ANALYZER_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IAM_FULL_ACCESS")
    def IAM_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IAM_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IAM_READ_ONLY_ACCESS")
    def IAM_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IAM_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IAM_SELF_MANAGE_SERVICE_SPECIFIC_CREDENTIALS")
    def IAM_SELF_MANAGE_SERVICE_SPECIFIC_CREDENTIALS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IAM_SELF_MANAGE_SERVICE_SPECIFIC_CREDENTIALS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IAM_USER_CHANGE_PASSWORD")
    def IAM_USER_CHANGE_PASSWORD(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IAM_USER_CHANGE_PASSWORD"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IAM_USER_SSH_KEYS")
    def IAM_USER_SSH_KEYS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IAM_USER_SSH_KEYS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IVS_FULL_ACCESS")
    def IVS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IVS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IVS_READ_ONLY_ACCESS")
    def IVS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IVS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MEDIA_CONNECT_GATEWAY_INSTANCE_ROLE_POLICY")
    def MEDIA_CONNECT_GATEWAY_INSTANCE_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "MEDIA_CONNECT_GATEWAY_INSTANCE_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="NEPTUNE_CONSOLE_FULL_ACCESS")
    def NEPTUNE_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "NEPTUNE_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="NEPTUNE_FULL_ACCESS")
    def NEPTUNE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "NEPTUNE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="NEPTUNE_GRAPH_READ_ONLY_ACCESS")
    def NEPTUNE_GRAPH_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "NEPTUNE_GRAPH_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="NEPTUNE_READ_ONLY_ACCESS")
    def NEPTUNE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "NEPTUNE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="OAM_FULL_ACCESS")
    def OAM_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "OAM_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="OAM_READ_ONLY_ACCESS")
    def OAM_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "OAM_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PARTNER_CENTRAL_ACCOUNT_MANAGEMENT_USER_ROLE_ASSOCIATION")
    def PARTNER_CENTRAL_ACCOUNT_MANAGEMENT_USER_ROLE_ASSOCIATION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PARTNER_CENTRAL_ACCOUNT_MANAGEMENT_USER_ROLE_ASSOCIATION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="POWER_USER_ACCESS")
    def POWER_USER_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "POWER_USER_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="Q_BUSINESS_QUICKSIGHT_PLUGIN_POLICY")
    def Q_BUSINESS_QUICKSIGHT_PLUGIN_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "Q_BUSINESS_QUICKSIGHT_PLUGIN_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="READ_ONLY_ACCESS")
    def READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="RESOURCE_GROUPS_AND_TAG_EDITOR_FULL_ACCESS")
    def RESOURCE_GROUPS_AND_TAG_EDITOR_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "RESOURCE_GROUPS_AND_TAG_EDITOR_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="RESOURCE_GROUPS_AND_TAG_EDITOR_READ_ONLY_ACCESS")
    def RESOURCE_GROUPS_AND_TAG_EDITOR_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "RESOURCE_GROUPS_AND_TAG_EDITOR_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="RESOURCE_GROUPS_TAGGING_API_TAG_UNTAG_SUPPORTED_RESOURCES")
    def RESOURCE_GROUPS_TAGGING_API_TAG_UNTAG_SUPPORTED_RESOURCES(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "RESOURCE_GROUPS_TAGGING_API_TAG_UNTAG_SUPPORTED_RESOURCES"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ROSA_MANAGE_SUBSCRIPTION")
    def ROSA_MANAGE_SUBSCRIPTION(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ROSA_MANAGE_SUBSCRIPTION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SAGE_MAKER_STUDIO_FULL_ACCESS")
    def SAGE_MAKER_STUDIO_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SAGE_MAKER_STUDIO_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SAGE_MAKER_STUDIO_PROJECT_ROLE_MACHINE_LEARNING_POLICY")
    def SAGE_MAKER_STUDIO_PROJECT_ROLE_MACHINE_LEARNING_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SAGE_MAKER_STUDIO_PROJECT_ROLE_MACHINE_LEARNING_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SAGE_MAKER_STUDIO_PROJECT_USER_ROLE_PERMISSIONS_BOUNDARY")
    def SAGE_MAKER_STUDIO_PROJECT_USER_ROLE_PERMISSIONS_BOUNDARY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SAGE_MAKER_STUDIO_PROJECT_USER_ROLE_PERMISSIONS_BOUNDARY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SAGE_MAKER_STUDIO_PROJECT_USER_ROLE_POLICY")
    def SAGE_MAKER_STUDIO_PROJECT_USER_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SAGE_MAKER_STUDIO_PROJECT_USER_ROLE_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SECRETS_MANAGER_READ_WRITE")
    def SECRETS_MANAGER_READ_WRITE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SECRETS_MANAGER_READ_WRITE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SECURITY_AUDIT")
    def SECURITY_AUDIT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SECURITY_AUDIT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SERVER_MIGRATION_CONNECTOR")
    def SERVER_MIGRATION_CONNECTOR(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SERVER_MIGRATION_CONNECTOR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SERVER_MIGRATION_SERVICE_CONSOLE_FULL_ACCESS")
    def SERVER_MIGRATION_SERVICE_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SERVER_MIGRATION_SERVICE_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SERVICE_QUOTAS_FULL_ACCESS")
    def SERVICE_QUOTAS_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SERVICE_QUOTAS_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SERVICE_QUOTAS_READ_ONLY_ACCESS")
    def SERVICE_QUOTAS_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SERVICE_QUOTAS_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="SIMPLE_WORKFLOW_FULL_ACCESS")
    def SIMPLE_WORKFLOW_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SIMPLE_WORKFLOW_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TRANSLATE_FULL_ACCESS")
    def TRANSLATE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "TRANSLATE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TRANSLATE_READ_ONLY")
    def TRANSLATE_READ_ONLY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "TRANSLATE_READ_ONLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="VPC_LATTICE_FULL_ACCESS")
    def VPC_LATTICE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "VPC_LATTICE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="VPC_LATTICE_READ_ONLY_ACCESS")
    def VPC_LATTICE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "VPC_LATTICE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="VPC_LATTICE_SERVICES_INVOKE_ACCESS")
    def VPC_LATTICE_SERVICES_INVOKE_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "VPC_LATTICE_SERVICES_INVOKE_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="WELL_ARCHITECTED_CONSOLE_FULL_ACCESS")
    def WELL_ARCHITECTED_CONSOLE_FULL_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "WELL_ARCHITECTED_CONSOLE_FULL_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="WELL_ARCHITECTED_CONSOLE_READ_ONLY_ACCESS")
    def WELL_ARCHITECTED_CONSOLE_READ_ONLY_ACCESS(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "WELL_ARCHITECTED_CONSOLE_READ_ONLY_ACCESS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="WORK_LINK_SERVICE_ROLE_POLICY")
    def WORK_LINK_SERVICE_ROLE_POLICY(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "WORK_LINK_SERVICE_ROLE_POLICY"))


@jsii.enum(jsii_type="@cdklabs/cdk-proserve-lib.types.DestructiveOperation")
class DestructiveOperation(enum.Enum):
    '''(experimental) Represents types of destructive operations that can be performed on resources.

    Destructive operations are actions that modify or remove existing resources,
    potentially resulting in data loss if not handled properly.

    :stability: experimental
    '''

    UPDATE = "UPDATE"
    '''(experimental) Indicates an operation that modifies existing resources.

    :stability: experimental
    '''
    DELETE = "DELETE"
    '''(experimental) Indicates an operation that removes resources.

    :stability: experimental
    '''
    ALL = "ALL"
    '''(experimental) Represents all types of destructive operations.

    :stability: experimental
    '''


class Ec2InstanceType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.types.Ec2InstanceType",
):
    '''(experimental) EC2 Instance Type.

    :stability: experimental
    '''

    @jsii.python.classproperty
    @jsii.member(jsii_name="A1_2XLARGE")
    def A1_2_XLARGE(cls) -> builtins.str:
        '''(experimental) a1.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "A1_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="A1_4XLARGE")
    def A1_4_XLARGE(cls) -> builtins.str:
        '''(experimental) a1.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "A1_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="A1_LARGE")
    def A1_LARGE(cls) -> builtins.str:
        '''(experimental) a1.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "A1_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="A1_MEDIUM")
    def A1_MEDIUM(cls) -> builtins.str:
        '''(experimental) a1.medium vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "A1_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="A1_METAL")
    def A1_METAL(cls) -> builtins.str:
        '''(experimental) a1.metal vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "A1_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="A1_XLARGE")
    def A1_XLARGE(cls) -> builtins.str:
        '''(experimental) a1.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "A1_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C1_MEDIUM")
    def C1_MEDIUM(cls) -> builtins.str:
        '''(experimental) c1.medium vCPUs: 2 Memory: 1740 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C1_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C1_XLARGE")
    def C1_XLARGE(cls) -> builtins.str:
        '''(experimental) c1.xlarge vCPUs: 8 Memory: 7168 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C1_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C3_2XLARGE")
    def C3_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c3.2xlarge vCPUs: 8 Memory: 15360 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C3_4XLARGE")
    def C3_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c3.4xlarge vCPUs: 16 Memory: 30720 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C3_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C3_8XLARGE")
    def C3_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c3.8xlarge vCPUs: 32 Memory: 61440 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C3_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C3_LARGE")
    def C3_LARGE(cls) -> builtins.str:
        '''(experimental) c3.large vCPUs: 2 Memory: 3840 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C3_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C3_XLARGE")
    def C3_XLARGE(cls) -> builtins.str:
        '''(experimental) c3.xlarge vCPUs: 4 Memory: 7680 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C3_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C4_2XLARGE")
    def C4_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c4.2xlarge vCPUs: 8 Memory: 15360 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C4_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C4_4XLARGE")
    def C4_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c4.4xlarge vCPUs: 16 Memory: 30720 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C4_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C4_8XLARGE")
    def C4_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c4.8xlarge vCPUs: 36 Memory: 61440 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C4_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C4_LARGE")
    def C4_LARGE(cls) -> builtins.str:
        '''(experimental) c4.large vCPUs: 2 Memory: 3840 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C4_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C4_XLARGE")
    def C4_XLARGE(cls) -> builtins.str:
        '''(experimental) c4.xlarge vCPUs: 4 Memory: 7680 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C4_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5_12XLARGE")
    def C5_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c5.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5_18XLARGE")
    def C5_18_XLARGE(cls) -> builtins.str:
        '''(experimental) c5.18xlarge vCPUs: 72 Memory: 147456 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5_18XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5_24XLARGE")
    def C5_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c5.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5_2XLARGE")
    def C5_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c5.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5_4XLARGE")
    def C5_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c5.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5_9XLARGE")
    def C5_9_XLARGE(cls) -> builtins.str:
        '''(experimental) c5.9xlarge vCPUs: 36 Memory: 73728 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5_9XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5_LARGE")
    def C5_LARGE(cls) -> builtins.str:
        '''(experimental) c5.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5_METAL")
    def C5_METAL(cls) -> builtins.str:
        '''(experimental) c5.metal vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5_XLARGE")
    def C5_XLARGE(cls) -> builtins.str:
        '''(experimental) c5.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5A_12XLARGE")
    def C5_A_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c5a.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5A_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5A_16XLARGE")
    def C5_A_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c5a.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5A_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5A_24XLARGE")
    def C5_A_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c5a.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5A_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5A_2XLARGE")
    def C5_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c5a.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5A_4XLARGE")
    def C5_A_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c5a.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5A_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5A_8XLARGE")
    def C5_A_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c5a.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5A_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5A_LARGE")
    def C5_A_LARGE(cls) -> builtins.str:
        '''(experimental) c5a.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5A_XLARGE")
    def C5_A_XLARGE(cls) -> builtins.str:
        '''(experimental) c5a.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5AD_12XLARGE")
    def C5_AD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c5ad.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5AD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5AD_16XLARGE")
    def C5_AD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c5ad.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5AD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5AD_24XLARGE")
    def C5_AD_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c5ad.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5AD_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5AD_2XLARGE")
    def C5_AD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c5ad.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5AD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5AD_4XLARGE")
    def C5_AD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c5ad.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5AD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5AD_8XLARGE")
    def C5_AD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c5ad.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5AD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5AD_LARGE")
    def C5_AD_LARGE(cls) -> builtins.str:
        '''(experimental) c5ad.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5AD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5AD_XLARGE")
    def C5_AD_XLARGE(cls) -> builtins.str:
        '''(experimental) c5ad.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5AD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5D_12XLARGE")
    def C5_D_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c5d.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5D_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5D_18XLARGE")
    def C5_D_18_XLARGE(cls) -> builtins.str:
        '''(experimental) c5d.18xlarge vCPUs: 72 Memory: 147456 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5D_18XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5D_24XLARGE")
    def C5_D_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c5d.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5D_2XLARGE")
    def C5_D_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c5d.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5D_4XLARGE")
    def C5_D_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c5d.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5D_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5D_9XLARGE")
    def C5_D_9_XLARGE(cls) -> builtins.str:
        '''(experimental) c5d.9xlarge vCPUs: 36 Memory: 73728 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5D_9XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5D_LARGE")
    def C5_D_LARGE(cls) -> builtins.str:
        '''(experimental) c5d.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5D_METAL")
    def C5_D_METAL(cls) -> builtins.str:
        '''(experimental) c5d.metal vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5D_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5D_XLARGE")
    def C5_D_XLARGE(cls) -> builtins.str:
        '''(experimental) c5d.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5D_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5N_18XLARGE")
    def C5_N_18_XLARGE(cls) -> builtins.str:
        '''(experimental) c5n.18xlarge vCPUs: 72 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5N_18XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5N_2XLARGE")
    def C5_N_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c5n.2xlarge vCPUs: 8 Memory: 21504 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5N_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5N_4XLARGE")
    def C5_N_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c5n.4xlarge vCPUs: 16 Memory: 43008 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5N_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5N_9XLARGE")
    def C5_N_9_XLARGE(cls) -> builtins.str:
        '''(experimental) c5n.9xlarge vCPUs: 36 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5N_9XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5N_LARGE")
    def C5_N_LARGE(cls) -> builtins.str:
        '''(experimental) c5n.large vCPUs: 2 Memory: 5376 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5N_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5N_METAL")
    def C5_N_METAL(cls) -> builtins.str:
        '''(experimental) c5n.metal vCPUs: 72 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5N_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C5N_XLARGE")
    def C5_N_XLARGE(cls) -> builtins.str:
        '''(experimental) c5n.xlarge vCPUs: 4 Memory: 10752 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C5N_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_12XLARGE")
    def C6_A_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c6a.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_16XLARGE")
    def C6_A_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c6a.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_24XLARGE")
    def C6_A_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c6a.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_2XLARGE")
    def C6_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c6a.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_32XLARGE")
    def C6_A_32_XLARGE(cls) -> builtins.str:
        '''(experimental) c6a.32xlarge vCPUs: 128 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_48XLARGE")
    def C6_A_48_XLARGE(cls) -> builtins.str:
        '''(experimental) c6a.48xlarge vCPUs: 192 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_4XLARGE")
    def C6_A_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c6a.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_8XLARGE")
    def C6_A_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c6a.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_LARGE")
    def C6_A_LARGE(cls) -> builtins.str:
        '''(experimental) c6a.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_METAL")
    def C6_A_METAL(cls) -> builtins.str:
        '''(experimental) c6a.metal vCPUs: 192 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6A_XLARGE")
    def C6_A_XLARGE(cls) -> builtins.str:
        '''(experimental) c6a.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6G_12XLARGE")
    def C6_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c6g.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6G_16XLARGE")
    def C6_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c6g.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6G_2XLARGE")
    def C6_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c6g.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6G_4XLARGE")
    def C6_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c6g.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6G_8XLARGE")
    def C6_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c6g.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6G_LARGE")
    def C6_G_LARGE(cls) -> builtins.str:
        '''(experimental) c6g.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6G_MEDIUM")
    def C6_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) c6g.medium vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6G_METAL")
    def C6_G_METAL(cls) -> builtins.str:
        '''(experimental) c6g.metal vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6G_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6G_XLARGE")
    def C6_G_XLARGE(cls) -> builtins.str:
        '''(experimental) c6g.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GD_12XLARGE")
    def C6_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gd.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GD_16XLARGE")
    def C6_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gd.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GD_2XLARGE")
    def C6_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gd.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GD_4XLARGE")
    def C6_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gd.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GD_8XLARGE")
    def C6_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gd.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GD_LARGE")
    def C6_GD_LARGE(cls) -> builtins.str:
        '''(experimental) c6gd.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GD_MEDIUM")
    def C6_GD_MEDIUM(cls) -> builtins.str:
        '''(experimental) c6gd.medium vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GD_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GD_METAL")
    def C6_GD_METAL(cls) -> builtins.str:
        '''(experimental) c6gd.metal vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GD_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GD_XLARGE")
    def C6_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gd.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GN_12XLARGE")
    def C6_GN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gn.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GN_16XLARGE")
    def C6_GN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gn.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GN_2XLARGE")
    def C6_GN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gn.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GN_4XLARGE")
    def C6_GN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gn.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GN_8XLARGE")
    def C6_GN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gn.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GN_LARGE")
    def C6_GN_LARGE(cls) -> builtins.str:
        '''(experimental) c6gn.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GN_MEDIUM")
    def C6_GN_MEDIUM(cls) -> builtins.str:
        '''(experimental) c6gn.medium vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GN_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6GN_XLARGE")
    def C6_GN_XLARGE(cls) -> builtins.str:
        '''(experimental) c6gn.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6GN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_12XLARGE")
    def C6_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c6i.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_16XLARGE")
    def C6_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c6i.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_24XLARGE")
    def C6_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c6i.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_2XLARGE")
    def C6_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c6i.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_32XLARGE")
    def C6_I_32_XLARGE(cls) -> builtins.str:
        '''(experimental) c6i.32xlarge vCPUs: 128 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_4XLARGE")
    def C6_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c6i.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_8XLARGE")
    def C6_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c6i.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_LARGE")
    def C6_I_LARGE(cls) -> builtins.str:
        '''(experimental) c6i.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_METAL")
    def C6_I_METAL(cls) -> builtins.str:
        '''(experimental) c6i.metal vCPUs: 128 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6I_XLARGE")
    def C6_I_XLARGE(cls) -> builtins.str:
        '''(experimental) c6i.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_12XLARGE")
    def C6_ID_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c6id.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_16XLARGE")
    def C6_ID_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c6id.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_24XLARGE")
    def C6_ID_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c6id.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_2XLARGE")
    def C6_ID_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c6id.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_32XLARGE")
    def C6_ID_32_XLARGE(cls) -> builtins.str:
        '''(experimental) c6id.32xlarge vCPUs: 128 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_4XLARGE")
    def C6_ID_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c6id.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_8XLARGE")
    def C6_ID_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c6id.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_LARGE")
    def C6_ID_LARGE(cls) -> builtins.str:
        '''(experimental) c6id.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_METAL")
    def C6_ID_METAL(cls) -> builtins.str:
        '''(experimental) c6id.metal vCPUs: 128 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6ID_XLARGE")
    def C6_ID_XLARGE(cls) -> builtins.str:
        '''(experimental) c6id.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6ID_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_12XLARGE")
    def C6_IN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c6in.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_16XLARGE")
    def C6_IN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c6in.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_24XLARGE")
    def C6_IN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c6in.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_2XLARGE")
    def C6_IN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c6in.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_32XLARGE")
    def C6_IN_32_XLARGE(cls) -> builtins.str:
        '''(experimental) c6in.32xlarge vCPUs: 128 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_4XLARGE")
    def C6_IN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c6in.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_8XLARGE")
    def C6_IN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c6in.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_LARGE")
    def C6_IN_LARGE(cls) -> builtins.str:
        '''(experimental) c6in.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_METAL")
    def C6_IN_METAL(cls) -> builtins.str:
        '''(experimental) c6in.metal vCPUs: 128 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C6IN_XLARGE")
    def C6_IN_XLARGE(cls) -> builtins.str:
        '''(experimental) c6in.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C6IN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_12XLARGE")
    def C7_A_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c7a.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_16XLARGE")
    def C7_A_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c7a.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_24XLARGE")
    def C7_A_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c7a.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_2XLARGE")
    def C7_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c7a.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_32XLARGE")
    def C7_A_32_XLARGE(cls) -> builtins.str:
        '''(experimental) c7a.32xlarge vCPUs: 128 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_48XLARGE")
    def C7_A_48_XLARGE(cls) -> builtins.str:
        '''(experimental) c7a.48xlarge vCPUs: 192 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_4XLARGE")
    def C7_A_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c7a.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_8XLARGE")
    def C7_A_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c7a.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_LARGE")
    def C7_A_LARGE(cls) -> builtins.str:
        '''(experimental) c7a.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_MEDIUM")
    def C7_A_MEDIUM(cls) -> builtins.str:
        '''(experimental) c7a.medium vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_METAL_48XL")
    def C7_A_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) c7a.metal-48xl vCPUs: 192 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7A_XLARGE")
    def C7_A_XLARGE(cls) -> builtins.str:
        '''(experimental) c7a.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7G_12XLARGE")
    def C7_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c7g.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7G_16XLARGE")
    def C7_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c7g.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7G_2XLARGE")
    def C7_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c7g.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7G_4XLARGE")
    def C7_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c7g.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7G_8XLARGE")
    def C7_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c7g.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7G_LARGE")
    def C7_G_LARGE(cls) -> builtins.str:
        '''(experimental) c7g.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7G_MEDIUM")
    def C7_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) c7g.medium vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7G_METAL")
    def C7_G_METAL(cls) -> builtins.str:
        '''(experimental) c7g.metal vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7G_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7G_XLARGE")
    def C7_G_XLARGE(cls) -> builtins.str:
        '''(experimental) c7g.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GD_12XLARGE")
    def C7_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gd.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GD_16XLARGE")
    def C7_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gd.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GD_2XLARGE")
    def C7_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gd.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GD_4XLARGE")
    def C7_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gd.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GD_8XLARGE")
    def C7_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gd.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GD_LARGE")
    def C7_GD_LARGE(cls) -> builtins.str:
        '''(experimental) c7gd.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GD_MEDIUM")
    def C7_GD_MEDIUM(cls) -> builtins.str:
        '''(experimental) c7gd.medium vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GD_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GD_METAL")
    def C7_GD_METAL(cls) -> builtins.str:
        '''(experimental) c7gd.metal vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GD_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GD_XLARGE")
    def C7_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gd.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GN_12XLARGE")
    def C7_GN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gn.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GN_16XLARGE")
    def C7_GN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gn.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GN_2XLARGE")
    def C7_GN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gn.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GN_4XLARGE")
    def C7_GN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gn.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GN_8XLARGE")
    def C7_GN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gn.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GN_LARGE")
    def C7_GN_LARGE(cls) -> builtins.str:
        '''(experimental) c7gn.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GN_MEDIUM")
    def C7_GN_MEDIUM(cls) -> builtins.str:
        '''(experimental) c7gn.medium vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GN_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GN_METAL")
    def C7_GN_METAL(cls) -> builtins.str:
        '''(experimental) c7gn.metal vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7GN_XLARGE")
    def C7_GN_XLARGE(cls) -> builtins.str:
        '''(experimental) c7gn.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7GN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_12XLARGE")
    def C7_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_16XLARGE")
    def C7_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_24XLARGE")
    def C7_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_2XLARGE")
    def C7_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_48XLARGE")
    def C7_I_48_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i.48xlarge vCPUs: 192 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_4XLARGE")
    def C7_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_8XLARGE")
    def C7_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_FLEX_12XLARGE")
    def C7_I_FLEX_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i-flex.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_FLEX_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_FLEX_16XLARGE")
    def C7_I_FLEX_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i-flex.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_FLEX_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_FLEX_2XLARGE")
    def C7_I_FLEX_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i-flex.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_FLEX_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_FLEX_4XLARGE")
    def C7_I_FLEX_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i-flex.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_FLEX_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_FLEX_8XLARGE")
    def C7_I_FLEX_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i-flex.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_FLEX_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_FLEX_LARGE")
    def C7_I_FLEX_LARGE(cls) -> builtins.str:
        '''(experimental) c7i-flex.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_FLEX_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_FLEX_XLARGE")
    def C7_I_FLEX_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i-flex.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_FLEX_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_LARGE")
    def C7_I_LARGE(cls) -> builtins.str:
        '''(experimental) c7i.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_METAL_24XL")
    def C7_I_METAL_24_XL(cls) -> builtins.str:
        '''(experimental) c7i.metal-24xl vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_METAL_24XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_METAL_48XL")
    def C7_I_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) c7i.metal-48xl vCPUs: 192 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C7I_XLARGE")
    def C7_I_XLARGE(cls) -> builtins.str:
        '''(experimental) c7i.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C7I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_12XLARGE")
    def C8_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) c8g.12xlarge vCPUs: 48 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_16XLARGE")
    def C8_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) c8g.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_24XLARGE")
    def C8_G_24_XLARGE(cls) -> builtins.str:
        '''(experimental) c8g.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_2XLARGE")
    def C8_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) c8g.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_48XLARGE")
    def C8_G_48_XLARGE(cls) -> builtins.str:
        '''(experimental) c8g.48xlarge vCPUs: 192 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_4XLARGE")
    def C8_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) c8g.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_8XLARGE")
    def C8_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) c8g.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_LARGE")
    def C8_G_LARGE(cls) -> builtins.str:
        '''(experimental) c8g.large vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_MEDIUM")
    def C8_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) c8g.medium vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_METAL_24XL")
    def C8_G_METAL_24_XL(cls) -> builtins.str:
        '''(experimental) c8g.metal-24xl vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_METAL_24XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_METAL_48XL")
    def C8_G_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) c8g.metal-48xl vCPUs: 192 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="C8G_XLARGE")
    def C8_G_XLARGE(cls) -> builtins.str:
        '''(experimental) c8g.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "C8G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D2_2XLARGE")
    def D2_2_XLARGE(cls) -> builtins.str:
        '''(experimental) d2.2xlarge vCPUs: 8 Memory: 62464 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D2_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D2_4XLARGE")
    def D2_4_XLARGE(cls) -> builtins.str:
        '''(experimental) d2.4xlarge vCPUs: 16 Memory: 124928 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D2_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D2_8XLARGE")
    def D2_8_XLARGE(cls) -> builtins.str:
        '''(experimental) d2.8xlarge vCPUs: 36 Memory: 249856 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D2_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D2_XLARGE")
    def D2_XLARGE(cls) -> builtins.str:
        '''(experimental) d2.xlarge vCPUs: 4 Memory: 31232 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3_2XLARGE")
    def D3_2_XLARGE(cls) -> builtins.str:
        '''(experimental) d3.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3_4XLARGE")
    def D3_4_XLARGE(cls) -> builtins.str:
        '''(experimental) d3.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3_8XLARGE")
    def D3_8_XLARGE(cls) -> builtins.str:
        '''(experimental) d3.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3_XLARGE")
    def D3_XLARGE(cls) -> builtins.str:
        '''(experimental) d3.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3EN_12XLARGE")
    def D3_EN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) d3en.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3EN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3EN_2XLARGE")
    def D3_EN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) d3en.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3EN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3EN_4XLARGE")
    def D3_EN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) d3en.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3EN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3EN_6XLARGE")
    def D3_EN_6_XLARGE(cls) -> builtins.str:
        '''(experimental) d3en.6xlarge vCPUs: 24 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3EN_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3EN_8XLARGE")
    def D3_EN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) d3en.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3EN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="D3EN_XLARGE")
    def D3_EN_XLARGE(cls) -> builtins.str:
        '''(experimental) d3en.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "D3EN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DL1_24XLARGE")
    def DL1_24_XLARGE(cls) -> builtins.str:
        '''(experimental) dl1.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DL1_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="F1_16XLARGE")
    def F1_16_XLARGE(cls) -> builtins.str:
        '''(experimental) f1.16xlarge vCPUs: 64 Memory: 999424 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "F1_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="F1_2XLARGE")
    def F1_2_XLARGE(cls) -> builtins.str:
        '''(experimental) f1.2xlarge vCPUs: 8 Memory: 124928 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "F1_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="F1_4XLARGE")
    def F1_4_XLARGE(cls) -> builtins.str:
        '''(experimental) f1.4xlarge vCPUs: 16 Memory: 249856 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "F1_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="F2_12XLARGE")
    def F2_12_XLARGE(cls) -> builtins.str:
        '''(experimental) f2.12xlarge vCPUs: 48 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "F2_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="F2_48XLARGE")
    def F2_48_XLARGE(cls) -> builtins.str:
        '''(experimental) f2.48xlarge vCPUs: 192 Memory: 2097152 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "F2_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="F2_6XLARGE")
    def F2_6_XLARGE(cls) -> builtins.str:
        '''(experimental) f2.6xlarge vCPUs: 24 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "F2_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4AD_16XLARGE")
    def G4_AD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) g4ad.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4AD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4AD_2XLARGE")
    def G4_AD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) g4ad.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4AD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4AD_4XLARGE")
    def G4_AD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) g4ad.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4AD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4AD_8XLARGE")
    def G4_AD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) g4ad.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4AD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4AD_XLARGE")
    def G4_AD_XLARGE(cls) -> builtins.str:
        '''(experimental) g4ad.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4AD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4DN_12XLARGE")
    def G4_DN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) g4dn.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4DN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4DN_16XLARGE")
    def G4_DN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) g4dn.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4DN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4DN_2XLARGE")
    def G4_DN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) g4dn.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4DN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4DN_4XLARGE")
    def G4_DN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) g4dn.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4DN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4DN_8XLARGE")
    def G4_DN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) g4dn.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4DN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4DN_METAL")
    def G4_DN_METAL(cls) -> builtins.str:
        '''(experimental) g4dn.metal vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4DN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G4DN_XLARGE")
    def G4_DN_XLARGE(cls) -> builtins.str:
        '''(experimental) g4dn.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G4DN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5_12XLARGE")
    def G5_12_XLARGE(cls) -> builtins.str:
        '''(experimental) g5.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5_16XLARGE")
    def G5_16_XLARGE(cls) -> builtins.str:
        '''(experimental) g5.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5_24XLARGE")
    def G5_24_XLARGE(cls) -> builtins.str:
        '''(experimental) g5.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5_2XLARGE")
    def G5_2_XLARGE(cls) -> builtins.str:
        '''(experimental) g5.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5_48XLARGE")
    def G5_48_XLARGE(cls) -> builtins.str:
        '''(experimental) g5.48xlarge vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5_4XLARGE")
    def G5_4_XLARGE(cls) -> builtins.str:
        '''(experimental) g5.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5_8XLARGE")
    def G5_8_XLARGE(cls) -> builtins.str:
        '''(experimental) g5.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5_XLARGE")
    def G5_XLARGE(cls) -> builtins.str:
        '''(experimental) g5.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5G_16XLARGE")
    def G5_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) g5g.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5G_2XLARGE")
    def G5_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) g5g.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5G_4XLARGE")
    def G5_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) g5g.4xlarge vCPUs: 16 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5G_8XLARGE")
    def G5_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) g5g.8xlarge vCPUs: 32 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5G_METAL")
    def G5_G_METAL(cls) -> builtins.str:
        '''(experimental) g5g.metal vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5G_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G5G_XLARGE")
    def G5_G_XLARGE(cls) -> builtins.str:
        '''(experimental) g5g.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G5G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6_12XLARGE")
    def G6_12_XLARGE(cls) -> builtins.str:
        '''(experimental) g6.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6_16XLARGE")
    def G6_16_XLARGE(cls) -> builtins.str:
        '''(experimental) g6.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6_24XLARGE")
    def G6_24_XLARGE(cls) -> builtins.str:
        '''(experimental) g6.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6_2XLARGE")
    def G6_2_XLARGE(cls) -> builtins.str:
        '''(experimental) g6.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6_48XLARGE")
    def G6_48_XLARGE(cls) -> builtins.str:
        '''(experimental) g6.48xlarge vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6_4XLARGE")
    def G6_4_XLARGE(cls) -> builtins.str:
        '''(experimental) g6.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6_8XLARGE")
    def G6_8_XLARGE(cls) -> builtins.str:
        '''(experimental) g6.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6_XLARGE")
    def G6_XLARGE(cls) -> builtins.str:
        '''(experimental) g6.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6E_12XLARGE")
    def G6_E_12_XLARGE(cls) -> builtins.str:
        '''(experimental) g6e.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6E_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6E_16XLARGE")
    def G6_E_16_XLARGE(cls) -> builtins.str:
        '''(experimental) g6e.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6E_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6E_24XLARGE")
    def G6_E_24_XLARGE(cls) -> builtins.str:
        '''(experimental) g6e.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6E_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6E_2XLARGE")
    def G6_E_2_XLARGE(cls) -> builtins.str:
        '''(experimental) g6e.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6E_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6E_48XLARGE")
    def G6_E_48_XLARGE(cls) -> builtins.str:
        '''(experimental) g6e.48xlarge vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6E_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6E_4XLARGE")
    def G6_E_4_XLARGE(cls) -> builtins.str:
        '''(experimental) g6e.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6E_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6E_8XLARGE")
    def G6_E_8_XLARGE(cls) -> builtins.str:
        '''(experimental) g6e.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6E_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="G6E_XLARGE")
    def G6_E_XLARGE(cls) -> builtins.str:
        '''(experimental) g6e.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "G6E_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GR6_4XLARGE")
    def GR6_4_XLARGE(cls) -> builtins.str:
        '''(experimental) gr6.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GR6_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GR6_8XLARGE")
    def GR6_8_XLARGE(cls) -> builtins.str:
        '''(experimental) gr6.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GR6_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="H1_16XLARGE")
    def H1_16_XLARGE(cls) -> builtins.str:
        '''(experimental) h1.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "H1_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="H1_2XLARGE")
    def H1_2_XLARGE(cls) -> builtins.str:
        '''(experimental) h1.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "H1_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="H1_4XLARGE")
    def H1_4_XLARGE(cls) -> builtins.str:
        '''(experimental) h1.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "H1_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="H1_8XLARGE")
    def H1_8_XLARGE(cls) -> builtins.str:
        '''(experimental) h1.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "H1_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HPC7G_16XLARGE")
    def HPC7_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) hpc7g.16xlarge vCPUs: 64 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "HPC7G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HPC7G_4XLARGE")
    def HPC7_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) hpc7g.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "HPC7G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HPC7G_8XLARGE")
    def HPC7_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) hpc7g.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "HPC7G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I2_2XLARGE")
    def I2_2_XLARGE(cls) -> builtins.str:
        '''(experimental) i2.2xlarge vCPUs: 8 Memory: 62464 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I2_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I2_4XLARGE")
    def I2_4_XLARGE(cls) -> builtins.str:
        '''(experimental) i2.4xlarge vCPUs: 16 Memory: 124928 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I2_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I2_8XLARGE")
    def I2_8_XLARGE(cls) -> builtins.str:
        '''(experimental) i2.8xlarge vCPUs: 32 Memory: 249856 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I2_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I2_XLARGE")
    def I2_XLARGE(cls) -> builtins.str:
        '''(experimental) i2.xlarge vCPUs: 4 Memory: 31232 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3_16XLARGE")
    def I3_16_XLARGE(cls) -> builtins.str:
        '''(experimental) i3.16xlarge vCPUs: 64 Memory: 499712 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3_2XLARGE")
    def I3_2_XLARGE(cls) -> builtins.str:
        '''(experimental) i3.2xlarge vCPUs: 8 Memory: 62464 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3_4XLARGE")
    def I3_4_XLARGE(cls) -> builtins.str:
        '''(experimental) i3.4xlarge vCPUs: 16 Memory: 124928 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3_8XLARGE")
    def I3_8_XLARGE(cls) -> builtins.str:
        '''(experimental) i3.8xlarge vCPUs: 32 Memory: 249856 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3_LARGE")
    def I3_LARGE(cls) -> builtins.str:
        '''(experimental) i3.large vCPUs: 2 Memory: 15616 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3_METAL")
    def I3_METAL(cls) -> builtins.str:
        '''(experimental) i3.metal vCPUs: 72 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3_XLARGE")
    def I3_XLARGE(cls) -> builtins.str:
        '''(experimental) i3.xlarge vCPUs: 4 Memory: 31232 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3EN_12XLARGE")
    def I3_EN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) i3en.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3EN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3EN_24XLARGE")
    def I3_EN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) i3en.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3EN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3EN_2XLARGE")
    def I3_EN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) i3en.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3EN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3EN_3XLARGE")
    def I3_EN_3_XLARGE(cls) -> builtins.str:
        '''(experimental) i3en.3xlarge vCPUs: 12 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3EN_3XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3EN_6XLARGE")
    def I3_EN_6_XLARGE(cls) -> builtins.str:
        '''(experimental) i3en.6xlarge vCPUs: 24 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3EN_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3EN_LARGE")
    def I3_EN_LARGE(cls) -> builtins.str:
        '''(experimental) i3en.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3EN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3EN_METAL")
    def I3_EN_METAL(cls) -> builtins.str:
        '''(experimental) i3en.metal vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3EN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I3EN_XLARGE")
    def I3_EN_XLARGE(cls) -> builtins.str:
        '''(experimental) i3en.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I3EN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4G_16XLARGE")
    def I4_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) i4g.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4G_2XLARGE")
    def I4_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) i4g.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4G_4XLARGE")
    def I4_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) i4g.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4G_8XLARGE")
    def I4_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) i4g.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4G_LARGE")
    def I4_G_LARGE(cls) -> builtins.str:
        '''(experimental) i4g.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4G_XLARGE")
    def I4_G_XLARGE(cls) -> builtins.str:
        '''(experimental) i4g.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_12XLARGE")
    def I4_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) i4i.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_16XLARGE")
    def I4_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) i4i.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_24XLARGE")
    def I4_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) i4i.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_2XLARGE")
    def I4_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) i4i.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_32XLARGE")
    def I4_I_32_XLARGE(cls) -> builtins.str:
        '''(experimental) i4i.32xlarge vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_4XLARGE")
    def I4_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) i4i.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_8XLARGE")
    def I4_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) i4i.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_LARGE")
    def I4_I_LARGE(cls) -> builtins.str:
        '''(experimental) i4i.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_METAL")
    def I4_I_METAL(cls) -> builtins.str:
        '''(experimental) i4i.metal vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I4I_XLARGE")
    def I4_I_XLARGE(cls) -> builtins.str:
        '''(experimental) i4i.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I4I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I7IE_12XLARGE")
    def I7_IE_12_XLARGE(cls) -> builtins.str:
        '''(experimental) i7ie.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I7IE_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I7IE_18XLARGE")
    def I7_IE_18_XLARGE(cls) -> builtins.str:
        '''(experimental) i7ie.18xlarge vCPUs: 72 Memory: 589824 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I7IE_18XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I7IE_24XLARGE")
    def I7_IE_24_XLARGE(cls) -> builtins.str:
        '''(experimental) i7ie.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I7IE_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I7IE_2XLARGE")
    def I7_IE_2_XLARGE(cls) -> builtins.str:
        '''(experimental) i7ie.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I7IE_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I7IE_3XLARGE")
    def I7_IE_3_XLARGE(cls) -> builtins.str:
        '''(experimental) i7ie.3xlarge vCPUs: 12 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I7IE_3XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I7IE_48XLARGE")
    def I7_IE_48_XLARGE(cls) -> builtins.str:
        '''(experimental) i7ie.48xlarge vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I7IE_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I7IE_6XLARGE")
    def I7_IE_6_XLARGE(cls) -> builtins.str:
        '''(experimental) i7ie.6xlarge vCPUs: 24 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I7IE_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I7IE_LARGE")
    def I7_IE_LARGE(cls) -> builtins.str:
        '''(experimental) i7ie.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I7IE_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I7IE_XLARGE")
    def I7_IE_XLARGE(cls) -> builtins.str:
        '''(experimental) i7ie.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I7IE_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I8G_12XLARGE")
    def I8_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) i8g.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I8G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I8G_16XLARGE")
    def I8_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) i8g.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I8G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I8G_24XLARGE")
    def I8_G_24_XLARGE(cls) -> builtins.str:
        '''(experimental) i8g.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I8G_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I8G_2XLARGE")
    def I8_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) i8g.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I8G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I8G_4XLARGE")
    def I8_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) i8g.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I8G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I8G_8XLARGE")
    def I8_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) i8g.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I8G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I8G_LARGE")
    def I8_G_LARGE(cls) -> builtins.str:
        '''(experimental) i8g.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I8G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I8G_METAL_24XL")
    def I8_G_METAL_24_XL(cls) -> builtins.str:
        '''(experimental) i8g.metal-24xl vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I8G_METAL_24XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="I8G_XLARGE")
    def I8_G_XLARGE(cls) -> builtins.str:
        '''(experimental) i8g.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "I8G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IM4GN_16XLARGE")
    def IM4_GN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) im4gn.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IM4GN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IM4GN_2XLARGE")
    def IM4_GN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) im4gn.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IM4GN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IM4GN_4XLARGE")
    def IM4_GN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) im4gn.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IM4GN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IM4GN_8XLARGE")
    def IM4_GN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) im4gn.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IM4GN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IM4GN_LARGE")
    def IM4_GN_LARGE(cls) -> builtins.str:
        '''(experimental) im4gn.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IM4GN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IM4GN_XLARGE")
    def IM4_GN_XLARGE(cls) -> builtins.str:
        '''(experimental) im4gn.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IM4GN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="INF1_24XLARGE")
    def INF1_24_XLARGE(cls) -> builtins.str:
        '''(experimental) inf1.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "INF1_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="INF1_2XLARGE")
    def INF1_2_XLARGE(cls) -> builtins.str:
        '''(experimental) inf1.2xlarge vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "INF1_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="INF1_6XLARGE")
    def INF1_6_XLARGE(cls) -> builtins.str:
        '''(experimental) inf1.6xlarge vCPUs: 24 Memory: 49152 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "INF1_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="INF1_XLARGE")
    def INF1_XLARGE(cls) -> builtins.str:
        '''(experimental) inf1.xlarge vCPUs: 4 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "INF1_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="INF2_24XLARGE")
    def INF2_24_XLARGE(cls) -> builtins.str:
        '''(experimental) inf2.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "INF2_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="INF2_48XLARGE")
    def INF2_48_XLARGE(cls) -> builtins.str:
        '''(experimental) inf2.48xlarge vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "INF2_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="INF2_8XLARGE")
    def INF2_8_XLARGE(cls) -> builtins.str:
        '''(experimental) inf2.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "INF2_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="INF2_XLARGE")
    def INF2_XLARGE(cls) -> builtins.str:
        '''(experimental) inf2.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "INF2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IS4GEN_2XLARGE")
    def IS4_GEN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) is4gen.2xlarge vCPUs: 8 Memory: 49152 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IS4GEN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IS4GEN_4XLARGE")
    def IS4_GEN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) is4gen.4xlarge vCPUs: 16 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IS4GEN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IS4GEN_8XLARGE")
    def IS4_GEN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) is4gen.8xlarge vCPUs: 32 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IS4GEN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IS4GEN_LARGE")
    def IS4_GEN_LARGE(cls) -> builtins.str:
        '''(experimental) is4gen.large vCPUs: 2 Memory: 12288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IS4GEN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IS4GEN_MEDIUM")
    def IS4_GEN_MEDIUM(cls) -> builtins.str:
        '''(experimental) is4gen.medium vCPUs: 1 Memory: 6144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IS4GEN_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="IS4GEN_XLARGE")
    def IS4_GEN_XLARGE(cls) -> builtins.str:
        '''(experimental) is4gen.xlarge vCPUs: 4 Memory: 24576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "IS4GEN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M1_LARGE")
    def M1_LARGE(cls) -> builtins.str:
        '''(experimental) m1.large vCPUs: 2 Memory: 7680 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M1_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M1_MEDIUM")
    def M1_MEDIUM(cls) -> builtins.str:
        '''(experimental) m1.medium vCPUs: 1 Memory: 3788 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M1_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M1_SMALL")
    def M1_SMALL(cls) -> builtins.str:
        '''(experimental) m1.small vCPUs: 1 Memory: 1740 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M1_SMALL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M1_XLARGE")
    def M1_XLARGE(cls) -> builtins.str:
        '''(experimental) m1.xlarge vCPUs: 4 Memory: 15360 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M1_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M2_2XLARGE")
    def M2_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m2.2xlarge vCPUs: 4 Memory: 35020 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M2_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M2_4XLARGE")
    def M2_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m2.4xlarge vCPUs: 8 Memory: 70041 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M2_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M2_XLARGE")
    def M2_XLARGE(cls) -> builtins.str:
        '''(experimental) m2.xlarge vCPUs: 2 Memory: 17510 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M3_2XLARGE")
    def M3_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m3.2xlarge vCPUs: 8 Memory: 30720 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M3_LARGE")
    def M3_LARGE(cls) -> builtins.str:
        '''(experimental) m3.large vCPUs: 2 Memory: 7680 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M3_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M3_MEDIUM")
    def M3_MEDIUM(cls) -> builtins.str:
        '''(experimental) m3.medium vCPUs: 1 Memory: 3840 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M3_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M3_XLARGE")
    def M3_XLARGE(cls) -> builtins.str:
        '''(experimental) m3.xlarge vCPUs: 4 Memory: 15360 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M3_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M4_10XLARGE")
    def M4_10_XLARGE(cls) -> builtins.str:
        '''(experimental) m4.10xlarge vCPUs: 40 Memory: 163840 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M4_10XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M4_16XLARGE")
    def M4_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m4.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M4_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M4_2XLARGE")
    def M4_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m4.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M4_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M4_4XLARGE")
    def M4_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m4.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M4_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M4_LARGE")
    def M4_LARGE(cls) -> builtins.str:
        '''(experimental) m4.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M4_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M4_XLARGE")
    def M4_XLARGE(cls) -> builtins.str:
        '''(experimental) m4.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M4_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5_12XLARGE")
    def M5_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m5.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5_16XLARGE")
    def M5_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m5.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5_24XLARGE")
    def M5_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m5.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5_2XLARGE")
    def M5_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m5.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5_4XLARGE")
    def M5_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m5.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5_8XLARGE")
    def M5_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m5.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5_LARGE")
    def M5_LARGE(cls) -> builtins.str:
        '''(experimental) m5.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5_METAL")
    def M5_METAL(cls) -> builtins.str:
        '''(experimental) m5.metal vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5_XLARGE")
    def M5_XLARGE(cls) -> builtins.str:
        '''(experimental) m5.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5A_12XLARGE")
    def M5_A_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m5a.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5A_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5A_16XLARGE")
    def M5_A_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m5a.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5A_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5A_24XLARGE")
    def M5_A_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m5a.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5A_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5A_2XLARGE")
    def M5_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m5a.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5A_4XLARGE")
    def M5_A_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m5a.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5A_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5A_8XLARGE")
    def M5_A_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m5a.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5A_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5A_LARGE")
    def M5_A_LARGE(cls) -> builtins.str:
        '''(experimental) m5a.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5A_XLARGE")
    def M5_A_XLARGE(cls) -> builtins.str:
        '''(experimental) m5a.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5AD_12XLARGE")
    def M5_AD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m5ad.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5AD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5AD_16XLARGE")
    def M5_AD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m5ad.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5AD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5AD_24XLARGE")
    def M5_AD_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m5ad.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5AD_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5AD_2XLARGE")
    def M5_AD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m5ad.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5AD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5AD_4XLARGE")
    def M5_AD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m5ad.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5AD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5AD_8XLARGE")
    def M5_AD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m5ad.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5AD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5AD_LARGE")
    def M5_AD_LARGE(cls) -> builtins.str:
        '''(experimental) m5ad.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5AD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5AD_XLARGE")
    def M5_AD_XLARGE(cls) -> builtins.str:
        '''(experimental) m5ad.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5AD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5D_12XLARGE")
    def M5_D_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m5d.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5D_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5D_16XLARGE")
    def M5_D_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m5d.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5D_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5D_24XLARGE")
    def M5_D_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m5d.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5D_2XLARGE")
    def M5_D_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m5d.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5D_4XLARGE")
    def M5_D_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m5d.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5D_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5D_8XLARGE")
    def M5_D_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m5d.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5D_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5D_LARGE")
    def M5_D_LARGE(cls) -> builtins.str:
        '''(experimental) m5d.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5D_METAL")
    def M5_D_METAL(cls) -> builtins.str:
        '''(experimental) m5d.metal vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5D_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5D_XLARGE")
    def M5_D_XLARGE(cls) -> builtins.str:
        '''(experimental) m5d.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5D_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5DN_12XLARGE")
    def M5_DN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m5dn.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5DN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5DN_16XLARGE")
    def M5_DN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m5dn.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5DN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5DN_24XLARGE")
    def M5_DN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m5dn.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5DN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5DN_2XLARGE")
    def M5_DN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m5dn.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5DN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5DN_4XLARGE")
    def M5_DN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m5dn.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5DN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5DN_8XLARGE")
    def M5_DN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m5dn.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5DN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5DN_LARGE")
    def M5_DN_LARGE(cls) -> builtins.str:
        '''(experimental) m5dn.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5DN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5DN_METAL")
    def M5_DN_METAL(cls) -> builtins.str:
        '''(experimental) m5dn.metal vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5DN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5DN_XLARGE")
    def M5_DN_XLARGE(cls) -> builtins.str:
        '''(experimental) m5dn.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5DN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5N_12XLARGE")
    def M5_N_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m5n.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5N_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5N_16XLARGE")
    def M5_N_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m5n.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5N_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5N_24XLARGE")
    def M5_N_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m5n.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5N_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5N_2XLARGE")
    def M5_N_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m5n.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5N_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5N_4XLARGE")
    def M5_N_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m5n.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5N_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5N_8XLARGE")
    def M5_N_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m5n.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5N_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5N_LARGE")
    def M5_N_LARGE(cls) -> builtins.str:
        '''(experimental) m5n.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5N_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5N_METAL")
    def M5_N_METAL(cls) -> builtins.str:
        '''(experimental) m5n.metal vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5N_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5N_XLARGE")
    def M5_N_XLARGE(cls) -> builtins.str:
        '''(experimental) m5n.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5N_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5ZN_12XLARGE")
    def M5_ZN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m5zn.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5ZN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5ZN_2XLARGE")
    def M5_ZN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m5zn.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5ZN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5ZN_3XLARGE")
    def M5_ZN_3_XLARGE(cls) -> builtins.str:
        '''(experimental) m5zn.3xlarge vCPUs: 12 Memory: 49152 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5ZN_3XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5ZN_6XLARGE")
    def M5_ZN_6_XLARGE(cls) -> builtins.str:
        '''(experimental) m5zn.6xlarge vCPUs: 24 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5ZN_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5ZN_LARGE")
    def M5_ZN_LARGE(cls) -> builtins.str:
        '''(experimental) m5zn.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5ZN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5ZN_METAL")
    def M5_ZN_METAL(cls) -> builtins.str:
        '''(experimental) m5zn.metal vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5ZN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M5ZN_XLARGE")
    def M5_ZN_XLARGE(cls) -> builtins.str:
        '''(experimental) m5zn.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M5ZN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_12XLARGE")
    def M6_A_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m6a.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_16XLARGE")
    def M6_A_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m6a.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_24XLARGE")
    def M6_A_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m6a.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_2XLARGE")
    def M6_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m6a.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_32XLARGE")
    def M6_A_32_XLARGE(cls) -> builtins.str:
        '''(experimental) m6a.32xlarge vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_48XLARGE")
    def M6_A_48_XLARGE(cls) -> builtins.str:
        '''(experimental) m6a.48xlarge vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_4XLARGE")
    def M6_A_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m6a.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_8XLARGE")
    def M6_A_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m6a.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_LARGE")
    def M6_A_LARGE(cls) -> builtins.str:
        '''(experimental) m6a.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_METAL")
    def M6_A_METAL(cls) -> builtins.str:
        '''(experimental) m6a.metal vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6A_XLARGE")
    def M6_A_XLARGE(cls) -> builtins.str:
        '''(experimental) m6a.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6G_12XLARGE")
    def M6_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m6g.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6G_16XLARGE")
    def M6_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m6g.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6G_2XLARGE")
    def M6_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m6g.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6G_4XLARGE")
    def M6_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m6g.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6G_8XLARGE")
    def M6_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m6g.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6G_LARGE")
    def M6_G_LARGE(cls) -> builtins.str:
        '''(experimental) m6g.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6G_MEDIUM")
    def M6_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) m6g.medium vCPUs: 1 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6G_METAL")
    def M6_G_METAL(cls) -> builtins.str:
        '''(experimental) m6g.metal vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6G_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6G_XLARGE")
    def M6_G_XLARGE(cls) -> builtins.str:
        '''(experimental) m6g.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6GD_12XLARGE")
    def M6_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m6gd.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6GD_16XLARGE")
    def M6_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m6gd.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6GD_2XLARGE")
    def M6_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m6gd.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6GD_4XLARGE")
    def M6_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m6gd.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6GD_8XLARGE")
    def M6_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m6gd.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6GD_LARGE")
    def M6_GD_LARGE(cls) -> builtins.str:
        '''(experimental) m6gd.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6GD_MEDIUM")
    def M6_GD_MEDIUM(cls) -> builtins.str:
        '''(experimental) m6gd.medium vCPUs: 1 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6GD_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6GD_METAL")
    def M6_GD_METAL(cls) -> builtins.str:
        '''(experimental) m6gd.metal vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6GD_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6GD_XLARGE")
    def M6_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) m6gd.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_12XLARGE")
    def M6_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m6i.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_16XLARGE")
    def M6_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m6i.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_24XLARGE")
    def M6_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m6i.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_2XLARGE")
    def M6_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m6i.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_32XLARGE")
    def M6_I_32_XLARGE(cls) -> builtins.str:
        '''(experimental) m6i.32xlarge vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_4XLARGE")
    def M6_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m6i.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_8XLARGE")
    def M6_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m6i.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_LARGE")
    def M6_I_LARGE(cls) -> builtins.str:
        '''(experimental) m6i.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_METAL")
    def M6_I_METAL(cls) -> builtins.str:
        '''(experimental) m6i.metal vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6I_XLARGE")
    def M6_I_XLARGE(cls) -> builtins.str:
        '''(experimental) m6i.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_12XLARGE")
    def M6_ID_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m6id.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_16XLARGE")
    def M6_ID_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m6id.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_24XLARGE")
    def M6_ID_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m6id.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_2XLARGE")
    def M6_ID_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m6id.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_32XLARGE")
    def M6_ID_32_XLARGE(cls) -> builtins.str:
        '''(experimental) m6id.32xlarge vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_4XLARGE")
    def M6_ID_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m6id.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_8XLARGE")
    def M6_ID_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m6id.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_LARGE")
    def M6_ID_LARGE(cls) -> builtins.str:
        '''(experimental) m6id.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_METAL")
    def M6_ID_METAL(cls) -> builtins.str:
        '''(experimental) m6id.metal vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6ID_XLARGE")
    def M6_ID_XLARGE(cls) -> builtins.str:
        '''(experimental) m6id.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6ID_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_12XLARGE")
    def M6_IDN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m6idn.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_16XLARGE")
    def M6_IDN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m6idn.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_24XLARGE")
    def M6_IDN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m6idn.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_2XLARGE")
    def M6_IDN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m6idn.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_32XLARGE")
    def M6_IDN_32_XLARGE(cls) -> builtins.str:
        '''(experimental) m6idn.32xlarge vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_4XLARGE")
    def M6_IDN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m6idn.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_8XLARGE")
    def M6_IDN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m6idn.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_LARGE")
    def M6_IDN_LARGE(cls) -> builtins.str:
        '''(experimental) m6idn.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_METAL")
    def M6_IDN_METAL(cls) -> builtins.str:
        '''(experimental) m6idn.metal vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IDN_XLARGE")
    def M6_IDN_XLARGE(cls) -> builtins.str:
        '''(experimental) m6idn.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IDN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_12XLARGE")
    def M6_IN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m6in.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_16XLARGE")
    def M6_IN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m6in.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_24XLARGE")
    def M6_IN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m6in.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_2XLARGE")
    def M6_IN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m6in.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_32XLARGE")
    def M6_IN_32_XLARGE(cls) -> builtins.str:
        '''(experimental) m6in.32xlarge vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_4XLARGE")
    def M6_IN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m6in.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_8XLARGE")
    def M6_IN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m6in.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_LARGE")
    def M6_IN_LARGE(cls) -> builtins.str:
        '''(experimental) m6in.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_METAL")
    def M6_IN_METAL(cls) -> builtins.str:
        '''(experimental) m6in.metal vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M6IN_XLARGE")
    def M6_IN_XLARGE(cls) -> builtins.str:
        '''(experimental) m6in.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M6IN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_12XLARGE")
    def M7_A_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m7a.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_16XLARGE")
    def M7_A_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m7a.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_24XLARGE")
    def M7_A_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m7a.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_2XLARGE")
    def M7_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m7a.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_32XLARGE")
    def M7_A_32_XLARGE(cls) -> builtins.str:
        '''(experimental) m7a.32xlarge vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_48XLARGE")
    def M7_A_48_XLARGE(cls) -> builtins.str:
        '''(experimental) m7a.48xlarge vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_4XLARGE")
    def M7_A_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m7a.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_8XLARGE")
    def M7_A_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m7a.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_LARGE")
    def M7_A_LARGE(cls) -> builtins.str:
        '''(experimental) m7a.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_MEDIUM")
    def M7_A_MEDIUM(cls) -> builtins.str:
        '''(experimental) m7a.medium vCPUs: 1 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_METAL_48XL")
    def M7_A_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) m7a.metal-48xl vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7A_XLARGE")
    def M7_A_XLARGE(cls) -> builtins.str:
        '''(experimental) m7a.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7G_12XLARGE")
    def M7_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m7g.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7G_16XLARGE")
    def M7_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m7g.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7G_2XLARGE")
    def M7_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m7g.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7G_4XLARGE")
    def M7_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m7g.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7G_8XLARGE")
    def M7_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m7g.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7G_LARGE")
    def M7_G_LARGE(cls) -> builtins.str:
        '''(experimental) m7g.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7G_MEDIUM")
    def M7_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) m7g.medium vCPUs: 1 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7G_METAL")
    def M7_G_METAL(cls) -> builtins.str:
        '''(experimental) m7g.metal vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7G_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7G_XLARGE")
    def M7_G_XLARGE(cls) -> builtins.str:
        '''(experimental) m7g.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7GD_12XLARGE")
    def M7_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m7gd.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7GD_16XLARGE")
    def M7_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m7gd.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7GD_2XLARGE")
    def M7_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m7gd.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7GD_4XLARGE")
    def M7_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m7gd.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7GD_8XLARGE")
    def M7_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m7gd.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7GD_LARGE")
    def M7_GD_LARGE(cls) -> builtins.str:
        '''(experimental) m7gd.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7GD_MEDIUM")
    def M7_GD_MEDIUM(cls) -> builtins.str:
        '''(experimental) m7gd.medium vCPUs: 1 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7GD_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7GD_METAL")
    def M7_GD_METAL(cls) -> builtins.str:
        '''(experimental) m7gd.metal vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7GD_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7GD_XLARGE")
    def M7_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) m7gd.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_12XLARGE")
    def M7_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_16XLARGE")
    def M7_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_24XLARGE")
    def M7_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_2XLARGE")
    def M7_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_48XLARGE")
    def M7_I_48_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i.48xlarge vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_4XLARGE")
    def M7_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_8XLARGE")
    def M7_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_FLEX_12XLARGE")
    def M7_I_FLEX_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i-flex.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_FLEX_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_FLEX_16XLARGE")
    def M7_I_FLEX_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i-flex.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_FLEX_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_FLEX_2XLARGE")
    def M7_I_FLEX_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i-flex.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_FLEX_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_FLEX_4XLARGE")
    def M7_I_FLEX_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i-flex.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_FLEX_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_FLEX_8XLARGE")
    def M7_I_FLEX_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i-flex.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_FLEX_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_FLEX_LARGE")
    def M7_I_FLEX_LARGE(cls) -> builtins.str:
        '''(experimental) m7i-flex.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_FLEX_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_FLEX_XLARGE")
    def M7_I_FLEX_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i-flex.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_FLEX_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_LARGE")
    def M7_I_LARGE(cls) -> builtins.str:
        '''(experimental) m7i.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_METAL_24XL")
    def M7_I_METAL_24_XL(cls) -> builtins.str:
        '''(experimental) m7i.metal-24xl vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_METAL_24XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_METAL_48XL")
    def M7_I_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) m7i.metal-48xl vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M7I_XLARGE")
    def M7_I_XLARGE(cls) -> builtins.str:
        '''(experimental) m7i.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M7I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_12XLARGE")
    def M8_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) m8g.12xlarge vCPUs: 48 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_16XLARGE")
    def M8_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) m8g.16xlarge vCPUs: 64 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_24XLARGE")
    def M8_G_24_XLARGE(cls) -> builtins.str:
        '''(experimental) m8g.24xlarge vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_2XLARGE")
    def M8_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) m8g.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_48XLARGE")
    def M8_G_48_XLARGE(cls) -> builtins.str:
        '''(experimental) m8g.48xlarge vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_4XLARGE")
    def M8_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) m8g.4xlarge vCPUs: 16 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_8XLARGE")
    def M8_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) m8g.8xlarge vCPUs: 32 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_LARGE")
    def M8_G_LARGE(cls) -> builtins.str:
        '''(experimental) m8g.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_MEDIUM")
    def M8_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) m8g.medium vCPUs: 1 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_METAL_24XL")
    def M8_G_METAL_24_XL(cls) -> builtins.str:
        '''(experimental) m8g.metal-24xl vCPUs: 96 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_METAL_24XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_METAL_48XL")
    def M8_G_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) m8g.metal-48xl vCPUs: 192 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="M8G_XLARGE")
    def M8_G_XLARGE(cls) -> builtins.str:
        '''(experimental) m8g.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "M8G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MAC1_METAL")
    def MAC1_METAL(cls) -> builtins.str:
        '''(experimental) mac1.metal vCPUs: 12 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "MAC1_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MAC2_M1ULTRA_METAL")
    def MAC2_M1_ULTRA_METAL(cls) -> builtins.str:
        '''(experimental) mac2-m1ultra.metal vCPUs: 20 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "MAC2_M1ULTRA_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MAC2_M2_METAL")
    def MAC2_M2_METAL(cls) -> builtins.str:
        '''(experimental) mac2-m2.metal vCPUs: 8 Memory: 24576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "MAC2_M2_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MAC2_M2PRO_METAL")
    def MAC2_M2_PRO_METAL(cls) -> builtins.str:
        '''(experimental) mac2-m2pro.metal vCPUs: 12 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "MAC2_M2PRO_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MAC2_METAL")
    def MAC2_METAL(cls) -> builtins.str:
        '''(experimental) mac2.metal vCPUs: 8 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "MAC2_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="P2_16XLARGE")
    def P2_16_XLARGE(cls) -> builtins.str:
        '''(experimental) p2.16xlarge vCPUs: 64 Memory: 749568 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "P2_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="P2_8XLARGE")
    def P2_8_XLARGE(cls) -> builtins.str:
        '''(experimental) p2.8xlarge vCPUs: 32 Memory: 499712 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "P2_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="P2_XLARGE")
    def P2_XLARGE(cls) -> builtins.str:
        '''(experimental) p2.xlarge vCPUs: 4 Memory: 62464 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "P2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="P3_16XLARGE")
    def P3_16_XLARGE(cls) -> builtins.str:
        '''(experimental) p3.16xlarge vCPUs: 64 Memory: 499712 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "P3_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="P3_2XLARGE")
    def P3_2_XLARGE(cls) -> builtins.str:
        '''(experimental) p3.2xlarge vCPUs: 8 Memory: 62464 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "P3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="P3_8XLARGE")
    def P3_8_XLARGE(cls) -> builtins.str:
        '''(experimental) p3.8xlarge vCPUs: 32 Memory: 249856 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "P3_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="P3DN_24XLARGE")
    def P3_DN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) p3dn.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "P3DN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="P4D_24XLARGE")
    def P4_D_24_XLARGE(cls) -> builtins.str:
        '''(experimental) p4d.24xlarge vCPUs: 96 Memory: 1179648 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "P4D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="P5_48XLARGE")
    def P5_48_XLARGE(cls) -> builtins.str:
        '''(experimental) p5.48xlarge vCPUs: 192 Memory: 2097152 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "P5_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R3_2XLARGE")
    def R3_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r3.2xlarge vCPUs: 8 Memory: 62464 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R3_4XLARGE")
    def R3_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r3.4xlarge vCPUs: 16 Memory: 124928 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R3_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R3_8XLARGE")
    def R3_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r3.8xlarge vCPUs: 32 Memory: 249856 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R3_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R3_LARGE")
    def R3_LARGE(cls) -> builtins.str:
        '''(experimental) r3.large vCPUs: 2 Memory: 15360 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R3_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R3_XLARGE")
    def R3_XLARGE(cls) -> builtins.str:
        '''(experimental) r3.xlarge vCPUs: 4 Memory: 31232 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R3_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R4_16XLARGE")
    def R4_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r4.16xlarge vCPUs: 64 Memory: 499712 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R4_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R4_2XLARGE")
    def R4_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r4.2xlarge vCPUs: 8 Memory: 62464 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R4_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R4_4XLARGE")
    def R4_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r4.4xlarge vCPUs: 16 Memory: 124928 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R4_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R4_8XLARGE")
    def R4_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r4.8xlarge vCPUs: 32 Memory: 249856 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R4_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R4_LARGE")
    def R4_LARGE(cls) -> builtins.str:
        '''(experimental) r4.large vCPUs: 2 Memory: 15616 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R4_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R4_XLARGE")
    def R4_XLARGE(cls) -> builtins.str:
        '''(experimental) r4.xlarge vCPUs: 4 Memory: 31232 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R4_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5_12XLARGE")
    def R5_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r5.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5_16XLARGE")
    def R5_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r5.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5_24XLARGE")
    def R5_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r5.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5_2XLARGE")
    def R5_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r5.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5_4XLARGE")
    def R5_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r5.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5_8XLARGE")
    def R5_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r5.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5_LARGE")
    def R5_LARGE(cls) -> builtins.str:
        '''(experimental) r5.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5_METAL")
    def R5_METAL(cls) -> builtins.str:
        '''(experimental) r5.metal vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5_XLARGE")
    def R5_XLARGE(cls) -> builtins.str:
        '''(experimental) r5.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5A_12XLARGE")
    def R5_A_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r5a.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5A_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5A_16XLARGE")
    def R5_A_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r5a.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5A_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5A_24XLARGE")
    def R5_A_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r5a.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5A_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5A_2XLARGE")
    def R5_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r5a.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5A_4XLARGE")
    def R5_A_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r5a.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5A_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5A_8XLARGE")
    def R5_A_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r5a.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5A_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5A_LARGE")
    def R5_A_LARGE(cls) -> builtins.str:
        '''(experimental) r5a.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5A_XLARGE")
    def R5_A_XLARGE(cls) -> builtins.str:
        '''(experimental) r5a.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5AD_12XLARGE")
    def R5_AD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r5ad.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5AD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5AD_16XLARGE")
    def R5_AD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r5ad.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5AD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5AD_24XLARGE")
    def R5_AD_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r5ad.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5AD_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5AD_2XLARGE")
    def R5_AD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r5ad.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5AD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5AD_4XLARGE")
    def R5_AD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r5ad.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5AD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5AD_8XLARGE")
    def R5_AD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r5ad.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5AD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5AD_LARGE")
    def R5_AD_LARGE(cls) -> builtins.str:
        '''(experimental) r5ad.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5AD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5AD_XLARGE")
    def R5_AD_XLARGE(cls) -> builtins.str:
        '''(experimental) r5ad.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5AD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5B_12XLARGE")
    def R5_B_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r5b.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5B_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5B_16XLARGE")
    def R5_B_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r5b.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5B_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5B_24XLARGE")
    def R5_B_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r5b.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5B_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5B_2XLARGE")
    def R5_B_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r5b.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5B_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5B_4XLARGE")
    def R5_B_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r5b.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5B_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5B_8XLARGE")
    def R5_B_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r5b.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5B_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5B_LARGE")
    def R5_B_LARGE(cls) -> builtins.str:
        '''(experimental) r5b.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5B_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5B_METAL")
    def R5_B_METAL(cls) -> builtins.str:
        '''(experimental) r5b.metal vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5B_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5B_XLARGE")
    def R5_B_XLARGE(cls) -> builtins.str:
        '''(experimental) r5b.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5B_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5D_12XLARGE")
    def R5_D_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r5d.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5D_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5D_16XLARGE")
    def R5_D_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r5d.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5D_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5D_24XLARGE")
    def R5_D_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r5d.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5D_2XLARGE")
    def R5_D_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r5d.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5D_4XLARGE")
    def R5_D_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r5d.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5D_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5D_8XLARGE")
    def R5_D_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r5d.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5D_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5D_LARGE")
    def R5_D_LARGE(cls) -> builtins.str:
        '''(experimental) r5d.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5D_METAL")
    def R5_D_METAL(cls) -> builtins.str:
        '''(experimental) r5d.metal vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5D_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5D_XLARGE")
    def R5_D_XLARGE(cls) -> builtins.str:
        '''(experimental) r5d.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5D_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5DN_12XLARGE")
    def R5_DN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r5dn.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5DN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5DN_16XLARGE")
    def R5_DN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r5dn.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5DN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5DN_24XLARGE")
    def R5_DN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r5dn.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5DN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5DN_2XLARGE")
    def R5_DN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r5dn.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5DN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5DN_4XLARGE")
    def R5_DN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r5dn.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5DN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5DN_8XLARGE")
    def R5_DN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r5dn.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5DN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5DN_LARGE")
    def R5_DN_LARGE(cls) -> builtins.str:
        '''(experimental) r5dn.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5DN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5DN_METAL")
    def R5_DN_METAL(cls) -> builtins.str:
        '''(experimental) r5dn.metal vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5DN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5DN_XLARGE")
    def R5_DN_XLARGE(cls) -> builtins.str:
        '''(experimental) r5dn.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5DN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5N_12XLARGE")
    def R5_N_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r5n.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5N_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5N_16XLARGE")
    def R5_N_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r5n.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5N_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5N_24XLARGE")
    def R5_N_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r5n.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5N_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5N_2XLARGE")
    def R5_N_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r5n.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5N_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5N_4XLARGE")
    def R5_N_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r5n.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5N_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5N_8XLARGE")
    def R5_N_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r5n.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5N_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5N_LARGE")
    def R5_N_LARGE(cls) -> builtins.str:
        '''(experimental) r5n.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5N_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5N_METAL")
    def R5_N_METAL(cls) -> builtins.str:
        '''(experimental) r5n.metal vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5N_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R5N_XLARGE")
    def R5_N_XLARGE(cls) -> builtins.str:
        '''(experimental) r5n.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R5N_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_12XLARGE")
    def R6_A_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r6a.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_16XLARGE")
    def R6_A_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r6a.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_24XLARGE")
    def R6_A_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r6a.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_2XLARGE")
    def R6_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r6a.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_32XLARGE")
    def R6_A_32_XLARGE(cls) -> builtins.str:
        '''(experimental) r6a.32xlarge vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_48XLARGE")
    def R6_A_48_XLARGE(cls) -> builtins.str:
        '''(experimental) r6a.48xlarge vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_4XLARGE")
    def R6_A_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r6a.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_8XLARGE")
    def R6_A_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r6a.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_LARGE")
    def R6_A_LARGE(cls) -> builtins.str:
        '''(experimental) r6a.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_METAL")
    def R6_A_METAL(cls) -> builtins.str:
        '''(experimental) r6a.metal vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6A_XLARGE")
    def R6_A_XLARGE(cls) -> builtins.str:
        '''(experimental) r6a.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6G_12XLARGE")
    def R6_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r6g.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6G_16XLARGE")
    def R6_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r6g.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6G_2XLARGE")
    def R6_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r6g.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6G_4XLARGE")
    def R6_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r6g.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6G_8XLARGE")
    def R6_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r6g.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6G_LARGE")
    def R6_G_LARGE(cls) -> builtins.str:
        '''(experimental) r6g.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6G_MEDIUM")
    def R6_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) r6g.medium vCPUs: 1 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6G_METAL")
    def R6_G_METAL(cls) -> builtins.str:
        '''(experimental) r6g.metal vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6G_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6G_XLARGE")
    def R6_G_XLARGE(cls) -> builtins.str:
        '''(experimental) r6g.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6GD_12XLARGE")
    def R6_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r6gd.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6GD_16XLARGE")
    def R6_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r6gd.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6GD_2XLARGE")
    def R6_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r6gd.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6GD_4XLARGE")
    def R6_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r6gd.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6GD_8XLARGE")
    def R6_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r6gd.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6GD_LARGE")
    def R6_GD_LARGE(cls) -> builtins.str:
        '''(experimental) r6gd.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6GD_MEDIUM")
    def R6_GD_MEDIUM(cls) -> builtins.str:
        '''(experimental) r6gd.medium vCPUs: 1 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6GD_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6GD_METAL")
    def R6_GD_METAL(cls) -> builtins.str:
        '''(experimental) r6gd.metal vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6GD_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6GD_XLARGE")
    def R6_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) r6gd.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_12XLARGE")
    def R6_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r6i.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_16XLARGE")
    def R6_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r6i.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_24XLARGE")
    def R6_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r6i.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_2XLARGE")
    def R6_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r6i.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_32XLARGE")
    def R6_I_32_XLARGE(cls) -> builtins.str:
        '''(experimental) r6i.32xlarge vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_4XLARGE")
    def R6_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r6i.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_8XLARGE")
    def R6_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r6i.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_LARGE")
    def R6_I_LARGE(cls) -> builtins.str:
        '''(experimental) r6i.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_METAL")
    def R6_I_METAL(cls) -> builtins.str:
        '''(experimental) r6i.metal vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6I_XLARGE")
    def R6_I_XLARGE(cls) -> builtins.str:
        '''(experimental) r6i.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_12XLARGE")
    def R6_ID_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r6id.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_16XLARGE")
    def R6_ID_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r6id.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_24XLARGE")
    def R6_ID_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r6id.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_2XLARGE")
    def R6_ID_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r6id.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_32XLARGE")
    def R6_ID_32_XLARGE(cls) -> builtins.str:
        '''(experimental) r6id.32xlarge vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_4XLARGE")
    def R6_ID_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r6id.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_8XLARGE")
    def R6_ID_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r6id.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_LARGE")
    def R6_ID_LARGE(cls) -> builtins.str:
        '''(experimental) r6id.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_METAL")
    def R6_ID_METAL(cls) -> builtins.str:
        '''(experimental) r6id.metal vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6ID_XLARGE")
    def R6_ID_XLARGE(cls) -> builtins.str:
        '''(experimental) r6id.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6ID_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_12XLARGE")
    def R6_IDN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r6idn.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_16XLARGE")
    def R6_IDN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r6idn.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_24XLARGE")
    def R6_IDN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r6idn.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_2XLARGE")
    def R6_IDN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r6idn.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_32XLARGE")
    def R6_IDN_32_XLARGE(cls) -> builtins.str:
        '''(experimental) r6idn.32xlarge vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_4XLARGE")
    def R6_IDN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r6idn.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_8XLARGE")
    def R6_IDN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r6idn.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_LARGE")
    def R6_IDN_LARGE(cls) -> builtins.str:
        '''(experimental) r6idn.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_METAL")
    def R6_IDN_METAL(cls) -> builtins.str:
        '''(experimental) r6idn.metal vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IDN_XLARGE")
    def R6_IDN_XLARGE(cls) -> builtins.str:
        '''(experimental) r6idn.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IDN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_12XLARGE")
    def R6_IN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r6in.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_16XLARGE")
    def R6_IN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r6in.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_24XLARGE")
    def R6_IN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r6in.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_2XLARGE")
    def R6_IN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r6in.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_32XLARGE")
    def R6_IN_32_XLARGE(cls) -> builtins.str:
        '''(experimental) r6in.32xlarge vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_4XLARGE")
    def R6_IN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r6in.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_8XLARGE")
    def R6_IN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r6in.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_LARGE")
    def R6_IN_LARGE(cls) -> builtins.str:
        '''(experimental) r6in.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_METAL")
    def R6_IN_METAL(cls) -> builtins.str:
        '''(experimental) r6in.metal vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R6IN_XLARGE")
    def R6_IN_XLARGE(cls) -> builtins.str:
        '''(experimental) r6in.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R6IN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_12XLARGE")
    def R7_A_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r7a.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_16XLARGE")
    def R7_A_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r7a.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_24XLARGE")
    def R7_A_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r7a.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_2XLARGE")
    def R7_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r7a.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_32XLARGE")
    def R7_A_32_XLARGE(cls) -> builtins.str:
        '''(experimental) r7a.32xlarge vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_48XLARGE")
    def R7_A_48_XLARGE(cls) -> builtins.str:
        '''(experimental) r7a.48xlarge vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_4XLARGE")
    def R7_A_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r7a.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_8XLARGE")
    def R7_A_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r7a.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_LARGE")
    def R7_A_LARGE(cls) -> builtins.str:
        '''(experimental) r7a.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_MEDIUM")
    def R7_A_MEDIUM(cls) -> builtins.str:
        '''(experimental) r7a.medium vCPUs: 1 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_METAL_48XL")
    def R7_A_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) r7a.metal-48xl vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7A_XLARGE")
    def R7_A_XLARGE(cls) -> builtins.str:
        '''(experimental) r7a.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7G_12XLARGE")
    def R7_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r7g.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7G_16XLARGE")
    def R7_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r7g.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7G_2XLARGE")
    def R7_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r7g.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7G_4XLARGE")
    def R7_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r7g.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7G_8XLARGE")
    def R7_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r7g.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7G_LARGE")
    def R7_G_LARGE(cls) -> builtins.str:
        '''(experimental) r7g.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7G_MEDIUM")
    def R7_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) r7g.medium vCPUs: 1 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7G_METAL")
    def R7_G_METAL(cls) -> builtins.str:
        '''(experimental) r7g.metal vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7G_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7G_XLARGE")
    def R7_G_XLARGE(cls) -> builtins.str:
        '''(experimental) r7g.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7GD_12XLARGE")
    def R7_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r7gd.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7GD_16XLARGE")
    def R7_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r7gd.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7GD_2XLARGE")
    def R7_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r7gd.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7GD_4XLARGE")
    def R7_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r7gd.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7GD_8XLARGE")
    def R7_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r7gd.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7GD_LARGE")
    def R7_GD_LARGE(cls) -> builtins.str:
        '''(experimental) r7gd.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7GD_MEDIUM")
    def R7_GD_MEDIUM(cls) -> builtins.str:
        '''(experimental) r7gd.medium vCPUs: 1 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7GD_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7GD_METAL")
    def R7_GD_METAL(cls) -> builtins.str:
        '''(experimental) r7gd.metal vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7GD_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7GD_XLARGE")
    def R7_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) r7gd.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_12XLARGE")
    def R7_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r7i.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_16XLARGE")
    def R7_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r7i.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_24XLARGE")
    def R7_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r7i.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_2XLARGE")
    def R7_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r7i.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_48XLARGE")
    def R7_I_48_XLARGE(cls) -> builtins.str:
        '''(experimental) r7i.48xlarge vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_4XLARGE")
    def R7_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r7i.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_8XLARGE")
    def R7_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r7i.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_LARGE")
    def R7_I_LARGE(cls) -> builtins.str:
        '''(experimental) r7i.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_METAL_24XL")
    def R7_I_METAL_24_XL(cls) -> builtins.str:
        '''(experimental) r7i.metal-24xl vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_METAL_24XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_METAL_48XL")
    def R7_I_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) r7i.metal-48xl vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7I_XLARGE")
    def R7_I_XLARGE(cls) -> builtins.str:
        '''(experimental) r7i.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_12XLARGE")
    def R7_IZ_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r7iz.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_16XLARGE")
    def R7_IZ_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r7iz.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_2XLARGE")
    def R7_IZ_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r7iz.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_32XLARGE")
    def R7_IZ_32_XLARGE(cls) -> builtins.str:
        '''(experimental) r7iz.32xlarge vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_4XLARGE")
    def R7_IZ_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r7iz.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_8XLARGE")
    def R7_IZ_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r7iz.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_LARGE")
    def R7_IZ_LARGE(cls) -> builtins.str:
        '''(experimental) r7iz.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_METAL_16XL")
    def R7_IZ_METAL_16_XL(cls) -> builtins.str:
        '''(experimental) r7iz.metal-16xl vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_METAL_16XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_METAL_32XL")
    def R7_IZ_METAL_32_XL(cls) -> builtins.str:
        '''(experimental) r7iz.metal-32xl vCPUs: 128 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_METAL_32XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R7IZ_XLARGE")
    def R7_IZ_XLARGE(cls) -> builtins.str:
        '''(experimental) r7iz.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R7IZ_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_12XLARGE")
    def R8_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) r8g.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_16XLARGE")
    def R8_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) r8g.16xlarge vCPUs: 64 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_24XLARGE")
    def R8_G_24_XLARGE(cls) -> builtins.str:
        '''(experimental) r8g.24xlarge vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_2XLARGE")
    def R8_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) r8g.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_48XLARGE")
    def R8_G_48_XLARGE(cls) -> builtins.str:
        '''(experimental) r8g.48xlarge vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_4XLARGE")
    def R8_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) r8g.4xlarge vCPUs: 16 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_8XLARGE")
    def R8_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) r8g.8xlarge vCPUs: 32 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_LARGE")
    def R8_G_LARGE(cls) -> builtins.str:
        '''(experimental) r8g.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_MEDIUM")
    def R8_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) r8g.medium vCPUs: 1 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_METAL_24XL")
    def R8_G_METAL_24_XL(cls) -> builtins.str:
        '''(experimental) r8g.metal-24xl vCPUs: 96 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_METAL_24XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_METAL_48XL")
    def R8_G_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) r8g.metal-48xl vCPUs: 192 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="R8G_XLARGE")
    def R8_G_XLARGE(cls) -> builtins.str:
        '''(experimental) r8g.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "R8G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T1_MICRO")
    def T1_MICRO(cls) -> builtins.str:
        '''(experimental) t1.micro vCPUs: 1 Memory: 627 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T1_MICRO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T2_2XLARGE")
    def T2_2_XLARGE(cls) -> builtins.str:
        '''(experimental) t2.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T2_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T2_LARGE")
    def T2_LARGE(cls) -> builtins.str:
        '''(experimental) t2.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T2_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T2_MEDIUM")
    def T2_MEDIUM(cls) -> builtins.str:
        '''(experimental) t2.medium vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T2_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T2_MICRO")
    def T2_MICRO(cls) -> builtins.str:
        '''(experimental) t2.micro vCPUs: 1 Memory: 1024 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T2_MICRO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T2_NANO")
    def T2_NANO(cls) -> builtins.str:
        '''(experimental) t2.nano vCPUs: 1 Memory: 512 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T2_NANO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T2_SMALL")
    def T2_SMALL(cls) -> builtins.str:
        '''(experimental) t2.small vCPUs: 1 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T2_SMALL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T2_XLARGE")
    def T2_XLARGE(cls) -> builtins.str:
        '''(experimental) t2.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3_2XLARGE")
    def T3_2_XLARGE(cls) -> builtins.str:
        '''(experimental) t3.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3_LARGE")
    def T3_LARGE(cls) -> builtins.str:
        '''(experimental) t3.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3_MEDIUM")
    def T3_MEDIUM(cls) -> builtins.str:
        '''(experimental) t3.medium vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3_MICRO")
    def T3_MICRO(cls) -> builtins.str:
        '''(experimental) t3.micro vCPUs: 2 Memory: 1024 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3_MICRO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3_NANO")
    def T3_NANO(cls) -> builtins.str:
        '''(experimental) t3.nano vCPUs: 2 Memory: 512 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3_NANO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3_SMALL")
    def T3_SMALL(cls) -> builtins.str:
        '''(experimental) t3.small vCPUs: 2 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3_SMALL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3_XLARGE")
    def T3_XLARGE(cls) -> builtins.str:
        '''(experimental) t3.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3A_2XLARGE")
    def T3_A_2_XLARGE(cls) -> builtins.str:
        '''(experimental) t3a.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3A_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3A_LARGE")
    def T3_A_LARGE(cls) -> builtins.str:
        '''(experimental) t3a.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3A_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3A_MEDIUM")
    def T3_A_MEDIUM(cls) -> builtins.str:
        '''(experimental) t3a.medium vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3A_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3A_MICRO")
    def T3_A_MICRO(cls) -> builtins.str:
        '''(experimental) t3a.micro vCPUs: 2 Memory: 1024 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3A_MICRO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3A_NANO")
    def T3_A_NANO(cls) -> builtins.str:
        '''(experimental) t3a.nano vCPUs: 2 Memory: 512 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3A_NANO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3A_SMALL")
    def T3_A_SMALL(cls) -> builtins.str:
        '''(experimental) t3a.small vCPUs: 2 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3A_SMALL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T3A_XLARGE")
    def T3_A_XLARGE(cls) -> builtins.str:
        '''(experimental) t3a.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T3A_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T4G_2XLARGE")
    def T4_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) t4g.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T4G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T4G_LARGE")
    def T4_G_LARGE(cls) -> builtins.str:
        '''(experimental) t4g.large vCPUs: 2 Memory: 8192 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T4G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T4G_MEDIUM")
    def T4_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) t4g.medium vCPUs: 2 Memory: 4096 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T4G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T4G_MICRO")
    def T4_G_MICRO(cls) -> builtins.str:
        '''(experimental) t4g.micro vCPUs: 2 Memory: 1024 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T4G_MICRO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T4G_NANO")
    def T4_G_NANO(cls) -> builtins.str:
        '''(experimental) t4g.nano vCPUs: 2 Memory: 512 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T4G_NANO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T4G_SMALL")
    def T4_G_SMALL(cls) -> builtins.str:
        '''(experimental) t4g.small vCPUs: 2 Memory: 2048 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T4G_SMALL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="T4G_XLARGE")
    def T4_G_XLARGE(cls) -> builtins.str:
        '''(experimental) t4g.xlarge vCPUs: 4 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "T4G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TRN1_2XLARGE")
    def TRN1_2_XLARGE(cls) -> builtins.str:
        '''(experimental) trn1.2xlarge vCPUs: 8 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "TRN1_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TRN1_32XLARGE")
    def TRN1_32_XLARGE(cls) -> builtins.str:
        '''(experimental) trn1.32xlarge vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "TRN1_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TRN1N_32XLARGE")
    def TRN1_N_32_XLARGE(cls) -> builtins.str:
        '''(experimental) trn1n.32xlarge vCPUs: 128 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "TRN1N_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U_12TB1_112XLARGE")
    def U_12_TB1_112_XLARGE(cls) -> builtins.str:
        '''(experimental) u-12tb1.112xlarge vCPUs: 448 Memory: 12582912 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U_12TB1_112XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U_18TB1_112XLARGE")
    def U_18_TB1_112_XLARGE(cls) -> builtins.str:
        '''(experimental) u-18tb1.112xlarge vCPUs: 448 Memory: 18874368 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U_18TB1_112XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U_24TB1_112XLARGE")
    def U_24_TB1_112_XLARGE(cls) -> builtins.str:
        '''(experimental) u-24tb1.112xlarge vCPUs: 448 Memory: 25165824 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U_24TB1_112XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U_3TB1_56XLARGE")
    def U_3_TB1_56_XLARGE(cls) -> builtins.str:
        '''(experimental) u-3tb1.56xlarge vCPUs: 224 Memory: 3145728 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U_3TB1_56XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U_6TB1_112XLARGE")
    def U_6_TB1_112_XLARGE(cls) -> builtins.str:
        '''(experimental) u-6tb1.112xlarge vCPUs: 448 Memory: 6291456 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U_6TB1_112XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U_6TB1_56XLARGE")
    def U_6_TB1_56_XLARGE(cls) -> builtins.str:
        '''(experimental) u-6tb1.56xlarge vCPUs: 224 Memory: 6291456 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U_6TB1_56XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U_9TB1_112XLARGE")
    def U_9_TB1_112_XLARGE(cls) -> builtins.str:
        '''(experimental) u-9tb1.112xlarge vCPUs: 448 Memory: 9437184 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U_9TB1_112XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U7I_12TB_224XLARGE")
    def U7_I_12_TB_224_XLARGE(cls) -> builtins.str:
        '''(experimental) u7i-12tb.224xlarge vCPUs: 896 Memory: 12582912 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U7I_12TB_224XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U7I_6TB_112XLARGE")
    def U7_I_6_TB_112_XLARGE(cls) -> builtins.str:
        '''(experimental) u7i-6tb.112xlarge vCPUs: 448 Memory: 6291456 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U7I_6TB_112XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U7I_8TB_112XLARGE")
    def U7_I_8_TB_112_XLARGE(cls) -> builtins.str:
        '''(experimental) u7i-8tb.112xlarge vCPUs: 448 Memory: 8388608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U7I_8TB_112XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U7IN_16TB_224XLARGE")
    def U7_IN_16_TB_224_XLARGE(cls) -> builtins.str:
        '''(experimental) u7in-16tb.224xlarge vCPUs: 896 Memory: 16777216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U7IN_16TB_224XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U7IN_24TB_224XLARGE")
    def U7_IN_24_TB_224_XLARGE(cls) -> builtins.str:
        '''(experimental) u7in-24tb.224xlarge vCPUs: 896 Memory: 25165824 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U7IN_24TB_224XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="U7IN_32TB_224XLARGE")
    def U7_IN_32_TB_224_XLARGE(cls) -> builtins.str:
        '''(experimental) u7in-32tb.224xlarge vCPUs: 896 Memory: 33554432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "U7IN_32TB_224XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="VT1_24XLARGE")
    def VT1_24_XLARGE(cls) -> builtins.str:
        '''(experimental) vt1.24xlarge vCPUs: 96 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "VT1_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="VT1_3XLARGE")
    def VT1_3_XLARGE(cls) -> builtins.str:
        '''(experimental) vt1.3xlarge vCPUs: 12 Memory: 24576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "VT1_3XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="VT1_6XLARGE")
    def VT1_6_XLARGE(cls) -> builtins.str:
        '''(experimental) vt1.6xlarge vCPUs: 24 Memory: 49152 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "VT1_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X1_16XLARGE")
    def X1_16_XLARGE(cls) -> builtins.str:
        '''(experimental) x1.16xlarge vCPUs: 64 Memory: 999424 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X1_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X1_32XLARGE")
    def X1_32_XLARGE(cls) -> builtins.str:
        '''(experimental) x1.32xlarge vCPUs: 128 Memory: 1998848 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X1_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X1E_16XLARGE")
    def X1_E_16_XLARGE(cls) -> builtins.str:
        '''(experimental) x1e.16xlarge vCPUs: 64 Memory: 1998848 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X1E_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X1E_2XLARGE")
    def X1_E_2_XLARGE(cls) -> builtins.str:
        '''(experimental) x1e.2xlarge vCPUs: 8 Memory: 249856 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X1E_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X1E_32XLARGE")
    def X1_E_32_XLARGE(cls) -> builtins.str:
        '''(experimental) x1e.32xlarge vCPUs: 128 Memory: 3997696 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X1E_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X1E_4XLARGE")
    def X1_E_4_XLARGE(cls) -> builtins.str:
        '''(experimental) x1e.4xlarge vCPUs: 16 Memory: 499712 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X1E_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X1E_8XLARGE")
    def X1_E_8_XLARGE(cls) -> builtins.str:
        '''(experimental) x1e.8xlarge vCPUs: 32 Memory: 999424 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X1E_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X1E_XLARGE")
    def X1_E_XLARGE(cls) -> builtins.str:
        '''(experimental) x1e.xlarge vCPUs: 4 Memory: 124928 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X1E_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2GD_12XLARGE")
    def X2_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) x2gd.12xlarge vCPUs: 48 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2GD_16XLARGE")
    def X2_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) x2gd.16xlarge vCPUs: 64 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2GD_2XLARGE")
    def X2_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) x2gd.2xlarge vCPUs: 8 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2GD_4XLARGE")
    def X2_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) x2gd.4xlarge vCPUs: 16 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2GD_8XLARGE")
    def X2_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) x2gd.8xlarge vCPUs: 32 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2GD_LARGE")
    def X2_GD_LARGE(cls) -> builtins.str:
        '''(experimental) x2gd.large vCPUs: 2 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2GD_MEDIUM")
    def X2_GD_MEDIUM(cls) -> builtins.str:
        '''(experimental) x2gd.medium vCPUs: 1 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2GD_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2GD_METAL")
    def X2_GD_METAL(cls) -> builtins.str:
        '''(experimental) x2gd.metal vCPUs: 64 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2GD_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2GD_XLARGE")
    def X2_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) x2gd.xlarge vCPUs: 4 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IDN_16XLARGE")
    def X2_IDN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) x2idn.16xlarge vCPUs: 64 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IDN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IDN_24XLARGE")
    def X2_IDN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) x2idn.24xlarge vCPUs: 96 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IDN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IDN_32XLARGE")
    def X2_IDN_32_XLARGE(cls) -> builtins.str:
        '''(experimental) x2idn.32xlarge vCPUs: 128 Memory: 2097152 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IDN_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IDN_METAL")
    def X2_IDN_METAL(cls) -> builtins.str:
        '''(experimental) x2idn.metal vCPUs: 128 Memory: 2097152 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IDN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEDN_16XLARGE")
    def X2_IEDN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iedn.16xlarge vCPUs: 64 Memory: 2097152 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEDN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEDN_24XLARGE")
    def X2_IEDN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iedn.24xlarge vCPUs: 96 Memory: 3145728 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEDN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEDN_2XLARGE")
    def X2_IEDN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iedn.2xlarge vCPUs: 8 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEDN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEDN_32XLARGE")
    def X2_IEDN_32_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iedn.32xlarge vCPUs: 128 Memory: 4194304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEDN_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEDN_4XLARGE")
    def X2_IEDN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iedn.4xlarge vCPUs: 16 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEDN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEDN_8XLARGE")
    def X2_IEDN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iedn.8xlarge vCPUs: 32 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEDN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEDN_METAL")
    def X2_IEDN_METAL(cls) -> builtins.str:
        '''(experimental) x2iedn.metal vCPUs: 128 Memory: 4194304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEDN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEDN_XLARGE")
    def X2_IEDN_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iedn.xlarge vCPUs: 4 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEDN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEZN_12XLARGE")
    def X2_IEZN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iezn.12xlarge vCPUs: 48 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEZN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEZN_2XLARGE")
    def X2_IEZN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iezn.2xlarge vCPUs: 8 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEZN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEZN_4XLARGE")
    def X2_IEZN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iezn.4xlarge vCPUs: 16 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEZN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEZN_6XLARGE")
    def X2_IEZN_6_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iezn.6xlarge vCPUs: 24 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEZN_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEZN_8XLARGE")
    def X2_IEZN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) x2iezn.8xlarge vCPUs: 32 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEZN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X2IEZN_METAL")
    def X2_IEZN_METAL(cls) -> builtins.str:
        '''(experimental) x2iezn.metal vCPUs: 48 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X2IEZN_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_12XLARGE")
    def X8_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) x8g.12xlarge vCPUs: 48 Memory: 786432 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_16XLARGE")
    def X8_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) x8g.16xlarge vCPUs: 64 Memory: 1048576 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_24XLARGE")
    def X8_G_24_XLARGE(cls) -> builtins.str:
        '''(experimental) x8g.24xlarge vCPUs: 96 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_2XLARGE")
    def X8_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) x8g.2xlarge vCPUs: 8 Memory: 131072 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_48XLARGE")
    def X8_G_48_XLARGE(cls) -> builtins.str:
        '''(experimental) x8g.48xlarge vCPUs: 192 Memory: 3145728 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_4XLARGE")
    def X8_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) x8g.4xlarge vCPUs: 16 Memory: 262144 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_8XLARGE")
    def X8_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) x8g.8xlarge vCPUs: 32 Memory: 524288 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_LARGE")
    def X8_G_LARGE(cls) -> builtins.str:
        '''(experimental) x8g.large vCPUs: 2 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_MEDIUM")
    def X8_G_MEDIUM(cls) -> builtins.str:
        '''(experimental) x8g.medium vCPUs: 1 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_METAL_24XL")
    def X8_G_METAL_24_XL(cls) -> builtins.str:
        '''(experimental) x8g.metal-24xl vCPUs: 96 Memory: 1572864 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_METAL_24XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_METAL_48XL")
    def X8_G_METAL_48_XL(cls) -> builtins.str:
        '''(experimental) x8g.metal-48xl vCPUs: 192 Memory: 3145728 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_METAL_48XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="X8G_XLARGE")
    def X8_G_XLARGE(cls) -> builtins.str:
        '''(experimental) x8g.xlarge vCPUs: 4 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "X8G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="Z1D_12XLARGE")
    def Z1_D_12_XLARGE(cls) -> builtins.str:
        '''(experimental) z1d.12xlarge vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "Z1D_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="Z1D_2XLARGE")
    def Z1_D_2_XLARGE(cls) -> builtins.str:
        '''(experimental) z1d.2xlarge vCPUs: 8 Memory: 65536 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "Z1D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="Z1D_3XLARGE")
    def Z1_D_3_XLARGE(cls) -> builtins.str:
        '''(experimental) z1d.3xlarge vCPUs: 12 Memory: 98304 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "Z1D_3XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="Z1D_6XLARGE")
    def Z1_D_6_XLARGE(cls) -> builtins.str:
        '''(experimental) z1d.6xlarge vCPUs: 24 Memory: 196608 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "Z1D_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="Z1D_LARGE")
    def Z1_D_LARGE(cls) -> builtins.str:
        '''(experimental) z1d.large vCPUs: 2 Memory: 16384 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "Z1D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="Z1D_METAL")
    def Z1_D_METAL(cls) -> builtins.str:
        '''(experimental) z1d.metal vCPUs: 48 Memory: 393216 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "Z1D_METAL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="Z1D_XLARGE")
    def Z1_D_XLARGE(cls) -> builtins.str:
        '''(experimental) z1d.xlarge vCPUs: 4 Memory: 32768 MiB.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "Z1D_XLARGE"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.types.LambdaConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "dead_letter_queue": "deadLetterQueue",
        "log_group_retention": "logGroupRetention",
        "reserved_concurrent_executions": "reservedConcurrentExecutions",
        "security_groups": "securityGroups",
        "subnets": "subnets",
        "vpc": "vpc",
    },
)
class LambdaConfiguration:
    def __init__(
        self,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        log_group_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param dead_letter_queue: (experimental) Optional SQS queue to use as a dead letter queue.
        :param log_group_retention: (experimental) Optional retention period for the Lambda functions log group. Default: RetentionDays.ONE_MONTH
        :param reserved_concurrent_executions: (experimental) The number of concurrent executions for the provider Lambda function. Default: 5
        :param security_groups: (experimental) Security groups to attach to the provider Lambda functions.
        :param subnets: (experimental) Optional subnet selection for the Lambda functions.
        :param vpc: (experimental) VPC where the Lambda functions will be deployed.

        :stability: experimental
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e572f0d30fd79ee590fe9464ce9e2e98acbf2c78d2f4d37c841c325412590fd9)
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument log_group_retention", value=log_group_retention, expected_type=type_hints["log_group_retention"])
            check_type(argname="argument reserved_concurrent_executions", value=reserved_concurrent_executions, expected_type=type_hints["reserved_concurrent_executions"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if log_group_retention is not None:
            self._values["log_group_retention"] = log_group_retention
        if reserved_concurrent_executions is not None:
            self._values["reserved_concurrent_executions"] = reserved_concurrent_executions
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue]:
        '''(experimental) Optional SQS queue to use as a dead letter queue.

        :stability: experimental
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue], result)

    @builtins.property
    def log_group_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''(experimental) Optional retention period for the Lambda functions log group.

        :default: RetentionDays.ONE_MONTH

        :stability: experimental
        '''
        result = self._values.get("log_group_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def reserved_concurrent_executions(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of concurrent executions for the provider Lambda function.

        Default: 5

        :stability: experimental
        '''
        result = self._values.get("reserved_concurrent_executions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) Security groups to attach to the provider Lambda functions.

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Optional subnet selection for the Lambda functions.

        :stability: experimental
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) VPC where the Lambda functions will be deployed.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SageMakerNotebookInstanceType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.types.SageMakerNotebookInstanceType",
):
    '''(experimental) SageMaker Instance Type.

    :stability: experimental
    '''

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_2XLARGE")
    def ML_C4_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c4.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C4_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_4XLARGE")
    def ML_C4_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c4.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C4_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_8XLARGE")
    def ML_C4_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c4.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C4_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_LARGE")
    def ML_C4_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c4.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C4_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C4_XLARGE")
    def ML_C4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c4.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C4_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_12XLARGE")
    def ML_C5_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_18XLARGE")
    def ML_C5_18_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5.18xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5_18XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_24XLARGE")
    def ML_C5_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_2XLARGE")
    def ML_C5_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_4XLARGE")
    def ML_C5_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_9XLARGE")
    def ML_C5_9_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5.9xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5_9XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_LARGE")
    def ML_C5_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c5.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5_XLARGE")
    def ML_C5_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_18XLARGE")
    def ML_C5_D_18_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5d.18xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5D_18XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_2XLARGE")
    def ML_C5_D_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5d.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_4XLARGE")
    def ML_C5_D_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5d.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5D_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_9XLARGE")
    def ML_C5_D_9_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5d.9xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5D_9XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_LARGE")
    def ML_C5_D_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c5d.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5D_XLARGE")
    def ML_C5_D_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5d.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5D_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5N_18XLARGE")
    def ML_C5_N_18_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5n.18xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5N_18XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5N_2XLARGE")
    def ML_C5_N_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5n.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5N_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5N_4XLARGE")
    def ML_C5_N_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5n.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5N_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5N_9XLARGE")
    def ML_C5_N_9_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5n.9xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5N_9XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5N_LARGE")
    def ML_C5_N_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c5n.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5N_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C5N_XLARGE")
    def ML_C5_N_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c5n.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C5N_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6G_12XLARGE")
    def ML_C6_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6g.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6G_16XLARGE")
    def ML_C6_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6g.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6G_2XLARGE")
    def ML_C6_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6g.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6G_4XLARGE")
    def ML_C6_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6g.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6G_8XLARGE")
    def ML_C6_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6g.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6G_LARGE")
    def ML_C6_G_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c6g.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6G_XLARGE")
    def ML_C6_G_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6g.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GD_12XLARGE")
    def ML_C6_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gd.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GD_16XLARGE")
    def ML_C6_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gd.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GD_2XLARGE")
    def ML_C6_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gd.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GD_4XLARGE")
    def ML_C6_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gd.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GD_8XLARGE")
    def ML_C6_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gd.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GD_LARGE")
    def ML_C6_GD_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gd.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GD_XLARGE")
    def ML_C6_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gd.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GN_12XLARGE")
    def ML_C6_GN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gn.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GN_16XLARGE")
    def ML_C6_GN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gn.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GN_2XLARGE")
    def ML_C6_GN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gn.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GN_4XLARGE")
    def ML_C6_GN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gn.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GN_8XLARGE")
    def ML_C6_GN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gn.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GN_LARGE")
    def ML_C6_GN_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gn.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GN_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6GN_XLARGE")
    def ML_C6_GN_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6gn.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6GN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_12XLARGE")
    def ML_C6_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6i.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_16XLARGE")
    def ML_C6_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6i.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_24XLARGE")
    def ML_C6_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6i.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_2XLARGE")
    def ML_C6_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6i.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_32XLARGE")
    def ML_C6_I_32_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6i.32xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6I_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_4XLARGE")
    def ML_C6_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6i.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_8XLARGE")
    def ML_C6_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6i.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_LARGE")
    def ML_C6_I_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c6i.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6I_XLARGE")
    def ML_C6_I_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6i.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6ID_12XLARGE")
    def ML_C6_ID_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6id.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6ID_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6ID_16XLARGE")
    def ML_C6_ID_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6id.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6ID_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6ID_24XLARGE")
    def ML_C6_ID_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6id.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6ID_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6ID_2XLARGE")
    def ML_C6_ID_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6id.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6ID_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6ID_32XLARGE")
    def ML_C6_ID_32_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6id.32xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6ID_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6ID_4XLARGE")
    def ML_C6_ID_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6id.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6ID_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6ID_8XLARGE")
    def ML_C6_ID_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6id.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6ID_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6ID_LARGE")
    def ML_C6_ID_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c6id.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6ID_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C6ID_XLARGE")
    def ML_C6_ID_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c6id.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C6ID_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7G_12XLARGE")
    def ML_C7_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7g.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7G_16XLARGE")
    def ML_C7_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7g.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7G_2XLARGE")
    def ML_C7_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7g.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7G_4XLARGE")
    def ML_C7_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7g.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7G_8XLARGE")
    def ML_C7_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7g.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7G_LARGE")
    def ML_C7_G_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c7g.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7G_XLARGE")
    def ML_C7_G_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7g.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7I_12XLARGE")
    def ML_C7_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7i.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7I_16XLARGE")
    def ML_C7_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7i.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7I_24XLARGE")
    def ML_C7_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7i.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7I_2XLARGE")
    def ML_C7_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7i.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7I_48XLARGE")
    def ML_C7_I_48_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7i.48xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7I_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7I_4XLARGE")
    def ML_C7_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7i.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7I_8XLARGE")
    def ML_C7_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7i.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7I_LARGE")
    def ML_C7_I_LARGE(cls) -> builtins.str:
        '''(experimental) ml.c7i.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_C7I_XLARGE")
    def ML_C7_I_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.c7i.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_C7I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_12XLARGE")
    def ML_G4_DN_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g4dn.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G4DN_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_16XLARGE")
    def ML_G4_DN_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g4dn.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G4DN_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_2XLARGE")
    def ML_G4_DN_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g4dn.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G4DN_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_4XLARGE")
    def ML_G4_DN_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g4dn.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G4DN_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_8XLARGE")
    def ML_G4_DN_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g4dn.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G4DN_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G4DN_XLARGE")
    def ML_G4_DN_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g4dn.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G4DN_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_12XLARGE")
    def ML_G5_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g5.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_16XLARGE")
    def ML_G5_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g5.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G5_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_24XLARGE")
    def ML_G5_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g5.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_2XLARGE")
    def ML_G5_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g5.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_48XLARGE")
    def ML_G5_48_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g5.48xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G5_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_4XLARGE")
    def ML_G5_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g5.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_8XLARGE")
    def ML_G5_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g5.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G5_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G5_XLARGE")
    def ML_G5_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g5.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6_12XLARGE")
    def ML_G6_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6_16XLARGE")
    def ML_G6_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6_24XLARGE")
    def ML_G6_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6_2XLARGE")
    def ML_G6_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6_48XLARGE")
    def ML_G6_48_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6.48xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6_4XLARGE")
    def ML_G6_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6_8XLARGE")
    def ML_G6_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6_XLARGE")
    def ML_G6_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6E_12XLARGE")
    def ML_G6_E_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6e.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6E_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6E_16XLARGE")
    def ML_G6_E_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6e.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6E_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6E_24XLARGE")
    def ML_G6_E_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6e.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6E_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6E_2XLARGE")
    def ML_G6_E_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6e.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6E_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6E_48XLARGE")
    def ML_G6_E_48_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6e.48xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6E_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6E_4XLARGE")
    def ML_G6_E_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6e.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6E_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6E_8XLARGE")
    def ML_G6_E_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6e.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6E_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_G6E_XLARGE")
    def ML_G6_E_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.g6e.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_G6E_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_GR6_4XLARGE")
    def ML_GR6_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.gr6.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_GR6_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_GR6_8XLARGE")
    def ML_GR6_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.gr6.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_GR6_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF1_24XLARGE")
    def ML_INF1_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.inf1.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_INF1_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF1_2XLARGE")
    def ML_INF1_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.inf1.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_INF1_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF1_6XLARGE")
    def ML_INF1_6_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.inf1.6xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_INF1_6XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF1_XLARGE")
    def ML_INF1_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.inf1.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_INF1_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF2_24XLARGE")
    def ML_INF2_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.inf2.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_INF2_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF2_48XLARGE")
    def ML_INF2_48_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.inf2.48xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_INF2_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF2_8XLARGE")
    def ML_INF2_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.inf2.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_INF2_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_INF2_XLARGE")
    def ML_INF2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.inf2.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_INF2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_10XLARGE")
    def ML_M4_10_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m4.10xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M4_10XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_16XLARGE")
    def ML_M4_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m4.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M4_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_2XLARGE")
    def ML_M4_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m4.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M4_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_4XLARGE")
    def ML_M4_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m4.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M4_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M4_XLARGE")
    def ML_M4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m4.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M4_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_12XLARGE")
    def ML_M5_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_16XLARGE")
    def ML_M5_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_24XLARGE")
    def ML_M5_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_2XLARGE")
    def ML_M5_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_4XLARGE")
    def ML_M5_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_8XLARGE")
    def ML_M5_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_LARGE")
    def ML_M5_LARGE(cls) -> builtins.str:
        '''(experimental) ml.m5.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5_XLARGE")
    def ML_M5_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_12XLARGE")
    def ML_M5_D_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5d.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5D_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_16XLARGE")
    def ML_M5_D_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5d.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5D_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_24XLARGE")
    def ML_M5_D_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5d.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_2XLARGE")
    def ML_M5_D_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5d.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_4XLARGE")
    def ML_M5_D_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5d.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5D_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_8XLARGE")
    def ML_M5_D_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5d.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5D_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_LARGE")
    def ML_M5_D_LARGE(cls) -> builtins.str:
        '''(experimental) ml.m5d.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M5D_XLARGE")
    def ML_M5_D_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m5d.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M5D_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6G_12XLARGE")
    def ML_M6_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6g.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6G_16XLARGE")
    def ML_M6_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6g.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6G_2XLARGE")
    def ML_M6_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6g.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6G_4XLARGE")
    def ML_M6_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6g.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6G_8XLARGE")
    def ML_M6_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6g.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6G_LARGE")
    def ML_M6_G_LARGE(cls) -> builtins.str:
        '''(experimental) ml.m6g.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6G_XLARGE")
    def ML_M6_G_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6g.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6GD_12XLARGE")
    def ML_M6_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6gd.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6GD_16XLARGE")
    def ML_M6_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6gd.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6GD_2XLARGE")
    def ML_M6_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6gd.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6GD_4XLARGE")
    def ML_M6_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6gd.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6GD_8XLARGE")
    def ML_M6_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6gd.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6GD_LARGE")
    def ML_M6_GD_LARGE(cls) -> builtins.str:
        '''(experimental) ml.m6gd.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6GD_XLARGE")
    def ML_M6_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6gd.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6I_12XLARGE")
    def ML_M6_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6i.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6I_16XLARGE")
    def ML_M6_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6i.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6I_24XLARGE")
    def ML_M6_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6i.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6I_2XLARGE")
    def ML_M6_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6i.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6I_32XLARGE")
    def ML_M6_I_32_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6i.32xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6I_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6I_4XLARGE")
    def ML_M6_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6i.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6I_8XLARGE")
    def ML_M6_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6i.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6I_LARGE")
    def ML_M6_I_LARGE(cls) -> builtins.str:
        '''(experimental) ml.m6i.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6I_XLARGE")
    def ML_M6_I_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6i.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6ID_12XLARGE")
    def ML_M6_ID_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6id.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6ID_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6ID_16XLARGE")
    def ML_M6_ID_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6id.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6ID_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6ID_24XLARGE")
    def ML_M6_ID_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6id.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6ID_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6ID_2XLARGE")
    def ML_M6_ID_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6id.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6ID_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6ID_32XLARGE")
    def ML_M6_ID_32_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6id.32xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6ID_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6ID_4XLARGE")
    def ML_M6_ID_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6id.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6ID_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6ID_8XLARGE")
    def ML_M6_ID_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6id.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6ID_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6ID_LARGE")
    def ML_M6_ID_LARGE(cls) -> builtins.str:
        '''(experimental) ml.m6id.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6ID_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M6ID_XLARGE")
    def ML_M6_ID_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m6id.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M6ID_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M7I_12XLARGE")
    def ML_M7_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m7i.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M7I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M7I_16XLARGE")
    def ML_M7_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m7i.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M7I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M7I_24XLARGE")
    def ML_M7_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m7i.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M7I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M7I_2XLARGE")
    def ML_M7_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m7i.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M7I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M7I_48XLARGE")
    def ML_M7_I_48_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m7i.48xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M7I_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M7I_4XLARGE")
    def ML_M7_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m7i.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M7I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M7I_8XLARGE")
    def ML_M7_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m7i.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M7I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M7I_LARGE")
    def ML_M7_I_LARGE(cls) -> builtins.str:
        '''(experimental) ml.m7i.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M7I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_M7I_XLARGE")
    def ML_M7_I_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.m7i.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_M7I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P2_16XLARGE")
    def ML_P2_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p2.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P2_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P2_8XLARGE")
    def ML_P2_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p2.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P2_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P2_XLARGE")
    def ML_P2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p2.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P3_16XLARGE")
    def ML_P3_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p3.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P3_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P3_2XLARGE")
    def ML_P3_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p3.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P3_8XLARGE")
    def ML_P3_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p3.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P3_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P3DN_24XLARGE")
    def ML_P3_DN_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p3dn.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P3DN_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P4D_24XLARGE")
    def ML_P4_D_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p4d.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P4D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P4DE_24XLARGE")
    def ML_P4_DE_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p4de.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P4DE_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_P5_48XLARGE")
    def ML_P5_48_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.p5.48xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_P5_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_12XLARGE")
    def ML_R5_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_16XLARGE")
    def ML_R5_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_24XLARGE")
    def ML_R5_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_2XLARGE")
    def ML_R5_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_4XLARGE")
    def ML_R5_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_8XLARGE")
    def ML_R5_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_LARGE")
    def ML_R5_LARGE(cls) -> builtins.str:
        '''(experimental) ml.r5.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5_XLARGE")
    def ML_R5_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_12XLARGE")
    def ML_R5_D_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5d.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5D_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_16XLARGE")
    def ML_R5_D_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5d.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5D_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_24XLARGE")
    def ML_R5_D_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5d.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5D_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_2XLARGE")
    def ML_R5_D_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5d.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5D_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_4XLARGE")
    def ML_R5_D_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5d.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5D_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_8XLARGE")
    def ML_R5_D_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5d.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5D_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_LARGE")
    def ML_R5_D_LARGE(cls) -> builtins.str:
        '''(experimental) ml.r5d.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5D_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R5D_XLARGE")
    def ML_R5_D_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r5d.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R5D_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6G_12XLARGE")
    def ML_R6_G_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6g.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6G_16XLARGE")
    def ML_R6_G_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6g.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6G_2XLARGE")
    def ML_R6_G_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6g.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6G_4XLARGE")
    def ML_R6_G_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6g.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6G_8XLARGE")
    def ML_R6_G_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6g.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6G_LARGE")
    def ML_R6_G_LARGE(cls) -> builtins.str:
        '''(experimental) ml.r6g.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6G_XLARGE")
    def ML_R6_G_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6g.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6GD_12XLARGE")
    def ML_R6_GD_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6gd.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6GD_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6GD_16XLARGE")
    def ML_R6_GD_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6gd.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6GD_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6GD_2XLARGE")
    def ML_R6_GD_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6gd.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6GD_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6GD_4XLARGE")
    def ML_R6_GD_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6gd.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6GD_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6GD_8XLARGE")
    def ML_R6_GD_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6gd.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6GD_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6GD_LARGE")
    def ML_R6_GD_LARGE(cls) -> builtins.str:
        '''(experimental) ml.r6gd.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6GD_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6GD_XLARGE")
    def ML_R6_GD_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6gd.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6GD_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6I_12XLARGE")
    def ML_R6_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6i.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6I_16XLARGE")
    def ML_R6_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6i.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6I_24XLARGE")
    def ML_R6_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6i.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6I_2XLARGE")
    def ML_R6_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6i.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6I_32XLARGE")
    def ML_R6_I_32_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6i.32xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6I_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6I_4XLARGE")
    def ML_R6_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6i.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6I_8XLARGE")
    def ML_R6_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6i.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6I_LARGE")
    def ML_R6_I_LARGE(cls) -> builtins.str:
        '''(experimental) ml.r6i.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6I_XLARGE")
    def ML_R6_I_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6i.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6ID_12XLARGE")
    def ML_R6_ID_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6id.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6ID_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6ID_16XLARGE")
    def ML_R6_ID_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6id.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6ID_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6ID_24XLARGE")
    def ML_R6_ID_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6id.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6ID_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6ID_2XLARGE")
    def ML_R6_ID_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6id.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6ID_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6ID_32XLARGE")
    def ML_R6_ID_32_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6id.32xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6ID_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6ID_4XLARGE")
    def ML_R6_ID_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6id.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6ID_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6ID_8XLARGE")
    def ML_R6_ID_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6id.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6ID_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6ID_LARGE")
    def ML_R6_ID_LARGE(cls) -> builtins.str:
        '''(experimental) ml.r6id.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6ID_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R6ID_XLARGE")
    def ML_R6_ID_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r6id.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R6ID_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R7I_12XLARGE")
    def ML_R7_I_12_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r7i.12xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R7I_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R7I_16XLARGE")
    def ML_R7_I_16_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r7i.16xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R7I_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R7I_24XLARGE")
    def ML_R7_I_24_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r7i.24xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R7I_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R7I_2XLARGE")
    def ML_R7_I_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r7i.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R7I_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R7I_48XLARGE")
    def ML_R7_I_48_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r7i.48xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R7I_48XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R7I_4XLARGE")
    def ML_R7_I_4_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r7i.4xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R7I_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R7I_8XLARGE")
    def ML_R7_I_8_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r7i.8xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R7I_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R7I_LARGE")
    def ML_R7_I_LARGE(cls) -> builtins.str:
        '''(experimental) ml.r7i.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R7I_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_R7I_XLARGE")
    def ML_R7_I_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.r7i.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_R7I_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T2_2XLARGE")
    def ML_T2_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.t2.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_T2_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T2_LARGE")
    def ML_T2_LARGE(cls) -> builtins.str:
        '''(experimental) ml.t2.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_T2_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T2_MEDIUM")
    def ML_T2_MEDIUM(cls) -> builtins.str:
        '''(experimental) ml.t2.medium Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_T2_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T2_XLARGE")
    def ML_T2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.t2.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_T2_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T3_2XLARGE")
    def ML_T3_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.t3.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_T3_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T3_LARGE")
    def ML_T3_LARGE(cls) -> builtins.str:
        '''(experimental) ml.t3.large Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_T3_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T3_MEDIUM")
    def ML_T3_MEDIUM(cls) -> builtins.str:
        '''(experimental) ml.t3.medium Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_T3_MEDIUM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_T3_XLARGE")
    def ML_T3_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.t3.xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_T3_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_TRN1_2XLARGE")
    def ML_TRN1_2_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.trn1.2xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_TRN1_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_TRN1_32XLARGE")
    def ML_TRN1_32_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.trn1.32xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_TRN1_32XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ML_TRN1N_32XLARGE")
    def ML_TRN1_N_32_XLARGE(cls) -> builtins.str:
        '''(experimental) ml.trn1n.32xlarge Notebook Instance Type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "ML_TRN1N_32XLARGE"))


__all__ = [
    "AwsCustomResourceLambdaConfiguration",
    "AwsManagedPolicy",
    "DestructiveOperation",
    "Ec2InstanceType",
    "LambdaConfiguration",
    "SageMakerNotebookInstanceType",
]

publication.publish()

def _typecheckingstub__94c5cee93e244643d0253938483ebf4729a03d1dbc4432b65477c09475f2f439(
    *,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e572f0d30fd79ee590fe9464ce9e2e98acbf2c78d2f4d37c841c325412590fd9(
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
    log_group_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass
