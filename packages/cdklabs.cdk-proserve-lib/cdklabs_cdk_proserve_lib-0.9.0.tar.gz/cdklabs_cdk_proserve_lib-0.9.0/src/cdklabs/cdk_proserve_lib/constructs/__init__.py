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
import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_imagebuilder as _aws_cdk_aws_imagebuilder_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_lambda_nodejs as _aws_cdk_aws_lambda_nodejs_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_networkfirewall as _aws_cdk_aws_networkfirewall_ceddda9d
import aws_cdk.aws_opensearchservice as _aws_cdk_aws_opensearchservice_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_s3_assets as _aws_cdk_aws_s3_assets_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import aws_cdk.aws_ssm as _aws_cdk_aws_ssm_ceddda9d
import aws_cdk.aws_wafv2 as _aws_cdk_aws_wafv2_ceddda9d
import constructs as _constructs_77d1e7e8
from ..types import (
    AwsCustomResourceLambdaConfiguration as _AwsCustomResourceLambdaConfiguration_be7862df,
    DestructiveOperation as _DestructiveOperation_8d644d1e,
    LambdaConfiguration as _LambdaConfiguration_9f8afc24,
)


class DynamoDbProvisionTable(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.DynamoDbProvisionTable",
):
    '''(experimental) Controls the contents of an Amazon DynamoDB table from Infrastructure as Code.

    This construct uses information about the key attributes of a table and a list of rows to populate the table upon
    creation, update the table upon update, and remove entries from the table upon delete.

    WARNING: This construct should only be used with tables that are created and fully managed via IaC. While the
    the construct will only manage rows within the table that it is aware of, there is no way to detect drift and thus
    it is possible to cause data loss within the table if it is managed outside of IaC as well.

    The construct also handles encryption for the framework resources using either a provided KMS key or an
    AWS managed key.

    :stability: experimental

    Example::

        import { DynamoDbProvisionTable } from '@cdklabs/cdk-proserve-lib/constructs';
        import { Table } from 'aws-cdk-lib/aws-dynamodb';
        import { Key } from 'aws-cdk-lib/aws-kms';
        
        interface TableRow {
            readonly uid: number;
            readonly isActive: boolean;
        }
        
        const partitionKey: keyof TableRow = 'uid';
        
        const rows: TableRow[] = [
            {
                isActive: true,
                uid: 1
            },
            {
                isActive: true,
                uid: 2
            },
            {
                isActive: false,
                uid: 3
            }
        ];
        
        const tableArn = 'arn:aws:dynamodb:us-west-1:111111111111:table/sample';
        const table = Table.fromTableArn(this, 'Table', tableArn);
        
        const keyArn = 'arn:aws:kms:us-east-1:111111111111:key/sample-key-id';
        const key = Key.fromKeyArn(this, 'Encryption', keyArn);
        
        new DynamoDbProvisionTable(this, 'ProvisionTable', {
            items: rows,
            table: {
                partitionKeyName: partitionKey,
                resource: table,
                encryption: key
            }
        });
        
        }
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        items: typing.Sequence[typing.Mapping[builtins.str, typing.Any]],
        table: typing.Union["DynamoDbProvisionTable.TableProps", typing.Dict[builtins.str, typing.Any]],
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Provisions an existing DynamoDB Table with user-specified data.

        :param scope: Parent to which the Custom Resource belongs.
        :param id: Unique identifier for this instance.
        :param items: (experimental) Items to provision within the DynamoDB table.
        :param table: (experimental) Table to provision.
        :param encryption: (experimental) Encryption key for protecting the framework resources.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75e675d5b6c5efc4f3d517f4b5cb2c050c01589db5dae3ccedefd4b2ace24b6d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DynamoDbProvisionTableProps(
            items=items,
            table=table,
            encryption=encryption,
            lambda_configuration=lambda_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.DynamoDbProvisionTable.TableProps",
        jsii_struct_bases=[],
        name_mapping={
            "partition_key_name": "partitionKeyName",
            "resource": "resource",
            "encryption": "encryption",
            "sort_key_name": "sortKeyName",
        },
    )
    class TableProps:
        def __init__(
            self,
            *,
            partition_key_name: builtins.str,
            resource: _aws_cdk_aws_dynamodb_ceddda9d.ITable,
            encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
            sort_key_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''(experimental) Information about the table to provision.

            :param partition_key_name: (experimental) Name of the partition key for the table.
            :param resource: (experimental) CDK representation of the table itself.
            :param encryption: (experimental) Optional existing encryption key associated with the table.
            :param sort_key_name: (experimental) Name of the sort key for the table if applicable.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__0f2f053da9013efed93700973fc9b6d139fabc44431d7adcc0531222ae5fc066)
                check_type(argname="argument partition_key_name", value=partition_key_name, expected_type=type_hints["partition_key_name"])
                check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
                check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
                check_type(argname="argument sort_key_name", value=sort_key_name, expected_type=type_hints["sort_key_name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "partition_key_name": partition_key_name,
                "resource": resource,
            }
            if encryption is not None:
                self._values["encryption"] = encryption
            if sort_key_name is not None:
                self._values["sort_key_name"] = sort_key_name

        @builtins.property
        def partition_key_name(self) -> builtins.str:
            '''(experimental) Name of the partition key for the table.

            :stability: experimental
            '''
            result = self._values.get("partition_key_name")
            assert result is not None, "Required property 'partition_key_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def resource(self) -> _aws_cdk_aws_dynamodb_ceddda9d.ITable:
            '''(experimental) CDK representation of the table itself.

            :stability: experimental
            '''
            result = self._values.get("resource")
            assert result is not None, "Required property 'resource' is missing"
            return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.ITable, result)

        @builtins.property
        def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
            '''(experimental) Optional existing encryption key associated with the table.

            :stability: experimental
            '''
            result = self._values.get("encryption")
            return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

        @builtins.property
        def sort_key_name(self) -> typing.Optional[builtins.str]:
            '''(experimental) Name of the sort key for the table if applicable.

            :stability: experimental
            '''
            result = self._values.get("sort_key_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TableProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.DynamoDbProvisionTableProps",
    jsii_struct_bases=[],
    name_mapping={
        "items": "items",
        "table": "table",
        "encryption": "encryption",
        "lambda_configuration": "lambdaConfiguration",
    },
)
class DynamoDbProvisionTableProps:
    def __init__(
        self,
        *,
        items: typing.Sequence[typing.Mapping[builtins.str, typing.Any]],
        table: typing.Union[DynamoDbProvisionTable.TableProps, typing.Dict[builtins.str, typing.Any]],
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the DynamoDbProvisionTable construct.

        :param items: (experimental) Items to provision within the DynamoDB table.
        :param table: (experimental) Table to provision.
        :param encryption: (experimental) Encryption key for protecting the framework resources.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if isinstance(table, dict):
            table = DynamoDbProvisionTable.TableProps(**table)
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__057380ca290e7837e75b9bfeb840e320aa76aea52a09b6ee95b22f8e83ee518a)
            check_type(argname="argument items", value=items, expected_type=type_hints["items"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "items": items,
            "table": table,
        }
        if encryption is not None:
            self._values["encryption"] = encryption
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration

    @builtins.property
    def items(self) -> typing.List[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Items to provision within the DynamoDB table.

        :stability: experimental
        '''
        result = self._values.get("items")
        assert result is not None, "Required property 'items' is missing"
        return typing.cast(typing.List[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def table(self) -> DynamoDbProvisionTable.TableProps:
        '''(experimental) Table to provision.

        :stability: experimental
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(DynamoDbProvisionTable.TableProps, result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Encryption key for protecting the framework resources.

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
        return "DynamoDbProvisionTableProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Ec2ImageBuilderGetImage(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImageBuilderGetImage",
):
    '''(experimental) Retrieves an EC2 Image Builder image build version.

    This is useful for retrieving the AMI ID of an image that was built by an
    EC2 Image Builder pipeline.

    :stability: experimental

    Example::

        import { CfnOutput } from 'aws-cdk-lib';
        import { Ec2ImageBuilderGetImage } from '@cdklabs/cdk-proserve-lib/constructs';
        
        const image = new Ec2ImageBuilderGetImage(this, 'SomeImage', {
          imageBuildVersionArn: 'arn:aws:imagebuilder:us-east-1:123456789012:image/some-image/0.0.1/1'
        });
        new CfnOutput(this, 'AmiId', { value: image.ami });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        image_build_version_arn: builtins.str,
        lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Retrieves an EC2 Image Builder image build version.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID.
        :param image_build_version_arn: (experimental) The ARN of the EC2 Image Builder image build version.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77b3847ea7ab39647e63e524b2fd35fa06cad82a271bbc9187a0da10595cdbc2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = Ec2ImageBuilderGetImageProps(
            image_build_version_arn=image_build_version_arn,
            lambda_configuration=lambda_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="ami")
    def ami(self) -> builtins.str:
        '''(experimental) The AMI ID retrieved from the EC2 Image Builder image.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "ami"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImageBuilderGetImageProps",
    jsii_struct_bases=[],
    name_mapping={
        "image_build_version_arn": "imageBuildVersionArn",
        "lambda_configuration": "lambdaConfiguration",
    },
)
class Ec2ImageBuilderGetImageProps:
    def __init__(
        self,
        *,
        image_build_version_arn: builtins.str,
        lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the Ec2ImageBuilderGetImage construct.

        :param image_build_version_arn: (experimental) The ARN of the EC2 Image Builder image build version.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _AwsCustomResourceLambdaConfiguration_be7862df(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__184e94d1d9278acaeb42b57dfec53575c7a9faed100c01fb9af15258d9421ef1)
            check_type(argname="argument image_build_version_arn", value=image_build_version_arn, expected_type=type_hints["image_build_version_arn"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "image_build_version_arn": image_build_version_arn,
        }
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration

    @builtins.property
    def image_build_version_arn(self) -> builtins.str:
        '''(experimental) The ARN of the EC2 Image Builder image build version.

        :stability: experimental
        '''
        result = self._values.get("image_build_version_arn")
        assert result is not None, "Required property 'image_build_version_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_configuration(
        self,
    ) -> typing.Optional[_AwsCustomResourceLambdaConfiguration_be7862df]:
        '''(experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_AwsCustomResourceLambdaConfiguration_be7862df], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ec2ImageBuilderGetImageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Ec2ImageBuilderStart(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImageBuilderStart",
):
    '''(experimental) Starts an EC2 Image Builder Pipeline and optionally waits for the build to complete.

    This construct is useful if you want to create an image as part of your IaC
    deployment. By waiting for completion of this construct, you can use the
    image in the same deployment by retrieving the AMI and passing it to an EC2
    build step.

    :stability: experimental

    Example::

        import { Duration } from 'aws-cdk-lib';
        import { Topic } from 'aws-cdk-lib/aws-sns';
        import { Ec2ImageBuilderStart } from '@cdklabs/cdk-proserve-lib/constructs';
        
        const topic = Topic.fromTopicArn(
          this,
          'MyTopic',
          'arn:aws:sns:us-east-1:123456789012:my-notification-topic'
        );
        new Ec2ImageBuilderStart(this, 'ImageBuilderStart', {
          pipelineArn:
            'arn:aws:imagebuilder:us-east-1:123456789012:image-pipeline/my-image-pipeline',
          waitForCompletion: {
            topic: topic,
            timeout: Duration.hours(7)  // wait up to 7 hours for completion
          }
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        pipeline_arn: builtins.str,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        hash: typing.Optional[builtins.str] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        wait_for_completion: typing.Optional[typing.Union["Ec2ImageBuilderStart.WaitForCompletionProps", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Starts an EC2 Image Builder Pipeline and optionally waits for the build to complete.

        :param scope: The construct scope.
        :param id: The construct ID.
        :param pipeline_arn: (experimental) The ARN of the Image Builder pipeline to start.
        :param encryption: (experimental) Optional KMS Encryption Key to use for encrypting resources.
        :param hash: (experimental) An optional user-generated hash value that will determine if the construct will start the build pipeline. If this is not set, the pipeline will only start once on initial deployment. By setting this, you can for example start a new build if your build instructions have changed and then wait for the pipeline to complete again. This hash should be a short string, ideally ~7 characters or less. It will be set as the Physical ID of the Custom Resource and also used to append to Waiter function Physical IDs.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param wait_for_completion: (experimental) Set these properties to wait for the Image Build to complete. This is useful if you need the AMI before your next infrastructure step.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c6b272e0e32c91e9ca6567ad3a5863fbf8d47e124cfe4db893341e0671f95ac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = Ec2ImageBuilderStartProps(
            pipeline_arn=pipeline_arn,
            encryption=encryption,
            hash=hash,
            lambda_configuration=lambda_configuration,
            wait_for_completion=wait_for_completion,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="imageBuildVersionArn")
    def image_build_version_arn(self) -> builtins.str:
        '''(experimental) The ARN of the image build version created by the pipeline execution.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageBuildVersionArn"))

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImageBuilderStart.WaitForCompletionProps",
        jsii_struct_bases=[],
        name_mapping={"topic": "topic", "timeout": "timeout"},
    )
    class WaitForCompletionProps:
        def __init__(
            self,
            *,
            topic: _aws_cdk_aws_sns_ceddda9d.ITopic,
            timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        ) -> None:
            '''
            :param topic: (experimental) An SNS Topic that will signal when the pipeline is complete. This is typically configured on your EC2 Image Builder pipeline to trigger an SNS notification when the pipeline completes.
            :param timeout: (experimental) The maximum amount of time to wait for the image build pipeline to complete. This is set to a maximum of 12 hours by default. Default: 12 hours

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__4a6651df0fe081b0ec228004b64fd177cf62b1f8699519c900e5306fc9889989)
                check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
                check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "topic": topic,
            }
            if timeout is not None:
                self._values["timeout"] = timeout

        @builtins.property
        def topic(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
            '''(experimental) An SNS Topic that will signal when the pipeline is complete.

            This is
            typically configured on your EC2 Image Builder pipeline to trigger an
            SNS notification when the pipeline completes.

            :stability: experimental
            '''
            result = self._values.get("topic")
            assert result is not None, "Required property 'topic' is missing"
            return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, result)

        @builtins.property
        def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
            '''(experimental) The maximum amount of time to wait for the image build pipeline to complete.

            This is set to a maximum of 12 hours by default.

            :default: 12 hours

            :stability: experimental
            '''
            result = self._values.get("timeout")
            return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "WaitForCompletionProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImageBuilderStartProps",
    jsii_struct_bases=[],
    name_mapping={
        "pipeline_arn": "pipelineArn",
        "encryption": "encryption",
        "hash": "hash",
        "lambda_configuration": "lambdaConfiguration",
        "wait_for_completion": "waitForCompletion",
    },
)
class Ec2ImageBuilderStartProps:
    def __init__(
        self,
        *,
        pipeline_arn: builtins.str,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        hash: typing.Optional[builtins.str] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        wait_for_completion: typing.Optional[typing.Union[Ec2ImageBuilderStart.WaitForCompletionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the EC2 Image Builder Start custom resource.

        :param pipeline_arn: (experimental) The ARN of the Image Builder pipeline to start.
        :param encryption: (experimental) Optional KMS Encryption Key to use for encrypting resources.
        :param hash: (experimental) An optional user-generated hash value that will determine if the construct will start the build pipeline. If this is not set, the pipeline will only start once on initial deployment. By setting this, you can for example start a new build if your build instructions have changed and then wait for the pipeline to complete again. This hash should be a short string, ideally ~7 characters or less. It will be set as the Physical ID of the Custom Resource and also used to append to Waiter function Physical IDs.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param wait_for_completion: (experimental) Set these properties to wait for the Image Build to complete. This is useful if you need the AMI before your next infrastructure step.

        :stability: experimental
        '''
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if isinstance(wait_for_completion, dict):
            wait_for_completion = Ec2ImageBuilderStart.WaitForCompletionProps(**wait_for_completion)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9660c3b729015c46b21753c84ffe9a1cbff9a627eda095023fcbd14bcac7e52c)
            check_type(argname="argument pipeline_arn", value=pipeline_arn, expected_type=type_hints["pipeline_arn"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument hash", value=hash, expected_type=type_hints["hash"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
            check_type(argname="argument wait_for_completion", value=wait_for_completion, expected_type=type_hints["wait_for_completion"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "pipeline_arn": pipeline_arn,
        }
        if encryption is not None:
            self._values["encryption"] = encryption
        if hash is not None:
            self._values["hash"] = hash
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration
        if wait_for_completion is not None:
            self._values["wait_for_completion"] = wait_for_completion

    @builtins.property
    def pipeline_arn(self) -> builtins.str:
        '''(experimental) The ARN of the Image Builder pipeline to start.

        :stability: experimental
        '''
        result = self._values.get("pipeline_arn")
        assert result is not None, "Required property 'pipeline_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Optional KMS Encryption Key to use for encrypting resources.

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def hash(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional user-generated hash value that will determine if the construct will start the build pipeline.

        If this is not set, the pipeline
        will only start once on initial deployment. By setting this, you can for
        example start a new build if your build instructions have changed and
        then wait for the pipeline to complete again.

        This hash should be a short
        string, ideally ~7 characters or less. It will be set as the Physical ID
        of the Custom Resource and also used to append to Waiter function
        Physical IDs.

        :stability: experimental
        '''
        result = self._values.get("hash")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_configuration(self) -> typing.Optional[_LambdaConfiguration_9f8afc24]:
        '''(experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_LambdaConfiguration_9f8afc24], result)

    @builtins.property
    def wait_for_completion(
        self,
    ) -> typing.Optional[Ec2ImageBuilderStart.WaitForCompletionProps]:
        '''(experimental) Set these properties to wait for the Image Build to complete.

        This is
        useful if you need the AMI before your next infrastructure step.

        :stability: experimental
        '''
        result = self._values.get("wait_for_completion")
        return typing.cast(typing.Optional[Ec2ImageBuilderStart.WaitForCompletionProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ec2ImageBuilderStartProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Ec2ImagePipeline(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImagePipeline",
):
    '''(experimental) An EC2 Image Pipeline that can be used to build a Amazon Machine Image (AMI) automatically.

    This construct simplifies the process of creating an EC2 Image Pipeline and
    provides all of the available components that can be used that are maintained
    by AWS.

    :stability: experimental

    Example::

        import { CfnOutput } from 'aws-cdk-lib';
        import { Ec2ImagePipeline } from '@cdklabs/cdk-proserve-lib/constructs';
        
        const pipeline = new Ec2ImagePipeline(this, 'ImagePipeline', {
          version: '0.1.0',
          buildConfiguration: {
            start: true,
            waitForCompletion: true
          },
          components: [
            Ec2ImagePipeline.Component.AWS_CLI_VERSION_2_LINUX,
            Ec2ImagePipeline.Component.DOCKER_CE_LINUX
          ]
        });
        new CfnOutput(this, 'ImagePipelineAmi', { value: pipeline.latestAmi! });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        block_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        components: typing.Optional[typing.Sequence[typing.Union["Ec2ImagePipeline.Component", _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
        machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        version: builtins.str,
        build_configuration: typing.Optional[typing.Union["Ec2ImagePipeline.BuildConfigurationProps", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_configuration: typing.Optional[typing.Union["Ec2ImagePipeline.VpcConfigurationProps", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) An EC2 Image Pipeline that can be used to build a Amazon Machine Image (AMI) automatically.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID.
        :param block_device_mappings: (experimental) Block device mappings for the image.
        :param components: (experimental) Components to be included in the image pipeline. Can be either custom Ec2ImagePipeline.Component or AWS CDK imagebuilder.CfnComponent.
        :param machine_image: (experimental) The machine image to use as a base for the pipeline. Default: AmazonLinux2023
        :param version: (experimental) Version of the image pipeline. This must be updated if you make underlying changes to the pipeline configuration.
        :param build_configuration: (experimental) Configuration options for the build process.
        :param description: (experimental) Description of the image pipeline.
        :param encryption: (experimental) KMS key for encryption.
        :param instance_types: (experimental) Instance types for the Image Builder Pipeline. Default: [t3.medium]
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param vpc_configuration: (experimental) VPC configuration for the image pipeline.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__737be13ffae0c45b3bddb7f3aafa412e381609e089f3c4cfe2bc669b2916689e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = Ec2ImagePipelineProps(
            block_device_mappings=block_device_mappings,
            components=components,
            machine_image=machine_image,
            version=version,
            build_configuration=build_configuration,
            description=description,
            encryption=encryption,
            instance_types=instance_types,
            lambda_configuration=lambda_configuration,
            vpc_configuration=vpc_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="imagePipelineArn")
    def image_pipeline_arn(self) -> builtins.str:
        '''(experimental) The Image Pipeline ARN that gets created.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "imagePipelineArn"))

    @builtins.property
    @jsii.member(jsii_name="imagePipelineTopic")
    def image_pipeline_topic(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
        '''(experimental) The Image Pipeline Topic that gets created.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, jsii.get(self, "imagePipelineTopic"))

    @builtins.property
    @jsii.member(jsii_name="latestAmi")
    def latest_ami(self) -> typing.Optional[builtins.str]:
        '''(experimental) The latest AMI built by the pipeline.

        NOTE: You must have enabled the
        Build Configuration option to wait for image build completion for this
        property to be available.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "latestAmi"))

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImagePipeline.BuildConfigurationProps",
        jsii_struct_bases=[],
        name_mapping={
            "start": "start",
            "hash": "hash",
            "wait_for_completion": "waitForCompletion",
        },
    )
    class BuildConfigurationProps:
        def __init__(
            self,
            *,
            start: builtins.bool,
            hash: typing.Optional[builtins.str] = None,
            wait_for_completion: typing.Optional[builtins.bool] = None,
        ) -> None:
            '''
            :param start: 
            :param hash: 
            :param wait_for_completion: 

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__27c54dc47bf0adadbe7c82a863cfc7874cd749dd459f64d5b19ac8e01b6d7bc1)
                check_type(argname="argument start", value=start, expected_type=type_hints["start"])
                check_type(argname="argument hash", value=hash, expected_type=type_hints["hash"])
                check_type(argname="argument wait_for_completion", value=wait_for_completion, expected_type=type_hints["wait_for_completion"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "start": start,
            }
            if hash is not None:
                self._values["hash"] = hash
            if wait_for_completion is not None:
                self._values["wait_for_completion"] = wait_for_completion

        @builtins.property
        def start(self) -> builtins.bool:
            '''
            :stability: experimental
            '''
            result = self._values.get("start")
            assert result is not None, "Required property 'start' is missing"
            return typing.cast(builtins.bool, result)

        @builtins.property
        def hash(self) -> typing.Optional[builtins.str]:
            '''
            :stability: experimental
            '''
            result = self._values.get("hash")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def wait_for_completion(self) -> typing.Optional[builtins.bool]:
            '''
            :stability: experimental
            '''
            result = self._values.get("wait_for_completion")
            return typing.cast(typing.Optional[builtins.bool], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BuildConfigurationProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.enum(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImagePipeline.Component"
    )
    class Component(enum.Enum):
        '''(experimental) Image Builder Component.

        :stability: experimental
        '''

        AMAZON_CLOUDWATCH_AGENT_LINUX = "AMAZON_CLOUDWATCH_AGENT_LINUX"
        '''(experimental) Installs the latest version of the Amazon CloudWatch agent.

        This component installs only the agent. You must take additional steps to configure and use the Amazon CloudWatch agent. For more information, see the documentation at https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Agent-on-EC2-Instance.html.

        :stability: experimental
        '''
        AMAZON_CLOUDWATCH_AGENT_WINDOWS = "AMAZON_CLOUDWATCH_AGENT_WINDOWS"
        '''(experimental) Installs the latest version of the Amazon CloudWatch agent.

        This component installs only the agent. You must take additional steps to configure and use the Amazon CloudWatch agent. For more information, see the documentation at https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Agent-on-EC2-Instance.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_11_APT_GENERIC = "AMAZON_CORRETTO_11_APT_GENERIC"
        '''(experimental) Installs Amazon Corretto 11 for Debian-based Linux platforms in accordance with the Amazon Corretto 11 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-11-ug/generic-linux-install.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_11_HEADLESS = "AMAZON_CORRETTO_11_HEADLESS"
        '''(experimental) Installs Amazon Corretto 11 Headless.

        :stability: experimental
        '''
        AMAZON_CORRETTO_11_RPM_GENERIC = "AMAZON_CORRETTO_11_RPM_GENERIC"
        '''(experimental) Installs Amazon Corretto 11 for RPM-based Linux platforms in accordance with the Amazon Corretto 11 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-11-ug/generic-linux-install.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_11_WINDOWS = "AMAZON_CORRETTO_11_WINDOWS"
        '''(experimental) Installs Amazon Corretto 11 for Windows in accordance with the Amazon Corretto 11 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-11-ug/windows-7-install.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_11 = "AMAZON_CORRETTO_11"
        '''(experimental) Installs Amazon Corretto 11.

        :stability: experimental
        '''
        AMAZON_CORRETTO_17_HEADLESS = "AMAZON_CORRETTO_17_HEADLESS"
        '''(experimental) Installs Amazon Corretto 17 Headless.

        :stability: experimental
        '''
        AMAZON_CORRETTO_17_JDK = "AMAZON_CORRETTO_17_JDK"
        '''(experimental) Installs Amazon Corretto 17 JDK in accordance with the Amazon Corretto 17 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-17-ug/linux-info.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_17_JRE = "AMAZON_CORRETTO_17_JRE"
        '''(experimental) Installs Amazon Corretto 17 JRE.

        :stability: experimental
        '''
        AMAZON_CORRETTO_17_WINDOWS = "AMAZON_CORRETTO_17_WINDOWS"
        '''(experimental) Installs Amazon Corretto 17 for Windows in accordance with the Amazon Corretto 17 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-17-ug/windows-7-install.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_21_HEADLESS = "AMAZON_CORRETTO_21_HEADLESS"
        '''(experimental) Installs Amazon Corretto 21 Headless.

        :stability: experimental
        '''
        AMAZON_CORRETTO_21_JDK = "AMAZON_CORRETTO_21_JDK"
        '''(experimental) Installs Amazon Corretto 21 JDK in accordance with the Amazon Corretto 21 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-21-ug/linux-info.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_21_JRE = "AMAZON_CORRETTO_21_JRE"
        '''(experimental) Installs Amazon Corretto 21 JRE.

        :stability: experimental
        '''
        AMAZON_CORRETTO_21_WINDOWS = "AMAZON_CORRETTO_21_WINDOWS"
        '''(experimental) Installs Amazon Corretto 21 for Windows in accordance with the Amazon Corretto 21 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-21-ug/windows-10-install.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_8_APT_GENERIC = "AMAZON_CORRETTO_8_APT_GENERIC"
        '''(experimental) Installs Amazon Corretto 8 for Debian-based Linux platforms in accordance with the Amazon Corretto 8 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-8-ug/generic-linux-install.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_8_JDK = "AMAZON_CORRETTO_8_JDK"
        '''(experimental) Installs Amazon Corretto 8 JDK.

        :stability: experimental
        '''
        AMAZON_CORRETTO_8_JRE = "AMAZON_CORRETTO_8_JRE"
        '''(experimental) Installs Amazon Corretto 8 JRE.

        :stability: experimental
        '''
        AMAZON_CORRETTO_8_RPM_GENERIC = "AMAZON_CORRETTO_8_RPM_GENERIC"
        '''(experimental) Installs Amazon Corretto 8 for RPM-based Linux platforms in accordance with the Amazon Corretto 8 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-8-ug/generic-linux-install.html.

        :stability: experimental
        '''
        AMAZON_CORRETTO_8_WINDOWS = "AMAZON_CORRETTO_8_WINDOWS"
        '''(experimental) Installs Amazon Corretto 8 for Windows in accordance with the Amazon Corretto 8 User Guide at https://docs.aws.amazon.com/corretto/latest/corretto-8-ug/windows-7-install.html.

        :stability: experimental
        '''
        AMAZON_KINESIS_AGENT_WINDOWS = "AMAZON_KINESIS_AGENT_WINDOWS"
        '''(experimental) Installs the latest version of Amazon Kinesis Agent for Windows.

        :stability: experimental
        '''
        ANACONDA_WINDOWS = "ANACONDA_WINDOWS"
        '''(experimental) Installs the Anaconda distribution and environments for Tensorflow, PyTorch, and MXNet.

        :stability: experimental
        '''
        APACHE_TOMCAT_9_LINUX = "APACHE_TOMCAT_9_LINUX"
        '''(experimental) Installs the latest version of Apache Tomcat and the JRE, sets required environment variables, and schedules Tomcat to run on startup.

        :stability: experimental
        '''
        APT_REPOSITORY_TEST_LINUX = "APT_REPOSITORY_TEST_LINUX"
        '''(experimental) Tests whether the apt package manager is functioning correctly.

        :stability: experimental
        '''
        AWS_CLI_VERSION_2_LINUX = "AWS_CLI_VERSION_2_LINUX"
        '''(experimental) Installs the latest version of the AWS CLI version 2, and creates the symlink /usr/bin/aws that points to the installed application.

        For more information, see https://docs.aws.amazon.com/cli/latest/userguide/.

        :stability: experimental
        '''
        AWS_CLI_VERSION_2_WINDOWS = "AWS_CLI_VERSION_2_WINDOWS"
        '''(experimental) Installs the latest version of the AWS CLI version 2.

        For more information, review the user guide at https://docs.aws.amazon.com/cli/latest/userguide/.

        :stability: experimental
        '''
        AWS_CODEDEPLOY_AGENT_LINUX = "AWS_CODEDEPLOY_AGENT_LINUX"
        '''(experimental) Installs the latest version of the AWS CodeDeploy agent.

        This component installs only the agent. You must take additional steps to configure and use the AWS CodeDeploy agent. For more information, see the documentation at https://docs.aws.amazon.com/codedeploy/latest/userguide/welcome.html.

        :stability: experimental
        '''
        AWS_CODEDEPLOY_AGENT_WINDOWS = "AWS_CODEDEPLOY_AGENT_WINDOWS"
        '''(experimental) Installs the latest version of the AWS CodeDeploy agent.

        This component installs only the agent. You must take additional steps to configure and use the agent. For more information, see the documentation at https://docs.aws.amazon.com/codedeploy/latest/userguide/codedeploy-agent-operations-install-windows.html.

        :stability: experimental
        '''
        AWS_VSS_COMPONENTS_WINDOWS = "AWS_VSS_COMPONENTS_WINDOWS"
        '''(experimental) Installs the AwsVssComponents Distributor package on a Windows instance.

        The instance must have an AWS Tools for PowerShell version that includes Systems Manager modules installed. The IAM profile attached to the build instance must have the following permissions - configure the ssm:SendCommand permission with the AWS-ConfigureAWSPackage Systems Manager document on all instances in the Region, and configure the ssm:GetCommandInvocation permission for '*'. For more information, see the documentation at https://docs.aws.amazon.com/imagebuilder/latest/userguide/mgdcomponent-distributor-win.html and https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/application-consistent-snapshots.html.

        :stability: experimental
        '''
        CHOCOLATEY = "CHOCOLATEY"
        '''(experimental) Installs Chocolatey for Windows.

        :stability: experimental
        '''
        CHRONY_TIME_CONFIGURATION_TEST = "CHRONY_TIME_CONFIGURATION_TEST"
        '''(experimental) Validates the Chrony configuration file and ensures that Chrony time sources on Amazon Linux 2 are configured for the Amazon time servers.

        Uses validation steps outlined here: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html.

        :stability: experimental
        '''
        DCV_SERVER_LINUX = "DCV_SERVER_LINUX"
        '''(experimental) Install and configure the latest NICE DCV server on Linux.

        :stability: experimental
        '''
        DCV_SERVER_WINDOWS = "DCV_SERVER_WINDOWS"
        '''(experimental) Install and configure the latest NICE DCV server on Windows.

        :stability: experimental
        '''
        DISTRIBUTOR_PACKAGE_WINDOWS = "DISTRIBUTOR_PACKAGE_WINDOWS"
        '''(experimental) Installs a Distributor package on a Windows instance.

        The instance must have an AWS Tools for PowerShell version that includes Systems Manager modules installed. The IAM profile attached to the build instance must have the following permissions - configure the ssm:SendCommand permission with the AWS-ConfigureAWSPackage Systems Manager document on all instances in the Region, and configure the ssm:GetCommandInvocation permission for '*'. For more information, see the documentation at https://docs.aws.amazon.com/imagebuilder/latest/userguide/mgdcomponent-distributor-win.html.

        :stability: experimental
        '''
        DOCKER_CE_CENTOS = "DOCKER_CE_CENTOS"
        '''(experimental) Installs Docker Community Edition from the Docker package repository, and enables the centos user to manage Docker without using sudo.

        For more information, review the installation guide at https://docs.docker.com/install/linux/docker-ce/centos/.

        :stability: experimental
        '''
        DOCKER_CE_LINUX = "DOCKER_CE_LINUX"
        '''(experimental) Install the latest Docker Community Edition from Amazon Linux Extras, and enable the ec2-user user to manage docker without using sudo.

        :stability: experimental
        '''
        DOCKER_CE_UBUNTU = "DOCKER_CE_UBUNTU"
        '''(experimental) Installs Docker Community Edition from the Docker package repository, and enables the ubuntu user to manage Docker without using sudo.

        For more information, review the installation guide at https://docs.docker.com/install/linux/docker-ce/ubuntu/.

        :stability: experimental
        '''
        DOTNET_DESKTOP_RUNTIME_LTS_WINDOWS = "DOTNET_DESKTOP_RUNTIME_LTS_WINDOWS"
        '''(experimental) Installs the latest 8.0 channel release of the Microsoft .NET Desktop Runtime. For more information, see the .NET 8.0 download page at https://dotnet.microsoft.com/download/dotnet/8.0.

        :stability: experimental
        '''
        DOTNET_HOSTING_BUNDLE_LTS_WINDOWS = "DOTNET_HOSTING_BUNDLE_LTS_WINDOWS"
        '''(experimental) Installs the latest 8.0 channel release of the Microsoft .NET Hosting Bundle. For more information, see the .NET 8.0 download page at https://dotnet.microsoft.com/download/dotnet/8.0.

        :stability: experimental
        '''
        DOTNET_RUNTIME_LTS_LINUX = "DOTNET_RUNTIME_LTS_LINUX"
        '''(experimental) Installs the latest 8.0 channel release of the Microsoft .NET Runtime. For more information, see the .NET 8.0 download page at https://dotnet.microsoft.com/download/dotnet/8.0.

        :stability: experimental
        '''
        DOTNET_RUNTIME_LTS_WINDOWS = "DOTNET_RUNTIME_LTS_WINDOWS"
        '''(experimental) Installs the latest 8.0 channel release of the Microsoft .NET Runtime. For more information, see the .NET 8.0 download page at https://dotnet.microsoft.com/download/dotnet/8.0.

        :stability: experimental
        '''
        DOTNET_SDK_LTS_LINUX = "DOTNET_SDK_LTS_LINUX"
        '''(experimental) Installs the latest 8.0 channel release of the Microsoft .NET SDK. For more information, see the .NET 8.0 download page at https://dotnet.microsoft.com/download/dotnet/8.0.

        :stability: experimental
        '''
        DOTNET_SDK_LTS_WINDOWS = "DOTNET_SDK_LTS_WINDOWS"
        '''(experimental) Installs the latest 8.0 channel release of the Microsoft .NET SDK. For more information, see the .NET 8.0 download page at https://dotnet.microsoft.com/download/dotnet/8.0.

        :stability: experimental
        '''
        EBS_VOLUME_USAGE_TEST_LINUX = "EBS_VOLUME_USAGE_TEST_LINUX"
        '''(experimental) The EBS volume usage test performs the following actions: 1) It creates an EBS volume and attaches it to the instance.

        1. It creates a temporary file on the volume and detaches the volume. 3) It reattaches the volume and validates that the file exists. 4) It detaches and deletes the volume. To perform this test, an IAM policy with the following actions is required: ec2:AttachVolume, ec2:Create Tags, ec2:CreateVolume, ec2:DeleteVolume, ec2:DescribeVolumes, and ec2:DetachVolume.

        :stability: experimental
        '''
        EBS_VOLUME_USAGE_TEST_WINDOWS = "EBS_VOLUME_USAGE_TEST_WINDOWS"
        '''(experimental) The EBS volume usage test performs the following actions: 1) It creates an EBS volume and attaches it to the instance.

        1. It creates a temporary file on the volume and detaches the volume. 3) It reattaches the volume and validates that the file exists. 4) It detaches and deletes the volume. To perform this test, an IAM policy with the following actions is required: ec2:AttachVolume, ec2:Create Tags, ec2:CreateVolume, ec2:DeleteVolume, ec2:DescribeVolumes, and ec2:DetachVolume.

        :stability: experimental
        '''
        EC2_NETWORK_ROUTE_TEST_WINDOWS = "EC2_NETWORK_ROUTE_TEST_WINDOWS"
        '''(experimental) Test to ensure all required EC2 network routes exist in the route table.

        :stability: experimental
        '''
        EC2LAUNCH_V2_WINDOWS = "EC2LAUNCH_V2_WINDOWS"
        '''(experimental) Installs the latest version of EC2Launch v2.

        For more information, see the documentation at https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/ec2launch-v2.html.

        :stability: experimental
        '''
        ECS_OPTIMIZED_AMI_WINDOWS = "ECS_OPTIMIZED_AMI_WINDOWS"
        '''(experimental) Installs Amazon ECS-optimized Windows artifacts.

        This includes latest Amazon ECS Container Agent and Docker CE version 20.10.21.

        :stability: experimental
        '''
        EKS_OPTIMIZED_AMI_WINDOWS = "EKS_OPTIMIZED_AMI_WINDOWS"
        '''(experimental) Installs Amazon EKS-optimized Windows artifacts for Amazon EKS version 1.32. This includes kubelet version 1.32.0, containerd version 1.7.20, and CSI Proxy version 1.1.2.

        :stability: experimental
        '''
        ENI_ATTACHMENT_TEST_LINUX = "ENI_ATTACHMENT_TEST_LINUX"
        '''(experimental) The ENI attachment test performs the following actions: 1) It creates an elastic network interface (ENI) and attaches it to the instance.

        1. It validates that the attached ENI has an IP address. 3) It detaches and deletes the ENI. To perform this test, an IAM policy with the following actions is required: ec2:AttachNetworkInterface, ec2:CreateNetworkInterface, ec2:CreateTags, ec2:DeleteNetworkInterface, ec2:DescribeNetworkInterfaces, ec2:DescribeNetworkInterfaceAttribute, and ec2:DetachNetworkInterface.

        :stability: experimental
        '''
        ENI_ATTACHMENT_TEST_WINDOWS = "ENI_ATTACHMENT_TEST_WINDOWS"
        '''(experimental) The ENI attachment test performs the following actions: 1) It creates an elastic network interface (ENI) and attaches it to the instance.

        1. It validates that the attached ENI has an IP address. 3) It detaches and deletes the ENI. To perform this test, an IAM policy with the following actions is required: ec2:AttachNetworkInterface, ec2:CreateNetworkInterface, ec2:CreateTags, ec2:DeleteNetworkInterface, ec2:DescribeNetworkInterfaces, ec2:DescribeNetworkInterfaceAttribute, and ec2:DetachNetworkInterface.

        :stability: experimental
        '''
        GO_STABLE_LINUX = "GO_STABLE_LINUX"
        '''(experimental) Installs the latest stable release of the Go programming language using the release information from https://go.dev/dl/.

        :stability: experimental
        '''
        GO_STABLE_WINDOWS = "GO_STABLE_WINDOWS"
        '''(experimental) Installs the latest stable release of the Go programming language using the release information from https://go.dev/dl/.

        :stability: experimental
        '''
        HELLO_WORLD_LINUX = "HELLO_WORLD_LINUX"
        '''(experimental) Hello world testing document for Linux.

        :stability: experimental
        '''
        HELLO_WORLD_WINDOWS = "HELLO_WORLD_WINDOWS"
        '''(experimental) Hello world testing document for Windows.

        :stability: experimental
        '''
        INSPECTOR_TEST_LINUX = "INSPECTOR_TEST_LINUX"
        '''(experimental) Performs a Center for Internet Security (CIS) security assessment for an instance, using Amazon Inspector (Inspector).

        This component performs the following actions: 1) It installs the Inspector agent. 2) It creates a resource group, assessment target, and assessment template. 3) It runs the assessment and provides a link to the results in the logs and on the Inspector Service console. In order to run successfully, this component requires that the AmazonInspectorFullAccess IAM policy and the ssm:SendCommand and ec2:CreateTags IAM permissions are attached to the instance profile. To find the list of supported Operating Systems and their rules packages, refer to the Inspector documentation https://docs.aws.amazon.com/inspector/v1/userguide/inspector_rule-packages_across_os.html.

        :stability: experimental
        '''
        INSPECTOR_TEST_WINDOWS = "INSPECTOR_TEST_WINDOWS"
        '''(experimental) Performs a Center for Internet Security (CIS) security assessment for an instance, using Amazon Inspector (Inspector).

        This component performs the following actions: 1) It installs the Inspector agent. 2) It creates a resource group, assessment target, and assessment template. 3) It runs the assessment and provides a link to the results in the logs and on the Inspector Service console. In order to run successfully, this component requires that the AmazonInspectorFullAccess IAM policy and the ssm:SendCommand and ec2:CreateTags IAM permissions are attached to the instance profile. To find the list of supported Operating Systems and their rules packages, refer to the Inspector documentation https://docs.aws.amazon.com/inspector/v1/userguide/inspector_rule-packages_across_os.html.

        :stability: experimental
        '''
        INSTALL_PACKAGE_FROM_REPOSITORY = "INSTALL_PACKAGE_FROM_REPOSITORY"
        '''(experimental) Installs a package from the Linux repository.

        :stability: experimental
        '''
        MARIADB_LINUX = "MARIADB_LINUX"
        '''(experimental) Installs the MariaDB package using apt, yum, or zypper.

        :stability: experimental
        '''
        MATE_DE_LINUX = "MATE_DE_LINUX"
        '''(experimental) Installs the MATE Desktop Environment, xrdp, TigerVNC server, and enables the xrdp service.

        :stability: experimental
        '''
        MONO_LINUX = "MONO_LINUX"
        '''(experimental) Installs the latest version of the Mono framework.

        Follows the instructions found at https://www.mono-project.com/.

        :stability: experimental
        '''
        PHP_8_2_LINUX = "PHP_8_2_LINUX"
        '''(experimental) Installs PHP 8.2.

        :stability: experimental
        '''
        POWERSHELL_LTS_LINUX = "POWERSHELL_LTS_LINUX"
        '''(experimental) Installs the latest LTS 7.4 release of PowerShell following the instructions at https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-linux?view=powershell-7.4.

        :stability: experimental
        '''
        POWERSHELL_LTS_WINDOWS = "POWERSHELL_LTS_WINDOWS"
        '''(experimental) Installs the latest LTS 7.4 release of PowerShell using the MSI installer from the GitHub repository located at https://github.com/PowerShell/PowerShell.

        :stability: experimental
        '''
        POWERSHELL_SNAP = "POWERSHELL_SNAP"
        '''(experimental) Installs the latest version of PowerShell using snap.

        :stability: experimental
        '''
        POWERSHELL_YUM = "POWERSHELL_YUM"
        '''(experimental) Installs the latest version of PowerShell from the Microsoft RedHat repository.

        :stability: experimental
        '''
        PUTTY = "PUTTY"
        '''(experimental) Installs the latest version of PuTTY from the 64-bit MSI link on the release page: https://the.earth.li/~sgtatham/putty/latest/w64/.

        :stability: experimental
        '''
        PYTHON_3_LINUX = "PYTHON_3_LINUX"
        '''(experimental) Installs the Python 3 package using apt, yum, or zypper.

        :stability: experimental
        '''
        PYTHON_3_WINDOWS = "PYTHON_3_WINDOWS"
        '''(experimental) Installs Python 3.8.2 for Windows.

        :stability: experimental
        '''
        REBOOT_LINUX = "REBOOT_LINUX"
        '''(experimental) Reboots the system.

        :stability: experimental
        '''
        REBOOT_TEST_LINUX = "REBOOT_TEST_LINUX"
        '''(experimental) Tests whether the system can reboot successfully.

        :stability: experimental
        '''
        REBOOT_TEST_WINDOWS = "REBOOT_TEST_WINDOWS"
        '''(experimental) Tests whether the system can reboot successfully.

        :stability: experimental
        '''
        REBOOT_WINDOWS = "REBOOT_WINDOWS"
        '''(experimental) Reboots the system.

        :stability: experimental
        '''
        SCAP_COMPLIANCE_CHECKER_LINUX = "SCAP_COMPLIANCE_CHECKER_LINUX"
        '''(experimental) Installs and runs SCAP Compliance Checker (SCC) 5.10 for Red Hat Enterprise Linux (RHEL) 7/8, Ubuntu 18.04/20.04/22.04 with all current STIG Q1 2025 benchmarks. SCC supports the AMD64 architecture. Other architectures are not currently supported or contain issues within the EC2 environment. For more information, see https://docs.aws.amazon.com/imagebuilder/latest/userguide/toe-stig.html.

        :stability: experimental
        '''
        SCAP_COMPLIANCE_CHECKER_WINDOWS = "SCAP_COMPLIANCE_CHECKER_WINDOWS"
        '''(experimental) Installs and runs SCAP Compliance Checker (SCC) 5.10 for Windows with all current STIG Q3 2024 benchmarks. For more information, see https://docs.aws.amazon.com/imagebuilder/latest/userguide/image-builder-stig.html.

        :stability: experimental
        '''
        SIMPLE_BOOT_TEST_LINUX = "SIMPLE_BOOT_TEST_LINUX"
        '''(experimental) Executes a simple boot test.

        :stability: experimental
        '''
        SIMPLE_BOOT_TEST_WINDOWS = "SIMPLE_BOOT_TEST_WINDOWS"
        '''(experimental) Executes a simple boot test.

        :stability: experimental
        '''
        STIG_BUILD_LINUX_HIGH = "STIG_BUILD_LINUX_HIGH"
        '''(experimental) Applies the high, medium, and low severity STIG settings for Red Hat Enterprise Linux (RHEL) to Amazon Linux 2, Amazon Linux 2023, RHEL 7, CentOS Linux 7, CentOS Linux 8, CentOS Stream 9, RHEL 8, RHEL 9, Ubuntu 18.04, Ubuntu 20.04, and Ubuntu 22.04 instances. For more information, see https://docs.aws.amazon.com/imagebuilder/latest/userguide/toe-stig.html.

        :stability: experimental
        '''
        STIG_BUILD_LINUX_LOW = "STIG_BUILD_LINUX_LOW"
        '''(experimental) Applies the low severity STIG settings for Red Hat Enterprise Linux (RHEL) to Amazon Linux 2, Amazon Linux 2023, RHEL 7, CentOS Linux 7, CentOS Linux 8, CentOS Stream 9, RHEL 8, RHEL 9, Ubuntu 18.04, Ubuntu 20.04, and Ubuntu 22.04 instances. For more information, see https://docs.aws.amazon.com/imagebuilder/latest/userguide/toe-stig.html.

        :stability: experimental
        '''
        STIG_BUILD_LINUX_MEDIUM = "STIG_BUILD_LINUX_MEDIUM"
        '''(experimental) Applies the medium and low severity STIG settings for Red Hat Enterprise Linux (RHEL) to Amazon Linux 2, Amazon Linux 2023, RHEL 7, CentOS Linux 7, CentOS Linux 8, CentOS Stream 9, RHEL 8, RHEL 9, Ubuntu 18.04, Ubuntu 20.04, and Ubuntu 22.04 instances. For more information, see https://docs.aws.amazon.com/imagebuilder/latest/userguide/toe-stig.html.

        :stability: experimental
        '''
        STIG_BUILD_WINDOWS_HIGH = "STIG_BUILD_WINDOWS_HIGH"
        '''(experimental) Applies the high, medium, and low severity STIG settings to Windows instances.

        For more information, see https://docs.aws.amazon.com/imagebuilder/latest/userguide/image-builder-stig.html.

        :stability: experimental
        '''
        STIG_BUILD_WINDOWS_LOW = "STIG_BUILD_WINDOWS_LOW"
        '''(experimental) Applies the low severity STIG settings to Windows instances.

        For more information, see https://docs.aws.amazon.com/imagebuilder/latest/userguide/image-builder-stig.html.

        :stability: experimental
        '''
        STIG_BUILD_WINDOWS_MEDIUM = "STIG_BUILD_WINDOWS_MEDIUM"
        '''(experimental) Applies the medium and low severity STIG settings to Windows instances.

        For more information, see https://docs.aws.amazon.com/imagebuilder/latest/userguide/image-builder-stig.html.

        :stability: experimental
        '''
        UPDATE_LINUX_KERNEL_5 = "UPDATE_LINUX_KERNEL_5"
        '''(experimental) Installs the Linux kernel 5.* for Amazon Linux 2 from Amazon Linux Extras.

        :stability: experimental
        '''
        UPDATE_LINUX_KERNEL_ML = "UPDATE_LINUX_KERNEL_ML"
        '''(experimental) Installs the latest mainline release of the Linux kernel for CentOS 7 and Red Hat Enterprise Linux 7 and 8 via the 'kernel-ml' package from https://www.elrepo.org.

        :stability: experimental
        '''
        UPDATE_LINUX = "UPDATE_LINUX"
        '''(experimental) Updates Linux by installing all available updates via the UpdateOS action module.

        :stability: experimental
        '''
        UPDATE_WINDOWS = "UPDATE_WINDOWS"
        '''(experimental) Updates Windows with the latest security updates.

        :stability: experimental
        '''
        VALIDATE_SINGLE_SSH_PUBLIC_KEY_TEST_LINUX = "VALIDATE_SINGLE_SSH_PUBLIC_KEY_TEST_LINUX"
        '''(experimental) Ensures the ``authorized_keys`` file contains only the SSH public key returned from the EC2 Instance Metadata Service.

        :stability: experimental
        '''
        VALIDATE_SSH_HOST_KEY_GENERATION_LINUX = "VALIDATE_SSH_HOST_KEY_GENERATION_LINUX"
        '''(experimental) Verifies whether the SSH host key was generated after the latest boot.

        :stability: experimental
        '''
        VALIDATE_SSH_PUBLIC_KEY_LINUX = "VALIDATE_SSH_PUBLIC_KEY_LINUX"
        '''(experimental) Ensures the ``authorized_keys`` file contains the SSH public key returned from the EC2 Instance Metadata Service.

        :stability: experimental
        '''
        WINDOWS_ACTIVATION_TEST = "WINDOWS_ACTIVATION_TEST"
        '''(experimental) Verifies the Windows license status in the Common Information Model.

        :stability: experimental
        '''
        WINDOWS_IS_READY_WITH_PASSWORD_GENERATION_TEST = "WINDOWS_IS_READY_WITH_PASSWORD_GENERATION_TEST"
        '''(experimental) Checks the EC2 logs for the statement ``Windows is Ready to use`` and for the password generation message on Windows Server 2016 and later SKUs.

        This component does not support instances launched without an EC2 key pair.

        :stability: experimental
        '''
        WINDOWS_SERVER_IIS = "WINDOWS_SERVER_IIS"
        '''(experimental) Installs the Internet Information Services (IIS) web server and management tools.

        The installation is performed by enabling the Windows features built into the Windows operating system.

        :stability: experimental
        '''
        YUM_REPOSITORY_TEST_LINUX = "YUM_REPOSITORY_TEST_LINUX"
        '''(experimental) Tests whether yum repository works successfully.

        :stability: experimental
        '''

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImagePipeline.VpcConfigurationProps",
        jsii_struct_bases=[],
        name_mapping={
            "vpc": "vpc",
            "security_group": "securityGroup",
            "subnet": "subnet",
        },
    )
    class VpcConfigurationProps:
        def __init__(
            self,
            *,
            vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
            security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
            subnet: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet] = None,
        ) -> None:
            '''(experimental) VPC Configuration.

            :param vpc: 
            :param security_group: 
            :param subnet: 

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__fcde20831541d1ff69c140ecf8eb01c2fa26796a4dbab5ece7343e4d177ec4c3)
                check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
                check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
                check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "vpc": vpc,
            }
            if security_group is not None:
                self._values["security_group"] = security_group
            if subnet is not None:
                self._values["subnet"] = subnet

        @builtins.property
        def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
            '''
            :stability: experimental
            '''
            result = self._values.get("vpc")
            assert result is not None, "Required property 'vpc' is missing"
            return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

        @builtins.property
        def security_group(
            self,
        ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
            '''
            :stability: experimental
            '''
            result = self._values.get("security_group")
            return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

        @builtins.property
        def subnet(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
            '''
            :stability: experimental
            '''
            result = self._values.get("subnet")
            return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VpcConfigurationProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImagePipelineBaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "version": "version",
        "build_configuration": "buildConfiguration",
        "description": "description",
        "encryption": "encryption",
        "instance_types": "instanceTypes",
        "lambda_configuration": "lambdaConfiguration",
        "vpc_configuration": "vpcConfiguration",
    },
)
class Ec2ImagePipelineBaseProps:
    def __init__(
        self,
        *,
        version: builtins.str,
        build_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Base properties for EC2 Image Pipeline configuration.

        :param version: (experimental) Version of the image pipeline. This must be updated if you make underlying changes to the pipeline configuration.
        :param build_configuration: (experimental) Configuration options for the build process.
        :param description: (experimental) Description of the image pipeline.
        :param encryption: (experimental) KMS key for encryption.
        :param instance_types: (experimental) Instance types for the Image Builder Pipeline. Default: [t3.medium]
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param vpc_configuration: (experimental) VPC configuration for the image pipeline.

        :stability: experimental
        '''
        if isinstance(build_configuration, dict):
            build_configuration = Ec2ImagePipeline.BuildConfigurationProps(**build_configuration)
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if isinstance(vpc_configuration, dict):
            vpc_configuration = Ec2ImagePipeline.VpcConfigurationProps(**vpc_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__802e96348c8a99aa2d3111175157a3a3a4b1b7f66997ab3055d8dd76318b4809)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument build_configuration", value=build_configuration, expected_type=type_hints["build_configuration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
            check_type(argname="argument vpc_configuration", value=vpc_configuration, expected_type=type_hints["vpc_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
        }
        if build_configuration is not None:
            self._values["build_configuration"] = build_configuration
        if description is not None:
            self._values["description"] = description
        if encryption is not None:
            self._values["encryption"] = encryption
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration
        if vpc_configuration is not None:
            self._values["vpc_configuration"] = vpc_configuration

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Version of the image pipeline.

        This must be updated if you make
        underlying changes to the pipeline configuration.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_configuration(
        self,
    ) -> typing.Optional[Ec2ImagePipeline.BuildConfigurationProps]:
        '''(experimental) Configuration options for the build process.

        :stability: experimental
        '''
        result = self._values.get("build_configuration")
        return typing.cast(typing.Optional[Ec2ImagePipeline.BuildConfigurationProps], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of the image pipeline.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) KMS key for encryption.

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Instance types for the Image Builder Pipeline.

        Default: [t3.medium]

        :stability: experimental
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def lambda_configuration(self) -> typing.Optional[_LambdaConfiguration_9f8afc24]:
        '''(experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_LambdaConfiguration_9f8afc24], result)

    @builtins.property
    def vpc_configuration(
        self,
    ) -> typing.Optional[Ec2ImagePipeline.VpcConfigurationProps]:
        '''(experimental) VPC configuration for the image pipeline.

        :stability: experimental
        '''
        result = self._values.get("vpc_configuration")
        return typing.cast(typing.Optional[Ec2ImagePipeline.VpcConfigurationProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ec2ImagePipelineBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.Ec2ImagePipelineProps",
    jsii_struct_bases=[Ec2ImagePipelineBaseProps],
    name_mapping={
        "version": "version",
        "build_configuration": "buildConfiguration",
        "description": "description",
        "encryption": "encryption",
        "instance_types": "instanceTypes",
        "lambda_configuration": "lambdaConfiguration",
        "vpc_configuration": "vpcConfiguration",
        "block_device_mappings": "blockDeviceMappings",
        "components": "components",
        "machine_image": "machineImage",
    },
)
class Ec2ImagePipelineProps(Ec2ImagePipelineBaseProps):
    def __init__(
        self,
        *,
        version: builtins.str,
        build_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
        block_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        components: typing.Optional[typing.Sequence[typing.Union[Ec2ImagePipeline.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
        machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    ) -> None:
        '''(experimental) Properties for EC2 Image Pipeline, extending the base properties.

        :param version: (experimental) Version of the image pipeline. This must be updated if you make underlying changes to the pipeline configuration.
        :param build_configuration: (experimental) Configuration options for the build process.
        :param description: (experimental) Description of the image pipeline.
        :param encryption: (experimental) KMS key for encryption.
        :param instance_types: (experimental) Instance types for the Image Builder Pipeline. Default: [t3.medium]
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param vpc_configuration: (experimental) VPC configuration for the image pipeline.
        :param block_device_mappings: (experimental) Block device mappings for the image.
        :param components: (experimental) Components to be included in the image pipeline. Can be either custom Ec2ImagePipeline.Component or AWS CDK imagebuilder.CfnComponent.
        :param machine_image: (experimental) The machine image to use as a base for the pipeline. Default: AmazonLinux2023

        :stability: experimental
        '''
        if isinstance(build_configuration, dict):
            build_configuration = Ec2ImagePipeline.BuildConfigurationProps(**build_configuration)
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if isinstance(vpc_configuration, dict):
            vpc_configuration = Ec2ImagePipeline.VpcConfigurationProps(**vpc_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a39e35bb21d08f951c8d42be5f389f8950b3c94272d8b6641ca758840295ee47)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument build_configuration", value=build_configuration, expected_type=type_hints["build_configuration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
            check_type(argname="argument vpc_configuration", value=vpc_configuration, expected_type=type_hints["vpc_configuration"])
            check_type(argname="argument block_device_mappings", value=block_device_mappings, expected_type=type_hints["block_device_mappings"])
            check_type(argname="argument components", value=components, expected_type=type_hints["components"])
            check_type(argname="argument machine_image", value=machine_image, expected_type=type_hints["machine_image"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
        }
        if build_configuration is not None:
            self._values["build_configuration"] = build_configuration
        if description is not None:
            self._values["description"] = description
        if encryption is not None:
            self._values["encryption"] = encryption
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration
        if vpc_configuration is not None:
            self._values["vpc_configuration"] = vpc_configuration
        if block_device_mappings is not None:
            self._values["block_device_mappings"] = block_device_mappings
        if components is not None:
            self._values["components"] = components
        if machine_image is not None:
            self._values["machine_image"] = machine_image

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Version of the image pipeline.

        This must be updated if you make
        underlying changes to the pipeline configuration.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_configuration(
        self,
    ) -> typing.Optional[Ec2ImagePipeline.BuildConfigurationProps]:
        '''(experimental) Configuration options for the build process.

        :stability: experimental
        '''
        result = self._values.get("build_configuration")
        return typing.cast(typing.Optional[Ec2ImagePipeline.BuildConfigurationProps], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of the image pipeline.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) KMS key for encryption.

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Instance types for the Image Builder Pipeline.

        Default: [t3.medium]

        :stability: experimental
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def lambda_configuration(self) -> typing.Optional[_LambdaConfiguration_9f8afc24]:
        '''(experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_LambdaConfiguration_9f8afc24], result)

    @builtins.property
    def vpc_configuration(
        self,
    ) -> typing.Optional[Ec2ImagePipeline.VpcConfigurationProps]:
        '''(experimental) VPC configuration for the image pipeline.

        :stability: experimental
        '''
        result = self._values.get("vpc_configuration")
        return typing.cast(typing.Optional[Ec2ImagePipeline.VpcConfigurationProps], result)

    @builtins.property
    def block_device_mappings(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty]]:
        '''(experimental) Block device mappings for the image.

        :stability: experimental
        '''
        result = self._values.get("block_device_mappings")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty]], result)

    @builtins.property
    def components(
        self,
    ) -> typing.Optional[typing.List[typing.Union[Ec2ImagePipeline.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]]:
        '''(experimental) Components to be included in the image pipeline.

        Can be either custom Ec2ImagePipeline.Component or AWS CDK imagebuilder.CfnComponent.

        :stability: experimental
        '''
        result = self._values.get("components")
        return typing.cast(typing.Optional[typing.List[typing.Union[Ec2ImagePipeline.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]], result)

    @builtins.property
    def machine_image(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage]:
        '''(experimental) The machine image to use as a base for the pipeline.

        :default: AmazonLinux2023

        :stability: experimental
        '''
        result = self._values.get("machine_image")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ec2ImagePipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FriendlyEmbrace(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.FriendlyEmbrace",
):
    '''(experimental) The Friendly Embrace construct can be used to remove CloudFormation stack dependencies that are based on stack exports and imports.

    🚨 WARNING: This construct is experimental and will directly modify
    CloudFormation stacks in your CDK application via a Lambda-backed Custom
    Resource. It is not recommended to use this construct in a production
    environment.

    A custom resource that is designed to remove the "Deadly Embrace" problem that
    occurs when you attempt to update a CloudFormation stack that is exporting
    a resource used by another stack. This custom resource will run before all of
    your stacks deploy/update and remove the dependencies by hardcoding each
    export for all stacks that use it. For this reason, this construct should run
    inside of its own stack and should be the last stack that is instantiated for
    your application. That way the construct will be able to retrieve all of the
    stacks from your CDK resource tree that it needs to update.
    .. epigraph::

       NOTE: You may need to add more permissions to the handler if the custom
       resource cannot update your stacks. You can call upon the ``handler`` property
       of the class to add more permissions to it.

    :stability: experimental

    Example::

        import { App, Stack } from 'aws-cdk-lib';
        import { FriendlyEmbrace } from '@cdklabs/cdk-proserve-lib/constructs';
        
        const app = new App();
        // ... other stack definitions
        const embrace = new Stack(app, 'FriendlyEmbrace'); // last stack
        new FriendlyEmbrace(embrace, 'FriendlyEmbrace'); // only construct in stack
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket_configuration: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        ignore_invalid_states: typing.Optional[builtins.bool] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        manual_read_permissions: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    ) -> None:
        '''(experimental) The Friendly Embrace construct can be used to remove CloudFormation stack dependencies that are based on stack exports and imports.

        🚨 WARNING: This construct is experimental and will directly modify
        CloudFormation stacks in your CDK application via a Lambda-backed Custom
        Resource. It is not recommended to use this construct in a production
        environment.

        :param scope: The scope in which to define this construct.
        :param id: The construct ID.
        :param bucket_configuration: (experimental) Optional S3 Bucket configuration settings.
        :param encryption: (experimental) Encryption key for protecting the Lambda environment.
        :param ignore_invalid_states: (experimental) Whether or not stacks in error state should be fatal to CR completion.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param manual_read_permissions: (experimental) Manually provide specific read-only permissions for resources in your CloudFormation templates to support instead of using the AWS managed policy `ReadOnlyAccess <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/ReadOnlyAccess.html>`_. This can be useful in environments where the caller wants to maintain tight control over the permissions granted to the custom resource worker.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a08886230823f61b9ec19693d376c572b9161a1cb35e9536e22c6608d6f9af65)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FriendlyEmbraceProps(
            bucket_configuration=bucket_configuration,
            encryption=encryption,
            ignore_invalid_states=ignore_invalid_states,
            lambda_configuration=lambda_configuration,
            manual_read_permissions=manual_read_permissions,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="onEventHandler")
    def on_event_handler(self) -> _aws_cdk_aws_lambda_nodejs_ceddda9d.NodejsFunction:
        '''(experimental) Handler for the custom resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_nodejs_ceddda9d.NodejsFunction, jsii.get(self, "onEventHandler"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.FriendlyEmbraceProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_configuration": "bucketConfiguration",
        "encryption": "encryption",
        "ignore_invalid_states": "ignoreInvalidStates",
        "lambda_configuration": "lambdaConfiguration",
        "manual_read_permissions": "manualReadPermissions",
    },
)
class FriendlyEmbraceProps:
    def __init__(
        self,
        *,
        bucket_configuration: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        ignore_invalid_states: typing.Optional[builtins.bool] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        manual_read_permissions: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    ) -> None:
        '''(experimental) Input metadata for the custom resource.

        :param bucket_configuration: (experimental) Optional S3 Bucket configuration settings.
        :param encryption: (experimental) Encryption key for protecting the Lambda environment.
        :param ignore_invalid_states: (experimental) Whether or not stacks in error state should be fatal to CR completion.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param manual_read_permissions: (experimental) Manually provide specific read-only permissions for resources in your CloudFormation templates to support instead of using the AWS managed policy `ReadOnlyAccess <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/ReadOnlyAccess.html>`_. This can be useful in environments where the caller wants to maintain tight control over the permissions granted to the custom resource worker.

        :stability: experimental
        '''
        if isinstance(bucket_configuration, dict):
            bucket_configuration = _aws_cdk_aws_s3_ceddda9d.BucketProps(**bucket_configuration)
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a24b8202515587c00146de8fecdb544e867498ebe708c1272c2072200a7b12f)
            check_type(argname="argument bucket_configuration", value=bucket_configuration, expected_type=type_hints["bucket_configuration"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument ignore_invalid_states", value=ignore_invalid_states, expected_type=type_hints["ignore_invalid_states"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
            check_type(argname="argument manual_read_permissions", value=manual_read_permissions, expected_type=type_hints["manual_read_permissions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_configuration is not None:
            self._values["bucket_configuration"] = bucket_configuration
        if encryption is not None:
            self._values["encryption"] = encryption
        if ignore_invalid_states is not None:
            self._values["ignore_invalid_states"] = ignore_invalid_states
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration
        if manual_read_permissions is not None:
            self._values["manual_read_permissions"] = manual_read_permissions

    @builtins.property
    def bucket_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''(experimental) Optional S3 Bucket configuration settings.

        :stability: experimental
        '''
        result = self._values.get("bucket_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Encryption key for protecting the Lambda environment.

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def ignore_invalid_states(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not stacks in error state should be fatal to CR completion.

        :stability: experimental
        '''
        result = self._values.get("ignore_invalid_states")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lambda_configuration(self) -> typing.Optional[_LambdaConfiguration_9f8afc24]:
        '''(experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_LambdaConfiguration_9f8afc24], result)

    @builtins.property
    def manual_read_permissions(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''(experimental) Manually provide specific read-only permissions for resources in your CloudFormation templates to support instead of using the AWS managed policy `ReadOnlyAccess <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/ReadOnlyAccess.html>`_.

        This can be useful in environments where the caller wants to maintain tight control over the permissions granted
        to the custom resource worker.

        :stability: experimental
        '''
        result = self._values.get("manual_read_permissions")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FriendlyEmbraceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamServerCertificate(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.IamServerCertificate",
):
    '''(experimental) Manages an AWS Identity and Access Management Server Certificate for use in regions/partitions where AWS Certificate Manager is not available.

    This construct allows you to create an IAM Server Certificate using a certificate and private key stored in either
    AWS Systems Manager Parameter Store or AWS Secrets Manager. It uses a Custom Resource to manage the lifecycle of the
    server certificate.

    The construct also handles encryption for the framework resources using either a provided KMS key or an
    AWS managed key.

    :stability: experimental

    Example::

        import { Key } from 'aws-cdk-lib/aws-kms';
        import { Secret } from 'aws-cdk-lib/aws-secretsmanager';
        import { StringParameter } from 'aws-cdk-lib/aws-ssm';
        import { IamServerCertificate } from '@cdklabs/cdk-proserve-lib/constructs';
        
        const keyArn = 'arn:aws:kms:us-east-1:111111111111:key/sample-key-id';
        const key = Key.fromKeyArn(this, 'Encryption', keyArn);
        
        const certificateData = StringParameter.fromSecureStringParameterAttributes(this, 'CertificateData', {
             parameterName: 'sample-parameter',
             encryptionKey: key
        });
        
        const privateKeyData = Secret.fromSecretAttributes(this, 'PrivateKeySecret', {
             encryptionKey: key,
             secretCompleteArn: 'arn:aws:secretsmanager:us-east-1:111111111111:secret:PrivateKeySecret-aBc123'
        });
        
        const certificate = new IamServerCertificate(this, 'ServerCertificate', {
             certificate: {
                 parameter: certificateData,
                 encryption: key
             },
             privateKey: {
                 secret: privateKeyData,
                 encryption: key
             },
             prefix: 'myapp'
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        certificate: typing.Union[typing.Union["IamServerCertificate.ParameterProps", typing.Dict[builtins.str, typing.Any]], typing.Union["IamServerCertificate.SecretProps", typing.Dict[builtins.str, typing.Any]]],
        prefix: builtins.str,
        private_key: typing.Union[typing.Union["IamServerCertificate.ParameterProps", typing.Dict[builtins.str, typing.Any]], typing.Union["IamServerCertificate.SecretProps", typing.Dict[builtins.str, typing.Any]]],
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Creates a new AWS IAM Server Certificate.

        :param scope: Parent to which the Custom Resource belongs.
        :param id: Unique identifier for this instance.
        :param certificate: (experimental) AWS Systems Manager parameter or AWS Secrets Manager secret which contains the public certificate.
        :param prefix: (experimental) Prefix to prepend to the AWS IAM Server Certificate name.
        :param private_key: (experimental) AWS Systems Manager parameter or AWS Secrets Manager secret which contains the private key.
        :param encryption: (experimental) Encryption key for protecting the framework resources.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b83600751ad5ce20528131f4fb433a007a960e427a87ae702a9539150d2cc3dd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IamServerCertificateProps(
            certificate=certificate,
            prefix=prefix,
            private_key=private_key,
            encryption=encryption,
            lambda_configuration=lambda_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) ARN for the created AWS IAM Server Certificate.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.IamServerCertificate.ParameterProps",
        jsii_struct_bases=[],
        name_mapping={"parameter": "parameter", "encryption": "encryption"},
    )
    class ParameterProps:
        def __init__(
            self,
            *,
            parameter: _aws_cdk_aws_ssm_ceddda9d.IParameter,
            encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        ) -> None:
            '''(experimental) Properties for a server certificate element when it is stored in AWS Systems Manager Parameter Store.

            :param parameter: (experimental) Reference to the AWS Systems Manager Parameter Store parameter that contains the data.
            :param encryption: (experimental) Optional encryption key that protects the secret.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__e4fe2891eb9e1869ca30826fbb44e85a4affa81f6af267d7d928f62e9045e0ed)
                check_type(argname="argument parameter", value=parameter, expected_type=type_hints["parameter"])
                check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "parameter": parameter,
            }
            if encryption is not None:
                self._values["encryption"] = encryption

        @builtins.property
        def parameter(self) -> _aws_cdk_aws_ssm_ceddda9d.IParameter:
            '''(experimental) Reference to the AWS Systems Manager Parameter Store parameter that contains the data.

            :stability: experimental
            '''
            result = self._values.get("parameter")
            assert result is not None, "Required property 'parameter' is missing"
            return typing.cast(_aws_cdk_aws_ssm_ceddda9d.IParameter, result)

        @builtins.property
        def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
            '''(experimental) Optional encryption key that protects the secret.

            :stability: experimental
            '''
            result = self._values.get("encryption")
            return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ParameterProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.IamServerCertificate.SecretProps",
        jsii_struct_bases=[],
        name_mapping={"secret": "secret", "encryption": "encryption"},
    )
    class SecretProps:
        def __init__(
            self,
            *,
            secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
            encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        ) -> None:
            '''(experimental) Properties for a server certificate element when it is stored in AWS Secrets Manager.

            :param secret: (experimental) Reference to the AWS Secrets Manager secret that contains the data.
            :param encryption: (experimental) Optional encryption key that protects the secret.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__8c490ec0a15ad8466c75d7ebfdb7c3aa3e9f15a2ea2e7c87dd90c47321f28233)
                check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
                check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "secret": secret,
            }
            if encryption is not None:
                self._values["encryption"] = encryption

        @builtins.property
        def secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
            '''(experimental) Reference to the AWS Secrets Manager secret that contains the data.

            :stability: experimental
            '''
            result = self._values.get("secret")
            assert result is not None, "Required property 'secret' is missing"
            return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

        @builtins.property
        def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
            '''(experimental) Optional encryption key that protects the secret.

            :stability: experimental
            '''
            result = self._values.get("encryption")
            return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SecretProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.IamServerCertificateProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "prefix": "prefix",
        "private_key": "privateKey",
        "encryption": "encryption",
        "lambda_configuration": "lambdaConfiguration",
    },
)
class IamServerCertificateProps:
    def __init__(
        self,
        *,
        certificate: typing.Union[typing.Union[IamServerCertificate.ParameterProps, typing.Dict[builtins.str, typing.Any]], typing.Union[IamServerCertificate.SecretProps, typing.Dict[builtins.str, typing.Any]]],
        prefix: builtins.str,
        private_key: typing.Union[typing.Union[IamServerCertificate.ParameterProps, typing.Dict[builtins.str, typing.Any]], typing.Union[IamServerCertificate.SecretProps, typing.Dict[builtins.str, typing.Any]]],
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the IamServerCertificate construct.

        :param certificate: (experimental) AWS Systems Manager parameter or AWS Secrets Manager secret which contains the public certificate.
        :param prefix: (experimental) Prefix to prepend to the AWS IAM Server Certificate name.
        :param private_key: (experimental) AWS Systems Manager parameter or AWS Secrets Manager secret which contains the private key.
        :param encryption: (experimental) Encryption key for protecting the framework resources.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aadb659070e20a08ee99b313037dd30162e04202beb26e1916ea22628c0b711)
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate": certificate,
            "prefix": prefix,
            "private_key": private_key,
        }
        if encryption is not None:
            self._values["encryption"] = encryption
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration

    @builtins.property
    def certificate(
        self,
    ) -> typing.Union[IamServerCertificate.ParameterProps, IamServerCertificate.SecretProps]:
        '''(experimental) AWS Systems Manager parameter or AWS Secrets Manager secret which contains the public certificate.

        :stability: experimental
        '''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(typing.Union[IamServerCertificate.ParameterProps, IamServerCertificate.SecretProps], result)

    @builtins.property
    def prefix(self) -> builtins.str:
        '''(experimental) Prefix to prepend to the AWS IAM Server Certificate name.

        :stability: experimental
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(
        self,
    ) -> typing.Union[IamServerCertificate.ParameterProps, IamServerCertificate.SecretProps]:
        '''(experimental) AWS Systems Manager parameter or AWS Secrets Manager secret which contains the private key.

        :stability: experimental
        '''
        result = self._values.get("private_key")
        assert result is not None, "Required property 'private_key' is missing"
        return typing.cast(typing.Union[IamServerCertificate.ParameterProps, IamServerCertificate.SecretProps], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Encryption key for protecting the framework resources.

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
        return "IamServerCertificateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkFirewall(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.NetworkFirewall",
):
    '''(experimental) Creates an AWS Network Firewall using a user-supplied Suricata rules file in a VPC.

    Follows guidelines that can be found at:

    :see: https://aws.github.io/aws-security-services-best-practices/guides/network-firewall/
    :stability: experimental

    Example::

        import { NetworkFirewall } from '@cdklabs/cdk-proserve-lib/constructs';
        
        new NetworkFirewall(this, 'Firewall', {
          vpc,
          firewallSubnets: vpc.selectSubnets({subnetGroupName: 'firewall'}).subnets,
          suricataRulesFilePath: './firewall-rules-suricata.txt',
          suricataRulesCapacity: 1000  // perform your own calculation based on the rules
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        firewall_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
        suricata_rules_capacity: jsii.Number,
        suricata_rules_file_path: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        configure_vpc_routes: typing.Optional[typing.Union["NetworkFirewall.NetworkFirewallVpcRouteProps", typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union["NetworkFirewall.LoggingConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Creates an AWS Network Firewall using a user-supplied Suricata rules file in a VPC.

        :param scope: - Parent construct scope.
        :param id: - Construct ID used to generate unique resource names.
        :param firewall_subnets: (experimental) List of subnets where the Network Firewall will be placed These should typically be dedicated firewall subnets.
        :param suricata_rules_capacity: (experimental) The capacity to set for the Suricata rule group. This cannot be modified after creation. You should set this to the upper bound of what you expect your firewall rule group to consume.
        :param suricata_rules_file_path: (experimental) Path to the Suricata rules file on the local file system.
        :param vpc: (experimental) VPC where the Network Firewall will be deployed.
        :param configure_vpc_routes: (experimental) Network Firewall routing configuration. By configuring these settings, the Construct will automatically setup basic routing statements for you for the provided subnets. This should be used with caution and you should double check the routing is correct prior to deployment.
        :param logging: (experimental) Optional logging configuration for the Network Firewall. If not provided, logs will not be written.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0efdf3491ffea7e177c5bed213822224ad81351ff2b50e17d90dafb117959206)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NetworkFirewallProps(
            firewall_subnets=firewall_subnets,
            suricata_rules_capacity=suricata_rules_capacity,
            suricata_rules_file_path=suricata_rules_file_path,
            vpc=vpc,
            configure_vpc_routes=configure_vpc_routes,
            logging=logging,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="firewall")
    def firewall(self) -> _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewall:
        '''(experimental) The underlying CloudFormation Network Firewall resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewall, jsii.get(self, "firewall"))

    @jsii.enum(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.NetworkFirewall.LogType"
    )
    class LogType(enum.Enum):
        '''
        :stability: experimental
        '''

        TLS = "TLS"
        '''(experimental) Logs for events that are related to TLS inspection.

        For more information, see Inspecting SSL/TLS traffic with TLS inspection configurations in the Network Firewall Developer Guide .

        :stability: experimental
        '''
        FLOW = "FLOW"
        '''(experimental) Standard network traffic flow logs.

        The stateful rules engine records flow logs for all network traffic that it receives. Each flow log record captures the network flow for a specific standard stateless rule group.

        :stability: experimental
        '''
        ALERT = "ALERT"
        '''(experimental) Logs for traffic that matches your stateful rules and that have an action that sends an alert.

        A stateful rule sends alerts for the rule actions DROP, ALERT, and REJECT. For more information, see the StatefulRule property.

        :stability: experimental
        '''

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.NetworkFirewall.LoggingConfiguration",
        jsii_struct_bases=[],
        name_mapping={
            "log_types": "logTypes",
            "encryption": "encryption",
            "log_group": "logGroup",
            "log_retention": "logRetention",
        },
    )
    class LoggingConfiguration:
        def __init__(
            self,
            *,
            log_types: typing.Sequence["NetworkFirewall.LogType"],
            encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
            log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
            log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        ) -> None:
            '''
            :param log_types: (experimental) The type of logs to write for the Network Firewall. This can be ``TLS``, ``FLOW``, or ``ALERT``.
            :param encryption: (experimental) Optional KMS key for encrypting Network Firewall logs.
            :param log_group: (experimental) Log group to use for Network Firewall Logging. If not specified, a log group is created for you. The encryption key provided will be used to encrypt it if one was provided to the construct.
            :param log_retention: (experimental) If you do not specify a log group, the amount of time to keep logs in the automatically created Log Group. Default: one week

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__63aa64adbf3b5d2c60e5d6c2881bd83d31fe62d8ff27bbf019cc9af5c73bc5bb)
                check_type(argname="argument log_types", value=log_types, expected_type=type_hints["log_types"])
                check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
                check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
                check_type(argname="argument log_retention", value=log_retention, expected_type=type_hints["log_retention"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "log_types": log_types,
            }
            if encryption is not None:
                self._values["encryption"] = encryption
            if log_group is not None:
                self._values["log_group"] = log_group
            if log_retention is not None:
                self._values["log_retention"] = log_retention

        @builtins.property
        def log_types(self) -> typing.List["NetworkFirewall.LogType"]:
            '''(experimental) The type of logs to write for the Network Firewall.

            This can be ``TLS``, ``FLOW``, or ``ALERT``.

            :stability: experimental
            '''
            result = self._values.get("log_types")
            assert result is not None, "Required property 'log_types' is missing"
            return typing.cast(typing.List["NetworkFirewall.LogType"], result)

        @builtins.property
        def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
            '''(experimental) Optional KMS key for encrypting Network Firewall logs.

            :stability: experimental
            '''
            result = self._values.get("encryption")
            return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

        @builtins.property
        def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
            '''(experimental) Log group to use for Network Firewall Logging.

            If not specified, a log group is created for you. The encryption key provided will be used to encrypt it if one was provided to the construct.

            :stability: experimental
            '''
            result = self._values.get("log_group")
            return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

        @builtins.property
        def log_retention(
            self,
        ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
            '''(experimental) If you do not specify a log group, the amount of time to keep logs in the automatically created Log Group.

            Default: one week

            :stability: experimental
            '''
            result = self._values.get("log_retention")
            return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LoggingConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.NetworkFirewall.NetworkFirewallVpcRouteProps",
        jsii_struct_bases=[],
        name_mapping={
            "protected_subnets": "protectedSubnets",
            "destination_cidr": "destinationCidr",
            "lambda_configuration": "lambdaConfiguration",
            "return_subnets": "returnSubnets",
        },
    )
    class NetworkFirewallVpcRouteProps:
        def __init__(
            self,
            *,
            protected_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
            destination_cidr: typing.Optional[builtins.str] = None,
            lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
            return_subnets: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet]] = None,
        ) -> None:
            '''
            :param protected_subnets: (experimental) Subnets that will sit behind the network firewall and should have routes to the Network Firewall. By supplying this parameter, routes will be created for these subnets to the Network Firewall. Specify the optional ``destinationCidr`` parameter if you want to restrict the routes to a specific CIDR block. By default, routes will be created for all outbound traffic (0.0.0.0/0) to the firewall.
            :param destination_cidr: (experimental) The destination CIDR block for the firewall (protectedSubnets) route. If not specified, defaults to '0.0.0.0/0' (all IPv4 traffic).
            :param lambda_configuration: (experimental) Configuration for the Lambda function that will be used to retrieve info about the AWS Network Firewall in order to setup the routing.
            :param return_subnets: (experimental) Subnets that should have routes back to the protected subnets. Since traffic is flowing through the firewall, routes should be put into the subnets where traffic is returning to. This is most likely your public subnets in the VPC. By supplying this parameter, routes will be created that send all traffic destined for the ``protectedSubnets`` back to the firewall for proper routing.

            :stability: experimental
            '''
            if isinstance(lambda_configuration, dict):
                lambda_configuration = _AwsCustomResourceLambdaConfiguration_be7862df(**lambda_configuration)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__6ace01da25292a8e889699aa698a73978bd428f1940d96890409aa76c9bbf80f)
                check_type(argname="argument protected_subnets", value=protected_subnets, expected_type=type_hints["protected_subnets"])
                check_type(argname="argument destination_cidr", value=destination_cidr, expected_type=type_hints["destination_cidr"])
                check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
                check_type(argname="argument return_subnets", value=return_subnets, expected_type=type_hints["return_subnets"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "protected_subnets": protected_subnets,
            }
            if destination_cidr is not None:
                self._values["destination_cidr"] = destination_cidr
            if lambda_configuration is not None:
                self._values["lambda_configuration"] = lambda_configuration
            if return_subnets is not None:
                self._values["return_subnets"] = return_subnets

        @builtins.property
        def protected_subnets(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
            '''(experimental) Subnets that will sit behind the network firewall and should have routes to the Network Firewall.

            By supplying this parameter, routes will
            be created for these subnets to the Network Firewall. Specify the
            optional ``destinationCidr`` parameter if you want to restrict the
            routes to a specific CIDR block. By default, routes will be created
            for all outbound traffic (0.0.0.0/0) to the firewall.

            :stability: experimental
            '''
            result = self._values.get("protected_subnets")
            assert result is not None, "Required property 'protected_subnets' is missing"
            return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet], result)

        @builtins.property
        def destination_cidr(self) -> typing.Optional[builtins.str]:
            '''(experimental) The destination CIDR block for the firewall (protectedSubnets) route.

            If not specified, defaults to '0.0.0.0/0' (all IPv4 traffic).

            :stability: experimental
            '''
            result = self._values.get("destination_cidr")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def lambda_configuration(
            self,
        ) -> typing.Optional[_AwsCustomResourceLambdaConfiguration_be7862df]:
            '''(experimental) Configuration for the Lambda function that will be used to retrieve info about the AWS Network Firewall in order to setup the routing.

            :stability: experimental
            '''
            result = self._values.get("lambda_configuration")
            return typing.cast(typing.Optional[_AwsCustomResourceLambdaConfiguration_be7862df], result)

        @builtins.property
        def return_subnets(
            self,
        ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]]:
            '''(experimental) Subnets that should have routes back to the protected subnets.

            Since
            traffic is flowing through the firewall, routes should be put into the
            subnets where traffic is returning to. This is most likely your public
            subnets in the VPC. By supplying this parameter, routes will be created
            that send all traffic destined for the ``protectedSubnets`` back to the
            firewall for proper routing.

            :stability: experimental
            '''
            result = self._values.get("return_subnets")
            return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "NetworkFirewallVpcRouteProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


class NetworkFirewallEndpoints(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.NetworkFirewallEndpoints",
):
    '''(experimental) Retrieves Network Firewall endpoints so that you can reference them in your other resources.

    Uses an AWS Custom Resource to fetch endpoint information from the Network
    Firewall service. This is useful so that you can both create a Network
    Firewall and reference the endpoints it creates, to do things like configure
    routing to the firewall.

    :stability: experimental

    Example::

        import { CfnOutput } from 'aws-cdk-lib';
        import { NetworkFirewallEndpoints } from '@cdklabs/cdk-proserve-lib/constructs';
        
        const endpoints = new NetworkFirewallEndpoints(this, 'Endpoints', {
          firewall: cfnFirewall,  // CfnFirewall resource to find endpoints for
        });
        const az1EndpointId = endpoints.getEndpointId('us-east-1a');
        const az2EndpointId = endpoints.getEndpointId('us-east-1b');
        new CfnOutput(this, 'Az1EndpointId', { value: az1Endpoint });
        new CfnOutput(this, 'Az2EndpointId', { value: az2Endpoint });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        firewall: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewall,
        lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Retrieves Network Firewall endpoints so that you can reference them in your other resources.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID.
        :param firewall: (experimental) The AWS Network Firewall to get the Endpoints for.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__814493a7a334a62a9dce7cd601a0b67fa4c645e77eceab9f1894bb4b630064af)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NetworkFirewallEndpointsProps(
            firewall=firewall, lambda_configuration=lambda_configuration
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getEndpointId")
    def get_endpoint_id(self, availability_zone: builtins.str) -> builtins.str:
        '''(experimental) Gets the endpoint ID for a specific availability zone.

        :param availability_zone: The availability zone to get the endpoint ID for.

        :return: The endpoint ID for the specified availability zone

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e9fd07c167ec8303ff19b47c28c2ae7a6b9056ffd494e1f325d9c91774f3775)
            check_type(argname="argument availability_zone", value=availability_zone, expected_type=type_hints["availability_zone"])
        return typing.cast(builtins.str, jsii.invoke(self, "getEndpointId", [availability_zone]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.NetworkFirewallEndpointsProps",
    jsii_struct_bases=[],
    name_mapping={
        "firewall": "firewall",
        "lambda_configuration": "lambdaConfiguration",
    },
)
class NetworkFirewallEndpointsProps:
    def __init__(
        self,
        *,
        firewall: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewall,
        lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the NetworkFirewallEndpoints construct.

        :param firewall: (experimental) The AWS Network Firewall to get the Endpoints for.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _AwsCustomResourceLambdaConfiguration_be7862df(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46421ac3a9e7f629694391452249c1e15f4a30971c4466574db708fb6b22fb69)
            check_type(argname="argument firewall", value=firewall, expected_type=type_hints["firewall"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "firewall": firewall,
        }
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration

    @builtins.property
    def firewall(self) -> _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewall:
        '''(experimental) The AWS Network Firewall to get the Endpoints for.

        :stability: experimental
        '''
        result = self._values.get("firewall")
        assert result is not None, "Required property 'firewall' is missing"
        return typing.cast(_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewall, result)

    @builtins.property
    def lambda_configuration(
        self,
    ) -> typing.Optional[_AwsCustomResourceLambdaConfiguration_be7862df]:
        '''(experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_AwsCustomResourceLambdaConfiguration_be7862df], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkFirewallEndpointsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.NetworkFirewallProps",
    jsii_struct_bases=[],
    name_mapping={
        "firewall_subnets": "firewallSubnets",
        "suricata_rules_capacity": "suricataRulesCapacity",
        "suricata_rules_file_path": "suricataRulesFilePath",
        "vpc": "vpc",
        "configure_vpc_routes": "configureVpcRoutes",
        "logging": "logging",
    },
)
class NetworkFirewallProps:
    def __init__(
        self,
        *,
        firewall_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
        suricata_rules_capacity: jsii.Number,
        suricata_rules_file_path: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        configure_vpc_routes: typing.Optional[typing.Union[NetworkFirewall.NetworkFirewallVpcRouteProps, typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union[NetworkFirewall.LoggingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for configuring a NetworkFirewall.

        :param firewall_subnets: (experimental) List of subnets where the Network Firewall will be placed These should typically be dedicated firewall subnets.
        :param suricata_rules_capacity: (experimental) The capacity to set for the Suricata rule group. This cannot be modified after creation. You should set this to the upper bound of what you expect your firewall rule group to consume.
        :param suricata_rules_file_path: (experimental) Path to the Suricata rules file on the local file system.
        :param vpc: (experimental) VPC where the Network Firewall will be deployed.
        :param configure_vpc_routes: (experimental) Network Firewall routing configuration. By configuring these settings, the Construct will automatically setup basic routing statements for you for the provided subnets. This should be used with caution and you should double check the routing is correct prior to deployment.
        :param logging: (experimental) Optional logging configuration for the Network Firewall. If not provided, logs will not be written.

        :stability: experimental
        '''
        if isinstance(configure_vpc_routes, dict):
            configure_vpc_routes = NetworkFirewall.NetworkFirewallVpcRouteProps(**configure_vpc_routes)
        if isinstance(logging, dict):
            logging = NetworkFirewall.LoggingConfiguration(**logging)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__944ba1d4d37915b6f2808152ac7939f147a45c5e12ea1623ea13954a65cf261e)
            check_type(argname="argument firewall_subnets", value=firewall_subnets, expected_type=type_hints["firewall_subnets"])
            check_type(argname="argument suricata_rules_capacity", value=suricata_rules_capacity, expected_type=type_hints["suricata_rules_capacity"])
            check_type(argname="argument suricata_rules_file_path", value=suricata_rules_file_path, expected_type=type_hints["suricata_rules_file_path"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument configure_vpc_routes", value=configure_vpc_routes, expected_type=type_hints["configure_vpc_routes"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "firewall_subnets": firewall_subnets,
            "suricata_rules_capacity": suricata_rules_capacity,
            "suricata_rules_file_path": suricata_rules_file_path,
            "vpc": vpc,
        }
        if configure_vpc_routes is not None:
            self._values["configure_vpc_routes"] = configure_vpc_routes
        if logging is not None:
            self._values["logging"] = logging

    @builtins.property
    def firewall_subnets(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
        '''(experimental) List of subnets where the Network Firewall will be placed These should typically be dedicated firewall subnets.

        :stability: experimental
        '''
        result = self._values.get("firewall_subnets")
        assert result is not None, "Required property 'firewall_subnets' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet], result)

    @builtins.property
    def suricata_rules_capacity(self) -> jsii.Number:
        '''(experimental) The capacity to set for the Suricata rule group.

        This cannot be modified
        after creation. You should set this to the upper bound of what you expect
        your firewall rule group to consume.

        :stability: experimental
        '''
        result = self._values.get("suricata_rules_capacity")
        assert result is not None, "Required property 'suricata_rules_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def suricata_rules_file_path(self) -> builtins.str:
        '''(experimental) Path to the Suricata rules file on the local file system.

        :stability: experimental
        '''
        result = self._values.get("suricata_rules_file_path")
        assert result is not None, "Required property 'suricata_rules_file_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) VPC where the Network Firewall will be deployed.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def configure_vpc_routes(
        self,
    ) -> typing.Optional[NetworkFirewall.NetworkFirewallVpcRouteProps]:
        '''(experimental) Network Firewall routing configuration.

        By configuring these settings,
        the Construct will automatically setup basic routing statements for you
        for the provided subnets. This should be used with caution and you should
        double check the routing is correct prior to deployment.

        :stability: experimental
        '''
        result = self._values.get("configure_vpc_routes")
        return typing.cast(typing.Optional[NetworkFirewall.NetworkFirewallVpcRouteProps], result)

    @builtins.property
    def logging(self) -> typing.Optional[NetworkFirewall.LoggingConfiguration]:
        '''(experimental) Optional logging configuration for the Network Firewall.

        If not provided,
        logs will not be written.

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[NetworkFirewall.LoggingConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkFirewallProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenSearchAdminUser(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.OpenSearchAdminUser",
):
    '''(experimental) Manages an admin user for an Amazon OpenSearch domain.

    This construct creates a Lambda-backed custom resource that adds an admin user to the specified OpenSearch domain.
    It uses the provided SSM parameter for the username, a provided SSM parameter or Secrets Manager secret for the
    password, and sets up the necessary IAM permissions for the Lambda function to interact with the OpenSearch domain
    and SSM parameter(s) and/or secret.

    The construct also handles encryption for the Lambda function's environment variables and dead letter queue,
    using either a provided KMS key or an AWS managed key.

    :stability: experimental

    Example::

        import { Key } from 'aws-cdk-lib/aws-kms';
        import { Domain } from 'aws-cdk-lib/aws-opensearchservice';
        import { Secret } from 'aws-cdk-lib/aws-secretsmanager';
        import { OpenSearchAdminUser } from '@cdklabs/cdk-proserve-lib/constructs';
        
        const keyArn = 'arn:aws:kms:us-east-1:111111111111:key/sample-key-id';
        const key = Key.fromKeyArn(this, 'Encryption', keyArn);
        
        const adminCredential = StringParameter.fromSecureStringParameterAttributes(this, 'AdminCredential', {
             parameterName: 'sample-parameter',
             encryptionKey: key
        });
        
        const domainKeyArn = 'arn:aws:kms:us-east-1:111111111111:key/sample-domain-key-id';
        const domainKey = Key.fromKeyArn(this, 'DomainEncryption', domainKeyArn);
        const domain = Domain.fromDomainEndpoint(this, 'Domain', 'vpc-testdomain.us-east-1.es.amazonaws.com');
        
        const adminUser = new OpenSearchAdminUser(this, 'AdminUser', {
             credential: {
                 secret: adminCredential,
                 encryption: key
             },
             domain: domain,
             domainKey: domainKey,
             username: 'admin'
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        credential: typing.Union[typing.Union["OpenSearchAdminUser.PasswordParameterProps", typing.Dict[builtins.str, typing.Any]], typing.Union["OpenSearchAdminUser.PasswordSecretProps", typing.Dict[builtins.str, typing.Any]]],
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
        username: _aws_cdk_aws_ssm_ceddda9d.IParameter,
        domain_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Constructor.

        :param scope: Parent to which the custom resource belongs.
        :param id: Unique identifier for this instance.
        :param credential: (experimental) The SSM parameter or Secret containing the password for the OpenSearch admin user.
        :param domain: (experimental) The OpenSearch domain to which the admin user will be added.
        :param username: (experimental) The SSM parameter containing the username for the OpenSearch admin user.
        :param domain_key: (experimental) Optional. The KMS key used to encrypt the OpenSearch domain. If provided, the construct will grant the necessary permissions to use this key.
        :param encryption: (experimental) Optional. The KMS key used to encrypt the worker resources (e.g., Lambda function environment variables). If provided, this key will be used for encryption; otherwise, an AWS managed key will be used.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f05c3bfeda6e475addd75dbb658119f41337a343f71dd7a3cb45945785a81fd9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenSearchAdminUserProps(
            credential=credential,
            domain=domain,
            username=username,
            domain_key=domain_key,
            encryption=encryption,
            lambda_configuration=lambda_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.OpenSearchAdminUser.PasswordParameterProps",
        jsii_struct_bases=[],
        name_mapping={"parameter": "parameter", "encryption": "encryption"},
    )
    class PasswordParameterProps:
        def __init__(
            self,
            *,
            parameter: _aws_cdk_aws_ssm_ceddda9d.IParameter,
            encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        ) -> None:
            '''(experimental) Properties for the admin user password specific to when the credential is stored in AWS Systems Manager Parameter Store.

            :param parameter: (experimental) Reference to the AWS Systems Manager Parameter Store parameter that contains the admin credential.
            :param encryption: (experimental) Optional encryption key that protects the secret.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__87e83aa659a038d1d6467b416d68f6f82588ff6c82d60e1b04a4cc02ae9820b1)
                check_type(argname="argument parameter", value=parameter, expected_type=type_hints["parameter"])
                check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "parameter": parameter,
            }
            if encryption is not None:
                self._values["encryption"] = encryption

        @builtins.property
        def parameter(self) -> _aws_cdk_aws_ssm_ceddda9d.IParameter:
            '''(experimental) Reference to the AWS Systems Manager Parameter Store parameter that contains the admin credential.

            :stability: experimental
            '''
            result = self._values.get("parameter")
            assert result is not None, "Required property 'parameter' is missing"
            return typing.cast(_aws_cdk_aws_ssm_ceddda9d.IParameter, result)

        @builtins.property
        def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
            '''(experimental) Optional encryption key that protects the secret.

            :stability: experimental
            '''
            result = self._values.get("encryption")
            return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PasswordParameterProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.OpenSearchAdminUser.PasswordSecretProps",
        jsii_struct_bases=[],
        name_mapping={"secret": "secret", "encryption": "encryption"},
    )
    class PasswordSecretProps:
        def __init__(
            self,
            *,
            secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
            encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        ) -> None:
            '''(experimental) Properties for the admin user password specific to when the credential is stored in AWS Secrets Manager.

            :param secret: (experimental) Reference to the AWS Secrets Manager secret that contains the admin credential.
            :param encryption: (experimental) Optional encryption key that protects the secret.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__d706a882ed5eb4a1c10b333c6f500d9fcfa8fd104530a097e0ecd94dee86a6e0)
                check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
                check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "secret": secret,
            }
            if encryption is not None:
                self._values["encryption"] = encryption

        @builtins.property
        def secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
            '''(experimental) Reference to the AWS Secrets Manager secret that contains the admin credential.

            :stability: experimental
            '''
            result = self._values.get("secret")
            assert result is not None, "Required property 'secret' is missing"
            return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

        @builtins.property
        def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
            '''(experimental) Optional encryption key that protects the secret.

            :stability: experimental
            '''
            result = self._values.get("encryption")
            return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PasswordSecretProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.OpenSearchAdminUserProps",
    jsii_struct_bases=[],
    name_mapping={
        "credential": "credential",
        "domain": "domain",
        "username": "username",
        "domain_key": "domainKey",
        "encryption": "encryption",
        "lambda_configuration": "lambdaConfiguration",
    },
)
class OpenSearchAdminUserProps:
    def __init__(
        self,
        *,
        credential: typing.Union[typing.Union[OpenSearchAdminUser.PasswordParameterProps, typing.Dict[builtins.str, typing.Any]], typing.Union[OpenSearchAdminUser.PasswordSecretProps, typing.Dict[builtins.str, typing.Any]]],
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
        username: _aws_cdk_aws_ssm_ceddda9d.IParameter,
        domain_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the OpenSearchAdminUser construct.

        :param credential: (experimental) The SSM parameter or Secret containing the password for the OpenSearch admin user.
        :param domain: (experimental) The OpenSearch domain to which the admin user will be added.
        :param username: (experimental) The SSM parameter containing the username for the OpenSearch admin user.
        :param domain_key: (experimental) Optional. The KMS key used to encrypt the OpenSearch domain. If provided, the construct will grant the necessary permissions to use this key.
        :param encryption: (experimental) Optional. The KMS key used to encrypt the worker resources (e.g., Lambda function environment variables). If provided, this key will be used for encryption; otherwise, an AWS managed key will be used.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e5d4a2781889ac772b1c0704e7cebf5e6ac1d19b2867f5bc9037a31e4154d80)
            check_type(argname="argument credential", value=credential, expected_type=type_hints["credential"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument domain_key", value=domain_key, expected_type=type_hints["domain_key"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "credential": credential,
            "domain": domain,
            "username": username,
        }
        if domain_key is not None:
            self._values["domain_key"] = domain_key
        if encryption is not None:
            self._values["encryption"] = encryption
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration

    @builtins.property
    def credential(
        self,
    ) -> typing.Union[OpenSearchAdminUser.PasswordParameterProps, OpenSearchAdminUser.PasswordSecretProps]:
        '''(experimental) The SSM parameter or Secret containing the password for the OpenSearch admin user.

        :stability: experimental
        '''
        result = self._values.get("credential")
        assert result is not None, "Required property 'credential' is missing"
        return typing.cast(typing.Union[OpenSearchAdminUser.PasswordParameterProps, OpenSearchAdminUser.PasswordSecretProps], result)

    @builtins.property
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.IDomain:
        '''(experimental) The OpenSearch domain to which the admin user will be added.

        :stability: experimental
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.IDomain, result)

    @builtins.property
    def username(self) -> _aws_cdk_aws_ssm_ceddda9d.IParameter:
        '''(experimental) The SSM parameter containing the username for the OpenSearch admin user.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(_aws_cdk_aws_ssm_ceddda9d.IParameter, result)

    @builtins.property
    def domain_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Optional.

        The KMS key used to encrypt the OpenSearch domain.
        If provided, the construct will grant the necessary permissions to use this key.

        :stability: experimental
        '''
        result = self._values.get("domain_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Optional.

        The KMS key used to encrypt the worker resources (e.g., Lambda function environment variables).
        If provided, this key will be used for encryption; otherwise, an AWS managed key will be used.

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
        return "OpenSearchAdminUserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenSearchProvisionDomain(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.OpenSearchProvisionDomain",
):
    '''(experimental) Controls the contents of an Amazon OpenSearch Service domain from Infrastructure as Code.

    This construct allows you to manage indices, component/index templates, cluster settings, Index State Management
    (ISM) policies, role / role mappings, and saved objects for a managed OpenSearch domain from CDK. Within your
    repository, you would create a directory containing the following sub-directories:

    - indices
    - ism-policies
    - role-mappings
    - roles
    - saved-objects
    - templates

      - component
      - index

    Within each subfolder, you can add JSON files to represent objects you want to be provisioned. The schema of the
    JSON file will be specific to the entity being provisioned and you can find more information withiin the OpenSearch
    documentation. The name of each file will be used as the name of the entity that is created within OpenSearch.

    The role-mappings entity is special and its structure is not found in the OpenSearch documentation. The name of the
    file should be the name of an internal OpenSearch role and will be used to send a PUT request to
    ``/_plugins/_security/api/rolesmapping/<name>``. The contents of the file should be backend role names to map to the
    internal OpenSearch role (where each backend role appears on a separate line). These backend roles can be LDAP
    Distinguished Names, AWS Identity and Access Management (IAM) Role ARNs, etc.

    The custom resource property 'dynamicRoleMappings' allows you to supplement role mappings at CDK deployment time.
    This is useful in situations where you are dynamically creating the backend role as part of IaC and its identifier
    will not be known ahead of time. For example, if you create an AWS IAM Role that will be mapped to an internal
    OpenSearch role like ``all_access`` via CDK, you can pass that Role ARN to the resource through ``dynamicRoleMappings``
    as such::

       dynamicRoleMappings: {
           all_access: [myRole.roleArn]
       }

    The property allows you to map multiple backend roles to a single internal OpenSearch role hence the value being a
    list of strings.

    The custom resource proeprty ``clusterSettings`` allows you to dynamicall configure cluster settings via IaC. Note
    that not all OpenSearch settings will be configurable in the managed Amazon OpenSearch Service and you receive an
    error when trying to do so. Additional details can be found
    `here <https://docs.opensearch.org/docs/latest/api-reference/cluster-api/cluster-settings/>`_

    By default, the custom resource will only modify the domain during AWS CloudFormation CREATE calls. This is to
    prevent potential data loss or issues as the domain will most likely drift from its initial provisioning
    configuration once established and used. If you would like to allow the custom resource to manage the domain
    provisioning during other CloudForamtion lifecycle events, you can do so by setting the ``allowDestructiveOperations``
    property on the custom resource.

    The construct also handles encryption for the framework resources using either a provided KMS key or an
    AWS managed key.

    The recommended pattern for provisioning a managed OpenSearch domain is to leverage this custom resource in a
    separate CDK stack from the one that deploys your domain. Typically OpenSearch domain deployments and teardowns
    take a significant amount of time and so you want to minimize errors in the stack that deploys your domain to
    prevent rollbacks and the need to redeploy. By separating your domain creation and provisioning, failures in
    provisioning will not cause the domain to be destroyed and will save a significant amount of development time.

    :stability: experimental

    Example::

        import { join } from 'node:path';
        import { OpenSearchProvisionDomain } from '@cdklabs/cdk-proserve-lib/constructs';
        import { DestructiveOperation } from '@cdklabs/cdk-proserve-lib/types';
        import { Role } from 'aws-cdk-lib/aws-iam';
        import { Domain } from 'aws-cdk-lib/aws-opensearchservice';
        
        const domain = Domain.fromDomainAttributes(this, 'Domain', {
            domainArn: 'XXXX',
            domainEndpoint: 'XXXX'
        });
        
        const admin = Role.fromRoleArn(this, 'DomainAdmin', 'XXXX');
        const user = Role.fromRoleArn(this, 'DomainUser', 'XXXX');
        
        new OpenSearchProvisionDomain(this, 'ProvisionDomain', {
            domain: domain,
            domainAdmin: admin,
            provisioningConfigurationPath: join(
                __dirname,
                '..',
                'dist',
                'cluster-configuration'
            ),
            allowDestructiveOperations: DestructiveOperation.UPDATE,
            clusterSettings: {
                persistent: {
                    'plugins.ml_commons.model_access_control_enabled': 'true'
                }
            },
            dynamicRoleMappings: {
                all_access: [user.roleArn]
            }
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
        domain_admin: _aws_cdk_aws_iam_ceddda9d.IRole,
        provisioning_configuration_path: builtins.str,
        allow_destructive_operations: typing.Optional[_DestructiveOperation_8d644d1e] = None,
        cluster_settings: typing.Optional[typing.Mapping[typing.Any, typing.Any]] = None,
        dynamic_role_mappings: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Provisions an existing Amazon OpenSearch Service domain with user-specified data.

        :param scope: Parent to which the Custom Resource belongs.
        :param id: Unique identifier for this instance.
        :param domain: (experimental) Amazon OpenSearch Service domain to provision.
        :param domain_admin: (experimental) AWS IAM Role that is configured as an administrative user of the Amazon OpenSearch Service domain.
        :param provisioning_configuration_path: (experimental) Path on the local disk to the files that will be used to provision the Amazon OpenSearch Service domain.
        :param allow_destructive_operations: (experimental) If specified, defines which destructive operations the Custom Resource will handle. If this is not specified, then the Custom Resource will only modify the domain on a CREATE call from AWS CloudFormation
        :param cluster_settings: (experimental) Additional settings to configure on the Amazon OpenSearch Service domain cluster itself. These settings will be sent as a JSON request to the /_cluster/settings API on OpenSearch. Additional details can be found `here <https://docs.opensearch.org/docs/latest/api-reference/cluster-api/cluster-settings/>`_
        :param dynamic_role_mappings: (experimental) Allows mapping of a role in an Amazon OpenSearch Service domain to multiple backend roles (like IAM Role ARNs, LDAP DNs, etc.). The key is the role name in OpenSearch and the value is a list of entities to map to that role (e.g. local database users or AWS IAM role ARNs)
        :param encryption: (experimental) Encryption key for protecting the framework resources.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72506fb1500f5c6ff037645c7a1d482804fef9969a9f476faa3007d5e6fa7bea)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenSearchProvisionDomainProps(
            domain=domain,
            domain_admin=domain_admin,
            provisioning_configuration_path=provisioning_configuration_path,
            allow_destructive_operations=allow_destructive_operations,
            cluster_settings=cluster_settings,
            dynamic_role_mappings=dynamic_role_mappings,
            encryption=encryption,
            lambda_configuration=lambda_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.OpenSearchProvisionDomainProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "domain_admin": "domainAdmin",
        "provisioning_configuration_path": "provisioningConfigurationPath",
        "allow_destructive_operations": "allowDestructiveOperations",
        "cluster_settings": "clusterSettings",
        "dynamic_role_mappings": "dynamicRoleMappings",
        "encryption": "encryption",
        "lambda_configuration": "lambdaConfiguration",
    },
)
class OpenSearchProvisionDomainProps:
    def __init__(
        self,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
        domain_admin: _aws_cdk_aws_iam_ceddda9d.IRole,
        provisioning_configuration_path: builtins.str,
        allow_destructive_operations: typing.Optional[_DestructiveOperation_8d644d1e] = None,
        cluster_settings: typing.Optional[typing.Mapping[typing.Any, typing.Any]] = None,
        dynamic_role_mappings: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the OpenSearchProvisionDomain construct.

        :param domain: (experimental) Amazon OpenSearch Service domain to provision.
        :param domain_admin: (experimental) AWS IAM Role that is configured as an administrative user of the Amazon OpenSearch Service domain.
        :param provisioning_configuration_path: (experimental) Path on the local disk to the files that will be used to provision the Amazon OpenSearch Service domain.
        :param allow_destructive_operations: (experimental) If specified, defines which destructive operations the Custom Resource will handle. If this is not specified, then the Custom Resource will only modify the domain on a CREATE call from AWS CloudFormation
        :param cluster_settings: (experimental) Additional settings to configure on the Amazon OpenSearch Service domain cluster itself. These settings will be sent as a JSON request to the /_cluster/settings API on OpenSearch. Additional details can be found `here <https://docs.opensearch.org/docs/latest/api-reference/cluster-api/cluster-settings/>`_
        :param dynamic_role_mappings: (experimental) Allows mapping of a role in an Amazon OpenSearch Service domain to multiple backend roles (like IAM Role ARNs, LDAP DNs, etc.). The key is the role name in OpenSearch and the value is a list of entities to map to that role (e.g. local database users or AWS IAM role ARNs)
        :param encryption: (experimental) Encryption key for protecting the framework resources.
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b50e5bc6a511d188b3051cff66623c572439b5a787e541535cb7aff488a3a4b)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument domain_admin", value=domain_admin, expected_type=type_hints["domain_admin"])
            check_type(argname="argument provisioning_configuration_path", value=provisioning_configuration_path, expected_type=type_hints["provisioning_configuration_path"])
            check_type(argname="argument allow_destructive_operations", value=allow_destructive_operations, expected_type=type_hints["allow_destructive_operations"])
            check_type(argname="argument cluster_settings", value=cluster_settings, expected_type=type_hints["cluster_settings"])
            check_type(argname="argument dynamic_role_mappings", value=dynamic_role_mappings, expected_type=type_hints["dynamic_role_mappings"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "domain_admin": domain_admin,
            "provisioning_configuration_path": provisioning_configuration_path,
        }
        if allow_destructive_operations is not None:
            self._values["allow_destructive_operations"] = allow_destructive_operations
        if cluster_settings is not None:
            self._values["cluster_settings"] = cluster_settings
        if dynamic_role_mappings is not None:
            self._values["dynamic_role_mappings"] = dynamic_role_mappings
        if encryption is not None:
            self._values["encryption"] = encryption
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration

    @builtins.property
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.IDomain:
        '''(experimental) Amazon OpenSearch Service domain to provision.

        :stability: experimental
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.IDomain, result)

    @builtins.property
    def domain_admin(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) AWS IAM Role that is configured as an administrative user of the Amazon OpenSearch Service domain.

        :stability: experimental
        '''
        result = self._values.get("domain_admin")
        assert result is not None, "Required property 'domain_admin' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def provisioning_configuration_path(self) -> builtins.str:
        '''(experimental) Path on the local disk to the files that will be used to provision the Amazon OpenSearch Service domain.

        :stability: experimental
        '''
        result = self._values.get("provisioning_configuration_path")
        assert result is not None, "Required property 'provisioning_configuration_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_destructive_operations(
        self,
    ) -> typing.Optional[_DestructiveOperation_8d644d1e]:
        '''(experimental) If specified, defines which destructive operations the Custom Resource will handle.

        If this is not specified, then the Custom Resource will only modify the domain on a CREATE call from AWS
        CloudFormation

        :stability: experimental
        '''
        result = self._values.get("allow_destructive_operations")
        return typing.cast(typing.Optional[_DestructiveOperation_8d644d1e], result)

    @builtins.property
    def cluster_settings(
        self,
    ) -> typing.Optional[typing.Mapping[typing.Any, typing.Any]]:
        '''(experimental) Additional settings to configure on the Amazon OpenSearch Service domain cluster itself.

        These settings will be sent as a JSON request to the /_cluster/settings API on OpenSearch.

        Additional details can be found
        `here <https://docs.opensearch.org/docs/latest/api-reference/cluster-api/cluster-settings/>`_

        :stability: experimental
        '''
        result = self._values.get("cluster_settings")
        return typing.cast(typing.Optional[typing.Mapping[typing.Any, typing.Any]], result)

    @builtins.property
    def dynamic_role_mappings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        '''(experimental) Allows mapping of a role in an Amazon OpenSearch Service domain to multiple backend roles (like IAM Role ARNs, LDAP DNs, etc.).

        The key is the role name in OpenSearch and the value is a list of entities to map to that role (e.g. local
        database users or AWS IAM role ARNs)

        :stability: experimental
        '''
        result = self._values.get("dynamic_role_mappings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Encryption key for protecting the framework resources.

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
        return "OpenSearchProvisionDomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenSearchWorkflow(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.OpenSearchWorkflow",
):
    '''(experimental) Create OpenSearch Workflows using the flow framework to automate the provisioning of complex tasks using JSON or YAML.

    This construct creates a custom resource that deploys a Flow Framework
    template to an OpenSearch domain. It handles the deployment and lifecycle
    management of the workflow through a Lambda-backed custom resources. You can
    read more about the flow framework on AWS at the reference link below.

    :stability: experimental
    :ref: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/ml-workflow-framework.html

    Example::

        import { OpenSearchWorkflow } from '@cdklabs/cdk-proserve-lib/constructs';
        import { Domain } from 'aws-cdk-lib/aws-opensearchservice';
        import { Role } from 'aws-cdk-lib/aws-iam';
        
        const aosDomain = Domain.fromDomainEndpoint(this, 'Domain', 'aos-endpoint');
        const aosRole = Role.fromRoleName(this, 'Role', 'AosRole');
        
        // Create OpenSearch Workflow using a YAML workflow template
        const nlpIngestPipeline = new OpenSearchWorkflow(
            this,
            'NlpIngestPipeline',
            {
                domain: aosDomain,
                domainAuthentication: aosRole,
                flowFrameworkTemplatePath: join(
                    __dirname,
                    'nlp-ingest-pipeline.yaml'
                )
            }
        );
        
        // Retrieve the deployed model from the OpenSearch Workflow
        this.embeddingModelId = nlpIngestPipeline.getResourceId(
            'deploy_sentence_model'
        );
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
        domain_authentication: _aws_cdk_aws_iam_ceddda9d.IRole,
        flow_framework_template_path: builtins.str,
        allow_destructive_operations: typing.Optional[_DestructiveOperation_8d644d1e] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        template_asset_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, _aws_cdk_aws_s3_assets_ceddda9d.Asset]]] = None,
        template_creation_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        template_provision_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Constructor.

        :param scope: Parent to which the custom resource belongs.
        :param id: Unique identifier for the custom resource.
        :param domain: (experimental) The OpenSearch domain to deploy the workflow to.
        :param domain_authentication: (experimental) IAM role used for domain authentication.
        :param flow_framework_template_path: (experimental) Path to the Flow Framework template file (YAML or JSON).
        :param allow_destructive_operations: (experimental) Whether to allow destructive operations like updating/deleting workflows.
        :param encryption: (experimental) Optional KMS key for encryption.
        :param lambda_configuration: (experimental) Optional lambda configuration settings for the custom resource provider.
        :param template_asset_variables: (experimental) Optional asset variables for the workflow. This can either be an AWS CDK S3 Asset object or a string that represents an S3 path (e.g. ``s3://my-bucket/my-key``). Your template must be configured to accept these variables using ``${{{ my_variable }}}`` syntax. For each one of these variables, an S3 pre-signed URL will be generated and substituted into your template right before workflow creation time. If you provide an S3 path, you must grant read permissions to the appropriate bucket in order for the custom resource to be able to generate a pre-signed url.
        :param template_creation_variables: (experimental) Optional creation variables for the workflow. Your template must be configured to accept these variables using ``${{{ my_variable }}}`` syntax. These variables will be substituted in prior to creation, so that will be available during creation time and provision time.
        :param template_provision_variables: (experimental) Optional provisioning variables for the workflow. Your template must be configured to accept these variables using ``${{ my_variable }}`` syntax. https://opensearch.org/docs/latest/automating-configurations/api/provision-workflow

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d69e7a0beffe2e3a42399915991e2a76276f793119ccb9d657b34d61446614a5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenSearchWorkflowProps(
            domain=domain,
            domain_authentication=domain_authentication,
            flow_framework_template_path=flow_framework_template_path,
            allow_destructive_operations=allow_destructive_operations,
            encryption=encryption,
            lambda_configuration=lambda_configuration,
            template_asset_variables=template_asset_variables,
            template_creation_variables=template_creation_variables,
            template_provision_variables=template_provision_variables,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getResourceId")
    def get_resource_id(self, workflow_step_id: builtins.str) -> builtins.str:
        '''(experimental) Retrieves a created Resource ID from the Workflow by the provided workflowStepId.

        The workflowStepId is the ``id`` value of the node in your
        list of workflow nodes from your workflow template

        :param workflow_step_id: the workflow step id from the workflow template.

        :return: string value of the resource id that was created

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15ed95aace02881b8569dbc646a97babb96362b68f80e2430bf5a39451100dcd)
            check_type(argname="argument workflow_step_id", value=workflow_step_id, expected_type=type_hints["workflow_step_id"])
        return typing.cast(builtins.str, jsii.invoke(self, "getResourceId", [workflow_step_id]))

    @builtins.property
    @jsii.member(jsii_name="isCompleteHandler")
    def is_complete_handler(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''(experimental) The Lambda function that will be called to determine if the execution is complete for the custom resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "isCompleteHandler"))

    @builtins.property
    @jsii.member(jsii_name="onEventHandler")
    def on_event_handler(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''(experimental) The Lambda function that will handle On Event requests for the custom resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "onEventHandler"))

    @builtins.property
    @jsii.member(jsii_name="workflowId")
    def workflow_id(self) -> builtins.str:
        '''(experimental) The unique identifier of the deployed OpenSearch workflow.

        This ID can be used to reference and manage the workflow after deployment.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "workflowId"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.OpenSearchWorkflowProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "domain_authentication": "domainAuthentication",
        "flow_framework_template_path": "flowFrameworkTemplatePath",
        "allow_destructive_operations": "allowDestructiveOperations",
        "encryption": "encryption",
        "lambda_configuration": "lambdaConfiguration",
        "template_asset_variables": "templateAssetVariables",
        "template_creation_variables": "templateCreationVariables",
        "template_provision_variables": "templateProvisionVariables",
    },
)
class OpenSearchWorkflowProps:
    def __init__(
        self,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
        domain_authentication: _aws_cdk_aws_iam_ceddda9d.IRole,
        flow_framework_template_path: builtins.str,
        allow_destructive_operations: typing.Optional[_DestructiveOperation_8d644d1e] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        template_asset_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, _aws_cdk_aws_s3_assets_ceddda9d.Asset]]] = None,
        template_creation_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        template_provision_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for configuring an OpenSearch workflow.

        :param domain: (experimental) The OpenSearch domain to deploy the workflow to.
        :param domain_authentication: (experimental) IAM role used for domain authentication.
        :param flow_framework_template_path: (experimental) Path to the Flow Framework template file (YAML or JSON).
        :param allow_destructive_operations: (experimental) Whether to allow destructive operations like updating/deleting workflows.
        :param encryption: (experimental) Optional KMS key for encryption.
        :param lambda_configuration: (experimental) Optional lambda configuration settings for the custom resource provider.
        :param template_asset_variables: (experimental) Optional asset variables for the workflow. This can either be an AWS CDK S3 Asset object or a string that represents an S3 path (e.g. ``s3://my-bucket/my-key``). Your template must be configured to accept these variables using ``${{{ my_variable }}}`` syntax. For each one of these variables, an S3 pre-signed URL will be generated and substituted into your template right before workflow creation time. If you provide an S3 path, you must grant read permissions to the appropriate bucket in order for the custom resource to be able to generate a pre-signed url.
        :param template_creation_variables: (experimental) Optional creation variables for the workflow. Your template must be configured to accept these variables using ``${{{ my_variable }}}`` syntax. These variables will be substituted in prior to creation, so that will be available during creation time and provision time.
        :param template_provision_variables: (experimental) Optional provisioning variables for the workflow. Your template must be configured to accept these variables using ``${{ my_variable }}`` syntax. https://opensearch.org/docs/latest/automating-configurations/api/provision-workflow

        :stability: experimental
        '''
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f58df00bbfc2d32adb19d8a2c49f777d13be48601c598cab05917867b09232cf)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument domain_authentication", value=domain_authentication, expected_type=type_hints["domain_authentication"])
            check_type(argname="argument flow_framework_template_path", value=flow_framework_template_path, expected_type=type_hints["flow_framework_template_path"])
            check_type(argname="argument allow_destructive_operations", value=allow_destructive_operations, expected_type=type_hints["allow_destructive_operations"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
            check_type(argname="argument template_asset_variables", value=template_asset_variables, expected_type=type_hints["template_asset_variables"])
            check_type(argname="argument template_creation_variables", value=template_creation_variables, expected_type=type_hints["template_creation_variables"])
            check_type(argname="argument template_provision_variables", value=template_provision_variables, expected_type=type_hints["template_provision_variables"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "domain_authentication": domain_authentication,
            "flow_framework_template_path": flow_framework_template_path,
        }
        if allow_destructive_operations is not None:
            self._values["allow_destructive_operations"] = allow_destructive_operations
        if encryption is not None:
            self._values["encryption"] = encryption
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration
        if template_asset_variables is not None:
            self._values["template_asset_variables"] = template_asset_variables
        if template_creation_variables is not None:
            self._values["template_creation_variables"] = template_creation_variables
        if template_provision_variables is not None:
            self._values["template_provision_variables"] = template_provision_variables

    @builtins.property
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.IDomain:
        '''(experimental) The OpenSearch domain to deploy the workflow to.

        :stability: experimental
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.IDomain, result)

    @builtins.property
    def domain_authentication(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) IAM role used for domain authentication.

        :stability: experimental
        '''
        result = self._values.get("domain_authentication")
        assert result is not None, "Required property 'domain_authentication' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def flow_framework_template_path(self) -> builtins.str:
        '''(experimental) Path to the Flow Framework template file (YAML or JSON).

        :stability: experimental
        '''
        result = self._values.get("flow_framework_template_path")
        assert result is not None, "Required property 'flow_framework_template_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_destructive_operations(
        self,
    ) -> typing.Optional[_DestructiveOperation_8d644d1e]:
        '''(experimental) Whether to allow destructive operations like updating/deleting workflows.

        :stability: experimental
        '''
        result = self._values.get("allow_destructive_operations")
        return typing.cast(typing.Optional[_DestructiveOperation_8d644d1e], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Optional KMS key for encryption.

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def lambda_configuration(self) -> typing.Optional[_LambdaConfiguration_9f8afc24]:
        '''(experimental) Optional lambda configuration settings for the custom resource provider.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_LambdaConfiguration_9f8afc24], result)

    @builtins.property
    def template_asset_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, _aws_cdk_aws_s3_assets_ceddda9d.Asset]]]:
        '''(experimental) Optional asset variables for the workflow.

        This can either be an AWS CDK
        S3 Asset object or a string that represents an S3 path (e.g. ``s3://my-bucket/my-key``).
        Your template must be configured to accept these variables using
        ``${{{ my_variable }}}`` syntax. For each one of these variables, an S3
        pre-signed URL will be generated and substituted into your template right
        before workflow creation time. If you provide an S3 path, you must grant
        read permissions to the appropriate bucket in order for the custom
        resource to be able to generate a pre-signed url.

        :stability: experimental
        '''
        result = self._values.get("template_asset_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, _aws_cdk_aws_s3_assets_ceddda9d.Asset]]], result)

    @builtins.property
    def template_creation_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Optional creation variables for the workflow. Your template must be configured to accept these variables using ``${{{ my_variable }}}`` syntax.

        These variables will be substituted in prior to creation, so that will
        be available during creation time and provision time.

        :stability: experimental
        '''
        result = self._values.get("template_creation_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def template_provision_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Optional provisioning variables for the workflow. Your template must be configured to accept these variables using ``${{ my_variable }}`` syntax.

        https://opensearch.org/docs/latest/automating-configurations/api/provision-workflow

        :stability: experimental
        '''
        result = self._values.get("template_provision_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchWorkflowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebApplicationFirewall(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.WebApplicationFirewall",
):
    '''(experimental) Creates an AWS Web Application Firewall (WAF) that can be associated with resources such as an Application Load Balancer.

    It allows configuring AWS managed rule groups, logging, and visibility
    settings. The construct simplifies the creation of a WAF by providing
    available AWS managed rule groups that can be utilized.

    Currently, the only resource that is supported to associate the WAF with is
    an ALB.

    :stability: experimental

    Example::

        import { ApplicationLoadBalancer } from 'aws-cdk-lib/aws-elasticloadbalancingv2';
        import { WebApplicationFirewall } from '@cdklabs/cdk-proserve-lib/constructs';
        
        const alb = new ApplicationLoadBalancer(this, 'Alb', { vpc });
        const waf = new WebApplicationFirewall(this, 'WAF', {
          awsManagedRuleGroups: [
            WebApplicationFirewall.AwsManagedRuleGroup.COMMON_RULE_SET,
            WebApplicationFirewall.AwsManagedRuleGroup.LINUX_RULE_SET
          ]
        });
        waf.associate(alb);  // Associate the WAF with the ALB
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        aws_managed_rule_groups: typing.Optional[typing.Sequence[typing.Union[typing.Union["WebApplicationFirewall.AwsManagedRuleGroupConfig", typing.Dict[builtins.str, typing.Any]], "WebApplicationFirewall.AwsManagedRuleGroup"]]] = None,
        cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union["WebApplicationFirewall.WebApplicationFirewallLoggingConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        sampled_requests_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Creates an AWS Web Application Firewall (WAF) that can be associated with resources such as an Application Load Balancer.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID.
        :param aws_managed_rule_groups: (experimental) List of AWS Managed Rule Groups to use for the firewall. Default: []
        :param cloud_watch_metrics_enabled: (experimental) Whether to enable CloudWatch metrics. Default: false
        :param logging: (experimental) Logging configuration for the firewall.
        :param sampled_requests_enabled: (experimental) Whether to enable sampled requests. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e73123a147ab61f7f5e1b4dd63bd49a5f6fb5beb4d9c15b2e42a424fefc81885)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebApplicationFirewallProps(
            aws_managed_rule_groups=aws_managed_rule_groups,
            cloud_watch_metrics_enabled=cloud_watch_metrics_enabled,
            logging=logging,
            sampled_requests_enabled=sampled_requests_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="associate")
    def associate(
        self,
        resource: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
    ) -> None:
        '''(experimental) Associates the Web Application Firewall to an applicable resource.

        :param resource: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb17097905b85e77dd68963514cb93012718b2a0e88a07310d41bfbdfd329ddd)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        return typing.cast(None, jsii.invoke(self, "associate", [resource]))

    @builtins.property
    @jsii.member(jsii_name="webAcl")
    def web_acl(self) -> _aws_cdk_aws_wafv2_ceddda9d.CfnWebACL:
        '''(experimental) The WAF Web ACL (Access Control List) resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL, jsii.get(self, "webAcl"))

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroup]:
        '''(experimental) Optional CloudWatch log group for WAF logging.

        This is available if you
        have configured ``logging`` on the construct.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroup], jsii.get(self, "logGroup"))

    @jsii.enum(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.WebApplicationFirewall.AwsManagedRuleGroup"
    )
    class AwsManagedRuleGroup(enum.Enum):
        '''(experimental) WAF Managed Rule Groups.

        :stability: experimental
        '''

        COMMON_RULE_SET = "COMMON_RULE_SET"
        '''(experimental) Contains rules that are generally applicable to web applications.

        This provides protection against exploitation of a wide range of vulnerabilities, including those described in OWASP publications.

        :stability: experimental
        '''
        ADMIN_PROTECTION_RULE_SET = "ADMIN_PROTECTION_RULE_SET"
        '''(experimental) Contains rules that allow you to block external access to exposed admin pages.

        This may be useful if you are running third-party software or would like to reduce the risk of a malicious actor gaining administrative access to your application.

        :stability: experimental
        '''
        KNOWN_BAD_INPUTS_RULE_SET = "KNOWN_BAD_INPUTS_RULE_SET"
        '''(experimental) Contains rules that allow you to block request patterns that are known to be invalid and are associated with exploitation or discovery of vulnerabilities.

        This can help reduce the risk of a malicious actor discovering a vulnerable application.

        :stability: experimental
        '''
        SQL_DATABASE_RULE_SET = "SQL_DATABASE_RULE_SET"
        '''(experimental) Contains rules that allow you to block request patterns associated with exploitation of SQL databases, like SQL injection attacks.

        This can help prevent remote injection of unauthorized queries.

        :stability: experimental
        '''
        LINUX_RULE_SET = "LINUX_RULE_SET"
        '''(experimental) Contains rules that block request patterns associated with exploitation of vulnerabilities specific to Linux, including LFI attacks.

        This can help prevent attacks that expose file contents or execute code for which the attacker should not have had access.

        :stability: experimental
        '''
        UNIX_RULE_SET = "UNIX_RULE_SET"
        '''(experimental) Contains rules that block request patterns associated with exploiting vulnerabilities specific to POSIX/POSIX-like OS, including LFI attacks.

        This can help prevent attacks that expose file contents or execute code for which access should not been allowed.

        :stability: experimental
        '''
        WINDOWS_RULE_SET = "WINDOWS_RULE_SET"
        '''(experimental) Contains rules that block request patterns associated with exploiting vulnerabilities specific to Windows, (e.g., PowerShell commands). This can help prevent exploits that allow attacker to run unauthorized commands or execute malicious code.

        :stability: experimental
        '''
        PHP_RULE_SET = "PHP_RULE_SET"
        '''(experimental) Contains rules that block request patterns associated with exploiting vulnerabilities specific to the use of the PHP, including injection of unsafe PHP functions.

        This can help prevent exploits that allow an attacker to remotely execute code or commands.

        :stability: experimental
        '''
        WORD_PRESS_RULE_SET = "WORD_PRESS_RULE_SET"
        '''(experimental) The WordPress Applications group contains rules that block request patterns associated with the exploitation of vulnerabilities specific to WordPress sites.

        :stability: experimental
        '''
        AMAZON_IP_REPUTATION_LIST = "AMAZON_IP_REPUTATION_LIST"
        '''(experimental) This group contains rules that are based on Amazon threat intelligence.

        This is useful if you would like to block sources associated with bots or other threats.

        :stability: experimental
        '''
        ANONYMOUS_IP_LIST = "ANONYMOUS_IP_LIST"
        '''(experimental) This group contains rules that allow you to block requests from services that allow obfuscation of viewer identity.

        This can include request originating from VPN, proxies, Tor nodes, and hosting providers. This is useful if you want to filter out viewers that may be trying to hide their identity from your application.

        :stability: experimental
        '''
        BOT_CONTROL_RULE_SET = "BOT_CONTROL_RULE_SET"
        '''(experimental) Provides protection against automated bots that can consume excess resources, skew business metrics, cause downtime, or perform malicious activities.

        Bot Control provides additional visibility through Amazon CloudWatch and generates labels that you can use to control bot traffic to your applications.

        :stability: experimental
        '''
        ATP_RULE_SET = "ATP_RULE_SET"
        '''(experimental) Provides protection for your login page against stolen credentials, credential stuffing attacks, brute force login attempts, and other anomalous login activities.

        With account takeover prevention, you can prevent unauthorized access that may lead to fraudulent activities, or inform legitimate users to take a preventive action.

        :stability: experimental
        '''
        ACFP_RULE_SET = "ACFP_RULE_SET"
        '''(experimental) Provides protection against the creation of fraudulent accounts on your site.

        Fraudulent accounts can be used for activities such as obtaining sign-up bonuses and impersonating legitimate users.

        :stability: experimental
        '''

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.WebApplicationFirewall.AwsManagedRuleGroupConfig",
        jsii_struct_bases=[],
        name_mapping={
            "rule_group": "ruleGroup",
            "rule_group_action_overrides": "ruleGroupActionOverrides",
        },
    )
    class AwsManagedRuleGroupConfig:
        def __init__(
            self,
            *,
            rule_group: "WebApplicationFirewall.AwsManagedRuleGroup",
            rule_group_action_overrides: typing.Optional[typing.Sequence[typing.Union["WebApplicationFirewall.OverrideConfig", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''(experimental) Configuration interface for AWS Managed Rule Groups.

            This interface allows you to specify a managed rule group and optionally
            override the default actions for specific rules within that group.

            :param rule_group: (experimental) The AWS Managed Rule Group to apply.
            :param rule_group_action_overrides: (experimental) Optional list of rule action overrides.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__366b30b777356565a2d25147dde650448b63ce88d57853714610c9c96d12842d)
                check_type(argname="argument rule_group", value=rule_group, expected_type=type_hints["rule_group"])
                check_type(argname="argument rule_group_action_overrides", value=rule_group_action_overrides, expected_type=type_hints["rule_group_action_overrides"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "rule_group": rule_group,
            }
            if rule_group_action_overrides is not None:
                self._values["rule_group_action_overrides"] = rule_group_action_overrides

        @builtins.property
        def rule_group(self) -> "WebApplicationFirewall.AwsManagedRuleGroup":
            '''(experimental) The AWS Managed Rule Group to apply.

            :stability: experimental
            '''
            result = self._values.get("rule_group")
            assert result is not None, "Required property 'rule_group' is missing"
            return typing.cast("WebApplicationFirewall.AwsManagedRuleGroup", result)

        @builtins.property
        def rule_group_action_overrides(
            self,
        ) -> typing.Optional[typing.List["WebApplicationFirewall.OverrideConfig"]]:
            '''(experimental) Optional list of rule action overrides.

            :stability: experimental
            '''
            result = self._values.get("rule_group_action_overrides")
            return typing.cast(typing.Optional[typing.List["WebApplicationFirewall.OverrideConfig"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AwsManagedRuleGroupConfig(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.enum(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.WebApplicationFirewall.OverrideAction"
    )
    class OverrideAction(enum.Enum):
        '''(experimental) Enum representing possible override actions for WAF rules.

        :stability: experimental
        '''

        ALLOW = "ALLOW"
        '''
        :stability: experimental
        '''
        BLOCK = "BLOCK"
        '''
        :stability: experimental
        '''
        COUNT = "COUNT"
        '''
        :stability: experimental
        '''

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.WebApplicationFirewall.OverrideConfig",
        jsii_struct_bases=[],
        name_mapping={"action": "action", "name": "name"},
    )
    class OverrideConfig:
        def __init__(
            self,
            *,
            action: "WebApplicationFirewall.OverrideAction",
            name: builtins.str,
        ) -> None:
            '''(experimental) Configuration for rule overrides.

            :param action: (experimental) The action to take for the specific rule.
            :param name: (experimental) The name of the specific rule to override.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b2807f89045ac6870539a2474ad79baf282359ba013194ddd634bfa7af26097e)
                check_type(argname="argument action", value=action, expected_type=type_hints["action"])
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "action": action,
                "name": name,
            }

        @builtins.property
        def action(self) -> "WebApplicationFirewall.OverrideAction":
            '''(experimental) The action to take for the specific rule.

            :stability: experimental
            '''
            result = self._values.get("action")
            assert result is not None, "Required property 'action' is missing"
            return typing.cast("WebApplicationFirewall.OverrideAction", result)

        @builtins.property
        def name(self) -> builtins.str:
            '''(experimental) The name of the specific rule to override.

            :stability: experimental
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OverrideConfig(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.constructs.WebApplicationFirewall.WebApplicationFirewallLoggingConfig",
        jsii_struct_bases=[],
        name_mapping={
            "log_group_name_affix": "logGroupNameAffix",
            "encryption_key": "encryptionKey",
            "removal_policy": "removalPolicy",
            "retention": "retention",
        },
    )
    class WebApplicationFirewallLoggingConfig:
        def __init__(
            self,
            *,
            log_group_name_affix: builtins.str,
            encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
            removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
            retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        ) -> None:
            '''
            :param log_group_name_affix: (experimental) Log Group name affix to be appended to aws-waf-logs-.
            :param encryption_key: (experimental) KMS key to use for encryption of the log group.
            :param removal_policy: (experimental) Removal policy for the log group. Default: DESTROY
            :param retention: (experimental) Retention period for the log group. Default: ONE_MONTH

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__348a0b36a02918bbbf326c8a9c00bbbc2223fe506081f7f3740db4cb18af2a91)
                check_type(argname="argument log_group_name_affix", value=log_group_name_affix, expected_type=type_hints["log_group_name_affix"])
                check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
                check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
                check_type(argname="argument retention", value=retention, expected_type=type_hints["retention"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "log_group_name_affix": log_group_name_affix,
            }
            if encryption_key is not None:
                self._values["encryption_key"] = encryption_key
            if removal_policy is not None:
                self._values["removal_policy"] = removal_policy
            if retention is not None:
                self._values["retention"] = retention

        @builtins.property
        def log_group_name_affix(self) -> builtins.str:
            '''(experimental) Log Group name affix to be appended to aws-waf-logs-.

            :stability: experimental
            '''
            result = self._values.get("log_group_name_affix")
            assert result is not None, "Required property 'log_group_name_affix' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
            '''(experimental) KMS key to use for encryption of the log group.

            :stability: experimental
            '''
            result = self._values.get("encryption_key")
            return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

        @builtins.property
        def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
            '''(experimental) Removal policy for the log group.

            :default: DESTROY

            :stability: experimental
            '''
            result = self._values.get("removal_policy")
            return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

        @builtins.property
        def retention(
            self,
        ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
            '''(experimental) Retention period for the log group.

            :default: ONE_MONTH

            :stability: experimental
            '''
            result = self._values.get("retention")
            return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "WebApplicationFirewallLoggingConfig(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.constructs.WebApplicationFirewallProps",
    jsii_struct_bases=[],
    name_mapping={
        "aws_managed_rule_groups": "awsManagedRuleGroups",
        "cloud_watch_metrics_enabled": "cloudWatchMetricsEnabled",
        "logging": "logging",
        "sampled_requests_enabled": "sampledRequestsEnabled",
    },
)
class WebApplicationFirewallProps:
    def __init__(
        self,
        *,
        aws_managed_rule_groups: typing.Optional[typing.Sequence[typing.Union[typing.Union[WebApplicationFirewall.AwsManagedRuleGroupConfig, typing.Dict[builtins.str, typing.Any]], WebApplicationFirewall.AwsManagedRuleGroup]]] = None,
        cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[WebApplicationFirewall.WebApplicationFirewallLoggingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        sampled_requests_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param aws_managed_rule_groups: (experimental) List of AWS Managed Rule Groups to use for the firewall. Default: []
        :param cloud_watch_metrics_enabled: (experimental) Whether to enable CloudWatch metrics. Default: false
        :param logging: (experimental) Logging configuration for the firewall.
        :param sampled_requests_enabled: (experimental) Whether to enable sampled requests. Default: false

        :stability: experimental
        '''
        if isinstance(logging, dict):
            logging = WebApplicationFirewall.WebApplicationFirewallLoggingConfig(**logging)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc0222cf648cd9f034f008b4afecb517b89d7528ca30105206f9add718afdb21)
            check_type(argname="argument aws_managed_rule_groups", value=aws_managed_rule_groups, expected_type=type_hints["aws_managed_rule_groups"])
            check_type(argname="argument cloud_watch_metrics_enabled", value=cloud_watch_metrics_enabled, expected_type=type_hints["cloud_watch_metrics_enabled"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument sampled_requests_enabled", value=sampled_requests_enabled, expected_type=type_hints["sampled_requests_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if aws_managed_rule_groups is not None:
            self._values["aws_managed_rule_groups"] = aws_managed_rule_groups
        if cloud_watch_metrics_enabled is not None:
            self._values["cloud_watch_metrics_enabled"] = cloud_watch_metrics_enabled
        if logging is not None:
            self._values["logging"] = logging
        if sampled_requests_enabled is not None:
            self._values["sampled_requests_enabled"] = sampled_requests_enabled

    @builtins.property
    def aws_managed_rule_groups(
        self,
    ) -> typing.Optional[typing.List[typing.Union[WebApplicationFirewall.AwsManagedRuleGroupConfig, WebApplicationFirewall.AwsManagedRuleGroup]]]:
        '''(experimental) List of AWS Managed Rule Groups to use for the firewall.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("aws_managed_rule_groups")
        return typing.cast(typing.Optional[typing.List[typing.Union[WebApplicationFirewall.AwsManagedRuleGroupConfig, WebApplicationFirewall.AwsManagedRuleGroup]]], result)

    @builtins.property
    def cloud_watch_metrics_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable CloudWatch metrics.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("cloud_watch_metrics_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logging(
        self,
    ) -> typing.Optional[WebApplicationFirewall.WebApplicationFirewallLoggingConfig]:
        '''(experimental) Logging configuration for the firewall.

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[WebApplicationFirewall.WebApplicationFirewallLoggingConfig], result)

    @builtins.property
    def sampled_requests_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable sampled requests.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("sampled_requests_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebApplicationFirewallProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamoDbProvisionTable",
    "DynamoDbProvisionTableProps",
    "Ec2ImageBuilderGetImage",
    "Ec2ImageBuilderGetImageProps",
    "Ec2ImageBuilderStart",
    "Ec2ImageBuilderStartProps",
    "Ec2ImagePipeline",
    "Ec2ImagePipelineBaseProps",
    "Ec2ImagePipelineProps",
    "FriendlyEmbrace",
    "FriendlyEmbraceProps",
    "IamServerCertificate",
    "IamServerCertificateProps",
    "NetworkFirewall",
    "NetworkFirewallEndpoints",
    "NetworkFirewallEndpointsProps",
    "NetworkFirewallProps",
    "OpenSearchAdminUser",
    "OpenSearchAdminUserProps",
    "OpenSearchProvisionDomain",
    "OpenSearchProvisionDomainProps",
    "OpenSearchWorkflow",
    "OpenSearchWorkflowProps",
    "WebApplicationFirewall",
    "WebApplicationFirewallProps",
]

publication.publish()

def _typecheckingstub__75e675d5b6c5efc4f3d517f4b5cb2c050c01589db5dae3ccedefd4b2ace24b6d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    items: typing.Sequence[typing.Mapping[builtins.str, typing.Any]],
    table: typing.Union[DynamoDbProvisionTable.TableProps, typing.Dict[builtins.str, typing.Any]],
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f2f053da9013efed93700973fc9b6d139fabc44431d7adcc0531222ae5fc066(
    *,
    partition_key_name: builtins.str,
    resource: _aws_cdk_aws_dynamodb_ceddda9d.ITable,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    sort_key_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__057380ca290e7837e75b9bfeb840e320aa76aea52a09b6ee95b22f8e83ee518a(
    *,
    items: typing.Sequence[typing.Mapping[builtins.str, typing.Any]],
    table: typing.Union[DynamoDbProvisionTable.TableProps, typing.Dict[builtins.str, typing.Any]],
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77b3847ea7ab39647e63e524b2fd35fa06cad82a271bbc9187a0da10595cdbc2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    image_build_version_arn: builtins.str,
    lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__184e94d1d9278acaeb42b57dfec53575c7a9faed100c01fb9af15258d9421ef1(
    *,
    image_build_version_arn: builtins.str,
    lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c6b272e0e32c91e9ca6567ad3a5863fbf8d47e124cfe4db893341e0671f95ac(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    pipeline_arn: builtins.str,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    hash: typing.Optional[builtins.str] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    wait_for_completion: typing.Optional[typing.Union[Ec2ImageBuilderStart.WaitForCompletionProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a6651df0fe081b0ec228004b64fd177cf62b1f8699519c900e5306fc9889989(
    *,
    topic: _aws_cdk_aws_sns_ceddda9d.ITopic,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9660c3b729015c46b21753c84ffe9a1cbff9a627eda095023fcbd14bcac7e52c(
    *,
    pipeline_arn: builtins.str,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    hash: typing.Optional[builtins.str] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    wait_for_completion: typing.Optional[typing.Union[Ec2ImageBuilderStart.WaitForCompletionProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__737be13ffae0c45b3bddb7f3aafa412e381609e089f3c4cfe2bc669b2916689e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    block_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    components: typing.Optional[typing.Sequence[typing.Union[Ec2ImagePipeline.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
    machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    version: builtins.str,
    build_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27c54dc47bf0adadbe7c82a863cfc7874cd749dd459f64d5b19ac8e01b6d7bc1(
    *,
    start: builtins.bool,
    hash: typing.Optional[builtins.str] = None,
    wait_for_completion: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcde20831541d1ff69c140ecf8eb01c2fa26796a4dbab5ece7343e4d177ec4c3(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    subnet: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__802e96348c8a99aa2d3111175157a3a3a4b1b7f66997ab3055d8dd76318b4809(
    *,
    version: builtins.str,
    build_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a39e35bb21d08f951c8d42be5f389f8950b3c94272d8b6641ca758840295ee47(
    *,
    version: builtins.str,
    build_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_configuration: typing.Optional[typing.Union[Ec2ImagePipeline.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    block_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    components: typing.Optional[typing.Sequence[typing.Union[Ec2ImagePipeline.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
    machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a08886230823f61b9ec19693d376c572b9161a1cb35e9536e22c6608d6f9af65(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket_configuration: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ignore_invalid_states: typing.Optional[builtins.bool] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    manual_read_permissions: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a24b8202515587c00146de8fecdb544e867498ebe708c1272c2072200a7b12f(
    *,
    bucket_configuration: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ignore_invalid_states: typing.Optional[builtins.bool] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    manual_read_permissions: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b83600751ad5ce20528131f4fb433a007a960e427a87ae702a9539150d2cc3dd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    certificate: typing.Union[typing.Union[IamServerCertificate.ParameterProps, typing.Dict[builtins.str, typing.Any]], typing.Union[IamServerCertificate.SecretProps, typing.Dict[builtins.str, typing.Any]]],
    prefix: builtins.str,
    private_key: typing.Union[typing.Union[IamServerCertificate.ParameterProps, typing.Dict[builtins.str, typing.Any]], typing.Union[IamServerCertificate.SecretProps, typing.Dict[builtins.str, typing.Any]]],
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4fe2891eb9e1869ca30826fbb44e85a4affa81f6af267d7d928f62e9045e0ed(
    *,
    parameter: _aws_cdk_aws_ssm_ceddda9d.IParameter,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c490ec0a15ad8466c75d7ebfdb7c3aa3e9f15a2ea2e7c87dd90c47321f28233(
    *,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aadb659070e20a08ee99b313037dd30162e04202beb26e1916ea22628c0b711(
    *,
    certificate: typing.Union[typing.Union[IamServerCertificate.ParameterProps, typing.Dict[builtins.str, typing.Any]], typing.Union[IamServerCertificate.SecretProps, typing.Dict[builtins.str, typing.Any]]],
    prefix: builtins.str,
    private_key: typing.Union[typing.Union[IamServerCertificate.ParameterProps, typing.Dict[builtins.str, typing.Any]], typing.Union[IamServerCertificate.SecretProps, typing.Dict[builtins.str, typing.Any]]],
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0efdf3491ffea7e177c5bed213822224ad81351ff2b50e17d90dafb117959206(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    firewall_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
    suricata_rules_capacity: jsii.Number,
    suricata_rules_file_path: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    configure_vpc_routes: typing.Optional[typing.Union[NetworkFirewall.NetworkFirewallVpcRouteProps, typing.Dict[builtins.str, typing.Any]]] = None,
    logging: typing.Optional[typing.Union[NetworkFirewall.LoggingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63aa64adbf3b5d2c60e5d6c2881bd83d31fe62d8ff27bbf019cc9af5c73bc5bb(
    *,
    log_types: typing.Sequence[NetworkFirewall.LogType],
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ace01da25292a8e889699aa698a73978bd428f1940d96890409aa76c9bbf80f(
    *,
    protected_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
    destination_cidr: typing.Optional[builtins.str] = None,
    lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
    return_subnets: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__814493a7a334a62a9dce7cd601a0b67fa4c645e77eceab9f1894bb4b630064af(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    firewall: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewall,
    lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e9fd07c167ec8303ff19b47c28c2ae7a6b9056ffd494e1f325d9c91774f3775(
    availability_zone: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46421ac3a9e7f629694391452249c1e15f4a30971c4466574db708fb6b22fb69(
    *,
    firewall: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewall,
    lambda_configuration: typing.Optional[typing.Union[_AwsCustomResourceLambdaConfiguration_be7862df, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__944ba1d4d37915b6f2808152ac7939f147a45c5e12ea1623ea13954a65cf261e(
    *,
    firewall_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
    suricata_rules_capacity: jsii.Number,
    suricata_rules_file_path: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    configure_vpc_routes: typing.Optional[typing.Union[NetworkFirewall.NetworkFirewallVpcRouteProps, typing.Dict[builtins.str, typing.Any]]] = None,
    logging: typing.Optional[typing.Union[NetworkFirewall.LoggingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f05c3bfeda6e475addd75dbb658119f41337a343f71dd7a3cb45945785a81fd9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    credential: typing.Union[typing.Union[OpenSearchAdminUser.PasswordParameterProps, typing.Dict[builtins.str, typing.Any]], typing.Union[OpenSearchAdminUser.PasswordSecretProps, typing.Dict[builtins.str, typing.Any]]],
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
    username: _aws_cdk_aws_ssm_ceddda9d.IParameter,
    domain_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87e83aa659a038d1d6467b416d68f6f82588ff6c82d60e1b04a4cc02ae9820b1(
    *,
    parameter: _aws_cdk_aws_ssm_ceddda9d.IParameter,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d706a882ed5eb4a1c10b333c6f500d9fcfa8fd104530a097e0ecd94dee86a6e0(
    *,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e5d4a2781889ac772b1c0704e7cebf5e6ac1d19b2867f5bc9037a31e4154d80(
    *,
    credential: typing.Union[typing.Union[OpenSearchAdminUser.PasswordParameterProps, typing.Dict[builtins.str, typing.Any]], typing.Union[OpenSearchAdminUser.PasswordSecretProps, typing.Dict[builtins.str, typing.Any]]],
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
    username: _aws_cdk_aws_ssm_ceddda9d.IParameter,
    domain_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72506fb1500f5c6ff037645c7a1d482804fef9969a9f476faa3007d5e6fa7bea(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
    domain_admin: _aws_cdk_aws_iam_ceddda9d.IRole,
    provisioning_configuration_path: builtins.str,
    allow_destructive_operations: typing.Optional[_DestructiveOperation_8d644d1e] = None,
    cluster_settings: typing.Optional[typing.Mapping[typing.Any, typing.Any]] = None,
    dynamic_role_mappings: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b50e5bc6a511d188b3051cff66623c572439b5a787e541535cb7aff488a3a4b(
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
    domain_admin: _aws_cdk_aws_iam_ceddda9d.IRole,
    provisioning_configuration_path: builtins.str,
    allow_destructive_operations: typing.Optional[_DestructiveOperation_8d644d1e] = None,
    cluster_settings: typing.Optional[typing.Mapping[typing.Any, typing.Any]] = None,
    dynamic_role_mappings: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d69e7a0beffe2e3a42399915991e2a76276f793119ccb9d657b34d61446614a5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
    domain_authentication: _aws_cdk_aws_iam_ceddda9d.IRole,
    flow_framework_template_path: builtins.str,
    allow_destructive_operations: typing.Optional[_DestructiveOperation_8d644d1e] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    template_asset_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, _aws_cdk_aws_s3_assets_ceddda9d.Asset]]] = None,
    template_creation_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    template_provision_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15ed95aace02881b8569dbc646a97babb96362b68f80e2430bf5a39451100dcd(
    workflow_step_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f58df00bbfc2d32adb19d8a2c49f777d13be48601c598cab05917867b09232cf(
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.IDomain,
    domain_authentication: _aws_cdk_aws_iam_ceddda9d.IRole,
    flow_framework_template_path: builtins.str,
    allow_destructive_operations: typing.Optional[_DestructiveOperation_8d644d1e] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    template_asset_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, _aws_cdk_aws_s3_assets_ceddda9d.Asset]]] = None,
    template_creation_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    template_provision_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e73123a147ab61f7f5e1b4dd63bd49a5f6fb5beb4d9c15b2e42a424fefc81885(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    aws_managed_rule_groups: typing.Optional[typing.Sequence[typing.Union[typing.Union[WebApplicationFirewall.AwsManagedRuleGroupConfig, typing.Dict[builtins.str, typing.Any]], WebApplicationFirewall.AwsManagedRuleGroup]]] = None,
    cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[WebApplicationFirewall.WebApplicationFirewallLoggingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    sampled_requests_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb17097905b85e77dd68963514cb93012718b2a0e88a07310d41bfbdfd329ddd(
    resource: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__366b30b777356565a2d25147dde650448b63ce88d57853714610c9c96d12842d(
    *,
    rule_group: WebApplicationFirewall.AwsManagedRuleGroup,
    rule_group_action_overrides: typing.Optional[typing.Sequence[typing.Union[WebApplicationFirewall.OverrideConfig, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2807f89045ac6870539a2474ad79baf282359ba013194ddd634bfa7af26097e(
    *,
    action: WebApplicationFirewall.OverrideAction,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__348a0b36a02918bbbf326c8a9c00bbbc2223fe506081f7f3740db4cb18af2a91(
    *,
    log_group_name_affix: builtins.str,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc0222cf648cd9f034f008b4afecb517b89d7528ca30105206f9add718afdb21(
    *,
    aws_managed_rule_groups: typing.Optional[typing.Sequence[typing.Union[typing.Union[WebApplicationFirewall.AwsManagedRuleGroupConfig, typing.Dict[builtins.str, typing.Any]], WebApplicationFirewall.AwsManagedRuleGroup]]] = None,
    cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[WebApplicationFirewall.WebApplicationFirewallLoggingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    sampled_requests_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
