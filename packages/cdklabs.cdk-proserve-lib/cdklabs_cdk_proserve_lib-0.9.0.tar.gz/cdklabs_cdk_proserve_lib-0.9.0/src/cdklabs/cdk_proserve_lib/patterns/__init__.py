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
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_imagebuilder as _aws_cdk_aws_imagebuilder_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8
from ..constructs import (
    Ec2ImagePipeline as _Ec2ImagePipeline_08b5ca60,
    Ec2ImagePipelineBaseProps as _Ec2ImagePipelineBaseProps_b9c7b595,
)
from ..types import LambdaConfiguration as _LambdaConfiguration_9f8afc24


class ApiGatewayStaticHosting(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting",
):
    '''(experimental) A pattern that deploys resources to support the hosting of static assets within an AWS account.

    Unlike the normal pattern for static content hosting (Amazon S3 fronted by Amazon CloudFront), this pattern instead
    uses a combination of Amazon S3, AWS Lambda, and Amazon API Gateway. This can be useful for rapidly deploying a
    static website that follows best practices when Amazon CloudFront is not available.

    The construct also handles encryption for the framework resources using either a provided KMS key or an
    AWS managed key.

    There are two methods for exposing the URL to consumers - the default API execution endpoint or via a custom domain
    name setup.

    If using the default API execution endpoint, you must provide a base path as this will translate to the
    stage name of the REST API. You must also ensure that all relative links in the static content either reference
    the base path in URLs relative to the root (e.g. preceded by '/') or uses URLs that are relative to the current
    directory (e.g. no '/').

    If using the custom domain name, then you do not need to provide a base path and relative links in your static
    content will not require modification. You can choose to specify a base path with this option if so desired - in
    that case, similar rules regarding relative URLs in the static content above must be followed.

    :stability: experimental

    Example::

        import { ApiGatewayStaticHosting } from '@cdklabs/cdk-proserve-lib/patterns';
        import { EndpointType } from 'aws-cdk-lib/aws-apigateway';
        
        new ApiGatewayStaticHosting(this, 'MyWebsite', {
            asset: {
                id: 'Entry',
                path: join(__dirname, 'assets', 'website', 'dist'),
                spaIndexPageName: 'index.html'
            },
            domain: {
                basePath: 'public'
            },
            endpoint: {
                types: [EndpointType.REGIONAL]
            },
            retainStoreOnDeletion: true,
            versionTag: '1.0.2'
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        asset: typing.Union["ApiGatewayStaticHosting.Asset", typing.Dict[builtins.str, typing.Any]],
        domain: typing.Union[typing.Union["ApiGatewayStaticHosting.CustomDomainConfiguration", typing.Dict[builtins.str, typing.Any]], typing.Union["ApiGatewayStaticHosting.DefaultEndpointConfiguration", typing.Dict[builtins.str, typing.Any]]],
        access_logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        access_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        api_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        endpoint: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        retain_store_on_deletion: typing.Optional[builtins.bool] = None,
        version_tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Creates a new static hosting pattern.

        :param scope: Parent to which the pattern belongs.
        :param id: Unique identifier for this instance.
        :param asset: (experimental) Metadata about the static assets to host.
        :param domain: (experimental) Configuration information for the distribution endpoint that will be used to serve static content.
        :param access_logging_bucket: (experimental) Amazon S3 bucket where access logs should be stored. Default: undefined A new bucket will be created for storing access logs
        :param access_policy: (experimental) Resource access policy to define on the API itself to control who can invoke the endpoint.
        :param api_log_destination: (experimental) Destination where Amazon API Gateway logs can be sent.
        :param encryption: (experimental) Encryption key for protecting the framework resources. Default: undefined AWS service-managed encryption keys will be used where available
        :param endpoint: (experimental) Endpoint deployment information for the REST API. Default: undefined Will deploy an edge-optimized API
        :param lambda_configuration: (experimental) Optional configuration settings for the backend handler.
        :param retain_store_on_deletion: (experimental) Whether or not to retain the Amazon S3 bucket where static assets are deployed on stack deletion. Default: false The Amazon S3 bucket and all assets contained within will be deleted
        :param version_tag: (experimental) A version identifier to deploy to the Amazon S3 bucket to help with rapid identification of current deployment This will appear as ``metadata.json`` at the root of the bucket. Default: undefined No version information will be deployed to the Amazon S3 bucket

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__926e3ab1cdccdb34f4dc75a68890781e04a583c1ec8481b471267ea1ecbb3c22)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApiGatewayStaticHostingProps(
            asset=asset,
            domain=domain,
            access_logging_bucket=access_logging_bucket,
            access_policy=access_policy,
            api_log_destination=api_log_destination,
            encryption=encryption,
            endpoint=endpoint,
            lambda_configuration=lambda_configuration,
            retain_store_on_deletion=retain_store_on_deletion,
            version_tag=version_tag,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="components")
    def components(self) -> "ApiGatewayStaticHosting.PatternComponents":
        '''(experimental) Provides access to the underlying components of the pattern as an escape hatch.

        WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not
        behave as expected or designed. You do so at your own risk.

        :stability: experimental
        '''
        return typing.cast("ApiGatewayStaticHosting.PatternComponents", jsii.get(self, "components"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''(experimental) URL for the API that distributes the static content.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="customDomainNameAlias")
    def custom_domain_name_alias(self) -> typing.Optional[builtins.str]:
        '''(experimental) Alias domain name for the API that distributes the static content.

        This is only available if the custom domain name configuration was provided to the pattern. In that event, you
        would then create either a CNAME or ALIAS record in your DNS system that maps your custom domain name to this
        value.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDomainNameAlias"))

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting.Asset",
        jsii_struct_bases=[],
        name_mapping={
            "id": "id",
            "path": "path",
            "spa_index_page_name": "spaIndexPageName",
        },
    )
    class Asset:
        def __init__(
            self,
            *,
            id: builtins.str,
            path: typing.Union[builtins.str, typing.Sequence[builtins.str]],
            spa_index_page_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''(experimental) Static Asset Definition.

            :param id: (experimental) Unique identifier to delineate an asset from other assets.
            :param path: (experimental) Path(s) on the local file system to the static asset(s). Each path must be either a directory or zip containing the assets
            :param spa_index_page_name: (experimental) Name of the index page for a Single Page Application (SPA). This is used as a default key to load when the path provided does not map to a concrete static asset.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__95377bd339103860abda9142b547350593c2c75dc36900d1cafdbd3ed1452918)
                check_type(argname="argument id", value=id, expected_type=type_hints["id"])
                check_type(argname="argument path", value=path, expected_type=type_hints["path"])
                check_type(argname="argument spa_index_page_name", value=spa_index_page_name, expected_type=type_hints["spa_index_page_name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "id": id,
                "path": path,
            }
            if spa_index_page_name is not None:
                self._values["spa_index_page_name"] = spa_index_page_name

        @builtins.property
        def id(self) -> builtins.str:
            '''(experimental) Unique identifier to delineate an asset from other assets.

            :stability: experimental
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def path(self) -> typing.Union[builtins.str, typing.List[builtins.str]]:
            '''(experimental) Path(s) on the local file system to the static asset(s).

            Each path must be either a directory or zip containing the assets

            :stability: experimental
            '''
            result = self._values.get("path")
            assert result is not None, "Required property 'path' is missing"
            return typing.cast(typing.Union[builtins.str, typing.List[builtins.str]], result)

        @builtins.property
        def spa_index_page_name(self) -> typing.Optional[builtins.str]:
            '''(experimental) Name of the index page for a Single Page Application (SPA).

            This is used as a default key to load when the path provided does not map to a concrete static asset.

            :stability: experimental

            Example::

                index.html
            '''
            result = self._values.get("spa_index_page_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "Asset(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting.CustomDomainConfiguration",
        jsii_struct_bases=[],
        name_mapping={"options": "options"},
    )
    class CustomDomainConfiguration:
        def __init__(
            self,
            *,
            options: typing.Union[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, typing.Dict[builtins.str, typing.Any]],
        ) -> None:
            '''(experimental) Domain configuration when using a Custom Domain Name for Amazon API Gateway.

            :param options: (experimental) Options for specifying the custom domain name setup.

            :stability: experimental
            '''
            if isinstance(options, dict):
                options = _aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions(**options)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__fb7dd65e823631a881c3757f3933e65e12d0ec00138d9e332d7bffc3beddf9ee)
                check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "options": options,
            }

        @builtins.property
        def options(self) -> _aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions:
            '''(experimental) Options for specifying the custom domain name setup.

            :stability: experimental
            '''
            result = self._values.get("options")
            assert result is not None, "Required property 'options' is missing"
            return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CustomDomainConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting.DefaultEndpointConfiguration",
        jsii_struct_bases=[],
        name_mapping={"base_path": "basePath"},
    )
    class DefaultEndpointConfiguration:
        def __init__(self, *, base_path: builtins.str) -> None:
            '''(experimental) Domain configuration when using the Amazon API Gateway Default Execution Endpoint.

            :param base_path: (experimental) Base path where all assets will be located. This is because the default execution endpoint does not serve content at the root but off of a stage. As such this base path will be used to create the deployment stage to serve assets from.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__af579bdb0d2e5a9bf7625d102861181c02edc99e90f1bea8aad195fde82acc1f)
                check_type(argname="argument base_path", value=base_path, expected_type=type_hints["base_path"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "base_path": base_path,
            }

        @builtins.property
        def base_path(self) -> builtins.str:
            '''(experimental) Base path where all assets will be located.

            This is because the default execution endpoint does not serve content at the root but off of a stage. As
            such this base path will be used to create the deployment stage to serve assets from.

            :stability: experimental

            Example::

                /dev/site1
            '''
            result = self._values.get("base_path")
            assert result is not None, "Required property 'base_path' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DefaultEndpointConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting.PatternComponents",
        jsii_struct_bases=[],
        name_mapping={
            "distribution": "distribution",
            "proxy": "proxy",
            "store": "store",
        },
    )
    class PatternComponents:
        def __init__(
            self,
            *,
            distribution: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
            proxy: _aws_cdk_aws_lambda_ceddda9d.Function,
            store: _aws_cdk_aws_s3_ceddda9d.Bucket,
        ) -> None:
            '''(experimental) Underlying components for the pattern.

            :param distribution: (experimental) Provides access to the underlying Amazon API Gateway REST API that serves as the distribution endpoint for the static content. WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not behave as expected or designed. You do so at your own risk.
            :param proxy: (experimental) Provides access to the underlying AWS Lambda function that proxies the static content from Amazon S3. WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not behave as expected or designed. You do so at your own risk.
            :param store: (experimental) Provides access to the underlying Amazon S3 bucket that stores the static content. WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not behave as expected or designed. You do so at your own risk.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__c61a977a949d583f93d83ff5cdd17e5856bd473ed360fd24f8219d952c9a0b61)
                check_type(argname="argument distribution", value=distribution, expected_type=type_hints["distribution"])
                check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
                check_type(argname="argument store", value=store, expected_type=type_hints["store"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "distribution": distribution,
                "proxy": proxy,
                "store": store,
            }

        @builtins.property
        def distribution(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
            '''(experimental) Provides access to the underlying Amazon API Gateway REST API that serves as the distribution endpoint for the static content.

            WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not
            behave as expected or designed. You do so at your own risk.

            :stability: experimental
            '''
            result = self._values.get("distribution")
            assert result is not None, "Required property 'distribution' is missing"
            return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, result)

        @builtins.property
        def proxy(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
            '''(experimental) Provides access to the underlying AWS Lambda function that proxies the static content from Amazon S3.

            WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not
            behave as expected or designed. You do so at your own risk.

            :stability: experimental
            '''
            result = self._values.get("proxy")
            assert result is not None, "Required property 'proxy' is missing"
            return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, result)

        @builtins.property
        def store(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
            '''(experimental) Provides access to the underlying Amazon S3 bucket that stores the static content.

            WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not
            behave as expected or designed. You do so at your own risk.

            :stability: experimental
            '''
            result = self._values.get("store")
            assert result is not None, "Required property 'store' is missing"
            return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PatternComponents(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHostingProps",
    jsii_struct_bases=[],
    name_mapping={
        "asset": "asset",
        "domain": "domain",
        "access_logging_bucket": "accessLoggingBucket",
        "access_policy": "accessPolicy",
        "api_log_destination": "apiLogDestination",
        "encryption": "encryption",
        "endpoint": "endpoint",
        "lambda_configuration": "lambdaConfiguration",
        "retain_store_on_deletion": "retainStoreOnDeletion",
        "version_tag": "versionTag",
    },
)
class ApiGatewayStaticHostingProps:
    def __init__(
        self,
        *,
        asset: typing.Union[ApiGatewayStaticHosting.Asset, typing.Dict[builtins.str, typing.Any]],
        domain: typing.Union[typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[ApiGatewayStaticHosting.DefaultEndpointConfiguration, typing.Dict[builtins.str, typing.Any]]],
        access_logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        access_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        api_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        endpoint: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        retain_store_on_deletion: typing.Optional[builtins.bool] = None,
        version_tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for configuring the static hosting pattern.

        :param asset: (experimental) Metadata about the static assets to host.
        :param domain: (experimental) Configuration information for the distribution endpoint that will be used to serve static content.
        :param access_logging_bucket: (experimental) Amazon S3 bucket where access logs should be stored. Default: undefined A new bucket will be created for storing access logs
        :param access_policy: (experimental) Resource access policy to define on the API itself to control who can invoke the endpoint.
        :param api_log_destination: (experimental) Destination where Amazon API Gateway logs can be sent.
        :param encryption: (experimental) Encryption key for protecting the framework resources. Default: undefined AWS service-managed encryption keys will be used where available
        :param endpoint: (experimental) Endpoint deployment information for the REST API. Default: undefined Will deploy an edge-optimized API
        :param lambda_configuration: (experimental) Optional configuration settings for the backend handler.
        :param retain_store_on_deletion: (experimental) Whether or not to retain the Amazon S3 bucket where static assets are deployed on stack deletion. Default: false The Amazon S3 bucket and all assets contained within will be deleted
        :param version_tag: (experimental) A version identifier to deploy to the Amazon S3 bucket to help with rapid identification of current deployment This will appear as ``metadata.json`` at the root of the bucket. Default: undefined No version information will be deployed to the Amazon S3 bucket

        :stability: experimental
        '''
        if isinstance(asset, dict):
            asset = ApiGatewayStaticHosting.Asset(**asset)
        if isinstance(endpoint, dict):
            endpoint = _aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration(**endpoint)
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4baf4c2294bf49627829b500b5815750efb5085b8be745e95cfca95c61678fd6)
            check_type(argname="argument asset", value=asset, expected_type=type_hints["asset"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument access_logging_bucket", value=access_logging_bucket, expected_type=type_hints["access_logging_bucket"])
            check_type(argname="argument access_policy", value=access_policy, expected_type=type_hints["access_policy"])
            check_type(argname="argument api_log_destination", value=api_log_destination, expected_type=type_hints["api_log_destination"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
            check_type(argname="argument retain_store_on_deletion", value=retain_store_on_deletion, expected_type=type_hints["retain_store_on_deletion"])
            check_type(argname="argument version_tag", value=version_tag, expected_type=type_hints["version_tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "asset": asset,
            "domain": domain,
        }
        if access_logging_bucket is not None:
            self._values["access_logging_bucket"] = access_logging_bucket
        if access_policy is not None:
            self._values["access_policy"] = access_policy
        if api_log_destination is not None:
            self._values["api_log_destination"] = api_log_destination
        if encryption is not None:
            self._values["encryption"] = encryption
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration
        if retain_store_on_deletion is not None:
            self._values["retain_store_on_deletion"] = retain_store_on_deletion
        if version_tag is not None:
            self._values["version_tag"] = version_tag

    @builtins.property
    def asset(self) -> ApiGatewayStaticHosting.Asset:
        '''(experimental) Metadata about the static assets to host.

        :stability: experimental
        '''
        result = self._values.get("asset")
        assert result is not None, "Required property 'asset' is missing"
        return typing.cast(ApiGatewayStaticHosting.Asset, result)

    @builtins.property
    def domain(
        self,
    ) -> typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, ApiGatewayStaticHosting.DefaultEndpointConfiguration]:
        '''(experimental) Configuration information for the distribution endpoint that will be used to serve static content.

        :stability: experimental
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, ApiGatewayStaticHosting.DefaultEndpointConfiguration], result)

    @builtins.property
    def access_logging_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) Amazon S3 bucket where access logs should be stored.

        :default: undefined A new bucket will be created for storing access logs

        :stability: experimental
        '''
        result = self._values.get("access_logging_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def access_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''(experimental) Resource access policy to define on the API itself to control who can invoke the endpoint.

        :stability: experimental
        '''
        result = self._values.get("access_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], result)

    @builtins.property
    def api_log_destination(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination]:
        '''(experimental) Destination where Amazon API Gateway logs can be sent.

        :stability: experimental
        '''
        result = self._values.get("api_log_destination")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Encryption key for protecting the framework resources.

        :default: undefined AWS service-managed encryption keys will be used where available

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration]:
        '''(experimental) Endpoint deployment information for the REST API.

        :default: undefined Will deploy an edge-optimized API

        :stability: experimental
        '''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration], result)

    @builtins.property
    def lambda_configuration(self) -> typing.Optional[_LambdaConfiguration_9f8afc24]:
        '''(experimental) Optional configuration settings for the backend handler.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_LambdaConfiguration_9f8afc24], result)

    @builtins.property
    def retain_store_on_deletion(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not to retain the Amazon S3 bucket where static assets are deployed on stack deletion.

        :default: false The Amazon S3 bucket and all assets contained within will be deleted

        :stability: experimental
        '''
        result = self._values.get("retain_store_on_deletion")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) A version identifier to deploy to the Amazon S3 bucket to help with rapid identification of current deployment This will appear as ``metadata.json`` at the root of the bucket.

        :default: undefined No version information will be deployed to the Amazon S3 bucket

        :stability: experimental

        Example::

            1.0.2
        '''
        result = self._values.get("version_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayStaticHostingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Ec2LinuxImagePipeline(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.Ec2LinuxImagePipeline",
):
    '''(experimental) A pattern to build an EC2 Image Pipeline specifically for Linux.

    This pattern contains opinionated code and features to help create a linux
    pipeline. This pattern further simplifies setting up an image pipeline by
    letting you choose specific operating systems and features. In addition, this
    pattern will automatically start the pipeline and wait for it to complete.
    This allows you to reference the AMI from this construct and utilize it in
    your application (see example).

    The example below shows how you can configure an image that contains the AWS
    CLI and retains the SSM agent on the image. The image will have a 100GB root
    volume.

    :stability: experimental

    Example::

        import { CfnOutput } from 'aws-cdk-lib';
        import { Ec2LinuxImagePipeline } from '@cdklabs/cdk-proserve-lib/patterns';
        
        const pipeline = new Ec2LinuxImagePipeline(this, 'ImagePipeline', {
          version: '0.1.0',
          operatingSystem:
            Ec2LinuxImagePipeline.OperatingSystem.AMAZON_LINUX_2023,
          rootVolumeSize: 100,
          features: [
            Ec2LinuxImagePipeline.Feature.AWS_CLI,
            Ec2LinuxImagePipeline.Feature.RETAIN_SSM_AGENT
          ]
        );
        
        new CfnOutput(this, 'AmiId', {
          value: pipeline.latestAmi,
        })
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        extra_components: typing.Optional[typing.Sequence[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
        extra_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        features: typing.Optional[typing.Sequence["Ec2LinuxImagePipeline.Feature"]] = None,
        operating_system: typing.Optional["Ec2LinuxImagePipeline.OperatingSystem"] = None,
        root_volume_size: typing.Optional[jsii.Number] = None,
        version: builtins.str,
        build_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) A pattern to build an EC2 Image Pipeline specifically for Linux.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID.
        :param extra_components: (experimental) Additional components to install in the image. These components will be added after the default Linux components. Use this to add custom components beyond the predefined features.
        :param extra_device_mappings: (experimental) Additional EBS volume mappings to add to the image. These volumes will be added in addition to the root volume. Use this to specify additional storage volumes that should be included in the AMI.
        :param features: (experimental) A list of features to install on the image. Features are predefined sets of components and configurations. Default: [AWS_CLI, RETAIN_SSM_AGENT] Default: [Ec2LinuxImagePipeline.Feature.AWS_CLI, Ec2LinuxImagePipeline.Feature.RETAIN_SSM_AGENT]
        :param operating_system: (experimental) The operating system to use for the image pipeline. Specifies which operating system version to use as the base image. Default: AMAZON_LINUX_2023. Default: Ec2LinuxImagePipeline.OperatingSystem.AMAZON_LINUX_2023
        :param root_volume_size: (experimental) Size for the root volume in GB. Default: 10 GB. Default: 10
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
            type_hints = typing.get_type_hints(_typecheckingstub__cfe75b8964707df740912e083b8358a4e940f27f7259ab820504b6c2ada0e612)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = Ec2LinuxImagePipelineProps(
            extra_components=extra_components,
            extra_device_mappings=extra_device_mappings,
            features=features,
            operating_system=operating_system,
            root_volume_size=root_volume_size,
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
        '''(experimental) The Amazon Resource Name (ARN) of the Image Pipeline.

        Used to uniquely identify this image pipeline.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "imagePipelineArn"))

    @image_pipeline_arn.setter
    def image_pipeline_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__480b8d9ad288b00a9019dff6ab448fa0084409e75666e22ebc710de08d511ef1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imagePipelineArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="imagePipelineTopic")
    def image_pipeline_topic(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
        '''(experimental) The SNS Topic associated with this Image Pipeline.

        Publishes notifications about pipeline execution events.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, jsii.get(self, "imagePipelineTopic"))

    @image_pipeline_topic.setter
    def image_pipeline_topic(self, value: _aws_cdk_aws_sns_ceddda9d.ITopic) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50c054b2b518ad1fdc972c31ac61f4ccead58620ac1a7b23a125009d747bc370)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imagePipelineTopic", value) # pyright: ignore[reportArgumentType]

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

    @latest_ami.setter
    def latest_ami(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e396117a6c4ae570f398094ede114baa7576df8e02406727ef327dda84877bda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latestAmi", value) # pyright: ignore[reportArgumentType]

    @jsii.enum(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.Ec2LinuxImagePipeline.Feature"
    )
    class Feature(enum.Enum):
        '''
        :stability: experimental
        '''

        AWS_CLI = "AWS_CLI"
        '''
        :stability: experimental
        '''
        NICE_DCV = "NICE_DCV"
        '''
        :stability: experimental
        '''
        RETAIN_SSM_AGENT = "RETAIN_SSM_AGENT"
        '''
        :stability: experimental
        '''
        STIG = "STIG"
        '''
        :stability: experimental
        '''
        SCAP = "SCAP"
        '''
        :stability: experimental
        '''

    @jsii.enum(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.Ec2LinuxImagePipeline.OperatingSystem"
    )
    class OperatingSystem(enum.Enum):
        '''
        :stability: experimental
        '''

        RED_HAT_ENTERPRISE_LINUX_8_9 = "RED_HAT_ENTERPRISE_LINUX_8_9"
        '''
        :stability: experimental
        '''
        AMAZON_LINUX_2 = "AMAZON_LINUX_2"
        '''
        :stability: experimental
        '''
        AMAZON_LINUX_2023 = "AMAZON_LINUX_2023"
        '''
        :stability: experimental
        '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.Ec2LinuxImagePipelineProps",
    jsii_struct_bases=[_Ec2ImagePipelineBaseProps_b9c7b595],
    name_mapping={
        "version": "version",
        "build_configuration": "buildConfiguration",
        "description": "description",
        "encryption": "encryption",
        "instance_types": "instanceTypes",
        "lambda_configuration": "lambdaConfiguration",
        "vpc_configuration": "vpcConfiguration",
        "extra_components": "extraComponents",
        "extra_device_mappings": "extraDeviceMappings",
        "features": "features",
        "operating_system": "operatingSystem",
        "root_volume_size": "rootVolumeSize",
    },
)
class Ec2LinuxImagePipelineProps(_Ec2ImagePipelineBaseProps_b9c7b595):
    def __init__(
        self,
        *,
        version: builtins.str,
        build_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
        extra_components: typing.Optional[typing.Sequence[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
        extra_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        features: typing.Optional[typing.Sequence[Ec2LinuxImagePipeline.Feature]] = None,
        operating_system: typing.Optional[Ec2LinuxImagePipeline.OperatingSystem] = None,
        root_volume_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties for creating a Linux STIG Image Pipeline.

        :param version: (experimental) Version of the image pipeline. This must be updated if you make underlying changes to the pipeline configuration.
        :param build_configuration: (experimental) Configuration options for the build process.
        :param description: (experimental) Description of the image pipeline.
        :param encryption: (experimental) KMS key for encryption.
        :param instance_types: (experimental) Instance types for the Image Builder Pipeline. Default: [t3.medium]
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param vpc_configuration: (experimental) VPC configuration for the image pipeline.
        :param extra_components: (experimental) Additional components to install in the image. These components will be added after the default Linux components. Use this to add custom components beyond the predefined features.
        :param extra_device_mappings: (experimental) Additional EBS volume mappings to add to the image. These volumes will be added in addition to the root volume. Use this to specify additional storage volumes that should be included in the AMI.
        :param features: (experimental) A list of features to install on the image. Features are predefined sets of components and configurations. Default: [AWS_CLI, RETAIN_SSM_AGENT] Default: [Ec2LinuxImagePipeline.Feature.AWS_CLI, Ec2LinuxImagePipeline.Feature.RETAIN_SSM_AGENT]
        :param operating_system: (experimental) The operating system to use for the image pipeline. Specifies which operating system version to use as the base image. Default: AMAZON_LINUX_2023. Default: Ec2LinuxImagePipeline.OperatingSystem.AMAZON_LINUX_2023
        :param root_volume_size: (experimental) Size for the root volume in GB. Default: 10 GB. Default: 10

        :stability: experimental
        '''
        if isinstance(build_configuration, dict):
            build_configuration = _Ec2ImagePipeline_08b5ca60.BuildConfigurationProps(**build_configuration)
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if isinstance(vpc_configuration, dict):
            vpc_configuration = _Ec2ImagePipeline_08b5ca60.VpcConfigurationProps(**vpc_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d272e504a6fabc4b04d50467e7c5293e2777ed064ddb4c6626d553e16c42dd65)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument build_configuration", value=build_configuration, expected_type=type_hints["build_configuration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
            check_type(argname="argument vpc_configuration", value=vpc_configuration, expected_type=type_hints["vpc_configuration"])
            check_type(argname="argument extra_components", value=extra_components, expected_type=type_hints["extra_components"])
            check_type(argname="argument extra_device_mappings", value=extra_device_mappings, expected_type=type_hints["extra_device_mappings"])
            check_type(argname="argument features", value=features, expected_type=type_hints["features"])
            check_type(argname="argument operating_system", value=operating_system, expected_type=type_hints["operating_system"])
            check_type(argname="argument root_volume_size", value=root_volume_size, expected_type=type_hints["root_volume_size"])
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
        if extra_components is not None:
            self._values["extra_components"] = extra_components
        if extra_device_mappings is not None:
            self._values["extra_device_mappings"] = extra_device_mappings
        if features is not None:
            self._values["features"] = features
        if operating_system is not None:
            self._values["operating_system"] = operating_system
        if root_volume_size is not None:
            self._values["root_volume_size"] = root_volume_size

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
    ) -> typing.Optional[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps]:
        '''(experimental) Configuration options for the build process.

        :stability: experimental
        '''
        result = self._values.get("build_configuration")
        return typing.cast(typing.Optional[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps], result)

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
    ) -> typing.Optional[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps]:
        '''(experimental) VPC configuration for the image pipeline.

        :stability: experimental
        '''
        result = self._values.get("vpc_configuration")
        return typing.cast(typing.Optional[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps], result)

    @builtins.property
    def extra_components(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]]:
        '''(experimental) Additional components to install in the image.

        These components will be added after the default Linux components.
        Use this to add custom components beyond the predefined features.

        :stability: experimental
        '''
        result = self._values.get("extra_components")
        return typing.cast(typing.Optional[typing.List[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]], result)

    @builtins.property
    def extra_device_mappings(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty]]:
        '''(experimental) Additional EBS volume mappings to add to the image.

        These volumes will be added in addition to the root volume.
        Use this to specify additional storage volumes that should be included in the AMI.

        :stability: experimental
        '''
        result = self._values.get("extra_device_mappings")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty]], result)

    @builtins.property
    def features(self) -> typing.Optional[typing.List[Ec2LinuxImagePipeline.Feature]]:
        '''(experimental) A list of features to install on the image.

        Features are predefined sets of components and configurations.
        Default: [AWS_CLI, RETAIN_SSM_AGENT]

        :default: [Ec2LinuxImagePipeline.Feature.AWS_CLI, Ec2LinuxImagePipeline.Feature.RETAIN_SSM_AGENT]

        :stability: experimental
        '''
        result = self._values.get("features")
        return typing.cast(typing.Optional[typing.List[Ec2LinuxImagePipeline.Feature]], result)

    @builtins.property
    def operating_system(
        self,
    ) -> typing.Optional[Ec2LinuxImagePipeline.OperatingSystem]:
        '''(experimental) The operating system to use for the image pipeline.

        Specifies which operating system version to use as the base image.
        Default: AMAZON_LINUX_2023.

        :default: Ec2LinuxImagePipeline.OperatingSystem.AMAZON_LINUX_2023

        :stability: experimental
        '''
        result = self._values.get("operating_system")
        return typing.cast(typing.Optional[Ec2LinuxImagePipeline.OperatingSystem], result)

    @builtins.property
    def root_volume_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Size for the root volume in GB.

        Default: 10 GB.

        :default: 10

        :stability: experimental
        '''
        result = self._values.get("root_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ec2LinuxImagePipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KeycloakService(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService",
):
    '''(experimental) Deploys a production-grade Keycloak service.

    This service deploys a containerized version of Keycloak using AWS Fargate to host and scale the application. The
    backend database is supported via Amazon Relational Database Service (RDS) and the application is fronted by a
    Network Load Balancer.

    The database will auto-scale based on CDK defaults or a consumer-specified scaling policy. The containers will not
    automatically scale unless a consumer-specified policy is applied.

    It is recommended to set the CDK feature flag ``@aws-cdk/aws-rds:databaseProxyUniqueResourceName`` in
    ``cdk.json`` to true. If not done, the database proxy name may conflict with other proxies in your account and
    will prevent you from being able to deploy more than one KeycloakService.

    At a minimum this pattern requires the consumer to build and provide their own Keycloak container image for
    deployment as well provide hostname configuration details. The Keycloak container image version MUST match the
    version specified for use here and must include the Amazon Aurora JDBC driver pre-installed. A minimum viable
    Dockerfile for that container image looks like::

       ARG VERSION=26.3.2

       FROM quay.io/keycloak/keycloak:${VERSION} AS builder

       # Optimizations (not necessary but speed up the container startup)
       ENV KC_DB=postgres
       ENV KC_DB_DRIVER=software.amazon.jdbc.Driver

       WORKDIR /opt/keycloak

       # TLS Configuration
       COPY --chmod=0666 certs/server.keystore conf/

       # Database Provider
       ADD --chmod=0666 https://github.com/aws/aws-advanced-jdbc-wrapper/releases/download/2.6.2/aws-advanced-jdbc-wrapper-2.6.2.jar providers/aws-advanced-jdbc-wrapper.jar

       RUN /opt/keycloak/bin/kc.sh build

       FROM quay.io/keycloak/keycloak:${VERSION}
       COPY --from=builder /opt/keycloak /opt/keycloak

       ENTRYPOINT [ "/opt/keycloak/bin/kc.sh" ]
       CMD [ "start" ]
    ------

    By default, the Keycloak service is deployed internally in isolated and/or private subnets but can be exposed by
    providing the fabric configuration option to expose the service with an internet-facing load balancer.

    :stability: experimental

    Example::

        import { join } from 'node:path';
        import { KeycloakService } from '@cdklabs/cdk-proserve-lib/patterns';
        import { App, Environment, RemovalPolicy, Stack } from 'aws-cdk-lib';
        import { IpAddresses, SubnetType, Vpc } from 'aws-cdk-lib/aws-ec2';
        import { AssetImage } from 'aws-cdk-lib/aws-ecs';
        import { Platform } from 'aws-cdk-lib/aws-ecr-assets';
        
        const dnsZoneName = 'example.com';
        const network = Vpc.fromLookup(this, 'Network', {
            vpcId: 'vpc-xxxx'
        });
        
        new KeycloakService(this, 'Keycloak', {
            keycloak: {
                image: AssetImage.fromAsset(join(__dirname, '..', 'src', 'keycloak'), {
                    platform: Platform.LINUX_AMD64
                }),
                configuration: {
                    hostnames: {
                        default: `auth.${dnsZoneName}`,
                        admin: `admin.auth.${dnsZoneName}`
                    },
                    loggingLevel: 'info'
                },
                version: KeycloakService.EngineVersion.V26_3_2
            },
            overrides: {
                cluster: {
                    scaling: {
                        minimum: 1,
                        maximum: 2
                    }
                }
                fabric: {
                    dnsZoneName: dnsZoneName,
                    internetFacing: true
                }
            },
            vpc: network
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        keycloak: typing.Union["KeycloakService.KeycloakProps", typing.Dict[builtins.str, typing.Any]],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        log_retention_duration: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        overrides: typing.Optional[typing.Union["KeycloakService.InfrastructureConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policies: typing.Optional[typing.Union["KeycloakService.RemovalPolicies", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Create a new Keycloak service.

        :param scope: Parent to which this construct belongs.
        :param id: Unique identifier for the component.
        :param keycloak: (experimental) Options related to Keycloak.
        :param vpc: (experimental) Network where Keycloak should be deployed.
        :param encryption: (experimental) Key for encrypting resource data. If not specified, a new key will be created
        :param log_retention_duration: (experimental) How long to retain logs for all components. If not specified, logs will be retained for one week
        :param overrides: (experimental) Overrides for prescribed defaults for the infrastructure.
        :param removal_policies: (experimental) Policies to lifecycle various components of the pattern during stack actions. If not specified, resources will be retained

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fab7697cc8698d9567cdcbe737e05dbb050c2e9c228d45bc10c1fcd17de5c3f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = KeycloakServiceProps(
            keycloak=keycloak,
            vpc=vpc,
            encryption=encryption,
            log_retention_duration=log_retention_duration,
            overrides=overrides,
            removal_policies=removal_policies,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="adminUser")
    def admin_user(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''(experimental) Credentials for bootstrapping a local admin user in Keycloak.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.get(self, "adminUser"))

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.ApplicationConfiguration",
        jsii_struct_bases=[],
        name_mapping={
            "hostnames": "hostnames",
            "admin_user": "adminUser",
            "logging_level": "loggingLevel",
            "management": "management",
            "path": "path",
            "port": "port",
        },
    )
    class ApplicationConfiguration:
        def __init__(
            self,
            *,
            hostnames: typing.Union["KeycloakService.HostnameConfiguration", typing.Dict[builtins.str, typing.Any]],
            admin_user: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
            logging_level: typing.Optional[builtins.str] = None,
            management: typing.Optional[typing.Union["KeycloakService.ManagementConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
            path: typing.Optional[builtins.str] = None,
            port: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''(experimental) Configuration for the Keycloak application.

            :param hostnames: (experimental) Hostname configuration for Keycloak.
            :param admin_user: (experimental) Credentials for bootstrapping a local admin user within Keycloak. Must be a key-value secret with ``username`` and ``password`` fields `Guide: Bootstrapping an Admin Account <https://www.keycloak.org/server/hostname>`_ By default, a new secret will be created with a username and randomly generated password
            :param logging_level: (experimental) Level of information for Keycloak to log. Default: warn
            :param management: (experimental) Configuration options for the management interface. If not specified, the management interface is disabled
            :param path: (experimental) Optional alternative relative path for serving content. Default: /
            :param port: (experimental) Port to serve the standard HTTPS web traffic on. Default: 443

            :stability: experimental
            '''
            if isinstance(hostnames, dict):
                hostnames = KeycloakService.HostnameConfiguration(**hostnames)
            if isinstance(management, dict):
                management = KeycloakService.ManagementConfiguration(**management)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__f80c0a4fd9c4c8dd41be39585e21c306ed5d241b22443fa1feaa4985b8b2e868)
                check_type(argname="argument hostnames", value=hostnames, expected_type=type_hints["hostnames"])
                check_type(argname="argument admin_user", value=admin_user, expected_type=type_hints["admin_user"])
                check_type(argname="argument logging_level", value=logging_level, expected_type=type_hints["logging_level"])
                check_type(argname="argument management", value=management, expected_type=type_hints["management"])
                check_type(argname="argument path", value=path, expected_type=type_hints["path"])
                check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "hostnames": hostnames,
            }
            if admin_user is not None:
                self._values["admin_user"] = admin_user
            if logging_level is not None:
                self._values["logging_level"] = logging_level
            if management is not None:
                self._values["management"] = management
            if path is not None:
                self._values["path"] = path
            if port is not None:
                self._values["port"] = port

        @builtins.property
        def hostnames(self) -> "KeycloakService.HostnameConfiguration":
            '''(experimental) Hostname configuration for Keycloak.

            :stability: experimental
            '''
            result = self._values.get("hostnames")
            assert result is not None, "Required property 'hostnames' is missing"
            return typing.cast("KeycloakService.HostnameConfiguration", result)

        @builtins.property
        def admin_user(
            self,
        ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
            '''(experimental) Credentials for bootstrapping a local admin user within Keycloak.

            Must be a key-value secret with ``username`` and ``password`` fields

            `Guide: Bootstrapping an Admin Account <https://www.keycloak.org/server/hostname>`_

            By default, a new secret will be created with a username and randomly generated password

            :stability: experimental
            '''
            result = self._values.get("admin_user")
            return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

        @builtins.property
        def logging_level(self) -> typing.Optional[builtins.str]:
            '''(experimental) Level of information for Keycloak to log.

            :default: warn

            :stability: experimental
            '''
            result = self._values.get("logging_level")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def management(
            self,
        ) -> typing.Optional["KeycloakService.ManagementConfiguration"]:
            '''(experimental) Configuration options for the management interface.

            If not specified, the management interface is disabled

            :stability: experimental
            '''
            result = self._values.get("management")
            return typing.cast(typing.Optional["KeycloakService.ManagementConfiguration"], result)

        @builtins.property
        def path(self) -> typing.Optional[builtins.str]:
            '''(experimental) Optional alternative relative path for serving content.

            :default: /

            :stability: experimental
            '''
            result = self._values.get("path")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def port(self) -> typing.Optional[jsii.Number]:
            '''(experimental) Port to serve the standard HTTPS web traffic on.

            :default: 443

            :stability: experimental
            '''
            result = self._values.get("port")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ApplicationConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.ClusterConfiguration",
        jsii_struct_bases=[],
        name_mapping={"scaling": "scaling", "sizing": "sizing"},
    )
    class ClusterConfiguration:
        def __init__(
            self,
            *,
            scaling: typing.Optional[typing.Union["KeycloakService.ClusterScalingConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
            sizing: typing.Optional[typing.Union["KeycloakService.TaskSizingConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''(experimental) Configuration options for the cluster.

            :param scaling: (experimental) Boundaries for cluster scaling. If not specified, auto scaling is disabled
            :param sizing: (experimental) Resource allocation options for each Keycloak task. If not specified, each task gets 1 vCPU and 2GB memory Guidance on sizing can be found `here <https://www.keycloak.org/high-availability/concepts-memory-and-cpu-sizing>`_

            :stability: experimental
            '''
            if isinstance(scaling, dict):
                scaling = KeycloakService.ClusterScalingConfiguration(**scaling)
            if isinstance(sizing, dict):
                sizing = KeycloakService.TaskSizingConfiguration(**sizing)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b9b6b8d8fbc3e6c32a2b26155533cdf9ef74e2edad588884e68cdfce6d2249eb)
                check_type(argname="argument scaling", value=scaling, expected_type=type_hints["scaling"])
                check_type(argname="argument sizing", value=sizing, expected_type=type_hints["sizing"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if scaling is not None:
                self._values["scaling"] = scaling
            if sizing is not None:
                self._values["sizing"] = sizing

        @builtins.property
        def scaling(
            self,
        ) -> typing.Optional["KeycloakService.ClusterScalingConfiguration"]:
            '''(experimental) Boundaries for cluster scaling.

            If not specified, auto scaling is disabled

            :stability: experimental
            '''
            result = self._values.get("scaling")
            return typing.cast(typing.Optional["KeycloakService.ClusterScalingConfiguration"], result)

        @builtins.property
        def sizing(self) -> typing.Optional["KeycloakService.TaskSizingConfiguration"]:
            '''(experimental) Resource allocation options for each Keycloak task.

            If not specified, each task gets 1 vCPU and 2GB memory

            Guidance on sizing can be found `here <https://www.keycloak.org/high-availability/concepts-memory-and-cpu-sizing>`_

            :stability: experimental
            '''
            result = self._values.get("sizing")
            return typing.cast(typing.Optional["KeycloakService.TaskSizingConfiguration"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ClusterConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.ClusterRequestCountScalingConfiguration",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled", "threshold": "threshold"},
    )
    class ClusterRequestCountScalingConfiguration:
        def __init__(
            self,
            *,
            enabled: builtins.bool,
            threshold: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''(experimental) Configuration options for scaling the cluster based on number of active requests.

            :param enabled: (experimental) Whether to enable scaling based on the number of active requests. Scaling is always enabled based on CPU utilization if the scaling bounds have been provided
            :param threshold: (experimental) The pivotal number of active requests through the load balancer before a scaling action is triggered. Used to fine-tune scaling to your specific capacity needs. If not specified but auto scaling is enabled, then by default scaling out will occur when the number of active requests exceeds 80 and scaling in will occur when this number drops below 80. All scaling activities incur a 5 minute cooldown period.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__231f1c6f7a0cff8811547d8037df0c5d9d85ca9643fc82af2edf832e6cd51f93)
                check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
                check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "enabled": enabled,
            }
            if threshold is not None:
                self._values["threshold"] = threshold

        @builtins.property
        def enabled(self) -> builtins.bool:
            '''(experimental) Whether to enable scaling based on the number of active requests.

            Scaling is always enabled based on CPU utilization if the scaling bounds have been provided

            :stability: experimental
            '''
            result = self._values.get("enabled")
            assert result is not None, "Required property 'enabled' is missing"
            return typing.cast(builtins.bool, result)

        @builtins.property
        def threshold(self) -> typing.Optional[jsii.Number]:
            '''(experimental) The pivotal number of active requests through the load balancer before a scaling action is triggered.

            Used
            to fine-tune scaling to your specific capacity needs.

            If not specified but auto scaling is enabled, then by default scaling out will occur when the number of
            active requests exceeds 80 and scaling in will occur when this number drops below 80. All scaling activities
            incur a 5 minute cooldown period.

            :stability: experimental
            '''
            result = self._values.get("threshold")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ClusterRequestCountScalingConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.ClusterScalingConfiguration",
        jsii_struct_bases=[],
        name_mapping={
            "maximum": "maximum",
            "minimum": "minimum",
            "request_count_scaling": "requestCountScaling",
        },
    )
    class ClusterScalingConfiguration:
        def __init__(
            self,
            *,
            maximum: jsii.Number,
            minimum: jsii.Number,
            request_count_scaling: typing.Optional[typing.Union["KeycloakService.ClusterRequestCountScalingConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''(experimental) Configuration options for scaling the cluster.

            :param maximum: (experimental) The minimum amount of Keycloak tasks that should be active at any given time.
            :param minimum: (experimental) The maximum amount of Keycloak tasks that should be active at any given time.
            :param request_count_scaling: (experimental) Configuration options for scaling the cluster based on number of active requests. Scaling is always enabled based on CPU utilization if the scaling bounds have been provided

            :stability: experimental
            '''
            if isinstance(request_count_scaling, dict):
                request_count_scaling = KeycloakService.ClusterRequestCountScalingConfiguration(**request_count_scaling)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__a1f26f24157aca6309c29c124d917259a7186571773c2d8d19f0542214ea4a3b)
                check_type(argname="argument maximum", value=maximum, expected_type=type_hints["maximum"])
                check_type(argname="argument minimum", value=minimum, expected_type=type_hints["minimum"])
                check_type(argname="argument request_count_scaling", value=request_count_scaling, expected_type=type_hints["request_count_scaling"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "maximum": maximum,
                "minimum": minimum,
            }
            if request_count_scaling is not None:
                self._values["request_count_scaling"] = request_count_scaling

        @builtins.property
        def maximum(self) -> jsii.Number:
            '''(experimental) The minimum amount of Keycloak tasks that should be active at any given time.

            :stability: experimental
            '''
            result = self._values.get("maximum")
            assert result is not None, "Required property 'maximum' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def minimum(self) -> jsii.Number:
            '''(experimental) The maximum amount of Keycloak tasks that should be active at any given time.

            :stability: experimental
            '''
            result = self._values.get("minimum")
            assert result is not None, "Required property 'minimum' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def request_count_scaling(
            self,
        ) -> typing.Optional["KeycloakService.ClusterRequestCountScalingConfiguration"]:
            '''(experimental) Configuration options for scaling the cluster based on number of active requests.

            Scaling is always enabled based on CPU utilization if the scaling bounds have been provided

            :stability: experimental
            '''
            result = self._values.get("request_count_scaling")
            return typing.cast(typing.Optional["KeycloakService.ClusterRequestCountScalingConfiguration"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ClusterScalingConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    class EngineVersion(
        metaclass=jsii.JSIIMeta,
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.EngineVersion",
    ):
        '''(experimental) Versions of the Keycloak application.

        :stability: experimental
        '''

        @jsii.member(jsii_name="of")
        @builtins.classmethod
        def of(cls, version: builtins.str) -> "KeycloakService.EngineVersion":
            '''(experimental) Create a new KeycloakVersion with an arbitrary version.

            :param version: Version of Keycloak.

            :return: KeycloakVersion

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b600bad4a56f0e04b8a1a8d27f269450defbf1c49c6c51c507bdbdc0a24f382d)
                check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            return typing.cast("KeycloakService.EngineVersion", jsii.sinvoke(cls, "of", [version]))

        @jsii.member(jsii_name="is")
        def is_(self, keycloak: "KeycloakService.EngineVersion") -> builtins.bool:
            '''(experimental) Determines if the KeycloakVersion matches a specific version.

            :param keycloak: Version to match against.

            :return: True if the current version matches the target version, false otherwise

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__917661cfb6f2356a5fa1118db4799671f72af53fe4738975f673d0b5cbe0b28a)
                check_type(argname="argument keycloak", value=keycloak, expected_type=type_hints["keycloak"])
            return typing.cast(builtins.bool, jsii.invoke(self, "is", [keycloak]))

        @jsii.python.classproperty
        @jsii.member(jsii_name="V26_3_2")
        def V26_3_2(cls) -> "KeycloakService.EngineVersion":
            '''(experimental) Version 26.3.2.

            :stability: experimental
            '''
            return typing.cast("KeycloakService.EngineVersion", jsii.sget(cls, "V26_3_2"))

        @builtins.property
        @jsii.member(jsii_name="value")
        def value(self) -> builtins.str:
            '''(experimental) The full version string.

            :stability: experimental
            '''
            return typing.cast(builtins.str, jsii.get(self, "value"))

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.FabricConfiguration",
        jsii_struct_bases=[],
        name_mapping={
            "dns_zone_name": "dnsZoneName",
            "internet_facing": "internetFacing",
        },
    )
    class FabricConfiguration:
        def __init__(
            self,
            *,
            dns_zone_name: typing.Optional[builtins.str] = None,
            internet_facing: typing.Optional[builtins.bool] = None,
        ) -> None:
            '''(experimental) Configuration options for the fabric.

            :param dns_zone_name: (experimental) Name of the Route53 DNS Zone where the Keycloak hostnames should be automatically configured if provided. By default, no Route53 records will be created
            :param internet_facing: (experimental) Whether or not the load balancer should be exposed to the external network. Default: false

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__ba771327ecd99e8860b7d2f861530bb282eacdc2c8a73490259c1f69e3976944)
                check_type(argname="argument dns_zone_name", value=dns_zone_name, expected_type=type_hints["dns_zone_name"])
                check_type(argname="argument internet_facing", value=internet_facing, expected_type=type_hints["internet_facing"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if dns_zone_name is not None:
                self._values["dns_zone_name"] = dns_zone_name
            if internet_facing is not None:
                self._values["internet_facing"] = internet_facing

        @builtins.property
        def dns_zone_name(self) -> typing.Optional[builtins.str]:
            '''(experimental) Name of the Route53 DNS Zone where the Keycloak hostnames should be automatically configured if provided.

            By default, no Route53 records will be created

            :stability: experimental

            Example::

                example.com
            '''
            result = self._values.get("dns_zone_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def internet_facing(self) -> typing.Optional[builtins.bool]:
            '''(experimental) Whether or not the load balancer should be exposed to the external network.

            :default: false

            :stability: experimental
            '''
            result = self._values.get("internet_facing")
            return typing.cast(typing.Optional[builtins.bool], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FabricConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.HostnameConfiguration",
        jsii_struct_bases=[],
        name_mapping={"default": "default", "admin": "admin"},
    )
    class HostnameConfiguration:
        def __init__(
            self,
            *,
            default: builtins.str,
            admin: typing.Optional[builtins.str] = None,
        ) -> None:
            '''(experimental) Details for the Keycloak hostname configuration.

            `Guide: Configuring the hostname <https://www.keycloak.org/server/hostname>`_

            :param default: (experimental) Hostname for all endpoints.
            :param admin: (experimental) Optional hostname for the administration endpoint. This allows for the separation of the user and administration endpoints for increased security By default, the administrative endpoints will use the default hostname unless this is specified

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__11844e1d564f7809621812d17ba3175a9188b525ff28317671bf40e446c0bc51)
                check_type(argname="argument default", value=default, expected_type=type_hints["default"])
                check_type(argname="argument admin", value=admin, expected_type=type_hints["admin"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "default": default,
            }
            if admin is not None:
                self._values["admin"] = admin

        @builtins.property
        def default(self) -> builtins.str:
            '''(experimental) Hostname for all endpoints.

            :stability: experimental

            Example::

                auth.example.com
            '''
            result = self._values.get("default")
            assert result is not None, "Required property 'default' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def admin(self) -> typing.Optional[builtins.str]:
            '''(experimental) Optional hostname for the administration endpoint.

            This allows for the separation of the user and administration endpoints for increased security

            By default, the administrative endpoints will use the default hostname unless this is specified

            :stability: experimental

            Example::

                admin.auth.example.com
            '''
            result = self._values.get("admin")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HostnameConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.InfrastructureConfiguration",
        jsii_struct_bases=[],
        name_mapping={
            "cluster": "cluster",
            "database": "database",
            "fabric": "fabric",
        },
    )
    class InfrastructureConfiguration:
        def __init__(
            self,
            *,
            cluster: typing.Optional[typing.Union["KeycloakService.ClusterConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
            database: typing.Optional[typing.Union[typing.Union["KeycloakService.ServerlessDatabaseConfiguration", typing.Dict[builtins.str, typing.Any]], typing.Union["KeycloakService.TraditionalDatabaseConfiguration", typing.Dict[builtins.str, typing.Any]]]] = None,
            fabric: typing.Optional[typing.Union["KeycloakService.FabricConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        ) -> None:
            '''(experimental) Overrides for prescribed defaults for the infrastructure.

            :param cluster: (experimental) Overrides related to the application hosting infrastructure.
            :param database: (experimental) Overrides related to the database infrastructure.
            :param fabric: (experimental) Overrides related to the networking infrastructure.

            :stability: experimental
            '''
            if isinstance(cluster, dict):
                cluster = KeycloakService.ClusterConfiguration(**cluster)
            if isinstance(fabric, dict):
                fabric = KeycloakService.FabricConfiguration(**fabric)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__33df0bf714e8ea28a78fdc53f282c21b6d6977d2f001bdb5a7191602f940fa08)
                check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
                check_type(argname="argument database", value=database, expected_type=type_hints["database"])
                check_type(argname="argument fabric", value=fabric, expected_type=type_hints["fabric"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if cluster is not None:
                self._values["cluster"] = cluster
            if database is not None:
                self._values["database"] = database
            if fabric is not None:
                self._values["fabric"] = fabric

        @builtins.property
        def cluster(self) -> typing.Optional["KeycloakService.ClusterConfiguration"]:
            '''(experimental) Overrides related to the application hosting infrastructure.

            :stability: experimental
            '''
            result = self._values.get("cluster")
            return typing.cast(typing.Optional["KeycloakService.ClusterConfiguration"], result)

        @builtins.property
        def database(
            self,
        ) -> typing.Optional[typing.Union["KeycloakService.ServerlessDatabaseConfiguration", "KeycloakService.TraditionalDatabaseConfiguration"]]:
            '''(experimental) Overrides related to the database infrastructure.

            :stability: experimental
            '''
            result = self._values.get("database")
            return typing.cast(typing.Optional[typing.Union["KeycloakService.ServerlessDatabaseConfiguration", "KeycloakService.TraditionalDatabaseConfiguration"]], result)

        @builtins.property
        def fabric(self) -> typing.Optional["KeycloakService.FabricConfiguration"]:
            '''(experimental) Overrides related to the networking infrastructure.

            :stability: experimental
            '''
            result = self._values.get("fabric")
            return typing.cast(typing.Optional["KeycloakService.FabricConfiguration"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "InfrastructureConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.KeycloakProps",
        jsii_struct_bases=[],
        name_mapping={
            "configuration": "configuration",
            "image": "image",
            "version": "version",
        },
    )
    class KeycloakProps:
        def __init__(
            self,
            *,
            configuration: typing.Union["KeycloakService.ApplicationConfiguration", typing.Dict[builtins.str, typing.Any]],
            image: _aws_cdk_aws_ecs_ceddda9d.ContainerImage,
            version: "KeycloakService.EngineVersion",
        ) -> None:
            '''(experimental) Options related to Keycloak.

            :param configuration: (experimental) Configuration for Keycloak.
            :param image: (experimental) Keycloak container image to use.
            :param version: (experimental) Keycloak version.

            :stability: experimental
            '''
            if isinstance(configuration, dict):
                configuration = KeycloakService.ApplicationConfiguration(**configuration)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__f17470288c514b03a9ef92c6abea1d24ebe334309c15f753b07daa18e29ee9cc)
                check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
                check_type(argname="argument image", value=image, expected_type=type_hints["image"])
                check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "configuration": configuration,
                "image": image,
                "version": version,
            }

        @builtins.property
        def configuration(self) -> "KeycloakService.ApplicationConfiguration":
            '''(experimental) Configuration for Keycloak.

            :stability: experimental
            '''
            result = self._values.get("configuration")
            assert result is not None, "Required property 'configuration' is missing"
            return typing.cast("KeycloakService.ApplicationConfiguration", result)

        @builtins.property
        def image(self) -> _aws_cdk_aws_ecs_ceddda9d.ContainerImage:
            '''(experimental) Keycloak container image to use.

            :stability: experimental
            '''
            result = self._values.get("image")
            assert result is not None, "Required property 'image' is missing"
            return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ContainerImage, result)

        @builtins.property
        def version(self) -> "KeycloakService.EngineVersion":
            '''(experimental) Keycloak version.

            :stability: experimental
            '''
            result = self._values.get("version")
            assert result is not None, "Required property 'version' is missing"
            return typing.cast("KeycloakService.EngineVersion", result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "KeycloakProps(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.ManagementConfiguration",
        jsii_struct_bases=[],
        name_mapping={
            "port": "port",
            "health": "health",
            "metrics": "metrics",
            "path": "path",
        },
    )
    class ManagementConfiguration:
        def __init__(
            self,
            *,
            port: jsii.Number,
            health: typing.Optional[builtins.bool] = None,
            metrics: typing.Optional[builtins.bool] = None,
            path: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param port: (experimental) Port to serve the management web traffic on.
            :param health: (experimental) Whether the health management API is enabled. Default: false
            :param metrics: (experimental) Whether the metrics management API is enabled. Default: false
            :param path: (experimental) Optional alternative relative path for serving content specifically for management. Default: /

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__d5c35da532548a9554669dc618e3ea8f4130dcbb9a3b45d7c95fb6dba10068a7)
                check_type(argname="argument port", value=port, expected_type=type_hints["port"])
                check_type(argname="argument health", value=health, expected_type=type_hints["health"])
                check_type(argname="argument metrics", value=metrics, expected_type=type_hints["metrics"])
                check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "port": port,
            }
            if health is not None:
                self._values["health"] = health
            if metrics is not None:
                self._values["metrics"] = metrics
            if path is not None:
                self._values["path"] = path

        @builtins.property
        def port(self) -> jsii.Number:
            '''(experimental) Port to serve the management web traffic on.

            :stability: experimental

            Example::

                9006
            '''
            result = self._values.get("port")
            assert result is not None, "Required property 'port' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def health(self) -> typing.Optional[builtins.bool]:
            '''(experimental) Whether the health management API is enabled.

            :default: false

            :stability: experimental
            '''
            result = self._values.get("health")
            return typing.cast(typing.Optional[builtins.bool], result)

        @builtins.property
        def metrics(self) -> typing.Optional[builtins.bool]:
            '''(experimental) Whether the metrics management API is enabled.

            :default: false

            :stability: experimental
            '''
            result = self._values.get("metrics")
            return typing.cast(typing.Optional[builtins.bool], result)

        @builtins.property
        def path(self) -> typing.Optional[builtins.str]:
            '''(experimental) Optional alternative relative path for serving content specifically for management.

            :default: /

            :stability: experimental
            '''
            result = self._values.get("path")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ManagementConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.RemovalPolicies",
        jsii_struct_bases=[],
        name_mapping={"data": "data", "logs": "logs"},
    )
    class RemovalPolicies:
        def __init__(
            self,
            *,
            data: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
            logs: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        ) -> None:
            '''(experimental) Policies to lifecycle various components of the pattern during stack actions.

            :param data: (experimental) How to deal with data-related elements. Default: RemovalPolicy.RETAIN
            :param logs: (experimental) How to deal with log-related elements. Default: RemovalPolicy.RETAIN

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__dc84adb2076c00ad72767f20c476598da6ab7b17b29cafd205af9d297025e960)
                check_type(argname="argument data", value=data, expected_type=type_hints["data"])
                check_type(argname="argument logs", value=logs, expected_type=type_hints["logs"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if data is not None:
                self._values["data"] = data
            if logs is not None:
                self._values["logs"] = logs

        @builtins.property
        def data(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
            '''(experimental) How to deal with data-related elements.

            :default: RemovalPolicy.RETAIN

            :stability: experimental
            '''
            result = self._values.get("data")
            return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

        @builtins.property
        def logs(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
            '''(experimental) How to deal with log-related elements.

            :default: RemovalPolicy.RETAIN

            :stability: experimental
            '''
            result = self._values.get("logs")
            return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RemovalPolicies(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.ServerlessDatabaseConfiguration",
        jsii_struct_bases=[],
        name_mapping={
            "backup": "backup",
            "log_retention_duration": "logRetentionDuration",
            "scaling": "scaling",
            "serverless": "serverless",
            "version_override": "versionOverride",
        },
    )
    class ServerlessDatabaseConfiguration:
        def __init__(
            self,
            *,
            backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
            log_retention_duration: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
            scaling: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.CfnDBCluster.ServerlessV2ScalingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
            serverless: typing.Optional[builtins.bool] = None,
            version_override: typing.Optional[_aws_cdk_aws_rds_ceddda9d.AuroraPostgresEngineVersion] = None,
        ) -> None:
            '''(experimental) Configuration options for a serverless database model.

            :param backup: (experimental) Backup lifecycle plan for the database. If not specified, CDK defaults are used
            :param log_retention_duration: (experimental) How long to retain logs for the database and supporting infrastructure. Default: RetentionDays.ONE_WEEK
            :param scaling: (experimental) How to scale the database. If not specified, CDK defaults are used
            :param serverless: (experimental) Whether a ServerlessV2 Aurora database should be deployed or not. Default: true
            :param version_override: (experimental) Alternate database engine version to use. Default: AuroraPostgresEngineVersion.VER_17_5

            :stability: experimental
            '''
            if isinstance(backup, dict):
                backup = _aws_cdk_aws_rds_ceddda9d.BackupProps(**backup)
            if isinstance(scaling, dict):
                scaling = _aws_cdk_aws_rds_ceddda9d.CfnDBCluster.ServerlessV2ScalingConfigurationProperty(**scaling)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__e11100757d96e59796c25ab3dac574f80d92763dd32b95b9c73462c7bb0c13ee)
                check_type(argname="argument backup", value=backup, expected_type=type_hints["backup"])
                check_type(argname="argument log_retention_duration", value=log_retention_duration, expected_type=type_hints["log_retention_duration"])
                check_type(argname="argument scaling", value=scaling, expected_type=type_hints["scaling"])
                check_type(argname="argument serverless", value=serverless, expected_type=type_hints["serverless"])
                check_type(argname="argument version_override", value=version_override, expected_type=type_hints["version_override"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if backup is not None:
                self._values["backup"] = backup
            if log_retention_duration is not None:
                self._values["log_retention_duration"] = log_retention_duration
            if scaling is not None:
                self._values["scaling"] = scaling
            if serverless is not None:
                self._values["serverless"] = serverless
            if version_override is not None:
                self._values["version_override"] = version_override

        @builtins.property
        def backup(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps]:
            '''(experimental) Backup lifecycle plan for the database.

            If not specified, CDK defaults are used

            :see: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseCluster.html#backup
            :stability: experimental
            '''
            result = self._values.get("backup")
            return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps], result)

        @builtins.property
        def log_retention_duration(
            self,
        ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
            '''(experimental) How long to retain logs for the database and supporting infrastructure.

            :default: RetentionDays.ONE_WEEK

            :stability: experimental
            '''
            result = self._values.get("log_retention_duration")
            return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

        @builtins.property
        def scaling(
            self,
        ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.CfnDBCluster.ServerlessV2ScalingConfigurationProperty]:
            '''(experimental) How to scale the database.

            If not specified, CDK defaults are used

            :see: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseClusterProps.html#serverlessv2mincapacity
            :stability: experimental
            '''
            result = self._values.get("scaling")
            return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.CfnDBCluster.ServerlessV2ScalingConfigurationProperty], result)

        @builtins.property
        def serverless(self) -> typing.Optional[builtins.bool]:
            '''(experimental) Whether a ServerlessV2 Aurora database should be deployed or not.

            :default: true

            :stability: experimental
            '''
            result = self._values.get("serverless")
            return typing.cast(typing.Optional[builtins.bool], result)

        @builtins.property
        def version_override(
            self,
        ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.AuroraPostgresEngineVersion]:
            '''(experimental) Alternate database engine version to use.

            :default: AuroraPostgresEngineVersion.VER_17_5

            :stability: experimental
            '''
            result = self._values.get("version_override")
            return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.AuroraPostgresEngineVersion], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ServerlessDatabaseConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.TaskSizingConfiguration",
        jsii_struct_bases=[],
        name_mapping={"cpu": "cpu", "memory_mb": "memoryMb"},
    )
    class TaskSizingConfiguration:
        def __init__(
            self,
            *,
            cpu: typing.Optional[jsii.Number] = None,
            memory_mb: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''(experimental) Configuration options for scaling the tasks.

            :param cpu: (experimental) vCPU allocation for each task. Values match the permitted values for ``FargateTaskDefinitionProps.cpu`` By default 1 vCPU (1024) is allocated Default: 1024
            :param memory_mb: (experimental) Memory allocation in MiB for each task. Values match the permitted values for ``FargateTaskDefinitionProps.memoryLimitMiB`` By default 2048 MiB (2GB) is allocated Default: 2048

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__377b43dca1eacee119e88fb1d2edb0e2f47bebaab3cbbf639b3162885f422b53)
                check_type(argname="argument cpu", value=cpu, expected_type=type_hints["cpu"])
                check_type(argname="argument memory_mb", value=memory_mb, expected_type=type_hints["memory_mb"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if cpu is not None:
                self._values["cpu"] = cpu
            if memory_mb is not None:
                self._values["memory_mb"] = memory_mb

        @builtins.property
        def cpu(self) -> typing.Optional[jsii.Number]:
            '''(experimental) vCPU allocation for each task.

            Values match the permitted values for ``FargateTaskDefinitionProps.cpu``

            By default 1 vCPU (1024) is allocated

            :default: 1024

            :see: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.FargateTaskDefinition.html#cpu
            :stability: experimental
            '''
            result = self._values.get("cpu")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def memory_mb(self) -> typing.Optional[jsii.Number]:
            '''(experimental) Memory allocation in MiB for each task.

            Values match the permitted values for ``FargateTaskDefinitionProps.memoryLimitMiB``

            By default 2048 MiB (2GB) is allocated

            :default: 2048

            :see: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.FargateTaskDefinition.html#memorylimitmib
            :stability: experimental
            '''
            result = self._values.get("memory_mb")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TaskSizingConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakService.TraditionalDatabaseConfiguration",
        jsii_struct_bases=[],
        name_mapping={
            "backup": "backup",
            "log_retention_duration": "logRetentionDuration",
            "serverless": "serverless",
            "version_override": "versionOverride",
        },
    )
    class TraditionalDatabaseConfiguration:
        def __init__(
            self,
            *,
            backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
            log_retention_duration: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
            serverless: typing.Optional[builtins.bool] = None,
            version_override: typing.Optional[_aws_cdk_aws_rds_ceddda9d.AuroraPostgresEngineVersion] = None,
        ) -> None:
            '''(experimental) Configuration options for a non-serverless database model.

            :param backup: (experimental) Backup lifecycle plan for the database. If not specified, CDK defaults are used
            :param log_retention_duration: (experimental) How long to retain logs for the database and supporting infrastructure. Default: RetentionDays.ONE_WEEK
            :param serverless: (experimental) Whether a ServerlessV2 Aurora database should be deployed or not. Default: true
            :param version_override: (experimental) Alternate database engine version to use. Default: AuroraPostgresEngineVersion.VER_17_5

            :stability: experimental
            '''
            if isinstance(backup, dict):
                backup = _aws_cdk_aws_rds_ceddda9d.BackupProps(**backup)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__f4a6450b4d71970170af9c2600865a292b9af867ff021dbc0b910d3ea6dace85)
                check_type(argname="argument backup", value=backup, expected_type=type_hints["backup"])
                check_type(argname="argument log_retention_duration", value=log_retention_duration, expected_type=type_hints["log_retention_duration"])
                check_type(argname="argument serverless", value=serverless, expected_type=type_hints["serverless"])
                check_type(argname="argument version_override", value=version_override, expected_type=type_hints["version_override"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if backup is not None:
                self._values["backup"] = backup
            if log_retention_duration is not None:
                self._values["log_retention_duration"] = log_retention_duration
            if serverless is not None:
                self._values["serverless"] = serverless
            if version_override is not None:
                self._values["version_override"] = version_override

        @builtins.property
        def backup(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps]:
            '''(experimental) Backup lifecycle plan for the database.

            If not specified, CDK defaults are used

            :see: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds.DatabaseCluster.html#backup
            :stability: experimental
            '''
            result = self._values.get("backup")
            return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps], result)

        @builtins.property
        def log_retention_duration(
            self,
        ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
            '''(experimental) How long to retain logs for the database and supporting infrastructure.

            :default: RetentionDays.ONE_WEEK

            :stability: experimental
            '''
            result = self._values.get("log_retention_duration")
            return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

        @builtins.property
        def serverless(self) -> typing.Optional[builtins.bool]:
            '''(experimental) Whether a ServerlessV2 Aurora database should be deployed or not.

            :default: true

            :stability: experimental
            '''
            result = self._values.get("serverless")
            return typing.cast(typing.Optional[builtins.bool], result)

        @builtins.property
        def version_override(
            self,
        ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.AuroraPostgresEngineVersion]:
            '''(experimental) Alternate database engine version to use.

            :default: AuroraPostgresEngineVersion.VER_17_5

            :stability: experimental
            '''
            result = self._values.get("version_override")
            return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.AuroraPostgresEngineVersion], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TraditionalDatabaseConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.KeycloakServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "keycloak": "keycloak",
        "vpc": "vpc",
        "encryption": "encryption",
        "log_retention_duration": "logRetentionDuration",
        "overrides": "overrides",
        "removal_policies": "removalPolicies",
    },
)
class KeycloakServiceProps:
    def __init__(
        self,
        *,
        keycloak: typing.Union[KeycloakService.KeycloakProps, typing.Dict[builtins.str, typing.Any]],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        log_retention_duration: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        overrides: typing.Optional[typing.Union[KeycloakService.InfrastructureConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policies: typing.Optional[typing.Union[KeycloakService.RemovalPolicies, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for the KeycloakService construct.

        :param keycloak: (experimental) Options related to Keycloak.
        :param vpc: (experimental) Network where Keycloak should be deployed.
        :param encryption: (experimental) Key for encrypting resource data. If not specified, a new key will be created
        :param log_retention_duration: (experimental) How long to retain logs for all components. If not specified, logs will be retained for one week
        :param overrides: (experimental) Overrides for prescribed defaults for the infrastructure.
        :param removal_policies: (experimental) Policies to lifecycle various components of the pattern during stack actions. If not specified, resources will be retained

        :stability: experimental
        '''
        if isinstance(keycloak, dict):
            keycloak = KeycloakService.KeycloakProps(**keycloak)
        if isinstance(overrides, dict):
            overrides = KeycloakService.InfrastructureConfiguration(**overrides)
        if isinstance(removal_policies, dict):
            removal_policies = KeycloakService.RemovalPolicies(**removal_policies)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2db6c3e148a219b7767d278297a95b36e6aa7a25f1b600e312b802f23f1ac9dc)
            check_type(argname="argument keycloak", value=keycloak, expected_type=type_hints["keycloak"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument log_retention_duration", value=log_retention_duration, expected_type=type_hints["log_retention_duration"])
            check_type(argname="argument overrides", value=overrides, expected_type=type_hints["overrides"])
            check_type(argname="argument removal_policies", value=removal_policies, expected_type=type_hints["removal_policies"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "keycloak": keycloak,
            "vpc": vpc,
        }
        if encryption is not None:
            self._values["encryption"] = encryption
        if log_retention_duration is not None:
            self._values["log_retention_duration"] = log_retention_duration
        if overrides is not None:
            self._values["overrides"] = overrides
        if removal_policies is not None:
            self._values["removal_policies"] = removal_policies

    @builtins.property
    def keycloak(self) -> KeycloakService.KeycloakProps:
        '''(experimental) Options related to Keycloak.

        :stability: experimental
        '''
        result = self._values.get("keycloak")
        assert result is not None, "Required property 'keycloak' is missing"
        return typing.cast(KeycloakService.KeycloakProps, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) Network where Keycloak should be deployed.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Key for encrypting resource data.

        If not specified, a new key will be created

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def log_retention_duration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''(experimental) How long to retain logs for all components.

        If not specified, logs will be retained for one week

        :stability: experimental
        '''
        result = self._values.get("log_retention_duration")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def overrides(self) -> typing.Optional[KeycloakService.InfrastructureConfiguration]:
        '''(experimental) Overrides for prescribed defaults for the infrastructure.

        :stability: experimental
        '''
        result = self._values.get("overrides")
        return typing.cast(typing.Optional[KeycloakService.InfrastructureConfiguration], result)

    @builtins.property
    def removal_policies(self) -> typing.Optional[KeycloakService.RemovalPolicies]:
        '''(experimental) Policies to lifecycle various components of the pattern during stack actions.

        If not specified, resources will be retained

        :stability: experimental
        '''
        result = self._values.get("removal_policies")
        return typing.cast(typing.Optional[KeycloakService.RemovalPolicies], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KeycloakServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayStaticHosting",
    "ApiGatewayStaticHostingProps",
    "Ec2LinuxImagePipeline",
    "Ec2LinuxImagePipelineProps",
    "KeycloakService",
    "KeycloakServiceProps",
]

publication.publish()

def _typecheckingstub__926e3ab1cdccdb34f4dc75a68890781e04a583c1ec8481b471267ea1ecbb3c22(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    asset: typing.Union[ApiGatewayStaticHosting.Asset, typing.Dict[builtins.str, typing.Any]],
    domain: typing.Union[typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[ApiGatewayStaticHosting.DefaultEndpointConfiguration, typing.Dict[builtins.str, typing.Any]]],
    access_logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    access_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    api_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    endpoint: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    retain_store_on_deletion: typing.Optional[builtins.bool] = None,
    version_tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95377bd339103860abda9142b547350593c2c75dc36900d1cafdbd3ed1452918(
    *,
    id: builtins.str,
    path: typing.Union[builtins.str, typing.Sequence[builtins.str]],
    spa_index_page_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb7dd65e823631a881c3757f3933e65e12d0ec00138d9e332d7bffc3beddf9ee(
    *,
    options: typing.Union[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af579bdb0d2e5a9bf7625d102861181c02edc99e90f1bea8aad195fde82acc1f(
    *,
    base_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c61a977a949d583f93d83ff5cdd17e5856bd473ed360fd24f8219d952c9a0b61(
    *,
    distribution: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
    proxy: _aws_cdk_aws_lambda_ceddda9d.Function,
    store: _aws_cdk_aws_s3_ceddda9d.Bucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4baf4c2294bf49627829b500b5815750efb5085b8be745e95cfca95c61678fd6(
    *,
    asset: typing.Union[ApiGatewayStaticHosting.Asset, typing.Dict[builtins.str, typing.Any]],
    domain: typing.Union[typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[ApiGatewayStaticHosting.DefaultEndpointConfiguration, typing.Dict[builtins.str, typing.Any]]],
    access_logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    access_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    api_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    endpoint: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    retain_store_on_deletion: typing.Optional[builtins.bool] = None,
    version_tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfe75b8964707df740912e083b8358a4e940f27f7259ab820504b6c2ada0e612(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    extra_components: typing.Optional[typing.Sequence[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
    extra_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    features: typing.Optional[typing.Sequence[Ec2LinuxImagePipeline.Feature]] = None,
    operating_system: typing.Optional[Ec2LinuxImagePipeline.OperatingSystem] = None,
    root_volume_size: typing.Optional[jsii.Number] = None,
    version: builtins.str,
    build_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__480b8d9ad288b00a9019dff6ab448fa0084409e75666e22ebc710de08d511ef1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50c054b2b518ad1fdc972c31ac61f4ccead58620ac1a7b23a125009d747bc370(
    value: _aws_cdk_aws_sns_ceddda9d.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e396117a6c4ae570f398094ede114baa7576df8e02406727ef327dda84877bda(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d272e504a6fabc4b04d50467e7c5293e2777ed064ddb4c6626d553e16c42dd65(
    *,
    version: builtins.str,
    build_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    extra_components: typing.Optional[typing.Sequence[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
    extra_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    features: typing.Optional[typing.Sequence[Ec2LinuxImagePipeline.Feature]] = None,
    operating_system: typing.Optional[Ec2LinuxImagePipeline.OperatingSystem] = None,
    root_volume_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fab7697cc8698d9567cdcbe737e05dbb050c2e9c228d45bc10c1fcd17de5c3f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    keycloak: typing.Union[KeycloakService.KeycloakProps, typing.Dict[builtins.str, typing.Any]],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    log_retention_duration: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    overrides: typing.Optional[typing.Union[KeycloakService.InfrastructureConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policies: typing.Optional[typing.Union[KeycloakService.RemovalPolicies, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f80c0a4fd9c4c8dd41be39585e21c306ed5d241b22443fa1feaa4985b8b2e868(
    *,
    hostnames: typing.Union[KeycloakService.HostnameConfiguration, typing.Dict[builtins.str, typing.Any]],
    admin_user: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    logging_level: typing.Optional[builtins.str] = None,
    management: typing.Optional[typing.Union[KeycloakService.ManagementConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    path: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9b6b8d8fbc3e6c32a2b26155533cdf9ef74e2edad588884e68cdfce6d2249eb(
    *,
    scaling: typing.Optional[typing.Union[KeycloakService.ClusterScalingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    sizing: typing.Optional[typing.Union[KeycloakService.TaskSizingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__231f1c6f7a0cff8811547d8037df0c5d9d85ca9643fc82af2edf832e6cd51f93(
    *,
    enabled: builtins.bool,
    threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1f26f24157aca6309c29c124d917259a7186571773c2d8d19f0542214ea4a3b(
    *,
    maximum: jsii.Number,
    minimum: jsii.Number,
    request_count_scaling: typing.Optional[typing.Union[KeycloakService.ClusterRequestCountScalingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b600bad4a56f0e04b8a1a8d27f269450defbf1c49c6c51c507bdbdc0a24f382d(
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__917661cfb6f2356a5fa1118db4799671f72af53fe4738975f673d0b5cbe0b28a(
    keycloak: KeycloakService.EngineVersion,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba771327ecd99e8860b7d2f861530bb282eacdc2c8a73490259c1f69e3976944(
    *,
    dns_zone_name: typing.Optional[builtins.str] = None,
    internet_facing: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11844e1d564f7809621812d17ba3175a9188b525ff28317671bf40e446c0bc51(
    *,
    default: builtins.str,
    admin: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33df0bf714e8ea28a78fdc53f282c21b6d6977d2f001bdb5a7191602f940fa08(
    *,
    cluster: typing.Optional[typing.Union[KeycloakService.ClusterConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    database: typing.Optional[typing.Union[typing.Union[KeycloakService.ServerlessDatabaseConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[KeycloakService.TraditionalDatabaseConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    fabric: typing.Optional[typing.Union[KeycloakService.FabricConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f17470288c514b03a9ef92c6abea1d24ebe334309c15f753b07daa18e29ee9cc(
    *,
    configuration: typing.Union[KeycloakService.ApplicationConfiguration, typing.Dict[builtins.str, typing.Any]],
    image: _aws_cdk_aws_ecs_ceddda9d.ContainerImage,
    version: KeycloakService.EngineVersion,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5c35da532548a9554669dc618e3ea8f4130dcbb9a3b45d7c95fb6dba10068a7(
    *,
    port: jsii.Number,
    health: typing.Optional[builtins.bool] = None,
    metrics: typing.Optional[builtins.bool] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc84adb2076c00ad72767f20c476598da6ab7b17b29cafd205af9d297025e960(
    *,
    data: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    logs: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e11100757d96e59796c25ab3dac574f80d92763dd32b95b9c73462c7bb0c13ee(
    *,
    backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    log_retention_duration: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    scaling: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.CfnDBCluster.ServerlessV2ScalingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    serverless: typing.Optional[builtins.bool] = None,
    version_override: typing.Optional[_aws_cdk_aws_rds_ceddda9d.AuroraPostgresEngineVersion] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__377b43dca1eacee119e88fb1d2edb0e2f47bebaab3cbbf639b3162885f422b53(
    *,
    cpu: typing.Optional[jsii.Number] = None,
    memory_mb: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4a6450b4d71970170af9c2600865a292b9af867ff021dbc0b910d3ea6dace85(
    *,
    backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    log_retention_duration: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    serverless: typing.Optional[builtins.bool] = None,
    version_override: typing.Optional[_aws_cdk_aws_rds_ceddda9d.AuroraPostgresEngineVersion] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2db6c3e148a219b7767d278297a95b36e6aa7a25f1b600e312b802f23f1ac9dc(
    *,
    keycloak: typing.Union[KeycloakService.KeycloakProps, typing.Dict[builtins.str, typing.Any]],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    log_retention_duration: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    overrides: typing.Optional[typing.Union[KeycloakService.InfrastructureConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policies: typing.Optional[typing.Union[KeycloakService.RemovalPolicies, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
