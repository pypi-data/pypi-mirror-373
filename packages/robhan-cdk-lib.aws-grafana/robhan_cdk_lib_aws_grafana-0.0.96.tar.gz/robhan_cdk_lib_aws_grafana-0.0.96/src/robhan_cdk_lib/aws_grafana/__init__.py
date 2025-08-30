r'''
# @robhan-cdk-lib/aws_grafana

AWS Cloud Development Kit (CDK) constructs for Amazon Managed Grafana.

In [aws-cdk-lib.aws_grafana](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_grafana-readme.html), there currently only exist L1 constructs for Amazon Managed Grafana.

While helpful, they miss convenience like:

* advanced parameter checking (min/max number values, string lengths, array lengths...) before CloudFormation deployment
* proper parameter typing, e.g. enum values instead of strings
* simply referencing other constructs instead of e.g. ARN strings

Those features are implemented here.

The CDK maintainers explain that [publishing your own package](https://github.com/aws/aws-cdk/blob/main/CONTRIBUTING.md#publishing-your-own-package) is "by far the strongest signal you can give to the CDK team that a feature should be included within the core aws-cdk packages".

This project aims to develop aws_grafana constructs to a maturity that can potentially be accepted to the CDK core.

It is not supported by AWS and is not endorsed by them. Please file issues in the [GitHub repository](https://github.com/robert-hanuschke/cdk-aws_grafana/issues) if you find any.

## Example use

```python
import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import {
  AccountAccessType,
  AuthenticationProviders,
  PermissionTypes,
  Workspace,
} from "@robhan-cdk-lib/aws_grafana";
import { Role, ServicePrincipal } from "aws-cdk-lib/aws-iam";

export class AwsGrafanaCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const grafanaRole = new Role(this, "GrafanaWorkspaceRole", {
      assumedBy: new ServicePrincipal("grafana.amazonaws.com"),
      description: "Role for Amazon Managed Grafana Workspace",
    });

    const workspace = new Workspace(this, "Workspace", {
      accountAccessType: AccountAccessType.CURRENT_ACCOUNT,
      authenticationProviders: [AuthenticationProviders.AWS_SSO],
      permissionType: PermissionTypes.SERVICE_MANAGED,
      role: grafanaRole,
    });
  }
}
```

## License

MIT
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
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="@robhan-cdk-lib/aws_grafana.AccountAccessType")
class AccountAccessType(enum.Enum):
    '''Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization.

    If this is
    ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the
    workspace can access.
    '''

    CURRENT_ACCOUNT = "CURRENT_ACCOUNT"
    '''Access is limited to the current AWS account only.'''
    ORGANIZATION = "ORGANIZATION"
    '''Access is extended to the entire AWS organization.'''


@jsii.enum(jsii_type="@robhan-cdk-lib/aws_grafana.AuthenticationProviders")
class AuthenticationProviders(enum.Enum):
    '''Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace.

    :see: https://docs.aws.amazon.com/grafana/latest/APIReference/API_CreateWorkspace.html
    '''

    AWS_SSO = "AWS_SSO"
    '''AWS Single Sign-On authentication provider.'''
    SAML = "SAML"
    '''Security Assertion Markup Language (SAML) authentication provider.'''


@jsii.interface(jsii_type="@robhan-cdk-lib/aws_grafana.IWorkspace")
class IWorkspace(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''Represents an Amazon Managed Service for Grafana workspace.'''

    @builtins.property
    @jsii.member(jsii_name="accountAccessType")
    def account_access_type(self) -> AccountAccessType:
        '''Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization.

        If this is
        ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the
        workspace can access.
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="authenticationProviders")
    def authentication_providers(self) -> typing.List[AuthenticationProviders]:
        '''Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="permissionType")
    def permission_type(self) -> "PermissionTypes":
        '''If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels.

        If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself.

        If you are working with a workspace in a member account of an organization and that account is
        not a delegated administrator account, and you want the workspace to access data sources in
        other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED.
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="workspaceArn")
    def workspace_arn(self) -> builtins.str:
        '''The ARN of this workspace.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        '''The unique ID of this workspace.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="clientToken")
    def client_token(self) -> typing.Optional[builtins.str]:
        '''A unique, case-sensitive, user-provided identifier to ensure the idempotency of the request.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="dataSources")
    def data_sources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the AWS data sources that have been configured to have IAM roles and permissions created to allow Amazon Managed Grafana to read data from these sources.

        This list is only used when the workspace was created through the AWS console, and the
        permissionType is SERVICE_MANAGED.
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''The user-defined description of the workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="networkAccessControl")
    def network_access_control(self) -> typing.Optional["NetworkAccessControl"]:
        '''The configuration settings for network access to your workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="notificationDestinations")
    def notification_destinations(
        self,
    ) -> typing.Optional[typing.List["NotificationDestinations"]]:
        '''The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="organizationalUnits")
    def organizational_units(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="organizationRoleName")
    def organization_role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role that is used to access resources through Organizations.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="pluginAdminEnabled")
    def plugin_admin_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether plugin administration is enabled in the workspace.

        Setting to true allows workspace
        admins to install, uninstall, and update plugins from within the Grafana workspace.

        This option is only valid for workspaces that support Grafana version 9 or newer.
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role that grants permissions to the AWS resources that the workspace will view data from.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="samlConfiguration")
    def saml_configuration(self) -> typing.Optional["SamlConfiguration"]:
        '''If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="stackSetName")
    def stack_set_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="vpcConfiguration")
    def vpc_configuration(self) -> typing.Optional["VpcConfiguration"]:
        '''The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.'''
        ...


class _IWorkspaceProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''Represents an Amazon Managed Service for Grafana workspace.'''

    __jsii_type__: typing.ClassVar[str] = "@robhan-cdk-lib/aws_grafana.IWorkspace"

    @builtins.property
    @jsii.member(jsii_name="accountAccessType")
    def account_access_type(self) -> AccountAccessType:
        '''Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization.

        If this is
        ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the
        workspace can access.
        '''
        return typing.cast(AccountAccessType, jsii.get(self, "accountAccessType"))

    @builtins.property
    @jsii.member(jsii_name="authenticationProviders")
    def authentication_providers(self) -> typing.List[AuthenticationProviders]:
        '''Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace.'''
        return typing.cast(typing.List[AuthenticationProviders], jsii.get(self, "authenticationProviders"))

    @builtins.property
    @jsii.member(jsii_name="permissionType")
    def permission_type(self) -> "PermissionTypes":
        '''If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels.

        If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself.

        If you are working with a workspace in a member account of an organization and that account is
        not a delegated administrator account, and you want the workspace to access data sources in
        other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED.
        '''
        return typing.cast("PermissionTypes", jsii.get(self, "permissionType"))

    @builtins.property
    @jsii.member(jsii_name="workspaceArn")
    def workspace_arn(self) -> builtins.str:
        '''The ARN of this workspace.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "workspaceArn"))

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        '''The unique ID of this workspace.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @builtins.property
    @jsii.member(jsii_name="clientToken")
    def client_token(self) -> typing.Optional[builtins.str]:
        '''A unique, case-sensitive, user-provided identifier to ensure the idempotency of the request.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientToken"))

    @builtins.property
    @jsii.member(jsii_name="dataSources")
    def data_sources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the AWS data sources that have been configured to have IAM roles and permissions created to allow Amazon Managed Grafana to read data from these sources.

        This list is only used when the workspace was created through the AWS console, and the
        permissionType is SERVICE_MANAGED.
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dataSources"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''The user-defined description of the workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="networkAccessControl")
    def network_access_control(self) -> typing.Optional["NetworkAccessControl"]:
        '''The configuration settings for network access to your workspace.'''
        return typing.cast(typing.Optional["NetworkAccessControl"], jsii.get(self, "networkAccessControl"))

    @builtins.property
    @jsii.member(jsii_name="notificationDestinations")
    def notification_destinations(
        self,
    ) -> typing.Optional[typing.List["NotificationDestinations"]]:
        '''The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.'''
        return typing.cast(typing.Optional[typing.List["NotificationDestinations"]], jsii.get(self, "notificationDestinations"))

    @builtins.property
    @jsii.member(jsii_name="organizationalUnits")
    def organizational_units(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.'''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "organizationalUnits"))

    @builtins.property
    @jsii.member(jsii_name="organizationRoleName")
    def organization_role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role that is used to access resources through Organizations.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationRoleName"))

    @builtins.property
    @jsii.member(jsii_name="pluginAdminEnabled")
    def plugin_admin_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether plugin administration is enabled in the workspace.

        Setting to true allows workspace
        admins to install, uninstall, and update plugins from within the Grafana workspace.

        This option is only valid for workspaces that support Grafana version 9 or newer.
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "pluginAdminEnabled"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role that grants permissions to the AWS resources that the workspace will view data from.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="samlConfiguration")
    def saml_configuration(self) -> typing.Optional["SamlConfiguration"]:
        '''If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.'''
        return typing.cast(typing.Optional["SamlConfiguration"], jsii.get(self, "samlConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="stackSetName")
    def stack_set_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackSetName"))

    @builtins.property
    @jsii.member(jsii_name="vpcConfiguration")
    def vpc_configuration(self) -> typing.Optional["VpcConfiguration"]:
        '''The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.'''
        return typing.cast(typing.Optional["VpcConfiguration"], jsii.get(self, "vpcConfiguration"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWorkspace).__jsii_proxy_class__ = lambda : _IWorkspaceProxy


@jsii.data_type(
    jsii_type="@robhan-cdk-lib/aws_grafana.NetworkAccessControl",
    jsii_struct_bases=[],
    name_mapping={"prefix_lists": "prefixLists", "vpc_endpoints": "vpcEndpoints"},
)
class NetworkAccessControl:
    def __init__(
        self,
        *,
        prefix_lists: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.IPrefixList]] = None,
        vpc_endpoints: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.IVpcEndpoint]] = None,
    ) -> None:
        '''The configuration settings for network access to your workspace.

        :param prefix_lists: An array of prefix list IDs. A prefix list is a list of CIDR ranges of IP addresses. The IP addresses specified are allowed to access your workspace. If the list is not included in the configuration (passed an empty array) then no IP addresses are allowed to access the workspace. Maximum of 5 prefix lists allowed.
        :param vpc_endpoints: An array of Amazon VPC endpoint IDs for the workspace. You can create VPC endpoints to your Amazon Managed Grafana workspace for access from within a VPC. If a NetworkAccessConfiguration is specified then only VPC endpoints specified here are allowed to access the workspace. If you pass in an empty array of strings, then no VPCs are allowed to access the workspace. Maximum of 5 VPC endpoints allowed.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b57abbd6d5412b27ea5caabeb6d58c1a772f5dd9e53d0ba1d0295296567cbb8)
            check_type(argname="argument prefix_lists", value=prefix_lists, expected_type=type_hints["prefix_lists"])
            check_type(argname="argument vpc_endpoints", value=vpc_endpoints, expected_type=type_hints["vpc_endpoints"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if prefix_lists is not None:
            self._values["prefix_lists"] = prefix_lists
        if vpc_endpoints is not None:
            self._values["vpc_endpoints"] = vpc_endpoints

    @builtins.property
    def prefix_lists(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.IPrefixList]]:
        '''An array of prefix list IDs.

        A prefix list is a list of CIDR ranges of IP addresses. The IP
        addresses specified are allowed to access your workspace. If the list is not included in the
        configuration (passed an empty array) then no IP addresses are allowed to access the
        workspace.

        Maximum of 5 prefix lists allowed.
        '''
        result = self._values.get("prefix_lists")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.IPrefixList]], result)

    @builtins.property
    def vpc_endpoints(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.IVpcEndpoint]]:
        '''An array of Amazon VPC endpoint IDs for the workspace.

        You can create VPC endpoints to your
        Amazon Managed Grafana workspace for access from within a VPC. If a NetworkAccessConfiguration
        is specified then only VPC endpoints specified here are allowed to access the workspace. If
        you pass in an empty array of strings, then no VPCs are allowed to access the workspace.

        Maximum of 5 VPC endpoints allowed.
        '''
        result = self._values.get("vpc_endpoints")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.IVpcEndpoint]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkAccessControl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@robhan-cdk-lib/aws_grafana.NotificationDestinations")
class NotificationDestinations(enum.Enum):
    '''The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.'''

    SNS = "SNS"
    '''Amazon Simple Notification Service (SNS) as notification destination.'''


@jsii.enum(jsii_type="@robhan-cdk-lib/aws_grafana.PermissionTypes")
class PermissionTypes(enum.Enum):
    '''If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels.

    If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself.

    If you are working with a workspace in a member account of an organization and that account is
    not a delegated administrator account, and you want the workspace to access data sources in
    other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED.
    '''

    CUSTOMER_MANAGED = "CUSTOMER_MANAGED"
    '''Customer-managed permissions where you manage user access to Grafana.'''
    SERVICE_MANAGED = "SERVICE_MANAGED"
    '''Service-managed permissions where AWS manages user access to Grafana.'''


@jsii.data_type(
    jsii_type="@robhan-cdk-lib/aws_grafana.SamlAssertionAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "email": "email",
        "groups": "groups",
        "login": "login",
        "name": "name",
        "org": "org",
        "role": "role",
    },
)
class SamlAssertionAttributes:
    def __init__(
        self,
        *,
        email: typing.Optional[builtins.str] = None,
        groups: typing.Optional[builtins.str] = None,
        login: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        org: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''A structure that defines which attributes in the IdP assertion are to be used to define information about the users authenticated by the IdP to use the workspace.

        Each attribute must be a string with length between 1 and 256 characters.

        :param email: The name of the attribute within the SAML assertion to use as the email names for SAML users. Must be between 1 and 256 characters long.
        :param groups: The name of the attribute within the SAML assertion to use as the user full "friendly" names for user groups. Must be between 1 and 256 characters long.
        :param login: The name of the attribute within the SAML assertion to use as the login names for SAML users. Must be between 1 and 256 characters long.
        :param name: The name of the attribute within the SAML assertion to use as the user full "friendly" names for SAML users. Must be between 1 and 256 characters long.
        :param org: The name of the attribute within the SAML assertion to use as the user full "friendly" names for the users' organizations. Must be between 1 and 256 characters long.
        :param role: The name of the attribute within the SAML assertion to use as the user roles. Must be between 1 and 256 characters long.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6b87a6ceb131220a990409e721206d988891f136b4ef9fd7de25db4bea7624d)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument groups", value=groups, expected_type=type_hints["groups"])
            check_type(argname="argument login", value=login, expected_type=type_hints["login"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument org", value=org, expected_type=type_hints["org"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if email is not None:
            self._values["email"] = email
        if groups is not None:
            self._values["groups"] = groups
        if login is not None:
            self._values["login"] = login
        if name is not None:
            self._values["name"] = name
        if org is not None:
            self._values["org"] = org
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''The name of the attribute within the SAML assertion to use as the email names for SAML users.

        Must be between 1 and 256 characters long.
        '''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def groups(self) -> typing.Optional[builtins.str]:
        '''The name of the attribute within the SAML assertion to use as the user full "friendly" names for user groups.

        Must be between 1 and 256 characters long.
        '''
        result = self._values.get("groups")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def login(self) -> typing.Optional[builtins.str]:
        '''The name of the attribute within the SAML assertion to use as the login names for SAML users.

        Must be between 1 and 256 characters long.
        '''
        result = self._values.get("login")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the attribute within the SAML assertion to use as the user full "friendly" names for SAML users.

        Must be between 1 and 256 characters long.
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def org(self) -> typing.Optional[builtins.str]:
        '''The name of the attribute within the SAML assertion to use as the user full "friendly" names for the users' organizations.

        Must be between 1 and 256 characters long.
        '''
        result = self._values.get("org")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''The name of the attribute within the SAML assertion to use as the user roles.

        Must be between 1 and 256 characters long.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SamlAssertionAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@robhan-cdk-lib/aws_grafana.SamlConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "idp_metadata": "idpMetadata",
        "allowed_organizations": "allowedOrganizations",
        "assertion_atrributes": "assertionAtrributes",
        "login_validity_duration": "loginValidityDuration",
        "role_values": "roleValues",
    },
)
class SamlConfiguration:
    def __init__(
        self,
        *,
        idp_metadata: typing.Union["SamlIdpMetadata", typing.Dict[builtins.str, typing.Any]],
        allowed_organizations: typing.Optional[typing.Sequence[builtins.str]] = None,
        assertion_atrributes: typing.Optional[typing.Union[SamlAssertionAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
        login_validity_duration: typing.Optional[jsii.Number] = None,
        role_values: typing.Optional[typing.Union["SamlRoleValues", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.

        :param idp_metadata: A structure containing the identity provider (IdP) metadata used to integrate the identity provider with this workspace. Required field for SAML configuration.
        :param allowed_organizations: Lists which organizations defined in the SAML assertion are allowed to use the Amazon Managed Grafana workspace. If this is empty, all organizations in the assertion attribute have access. Must have between 1 and 256 elements.
        :param assertion_atrributes: A structure that defines which attributes in the SAML assertion are to be used to define information about the users authenticated by that IdP to use the workspace.
        :param login_validity_duration: How long a sign-on session by a SAML user is valid, before the user has to sign on again. Must be a positive number.
        :param role_values: A structure containing arrays that map group names in the SAML assertion to the Grafana Admin and Editor roles in the workspace.
        '''
        if isinstance(idp_metadata, dict):
            idp_metadata = SamlIdpMetadata(**idp_metadata)
        if isinstance(assertion_atrributes, dict):
            assertion_atrributes = SamlAssertionAttributes(**assertion_atrributes)
        if isinstance(role_values, dict):
            role_values = SamlRoleValues(**role_values)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94e3d50853b0fff8b07aef213a42805e2945150053d7d713d52a23ad79a71a21)
            check_type(argname="argument idp_metadata", value=idp_metadata, expected_type=type_hints["idp_metadata"])
            check_type(argname="argument allowed_organizations", value=allowed_organizations, expected_type=type_hints["allowed_organizations"])
            check_type(argname="argument assertion_atrributes", value=assertion_atrributes, expected_type=type_hints["assertion_atrributes"])
            check_type(argname="argument login_validity_duration", value=login_validity_duration, expected_type=type_hints["login_validity_duration"])
            check_type(argname="argument role_values", value=role_values, expected_type=type_hints["role_values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "idp_metadata": idp_metadata,
        }
        if allowed_organizations is not None:
            self._values["allowed_organizations"] = allowed_organizations
        if assertion_atrributes is not None:
            self._values["assertion_atrributes"] = assertion_atrributes
        if login_validity_duration is not None:
            self._values["login_validity_duration"] = login_validity_duration
        if role_values is not None:
            self._values["role_values"] = role_values

    @builtins.property
    def idp_metadata(self) -> "SamlIdpMetadata":
        '''A structure containing the identity provider (IdP) metadata used to integrate the identity provider with this workspace.

        Required field for SAML configuration.
        '''
        result = self._values.get("idp_metadata")
        assert result is not None, "Required property 'idp_metadata' is missing"
        return typing.cast("SamlIdpMetadata", result)

    @builtins.property
    def allowed_organizations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Lists which organizations defined in the SAML assertion are allowed to use the Amazon Managed Grafana workspace.

        If this is empty, all organizations in the assertion attribute have access.

        Must have between 1 and 256 elements.
        '''
        result = self._values.get("allowed_organizations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def assertion_atrributes(self) -> typing.Optional[SamlAssertionAttributes]:
        '''A structure that defines which attributes in the SAML assertion are to be used to define information about the users authenticated by that IdP to use the workspace.'''
        result = self._values.get("assertion_atrributes")
        return typing.cast(typing.Optional[SamlAssertionAttributes], result)

    @builtins.property
    def login_validity_duration(self) -> typing.Optional[jsii.Number]:
        '''How long a sign-on session by a SAML user is valid, before the user has to sign on again.

        Must be a positive number.
        '''
        result = self._values.get("login_validity_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role_values(self) -> typing.Optional["SamlRoleValues"]:
        '''A structure containing arrays that map group names in the SAML assertion to the Grafana Admin and Editor roles in the workspace.'''
        result = self._values.get("role_values")
        return typing.cast(typing.Optional["SamlRoleValues"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SamlConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@robhan-cdk-lib/aws_grafana.SamlConfigurationStatuses")
class SamlConfigurationStatuses(enum.Enum):
    '''Status of SAML configuration for a Grafana workspace.'''

    CONFIGURED = "CONFIGURED"
    '''SAML is configured for the workspace.'''
    NOT_CONFIGURED = "NOT_CONFIGURED"
    '''SAML is not configured for the workspace.'''


@jsii.data_type(
    jsii_type="@robhan-cdk-lib/aws_grafana.SamlIdpMetadata",
    jsii_struct_bases=[],
    name_mapping={"url": "url", "xml": "xml"},
)
class SamlIdpMetadata:
    def __init__(
        self,
        *,
        url: typing.Optional[builtins.str] = None,
        xml: typing.Optional[builtins.str] = None,
    ) -> None:
        '''A structure containing the identity provider (IdP) metadata used to integrate the identity provider with this workspace.

        :param url: The URL of the location containing the IdP metadata. Must be a string with length between 1 and 2048 characters.
        :param xml: The full IdP metadata, in XML format.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39c75c23ab5e000de459956f9472e74b38296a7f5017220c3d3353acf47ebeb1)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument xml", value=xml, expected_type=type_hints["xml"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if url is not None:
            self._values["url"] = url
        if xml is not None:
            self._values["xml"] = xml

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''The URL of the location containing the IdP metadata.

        Must be a string with length between 1 and 2048 characters.
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def xml(self) -> typing.Optional[builtins.str]:
        '''The full IdP metadata, in XML format.'''
        result = self._values.get("xml")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SamlIdpMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@robhan-cdk-lib/aws_grafana.SamlRoleValues",
    jsii_struct_bases=[],
    name_mapping={"admin": "admin", "editor": "editor"},
)
class SamlRoleValues:
    def __init__(
        self,
        *,
        admin: typing.Optional[typing.Sequence[builtins.str]] = None,
        editor: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''A structure containing arrays that map group names in the SAML assertion to the Grafana Admin and Editor roles in the workspace.

        :param admin: A list of groups from the SAML assertion attribute to grant the Grafana Admin role to. Maximum of 256 elements.
        :param editor: A list of groups from the SAML assertion attribute to grant the Grafana Editor role to. Maximum of 256 elements.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef1c910c03fee4fe40765505578b098a7dc7c4001c0dbce28b9c817cd1ceeb97)
            check_type(argname="argument admin", value=admin, expected_type=type_hints["admin"])
            check_type(argname="argument editor", value=editor, expected_type=type_hints["editor"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if admin is not None:
            self._values["admin"] = admin
        if editor is not None:
            self._values["editor"] = editor

    @builtins.property
    def admin(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of groups from the SAML assertion attribute to grant the Grafana Admin role to.

        Maximum of 256 elements.
        '''
        result = self._values.get("admin")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def editor(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of groups from the SAML assertion attribute to grant the Grafana Editor role to.

        Maximum of 256 elements.
        '''
        result = self._values.get("editor")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SamlRoleValues(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@robhan-cdk-lib/aws_grafana.Status")
class Status(enum.Enum):
    '''Status of a Grafana workspace.'''

    ACTIVE = "ACTIVE"
    '''Workspace is active and ready to use.'''
    CREATING = "CREATING"
    '''Workspace is being created.'''
    DELETING = "DELETING"
    '''Workspace is being deleted.'''
    FAILED = "FAILED"
    '''Workspace operation has failed.'''
    UPDATING = "UPDATING"
    '''Workspace is being updated.'''
    UPGRADING = "UPGRADING"
    '''Workspace is being upgraded.'''
    DELETION_FAILED = "DELETION_FAILED"
    '''Workspace deletion has failed.'''
    CREATION_FAILED = "CREATION_FAILED"
    '''Workspace creation has failed.'''
    UPDATE_FAILED = "UPDATE_FAILED"
    '''Workspace update has failed.'''
    UPGRADE_FAILED = "UPGRADE_FAILED"
    '''Workspace upgrade has failed.'''
    LICENSE_REMOVAL_FAILED = "LICENSE_REMOVAL_FAILED"
    '''License removal has failed.'''


@jsii.data_type(
    jsii_type="@robhan-cdk-lib/aws_grafana.VpcConfiguration",
    jsii_struct_bases=[],
    name_mapping={"security_groups": "securityGroups", "subnets": "subnets"},
)
class VpcConfiguration:
    def __init__(
        self,
        *,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
    ) -> None:
        '''The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.

        :param security_groups: The list of Amazon EC2 security groups attached to the Amazon VPC for your Grafana workspace to connect. Duplicates not allowed. Array Members: Minimum number of 1 items. Maximum number of 5 items. Required for VPC configuration.
        :param subnets: The list of Amazon EC2 subnets created in the Amazon VPC for your Grafana workspace to connect. Duplicates not allowed. Array Members: Minimum number of 2 items. Maximum number of 6 items. Required for VPC configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__587300abdd3ca28460b0e172422b96189b41d352cc212cc6461caee2653c197d)
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "security_groups": security_groups,
            "subnets": subnets,
        }

    @builtins.property
    def security_groups(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The list of Amazon EC2 security groups attached to the Amazon VPC for your Grafana workspace to connect.

        Duplicates not allowed.

        Array Members: Minimum number of 1 items. Maximum number of 5 items.

        Required for VPC configuration.
        '''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def subnets(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
        '''The list of Amazon EC2 subnets created in the Amazon VPC for your Grafana workspace to connect. Duplicates not allowed.

        Array Members: Minimum number of 2 items. Maximum number of 6 items.

        Required for VPC configuration.
        '''
        result = self._values.get("subnets")
        assert result is not None, "Required property 'subnets' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@robhan-cdk-lib/aws_grafana.WorkspaceAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "account_access_type": "accountAccessType",
        "authentication_providers": "authenticationProviders",
        "permission_type": "permissionType",
        "workspace_arn": "workspaceArn",
        "client_token": "clientToken",
        "data_sources": "dataSources",
        "description": "description",
        "name": "name",
        "network_access_control": "networkAccessControl",
        "notification_destinations": "notificationDestinations",
        "organizational_units": "organizationalUnits",
        "organization_role_name": "organizationRoleName",
        "plugin_admin_enabled": "pluginAdminEnabled",
        "role": "role",
        "saml_configuration": "samlConfiguration",
        "stack_set_name": "stackSetName",
        "vpc_configuration": "vpcConfiguration",
    },
)
class WorkspaceAttributes:
    def __init__(
        self,
        *,
        account_access_type: AccountAccessType,
        authentication_providers: typing.Sequence[AuthenticationProviders],
        permission_type: PermissionTypes,
        workspace_arn: builtins.str,
        client_token: typing.Optional[builtins.str] = None,
        data_sources: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        network_access_control: typing.Optional[typing.Union[NetworkAccessControl, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_destinations: typing.Optional[typing.Sequence[NotificationDestinations]] = None,
        organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_role_name: typing.Optional[builtins.str] = None,
        plugin_admin_enabled: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        saml_configuration: typing.Optional[typing.Union[SamlConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_set_name: typing.Optional[builtins.str] = None,
        vpc_configuration: typing.Optional[typing.Union[VpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param account_access_type: Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization. If this is ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the workspace can access. Required field.
        :param authentication_providers: Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace. Required field.
        :param permission_type: If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels. If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself. If you are working with a workspace in a member account of an organization and that account is not a delegated administrator account, and you want the workspace to access data sources in other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED. Required field.
        :param workspace_arn: The arn of this workspace.
        :param client_token: A unique, case-sensitive, user-provided identifier to ensure the idempotency of the request. Must be 1-64 characters long and contain only printable ASCII characters.
        :param data_sources: Specifies the AWS data sources that have been configured to have IAM roles and permissions created to allow Amazon Managed Grafana to read data from these sources. This list is only used when the workspace was created through the AWS console, and the permissionType is SERVICE_MANAGED.
        :param description: The user-defined description of the workspace. Maximum length of 2048 characters.
        :param name: The name of the workspace. Must be 1-255 characters long and contain only alphanumeric characters, hyphens, dots, underscores, and tildes.
        :param network_access_control: The configuration settings for network access to your workspace.
        :param notification_destinations: The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.
        :param organizational_units: Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.
        :param organization_role_name: Name of the IAM role to use for the organization. Maximum length of 2048 characters.
        :param plugin_admin_enabled: Whether plugin administration is enabled in the workspace. Setting to true allows workspace admins to install, uninstall, and update plugins from within the Grafana workspace. This option is only valid for workspaces that support Grafana version 9 or newer. Default: false
        :param role: The IAM role that grants permissions to the AWS resources that the workspace will view data from.
        :param saml_configuration: If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.
        :param stack_set_name: The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.
        :param vpc_configuration: The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.
        '''
        if isinstance(network_access_control, dict):
            network_access_control = NetworkAccessControl(**network_access_control)
        if isinstance(saml_configuration, dict):
            saml_configuration = SamlConfiguration(**saml_configuration)
        if isinstance(vpc_configuration, dict):
            vpc_configuration = VpcConfiguration(**vpc_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7b2f7e0bca3214d1d530a9824b09f4187fa0fc3d9bc0a9db3801c372ca6867d)
            check_type(argname="argument account_access_type", value=account_access_type, expected_type=type_hints["account_access_type"])
            check_type(argname="argument authentication_providers", value=authentication_providers, expected_type=type_hints["authentication_providers"])
            check_type(argname="argument permission_type", value=permission_type, expected_type=type_hints["permission_type"])
            check_type(argname="argument workspace_arn", value=workspace_arn, expected_type=type_hints["workspace_arn"])
            check_type(argname="argument client_token", value=client_token, expected_type=type_hints["client_token"])
            check_type(argname="argument data_sources", value=data_sources, expected_type=type_hints["data_sources"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_access_control", value=network_access_control, expected_type=type_hints["network_access_control"])
            check_type(argname="argument notification_destinations", value=notification_destinations, expected_type=type_hints["notification_destinations"])
            check_type(argname="argument organizational_units", value=organizational_units, expected_type=type_hints["organizational_units"])
            check_type(argname="argument organization_role_name", value=organization_role_name, expected_type=type_hints["organization_role_name"])
            check_type(argname="argument plugin_admin_enabled", value=plugin_admin_enabled, expected_type=type_hints["plugin_admin_enabled"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument saml_configuration", value=saml_configuration, expected_type=type_hints["saml_configuration"])
            check_type(argname="argument stack_set_name", value=stack_set_name, expected_type=type_hints["stack_set_name"])
            check_type(argname="argument vpc_configuration", value=vpc_configuration, expected_type=type_hints["vpc_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_access_type": account_access_type,
            "authentication_providers": authentication_providers,
            "permission_type": permission_type,
            "workspace_arn": workspace_arn,
        }
        if client_token is not None:
            self._values["client_token"] = client_token
        if data_sources is not None:
            self._values["data_sources"] = data_sources
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if network_access_control is not None:
            self._values["network_access_control"] = network_access_control
        if notification_destinations is not None:
            self._values["notification_destinations"] = notification_destinations
        if organizational_units is not None:
            self._values["organizational_units"] = organizational_units
        if organization_role_name is not None:
            self._values["organization_role_name"] = organization_role_name
        if plugin_admin_enabled is not None:
            self._values["plugin_admin_enabled"] = plugin_admin_enabled
        if role is not None:
            self._values["role"] = role
        if saml_configuration is not None:
            self._values["saml_configuration"] = saml_configuration
        if stack_set_name is not None:
            self._values["stack_set_name"] = stack_set_name
        if vpc_configuration is not None:
            self._values["vpc_configuration"] = vpc_configuration

    @builtins.property
    def account_access_type(self) -> AccountAccessType:
        '''Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization.

        If this is
        ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the
        workspace can access.

        Required field.
        '''
        result = self._values.get("account_access_type")
        assert result is not None, "Required property 'account_access_type' is missing"
        return typing.cast(AccountAccessType, result)

    @builtins.property
    def authentication_providers(self) -> typing.List[AuthenticationProviders]:
        '''Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace.

        Required field.
        '''
        result = self._values.get("authentication_providers")
        assert result is not None, "Required property 'authentication_providers' is missing"
        return typing.cast(typing.List[AuthenticationProviders], result)

    @builtins.property
    def permission_type(self) -> PermissionTypes:
        '''If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels.

        If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself.

        If you are working with a workspace in a member account of an organization and that account is
        not a delegated administrator account, and you want the workspace to access data sources in
        other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED.

        Required field.
        '''
        result = self._values.get("permission_type")
        assert result is not None, "Required property 'permission_type' is missing"
        return typing.cast(PermissionTypes, result)

    @builtins.property
    def workspace_arn(self) -> builtins.str:
        '''The arn of this workspace.'''
        result = self._values.get("workspace_arn")
        assert result is not None, "Required property 'workspace_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_token(self) -> typing.Optional[builtins.str]:
        '''A unique, case-sensitive, user-provided identifier to ensure the idempotency of the request.

        Must be 1-64 characters long and contain only printable ASCII characters.
        '''
        result = self._values.get("client_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_sources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the AWS data sources that have been configured to have IAM roles and permissions created to allow Amazon Managed Grafana to read data from these sources.

        This list is only used when the workspace was created through the AWS console, and the
        permissionType is SERVICE_MANAGED.
        '''
        result = self._values.get("data_sources")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The user-defined description of the workspace.

        Maximum length of 2048 characters.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the workspace.

        Must be 1-255 characters long and contain only alphanumeric characters, hyphens, dots,
        underscores, and tildes.
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_access_control(self) -> typing.Optional[NetworkAccessControl]:
        '''The configuration settings for network access to your workspace.'''
        result = self._values.get("network_access_control")
        return typing.cast(typing.Optional[NetworkAccessControl], result)

    @builtins.property
    def notification_destinations(
        self,
    ) -> typing.Optional[typing.List[NotificationDestinations]]:
        '''The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.'''
        result = self._values.get("notification_destinations")
        return typing.cast(typing.Optional[typing.List[NotificationDestinations]], result)

    @builtins.property
    def organizational_units(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.'''
        result = self._values.get("organizational_units")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def organization_role_name(self) -> typing.Optional[builtins.str]:
        '''Name of the IAM role to use for the organization.

        Maximum length of 2048 characters.
        '''
        result = self._values.get("organization_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plugin_admin_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether plugin administration is enabled in the workspace.

        Setting to true allows workspace
        admins to install, uninstall, and update plugins from within the Grafana workspace.

        This option is only valid for workspaces that support Grafana version 9 or newer.

        Default: false
        '''
        result = self._values.get("plugin_admin_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role that grants permissions to the AWS resources that the workspace will view data from.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def saml_configuration(self) -> typing.Optional[SamlConfiguration]:
        '''If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.'''
        result = self._values.get("saml_configuration")
        return typing.cast(typing.Optional[SamlConfiguration], result)

    @builtins.property
    def stack_set_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.'''
        result = self._values.get("stack_set_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_configuration(self) -> typing.Optional[VpcConfiguration]:
        '''The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.'''
        result = self._values.get("vpc_configuration")
        return typing.cast(typing.Optional[VpcConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IWorkspace)
class WorkspaceBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@robhan-cdk-lib/aws_grafana.WorkspaceBase",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__245faeb95108a919895d5be8305f00bb27663481697705f156a940170d368cd9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getWorkspaceArn")
    def _get_workspace_arn(self, workspace_id: builtins.str) -> builtins.str:
        '''
        :param workspace_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a276f8424bdc34ea475b2154afcc166ec7c942b054911427f1337d0e31dba971)
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        return typing.cast(builtins.str, jsii.invoke(self, "getWorkspaceArn", [workspace_id]))

    @jsii.member(jsii_name="getWorkspaceId")
    def _get_workspace_id(self, workspace_arn: builtins.str) -> builtins.str:
        '''
        :param workspace_arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e82b32e64bf2f45936f97dd7e9c4f587db6f6dc8f86a630542d208da05807e97)
            check_type(argname="argument workspace_arn", value=workspace_arn, expected_type=type_hints["workspace_arn"])
        return typing.cast(builtins.str, jsii.invoke(self, "getWorkspaceId", [workspace_arn]))

    @builtins.property
    @jsii.member(jsii_name="accountAccessType")
    @abc.abstractmethod
    def account_access_type(self) -> AccountAccessType:
        '''The account access type for the workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="authenticationProviders")
    @abc.abstractmethod
    def authentication_providers(self) -> typing.List[AuthenticationProviders]:
        '''The authentication providers for the workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="permissionType")
    @abc.abstractmethod
    def permission_type(self) -> PermissionTypes:
        '''The permission type for the workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="workspaceArn")
    @abc.abstractmethod
    def workspace_arn(self) -> builtins.str:
        '''The ARN of this workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    @abc.abstractmethod
    def workspace_id(self) -> builtins.str:
        '''The unique ID of this workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="clientToken")
    @abc.abstractmethod
    def client_token(self) -> typing.Optional[builtins.str]:
        '''The client token for the workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="dataSources")
    @abc.abstractmethod
    def data_sources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The data sources of this workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    @abc.abstractmethod
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of this workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    @abc.abstractmethod
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of this workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="networkAccessControl")
    @abc.abstractmethod
    def network_access_control(self) -> typing.Optional[NetworkAccessControl]:
        '''The configuration settings for network access to your workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="notificationDestinations")
    @abc.abstractmethod
    def notification_destinations(
        self,
    ) -> typing.Optional[typing.List[NotificationDestinations]]:
        '''The notification destinations for the workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="organizationalUnits")
    @abc.abstractmethod
    def organizational_units(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="organizationRoleName")
    @abc.abstractmethod
    def organization_role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role that is used to access resources through Organizations.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="pluginAdminEnabled")
    @abc.abstractmethod
    def plugin_admin_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether plugin administration is enabled in the workspace.

        Setting to true allows workspace
        admins to install, uninstall, and update plugins from within the Grafana workspace.

        This option is only valid for workspaces that support Grafana version 9 or newer.
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="role")
    @abc.abstractmethod
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role that grants permissions to the AWS resources that the workspace will view data from.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="samlConfiguration")
    @abc.abstractmethod
    def saml_configuration(self) -> typing.Optional[SamlConfiguration]:
        '''If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="stackSetName")
    @abc.abstractmethod
    def stack_set_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="vpcConfiguration")
    @abc.abstractmethod
    def vpc_configuration(self) -> typing.Optional[VpcConfiguration]:
        '''The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.'''
        ...


class _WorkspaceBaseProxy(
    WorkspaceBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="accountAccessType")
    def account_access_type(self) -> AccountAccessType:
        '''The account access type for the workspace.'''
        return typing.cast(AccountAccessType, jsii.get(self, "accountAccessType"))

    @builtins.property
    @jsii.member(jsii_name="authenticationProviders")
    def authentication_providers(self) -> typing.List[AuthenticationProviders]:
        '''The authentication providers for the workspace.'''
        return typing.cast(typing.List[AuthenticationProviders], jsii.get(self, "authenticationProviders"))

    @builtins.property
    @jsii.member(jsii_name="permissionType")
    def permission_type(self) -> PermissionTypes:
        '''The permission type for the workspace.'''
        return typing.cast(PermissionTypes, jsii.get(self, "permissionType"))

    @builtins.property
    @jsii.member(jsii_name="workspaceArn")
    def workspace_arn(self) -> builtins.str:
        '''The ARN of this workspace.'''
        return typing.cast(builtins.str, jsii.get(self, "workspaceArn"))

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        '''The unique ID of this workspace.'''
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @builtins.property
    @jsii.member(jsii_name="clientToken")
    def client_token(self) -> typing.Optional[builtins.str]:
        '''The client token for the workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientToken"))

    @builtins.property
    @jsii.member(jsii_name="dataSources")
    def data_sources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The data sources of this workspace.'''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dataSources"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of this workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of this workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="networkAccessControl")
    def network_access_control(self) -> typing.Optional[NetworkAccessControl]:
        '''The configuration settings for network access to your workspace.'''
        return typing.cast(typing.Optional[NetworkAccessControl], jsii.get(self, "networkAccessControl"))

    @builtins.property
    @jsii.member(jsii_name="notificationDestinations")
    def notification_destinations(
        self,
    ) -> typing.Optional[typing.List[NotificationDestinations]]:
        '''The notification destinations for the workspace.'''
        return typing.cast(typing.Optional[typing.List[NotificationDestinations]], jsii.get(self, "notificationDestinations"))

    @builtins.property
    @jsii.member(jsii_name="organizationalUnits")
    def organizational_units(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.'''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "organizationalUnits"))

    @builtins.property
    @jsii.member(jsii_name="organizationRoleName")
    def organization_role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role that is used to access resources through Organizations.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationRoleName"))

    @builtins.property
    @jsii.member(jsii_name="pluginAdminEnabled")
    def plugin_admin_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether plugin administration is enabled in the workspace.

        Setting to true allows workspace
        admins to install, uninstall, and update plugins from within the Grafana workspace.

        This option is only valid for workspaces that support Grafana version 9 or newer.
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "pluginAdminEnabled"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role that grants permissions to the AWS resources that the workspace will view data from.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="samlConfiguration")
    def saml_configuration(self) -> typing.Optional[SamlConfiguration]:
        '''If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.'''
        return typing.cast(typing.Optional[SamlConfiguration], jsii.get(self, "samlConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="stackSetName")
    def stack_set_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackSetName"))

    @builtins.property
    @jsii.member(jsii_name="vpcConfiguration")
    def vpc_configuration(self) -> typing.Optional[VpcConfiguration]:
        '''The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.'''
        return typing.cast(typing.Optional[VpcConfiguration], jsii.get(self, "vpcConfiguration"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, WorkspaceBase).__jsii_proxy_class__ = lambda : _WorkspaceBaseProxy


@jsii.data_type(
    jsii_type="@robhan-cdk-lib/aws_grafana.WorkspaceProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_access_type": "accountAccessType",
        "authentication_providers": "authenticationProviders",
        "permission_type": "permissionType",
        "client_token": "clientToken",
        "data_sources": "dataSources",
        "description": "description",
        "grafana_version": "grafanaVersion",
        "name": "name",
        "network_access_control": "networkAccessControl",
        "notification_destinations": "notificationDestinations",
        "organizational_units": "organizationalUnits",
        "organization_role_name": "organizationRoleName",
        "plugin_admin_enabled": "pluginAdminEnabled",
        "role": "role",
        "saml_configuration": "samlConfiguration",
        "stack_set_name": "stackSetName",
        "vpc_configuration": "vpcConfiguration",
    },
)
class WorkspaceProps:
    def __init__(
        self,
        *,
        account_access_type: AccountAccessType,
        authentication_providers: typing.Sequence[AuthenticationProviders],
        permission_type: PermissionTypes,
        client_token: typing.Optional[builtins.str] = None,
        data_sources: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        grafana_version: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        network_access_control: typing.Optional[typing.Union[NetworkAccessControl, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_destinations: typing.Optional[typing.Sequence[NotificationDestinations]] = None,
        organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_role_name: typing.Optional[builtins.str] = None,
        plugin_admin_enabled: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        saml_configuration: typing.Optional[typing.Union[SamlConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_set_name: typing.Optional[builtins.str] = None,
        vpc_configuration: typing.Optional[typing.Union[VpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for creating an Amazon Managed Grafana workspace.

        :param account_access_type: Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization. If this is ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the workspace can access. Required field.
        :param authentication_providers: Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace. Required field.
        :param permission_type: If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels. If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself. If you are working with a workspace in a member account of an organization and that account is not a delegated administrator account, and you want the workspace to access data sources in other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED. Required field.
        :param client_token: A unique, case-sensitive, user-provided identifier to ensure the idempotency of the request. Must be 1-64 characters long and contain only printable ASCII characters.
        :param data_sources: Specifies the AWS data sources that have been configured to have IAM roles and permissions created to allow Amazon Managed Grafana to read data from these sources. This list is only used when the workspace was created through the AWS console, and the permissionType is SERVICE_MANAGED.
        :param description: The user-defined description of the workspace. Maximum length of 2048 characters.
        :param grafana_version: Specifies the version of Grafana to support in the workspace. Defaults to the latest version on create (for example, 9.4), or the current version of the workspace on update. Can only be used to upgrade (for example, from 8.4 to 9.4), not downgrade (for example, from 9.4 to 8.4). Must be 1-255 characters long.
        :param name: The name of the workspace. Must be 1-255 characters long and contain only alphanumeric characters, hyphens, dots, underscores, and tildes.
        :param network_access_control: The configuration settings for network access to your workspace.
        :param notification_destinations: The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.
        :param organizational_units: Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.
        :param organization_role_name: Name of the IAM role to use for the organization. Maximum length of 2048 characters.
        :param plugin_admin_enabled: Whether plugin administration is enabled in the workspace. Setting to true allows workspace admins to install, uninstall, and update plugins from within the Grafana workspace. This option is only valid for workspaces that support Grafana version 9 or newer. Default: false
        :param role: The IAM role that grants permissions to the AWS resources that the workspace will view data from.
        :param saml_configuration: If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.
        :param stack_set_name: The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.
        :param vpc_configuration: The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.
        '''
        if isinstance(network_access_control, dict):
            network_access_control = NetworkAccessControl(**network_access_control)
        if isinstance(saml_configuration, dict):
            saml_configuration = SamlConfiguration(**saml_configuration)
        if isinstance(vpc_configuration, dict):
            vpc_configuration = VpcConfiguration(**vpc_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a19e08d1da95762003a1adc6b6920b31ab0030dc3f030331c79c2bfcebcfdcf2)
            check_type(argname="argument account_access_type", value=account_access_type, expected_type=type_hints["account_access_type"])
            check_type(argname="argument authentication_providers", value=authentication_providers, expected_type=type_hints["authentication_providers"])
            check_type(argname="argument permission_type", value=permission_type, expected_type=type_hints["permission_type"])
            check_type(argname="argument client_token", value=client_token, expected_type=type_hints["client_token"])
            check_type(argname="argument data_sources", value=data_sources, expected_type=type_hints["data_sources"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument grafana_version", value=grafana_version, expected_type=type_hints["grafana_version"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_access_control", value=network_access_control, expected_type=type_hints["network_access_control"])
            check_type(argname="argument notification_destinations", value=notification_destinations, expected_type=type_hints["notification_destinations"])
            check_type(argname="argument organizational_units", value=organizational_units, expected_type=type_hints["organizational_units"])
            check_type(argname="argument organization_role_name", value=organization_role_name, expected_type=type_hints["organization_role_name"])
            check_type(argname="argument plugin_admin_enabled", value=plugin_admin_enabled, expected_type=type_hints["plugin_admin_enabled"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument saml_configuration", value=saml_configuration, expected_type=type_hints["saml_configuration"])
            check_type(argname="argument stack_set_name", value=stack_set_name, expected_type=type_hints["stack_set_name"])
            check_type(argname="argument vpc_configuration", value=vpc_configuration, expected_type=type_hints["vpc_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_access_type": account_access_type,
            "authentication_providers": authentication_providers,
            "permission_type": permission_type,
        }
        if client_token is not None:
            self._values["client_token"] = client_token
        if data_sources is not None:
            self._values["data_sources"] = data_sources
        if description is not None:
            self._values["description"] = description
        if grafana_version is not None:
            self._values["grafana_version"] = grafana_version
        if name is not None:
            self._values["name"] = name
        if network_access_control is not None:
            self._values["network_access_control"] = network_access_control
        if notification_destinations is not None:
            self._values["notification_destinations"] = notification_destinations
        if organizational_units is not None:
            self._values["organizational_units"] = organizational_units
        if organization_role_name is not None:
            self._values["organization_role_name"] = organization_role_name
        if plugin_admin_enabled is not None:
            self._values["plugin_admin_enabled"] = plugin_admin_enabled
        if role is not None:
            self._values["role"] = role
        if saml_configuration is not None:
            self._values["saml_configuration"] = saml_configuration
        if stack_set_name is not None:
            self._values["stack_set_name"] = stack_set_name
        if vpc_configuration is not None:
            self._values["vpc_configuration"] = vpc_configuration

    @builtins.property
    def account_access_type(self) -> AccountAccessType:
        '''Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization.

        If this is
        ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the
        workspace can access.

        Required field.
        '''
        result = self._values.get("account_access_type")
        assert result is not None, "Required property 'account_access_type' is missing"
        return typing.cast(AccountAccessType, result)

    @builtins.property
    def authentication_providers(self) -> typing.List[AuthenticationProviders]:
        '''Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace.

        Required field.
        '''
        result = self._values.get("authentication_providers")
        assert result is not None, "Required property 'authentication_providers' is missing"
        return typing.cast(typing.List[AuthenticationProviders], result)

    @builtins.property
    def permission_type(self) -> PermissionTypes:
        '''If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels.

        If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself.

        If you are working with a workspace in a member account of an organization and that account is
        not a delegated administrator account, and you want the workspace to access data sources in
        other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED.

        Required field.
        '''
        result = self._values.get("permission_type")
        assert result is not None, "Required property 'permission_type' is missing"
        return typing.cast(PermissionTypes, result)

    @builtins.property
    def client_token(self) -> typing.Optional[builtins.str]:
        '''A unique, case-sensitive, user-provided identifier to ensure the idempotency of the request.

        Must be 1-64 characters long and contain only printable ASCII characters.
        '''
        result = self._values.get("client_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_sources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the AWS data sources that have been configured to have IAM roles and permissions created to allow Amazon Managed Grafana to read data from these sources.

        This list is only used when the workspace was created through the AWS console, and the
        permissionType is SERVICE_MANAGED.
        '''
        result = self._values.get("data_sources")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The user-defined description of the workspace.

        Maximum length of 2048 characters.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def grafana_version(self) -> typing.Optional[builtins.str]:
        '''Specifies the version of Grafana to support in the workspace.

        Defaults to the latest version
        on create (for example, 9.4), or the current version of the workspace on update.
        Can only be used to upgrade (for example, from 8.4 to 9.4), not downgrade (for example, from
        9.4 to 8.4).

        Must be 1-255 characters long.
        '''
        result = self._values.get("grafana_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the workspace.

        Must be 1-255 characters long and contain only alphanumeric characters, hyphens, dots,
        underscores, and tildes.
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_access_control(self) -> typing.Optional[NetworkAccessControl]:
        '''The configuration settings for network access to your workspace.'''
        result = self._values.get("network_access_control")
        return typing.cast(typing.Optional[NetworkAccessControl], result)

    @builtins.property
    def notification_destinations(
        self,
    ) -> typing.Optional[typing.List[NotificationDestinations]]:
        '''The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.'''
        result = self._values.get("notification_destinations")
        return typing.cast(typing.Optional[typing.List[NotificationDestinations]], result)

    @builtins.property
    def organizational_units(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.'''
        result = self._values.get("organizational_units")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def organization_role_name(self) -> typing.Optional[builtins.str]:
        '''Name of the IAM role to use for the organization.

        Maximum length of 2048 characters.
        '''
        result = self._values.get("organization_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plugin_admin_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether plugin administration is enabled in the workspace.

        Setting to true allows workspace
        admins to install, uninstall, and update plugins from within the Grafana workspace.

        This option is only valid for workspaces that support Grafana version 9 or newer.

        Default: false
        '''
        result = self._values.get("plugin_admin_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role that grants permissions to the AWS resources that the workspace will view data from.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def saml_configuration(self) -> typing.Optional[SamlConfiguration]:
        '''If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.'''
        result = self._values.get("saml_configuration")
        return typing.cast(typing.Optional[SamlConfiguration], result)

    @builtins.property
    def stack_set_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.'''
        result = self._values.get("stack_set_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_configuration(self) -> typing.Optional[VpcConfiguration]:
        '''The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.'''
        result = self._values.get("vpc_configuration")
        return typing.cast(typing.Optional[VpcConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Workspace(
    WorkspaceBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@robhan-cdk-lib/aws_grafana.Workspace",
):
    '''Specifies a workspace.

    In a workspace, you can create Grafana dashboards and visualizations to
    analyze your metrics, logs, and traces. You don't have to build, package, or deploy any hardware
    to run the Grafana server.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_access_type: AccountAccessType,
        authentication_providers: typing.Sequence[AuthenticationProviders],
        permission_type: PermissionTypes,
        client_token: typing.Optional[builtins.str] = None,
        data_sources: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        grafana_version: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        network_access_control: typing.Optional[typing.Union[NetworkAccessControl, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_destinations: typing.Optional[typing.Sequence[NotificationDestinations]] = None,
        organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_role_name: typing.Optional[builtins.str] = None,
        plugin_admin_enabled: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        saml_configuration: typing.Optional[typing.Union[SamlConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_set_name: typing.Optional[builtins.str] = None,
        vpc_configuration: typing.Optional[typing.Union[VpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account_access_type: Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization. If this is ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the workspace can access. Required field.
        :param authentication_providers: Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace. Required field.
        :param permission_type: If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels. If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself. If you are working with a workspace in a member account of an organization and that account is not a delegated administrator account, and you want the workspace to access data sources in other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED. Required field.
        :param client_token: A unique, case-sensitive, user-provided identifier to ensure the idempotency of the request. Must be 1-64 characters long and contain only printable ASCII characters.
        :param data_sources: Specifies the AWS data sources that have been configured to have IAM roles and permissions created to allow Amazon Managed Grafana to read data from these sources. This list is only used when the workspace was created through the AWS console, and the permissionType is SERVICE_MANAGED.
        :param description: The user-defined description of the workspace. Maximum length of 2048 characters.
        :param grafana_version: Specifies the version of Grafana to support in the workspace. Defaults to the latest version on create (for example, 9.4), or the current version of the workspace on update. Can only be used to upgrade (for example, from 8.4 to 9.4), not downgrade (for example, from 9.4 to 8.4). Must be 1-255 characters long.
        :param name: The name of the workspace. Must be 1-255 characters long and contain only alphanumeric characters, hyphens, dots, underscores, and tildes.
        :param network_access_control: The configuration settings for network access to your workspace.
        :param notification_destinations: The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.
        :param organizational_units: Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.
        :param organization_role_name: Name of the IAM role to use for the organization. Maximum length of 2048 characters.
        :param plugin_admin_enabled: Whether plugin administration is enabled in the workspace. Setting to true allows workspace admins to install, uninstall, and update plugins from within the Grafana workspace. This option is only valid for workspaces that support Grafana version 9 or newer. Default: false
        :param role: The IAM role that grants permissions to the AWS resources that the workspace will view data from.
        :param saml_configuration: If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.
        :param stack_set_name: The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.
        :param vpc_configuration: The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b689f4d81575ce56f0717294fb20c042f4f3a61a02b0d137e099a528d65a115)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WorkspaceProps(
            account_access_type=account_access_type,
            authentication_providers=authentication_providers,
            permission_type=permission_type,
            client_token=client_token,
            data_sources=data_sources,
            description=description,
            grafana_version=grafana_version,
            name=name,
            network_access_control=network_access_control,
            notification_destinations=notification_destinations,
            organizational_units=organizational_units,
            organization_role_name=organization_role_name,
            plugin_admin_enabled=plugin_admin_enabled,
            role=role,
            saml_configuration=saml_configuration,
            stack_set_name=stack_set_name,
            vpc_configuration=vpc_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromWorkspaceAttributes")
    @builtins.classmethod
    def from_workspace_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_access_type: AccountAccessType,
        authentication_providers: typing.Sequence[AuthenticationProviders],
        permission_type: PermissionTypes,
        workspace_arn: builtins.str,
        client_token: typing.Optional[builtins.str] = None,
        data_sources: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        network_access_control: typing.Optional[typing.Union[NetworkAccessControl, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_destinations: typing.Optional[typing.Sequence[NotificationDestinations]] = None,
        organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_role_name: typing.Optional[builtins.str] = None,
        plugin_admin_enabled: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        saml_configuration: typing.Optional[typing.Union[SamlConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_set_name: typing.Optional[builtins.str] = None,
        vpc_configuration: typing.Optional[typing.Union[VpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> IWorkspace:
        '''
        :param scope: -
        :param id: -
        :param account_access_type: Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization. If this is ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the workspace can access. Required field.
        :param authentication_providers: Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace. Required field.
        :param permission_type: If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels. If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself. If you are working with a workspace in a member account of an organization and that account is not a delegated administrator account, and you want the workspace to access data sources in other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED. Required field.
        :param workspace_arn: The arn of this workspace.
        :param client_token: A unique, case-sensitive, user-provided identifier to ensure the idempotency of the request. Must be 1-64 characters long and contain only printable ASCII characters.
        :param data_sources: Specifies the AWS data sources that have been configured to have IAM roles and permissions created to allow Amazon Managed Grafana to read data from these sources. This list is only used when the workspace was created through the AWS console, and the permissionType is SERVICE_MANAGED.
        :param description: The user-defined description of the workspace. Maximum length of 2048 characters.
        :param name: The name of the workspace. Must be 1-255 characters long and contain only alphanumeric characters, hyphens, dots, underscores, and tildes.
        :param network_access_control: The configuration settings for network access to your workspace.
        :param notification_destinations: The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.
        :param organizational_units: Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.
        :param organization_role_name: Name of the IAM role to use for the organization. Maximum length of 2048 characters.
        :param plugin_admin_enabled: Whether plugin administration is enabled in the workspace. Setting to true allows workspace admins to install, uninstall, and update plugins from within the Grafana workspace. This option is only valid for workspaces that support Grafana version 9 or newer. Default: false
        :param role: The IAM role that grants permissions to the AWS resources that the workspace will view data from.
        :param saml_configuration: If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.
        :param stack_set_name: The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.
        :param vpc_configuration: The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3998e8138348ba3fd0198ea857bd0357c9ffc4806dd420f1974b384d9116186f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = WorkspaceAttributes(
            account_access_type=account_access_type,
            authentication_providers=authentication_providers,
            permission_type=permission_type,
            workspace_arn=workspace_arn,
            client_token=client_token,
            data_sources=data_sources,
            description=description,
            name=name,
            network_access_control=network_access_control,
            notification_destinations=notification_destinations,
            organizational_units=organizational_units,
            organization_role_name=organization_role_name,
            plugin_admin_enabled=plugin_admin_enabled,
            role=role,
            saml_configuration=saml_configuration,
            stack_set_name=stack_set_name,
            vpc_configuration=vpc_configuration,
        )

        return typing.cast(IWorkspace, jsii.sinvoke(cls, "fromWorkspaceAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="isWorkspace")
    @builtins.classmethod
    def is_workspace(cls, x: typing.Any) -> builtins.bool:
        '''
        :param x: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8766b8935a0812af5a2370796de3e9ea5301499bca4f246f4d41b667fa063728)
            check_type(argname="argument x", value=x, expected_type=type_hints["x"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isWorkspace", [x]))

    @builtins.property
    @jsii.member(jsii_name="accountAccessType")
    def account_access_type(self) -> AccountAccessType:
        '''Specifies whether the workspace can access AWS resources in this AWS account only, or whether it can also access AWS resources in other accounts in the same organization.

        If this is
        ORGANIZATION, the OrganizationalUnits parameter specifies which organizational units the
        workspace can access.
        '''
        return typing.cast(AccountAccessType, jsii.get(self, "accountAccessType"))

    @builtins.property
    @jsii.member(jsii_name="authenticationProviders")
    def authentication_providers(self) -> typing.List[AuthenticationProviders]:
        '''Specifies whether this workspace uses SAML 2.0, AWS IAM Identity Center, or both to authenticate users for using the Grafana console within a workspace.'''
        return typing.cast(typing.List[AuthenticationProviders], jsii.get(self, "authenticationProviders"))

    @builtins.property
    @jsii.member(jsii_name="creationTimestamp")
    def creation_timestamp(self) -> builtins.str:
        '''The date that the workspace was created.'''
        return typing.cast(builtins.str, jsii.get(self, "creationTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        '''The URL that users can use to access the Grafana console in the workspace.'''
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="grafanaVersion")
    def grafana_version(self) -> builtins.str:
        '''Specifies the version of Grafana supported by this workspace.'''
        return typing.cast(builtins.str, jsii.get(self, "grafanaVersion"))

    @builtins.property
    @jsii.member(jsii_name="modificationTimestamp")
    def modification_timestamp(self) -> builtins.str:
        '''The most recent date that the workspace was modified.'''
        return typing.cast(builtins.str, jsii.get(self, "modificationTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="permissionType")
    def permission_type(self) -> PermissionTypes:
        '''If this is SERVICE_MANAGED, and the workplace was created through the Amazon Managed Grafana console, then Amazon Managed Grafana automatically creates the IAM roles and provisions the permissions that the workspace needs to use AWS data sources and notification channels.

        If this is CUSTOMER_MANAGED, you must manage those roles and permissions yourself.

        If you are working with a workspace in a member account of an organization and that account is
        not a delegated administrator account, and you want the workspace to access data sources in
        other AWS accounts in the organization, this parameter must be set to CUSTOMER_MANAGED.
        '''
        return typing.cast(PermissionTypes, jsii.get(self, "permissionType"))

    @builtins.property
    @jsii.member(jsii_name="samlConfigurationStatus")
    def saml_configuration_status(self) -> SamlConfigurationStatuses:
        '''Specifies whether the workspace's SAML configuration is complete.'''
        return typing.cast(SamlConfigurationStatuses, jsii.get(self, "samlConfigurationStatus"))

    @builtins.property
    @jsii.member(jsii_name="ssoClientId")
    def sso_client_id(self) -> builtins.str:
        '''The ID of the IAM Identity Center-managed application that is created by Amazon Managed Grafana.'''
        return typing.cast(builtins.str, jsii.get(self, "ssoClientId"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> Status:
        '''The current status of the workspace.'''
        return typing.cast(Status, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="workspaceArn")
    def workspace_arn(self) -> builtins.str:
        '''The arn of this workspace.'''
        return typing.cast(builtins.str, jsii.get(self, "workspaceArn"))

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        '''The unique ID of this workspace.'''
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @builtins.property
    @jsii.member(jsii_name="clientToken")
    def client_token(self) -> typing.Optional[builtins.str]:
        '''A unique, case-sensitive, user-provided identifier to ensure the idempotency of the request.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientToken"))

    @builtins.property
    @jsii.member(jsii_name="dataSources")
    def data_sources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the AWS data sources that have been configured to have IAM roles and permissions created to allow Amazon Managed Grafana to read data from these sources.

        This list is only used when the workspace was created through the AWS console, and the
        permissionType is SERVICE_MANAGED.
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dataSources"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''The user-defined description of the workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="networkAccessControl")
    def network_access_control(self) -> typing.Optional[NetworkAccessControl]:
        '''The configuration settings for network access to your workspace.'''
        return typing.cast(typing.Optional[NetworkAccessControl], jsii.get(self, "networkAccessControl"))

    @builtins.property
    @jsii.member(jsii_name="notificationDestinations")
    def notification_destinations(
        self,
    ) -> typing.Optional[typing.List[NotificationDestinations]]:
        '''The AWS notification channels that Amazon Managed Grafana can automatically create IAM roles and permissions for, to allow Amazon Managed Grafana to use these channels.'''
        return typing.cast(typing.Optional[typing.List[NotificationDestinations]], jsii.get(self, "notificationDestinations"))

    @builtins.property
    @jsii.member(jsii_name="organizationalUnits")
    def organizational_units(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the organizational units that this workspace is allowed to use data sources from, if this workspace is in an account that is part of an organization.'''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "organizationalUnits"))

    @builtins.property
    @jsii.member(jsii_name="organizationRoleName")
    def organization_role_name(self) -> typing.Optional[builtins.str]:
        '''The name of the IAM role that is used to access resources through Organizations.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationRoleName"))

    @builtins.property
    @jsii.member(jsii_name="pluginAdminEnabled")
    def plugin_admin_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether plugin administration is enabled in the workspace.

        Setting to true allows workspace
        admins to install, uninstall, and update plugins from within the Grafana workspace.

        This option is only valid for workspaces that support Grafana version 9 or newer.
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "pluginAdminEnabled"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role that grants permissions to the AWS resources that the workspace will view data from.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="samlConfiguration")
    def saml_configuration(self) -> typing.Optional[SamlConfiguration]:
        '''If the workspace uses SAML, use this structure to map SAML assertion attributes to workspace user information and define which groups in the assertion attribute are to have the Admin and Editor roles in the workspace.'''
        return typing.cast(typing.Optional[SamlConfiguration], jsii.get(self, "samlConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="stackSetName")
    def stack_set_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS CloudFormation stack set that is used to generate IAM roles to be used for this workspace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackSetName"))

    @builtins.property
    @jsii.member(jsii_name="vpcConfiguration")
    def vpc_configuration(self) -> typing.Optional[VpcConfiguration]:
        '''The configuration settings for an Amazon VPC that contains data sources for your Grafana workspace to connect to.'''
        return typing.cast(typing.Optional[VpcConfiguration], jsii.get(self, "vpcConfiguration"))


__all__ = [
    "AccountAccessType",
    "AuthenticationProviders",
    "IWorkspace",
    "NetworkAccessControl",
    "NotificationDestinations",
    "PermissionTypes",
    "SamlAssertionAttributes",
    "SamlConfiguration",
    "SamlConfigurationStatuses",
    "SamlIdpMetadata",
    "SamlRoleValues",
    "Status",
    "VpcConfiguration",
    "Workspace",
    "WorkspaceAttributes",
    "WorkspaceBase",
    "WorkspaceProps",
]

publication.publish()

def _typecheckingstub__1b57abbd6d5412b27ea5caabeb6d58c1a772f5dd9e53d0ba1d0295296567cbb8(
    *,
    prefix_lists: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.IPrefixList]] = None,
    vpc_endpoints: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.IVpcEndpoint]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6b87a6ceb131220a990409e721206d988891f136b4ef9fd7de25db4bea7624d(
    *,
    email: typing.Optional[builtins.str] = None,
    groups: typing.Optional[builtins.str] = None,
    login: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    org: typing.Optional[builtins.str] = None,
    role: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94e3d50853b0fff8b07aef213a42805e2945150053d7d713d52a23ad79a71a21(
    *,
    idp_metadata: typing.Union[SamlIdpMetadata, typing.Dict[builtins.str, typing.Any]],
    allowed_organizations: typing.Optional[typing.Sequence[builtins.str]] = None,
    assertion_atrributes: typing.Optional[typing.Union[SamlAssertionAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    login_validity_duration: typing.Optional[jsii.Number] = None,
    role_values: typing.Optional[typing.Union[SamlRoleValues, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39c75c23ab5e000de459956f9472e74b38296a7f5017220c3d3353acf47ebeb1(
    *,
    url: typing.Optional[builtins.str] = None,
    xml: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef1c910c03fee4fe40765505578b098a7dc7c4001c0dbce28b9c817cd1ceeb97(
    *,
    admin: typing.Optional[typing.Sequence[builtins.str]] = None,
    editor: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__587300abdd3ca28460b0e172422b96189b41d352cc212cc6461caee2653c197d(
    *,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7b2f7e0bca3214d1d530a9824b09f4187fa0fc3d9bc0a9db3801c372ca6867d(
    *,
    account_access_type: AccountAccessType,
    authentication_providers: typing.Sequence[AuthenticationProviders],
    permission_type: PermissionTypes,
    workspace_arn: builtins.str,
    client_token: typing.Optional[builtins.str] = None,
    data_sources: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    network_access_control: typing.Optional[typing.Union[NetworkAccessControl, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_destinations: typing.Optional[typing.Sequence[NotificationDestinations]] = None,
    organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
    organization_role_name: typing.Optional[builtins.str] = None,
    plugin_admin_enabled: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    saml_configuration: typing.Optional[typing.Union[SamlConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_set_name: typing.Optional[builtins.str] = None,
    vpc_configuration: typing.Optional[typing.Union[VpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__245faeb95108a919895d5be8305f00bb27663481697705f156a940170d368cd9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a276f8424bdc34ea475b2154afcc166ec7c942b054911427f1337d0e31dba971(
    workspace_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e82b32e64bf2f45936f97dd7e9c4f587db6f6dc8f86a630542d208da05807e97(
    workspace_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a19e08d1da95762003a1adc6b6920b31ab0030dc3f030331c79c2bfcebcfdcf2(
    *,
    account_access_type: AccountAccessType,
    authentication_providers: typing.Sequence[AuthenticationProviders],
    permission_type: PermissionTypes,
    client_token: typing.Optional[builtins.str] = None,
    data_sources: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    grafana_version: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    network_access_control: typing.Optional[typing.Union[NetworkAccessControl, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_destinations: typing.Optional[typing.Sequence[NotificationDestinations]] = None,
    organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
    organization_role_name: typing.Optional[builtins.str] = None,
    plugin_admin_enabled: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    saml_configuration: typing.Optional[typing.Union[SamlConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_set_name: typing.Optional[builtins.str] = None,
    vpc_configuration: typing.Optional[typing.Union[VpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b689f4d81575ce56f0717294fb20c042f4f3a61a02b0d137e099a528d65a115(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_access_type: AccountAccessType,
    authentication_providers: typing.Sequence[AuthenticationProviders],
    permission_type: PermissionTypes,
    client_token: typing.Optional[builtins.str] = None,
    data_sources: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    grafana_version: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    network_access_control: typing.Optional[typing.Union[NetworkAccessControl, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_destinations: typing.Optional[typing.Sequence[NotificationDestinations]] = None,
    organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
    organization_role_name: typing.Optional[builtins.str] = None,
    plugin_admin_enabled: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    saml_configuration: typing.Optional[typing.Union[SamlConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_set_name: typing.Optional[builtins.str] = None,
    vpc_configuration: typing.Optional[typing.Union[VpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3998e8138348ba3fd0198ea857bd0357c9ffc4806dd420f1974b384d9116186f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_access_type: AccountAccessType,
    authentication_providers: typing.Sequence[AuthenticationProviders],
    permission_type: PermissionTypes,
    workspace_arn: builtins.str,
    client_token: typing.Optional[builtins.str] = None,
    data_sources: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    network_access_control: typing.Optional[typing.Union[NetworkAccessControl, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_destinations: typing.Optional[typing.Sequence[NotificationDestinations]] = None,
    organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
    organization_role_name: typing.Optional[builtins.str] = None,
    plugin_admin_enabled: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    saml_configuration: typing.Optional[typing.Union[SamlConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_set_name: typing.Optional[builtins.str] = None,
    vpc_configuration: typing.Optional[typing.Union[VpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8766b8935a0812af5a2370796de3e9ea5301499bca4f246f4d41b667fa063728(
    x: typing.Any,
) -> None:
    """Type checking stubs"""
    pass
