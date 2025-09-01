r'''
# datadog-integrations-awsaccount

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `Datadog::Integrations::AWSAccount` v1.0.0.

## Description

Datadog AWS Account Integration 1.0.0

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name Datadog::Integrations::AWSAccount \
  --publisher-id 7171b96e5d207b947eb72ca9ce05247c246de623 \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/7171b96e5d207b947eb72ca9ce05247c246de623/Datadog-Integrations-AWSAccount \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `Datadog::Integrations::AWSAccount`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fdatadog-integrations-awsaccount+v1.0.0).
* Issues related to `Datadog::Integrations::AWSAccount` should be reported to the [publisher](undefined).

## License

Distributed under the Apache-2.0 License.
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
import constructs as _constructs_77d1e7e8


class CfnAwsAccount(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccount",
):
    '''A CloudFormation ``Datadog::Integrations::AWSAccount``.

    :cloudformationResource: Datadog::Integrations::AWSAccount
    :link: http://unknown-url
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        auth_config: typing.Union["CfnAwsAccountPropsAuthConfig", typing.Dict[builtins.str, typing.Any]],
        aws_partition: "CfnAwsAccountPropsAwsPartition",
        account_id: typing.Optional[builtins.str] = None,
        account_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        aws_regions: typing.Optional[typing.Union["CfnAwsAccountPropsAwsRegions", typing.Dict[builtins.str, typing.Any]]] = None,
        external_id_secret_name: typing.Optional[builtins.str] = None,
        logs_config: typing.Optional[typing.Union["CfnAwsAccountPropsLogsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        metrics_config: typing.Optional[typing.Union["CfnAwsAccountPropsMetricsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        resources_config: typing.Optional[typing.Union["CfnAwsAccountPropsResourcesConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        traces_config: typing.Optional[typing.Union["CfnAwsAccountPropsTracesConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Create a new ``Datadog::Integrations::AWSAccount``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param auth_config: The configuration for the AWS role delegation.
        :param aws_partition: The AWS partition to use. This should be set to 'aws' for commercial accounts, 'aws-us-gov' for GovCloud accounts, and 'aws-cn' for China accounts.
        :param account_id: Your AWS Account ID without dashes.
        :param account_tags: Array of tags (in the form key:value) to add to all hosts and metrics reporting through this integration.
        :param aws_regions: The configuration for which regions to collect data from.
        :param external_id_secret_name: The name of the AWS SecretsManager secret created in your account to hold this integration's ``external_id``. Defaults to ``DatadogIntegrationExternalID``. Cannot be referenced from created resource. Default: DatadogIntegrationExternalID`. Cannot be referenced from created resource.
        :param logs_config: The configuration for ingesting AWS Logs into Datadog.
        :param metrics_config: The configuration for ingesting AWS Metrics into Datadog.
        :param resources_config: The configuration for ingesting AWS Resources into Datadog.
        :param traces_config: The configuration for ingesting AWS Traces into Datadog.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eedd984825c69b36d4c1533da5427e2cb123b3a6e9dd2d782e5444bd23659cbf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnAwsAccountProps(
            auth_config=auth_config,
            aws_partition=aws_partition,
            account_id=account_id,
            account_tags=account_tags,
            aws_regions=aws_regions,
            external_id_secret_name=external_id_secret_name,
            logs_config=logs_config,
            metrics_config=metrics_config,
            resources_config=resources_config,
            traces_config=traces_config,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''Attribute ``Datadog::Integrations::AWSAccount.Id``.

        :link: http://unknown-url
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnAwsAccountProps":
        '''Resource props.'''
        return typing.cast("CfnAwsAccountProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountProps",
    jsii_struct_bases=[],
    name_mapping={
        "auth_config": "authConfig",
        "aws_partition": "awsPartition",
        "account_id": "accountId",
        "account_tags": "accountTags",
        "aws_regions": "awsRegions",
        "external_id_secret_name": "externalIdSecretName",
        "logs_config": "logsConfig",
        "metrics_config": "metricsConfig",
        "resources_config": "resourcesConfig",
        "traces_config": "tracesConfig",
    },
)
class CfnAwsAccountProps:
    def __init__(
        self,
        *,
        auth_config: typing.Union["CfnAwsAccountPropsAuthConfig", typing.Dict[builtins.str, typing.Any]],
        aws_partition: "CfnAwsAccountPropsAwsPartition",
        account_id: typing.Optional[builtins.str] = None,
        account_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        aws_regions: typing.Optional[typing.Union["CfnAwsAccountPropsAwsRegions", typing.Dict[builtins.str, typing.Any]]] = None,
        external_id_secret_name: typing.Optional[builtins.str] = None,
        logs_config: typing.Optional[typing.Union["CfnAwsAccountPropsLogsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        metrics_config: typing.Optional[typing.Union["CfnAwsAccountPropsMetricsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        resources_config: typing.Optional[typing.Union["CfnAwsAccountPropsResourcesConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        traces_config: typing.Optional[typing.Union["CfnAwsAccountPropsTracesConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Datadog AWS Account Integration 1.0.0.

        :param auth_config: The configuration for the AWS role delegation.
        :param aws_partition: The AWS partition to use. This should be set to 'aws' for commercial accounts, 'aws-us-gov' for GovCloud accounts, and 'aws-cn' for China accounts.
        :param account_id: Your AWS Account ID without dashes.
        :param account_tags: Array of tags (in the form key:value) to add to all hosts and metrics reporting through this integration.
        :param aws_regions: The configuration for which regions to collect data from.
        :param external_id_secret_name: The name of the AWS SecretsManager secret created in your account to hold this integration's ``external_id``. Defaults to ``DatadogIntegrationExternalID``. Cannot be referenced from created resource. Default: DatadogIntegrationExternalID`. Cannot be referenced from created resource.
        :param logs_config: The configuration for ingesting AWS Logs into Datadog.
        :param metrics_config: The configuration for ingesting AWS Metrics into Datadog.
        :param resources_config: The configuration for ingesting AWS Resources into Datadog.
        :param traces_config: The configuration for ingesting AWS Traces into Datadog.

        :schema: CfnAwsAccountProps
        '''
        if isinstance(auth_config, dict):
            auth_config = CfnAwsAccountPropsAuthConfig(**auth_config)
        if isinstance(aws_regions, dict):
            aws_regions = CfnAwsAccountPropsAwsRegions(**aws_regions)
        if isinstance(logs_config, dict):
            logs_config = CfnAwsAccountPropsLogsConfig(**logs_config)
        if isinstance(metrics_config, dict):
            metrics_config = CfnAwsAccountPropsMetricsConfig(**metrics_config)
        if isinstance(resources_config, dict):
            resources_config = CfnAwsAccountPropsResourcesConfig(**resources_config)
        if isinstance(traces_config, dict):
            traces_config = CfnAwsAccountPropsTracesConfig(**traces_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1257d217dabd28334fd6a473666fbf1dcdb5458a7c01c668347093026341385)
            check_type(argname="argument auth_config", value=auth_config, expected_type=type_hints["auth_config"])
            check_type(argname="argument aws_partition", value=aws_partition, expected_type=type_hints["aws_partition"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument account_tags", value=account_tags, expected_type=type_hints["account_tags"])
            check_type(argname="argument aws_regions", value=aws_regions, expected_type=type_hints["aws_regions"])
            check_type(argname="argument external_id_secret_name", value=external_id_secret_name, expected_type=type_hints["external_id_secret_name"])
            check_type(argname="argument logs_config", value=logs_config, expected_type=type_hints["logs_config"])
            check_type(argname="argument metrics_config", value=metrics_config, expected_type=type_hints["metrics_config"])
            check_type(argname="argument resources_config", value=resources_config, expected_type=type_hints["resources_config"])
            check_type(argname="argument traces_config", value=traces_config, expected_type=type_hints["traces_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_config": auth_config,
            "aws_partition": aws_partition,
        }
        if account_id is not None:
            self._values["account_id"] = account_id
        if account_tags is not None:
            self._values["account_tags"] = account_tags
        if aws_regions is not None:
            self._values["aws_regions"] = aws_regions
        if external_id_secret_name is not None:
            self._values["external_id_secret_name"] = external_id_secret_name
        if logs_config is not None:
            self._values["logs_config"] = logs_config
        if metrics_config is not None:
            self._values["metrics_config"] = metrics_config
        if resources_config is not None:
            self._values["resources_config"] = resources_config
        if traces_config is not None:
            self._values["traces_config"] = traces_config

    @builtins.property
    def auth_config(self) -> "CfnAwsAccountPropsAuthConfig":
        '''The configuration for the AWS role delegation.

        :schema: CfnAwsAccountProps#AuthConfig
        '''
        result = self._values.get("auth_config")
        assert result is not None, "Required property 'auth_config' is missing"
        return typing.cast("CfnAwsAccountPropsAuthConfig", result)

    @builtins.property
    def aws_partition(self) -> "CfnAwsAccountPropsAwsPartition":
        '''The AWS partition to use.

        This should be set to 'aws' for commercial accounts, 'aws-us-gov' for GovCloud accounts, and 'aws-cn' for China accounts.

        :schema: CfnAwsAccountProps#AWSPartition
        '''
        result = self._values.get("aws_partition")
        assert result is not None, "Required property 'aws_partition' is missing"
        return typing.cast("CfnAwsAccountPropsAwsPartition", result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Your AWS Account ID without dashes.

        :schema: CfnAwsAccountProps#AccountID
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def account_tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Array of tags (in the form key:value) to add to all hosts and metrics reporting through this integration.

        :schema: CfnAwsAccountProps#AccountTags
        '''
        result = self._values.get("account_tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def aws_regions(self) -> typing.Optional["CfnAwsAccountPropsAwsRegions"]:
        '''The configuration for which regions to collect data from.

        :schema: CfnAwsAccountProps#AWSRegions
        '''
        result = self._values.get("aws_regions")
        return typing.cast(typing.Optional["CfnAwsAccountPropsAwsRegions"], result)

    @builtins.property
    def external_id_secret_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS SecretsManager secret created in your account to hold this integration's ``external_id``.

        Defaults to ``DatadogIntegrationExternalID``. Cannot be referenced from created resource.

        :default: DatadogIntegrationExternalID`. Cannot be referenced from created resource.

        :schema: CfnAwsAccountProps#ExternalIDSecretName
        '''
        result = self._values.get("external_id_secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logs_config(self) -> typing.Optional["CfnAwsAccountPropsLogsConfig"]:
        '''The configuration for ingesting AWS Logs into Datadog.

        :schema: CfnAwsAccountProps#LogsConfig
        '''
        result = self._values.get("logs_config")
        return typing.cast(typing.Optional["CfnAwsAccountPropsLogsConfig"], result)

    @builtins.property
    def metrics_config(self) -> typing.Optional["CfnAwsAccountPropsMetricsConfig"]:
        '''The configuration for ingesting AWS Metrics into Datadog.

        :schema: CfnAwsAccountProps#MetricsConfig
        '''
        result = self._values.get("metrics_config")
        return typing.cast(typing.Optional["CfnAwsAccountPropsMetricsConfig"], result)

    @builtins.property
    def resources_config(self) -> typing.Optional["CfnAwsAccountPropsResourcesConfig"]:
        '''The configuration for ingesting AWS Resources into Datadog.

        :schema: CfnAwsAccountProps#ResourcesConfig
        '''
        result = self._values.get("resources_config")
        return typing.cast(typing.Optional["CfnAwsAccountPropsResourcesConfig"], result)

    @builtins.property
    def traces_config(self) -> typing.Optional["CfnAwsAccountPropsTracesConfig"]:
        '''The configuration for ingesting AWS Traces into Datadog.

        :schema: CfnAwsAccountProps#TracesConfig
        '''
        result = self._values.get("traces_config")
        return typing.cast(typing.Optional["CfnAwsAccountPropsTracesConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsAuthConfig",
    jsii_struct_bases=[],
    name_mapping={"role_name": "roleName"},
)
class CfnAwsAccountPropsAuthConfig:
    def __init__(self, *, role_name: builtins.str) -> None:
        '''The configuration for the AWS role delegation.

        :param role_name: Your Datadog role delegation name.

        :schema: CfnAwsAccountPropsAuthConfig
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00bca8b180a23726f8f5105f96051004cbea09ccf99665f89d865bed9f32b785)
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_name": role_name,
        }

    @builtins.property
    def role_name(self) -> builtins.str:
        '''Your Datadog role delegation name.

        :schema: CfnAwsAccountPropsAuthConfig#RoleName
        '''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsAuthConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsAwsPartition"
)
class CfnAwsAccountPropsAwsPartition(enum.Enum):
    '''The AWS partition to use.

    This should be set to 'aws' for commercial accounts, 'aws-us-gov' for GovCloud accounts, and 'aws-cn' for China accounts.

    :schema: CfnAwsAccountPropsAwsPartition
    '''

    AWS = "AWS"
    '''aws.'''
    AWS_HYPHEN_US_HYPHEN_GOV = "AWS_HYPHEN_US_HYPHEN_GOV"
    '''aws-us-gov.'''
    AWS_HYPHEN_CN = "AWS_HYPHEN_CN"
    '''aws-cn.'''


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsAwsRegions",
    jsii_struct_bases=[],
    name_mapping={"include_all": "includeAll", "include_only": "includeOnly"},
)
class CfnAwsAccountPropsAwsRegions:
    def __init__(
        self,
        *,
        include_all: typing.Optional[builtins.bool] = None,
        include_only: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''The configuration for which regions to collect data from.

        :param include_all: Collect data for all AWS regions.
        :param include_only: Array of AWS regions to include from metrics collection.

        :schema: CfnAwsAccountPropsAwsRegions
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__610a9251870b617546874a092da09a24eb418c6d6305e3dc2e953e86730abd7f)
            check_type(argname="argument include_all", value=include_all, expected_type=type_hints["include_all"])
            check_type(argname="argument include_only", value=include_only, expected_type=type_hints["include_only"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if include_all is not None:
            self._values["include_all"] = include_all
        if include_only is not None:
            self._values["include_only"] = include_only

    @builtins.property
    def include_all(self) -> typing.Optional[builtins.bool]:
        '''Collect data for all AWS regions.

        :schema: CfnAwsAccountPropsAwsRegions#IncludeAll
        '''
        result = self._values.get("include_all")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def include_only(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Array of AWS regions to include from metrics collection.

        :schema: CfnAwsAccountPropsAwsRegions#IncludeOnly
        '''
        result = self._values.get("include_only")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsAwsRegions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsLogsConfig",
    jsii_struct_bases=[],
    name_mapping={"lambda_forwarder": "lambdaForwarder"},
)
class CfnAwsAccountPropsLogsConfig:
    def __init__(
        self,
        *,
        lambda_forwarder: typing.Optional[typing.Union["CfnAwsAccountPropsLogsConfigLambdaForwarder", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''The configuration for ingesting AWS Logs into Datadog.

        :param lambda_forwarder: The configuration for Lambda Log Forwarders.

        :schema: CfnAwsAccountPropsLogsConfig
        '''
        if isinstance(lambda_forwarder, dict):
            lambda_forwarder = CfnAwsAccountPropsLogsConfigLambdaForwarder(**lambda_forwarder)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a96310366ae7d5675ca20c8d07817c280dacdadf6154f4b10f366db6a58af573)
            check_type(argname="argument lambda_forwarder", value=lambda_forwarder, expected_type=type_hints["lambda_forwarder"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if lambda_forwarder is not None:
            self._values["lambda_forwarder"] = lambda_forwarder

    @builtins.property
    def lambda_forwarder(
        self,
    ) -> typing.Optional["CfnAwsAccountPropsLogsConfigLambdaForwarder"]:
        '''The configuration for Lambda Log Forwarders.

        :schema: CfnAwsAccountPropsLogsConfig#LambdaForwarder
        '''
        result = self._values.get("lambda_forwarder")
        return typing.cast(typing.Optional["CfnAwsAccountPropsLogsConfigLambdaForwarder"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsLogsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsLogsConfigLambdaForwarder",
    jsii_struct_bases=[],
    name_mapping={"lambdas": "lambdas", "sources": "sources"},
)
class CfnAwsAccountPropsLogsConfigLambdaForwarder:
    def __init__(
        self,
        *,
        lambdas: typing.Optional[typing.Sequence[builtins.str]] = None,
        sources: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''The configuration for Lambda Log Forwarders.

        :param lambdas: List of Datadog Lambda Log Forwarder ARNs.
        :param sources: List of AWS services that will send logs to the Datadog Lambda Log Forwarder.

        :schema: CfnAwsAccountPropsLogsConfigLambdaForwarder
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__346546c03a01cf4ec35c2040998cd06e2df956fccf29d95d1a9d6c161acb8bd2)
            check_type(argname="argument lambdas", value=lambdas, expected_type=type_hints["lambdas"])
            check_type(argname="argument sources", value=sources, expected_type=type_hints["sources"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if lambdas is not None:
            self._values["lambdas"] = lambdas
        if sources is not None:
            self._values["sources"] = sources

    @builtins.property
    def lambdas(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Datadog Lambda Log Forwarder ARNs.

        :schema: CfnAwsAccountPropsLogsConfigLambdaForwarder#Lambdas
        '''
        result = self._values.get("lambdas")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of AWS services that will send logs to the Datadog Lambda Log Forwarder.

        :schema: CfnAwsAccountPropsLogsConfigLambdaForwarder#Sources
        '''
        result = self._values.get("sources")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsLogsConfigLambdaForwarder(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsMetricsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "automute_enabled": "automuteEnabled",
        "collect_cloudwatch_alarms": "collectCloudwatchAlarms",
        "collect_custom_metrics": "collectCustomMetrics",
        "enabled": "enabled",
        "namespace_filters": "namespaceFilters",
        "tag_filters": "tagFilters",
    },
)
class CfnAwsAccountPropsMetricsConfig:
    def __init__(
        self,
        *,
        automute_enabled: typing.Optional[builtins.bool] = None,
        collect_cloudwatch_alarms: typing.Optional[builtins.bool] = None,
        collect_custom_metrics: typing.Optional[builtins.bool] = None,
        enabled: typing.Optional[builtins.bool] = None,
        namespace_filters: typing.Optional[typing.Union["CfnAwsAccountPropsMetricsConfigNamespaceFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        tag_filters: typing.Optional[typing.Sequence[typing.Union["CfnAwsAccountPropsMetricsConfigTagFilters", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''The configuration for ingesting AWS Metrics into Datadog.

        :param automute_enabled: Enable EC2 automute for AWS metrics.
        :param collect_cloudwatch_alarms: Enable CloudWatch alarms collection.
        :param collect_custom_metrics: Enable custom metrics collection.
        :param enabled: Enable the infrastructure monitoring Datadog product for this AWS Account. This will enable collecting all AWS metrics in your account.
        :param namespace_filters: 
        :param tag_filters: The array of EC2 tags (in the form key:value) defines a filter that Datadog uses when collecting metrics from EC2.

        :schema: CfnAwsAccountPropsMetricsConfig
        '''
        if isinstance(namespace_filters, dict):
            namespace_filters = CfnAwsAccountPropsMetricsConfigNamespaceFilters(**namespace_filters)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b27b58555e56b0e37e678cd55f81f734c7852221c12827ac012e4e2bd4f09614)
            check_type(argname="argument automute_enabled", value=automute_enabled, expected_type=type_hints["automute_enabled"])
            check_type(argname="argument collect_cloudwatch_alarms", value=collect_cloudwatch_alarms, expected_type=type_hints["collect_cloudwatch_alarms"])
            check_type(argname="argument collect_custom_metrics", value=collect_custom_metrics, expected_type=type_hints["collect_custom_metrics"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument namespace_filters", value=namespace_filters, expected_type=type_hints["namespace_filters"])
            check_type(argname="argument tag_filters", value=tag_filters, expected_type=type_hints["tag_filters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if automute_enabled is not None:
            self._values["automute_enabled"] = automute_enabled
        if collect_cloudwatch_alarms is not None:
            self._values["collect_cloudwatch_alarms"] = collect_cloudwatch_alarms
        if collect_custom_metrics is not None:
            self._values["collect_custom_metrics"] = collect_custom_metrics
        if enabled is not None:
            self._values["enabled"] = enabled
        if namespace_filters is not None:
            self._values["namespace_filters"] = namespace_filters
        if tag_filters is not None:
            self._values["tag_filters"] = tag_filters

    @builtins.property
    def automute_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable EC2 automute for AWS metrics.

        :schema: CfnAwsAccountPropsMetricsConfig#AutomuteEnabled
        '''
        result = self._values.get("automute_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def collect_cloudwatch_alarms(self) -> typing.Optional[builtins.bool]:
        '''Enable CloudWatch alarms collection.

        :schema: CfnAwsAccountPropsMetricsConfig#CollectCloudwatchAlarms
        '''
        result = self._values.get("collect_cloudwatch_alarms")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def collect_custom_metrics(self) -> typing.Optional[builtins.bool]:
        '''Enable custom metrics collection.

        :schema: CfnAwsAccountPropsMetricsConfig#CollectCustomMetrics
        '''
        result = self._values.get("collect_custom_metrics")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable the infrastructure monitoring Datadog product for this AWS Account.

        This will enable collecting all AWS metrics in your account.

        :schema: CfnAwsAccountPropsMetricsConfig#Enabled
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def namespace_filters(
        self,
    ) -> typing.Optional["CfnAwsAccountPropsMetricsConfigNamespaceFilters"]:
        '''
        :schema: CfnAwsAccountPropsMetricsConfig#NamespaceFilters
        '''
        result = self._values.get("namespace_filters")
        return typing.cast(typing.Optional["CfnAwsAccountPropsMetricsConfigNamespaceFilters"], result)

    @builtins.property
    def tag_filters(
        self,
    ) -> typing.Optional[typing.List["CfnAwsAccountPropsMetricsConfigTagFilters"]]:
        '''The array of EC2 tags (in the form key:value) defines a filter that Datadog uses when collecting metrics from EC2.

        :schema: CfnAwsAccountPropsMetricsConfig#TagFilters
        '''
        result = self._values.get("tag_filters")
        return typing.cast(typing.Optional[typing.List["CfnAwsAccountPropsMetricsConfigTagFilters"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsMetricsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsMetricsConfigNamespaceFilters",
    jsii_struct_bases=[],
    name_mapping={"exclude_only": "excludeOnly", "include_only": "includeOnly"},
)
class CfnAwsAccountPropsMetricsConfigNamespaceFilters:
    def __init__(
        self,
        *,
        exclude_only: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_only: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude_only: Array of AWS namespaces to exclude from metrics collection. Only one of IncludeOnlyNamespaces or ExcludeNamespaces can be set.
        :param include_only: Array of AWS namespaces to include from metrics collection. Only one of IncludeOnlyNamespaces or ExcludeNamespaces can be set.

        :schema: CfnAwsAccountPropsMetricsConfigNamespaceFilters
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5ba132f2a1a4de9a3b5618c69d9bd7f10b5883f8e75ef0bc8e22f7eca9147f6)
            check_type(argname="argument exclude_only", value=exclude_only, expected_type=type_hints["exclude_only"])
            check_type(argname="argument include_only", value=include_only, expected_type=type_hints["include_only"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude_only is not None:
            self._values["exclude_only"] = exclude_only
        if include_only is not None:
            self._values["include_only"] = include_only

    @builtins.property
    def exclude_only(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Array of AWS namespaces to exclude from metrics collection.

        Only one of IncludeOnlyNamespaces or ExcludeNamespaces can be set.

        :schema: CfnAwsAccountPropsMetricsConfigNamespaceFilters#ExcludeOnly
        '''
        result = self._values.get("exclude_only")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_only(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Array of AWS namespaces to include from metrics collection.

        Only one of IncludeOnlyNamespaces or ExcludeNamespaces can be set.

        :schema: CfnAwsAccountPropsMetricsConfigNamespaceFilters#IncludeOnly
        '''
        result = self._values.get("include_only")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsMetricsConfigNamespaceFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsMetricsConfigTagFilters",
    jsii_struct_bases=[],
    name_mapping={"namespace": "namespace", "tags": "tags"},
)
class CfnAwsAccountPropsMetricsConfigTagFilters:
    def __init__(
        self,
        *,
        namespace: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param namespace: 
        :param tags: 

        :schema: CfnAwsAccountPropsMetricsConfigTagFilters
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f584a438e0a54a596d9505c065909dff51ccd90ded4bf68c69ec82b01a5dedf6)
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if namespace is not None:
            self._values["namespace"] = namespace
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnAwsAccountPropsMetricsConfigTagFilters#Namespace
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :schema: CfnAwsAccountPropsMetricsConfigTagFilters#Tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsMetricsConfigTagFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsResourcesConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cspm_resource_collection": "cspmResourceCollection",
        "extended_resource_collection": "extendedResourceCollection",
    },
)
class CfnAwsAccountPropsResourcesConfig:
    def __init__(
        self,
        *,
        cspm_resource_collection: typing.Optional[builtins.bool] = None,
        extended_resource_collection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''The configuration for ingesting AWS Resources into Datadog.

        :param cspm_resource_collection: Enable the compliance and security posture management Datadog product. This will enable collecting information on your AWS resources and providing security validation.
        :param extended_resource_collection: Enable collecting information on your AWS resources for use in Datadog products such as Network Process Monitoring.

        :schema: CfnAwsAccountPropsResourcesConfig
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__063ada2f14eeaf038d452c958b0d0bbbfeb4d17e2664de8e8286a9669b0ce13b)
            check_type(argname="argument cspm_resource_collection", value=cspm_resource_collection, expected_type=type_hints["cspm_resource_collection"])
            check_type(argname="argument extended_resource_collection", value=extended_resource_collection, expected_type=type_hints["extended_resource_collection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cspm_resource_collection is not None:
            self._values["cspm_resource_collection"] = cspm_resource_collection
        if extended_resource_collection is not None:
            self._values["extended_resource_collection"] = extended_resource_collection

    @builtins.property
    def cspm_resource_collection(self) -> typing.Optional[builtins.bool]:
        '''Enable the compliance and security posture management Datadog product.

        This will enable collecting information on your AWS resources and providing security validation.

        :schema: CfnAwsAccountPropsResourcesConfig#CSPMResourceCollection
        '''
        result = self._values.get("cspm_resource_collection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def extended_resource_collection(self) -> typing.Optional[builtins.bool]:
        '''Enable collecting information on your AWS resources for use in Datadog products such as Network Process Monitoring.

        :schema: CfnAwsAccountPropsResourcesConfig#ExtendedResourceCollection
        '''
        result = self._values.get("extended_resource_collection")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsResourcesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsTracesConfig",
    jsii_struct_bases=[],
    name_mapping={"x_ray_services": "xRayServices"},
)
class CfnAwsAccountPropsTracesConfig:
    def __init__(
        self,
        *,
        x_ray_services: typing.Optional[typing.Union["CfnAwsAccountPropsTracesConfigXRayServices", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''The configuration for ingesting AWS Traces into Datadog.

        :param x_ray_services: The services to collect X-Ray traces from.

        :schema: CfnAwsAccountPropsTracesConfig
        '''
        if isinstance(x_ray_services, dict):
            x_ray_services = CfnAwsAccountPropsTracesConfigXRayServices(**x_ray_services)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dbe02c8e90caaecbee173ee5a775420257c9750f95a51a786244687838ba656)
            check_type(argname="argument x_ray_services", value=x_ray_services, expected_type=type_hints["x_ray_services"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if x_ray_services is not None:
            self._values["x_ray_services"] = x_ray_services

    @builtins.property
    def x_ray_services(
        self,
    ) -> typing.Optional["CfnAwsAccountPropsTracesConfigXRayServices"]:
        '''The services to collect X-Ray traces from.

        :schema: CfnAwsAccountPropsTracesConfig#XRayServices
        '''
        result = self._values.get("x_ray_services")
        return typing.cast(typing.Optional["CfnAwsAccountPropsTracesConfigXRayServices"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsTracesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/datadog-integrations-awsaccount.CfnAwsAccountPropsTracesConfigXRayServices",
    jsii_struct_bases=[],
    name_mapping={"include_all": "includeAll", "include_only": "includeOnly"},
)
class CfnAwsAccountPropsTracesConfigXRayServices:
    def __init__(
        self,
        *,
        include_all: typing.Optional[builtins.bool] = None,
        include_only: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''The services to collect X-Ray traces from.

        :param include_all: Collect traces for all services.
        :param include_only: Array of services to collect traces for.

        :schema: CfnAwsAccountPropsTracesConfigXRayServices
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__effe307084c758b4065db7c7eddc70282eced1fed15f5a2b2616c466123c447c)
            check_type(argname="argument include_all", value=include_all, expected_type=type_hints["include_all"])
            check_type(argname="argument include_only", value=include_only, expected_type=type_hints["include_only"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if include_all is not None:
            self._values["include_all"] = include_all
        if include_only is not None:
            self._values["include_only"] = include_only

    @builtins.property
    def include_all(self) -> typing.Optional[builtins.bool]:
        '''Collect traces for all services.

        :schema: CfnAwsAccountPropsTracesConfigXRayServices#IncludeAll
        '''
        result = self._values.get("include_all")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def include_only(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Array of services to collect traces for.

        :schema: CfnAwsAccountPropsTracesConfigXRayServices#IncludeOnly
        '''
        result = self._values.get("include_only")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAwsAccountPropsTracesConfigXRayServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnAwsAccount",
    "CfnAwsAccountProps",
    "CfnAwsAccountPropsAuthConfig",
    "CfnAwsAccountPropsAwsPartition",
    "CfnAwsAccountPropsAwsRegions",
    "CfnAwsAccountPropsLogsConfig",
    "CfnAwsAccountPropsLogsConfigLambdaForwarder",
    "CfnAwsAccountPropsMetricsConfig",
    "CfnAwsAccountPropsMetricsConfigNamespaceFilters",
    "CfnAwsAccountPropsMetricsConfigTagFilters",
    "CfnAwsAccountPropsResourcesConfig",
    "CfnAwsAccountPropsTracesConfig",
    "CfnAwsAccountPropsTracesConfigXRayServices",
]

publication.publish()

def _typecheckingstub__eedd984825c69b36d4c1533da5427e2cb123b3a6e9dd2d782e5444bd23659cbf(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    auth_config: typing.Union[CfnAwsAccountPropsAuthConfig, typing.Dict[builtins.str, typing.Any]],
    aws_partition: CfnAwsAccountPropsAwsPartition,
    account_id: typing.Optional[builtins.str] = None,
    account_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    aws_regions: typing.Optional[typing.Union[CfnAwsAccountPropsAwsRegions, typing.Dict[builtins.str, typing.Any]]] = None,
    external_id_secret_name: typing.Optional[builtins.str] = None,
    logs_config: typing.Optional[typing.Union[CfnAwsAccountPropsLogsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    metrics_config: typing.Optional[typing.Union[CfnAwsAccountPropsMetricsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    resources_config: typing.Optional[typing.Union[CfnAwsAccountPropsResourcesConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    traces_config: typing.Optional[typing.Union[CfnAwsAccountPropsTracesConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1257d217dabd28334fd6a473666fbf1dcdb5458a7c01c668347093026341385(
    *,
    auth_config: typing.Union[CfnAwsAccountPropsAuthConfig, typing.Dict[builtins.str, typing.Any]],
    aws_partition: CfnAwsAccountPropsAwsPartition,
    account_id: typing.Optional[builtins.str] = None,
    account_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    aws_regions: typing.Optional[typing.Union[CfnAwsAccountPropsAwsRegions, typing.Dict[builtins.str, typing.Any]]] = None,
    external_id_secret_name: typing.Optional[builtins.str] = None,
    logs_config: typing.Optional[typing.Union[CfnAwsAccountPropsLogsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    metrics_config: typing.Optional[typing.Union[CfnAwsAccountPropsMetricsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    resources_config: typing.Optional[typing.Union[CfnAwsAccountPropsResourcesConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    traces_config: typing.Optional[typing.Union[CfnAwsAccountPropsTracesConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00bca8b180a23726f8f5105f96051004cbea09ccf99665f89d865bed9f32b785(
    *,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__610a9251870b617546874a092da09a24eb418c6d6305e3dc2e953e86730abd7f(
    *,
    include_all: typing.Optional[builtins.bool] = None,
    include_only: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a96310366ae7d5675ca20c8d07817c280dacdadf6154f4b10f366db6a58af573(
    *,
    lambda_forwarder: typing.Optional[typing.Union[CfnAwsAccountPropsLogsConfigLambdaForwarder, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__346546c03a01cf4ec35c2040998cd06e2df956fccf29d95d1a9d6c161acb8bd2(
    *,
    lambdas: typing.Optional[typing.Sequence[builtins.str]] = None,
    sources: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b27b58555e56b0e37e678cd55f81f734c7852221c12827ac012e4e2bd4f09614(
    *,
    automute_enabled: typing.Optional[builtins.bool] = None,
    collect_cloudwatch_alarms: typing.Optional[builtins.bool] = None,
    collect_custom_metrics: typing.Optional[builtins.bool] = None,
    enabled: typing.Optional[builtins.bool] = None,
    namespace_filters: typing.Optional[typing.Union[CfnAwsAccountPropsMetricsConfigNamespaceFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    tag_filters: typing.Optional[typing.Sequence[typing.Union[CfnAwsAccountPropsMetricsConfigTagFilters, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5ba132f2a1a4de9a3b5618c69d9bd7f10b5883f8e75ef0bc8e22f7eca9147f6(
    *,
    exclude_only: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_only: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f584a438e0a54a596d9505c065909dff51ccd90ded4bf68c69ec82b01a5dedf6(
    *,
    namespace: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__063ada2f14eeaf038d452c958b0d0bbbfeb4d17e2664de8e8286a9669b0ce13b(
    *,
    cspm_resource_collection: typing.Optional[builtins.bool] = None,
    extended_resource_collection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dbe02c8e90caaecbee173ee5a775420257c9750f95a51a786244687838ba656(
    *,
    x_ray_services: typing.Optional[typing.Union[CfnAwsAccountPropsTracesConfigXRayServices, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__effe307084c758b4065db7c7eddc70282eced1fed15f5a2b2616c466123c447c(
    *,
    include_all: typing.Optional[builtins.bool] = None,
    include_only: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
