r'''
# AWS CodeConnections Host Custom Resource

[![GitHub](https://img.shields.io/github/license/gammarers/aws-codeconnections-host-custom-resource?style=flat-square)](https://github.com/gammarers/aws-codeconnections-host-custom-resource/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarers/aws-codeconnections-host-custom-resource?style=flat-square)](https://www.npmjs.com/package/@gammarers/aws-codeconnections-host-custom-resource)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/gammarers/aws-codeconnections-host-custom-resource/release.yml?branch=main&label=release&style=flat-square)](https://github.com/gammarers/aws-codeconnections-host-custom-resource/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/gammarers/aws-codeconnections-host-custom-resource?sort=semver&style=flat-square)](https://github.com/gammarers/aws-codeconnections-host-custom-resource/releases)

[![View on Construct Hub](https://constructs.dev/badge?package=@gammarers/aws-codeconnections-host-custom-resource)](https://constructs.dev/packages/@gammarers/aws-codeconnections-host-custom-resource)

This AWS CDK Construct provides a custom resource (Lambda Function) to create a connection host for Self-Managed GitLab, which is not yet supported by CloudFormation. Additionally, even after creating the Host and the connection, authentication must be done via a browser.

## Install

### TypeScript

#### install by npm

```shell
npm install @gammarers/aws-codeconnections-host-custom-resource
```

#### install by yarn

```shell
yarn add @gammarers/aws-codeconnections-host-custom-resource
```

### Python

#### install by pip

```shell
pip install gammarers.aws-budgets-notification
```

## Example

```python
import { CodeConnectionsHostCustomResource, CodeConnectionsHostProviderType } from '@gammarers/aws-codeconnections-host-custom-resource';

const codeConnectionsHostCustomResource = new CodeConnectionsHostCustomResource(this, 'CodeConnectionsHost', {
  name: 'gitlab.example.com', // required, connection host name (Minimum length of 1. Maximum length of 64.)
  providerEndpoint: 'https://gitlab.example.com', // required, your provider endpoint (Minimum length of 1. Maximum length of 512.)
  providerType: CodeConnectionsHostProviderType.GIT_LAB_SELF_MANAGED,
});

// get host arn
const hostArn = gitLabSelfManagedConnectionHostCustomResource.findHostArn();

new codeconnections.CfnConnection(this, 'Connection', {
  connectionName: 'example-gitlab-connection',
  hostArn,
});
```

## How to complete (Update a pending connection)

Deploy completed after being configured in EXAMPLE.
At this point, the status is ‘Pending’ as shown below because authentication has not yet been completed.

<img alt="CodeConnection Setup 01" src="images/CodeConnection-Setup-01.png" width="800" />

Select the ‘Connection’ you have created to display the Connection detail screen.

<img alt="CodeConnection Setup 02" src="images/CodeConnection-Setup-02.png" width="800" />

You will see the ‘Pending’ status as follows. Select ‘Update pending connection’.

<img alt="CodeConnection Setup 03" src="images/CodeConnection-Setup-03.png" width="800" />

A screen to enter the Provide personal access token (pat) will be displayed; the pat should be created in the target host environment (only api should be enabled). Enter the pat and select ‘Continue’.

<img alt="CodeConnection Setup 04" src="images/CodeConnection-Setup-04.png" width="500" />

The host authorisation screen will appear as shown below, select ‘Authorise’ (the screen will pop up).

> If you have not logged in, a login screen will be displayed, please log in.

<img alt="CodeConnection Setup 05" src="images/CodeConnection-Setup-05.png" width="800" />

When completed, the status will change to ‘Available’ as follows. This completes all Connection settings.

## License

This project is licensed under the Apache-2.0 License.
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

import aws_cdk.custom_resources as _aws_cdk_custom_resources_ceddda9d
import constructs as _constructs_77d1e7e8
import gammarers.aws_resource_naming as _gammarers_aws_resource_naming_22f917da


class CodeConnectionsHostCustomResource(
    _aws_cdk_custom_resources_ceddda9d.AwsCustomResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarers/aws-codeconnections-host-custom-resource.CodeConnectionsHostCustomResource",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        provider_endpoint: builtins.str,
        provider_type: "CodeConnectionsHostProviderType",
        resource_naming_option: typing.Optional[typing.Union[typing.Union["CustomNaming", typing.Dict[builtins.str, typing.Any]], typing.Union[_gammarers_aws_resource_naming_22f917da.ResourceDefaultNaming, typing.Dict[builtins.str, typing.Any]], typing.Union[_gammarers_aws_resource_naming_22f917da.ResourceAutoNaming, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: 
        :param provider_endpoint: 
        :param provider_type: 
        :param resource_naming_option: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93e92fc39e37866f7e6881c8a553116ad11f67a1051166fa67f97f695c92329f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CodeConnectionsHostCustomResourceProps(
            name=name,
            provider_endpoint=provider_endpoint,
            provider_type=provider_type,
            resource_naming_option=resource_naming_option,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="findHostArn")
    def find_host_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "findHostArn", []))


@jsii.data_type(
    jsii_type="@gammarers/aws-codeconnections-host-custom-resource.CodeConnectionsHostCustomResourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "provider_endpoint": "providerEndpoint",
        "provider_type": "providerType",
        "resource_naming_option": "resourceNamingOption",
    },
)
class CodeConnectionsHostCustomResourceProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        provider_endpoint: builtins.str,
        provider_type: "CodeConnectionsHostProviderType",
        resource_naming_option: typing.Optional[typing.Union[typing.Union["CustomNaming", typing.Dict[builtins.str, typing.Any]], typing.Union[_gammarers_aws_resource_naming_22f917da.ResourceDefaultNaming, typing.Dict[builtins.str, typing.Any]], typing.Union[_gammarers_aws_resource_naming_22f917da.ResourceAutoNaming, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param name: 
        :param provider_endpoint: 
        :param provider_type: 
        :param resource_naming_option: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__784fa6fe7d14609c195c71c179fa9c4b8deffdef65bb91d227c890fbdca7b022)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument provider_endpoint", value=provider_endpoint, expected_type=type_hints["provider_endpoint"])
            check_type(argname="argument provider_type", value=provider_type, expected_type=type_hints["provider_type"])
            check_type(argname="argument resource_naming_option", value=resource_naming_option, expected_type=type_hints["resource_naming_option"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "provider_endpoint": provider_endpoint,
            "provider_type": provider_type,
        }
        if resource_naming_option is not None:
            self._values["resource_naming_option"] = resource_naming_option

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_endpoint(self) -> builtins.str:
        result = self._values.get("provider_endpoint")
        assert result is not None, "Required property 'provider_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_type(self) -> "CodeConnectionsHostProviderType":
        result = self._values.get("provider_type")
        assert result is not None, "Required property 'provider_type' is missing"
        return typing.cast("CodeConnectionsHostProviderType", result)

    @builtins.property
    def resource_naming_option(
        self,
    ) -> typing.Optional[typing.Union["CustomNaming", _gammarers_aws_resource_naming_22f917da.ResourceDefaultNaming, _gammarers_aws_resource_naming_22f917da.ResourceAutoNaming]]:
        result = self._values.get("resource_naming_option")
        return typing.cast(typing.Optional[typing.Union["CustomNaming", _gammarers_aws_resource_naming_22f917da.ResourceDefaultNaming, _gammarers_aws_resource_naming_22f917da.ResourceAutoNaming]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeConnectionsHostCustomResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@gammarers/aws-codeconnections-host-custom-resource.CodeConnectionsHostProviderType"
)
class CodeConnectionsHostProviderType(enum.Enum):
    BIT_BUCKET = "BIT_BUCKET"
    GIT_HUB = "GIT_HUB"
    GIT_HUB_ENTERPRISE_SERVER = "GIT_HUB_ENTERPRISE_SERVER"
    GIT_LAB = "GIT_LAB"
    GIT_LAB_SELF_MANAGED = "GIT_LAB_SELF_MANAGED"


@jsii.data_type(
    jsii_type="@gammarers/aws-codeconnections-host-custom-resource.CustomNaming",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "function_role_name": "functionRoleName",
        "type": "type",
    },
)
class CustomNaming:
    def __init__(
        self,
        *,
        function_name: builtins.str,
        function_role_name: builtins.str,
        type: _gammarers_aws_resource_naming_22f917da.ResourceNamingType,
    ) -> None:
        '''
        :param function_name: 
        :param function_role_name: 
        :param type: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1579af63e1a9a0d79323a6813932ed60b7460de2012517ed07509522a63c45c)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument function_role_name", value=function_role_name, expected_type=type_hints["function_role_name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "function_name": function_name,
            "function_role_name": function_role_name,
            "type": type,
        }

    @builtins.property
    def function_name(self) -> builtins.str:
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_role_name(self) -> builtins.str:
        result = self._values.get("function_role_name")
        assert result is not None, "Required property 'function_role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> _gammarers_aws_resource_naming_22f917da.ResourceNamingType:
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(_gammarers_aws_resource_naming_22f917da.ResourceNamingType, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomNaming(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@gammarers/aws-codeconnections-host-custom-resource.ResponseField"
)
class ResponseField(enum.Enum):
    HOST_ARN = "HOST_ARN"


__all__ = [
    "CodeConnectionsHostCustomResource",
    "CodeConnectionsHostCustomResourceProps",
    "CodeConnectionsHostProviderType",
    "CustomNaming",
    "ResponseField",
]

publication.publish()

def _typecheckingstub__93e92fc39e37866f7e6881c8a553116ad11f67a1051166fa67f97f695c92329f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    provider_endpoint: builtins.str,
    provider_type: CodeConnectionsHostProviderType,
    resource_naming_option: typing.Optional[typing.Union[typing.Union[CustomNaming, typing.Dict[builtins.str, typing.Any]], typing.Union[_gammarers_aws_resource_naming_22f917da.ResourceDefaultNaming, typing.Dict[builtins.str, typing.Any]], typing.Union[_gammarers_aws_resource_naming_22f917da.ResourceAutoNaming, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__784fa6fe7d14609c195c71c179fa9c4b8deffdef65bb91d227c890fbdca7b022(
    *,
    name: builtins.str,
    provider_endpoint: builtins.str,
    provider_type: CodeConnectionsHostProviderType,
    resource_naming_option: typing.Optional[typing.Union[typing.Union[CustomNaming, typing.Dict[builtins.str, typing.Any]], typing.Union[_gammarers_aws_resource_naming_22f917da.ResourceDefaultNaming, typing.Dict[builtins.str, typing.Any]], typing.Union[_gammarers_aws_resource_naming_22f917da.ResourceAutoNaming, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1579af63e1a9a0d79323a6813932ed60b7460de2012517ed07509522a63c45c(
    *,
    function_name: builtins.str,
    function_role_name: builtins.str,
    type: _gammarers_aws_resource_naming_22f917da.ResourceNamingType,
) -> None:
    """Type checking stubs"""
    pass
