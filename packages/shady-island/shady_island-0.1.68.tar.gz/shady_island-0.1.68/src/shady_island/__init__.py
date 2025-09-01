r'''
# shady-island

[![Apache 2.0](https://img.shields.io/github/license/libreworks/shady-island)](https://github.com/libreworks/shady-island/blob/main/LICENSE)
[![npm](https://img.shields.io/npm/v/shady-island)](https://www.npmjs.com/package/shady-island)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/libreworks/shady-island/release/main?label=release)](https://github.com/libreworks/shady-island/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/libreworks/shady-island?sort=semver)](https://github.com/libreworks/shady-island/releases)
[![codecov](https://codecov.io/gh/libreworks/shady-island/branch/main/graph/badge.svg?token=OHTRGNTSPO)](https://codecov.io/gh/libreworks/shady-island)

Utilities and constructs for the AWS CDK.

## Features

* Create IPv6 CIDRs and routes for subnets in a VPC with the `CidrContext` construct.
* Set the `AssignIpv6AddressOnCreation` property of subnets in a VPC with the `AssignOnLaunch` construct.
* Properly encrypt a CloudWatch Log group with a KMS key and provision IAM permissions with the `EncryptedLogGroup` construct.
* Represent a deployment tier with the `Tier` class.
* Create a subclass of the `Workload` construct to contain your `Stack`s, and optionally load context values from a JSON file you specify.

## Documentation

* [TypeScript API Reference](https://libreworks.github.io/shady-island/api/)

## The Name

It's a pun. In English, the pronunciation of the acronym *CDK* sounds a bit like the phrase *seedy cay*. A seedy cay might also be called a *shady island*.
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
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_ecs_patterns as _aws_cdk_aws_ecs_patterns_ceddda9d
import aws_cdk.aws_efs as _aws_cdk_aws_efs_ceddda9d
import aws_cdk.aws_events_targets as _aws_cdk_aws_events_targets_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import aws_cdk.aws_stepfunctions_tasks as _aws_cdk_aws_stepfunctions_tasks_ceddda9d
import aws_cdk.triggers as _aws_cdk_triggers_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="shady-island.AssignOnLaunchProps",
    jsii_struct_bases=[],
    name_mapping={"vpc": "vpc", "vpc_subnets": "vpcSubnets"},
)
class AssignOnLaunchProps:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for creating a new {@link AssignOnLaunch}.

        :param vpc: The VPC whose subnets will be configured.
        :param vpc_subnets: Which subnets to assign IPv6 addresses upon ENI creation.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf6464fd9d48d82d0db14a3cccbdb92cb250ed4fe6d6bd38b8e06d86417f53f2)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC whose subnets will be configured.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Which subnets to assign IPv6 addresses upon ENI creation.'''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AssignOnLaunchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.BaseDatabaseOptions",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "security_group": "securityGroup",
        "vpc_subnets": "vpcSubnets",
    },
)
class BaseDatabaseOptions:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''These options cannot be determined from existing Database constructs.

        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcb5a876ef1282aa92f1dad8eb5bf7808d5fb9ec194106c40e9fd2365c63e177)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
        }
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog to create.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group for the Lambda function.

        :default: - a new security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The type of subnets in the VPC where the Lambda function will run.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseDatabaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.BaseDatabaseProps",
    jsii_struct_bases=[BaseDatabaseOptions],
    name_mapping={
        "database_name": "databaseName",
        "security_group": "securityGroup",
        "vpc_subnets": "vpcSubnets",
        "admin_secret": "adminSecret",
        "endpoint": "endpoint",
        "target": "target",
        "vpc": "vpc",
    },
)
class BaseDatabaseProps(BaseDatabaseOptions):
    def __init__(
        self,
        *,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
        target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    ) -> None:
        '''The properties for a database.

        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param endpoint: The cluster or instance endpoint.
        :param target: The target service or database.
        :param vpc: The VPC where the Lambda function will run.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__638e3f17e92b33884a123777384d2096ff52784838ea6a387eb453df4acabdf0)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument admin_secret", value=admin_secret, expected_type=type_hints["admin_secret"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "admin_secret": admin_secret,
            "endpoint": endpoint,
            "target": target,
            "vpc": vpc,
        }
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog to create.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group for the Lambda function.

        :default: - a new security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The type of subnets in the VPC where the Lambda function will run.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def admin_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''A Secrets Manager secret that contains administrative credentials.'''
        result = self._values.get("admin_secret")
        assert result is not None, "Required property 'admin_secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''The cluster or instance endpoint.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, result)

    @builtins.property
    def target(self) -> _aws_cdk_aws_ec2_ceddda9d.IConnectable:
        '''The target service or database.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IConnectable, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where the Lambda function will run.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.BaseFargateTaskProps",
    jsii_struct_bases=[],
    name_mapping={
        "assign_public_ip": "assignPublicIp",
        "security_groups": "securityGroups",
        "vpc_subnets": "vpcSubnets",
    },
)
class BaseFargateTaskProps:
    def __init__(
        self,
        *,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Common parameters for Fargate Tasks.

        :param assign_public_ip: Specifies whether the task's elastic network interface receives a public IP address. If true, the task will receive a public IP address. Default: false
        :param security_groups: Existing security groups to use for your task. Default: - a new security group will be created.
        :param vpc_subnets: The subnets to associate with the task. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2d82fd0175001f3a0180f4788e513f4bb8d14a42ee961f880b1ba5b5ed8e2bc)
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether the task's elastic network interface receives a public IP address.

        If true, the task will receive a public IP address.

        :default: false
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Existing security groups to use for your task.

        :default: - a new security group will be created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets to associate with the task.

        :default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseFargateTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.CidrContextProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "address_pool": "addressPool",
        "assign_address_on_launch": "assignAddressOnLaunch",
        "cidr_block": "cidrBlock",
        "cidr_count": "cidrCount",
    },
)
class CidrContextProps:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        address_pool: typing.Optional[builtins.str] = None,
        assign_address_on_launch: typing.Optional[builtins.bool] = None,
        cidr_block: typing.Optional[builtins.str] = None,
        cidr_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties for creating a new {@link CidrContext}.

        :param vpc: The VPC whose subnets will be configured.
        :param address_pool: The ID of a BYOIP IPv6 address pool from which to allocate the CIDR block. If this parameter is not specified or is undefined, the CIDR block will be provided by AWS.
        :param assign_address_on_launch: (deprecated) Whether this VPC should auto-assign an IPv6 address to launched ENIs. True by default.
        :param cidr_block: An IPv6 CIDR block from the IPv6 address pool to use for this VPC. The {@link EnableIpv6Props#addressPool } attribute is required if this parameter is specified.
        :param cidr_count: Split the CIDRs into this many groups (by default one for each subnet).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__050e47d5b52c553cfe8b87e6673a27b8787fd0db2253c4e7b62521814ed5ae1d)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument address_pool", value=address_pool, expected_type=type_hints["address_pool"])
            check_type(argname="argument assign_address_on_launch", value=assign_address_on_launch, expected_type=type_hints["assign_address_on_launch"])
            check_type(argname="argument cidr_block", value=cidr_block, expected_type=type_hints["cidr_block"])
            check_type(argname="argument cidr_count", value=cidr_count, expected_type=type_hints["cidr_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if address_pool is not None:
            self._values["address_pool"] = address_pool
        if assign_address_on_launch is not None:
            self._values["assign_address_on_launch"] = assign_address_on_launch
        if cidr_block is not None:
            self._values["cidr_block"] = cidr_block
        if cidr_count is not None:
            self._values["cidr_count"] = cidr_count

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC whose subnets will be configured.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def address_pool(self) -> typing.Optional[builtins.str]:
        '''The ID of a BYOIP IPv6 address pool from which to allocate the CIDR block.

        If this parameter is not specified or is undefined, the CIDR block will be
        provided by AWS.
        '''
        result = self._values.get("address_pool")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assign_address_on_launch(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether this VPC should auto-assign an IPv6 address to launched ENIs.

        True by default.

        :deprecated: - Launch templates now support specifying IPv6 addresses

        :stability: deprecated
        '''
        result = self._values.get("assign_address_on_launch")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cidr_block(self) -> typing.Optional[builtins.str]:
        '''An IPv6 CIDR block from the IPv6 address pool to use for this VPC.

        The {@link EnableIpv6Props#addressPool } attribute is required if this
        parameter is specified.
        '''
        result = self._values.get("cidr_block")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cidr_count(self) -> typing.Optional[jsii.Number]:
        '''Split the CIDRs into this many groups (by default one for each subnet).'''
        result = self._values.get("cidr_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CidrContextProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContextLoader(metaclass=jsii.JSIIMeta, jsii_type="shady-island.ContextLoader"):
    '''A utility to load context values into a construct node.

    If you want to use this utility in your own construct, make sure to invoke it
    before you create any child constructs.
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="loadContext")
    @builtins.classmethod
    def load_context(
        cls,
        filename: builtins.str,
        node: _constructs_77d1e7e8.Node,
    ) -> None:
        '''Parses JSON file contents, then provides the values to a Node's context.

        :param filename: - The JSON file with an object to use as context values.
        :param node: - The constructs node to receive the context values.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92ecc06c0a44e3636156ab00eb64f42cc69e3471e1fdad7321210a3770b10cfd)
            check_type(argname="argument filename", value=filename, expected_type=type_hints["filename"])
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.sinvoke(cls, "loadContext", [filename, node]))


class ContextLoadingStage(
    _aws_cdk_ceddda9d.Stage,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.ContextLoadingStage",
):
    '''A Stage that can load context values from a JSON file.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        context_file: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new ContextLoadingStage.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param context_file: The filesystem path to a JSON file that contains context values to load. Using this property allows you to load different context values within each Stage, directly from a file you can check into source control.
        :param env: Default AWS environment (account/region) for ``Stack``s in this ``Stage``. Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing from its env will use the corresponding field given here. If either ``region`` or ``account``is is not configured for ``Stack`` (either on the ``Stack`` itself or on the containing ``Stage``), the Stack will be *environment-agnostic*. Environment-agnostic stacks can be deployed to any environment, may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups, will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environments should be configured on the ``Stack``s.
        :param outdir: The output directory into which to emit synthesized artifacts. Can only be specified if this stage is the root stage (the app). If this is specified and this stage is nested within another stage, an error will be thrown. Default: - for nested stages, outdir will be determined as a relative directory to the outdir of the app. For apps, if outdir is not specified, a temporary directory will be created.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param policy_validation_beta1: Validation plugins to run during synthesis. If any plugin reports any violation, synthesis will be interrupted and the report displayed to the user. Default: - no validation plugins are used
        :param stage_name: Name of this stage. Default: - Derived from the id.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af9e712087c9d94895740eba9c235f48c4ad49d51b9e4dbb62f7a6fd29fb1620)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ContextLoadingStageProps(
            context_file=context_file,
            env=env,
            outdir=outdir,
            permissions_boundary=permissions_boundary,
            policy_validation_beta1=policy_validation_beta1,
            stage_name=stage_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="shady-island.ContextLoadingStageProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StageProps],
    name_mapping={
        "env": "env",
        "outdir": "outdir",
        "permissions_boundary": "permissionsBoundary",
        "policy_validation_beta1": "policyValidationBeta1",
        "stage_name": "stageName",
        "context_file": "contextFile",
    },
)
class ContextLoadingStageProps(_aws_cdk_ceddda9d.StageProps):
    def __init__(
        self,
        *,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        stage_name: typing.Optional[builtins.str] = None,
        context_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructor properties for ContextLoadingStage.

        :param env: Default AWS environment (account/region) for ``Stack``s in this ``Stage``. Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing from its env will use the corresponding field given here. If either ``region`` or ``account``is is not configured for ``Stack`` (either on the ``Stack`` itself or on the containing ``Stage``), the Stack will be *environment-agnostic*. Environment-agnostic stacks can be deployed to any environment, may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups, will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environments should be configured on the ``Stack``s.
        :param outdir: The output directory into which to emit synthesized artifacts. Can only be specified if this stage is the root stage (the app). If this is specified and this stage is nested within another stage, an error will be thrown. Default: - for nested stages, outdir will be determined as a relative directory to the outdir of the app. For apps, if outdir is not specified, a temporary directory will be created.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param policy_validation_beta1: Validation plugins to run during synthesis. If any plugin reports any violation, synthesis will be interrupted and the report displayed to the user. Default: - no validation plugins are used
        :param stage_name: Name of this stage. Default: - Derived from the id.
        :param context_file: The filesystem path to a JSON file that contains context values to load. Using this property allows you to load different context values within each Stage, directly from a file you can check into source control.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__277bf43d40bebd128d971cb569404cd830e470eabdf722b84fcad858785a344e)
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument policy_validation_beta1", value=policy_validation_beta1, expected_type=type_hints["policy_validation_beta1"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument context_file", value=context_file, expected_type=type_hints["context_file"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if env is not None:
            self._values["env"] = env
        if outdir is not None:
            self._values["outdir"] = outdir
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if policy_validation_beta1 is not None:
            self._values["policy_validation_beta1"] = policy_validation_beta1
        if stage_name is not None:
            self._values["stage_name"] = stage_name
        if context_file is not None:
            self._values["context_file"] = context_file

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''Default AWS environment (account/region) for ``Stack``s in this ``Stage``.

        Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing
        from its env will use the corresponding field given here.

        If either ``region`` or ``account``is is not configured for ``Stack`` (either on
        the ``Stack`` itself or on the containing ``Stage``), the Stack will be
        *environment-agnostic*.

        Environment-agnostic stacks can be deployed to any environment, may not be
        able to take advantage of all features of the CDK. For example, they will
        not be able to use environmental context lookups, will not automatically
        translate Service Principals to the right format based on the environment's
        AWS partition, and other such enhancements.

        :default: - The environments should be configured on the ``Stack``s.

        Example::

            // Use a concrete account and region to deploy this Stage to
            new Stage(app, 'Stage1', {
              env: { account: '123456789012', region: 'us-east-1' },
            });
            
            // Use the CLI's current credentials to determine the target environment
            new Stage(app, 'Stage2', {
              env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
            });
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''The output directory into which to emit synthesized artifacts.

        Can only be specified if this stage is the root stage (the app). If this is
        specified and this stage is nested within another stage, an error will be
        thrown.

        :default:

        - for nested stages, outdir will be determined as a relative
        directory to the outdir of the app. For apps, if outdir is not specified, a
        temporary directory will be created.
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def policy_validation_beta1(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]]:
        '''Validation plugins to run during synthesis.

        If any plugin reports any violation,
        synthesis will be interrupted and the report displayed to the user.

        :default: - no validation plugins are used
        '''
        result = self._values.get("policy_validation_beta1")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''Name of this stage.

        :default: - Derived from the id.
        '''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context_file(self) -> typing.Optional[builtins.str]:
        '''The filesystem path to a JSON file that contains context values to load.

        Using this property allows you to load different context values within each
        Stage, directly from a file you can check into source control.
        '''
        result = self._values.get("context_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContextLoadingStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DeploymentTierStage(
    ContextLoadingStage,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.DeploymentTierStage",
):
    '''A Stage whose stacks are part of a single deployment tier.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        tier: "Tier",
        add_tag: typing.Optional[builtins.bool] = None,
        context_file: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new DeploymentTierStage.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param tier: The deployment tier.
        :param add_tag: Whether a ``DeploymentTier`` tag is added to nested constructs. Default: - true
        :param context_file: The filesystem path to a JSON file that contains context values to load. Using this property allows you to load different context values within each Stage, directly from a file you can check into source control.
        :param env: Default AWS environment (account/region) for ``Stack``s in this ``Stage``. Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing from its env will use the corresponding field given here. If either ``region`` or ``account``is is not configured for ``Stack`` (either on the ``Stack`` itself or on the containing ``Stage``), the Stack will be *environment-agnostic*. Environment-agnostic stacks can be deployed to any environment, may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups, will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environments should be configured on the ``Stack``s.
        :param outdir: The output directory into which to emit synthesized artifacts. Can only be specified if this stage is the root stage (the app). If this is specified and this stage is nested within another stage, an error will be thrown. Default: - for nested stages, outdir will be determined as a relative directory to the outdir of the app. For apps, if outdir is not specified, a temporary directory will be created.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param policy_validation_beta1: Validation plugins to run during synthesis. If any plugin reports any violation, synthesis will be interrupted and the report displayed to the user. Default: - no validation plugins are used
        :param stage_name: Name of this stage. Default: - Derived from the id.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f9a764490bae5a194e32e533087b38ed7fd9f77f0cf0c41a14406ab48f535ac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DeploymentTierStageProps(
            tier=tier,
            add_tag=add_tag,
            context_file=context_file,
            env=env,
            outdir=outdir,
            permissions_boundary=permissions_boundary,
            policy_validation_beta1=policy_validation_beta1,
            stage_name=stage_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="inProduction")
    def in_production(self) -> builtins.bool:
        '''Whether this stage is considered a production deployment.'''
        return typing.cast(builtins.bool, jsii.get(self, "inProduction"))

    @builtins.property
    @jsii.member(jsii_name="tier")
    def tier(self) -> "Tier":
        return typing.cast("Tier", jsii.get(self, "tier"))


@jsii.data_type(
    jsii_type="shady-island.DeploymentTierStageProps",
    jsii_struct_bases=[ContextLoadingStageProps],
    name_mapping={
        "env": "env",
        "outdir": "outdir",
        "permissions_boundary": "permissionsBoundary",
        "policy_validation_beta1": "policyValidationBeta1",
        "stage_name": "stageName",
        "context_file": "contextFile",
        "tier": "tier",
        "add_tag": "addTag",
    },
)
class DeploymentTierStageProps(ContextLoadingStageProps):
    def __init__(
        self,
        *,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        stage_name: typing.Optional[builtins.str] = None,
        context_file: typing.Optional[builtins.str] = None,
        tier: "Tier",
        add_tag: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructor properties for DeploymentTierStage.

        :param env: Default AWS environment (account/region) for ``Stack``s in this ``Stage``. Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing from its env will use the corresponding field given here. If either ``region`` or ``account``is is not configured for ``Stack`` (either on the ``Stack`` itself or on the containing ``Stage``), the Stack will be *environment-agnostic*. Environment-agnostic stacks can be deployed to any environment, may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups, will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environments should be configured on the ``Stack``s.
        :param outdir: The output directory into which to emit synthesized artifacts. Can only be specified if this stage is the root stage (the app). If this is specified and this stage is nested within another stage, an error will be thrown. Default: - for nested stages, outdir will be determined as a relative directory to the outdir of the app. For apps, if outdir is not specified, a temporary directory will be created.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param policy_validation_beta1: Validation plugins to run during synthesis. If any plugin reports any violation, synthesis will be interrupted and the report displayed to the user. Default: - no validation plugins are used
        :param stage_name: Name of this stage. Default: - Derived from the id.
        :param context_file: The filesystem path to a JSON file that contains context values to load. Using this property allows you to load different context values within each Stage, directly from a file you can check into source control.
        :param tier: The deployment tier.
        :param add_tag: Whether a ``DeploymentTier`` tag is added to nested constructs. Default: - true
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5542255303c0108ee3ba400c22bcd0da4bf25b7393c820287f49f7738999e86b)
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument policy_validation_beta1", value=policy_validation_beta1, expected_type=type_hints["policy_validation_beta1"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument context_file", value=context_file, expected_type=type_hints["context_file"])
            check_type(argname="argument tier", value=tier, expected_type=type_hints["tier"])
            check_type(argname="argument add_tag", value=add_tag, expected_type=type_hints["add_tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "tier": tier,
        }
        if env is not None:
            self._values["env"] = env
        if outdir is not None:
            self._values["outdir"] = outdir
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if policy_validation_beta1 is not None:
            self._values["policy_validation_beta1"] = policy_validation_beta1
        if stage_name is not None:
            self._values["stage_name"] = stage_name
        if context_file is not None:
            self._values["context_file"] = context_file
        if add_tag is not None:
            self._values["add_tag"] = add_tag

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''Default AWS environment (account/region) for ``Stack``s in this ``Stage``.

        Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing
        from its env will use the corresponding field given here.

        If either ``region`` or ``account``is is not configured for ``Stack`` (either on
        the ``Stack`` itself or on the containing ``Stage``), the Stack will be
        *environment-agnostic*.

        Environment-agnostic stacks can be deployed to any environment, may not be
        able to take advantage of all features of the CDK. For example, they will
        not be able to use environmental context lookups, will not automatically
        translate Service Principals to the right format based on the environment's
        AWS partition, and other such enhancements.

        :default: - The environments should be configured on the ``Stack``s.

        Example::

            // Use a concrete account and region to deploy this Stage to
            new Stage(app, 'Stage1', {
              env: { account: '123456789012', region: 'us-east-1' },
            });
            
            // Use the CLI's current credentials to determine the target environment
            new Stage(app, 'Stage2', {
              env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
            });
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''The output directory into which to emit synthesized artifacts.

        Can only be specified if this stage is the root stage (the app). If this is
        specified and this stage is nested within another stage, an error will be
        thrown.

        :default:

        - for nested stages, outdir will be determined as a relative
        directory to the outdir of the app. For apps, if outdir is not specified, a
        temporary directory will be created.
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def policy_validation_beta1(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]]:
        '''Validation plugins to run during synthesis.

        If any plugin reports any violation,
        synthesis will be interrupted and the report displayed to the user.

        :default: - no validation plugins are used
        '''
        result = self._values.get("policy_validation_beta1")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''Name of this stage.

        :default: - Derived from the id.
        '''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context_file(self) -> typing.Optional[builtins.str]:
        '''The filesystem path to a JSON file that contains context values to load.

        Using this property allows you to load different context values within each
        Stage, directly from a file you can check into source control.
        '''
        result = self._values.get("context_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tier(self) -> "Tier":
        '''The deployment tier.'''
        result = self._values.get("tier")
        assert result is not None, "Required property 'tier' is missing"
        return typing.cast("Tier", result)

    @builtins.property
    def add_tag(self) -> typing.Optional[builtins.bool]:
        '''Whether a ``DeploymentTier`` tag is added to nested constructs.

        :default: - true
        '''
        result = self._values.get("add_tag")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeploymentTierStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.EncryptedFileSystemProps",
    jsii_struct_bases=[_aws_cdk_aws_efs_ceddda9d.FileSystemProps],
    name_mapping={
        "vpc": "vpc",
        "allow_anonymous_access": "allowAnonymousAccess",
        "enable_automatic_backups": "enableAutomaticBackups",
        "encrypted": "encrypted",
        "file_system_name": "fileSystemName",
        "file_system_policy": "fileSystemPolicy",
        "kms_key": "kmsKey",
        "lifecycle_policy": "lifecyclePolicy",
        "one_zone": "oneZone",
        "out_of_infrequent_access_policy": "outOfInfrequentAccessPolicy",
        "performance_mode": "performanceMode",
        "provisioned_throughput_per_second": "provisionedThroughputPerSecond",
        "removal_policy": "removalPolicy",
        "replication_configuration": "replicationConfiguration",
        "replication_overwrite_protection": "replicationOverwriteProtection",
        "security_group": "securityGroup",
        "throughput_mode": "throughputMode",
        "transition_to_archive_policy": "transitionToArchivePolicy",
        "vpc_subnets": "vpcSubnets",
    },
)
class EncryptedFileSystemProps(_aws_cdk_aws_efs_ceddda9d.FileSystemProps):
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_anonymous_access: typing.Optional[builtins.bool] = None,
        enable_automatic_backups: typing.Optional[builtins.bool] = None,
        encrypted: typing.Optional[builtins.bool] = None,
        file_system_name: typing.Optional[builtins.str] = None,
        file_system_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lifecycle_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
        one_zone: typing.Optional[builtins.bool] = None,
        out_of_infrequent_access_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy] = None,
        performance_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode] = None,
        provisioned_throughput_per_second: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_configuration: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationConfiguration] = None,
        replication_overwrite_protection: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        throughput_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode] = None,
        transition_to_archive_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Constructor parameters for EncryptedFileSystem.

        The ``encrypted`` argument is ignored.

        :param vpc: VPC to launch the file system in.
        :param allow_anonymous_access: Allow access from anonymous client that doesn't use IAM authentication. Default: false when using ``grantRead``, ``grantWrite``, ``grantRootAccess`` or set ``@aws-cdk/aws-efs:denyAnonymousAccess`` feature flag, otherwise true
        :param enable_automatic_backups: Whether to enable automatic backups for the file system. Default: false
        :param encrypted: Defines if the data at rest in the file system is encrypted or not. Default: - If your application has the '@aws-cdk/aws-efs:defaultEncryptionAtRest' feature flag set, the default is true, otherwise, the default is false.
        :param file_system_name: The file system's name. Default: - CDK generated name
        :param file_system_policy: File system policy is an IAM resource policy used to control NFS access to an EFS file system. Default: none
        :param kms_key: The KMS key used for encryption. This is required to encrypt the data at rest if Default: - if 'encrypted' is true, the default key for EFS (/aws/elasticfilesystem) is used
        :param lifecycle_policy: A policy used by EFS lifecycle management to transition files to the Infrequent Access (IA) storage class. Default: - None. EFS will not transition files to the IA storage class.
        :param one_zone: Whether this is a One Zone file system. If enabled, ``performanceMode`` must be set to ``GENERAL_PURPOSE`` and ``vpcSubnets`` cannot be set. Default: false
        :param out_of_infrequent_access_policy: A policy used by EFS lifecycle management to transition files from Infrequent Access (IA) storage class to primary storage class. Default: - None. EFS will not transition files from IA storage to primary storage.
        :param performance_mode: The performance mode that the file system will operate under. An Amazon EFS file system's performance mode can't be changed after the file system has been created. Updating this property will replace the file system. Default: PerformanceMode.GENERAL_PURPOSE
        :param provisioned_throughput_per_second: Provisioned throughput for the file system. This is a required property if the throughput mode is set to PROVISIONED. Must be at least 1MiB/s. Default: - none, errors out
        :param removal_policy: The removal policy to apply to the file system. Default: RemovalPolicy.RETAIN
        :param replication_configuration: Replication configuration for the file system. Default: - no replication
        :param replication_overwrite_protection: Whether to enable the filesystem's replication overwrite protection or not. Set false if you want to create a read-only filesystem for use as a replication destination. Default: ReplicationOverwriteProtection.ENABLED
        :param security_group: Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic
        :param throughput_mode: Enum to mention the throughput mode of the file system. Default: ThroughputMode.BURSTING
        :param transition_to_archive_policy: The number of days after files were last accessed in primary storage (the Standard storage class) at which to move them to Archive storage. Metadata operations such as listing the contents of a directory don't count as file access events. Default: - None. EFS will not transition files to Archive storage class.
        :param vpc_subnets: Which subnets to place the mount target in the VPC. Default: - the Vpc default strategy if not specified
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fd1576cc635c21f66d4c77cc0746612de310b047b380081961173028162c533)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument allow_anonymous_access", value=allow_anonymous_access, expected_type=type_hints["allow_anonymous_access"])
            check_type(argname="argument enable_automatic_backups", value=enable_automatic_backups, expected_type=type_hints["enable_automatic_backups"])
            check_type(argname="argument encrypted", value=encrypted, expected_type=type_hints["encrypted"])
            check_type(argname="argument file_system_name", value=file_system_name, expected_type=type_hints["file_system_name"])
            check_type(argname="argument file_system_policy", value=file_system_policy, expected_type=type_hints["file_system_policy"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument lifecycle_policy", value=lifecycle_policy, expected_type=type_hints["lifecycle_policy"])
            check_type(argname="argument one_zone", value=one_zone, expected_type=type_hints["one_zone"])
            check_type(argname="argument out_of_infrequent_access_policy", value=out_of_infrequent_access_policy, expected_type=type_hints["out_of_infrequent_access_policy"])
            check_type(argname="argument performance_mode", value=performance_mode, expected_type=type_hints["performance_mode"])
            check_type(argname="argument provisioned_throughput_per_second", value=provisioned_throughput_per_second, expected_type=type_hints["provisioned_throughput_per_second"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument replication_configuration", value=replication_configuration, expected_type=type_hints["replication_configuration"])
            check_type(argname="argument replication_overwrite_protection", value=replication_overwrite_protection, expected_type=type_hints["replication_overwrite_protection"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument throughput_mode", value=throughput_mode, expected_type=type_hints["throughput_mode"])
            check_type(argname="argument transition_to_archive_policy", value=transition_to_archive_policy, expected_type=type_hints["transition_to_archive_policy"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if allow_anonymous_access is not None:
            self._values["allow_anonymous_access"] = allow_anonymous_access
        if enable_automatic_backups is not None:
            self._values["enable_automatic_backups"] = enable_automatic_backups
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if file_system_name is not None:
            self._values["file_system_name"] = file_system_name
        if file_system_policy is not None:
            self._values["file_system_policy"] = file_system_policy
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if lifecycle_policy is not None:
            self._values["lifecycle_policy"] = lifecycle_policy
        if one_zone is not None:
            self._values["one_zone"] = one_zone
        if out_of_infrequent_access_policy is not None:
            self._values["out_of_infrequent_access_policy"] = out_of_infrequent_access_policy
        if performance_mode is not None:
            self._values["performance_mode"] = performance_mode
        if provisioned_throughput_per_second is not None:
            self._values["provisioned_throughput_per_second"] = provisioned_throughput_per_second
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if replication_configuration is not None:
            self._values["replication_configuration"] = replication_configuration
        if replication_overwrite_protection is not None:
            self._values["replication_overwrite_protection"] = replication_overwrite_protection
        if security_group is not None:
            self._values["security_group"] = security_group
        if throughput_mode is not None:
            self._values["throughput_mode"] = throughput_mode
        if transition_to_archive_policy is not None:
            self._values["transition_to_archive_policy"] = transition_to_archive_policy
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''VPC to launch the file system in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def allow_anonymous_access(self) -> typing.Optional[builtins.bool]:
        '''Allow access from anonymous client that doesn't use IAM authentication.

        :default:

        false when using ``grantRead``, ``grantWrite``, ``grantRootAccess``
        or set ``@aws-cdk/aws-efs:denyAnonymousAccess`` feature flag, otherwise true
        '''
        result = self._values.get("allow_anonymous_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_automatic_backups(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable automatic backups for the file system.

        :default: false
        '''
        result = self._values.get("enable_automatic_backups")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encrypted(self) -> typing.Optional[builtins.bool]:
        '''Defines if the data at rest in the file system is encrypted or not.

        :default: - If your application has the '@aws-cdk/aws-efs:defaultEncryptionAtRest' feature flag set, the default is true, otherwise, the default is false.

        :link: https://docs.aws.amazon.com/cdk/latest/guide/featureflags.html
        '''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def file_system_name(self) -> typing.Optional[builtins.str]:
        '''The file system's name.

        :default: - CDK generated name
        '''
        result = self._values.get("file_system_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_system_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''File system policy is an IAM resource policy used to control NFS access to an EFS file system.

        :default: none
        '''
        result = self._values.get("file_system_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key used for encryption.

        This is required to encrypt the data at rest if

        :default: - if 'encrypted' is true, the default key for EFS (/aws/elasticfilesystem) is used

        :encrypted: is set to true.
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def lifecycle_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy]:
        '''A policy used by EFS lifecycle management to transition files to the Infrequent Access (IA) storage class.

        :default: - None. EFS will not transition files to the IA storage class.
        '''
        result = self._values.get("lifecycle_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy], result)

    @builtins.property
    def one_zone(self) -> typing.Optional[builtins.bool]:
        '''Whether this is a One Zone file system.

        If enabled, ``performanceMode`` must be set to ``GENERAL_PURPOSE`` and ``vpcSubnets`` cannot be set.

        :default: false

        :link: https://docs.aws.amazon.com/efs/latest/ug/availability-durability.html#file-system-type
        '''
        result = self._values.get("one_zone")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def out_of_infrequent_access_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy]:
        '''A policy used by EFS lifecycle management to transition files from Infrequent Access (IA) storage class to primary storage class.

        :default: - None. EFS will not transition files from IA storage to primary storage.
        '''
        result = self._values.get("out_of_infrequent_access_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy], result)

    @builtins.property
    def performance_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode]:
        '''The performance mode that the file system will operate under.

        An Amazon EFS file system's performance mode can't be changed after the file system has been created.
        Updating this property will replace the file system.

        :default: PerformanceMode.GENERAL_PURPOSE
        '''
        result = self._values.get("performance_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode], result)

    @builtins.property
    def provisioned_throughput_per_second(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''Provisioned throughput for the file system.

        This is a required property if the throughput mode is set to PROVISIONED.
        Must be at least 1MiB/s.

        :default: - none, errors out
        '''
        result = self._values.get("provisioned_throughput_per_second")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply to the file system.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def replication_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationConfiguration]:
        '''Replication configuration for the file system.

        :default: - no replication
        '''
        result = self._values.get("replication_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationConfiguration], result)

    @builtins.property
    def replication_overwrite_protection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection]:
        '''Whether to enable the filesystem's replication overwrite protection or not.

        Set false if you want to create a read-only filesystem for use as a replication destination.

        :default: ReplicationOverwriteProtection.ENABLED

        :see: https://docs.aws.amazon.com/efs/latest/ug/replication-use-cases.html#replicate-existing-destination
        '''
        result = self._values.get("replication_overwrite_protection")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''Security Group to assign to this file system.

        :default: - creates new security group which allows all outbound traffic
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def throughput_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode]:
        '''Enum to mention the throughput mode of the file system.

        :default: ThroughputMode.BURSTING
        '''
        result = self._values.get("throughput_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode], result)

    @builtins.property
    def transition_to_archive_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy]:
        '''The number of days after files were last accessed in primary storage (the Standard storage class) at which to move them to Archive storage.

        Metadata operations such as listing the contents of a directory don't count as file access events.

        :default: - None. EFS will not transition files to Archive storage class.
        '''
        result = self._values.get("transition_to_archive_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Which subnets to place the mount target in the VPC.

        :default: - the Vpc default strategy if not specified
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptedFileSystemProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.EncryptedLogGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "log_group_name": "logGroupName",
        "encryption_key": "encryptionKey",
        "removal_policy": "removalPolicy",
        "retention": "retention",
    },
)
class EncryptedLogGroupProps:
    def __init__(
        self,
        *,
        log_group_name: builtins.str,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''Constructor properties for EncryptedLogGroup.

        :param log_group_name: Name of the log group. We need a log group name ahead of time because otherwise the key policy would create a cyclical dependency.
        :param encryption_key: The KMS Key to encrypt the log group with. Default: A new KMS key will be created
        :param removal_policy: Whether the key and group should be retained when they are removed from the Stack. Default: RemovalPolicy.RETAIN
        :param retention: How long, in days, the log contents will be retained. Default: RetentionDays.TWO_YEARS
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__336d3d15e4b6b1d5a3f1d25302a1b6aa54f3525152e85c4efc9022074bbc84ef)
            check_type(argname="argument log_group_name", value=log_group_name, expected_type=type_hints["log_group_name"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument retention", value=retention, expected_type=type_hints["retention"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "log_group_name": log_group_name,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if retention is not None:
            self._values["retention"] = retention

    @builtins.property
    def log_group_name(self) -> builtins.str:
        '''Name of the log group.

        We need a log group name ahead of time because otherwise the key policy
        would create a cyclical dependency.
        '''
        result = self._values.get("log_group_name")
        assert result is not None, "Required property 'log_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key to encrypt the log group with.

        :default: A new KMS key will be created
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Whether the key and group should be retained when they are removed from the Stack.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def retention(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''How long, in days, the log contents will be retained.

        :default: RetentionDays.TWO_YEARS
        '''
        result = self._values.get("retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptedLogGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.EventTargetProps",
    jsii_struct_bases=[_aws_cdk_aws_events_targets_ceddda9d.TargetBaseProps],
    name_mapping={
        "dead_letter_queue": "deadLetterQueue",
        "max_event_age": "maxEventAge",
        "retry_attempts": "retryAttempts",
        "container_overrides": "containerOverrides",
        "enable_execute_command": "enableExecuteCommand",
        "launch_type": "launchType",
        "propagate_tags": "propagateTags",
        "role": "role",
        "tags": "tags",
        "task_count": "taskCount",
    },
)
class EventTargetProps(_aws_cdk_aws_events_targets_ceddda9d.TargetBaseProps):
    def __init__(
        self,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        launch_type: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LaunchType] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.Tag, typing.Dict[builtins.str, typing.Any]]]] = None,
        task_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties to create a new EventBridge Rule Target.

        :param dead_letter_queue: The SQS queue to be used as deadLetterQueue. Check out the `considerations for using a dead-letter queue <https://docs.aws.amazon.com/eventbridge/latest/userguide/rule-dlq.html#dlq-considerations>`_. The events not successfully delivered are automatically retried for a specified period of time, depending on the retry policy of the target. If an event is not delivered before all retry attempts are exhausted, it will be sent to the dead letter queue. Default: - no dead-letter queue
        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum value of 60. Maximum value of 86400. Default: Duration.hours(24)
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum value of 0. Maximum value of 185. Default: 185
        :param container_overrides: Container setting overrides. Key is the name of the container to override, value is the values you want to override.
        :param enable_execute_command: Whether or not to enable the execute command functionality for the containers in this task. If true, this enables execute command functionality on all containers in the task. Default: - false
        :param launch_type: Specifies the launch type on which your task is running. The launch type that you specify here must match one of the launch type (compatibilities) of the target task. Default: - 'EC2' if ``isEc2Compatible`` for the ``taskDefinition`` is true, otherwise 'FARGATE'
        :param propagate_tags: Specifies whether to propagate the tags from the task definition to the task. If no value is specified, the tags are not propagated. Default: - Tags will not be propagated
        :param role: Existing IAM role to run the ECS task. Default: - A new IAM role is created
        :param tags: The metadata that you apply to the task to help you categorize and organize them. Each tag consists of a key and an optional value, both of which you define. Default: - No additional tags are applied to the task
        :param task_count: How many tasks should be started when this event is triggered. Default: - 1
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__897dc07b48a2eb17398fb35f77b60b5ef5a46dc3283b5be7f1587d908f9d4f1a)
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument max_event_age", value=max_event_age, expected_type=type_hints["max_event_age"])
            check_type(argname="argument retry_attempts", value=retry_attempts, expected_type=type_hints["retry_attempts"])
            check_type(argname="argument container_overrides", value=container_overrides, expected_type=type_hints["container_overrides"])
            check_type(argname="argument enable_execute_command", value=enable_execute_command, expected_type=type_hints["enable_execute_command"])
            check_type(argname="argument launch_type", value=launch_type, expected_type=type_hints["launch_type"])
            check_type(argname="argument propagate_tags", value=propagate_tags, expected_type=type_hints["propagate_tags"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument task_count", value=task_count, expected_type=type_hints["task_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if max_event_age is not None:
            self._values["max_event_age"] = max_event_age
        if retry_attempts is not None:
            self._values["retry_attempts"] = retry_attempts
        if container_overrides is not None:
            self._values["container_overrides"] = container_overrides
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if launch_type is not None:
            self._values["launch_type"] = launch_type
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if role is not None:
            self._values["role"] = role
        if tags is not None:
            self._values["tags"] = tags
        if task_count is not None:
            self._values["task_count"] = task_count

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue]:
        '''The SQS queue to be used as deadLetterQueue. Check out the `considerations for using a dead-letter queue <https://docs.aws.amazon.com/eventbridge/latest/userguide/rule-dlq.html#dlq-considerations>`_.

        The events not successfully delivered are automatically retried for a specified period of time,
        depending on the retry policy of the target.
        If an event is not delivered before all retry attempts are exhausted, it will be sent to the dead letter queue.

        :default: - no dead-letter queue
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue], result)

    @builtins.property
    def max_event_age(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum age of a request that Lambda sends to a function for processing.

        Minimum value of 60.
        Maximum value of 86400.

        :default: Duration.hours(24)
        '''
        result = self._values.get("max_event_age")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times to retry when the function returns an error.

        Minimum value of 0.
        Maximum value of 185.

        :default: 185
        '''
        result = self._values.get("retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def container_overrides(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_targets_ceddda9d.ContainerOverride]]:
        '''Container setting overrides.

        Key is the name of the container to override, value is the
        values you want to override.
        '''
        result = self._values.get("container_overrides")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_targets_ceddda9d.ContainerOverride]], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable the execute command functionality for the containers in this task.

        If true, this enables execute command functionality on all containers in the task.

        :default: - false
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def launch_type(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LaunchType]:
        '''Specifies the launch type on which your task is running.

        The launch type that you specify here
        must match one of the launch type (compatibilities) of the target task.

        :default: - 'EC2' if ``isEc2Compatible`` for the ``taskDefinition`` is true, otherwise 'FARGATE'
        '''
        result = self._values.get("launch_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LaunchType], result)

    @builtins.property
    def propagate_tags(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource]:
        '''Specifies whether to propagate the tags from the task definition to the task.

        If no value is specified, the tags are not propagated.

        :default: - Tags will not be propagated
        '''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Existing IAM role to run the ECS task.

        :default: - A new IAM role is created
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_targets_ceddda9d.Tag]]:
        '''The metadata that you apply to the task to help you categorize and organize them.

        Each tag consists of a key and an optional value, both of which you define.

        :default: - No additional tags are applied to the task
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_targets_ceddda9d.Tag]], result)

    @builtins.property
    def task_count(self) -> typing.Optional[jsii.Number]:
        '''How many tasks should be started when this event is triggered.

        :default: - 1
        '''
        result = self._values.get("task_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventTargetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.FargateAwsVpcConfiguration",
    jsii_struct_bases=[
        _aws_cdk_aws_ecs_ceddda9d.CfnService.AwsVpcConfigurationProperty
    ],
    name_mapping={
        "assign_public_ip": "assignPublicIp",
        "security_groups": "securityGroups",
        "subnets": "subnets",
    },
)
class FargateAwsVpcConfiguration(
    _aws_cdk_aws_ecs_ceddda9d.CfnService.AwsVpcConfigurationProperty,
):
    def __init__(
        self,
        *,
        assign_public_ip: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''The ``networkConfiguration.awsvpcConfiguration`` values for ``ecs.RunTask``.

        :param assign_public_ip: Whether the task's elastic network interface receives a public IP address. The default value is ``ENABLED`` .
        :param security_groups: The IDs of the security groups associated with the task or service. If you don't specify a security group, the default security group for the VPC is used. There's a limit of 5 security groups that can be specified. .. epigraph:: All specified security groups must be from the same VPC.
        :param subnets: The IDs of the subnets associated with the task or service. There's a limit of 16 subnets that can be specified. .. epigraph:: All specified subnets must be from the same VPC.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51c80a2d906cd1addfd30d9a8ba48b35ba0ff6bcdacdd5b465c97943ae8633de)
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnets is not None:
            self._values["subnets"] = subnets

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.str]:
        '''Whether the task's elastic network interface receives a public IP address.

        The default value is ``ENABLED`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-awsvpcconfiguration.html#cfn-ecs-service-awsvpcconfiguration-assignpublicip
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The IDs of the security groups associated with the task or service.

        If you don't specify a security group, the default security group for the VPC is used. There's a limit of 5 security groups that can be specified.
        .. epigraph::

           All specified security groups must be from the same VPC.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-awsvpcconfiguration.html#cfn-ecs-service-awsvpcconfiguration-securitygroups
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subnets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The IDs of the subnets associated with the task or service.

        There's a limit of 16 subnets that can be specified.
        .. epigraph::

           All specified subnets must be from the same VPC.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-awsvpcconfiguration.html#cfn-ecs-service-awsvpcconfiguration-subnets
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateAwsVpcConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.FargateTaskImageOptions",
    jsii_struct_bases=[
        _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions
    ],
    name_mapping={
        "image": "image",
        "command": "command",
        "container_name": "containerName",
        "container_port": "containerPort",
        "docker_labels": "dockerLabels",
        "enable_logging": "enableLogging",
        "entry_point": "entryPoint",
        "environment": "environment",
        "execution_role": "executionRole",
        "family": "family",
        "log_driver": "logDriver",
        "secrets": "secrets",
        "task_role": "taskRole",
    },
)
class FargateTaskImageOptions(
    _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions,
):
    def __init__(
        self,
        *,
        image: _aws_cdk_aws_ecs_ceddda9d.ContainerImage,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        container_name: typing.Optional[builtins.str] = None,
        container_port: typing.Optional[jsii.Number] = None,
        docker_labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        entry_point: typing.Optional[typing.Sequence[builtins.str]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        family: typing.Optional[builtins.str] = None,
        log_driver: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]] = None,
        task_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''The properties for the FargateTask using an image.

        :param image: The image used to start a container. Image or taskDefinition must be specified, not both. Default: - none
        :param command: The command that's passed to the container. If there are multiple arguments, make sure that each argument is a separated string in the array. This parameter maps to ``Cmd`` in the `Create a container <https://docs.docker.com/engine/api/v1.38/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.docker.com/engine/api/v1.38/>`_ and the ``COMMAND`` parameter to `docker run <https://docs.docker.com/engine/reference/commandline/run/>`_. For more information about the Docker ``CMD`` parameter, see https://docs.docker.com/engine/reference/builder/#cmd. Default: none
        :param container_name: The container name value to be specified in the task definition. Default: - none
        :param container_port: The port number on the container that is bound to the user-specified or automatically assigned host port. If you are using containers in a task with the awsvpc or host network mode, exposed ports should be specified using containerPort. If you are using containers in a task with the bridge network mode and you specify a container port and not a host port, your container automatically receives a host port in the ephemeral port range. Port mappings that are automatically assigned in this way do not count toward the 100 reserved ports limit of a container instance. For more information, see `hostPort <https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_PortMapping.html#ECS-Type-PortMapping-hostPort>`_. Default: 80
        :param docker_labels: A key/value map of labels to add to the container. Default: - No labels.
        :param enable_logging: Flag to indicate whether to enable logging. Default: true
        :param entry_point: The entry point that's passed to the container. This parameter maps to ``Entrypoint`` in the `Create a container <https://docs.docker.com/engine/api/v1.38/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.docker.com/engine/api/v1.38/>`_ and the ``--entrypoint`` option to `docker run <https://docs.docker.com/engine/reference/commandline/run/>`_. For more information about the Docker ``ENTRYPOINT`` parameter, see https://docs.docker.com/engine/reference/builder/#entrypoint. Default: none
        :param environment: The environment variables to pass to the container. Default: - No environment variables.
        :param execution_role: The name of the task execution IAM role that grants the Amazon ECS container agent permission to call AWS APIs on your behalf. Default: - No value
        :param family: The name of a family that this task definition is registered to. A family groups multiple versions of a task definition. Default: - Automatically generated name.
        :param log_driver: The log driver to use. Default: - AwsLogDriver if enableLogging is true
        :param secrets: The secret to expose to the container as an environment variable. Default: - No secret environment variables.
        :param task_role: The name of the task IAM role that grants containers in the task permission to call AWS APIs on your behalf. Default: - A task role is automatically created for you.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09105b6ea9eae34595c8cb0f3710694a2e074d2c7f093bb2ddc1d83da13a547d)
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument command", value=command, expected_type=type_hints["command"])
            check_type(argname="argument container_name", value=container_name, expected_type=type_hints["container_name"])
            check_type(argname="argument container_port", value=container_port, expected_type=type_hints["container_port"])
            check_type(argname="argument docker_labels", value=docker_labels, expected_type=type_hints["docker_labels"])
            check_type(argname="argument enable_logging", value=enable_logging, expected_type=type_hints["enable_logging"])
            check_type(argname="argument entry_point", value=entry_point, expected_type=type_hints["entry_point"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument family", value=family, expected_type=type_hints["family"])
            check_type(argname="argument log_driver", value=log_driver, expected_type=type_hints["log_driver"])
            check_type(argname="argument secrets", value=secrets, expected_type=type_hints["secrets"])
            check_type(argname="argument task_role", value=task_role, expected_type=type_hints["task_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "image": image,
        }
        if command is not None:
            self._values["command"] = command
        if container_name is not None:
            self._values["container_name"] = container_name
        if container_port is not None:
            self._values["container_port"] = container_port
        if docker_labels is not None:
            self._values["docker_labels"] = docker_labels
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if entry_point is not None:
            self._values["entry_point"] = entry_point
        if environment is not None:
            self._values["environment"] = environment
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if family is not None:
            self._values["family"] = family
        if log_driver is not None:
            self._values["log_driver"] = log_driver
        if secrets is not None:
            self._values["secrets"] = secrets
        if task_role is not None:
            self._values["task_role"] = task_role

    @builtins.property
    def image(self) -> _aws_cdk_aws_ecs_ceddda9d.ContainerImage:
        '''The image used to start a container.

        Image or taskDefinition must be specified, not both.

        :default: - none
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ContainerImage, result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The command that's passed to the container.

        If there are multiple arguments, make sure that each argument is a separated string in the array.

        This parameter maps to ``Cmd`` in the `Create a container <https://docs.docker.com/engine/api/v1.38/#operation/ContainerCreate>`_ section
        of the `Docker Remote API <https://docs.docker.com/engine/api/v1.38/>`_ and the ``COMMAND`` parameter to
        `docker run <https://docs.docker.com/engine/reference/commandline/run/>`_.

        For more information about the Docker ``CMD`` parameter, see https://docs.docker.com/engine/reference/builder/#cmd.

        :default: none
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def container_name(self) -> typing.Optional[builtins.str]:
        '''The container name value to be specified in the task definition.

        :default: - none
        '''
        result = self._values.get("container_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def container_port(self) -> typing.Optional[jsii.Number]:
        '''The port number on the container that is bound to the user-specified or automatically assigned host port.

        If you are using containers in a task with the awsvpc or host network mode, exposed ports should be specified using containerPort.
        If you are using containers in a task with the bridge network mode and you specify a container port and not a host port,
        your container automatically receives a host port in the ephemeral port range.

        Port mappings that are automatically assigned in this way do not count toward the 100 reserved ports limit of a container instance.

        For more information, see
        `hostPort <https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_PortMapping.html#ECS-Type-PortMapping-hostPort>`_.

        :default: 80
        '''
        result = self._values.get("container_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def docker_labels(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A key/value map of labels to add to the container.

        :default: - No labels.
        '''
        result = self._values.get("docker_labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''Flag to indicate whether to enable logging.

        :default: true
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def entry_point(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The entry point that's passed to the container.

        This parameter maps to ``Entrypoint`` in the `Create a container <https://docs.docker.com/engine/api/v1.38/#operation/ContainerCreate>`_ section
        of the `Docker Remote API <https://docs.docker.com/engine/api/v1.38/>`_ and the ``--entrypoint`` option to
        `docker run <https://docs.docker.com/engine/reference/commandline/run/>`_.

        For more information about the Docker ``ENTRYPOINT`` parameter, see https://docs.docker.com/engine/reference/builder/#entrypoint.

        :default: none
        '''
        result = self._values.get("entry_point")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The environment variables to pass to the container.

        :default: - No environment variables.
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The name of the task execution IAM role that grants the Amazon ECS container agent permission to call AWS APIs on your behalf.

        :default: - No value
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def family(self) -> typing.Optional[builtins.str]:
        '''The name of a family that this task definition is registered to.

        A family groups multiple versions of a task definition.

        :default: - Automatically generated name.
        '''
        result = self._values.get("family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_driver(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver]:
        '''The log driver to use.

        :default: - AwsLogDriver if enableLogging is true
        '''
        result = self._values.get("log_driver")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]]:
        '''The secret to expose to the container as an environment variable.

        :default: - No secret environment variables.
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]], result)

    @builtins.property
    def task_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The name of the task IAM role that grants containers in the task permission to call AWS APIs on your behalf.

        :default: - A task role is automatically created for you.
        '''
        result = self._values.get("task_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateTaskImageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.FargateTaskProps",
    jsii_struct_bases=[BaseFargateTaskProps],
    name_mapping={
        "assign_public_ip": "assignPublicIp",
        "security_groups": "securityGroups",
        "vpc_subnets": "vpcSubnets",
        "cluster": "cluster",
        "task_definition": "taskDefinition",
    },
)
class FargateTaskProps(BaseFargateTaskProps):
    def __init__(
        self,
        *,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        task_definition: _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition,
    ) -> None:
        '''Constructor parameters for FargateTask.

        :param assign_public_ip: Specifies whether the task's elastic network interface receives a public IP address. If true, the task will receive a public IP address. Default: false
        :param security_groups: Existing security groups to use for your task. Default: - a new security group will be created.
        :param vpc_subnets: The subnets to associate with the task. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param cluster: The name of the cluster that hosts the service.
        :param task_definition: The task definition that can be launched.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48906dd5b4e8a7c31ff88ad932bf788d1acda56897daf0ddbd9a63f01a440cb3)
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument task_definition", value=task_definition, expected_type=type_hints["task_definition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "task_definition": task_definition,
        }
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether the task's elastic network interface receives a public IP address.

        If true, the task will receive a public IP address.

        :default: false
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Existing security groups to use for your task.

        :default: - a new security group will be created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets to associate with the task.

        :default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''The name of the cluster that hosts the service.'''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, result)

    @builtins.property
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition:
        '''The task definition that can be launched.'''
        result = self._values.get("task_definition")
        assert result is not None, "Required property 'task_definition' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="shady-island.IAssignOnLaunch")
class IAssignOnLaunch(typing_extensions.Protocol):
    '''Interface for the AssignOnLaunch class.'''

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The IPv6-enabled VPC.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="vpcPlacement")
    def vpc_placement(self) -> _aws_cdk_aws_ec2_ceddda9d.SelectedSubnets:
        '''The chosen subnets for address assignment on ENI launch.'''
        ...


class _IAssignOnLaunchProxy:
    '''Interface for the AssignOnLaunch class.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.IAssignOnLaunch"

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The IPv6-enabled VPC.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="vpcPlacement")
    def vpc_placement(self) -> _aws_cdk_aws_ec2_ceddda9d.SelectedSubnets:
        '''The chosen subnets for address assignment on ENI launch.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, jsii.get(self, "vpcPlacement"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAssignOnLaunch).__jsii_proxy_class__ = lambda : _IAssignOnLaunchProxy


@jsii.interface(jsii_type="shady-island.ICidrContext")
class ICidrContext(typing_extensions.Protocol):
    '''Interface for the CidrContext class.'''

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The IPv6-enabled VPC.'''
        ...


class _ICidrContextProxy:
    '''Interface for the CidrContext class.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.ICidrContext"

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The IPv6-enabled VPC.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICidrContext).__jsii_proxy_class__ = lambda : _ICidrContextProxy


@jsii.interface(jsii_type="shady-island.IDatabase")
class IDatabase(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''The definition used to create a database.'''

    @builtins.property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''The cluster or instance endpoint.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> _aws_cdk_triggers_ceddda9d.ITrigger:
        '''The CDK Trigger that kicks off the process.

        You can further customize when the trigger fires using ``executeAfter``.
        '''
        ...

    @jsii.member(jsii_name="addUserAsOwner")
    def add_user_as_owner(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned ownership permissions.

        :param secret: - The Secrets Manager secret containing credentials.
        '''
        ...

    @jsii.member(jsii_name="addUserAsReader")
    def add_user_as_reader(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned read-only permissions.

        :param secret: - The Secrets Manager secret containing credentials.
        '''
        ...

    @jsii.member(jsii_name="addUserAsUnprivileged")
    def add_user_as_unprivileged(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user with no permissions.

        :param secret: - The Secrets Manager secret containing credentials.
        '''
        ...


class _IDatabaseProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''The definition used to create a database.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.IDatabase"

    @builtins.property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog.'''
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''The cluster or instance endpoint.'''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> _aws_cdk_triggers_ceddda9d.ITrigger:
        '''The CDK Trigger that kicks off the process.

        You can further customize when the trigger fires using ``executeAfter``.
        '''
        return typing.cast(_aws_cdk_triggers_ceddda9d.ITrigger, jsii.get(self, "trigger"))

    @jsii.member(jsii_name="addUserAsOwner")
    def add_user_as_owner(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned ownership permissions.

        :param secret: - The Secrets Manager secret containing credentials.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa04cb10e6d6f3a14885b573c1500a16f427d23d29420c9282c7b47bf510a8d5)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsOwner", [secret]))

    @jsii.member(jsii_name="addUserAsReader")
    def add_user_as_reader(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned read-only permissions.

        :param secret: - The Secrets Manager secret containing credentials.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3afa465271b9422d8a26592c854f527c297eff5926d505012bdcd9c9c73a12c2)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsReader", [secret]))

    @jsii.member(jsii_name="addUserAsUnprivileged")
    def add_user_as_unprivileged(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user with no permissions.

        :param secret: - The Secrets Manager secret containing credentials.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85cd5b491150e098fe53def9ea0f1c89f9845fb5fd9030a27ecc6148e091c23b)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsUnprivileged", [secret]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDatabase).__jsii_proxy_class__ = lambda : _IDatabaseProxy


@jsii.interface(jsii_type="shady-island.IEncryptedFileSystem")
class IEncryptedFileSystem(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''Interface for EncryptedFileSystem.'''

    @builtins.property
    @jsii.member(jsii_name="fileSystem")
    def file_system(self) -> _aws_cdk_aws_efs_ceddda9d.IFileSystem:
        '''The EFS file system.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS encryption key.'''
        ...


class _IEncryptedFileSystemProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''Interface for EncryptedFileSystem.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.IEncryptedFileSystem"

    @builtins.property
    @jsii.member(jsii_name="fileSystem")
    def file_system(self) -> _aws_cdk_aws_efs_ceddda9d.IFileSystem:
        '''The EFS file system.'''
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.IFileSystem, jsii.get(self, "fileSystem"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS encryption key.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "key"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEncryptedFileSystem).__jsii_proxy_class__ = lambda : _IEncryptedFileSystemProxy


@jsii.interface(jsii_type="shady-island.IEncryptedLogGroup")
class IEncryptedLogGroup(typing_extensions.Protocol):
    '''A log group encrypted by a KMS customer managed key.'''

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS encryption key.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The log group.'''
        ...


class _IEncryptedLogGroupProxy:
    '''A log group encrypted by a KMS customer managed key.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.IEncryptedLogGroup"

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS encryption key.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The log group.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "logGroup"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEncryptedLogGroup).__jsii_proxy_class__ = lambda : _IEncryptedLogGroupProxy


@jsii.interface(jsii_type="shady-island.IFargateTask")
class IFargateTask(
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    _constructs_77d1e7e8.IConstruct,
    typing_extensions.Protocol,
):
    '''Interface for FargateTask.'''

    @builtins.property
    @jsii.member(jsii_name="awsVpcNetworkConfig")
    def aws_vpc_network_config(self) -> FargateAwsVpcConfiguration:
        '''Get the networkConfiguration.awsvpcConfiguration property to run this task.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''The name of the cluster that hosts the service.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition:
        '''The task definition that can be launched.'''
        ...

    @jsii.member(jsii_name="createRuleTarget")
    def create_rule_target(
        self,
        *,
        container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        launch_type: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LaunchType] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.Tag, typing.Dict[builtins.str, typing.Any]]]] = None,
        task_count: typing.Optional[jsii.Number] = None,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
    ) -> _aws_cdk_aws_events_targets_ceddda9d.EcsTask:
        '''Create a new EventBridge Rule Target that launches this ECS task.

        :param container_overrides: Container setting overrides. Key is the name of the container to override, value is the values you want to override.
        :param enable_execute_command: Whether or not to enable the execute command functionality for the containers in this task. If true, this enables execute command functionality on all containers in the task. Default: - false
        :param launch_type: Specifies the launch type on which your task is running. The launch type that you specify here must match one of the launch type (compatibilities) of the target task. Default: - 'EC2' if ``isEc2Compatible`` for the ``taskDefinition`` is true, otherwise 'FARGATE'
        :param propagate_tags: Specifies whether to propagate the tags from the task definition to the task. If no value is specified, the tags are not propagated. Default: - Tags will not be propagated
        :param role: Existing IAM role to run the ECS task. Default: - A new IAM role is created
        :param tags: The metadata that you apply to the task to help you categorize and organize them. Each tag consists of a key and an optional value, both of which you define. Default: - No additional tags are applied to the task
        :param task_count: How many tasks should be started when this event is triggered. Default: - 1
        :param dead_letter_queue: The SQS queue to be used as deadLetterQueue. Check out the `considerations for using a dead-letter queue <https://docs.aws.amazon.com/eventbridge/latest/userguide/rule-dlq.html#dlq-considerations>`_. The events not successfully delivered are automatically retried for a specified period of time, depending on the retry policy of the target. If an event is not delivered before all retry attempts are exhausted, it will be sent to the dead letter queue. Default: - no dead-letter queue
        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum value of 60. Maximum value of 86400. Default: Duration.hours(24)
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum value of 0. Maximum value of 185. Default: 185
        '''
        ...

    @jsii.member(jsii_name="createStateMachineTask")
    def create_state_machine_task(
        self,
        id: builtins.str,
        *,
        container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        propagated_tag_source: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        revision_number: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.EcsRunTask:
        '''Create a new Step Functions task that launches this ECS task.

        :param id: - The construct ID.
        :param container_overrides: Container setting overrides. Specify the container to use and the overrides to apply. Default: - No overrides
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: false
        :param propagated_tag_source: Specifies whether to propagate the tags from the task definition to the task. An error will be received if you specify the SERVICE option when running a task. Default: - No tags are propagated.
        :param revision_number: The revision number of ECS task definition family. Default: - '$latest'
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        ...

    @jsii.member(jsii_name="grantRun")
    def grant_run(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants permission to invoke ecs:RunTask on this task's cluster.

        :param grantee: - The recipient of the permissions.
        '''
        ...


class _IFargateTaskProxy(
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''Interface for FargateTask.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.IFargateTask"

    @builtins.property
    @jsii.member(jsii_name="awsVpcNetworkConfig")
    def aws_vpc_network_config(self) -> FargateAwsVpcConfiguration:
        '''Get the networkConfiguration.awsvpcConfiguration property to run this task.'''
        return typing.cast(FargateAwsVpcConfiguration, jsii.get(self, "awsVpcNetworkConfig"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''The name of the cluster that hosts the service.'''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition:
        '''The task definition that can be launched.'''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition, jsii.get(self, "taskDefinition"))

    @jsii.member(jsii_name="createRuleTarget")
    def create_rule_target(
        self,
        *,
        container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        launch_type: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LaunchType] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.Tag, typing.Dict[builtins.str, typing.Any]]]] = None,
        task_count: typing.Optional[jsii.Number] = None,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
    ) -> _aws_cdk_aws_events_targets_ceddda9d.EcsTask:
        '''Create a new EventBridge Rule Target that launches this ECS task.

        :param container_overrides: Container setting overrides. Key is the name of the container to override, value is the values you want to override.
        :param enable_execute_command: Whether or not to enable the execute command functionality for the containers in this task. If true, this enables execute command functionality on all containers in the task. Default: - false
        :param launch_type: Specifies the launch type on which your task is running. The launch type that you specify here must match one of the launch type (compatibilities) of the target task. Default: - 'EC2' if ``isEc2Compatible`` for the ``taskDefinition`` is true, otherwise 'FARGATE'
        :param propagate_tags: Specifies whether to propagate the tags from the task definition to the task. If no value is specified, the tags are not propagated. Default: - Tags will not be propagated
        :param role: Existing IAM role to run the ECS task. Default: - A new IAM role is created
        :param tags: The metadata that you apply to the task to help you categorize and organize them. Each tag consists of a key and an optional value, both of which you define. Default: - No additional tags are applied to the task
        :param task_count: How many tasks should be started when this event is triggered. Default: - 1
        :param dead_letter_queue: The SQS queue to be used as deadLetterQueue. Check out the `considerations for using a dead-letter queue <https://docs.aws.amazon.com/eventbridge/latest/userguide/rule-dlq.html#dlq-considerations>`_. The events not successfully delivered are automatically retried for a specified period of time, depending on the retry policy of the target. If an event is not delivered before all retry attempts are exhausted, it will be sent to the dead letter queue. Default: - no dead-letter queue
        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum value of 60. Maximum value of 86400. Default: Duration.hours(24)
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum value of 0. Maximum value of 185. Default: 185
        '''
        props = EventTargetProps(
            container_overrides=container_overrides,
            enable_execute_command=enable_execute_command,
            launch_type=launch_type,
            propagate_tags=propagate_tags,
            role=role,
            tags=tags,
            task_count=task_count,
            dead_letter_queue=dead_letter_queue,
            max_event_age=max_event_age,
            retry_attempts=retry_attempts,
        )

        return typing.cast(_aws_cdk_aws_events_targets_ceddda9d.EcsTask, jsii.invoke(self, "createRuleTarget", [props]))

    @jsii.member(jsii_name="createStateMachineTask")
    def create_state_machine_task(
        self,
        id: builtins.str,
        *,
        container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        propagated_tag_source: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        revision_number: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.EcsRunTask:
        '''Create a new Step Functions task that launches this ECS task.

        :param id: - The construct ID.
        :param container_overrides: Container setting overrides. Specify the container to use and the overrides to apply. Default: - No overrides
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: false
        :param propagated_tag_source: Specifies whether to propagate the tags from the task definition to the task. An error will be received if you specify the SERVICE option when running a task. Default: - No tags are propagated.
        :param revision_number: The revision number of ECS task definition family. Default: - '$latest'
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48c037a9d29925d5cc91f797f5826290b380d79fe3f87a6eda42191172d636cc)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StateMachineTaskProps(
            container_overrides=container_overrides,
            enable_execute_command=enable_execute_command,
            propagated_tag_source=propagated_tag_source,
            revision_number=revision_number,
            comment=comment,
            credentials=credentials,
            heartbeat=heartbeat,
            heartbeat_timeout=heartbeat_timeout,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            state_name=state_name,
            task_timeout=task_timeout,
            timeout=timeout,
        )

        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.EcsRunTask, jsii.invoke(self, "createStateMachineTask", [id, props]))

    @jsii.member(jsii_name="grantRun")
    def grant_run(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants permission to invoke ecs:RunTask on this task's cluster.

        :param grantee: - The recipient of the permissions.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11d3684d379a3f021959b8059e0a87bd5a4301f03fcadfcfeb09484fc5a6ba68)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRun", [grantee]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFargateTask).__jsii_proxy_class__ = lambda : _IFargateTaskProxy


@jsii.interface(jsii_type="shady-island.IRunnableFargateTask")
class IRunnableFargateTask(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''Interface for RunnableFargateTask.'''

    @builtins.property
    @jsii.member(jsii_name="task")
    def task(self) -> IFargateTask:
        '''The FargateTask in this construct.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition:
        '''The FargateTaskDefinition in this construct.'''
        ...


class _IRunnableFargateTaskProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''Interface for RunnableFargateTask.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.IRunnableFargateTask"

    @builtins.property
    @jsii.member(jsii_name="task")
    def task(self) -> IFargateTask:
        '''The FargateTask in this construct.'''
        return typing.cast(IFargateTask, jsii.get(self, "task"))

    @builtins.property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition:
        '''The FargateTaskDefinition in this construct.'''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition, jsii.get(self, "taskDefinition"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRunnableFargateTask).__jsii_proxy_class__ = lambda : _IRunnableFargateTaskProxy


@jsii.data_type(
    jsii_type="shady-island.MysqlDatabaseOptions",
    jsii_struct_bases=[],
    name_mapping={
        "certificate_authorities_url": "certificateAuthoritiesUrl",
        "character_set": "characterSet",
        "collation": "collation",
    },
)
class MysqlDatabaseOptions:
    def __init__(
        self,
        *,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
    ) -> None:
        '''MySQL-specific options.

        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d514adc7950cfce4177d69ffd36ac66492872090c9fd306589f40229c06f7659)
            check_type(argname="argument certificate_authorities_url", value=certificate_authorities_url, expected_type=type_hints["certificate_authorities_url"])
            check_type(argname="argument character_set", value=character_set, expected_type=type_hints["character_set"])
            check_type(argname="argument collation", value=collation, expected_type=type_hints["collation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if certificate_authorities_url is not None:
            self._values["certificate_authorities_url"] = certificate_authorities_url
        if character_set is not None:
            self._values["character_set"] = character_set
        if collation is not None:
            self._values["collation"] = collation

    @builtins.property
    def certificate_authorities_url(self) -> typing.Optional[builtins.str]:
        '''The URL to the PEM-encoded Certificate Authority file.

        Normally, we would just assume the Lambda runtime has the certificates to
        trust already installed. Since the current Lambda runtime environments lack
        the newer RDS certificate authority certificates, this option can be used
        to specify a URL to a remote file containing the CAs.

        :default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem

        :see: https://github.com/aws/aws-lambda-base-images/issues/123
        '''
        result = self._values.get("certificate_authorities_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def character_set(self) -> typing.Optional[builtins.str]:
        '''The database default character set to use.

        :default: - "utf8mb4"
        '''
        result = self._values.get("character_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def collation(self) -> typing.Optional[builtins.str]:
        '''The database default collation to use.

        :default: - rely on MySQL to choose the default collation.
        '''
        result = self._values.get("collation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MysqlDatabaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.MysqlDatabaseProps",
    jsii_struct_bases=[BaseDatabaseProps, MysqlDatabaseOptions],
    name_mapping={
        "database_name": "databaseName",
        "security_group": "securityGroup",
        "vpc_subnets": "vpcSubnets",
        "admin_secret": "adminSecret",
        "endpoint": "endpoint",
        "target": "target",
        "vpc": "vpc",
        "certificate_authorities_url": "certificateAuthoritiesUrl",
        "character_set": "characterSet",
        "collation": "collation",
    },
)
class MysqlDatabaseProps(BaseDatabaseProps, MysqlDatabaseOptions):
    def __init__(
        self,
        *,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
        target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructor properties for MysqlDatabase.

        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param endpoint: The cluster or instance endpoint.
        :param target: The target service or database.
        :param vpc: The VPC where the Lambda function will run.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b42b3dc678f48a79d6d0214768d515a19ddc59d87098698b7f0ef95f408ac76b)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument admin_secret", value=admin_secret, expected_type=type_hints["admin_secret"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument certificate_authorities_url", value=certificate_authorities_url, expected_type=type_hints["certificate_authorities_url"])
            check_type(argname="argument character_set", value=character_set, expected_type=type_hints["character_set"])
            check_type(argname="argument collation", value=collation, expected_type=type_hints["collation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "admin_secret": admin_secret,
            "endpoint": endpoint,
            "target": target,
            "vpc": vpc,
        }
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if certificate_authorities_url is not None:
            self._values["certificate_authorities_url"] = certificate_authorities_url
        if character_set is not None:
            self._values["character_set"] = character_set
        if collation is not None:
            self._values["collation"] = collation

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog to create.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group for the Lambda function.

        :default: - a new security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The type of subnets in the VPC where the Lambda function will run.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def admin_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''A Secrets Manager secret that contains administrative credentials.'''
        result = self._values.get("admin_secret")
        assert result is not None, "Required property 'admin_secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''The cluster or instance endpoint.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, result)

    @builtins.property
    def target(self) -> _aws_cdk_aws_ec2_ceddda9d.IConnectable:
        '''The target service or database.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IConnectable, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where the Lambda function will run.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def certificate_authorities_url(self) -> typing.Optional[builtins.str]:
        '''The URL to the PEM-encoded Certificate Authority file.

        Normally, we would just assume the Lambda runtime has the certificates to
        trust already installed. Since the current Lambda runtime environments lack
        the newer RDS certificate authority certificates, this option can be used
        to specify a URL to a remote file containing the CAs.

        :default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem

        :see: https://github.com/aws/aws-lambda-base-images/issues/123
        '''
        result = self._values.get("certificate_authorities_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def character_set(self) -> typing.Optional[builtins.str]:
        '''The database default character set to use.

        :default: - "utf8mb4"
        '''
        result = self._values.get("character_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def collation(self) -> typing.Optional[builtins.str]:
        '''The database default collation to use.

        :default: - rely on MySQL to choose the default collation.
        '''
        result = self._values.get("collation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MysqlDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.PostgresqlDatabaseOptions",
    jsii_struct_bases=[],
    name_mapping={
        "owner_secret": "ownerSecret",
        "certificate_authorities_url": "certificateAuthoritiesUrl",
        "encoding": "encoding",
        "locale": "locale",
        "schema_name": "schemaName",
    },
)
class PostgresqlDatabaseOptions:
    def __init__(
        self,
        *,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''PostgreSQL-specific options.

        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6710a06e4f6994850322149d3a968d6631f7dee52c2feaa18bec04cfc18126ed)
            check_type(argname="argument owner_secret", value=owner_secret, expected_type=type_hints["owner_secret"])
            check_type(argname="argument certificate_authorities_url", value=certificate_authorities_url, expected_type=type_hints["certificate_authorities_url"])
            check_type(argname="argument encoding", value=encoding, expected_type=type_hints["encoding"])
            check_type(argname="argument locale", value=locale, expected_type=type_hints["locale"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner_secret": owner_secret,
        }
        if certificate_authorities_url is not None:
            self._values["certificate_authorities_url"] = certificate_authorities_url
        if encoding is not None:
            self._values["encoding"] = encoding
        if locale is not None:
            self._values["locale"] = locale
        if schema_name is not None:
            self._values["schema_name"] = schema_name

    @builtins.property
    def owner_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The Secrets Manager secret for the owner of the schema.'''
        result = self._values.get("owner_secret")
        assert result is not None, "Required property 'owner_secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def certificate_authorities_url(self) -> typing.Optional[builtins.str]:
        '''The URL to the PEM-encoded Certificate Authority file.

        Normally, we would just assume the Lambda runtime has the certificates to
        trust already installed. Since the current Lambda runtime environments lack
        the newer RDS certificate authority certificates, this option can be used
        to specify a URL to a remote file containing the CAs.

        :default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem

        :see: https://github.com/aws/aws-lambda-base-images/issues/123
        '''
        result = self._values.get("certificate_authorities_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encoding(self) -> typing.Optional[builtins.str]:
        '''The database default encoding set to use.

        :default: - "UTF8"
        '''
        result = self._values.get("encoding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locale(self) -> typing.Optional[builtins.str]:
        '''The database default locale to use.

        :default: - rely on PostgreSQL to choose the default locale.
        '''
        result = self._values.get("locale")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''The name of the schema to create.

        :default: - The username of the ownerSecret.
        '''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PostgresqlDatabaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.PostgresqlDatabaseProps",
    jsii_struct_bases=[BaseDatabaseProps, PostgresqlDatabaseOptions],
    name_mapping={
        "database_name": "databaseName",
        "security_group": "securityGroup",
        "vpc_subnets": "vpcSubnets",
        "admin_secret": "adminSecret",
        "endpoint": "endpoint",
        "target": "target",
        "vpc": "vpc",
        "owner_secret": "ownerSecret",
        "certificate_authorities_url": "certificateAuthoritiesUrl",
        "encoding": "encoding",
        "locale": "locale",
        "schema_name": "schemaName",
    },
)
class PostgresqlDatabaseProps(BaseDatabaseProps, PostgresqlDatabaseOptions):
    def __init__(
        self,
        *,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
        target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructor properties for PostgresqlDatabase.

        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param endpoint: The cluster or instance endpoint.
        :param target: The target service or database.
        :param vpc: The VPC where the Lambda function will run.
        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74ccdbb57cdd98a0b070eec3cf06b644c97e97df1c05f3475ccf70231f6d0f73)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument admin_secret", value=admin_secret, expected_type=type_hints["admin_secret"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument owner_secret", value=owner_secret, expected_type=type_hints["owner_secret"])
            check_type(argname="argument certificate_authorities_url", value=certificate_authorities_url, expected_type=type_hints["certificate_authorities_url"])
            check_type(argname="argument encoding", value=encoding, expected_type=type_hints["encoding"])
            check_type(argname="argument locale", value=locale, expected_type=type_hints["locale"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "admin_secret": admin_secret,
            "endpoint": endpoint,
            "target": target,
            "vpc": vpc,
            "owner_secret": owner_secret,
        }
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if certificate_authorities_url is not None:
            self._values["certificate_authorities_url"] = certificate_authorities_url
        if encoding is not None:
            self._values["encoding"] = encoding
        if locale is not None:
            self._values["locale"] = locale
        if schema_name is not None:
            self._values["schema_name"] = schema_name

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog to create.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group for the Lambda function.

        :default: - a new security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The type of subnets in the VPC where the Lambda function will run.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def admin_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''A Secrets Manager secret that contains administrative credentials.'''
        result = self._values.get("admin_secret")
        assert result is not None, "Required property 'admin_secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''The cluster or instance endpoint.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, result)

    @builtins.property
    def target(self) -> _aws_cdk_aws_ec2_ceddda9d.IConnectable:
        '''The target service or database.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IConnectable, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where the Lambda function will run.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def owner_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The Secrets Manager secret for the owner of the schema.'''
        result = self._values.get("owner_secret")
        assert result is not None, "Required property 'owner_secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def certificate_authorities_url(self) -> typing.Optional[builtins.str]:
        '''The URL to the PEM-encoded Certificate Authority file.

        Normally, we would just assume the Lambda runtime has the certificates to
        trust already installed. Since the current Lambda runtime environments lack
        the newer RDS certificate authority certificates, this option can be used
        to specify a URL to a remote file containing the CAs.

        :default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem

        :see: https://github.com/aws/aws-lambda-base-images/issues/123
        '''
        result = self._values.get("certificate_authorities_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encoding(self) -> typing.Optional[builtins.str]:
        '''The database default encoding set to use.

        :default: - "UTF8"
        '''
        result = self._values.get("encoding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locale(self) -> typing.Optional[builtins.str]:
        '''The database default locale to use.

        :default: - rely on PostgreSQL to choose the default locale.
        '''
        result = self._values.get("locale")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''The name of the schema to create.

        :default: - The username of the ownerSecret.
        '''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PostgresqlDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.PrioritizedLines",
    jsii_struct_bases=[],
    name_mapping={"lines": "lines", "priority": "priority"},
)
class PrioritizedLines:
    def __init__(
        self,
        *,
        lines: typing.Sequence[builtins.str],
        priority: jsii.Number,
    ) -> None:
        '''A container for lines of a User Data script, sortable by ``priority``.

        :param lines: The command lines.
        :param priority: The priority for this set of commands.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6e48c7b1cd24344a1cdbb27f3f7aea01ec3a2ce2f1bf2ce870bcc01f662aa91)
            check_type(argname="argument lines", value=lines, expected_type=type_hints["lines"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lines": lines,
            "priority": priority,
        }

    @builtins.property
    def lines(self) -> typing.List[builtins.str]:
        '''The command lines.'''
        result = self._values.get("lines")
        assert result is not None, "Required property 'lines' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''The priority for this set of commands.'''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrioritizedLines(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IRunnableFargateTask)
class RunnableFargateTask(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.RunnableFargateTask",
):
    '''An RunnableFargateTask construct.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        task_image_options: typing.Optional[typing.Union[FargateTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    ) -> None:
        '''Creates a new RunnableFargateTask.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param cluster: The cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param task_image_options: The properties to define if the construct is to create a TaskDefinition. taskDefinition or image must be defined, but not both. Default: - none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        :param assign_public_ip: Specifies whether the task's elastic network interface receives a public IP address. If true, the task will receive a public IP address. Default: false
        :param security_groups: Existing security groups to use for your task. Default: - a new security group will be created.
        :param vpc_subnets: The subnets to associate with the task. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dec19256510924858e71ecf29fae220381410f999cfdc1c91b843af29b20b2e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RunnableFargateTaskProps(
            cluster=cluster,
            task_image_options=task_image_options,
            vpc=vpc,
            assign_public_ip=assign_public_ip,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
            cpu=cpu,
            ephemeral_storage_gib=ephemeral_storage_gib,
            memory_limit_mib=memory_limit_mib,
            platform_version=platform_version,
            runtime_platform=runtime_platform,
            task_definition=task_definition,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createAWSLogDriver")
    def _create_aws_log_driver(
        self,
        prefix: builtins.str,
    ) -> _aws_cdk_aws_ecs_ceddda9d.AwsLogDriver:
        '''Creates a new AwsLogDriver.

        Modeled after "aws-cdk-lib/aws-ecs".

        :param prefix: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a0bd282b45a84f20604bbb11f720ffdb12ec08cdb90c52b55e8805df57e3fc9)
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.AwsLogDriver, jsii.invoke(self, "createAWSLogDriver", [prefix]))

    @jsii.member(jsii_name="getDefaultCluster")
    def _get_default_cluster(
        self,
        scope: _constructs_77d1e7e8.Construct,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> _aws_cdk_aws_ecs_ceddda9d.Cluster:
        '''Returns the default cluster.

        Modeled after "aws-cdk-lib/aws-ecs-patterns".

        :param scope: -
        :param vpc: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cb2fc9c646ea45b7bcc43751c1719285f05896779ef4f2931636d2e5ba77503)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.Cluster, jsii.invoke(self, "getDefaultCluster", [scope, vpc]))

    @builtins.property
    @jsii.member(jsii_name="task")
    def task(self) -> IFargateTask:
        '''The FargateTask in this construct.'''
        return typing.cast(IFargateTask, jsii.get(self, "task"))

    @builtins.property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition:
        '''The FargateTaskDefinition in this construct.'''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition, jsii.get(self, "taskDefinition"))


@jsii.data_type(
    jsii_type="shady-island.RunnableFargateTaskProps",
    jsii_struct_bases=[
        BaseFargateTaskProps,
        _aws_cdk_aws_ecs_patterns_ceddda9d.FargateServiceBaseProps,
    ],
    name_mapping={
        "assign_public_ip": "assignPublicIp",
        "security_groups": "securityGroups",
        "vpc_subnets": "vpcSubnets",
        "cpu": "cpu",
        "ephemeral_storage_gib": "ephemeralStorageGiB",
        "memory_limit_mib": "memoryLimitMiB",
        "platform_version": "platformVersion",
        "runtime_platform": "runtimePlatform",
        "task_definition": "taskDefinition",
        "cluster": "cluster",
        "task_image_options": "taskImageOptions",
        "vpc": "vpc",
    },
)
class RunnableFargateTaskProps(
    BaseFargateTaskProps,
    _aws_cdk_aws_ecs_patterns_ceddda9d.FargateServiceBaseProps,
):
    def __init__(
        self,
        *,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        task_image_options: typing.Optional[typing.Union[FargateTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Constructor properties for RunnableFargateTask.

        :param assign_public_ip: Specifies whether the task's elastic network interface receives a public IP address. If true, the task will receive a public IP address. Default: false
        :param security_groups: Existing security groups to use for your task. Default: - a new security group will be created.
        :param vpc_subnets: The subnets to associate with the task. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none
        :param cluster: The cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param task_image_options: The properties to define if the construct is to create a TaskDefinition. taskDefinition or image must be defined, but not both. Default: - none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if isinstance(runtime_platform, dict):
            runtime_platform = _aws_cdk_aws_ecs_ceddda9d.RuntimePlatform(**runtime_platform)
        if isinstance(task_image_options, dict):
            task_image_options = FargateTaskImageOptions(**task_image_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bc78880d3229e5744813c8ea28556d3cb503c816f71a3d30639005c586811d5)
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument cpu", value=cpu, expected_type=type_hints["cpu"])
            check_type(argname="argument ephemeral_storage_gib", value=ephemeral_storage_gib, expected_type=type_hints["ephemeral_storage_gib"])
            check_type(argname="argument memory_limit_mib", value=memory_limit_mib, expected_type=type_hints["memory_limit_mib"])
            check_type(argname="argument platform_version", value=platform_version, expected_type=type_hints["platform_version"])
            check_type(argname="argument runtime_platform", value=runtime_platform, expected_type=type_hints["runtime_platform"])
            check_type(argname="argument task_definition", value=task_definition, expected_type=type_hints["task_definition"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument task_image_options", value=task_image_options, expected_type=type_hints["task_image_options"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if cpu is not None:
            self._values["cpu"] = cpu
        if ephemeral_storage_gib is not None:
            self._values["ephemeral_storage_gib"] = ephemeral_storage_gib
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if platform_version is not None:
            self._values["platform_version"] = platform_version
        if runtime_platform is not None:
            self._values["runtime_platform"] = runtime_platform
        if task_definition is not None:
            self._values["task_definition"] = task_definition
        if cluster is not None:
            self._values["cluster"] = cluster
        if task_image_options is not None:
            self._values["task_image_options"] = task_image_options
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether the task's elastic network interface receives a public IP address.

        If true, the task will receive a public IP address.

        :default: false
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Existing security groups to use for your task.

        :default: - a new security group will be created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets to associate with the task.

        :default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''The number of cpu units used by the task.

        Valid values, which determines your range of valid values for the memory parameter:

        256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB

        512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB

        1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB

        2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments

        4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments

        8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments

        16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 256
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ephemeral_storage_gib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in GiB) of ephemeral storage to be allocated to the task.

        The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB.

        Only supported in Fargate platform version 1.4.0 or later.

        :default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        '''
        result = self._values.get("ephemeral_storage_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in MiB) of memory used by the task.

        This field is required and you must use one of the following values, which determines your range of valid values
        for the cpu parameter:

        512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU)

        1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU)

        2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU)

        Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU)

        Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU)

        Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU)

        Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU)

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 512
        '''
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def platform_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion]:
        '''The platform version on which to run your service.

        If one is not specified, the LATEST platform version is used by default. For more information, see
        `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_
        in the Amazon Elastic Container Service Developer Guide.

        :default: Latest
        '''
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion], result)

    @builtins.property
    def runtime_platform(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform]:
        '''The runtime platform of the task definition.

        :default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        '''
        result = self._values.get("runtime_platform")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform], result)

    @builtins.property
    def task_definition(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition]:
        '''The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both.

        [disable-awslint:ref-via-interface]

        :default: - none
        '''
        result = self._values.get("task_definition")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition], result)

    @builtins.property
    def cluster(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster]:
        '''The cluster that hosts the service.

        If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc.

        :default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster], result)

    @builtins.property
    def task_image_options(self) -> typing.Optional[FargateTaskImageOptions]:
        '''The properties to define if the construct is to create a TaskDefinition.

        taskDefinition or image must be defined, but not both.

        :default: - none
        '''
        result = self._values.get("task_image_options")
        return typing.cast(typing.Optional[FargateTaskImageOptions], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed.

        If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster.

        :default: - uses the VPC defined in the cluster or creates a new VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RunnableFargateTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.StateMachineTaskProps",
    jsii_struct_bases=[_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps],
    name_mapping={
        "comment": "comment",
        "credentials": "credentials",
        "heartbeat": "heartbeat",
        "heartbeat_timeout": "heartbeatTimeout",
        "input_path": "inputPath",
        "integration_pattern": "integrationPattern",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "state_name": "stateName",
        "task_timeout": "taskTimeout",
        "timeout": "timeout",
        "container_overrides": "containerOverrides",
        "enable_execute_command": "enableExecuteCommand",
        "propagated_tag_source": "propagatedTagSource",
        "revision_number": "revisionNumber",
    },
)
class StateMachineTaskProps(_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps):
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        propagated_tag_source: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        revision_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties to create a new State Machine EcsRunTask step.

        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        :param container_overrides: Container setting overrides. Specify the container to use and the overrides to apply. Default: - No overrides
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: false
        :param propagated_tag_source: Specifies whether to propagate the tags from the task definition to the task. An error will be received if you specify the SERVICE option when running a task. Default: - No tags are propagated.
        :param revision_number: The revision number of ECS task definition family. Default: - '$latest'
        '''
        if isinstance(credentials, dict):
            credentials = _aws_cdk_aws_stepfunctions_ceddda9d.Credentials(**credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b318285290bae1c9ced1c85c8d15ba99f3be22a5cc9028602343e8d66cac1711)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument heartbeat_timeout", value=heartbeat_timeout, expected_type=type_hints["heartbeat_timeout"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument integration_pattern", value=integration_pattern, expected_type=type_hints["integration_pattern"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument state_name", value=state_name, expected_type=type_hints["state_name"])
            check_type(argname="argument task_timeout", value=task_timeout, expected_type=type_hints["task_timeout"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument container_overrides", value=container_overrides, expected_type=type_hints["container_overrides"])
            check_type(argname="argument enable_execute_command", value=enable_execute_command, expected_type=type_hints["enable_execute_command"])
            check_type(argname="argument propagated_tag_source", value=propagated_tag_source, expected_type=type_hints["propagated_tag_source"])
            check_type(argname="argument revision_number", value=revision_number, expected_type=type_hints["revision_number"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if credentials is not None:
            self._values["credentials"] = credentials
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if heartbeat_timeout is not None:
            self._values["heartbeat_timeout"] = heartbeat_timeout
        if input_path is not None:
            self._values["input_path"] = input_path
        if integration_pattern is not None:
            self._values["integration_pattern"] = integration_pattern
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if state_name is not None:
            self._values["state_name"] = state_name
        if task_timeout is not None:
            self._values["task_timeout"] = task_timeout
        if timeout is not None:
            self._values["timeout"] = timeout
        if container_overrides is not None:
            self._values["container_overrides"] = container_overrides
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if propagated_tag_source is not None:
            self._values["propagated_tag_source"] = propagated_tag_source
        if revision_number is not None:
            self._values["revision_number"] = revision_number

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: - No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials]:
        '''Credentials for an IAM Role that the State Machine assumes for executing the task.

        This enables cross-account resource invocations.

        :default: - None (Task is executed using the State Machine's execution role)

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-access-cross-acct-resources.html
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials], result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the heartbeat.

        :default: - None

        :deprecated: use ``heartbeatTimeout``

        :stability: deprecated
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def heartbeat_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the heartbeat.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("heartbeat_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: - The entire task input (JSON path '$')
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern]:
        '''AWS Step Functions integrates with services directly in the Amazon States Language.

        You can control these AWS services using service integration patterns.

        Depending on the AWS Service, the Service Integration Pattern availability will vary.

        :default:

        - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks.
        ``IntegrationPattern.RUN_JOB`` for the following exceptions:
        ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-supported-services.html
        '''
        result = self._values.get("integration_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select select a portion of the state output to pass to the next state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default:

        - The entire JSON node determined by the state input, the task result,
        and resultPath is passed to the next state (JSON path '$')
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: - Replaces the entire input with the result (JSON path '$')
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for this state.

        :default: - The construct ID will be used as state name
        '''
        result = self._values.get("state_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the task.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("task_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the task.

        :default: - None

        :deprecated: use ``taskTimeout``

        :stability: deprecated
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def container_overrides(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ContainerOverride]]:
        '''Container setting overrides.

        Specify the container to use and the overrides to apply.

        :default: - No overrides
        '''
        result = self._values.get("container_overrides")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ContainerOverride]], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether ECS Exec should be enabled.

        :default: false

        :see: https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_RunTask.html#ECS-RunTask-request-enableExecuteCommand
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def propagated_tag_source(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource]:
        '''Specifies whether to propagate the tags from the task definition to the task.

        An error will be received if you specify the SERVICE option when running a task.

        :default: - No tags are propagated.

        :see: https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_RunTask.html#ECS-RunTask-request-propagateTags
        '''
        result = self._values.get("propagated_tag_source")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource], result)

    @builtins.property
    def revision_number(self) -> typing.Optional[jsii.Number]:
        '''The revision number of ECS task definition family.

        :default: - '$latest'
        '''
        result = self._values.get("revision_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StateMachineTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Tier(metaclass=jsii.JSIIMeta, jsii_type="shady-island.Tier"):
    '''A deployment environment with a specific purpose and audience.

    You can create any Tier you like, but we include those explained by DTAP.

    :see: https://en.wikipedia.org/wiki/Development,_testing,_acceptance_and_production
    '''

    def __init__(self, id: builtins.str, label: builtins.str) -> None:
        '''Creates a new Tier.

        :param id: - The machine-readable identifier for this tier (e.g. prod).
        :param label: - The human-readable label for this tier (e.g. Production).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__530a177d1cc816f59517c3e52dceeb99d4c7774e513d4d6bf96e414b10eee80f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
        jsii.create(self.__class__, self, [id, label])

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, construct: _constructs_77d1e7e8.IConstruct) -> typing.Optional["Tier"]:
        '''Finds the deployment tier of the given construct.

        :param construct: - The construct to inspect.

        :return: The assigned deployment tier if found, otherwise undefined
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b29107dd146351897f69274b70bc4ebc35a56ff67af9f9ba3babcc98acfbfcf3)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(typing.Optional["Tier"], jsii.sinvoke(cls, "of", [construct]))

    @jsii.member(jsii_name="parse")
    @builtins.classmethod
    def parse(cls, value: builtins.str) -> "Tier":
        '''Return the deployment tier that corresponds to the provided value.

        Production: "live", "prod", or "production".
        Acceptance: "uat", "stage", "staging", or "acceptance".
        Testing: "qc", "qa", "test", or "testing".
        Development: anything else.

        :param value: - The value to parse, case-insensitive.

        :return: The matching deployment tier, or else ``DEVELOPMENT``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2f20e1b838706908cb4dc457364ab4d6a3ba246f70b4d648ff5df5ead1e52df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Tier", jsii.sinvoke(cls, "parse", [value]))

    @jsii.member(jsii_name="applyTags")
    def apply_tags(self, construct: _constructs_77d1e7e8.IConstruct) -> None:
        '''Adds the label of this tier as a tag to the provided construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c184966e811a15ee5af7f9b885e27fa53713f5978c027ccfe09f4878a486801)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(None, jsii.invoke(self, "applyTags", [construct]))

    @jsii.member(jsii_name="assignTo")
    def assign_to(self, construct: _constructs_77d1e7e8.IConstruct) -> None:
        '''Assigns this tier to a construct.

        This method will register an error annotation on the construct if any of
        the constructs in its parent scopes have a different tier assigned.

        :param construct: - The construct to receive the tier assignment.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cf79e20cf3b8dc496886cc4ba33e3e35eb2f7aa6b620c4974179e5aa009b220)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(None, jsii.invoke(self, "assignTo", [construct]))

    @jsii.member(jsii_name="matches")
    def matches(self, other: "Tier") -> builtins.bool:
        '''Compares this tier to the provided value and tests for equality.

        :param other: - The value to compare.

        :return: Whether the provided value is equal to this tier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc74e7f1b826ca0249b2f9a045466e09289c315ccc1cc9056778d302475eac52)
            check_type(argname="argument other", value=other, expected_type=type_hints["other"])
        return typing.cast(builtins.bool, jsii.invoke(self, "matches", [other]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ACCEPTANCE")
    def ACCEPTANCE(cls) -> "Tier":
        '''A tier that represents an acceptance environment.'''
        return typing.cast("Tier", jsii.sget(cls, "ACCEPTANCE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEVELOPMENT")
    def DEVELOPMENT(cls) -> "Tier":
        '''A tier that represents a development environment.'''
        return typing.cast("Tier", jsii.sget(cls, "DEVELOPMENT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PRODUCTION")
    def PRODUCTION(cls) -> "Tier":
        '''A tier that represents a production environment.'''
        return typing.cast("Tier", jsii.sget(cls, "PRODUCTION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TESTING")
    def TESTING(cls) -> "Tier":
        '''A tier that represents a testing environment.'''
        return typing.cast("Tier", jsii.sget(cls, "TESTING"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The machine-readable identifier for this tier (e.g. prod).'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''The human-readable label for this tier (e.g. Production).'''
        return typing.cast(builtins.str, jsii.get(self, "label"))


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class TierTagger(metaclass=jsii.JSIIMeta, jsii_type="shady-island.TierTagger"):
    '''A CDK Aspect to apply the ``DeploymentTier`` tag to Stacks.'''

    def __init__(self, tier: Tier) -> None:
        '''Create a new TierTagger.

        :param tier: - The deployment tier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__990a574adf189a6673820477e428083f72ec0266d44b5e27d24c121fa0e63484)
            check_type(argname="argument tier", value=tier, expected_type=type_hints["tier"])
        jsii.create(self.__class__, self, [tier])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a15fa1bc21541be12e0110218ecd1f0ad7b7835b2f7f90b8fc12445814d93ef6)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


class UserDataBuilder(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="shady-island.UserDataBuilder",
):
    '''A utility class to assist with composing instance User Data.

    This class allows multiple observers in code to add lines to the same end
    result UserData without clobbering each other. Just like ``conf.d`` directories
    with priority number prefixes, you can declare the proper execution order of
    your UserData commands without having to add them in that order.
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="forLinux")
    @builtins.classmethod
    def for_linux(
        cls,
        *,
        shebang: typing.Optional[builtins.str] = None,
    ) -> "UserDataBuilder":
        '''Returns a user data builder for GNU/Linux operating systems.

        :param shebang: Shebang for the UserData script. Default: "#!/bin/bash"

        :return: the new builder object
        '''
        options = _aws_cdk_aws_ec2_ceddda9d.LinuxUserDataOptions(shebang=shebang)

        return typing.cast("UserDataBuilder", jsii.sinvoke(cls, "forLinux", [options]))

    @jsii.member(jsii_name="forWindows")
    @builtins.classmethod
    def for_windows(cls) -> "UserDataBuilder":
        '''Returns a user data builder for Windows operating systems.

        :return: the new builder object
        '''
        return typing.cast("UserDataBuilder", jsii.sinvoke(cls, "forWindows", []))

    @jsii.member(jsii_name="addCommands")
    def add_commands(self, *commands: builtins.str) -> None:
        '''Add one or more commands to the user data with a priority of ``0``.

        :param commands: - The lines to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f56dc72e2b8d9e69be937435e41fa771eb82b99df61762e67305a1aa7d1a25cd)
            check_type(argname="argument commands", value=commands, expected_type=typing.Tuple[type_hints["commands"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addCommands", [*commands]))

    @jsii.member(jsii_name="buildUserData")
    @abc.abstractmethod
    def build_user_data(self) -> _aws_cdk_aws_ec2_ceddda9d.UserData:
        '''Produces the User Data script with all lines sorted in priority order.

        :return: The assembled User Data
        '''
        ...

    @jsii.member(jsii_name="insertCommands")
    def insert_commands(self, priority: jsii.Number, *commands: builtins.str) -> None:
        '''Add one or more commands to the user data at a specific priority.

        :param priority: - The priority of these lines (lower executes earlier).
        :param commands: - The lines to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6114eade1a4b4469c7ffa50dbde1b95b36c5b299d356317bbe384e4caf526133)
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument commands", value=commands, expected_type=typing.Tuple[type_hints["commands"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "insertCommands", [priority, *commands]))

    @builtins.property
    @jsii.member(jsii_name="lines")
    def _lines(self) -> typing.List[PrioritizedLines]:
        '''The groups of prioritized command line entries.'''
        return typing.cast(typing.List[PrioritizedLines], jsii.get(self, "lines"))


class _UserDataBuilderProxy(UserDataBuilder):
    @jsii.member(jsii_name="buildUserData")
    def build_user_data(self) -> _aws_cdk_aws_ec2_ceddda9d.UserData:
        '''Produces the User Data script with all lines sorted in priority order.

        :return: The assembled User Data
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.UserData, jsii.invoke(self, "buildUserData", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, UserDataBuilder).__jsii_proxy_class__ = lambda : _UserDataBuilderProxy


class Workload(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.Workload",
):
    '''A collection of Stacks in an Environment representing a deployment Tier.

    Consider deriving a subclass of ``Workload`` and creating your ``Stack`` objects
    within its constructor.

    The difference between this class and a ``Stage`` is that a ``Stage`` is meant to
    be deployed with CDK Pipelines. This class can be used with ``cdk deploy``.
    This class also provides context loading capabilities.

    It is an anti-pattern to provide a ``Workload`` instance as the parent scope to
    the ``aws-cdk-lib.Stack`` constructor. You should either use the
    ``createStack()`` method, create your own sub-class of ``Stack`` and provide a
    ``Workload`` instance as the parent scope, or use the ``import()`` method to
    essentially *import* a ``Stack`` and its constructs into a ``Workload`` without
    changing its scope.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        tier: Tier,
        base_domain_name: typing.Optional[builtins.str] = None,
        context_file: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        workload_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new Workload.

        :param scope: - The construct scope.
        :param id: - The construct ID.
        :param tier: The deployment tier.
        :param base_domain_name: The base domain name used to create the FQDN for public resources.
        :param context_file: The filesystem path to a JSON file that contains context values to load. Using this property allows you to load different context values within each instantiated ``Workload``, directly from a file you can check into source control.
        :param env: The AWS environment (account/region) where this stack will be deployed.
        :param workload_name: The machine identifier for this workload. This value will be used to create the ``publicDomainName`` property. By default, the ``stackName`` property used to create ``Stack`` constructs in the ``createStack`` method will begin with this Workload's ``workloadName`` and its ``tier`` separated by hyphens. Consider providing a constant ``workloadName`` value to the superclass constructor in your derived class. Default: - The id passed to the ``Workload`` constructor, but in lowercase
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bc677f9592ce3b6c83e0b51756bcbfa8439cf4279d746c77e45e81d3ac83c74)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WorkloadProps(
            tier=tier,
            base_domain_name=base_domain_name,
            context_file=context_file,
            env=env,
            workload_name=workload_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="isWorkload")
    @builtins.classmethod
    def is_workload(cls, x: typing.Any) -> builtins.bool:
        '''Test whether the given construct is a Workload.

        :param x: - The value to test.

        :return: Whether the value is a Workload object.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96ebb0ba06e254e10fe2379e1883988108104f296135702e61231d2437cee11e)
            check_type(argname="argument x", value=x, expected_type=type_hints["x"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isWorkload", [x]))

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, construct: _constructs_77d1e7e8.IConstruct) -> "Workload":
        '''Return the Workload the construct is contained within, fails if there is no workload up the tree.

        :param construct: - The construct whose parent nodes will be searched.

        :return: The Workload containing the construct

        :throws: Error - if none of the construct's parents are a workload
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e27f5fc4333ac0563c57801a0b496252f1fe2f4b9a122724ccfbfec6d7998dbf)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast("Workload", jsii.sinvoke(cls, "of", [construct]))

    @jsii.member(jsii_name="createStack")
    def create_stack(
        self,
        id: builtins.str,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_ceddda9d.Stack:
        '''Adds a stack to the Workload.

        This method will return a ``Stack`` with this Workload as its scope. By
        default, the ``stackName`` property provided to the ``Stack`` will be this
        Workload's ``workloadName``, its ``tier``, and the value of the ``id``
        parameter separated by hyphens, all in lowercase.

        :param id: - The Stack construct id (e.g. "Network").
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        Example::

            const exampleDev = new Workload(app, 'Example', {
              tier: Tier.DEVELOPMENT,
              env: { account: '123456789012', region: 'us-east-1' },
            });
            const networkStack = exampleDev.createStack('Network', {});
            assert.strictEqual(networkStack.stackName, 'example-dev-network').
            
            You can override the `env` and `stackName` properties in the `props`
            argument if desired.
            
            The stack will have a `DeploymentTier` tag added, set to the tier label.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9ba1202ef7d254e0e9e1f79faf21a7241261ea59fec1d6b565e8f9c5709830b)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.StackProps(
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        return typing.cast(_aws_cdk_ceddda9d.Stack, jsii.invoke(self, "createStack", [id, props]))

    @jsii.member(jsii_name="import")
    def import_(self, *stacks: _aws_cdk_ceddda9d.Stack) -> None:
        '''Forces a return value for ``Workload.of`` for one or more ``Stack`` objects.

        Normally, a construct must be within the scope of the ``Workload`` instance,
        such as a construct that is a descendant of a ``Stack`` returned from
        ``createStack()``.

        That means that any ``Stack`` instances you created in your CDK application
        *before* installing the ``shady-island`` library would not be able to be part
        of a ``Workload`` unless you changed the ``scope`` argument of the ``Stack``
        constructor from the ``App`` or ``Stage`` to the desired ``Workload`` instance.
        However, that's bad news for a ``Stack`` that has already been deployed to
        CloudFormation because the resource identifier of persistent child
        constructs (e.g. RDS databases, S3 buckets) would change.

        A successful call to this method will register the provided ``Stack`` objects
        and all their construct descendants as members of that ``Workload`` instance.
        Calling ``Workload.of()`` with any of the provided ``Stack`` objects or their
        descendant constructs will return that ``Workload`` instance.

        If any of the ``Stack`` objects provided to this method already belong to a
        different ``Workload`` object, or whose parent scope is not identical to the
        parent scope of this ``Workload`` (i.e. the ``Stage`` or the ``App``), an error
        will be thrown.

        :param stacks: - The ``Stack`` instances to import to this ``Workload``.

        :throws: {Error} if any of the stacks have a different parent scope
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd2eedf91b5d4e25d97e311a1a26f03b3db1e8d5bba809f0a2bd20df11d9bdfb)
            check_type(argname="argument stacks", value=stacks, expected_type=typing.Tuple[type_hints["stacks"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "import", [*stacks]))

    @jsii.member(jsii_name="registerStack")
    def _register_stack(
        self,
        stack: _aws_cdk_ceddda9d.Stack,
    ) -> _aws_cdk_ceddda9d.Stack:
        '''Register the provided ``Stack`` as being part of this ``Workload``.

        :param stack: - The stack to register.

        :return: The provided Stack
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19f32a870d457362c1bd937f00bb736bfc4263b2f555fd93d34c4bf7dd53f7a7)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(_aws_cdk_ceddda9d.Stack, jsii.invoke(self, "registerStack", [stack]))

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List[_aws_cdk_ceddda9d.Stack]:
        '''
        :return: The stacks created by invoking ``createStack``
        '''
        return typing.cast(typing.List[_aws_cdk_ceddda9d.Stack], jsii.get(self, "stacks"))

    @builtins.property
    @jsii.member(jsii_name="tier")
    def tier(self) -> Tier:
        '''The deployment tier.'''
        return typing.cast(Tier, jsii.get(self, "tier"))

    @builtins.property
    @jsii.member(jsii_name="workloadName")
    def workload_name(self) -> builtins.str:
        '''The prefix used in the default ``stackName`` provided to child Stacks.'''
        return typing.cast(builtins.str, jsii.get(self, "workloadName"))

    @builtins.property
    @jsii.member(jsii_name="account")
    def account(self) -> typing.Optional[builtins.str]:
        '''The default account for all resources defined within this workload.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "account"))

    @builtins.property
    @jsii.member(jsii_name="publicDomainName")
    def public_domain_name(self) -> typing.Optional[builtins.str]:
        '''The domain name to use for resources that expose public endpoints.

        You can use ``Workload.of(this).publicDomainName`` as the ``zoneName`` of a
        Route 53 hosted zone.

        Any construct that creates public DNS resources (e.g. those of API Gateway,
        Application Load Balancing, CloudFront) can use this property to format
        a FQDN for itself by adding a subdomain.

        :default: - If ``baseDomainName`` was empty, this will be ``undefined``

        Example::

            const app = new App();
            const workload = new Workload(app, "Foobar", {
              tier: Tier.PRODUCTION,
              baseDomainName: 'example.com'
            });
            assert.strictEqual(workload.publicDomainName, 'prod.foobar.example.com');
            const stack = workload.createStack("DNS");
            const hostedZone = new HostedZone(stack, "HostedZone", {
              zoneName: `${workload.publicDomainName}`
            });
            const api = new RestApi(stack, "API", {
              restApiName: "foobar",
              domainName: { domainName: `api.${workload.publicDomainName}` },
            });
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicDomainName"))

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''The default region for all resources defined within this workload.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))


@jsii.data_type(
    jsii_type="shady-island.WorkloadProps",
    jsii_struct_bases=[],
    name_mapping={
        "tier": "tier",
        "base_domain_name": "baseDomainName",
        "context_file": "contextFile",
        "env": "env",
        "workload_name": "workloadName",
    },
)
class WorkloadProps:
    def __init__(
        self,
        *,
        tier: Tier,
        base_domain_name: typing.Optional[builtins.str] = None,
        context_file: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        workload_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructor properties for a Workload.

        :param tier: The deployment tier.
        :param base_domain_name: The base domain name used to create the FQDN for public resources.
        :param context_file: The filesystem path to a JSON file that contains context values to load. Using this property allows you to load different context values within each instantiated ``Workload``, directly from a file you can check into source control.
        :param env: The AWS environment (account/region) where this stack will be deployed.
        :param workload_name: The machine identifier for this workload. This value will be used to create the ``publicDomainName`` property. By default, the ``stackName`` property used to create ``Stack`` constructs in the ``createStack`` method will begin with this Workload's ``workloadName`` and its ``tier`` separated by hyphens. Consider providing a constant ``workloadName`` value to the superclass constructor in your derived class. Default: - The id passed to the ``Workload`` constructor, but in lowercase
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46d21735e564e0f2e2aaeb9fd18b82adda3268ccc0278f45c2386e1cb3a55271)
            check_type(argname="argument tier", value=tier, expected_type=type_hints["tier"])
            check_type(argname="argument base_domain_name", value=base_domain_name, expected_type=type_hints["base_domain_name"])
            check_type(argname="argument context_file", value=context_file, expected_type=type_hints["context_file"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument workload_name", value=workload_name, expected_type=type_hints["workload_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "tier": tier,
        }
        if base_domain_name is not None:
            self._values["base_domain_name"] = base_domain_name
        if context_file is not None:
            self._values["context_file"] = context_file
        if env is not None:
            self._values["env"] = env
        if workload_name is not None:
            self._values["workload_name"] = workload_name

    @builtins.property
    def tier(self) -> Tier:
        '''The deployment tier.'''
        result = self._values.get("tier")
        assert result is not None, "Required property 'tier' is missing"
        return typing.cast(Tier, result)

    @builtins.property
    def base_domain_name(self) -> typing.Optional[builtins.str]:
        '''The base domain name used to create the FQDN for public resources.'''
        result = self._values.get("base_domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context_file(self) -> typing.Optional[builtins.str]:
        '''The filesystem path to a JSON file that contains context values to load.

        Using this property allows you to load different context values within each
        instantiated ``Workload``, directly from a file you can check into source
        control.
        '''
        result = self._values.get("context_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.'''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def workload_name(self) -> typing.Optional[builtins.str]:
        '''The machine identifier for this workload.

        This value will be used to create the ``publicDomainName`` property.

        By default, the ``stackName`` property used to create ``Stack`` constructs in
        the ``createStack`` method will begin with this Workload's ``workloadName`` and
        its ``tier`` separated by hyphens.

        Consider providing a constant ``workloadName`` value to the superclass
        constructor in your derived class.

        :default: - The id passed to the ``Workload`` constructor, but in lowercase

        Example::

            class MyWorkload extends Workload {
              constructor(scope: Construct, id: string, props: WorkloadProps) {
                super(scope, id, { ...props, workloadName: 'my-workload' });
              }
            }
        '''
        result = self._values.get("workload_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkloadProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IAssignOnLaunch)
class AssignOnLaunch(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.AssignOnLaunch",
):
    '''Enables the "assignIpv6AddressOnCreation" attribute on selected subnets.

    :see: {@link https://github.com/aws/aws-cdk/issues/5927}
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Creates a new BetterVpc.

        :param scope: - The construct scope.
        :param id: - The construct ID.
        :param vpc: The VPC whose subnets will be configured.
        :param vpc_subnets: Which subnets to assign IPv6 addresses upon ENI creation.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef34bf6f916957f913c4aa2b3459686556aaef0c4dde4b4cd1da18bd1bdf38e1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = AssignOnLaunchProps(vpc=vpc, vpc_subnets=vpc_subnets)

        jsii.create(self.__class__, self, [scope, id, options])

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The IPv6-enabled VPC.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="vpcPlacement")
    def vpc_placement(self) -> _aws_cdk_aws_ec2_ceddda9d.SelectedSubnets:
        '''The chosen subnets for address assignment on ENI launch.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, jsii.get(self, "vpcPlacement"))


@jsii.implements(IDatabase)
class BaseDatabase(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="shady-island.BaseDatabase",
):
    '''A database.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        *,
        admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
        target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Creates a new BaseDatabase.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param endpoint: The cluster or instance endpoint.
        :param target: The target service or database.
        :param vpc: The VPC where the Lambda function will run.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdb1e2eeb461f1db3ac370047353ac0ea52393d0b3bd224f768e3785beb6c62f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseDatabaseProps(
            admin_secret=admin_secret,
            endpoint=endpoint,
            target=target,
            vpc=vpc,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addUserAsOwner")
    @abc.abstractmethod
    def add_user_as_owner(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned ownership permissions.

        :param secret: -
        '''
        ...

    @jsii.member(jsii_name="addUserAsReader")
    @abc.abstractmethod
    def add_user_as_reader(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned read-only permissions.

        :param secret: -
        '''
        ...

    @jsii.member(jsii_name="addUserAsUnprivileged")
    @abc.abstractmethod
    def add_user_as_unprivileged(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user with no permissions.

        :param secret: -
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog.'''
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> _aws_cdk_aws_rds_ceddda9d.Endpoint:
        '''The cluster or instance endpoint.'''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.Endpoint, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def _security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="subnetSelection")
    def _subnet_selection(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, jsii.get(self, "subnetSelection"))

    @builtins.property
    @jsii.member(jsii_name="trigger")
    @abc.abstractmethod
    def trigger(self) -> _aws_cdk_triggers_ceddda9d.ITrigger:
        '''The CDK Trigger that kicks off the process.

        You can further customize when the trigger fires using ``executeAfter``.
        '''
        ...


class _BaseDatabaseProxy(BaseDatabase):
    @jsii.member(jsii_name="addUserAsOwner")
    def add_user_as_owner(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned ownership permissions.

        :param secret: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8321fe7ebfabec2cfb0821b009699253ead41aa4a47ace8c7c1cf6dd0e3316f7)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsOwner", [secret]))

    @jsii.member(jsii_name="addUserAsReader")
    def add_user_as_reader(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned read-only permissions.

        :param secret: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ded6f3a40e3d6bb06fc7f9e26451f444265c699a2074e084da4b942c563b230)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsReader", [secret]))

    @jsii.member(jsii_name="addUserAsUnprivileged")
    def add_user_as_unprivileged(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user with no permissions.

        :param secret: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efc753d3732cabfad2d16ab9d335759b80f3f0ebffd50d1f02ac84e731fca0c9)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsUnprivileged", [secret]))

    @builtins.property
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> _aws_cdk_triggers_ceddda9d.ITrigger:
        '''The CDK Trigger that kicks off the process.

        You can further customize when the trigger fires using ``executeAfter``.
        '''
        return typing.cast(_aws_cdk_triggers_ceddda9d.ITrigger, jsii.get(self, "trigger"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseDatabase).__jsii_proxy_class__ = lambda : _BaseDatabaseProxy


@jsii.implements(ICidrContext)
class CidrContext(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.CidrContext",
):
    '''Allocates IPv6 CIDRs and routes for subnets in a VPC.

    :see: {@link https://github.com/aws/aws-cdk/issues/5927}
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        address_pool: typing.Optional[builtins.str] = None,
        assign_address_on_launch: typing.Optional[builtins.bool] = None,
        cidr_block: typing.Optional[builtins.str] = None,
        cidr_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Creates a new BetterVpc.

        :param scope: - The construct scope.
        :param id: - The construct ID.
        :param vpc: The VPC whose subnets will be configured.
        :param address_pool: The ID of a BYOIP IPv6 address pool from which to allocate the CIDR block. If this parameter is not specified or is undefined, the CIDR block will be provided by AWS.
        :param assign_address_on_launch: (deprecated) Whether this VPC should auto-assign an IPv6 address to launched ENIs. True by default.
        :param cidr_block: An IPv6 CIDR block from the IPv6 address pool to use for this VPC. The {@link EnableIpv6Props#addressPool } attribute is required if this parameter is specified.
        :param cidr_count: Split the CIDRs into this many groups (by default one for each subnet).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b0de4a00dc5c9be3f27b4ab96a0dcd78e40528295ed76dce57eec996acc188c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = CidrContextProps(
            vpc=vpc,
            address_pool=address_pool,
            assign_address_on_launch=assign_address_on_launch,
            cidr_block=cidr_block,
            cidr_count=cidr_count,
        )

        jsii.create(self.__class__, self, [scope, id, options])

    @jsii.member(jsii_name="assignPrivateSubnetCidrs")
    def _assign_private_subnet_cidrs(
        self,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cidrs: typing.Sequence[builtins.str],
        cidr_block: _aws_cdk_ceddda9d.CfnResource,
    ) -> None:
        '''Override the template;

        set the IPv6 CIDR for private subnets.

        :param vpc: - The VPC of the subnets.
        :param cidrs: - The possible IPv6 CIDRs to assign.
        :param cidr_block: - The CfnVPCCidrBlock the subnets depend on.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b002de4531052fe21d5d3510d0331c20a853e0a42c33e19aabc0f4c089723954)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cidrs", value=cidrs, expected_type=type_hints["cidrs"])
            check_type(argname="argument cidr_block", value=cidr_block, expected_type=type_hints["cidr_block"])
        return typing.cast(None, jsii.invoke(self, "assignPrivateSubnetCidrs", [vpc, cidrs, cidr_block]))

    @jsii.member(jsii_name="assignPublicSubnetCidrs")
    def _assign_public_subnet_cidrs(
        self,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cidrs: typing.Sequence[builtins.str],
        cidr_block: _aws_cdk_ceddda9d.CfnResource,
    ) -> None:
        '''Override the template;

        set the IPv6 CIDR for isolated subnets.

        :param vpc: - The VPC of the subnets.
        :param cidrs: - The possible IPv6 CIDRs to assign.
        :param cidr_block: - The CfnVPCCidrBlock the subnets depend on.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7693f240a70888012a03fe0b6a47ff72168fbb02ae5de987a68ac482cbe1a967)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cidrs", value=cidrs, expected_type=type_hints["cidrs"])
            check_type(argname="argument cidr_block", value=cidr_block, expected_type=type_hints["cidr_block"])
        return typing.cast(None, jsii.invoke(self, "assignPublicSubnetCidrs", [vpc, cidrs, cidr_block]))

    @jsii.member(jsii_name="validateCidrCount")
    def _validate_cidr_count(
        self,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cidr_count: typing.Optional[jsii.Number] = None,
    ) -> jsii.Number:
        '''Figure out the minimun required CIDR subnets and the number desired.

        :param vpc: - The VPC.
        :param cidr_count: - Optional. Divide the VPC CIDR into this many subsets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__824a74b960abc01e0c39abfdf3e11416c999207fb7b170a7c45ff9e6f49b5189)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cidr_count", value=cidr_count, expected_type=type_hints["cidr_count"])
        return typing.cast(jsii.Number, jsii.invoke(self, "validateCidrCount", [vpc, cidr_count]))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The IPv6-enabled VPC.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))


@jsii.implements(IEncryptedFileSystem)
class EncryptedFileSystem(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.EncryptedFileSystem",
):
    '''An EncryptedFileSystem.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_anonymous_access: typing.Optional[builtins.bool] = None,
        enable_automatic_backups: typing.Optional[builtins.bool] = None,
        encrypted: typing.Optional[builtins.bool] = None,
        file_system_name: typing.Optional[builtins.str] = None,
        file_system_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lifecycle_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
        one_zone: typing.Optional[builtins.bool] = None,
        out_of_infrequent_access_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy] = None,
        performance_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode] = None,
        provisioned_throughput_per_second: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_configuration: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationConfiguration] = None,
        replication_overwrite_protection: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        throughput_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode] = None,
        transition_to_archive_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Creates a new EncryptedFileSystem.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param vpc: VPC to launch the file system in.
        :param allow_anonymous_access: Allow access from anonymous client that doesn't use IAM authentication. Default: false when using ``grantRead``, ``grantWrite``, ``grantRootAccess`` or set ``@aws-cdk/aws-efs:denyAnonymousAccess`` feature flag, otherwise true
        :param enable_automatic_backups: Whether to enable automatic backups for the file system. Default: false
        :param encrypted: Defines if the data at rest in the file system is encrypted or not. Default: - If your application has the '@aws-cdk/aws-efs:defaultEncryptionAtRest' feature flag set, the default is true, otherwise, the default is false.
        :param file_system_name: The file system's name. Default: - CDK generated name
        :param file_system_policy: File system policy is an IAM resource policy used to control NFS access to an EFS file system. Default: none
        :param kms_key: The KMS key used for encryption. This is required to encrypt the data at rest if Default: - if 'encrypted' is true, the default key for EFS (/aws/elasticfilesystem) is used
        :param lifecycle_policy: A policy used by EFS lifecycle management to transition files to the Infrequent Access (IA) storage class. Default: - None. EFS will not transition files to the IA storage class.
        :param one_zone: Whether this is a One Zone file system. If enabled, ``performanceMode`` must be set to ``GENERAL_PURPOSE`` and ``vpcSubnets`` cannot be set. Default: false
        :param out_of_infrequent_access_policy: A policy used by EFS lifecycle management to transition files from Infrequent Access (IA) storage class to primary storage class. Default: - None. EFS will not transition files from IA storage to primary storage.
        :param performance_mode: The performance mode that the file system will operate under. An Amazon EFS file system's performance mode can't be changed after the file system has been created. Updating this property will replace the file system. Default: PerformanceMode.GENERAL_PURPOSE
        :param provisioned_throughput_per_second: Provisioned throughput for the file system. This is a required property if the throughput mode is set to PROVISIONED. Must be at least 1MiB/s. Default: - none, errors out
        :param removal_policy: The removal policy to apply to the file system. Default: RemovalPolicy.RETAIN
        :param replication_configuration: Replication configuration for the file system. Default: - no replication
        :param replication_overwrite_protection: Whether to enable the filesystem's replication overwrite protection or not. Set false if you want to create a read-only filesystem for use as a replication destination. Default: ReplicationOverwriteProtection.ENABLED
        :param security_group: Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic
        :param throughput_mode: Enum to mention the throughput mode of the file system. Default: ThroughputMode.BURSTING
        :param transition_to_archive_policy: The number of days after files were last accessed in primary storage (the Standard storage class) at which to move them to Archive storage. Metadata operations such as listing the contents of a directory don't count as file access events. Default: - None. EFS will not transition files to Archive storage class.
        :param vpc_subnets: Which subnets to place the mount target in the VPC. Default: - the Vpc default strategy if not specified
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0265e0783e7671397c96c0da68a8c3724a7f5c6f4f86f1260aca2a10c0d21309)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EncryptedFileSystemProps(
            vpc=vpc,
            allow_anonymous_access=allow_anonymous_access,
            enable_automatic_backups=enable_automatic_backups,
            encrypted=encrypted,
            file_system_name=file_system_name,
            file_system_policy=file_system_policy,
            kms_key=kms_key,
            lifecycle_policy=lifecycle_policy,
            one_zone=one_zone,
            out_of_infrequent_access_policy=out_of_infrequent_access_policy,
            performance_mode=performance_mode,
            provisioned_throughput_per_second=provisioned_throughput_per_second,
            removal_policy=removal_policy,
            replication_configuration=replication_configuration,
            replication_overwrite_protection=replication_overwrite_protection,
            security_group=security_group,
            throughput_mode=throughput_mode,
            transition_to_archive_policy=transition_to_archive_policy,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="fileSystem")
    def file_system(self) -> _aws_cdk_aws_efs_ceddda9d.IFileSystem:
        '''The EFS file system.'''
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.IFileSystem, jsii.get(self, "fileSystem"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS encryption key.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "key"))


@jsii.implements(IEncryptedLogGroup)
class EncryptedLogGroup(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.EncryptedLogGroup",
):
    '''A log group encrypted by a KMS customer managed key.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        log_group_name: builtins.str,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''Creates a new EncryptedLogGroup.

        :param scope: -
        :param id: -
        :param log_group_name: Name of the log group. We need a log group name ahead of time because otherwise the key policy would create a cyclical dependency.
        :param encryption_key: The KMS Key to encrypt the log group with. Default: A new KMS key will be created
        :param removal_policy: Whether the key and group should be retained when they are removed from the Stack. Default: RemovalPolicy.RETAIN
        :param retention: How long, in days, the log contents will be retained. Default: RetentionDays.TWO_YEARS
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49e62c39421d32db71f8755871011ead455af0c78b5896a1837602bdf3019046)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EncryptedLogGroupProps(
            log_group_name=log_group_name,
            encryption_key=encryption_key,
            removal_policy=removal_policy,
            retention=retention,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS encryption key.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The log group.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "logGroup"))


@jsii.implements(IFargateTask)
class FargateTask(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.FargateTask",
):
    '''An ECS Fargate Task.

    If ``vpcSubnets`` is blank but ``assignPublicIp`` is set, the task will launch
    in Public subnets, otherwise the first available one of Private, Isolated,
    Public, in that order.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        task_definition: _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Creates a new FargateTask.

        :param scope: -
        :param id: -
        :param cluster: The name of the cluster that hosts the service.
        :param task_definition: The task definition that can be launched.
        :param assign_public_ip: Specifies whether the task's elastic network interface receives a public IP address. If true, the task will receive a public IP address. Default: false
        :param security_groups: Existing security groups to use for your task. Default: - a new security group will be created.
        :param vpc_subnets: The subnets to associate with the task. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__534f146c7e4cc1f3a1c4bde7904c9c4c31d25fc5a4101fe2884c58404e8402e2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FargateTaskProps(
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=assign_public_ip,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createRuleTarget")
    def create_rule_target(
        self,
        *,
        container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        launch_type: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LaunchType] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.Tag, typing.Dict[builtins.str, typing.Any]]]] = None,
        task_count: typing.Optional[jsii.Number] = None,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
        max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
    ) -> _aws_cdk_aws_events_targets_ceddda9d.EcsTask:
        '''Create a new EventBridge Rule Target that launches this ECS task.

        :param container_overrides: Container setting overrides. Key is the name of the container to override, value is the values you want to override.
        :param enable_execute_command: Whether or not to enable the execute command functionality for the containers in this task. If true, this enables execute command functionality on all containers in the task. Default: - false
        :param launch_type: Specifies the launch type on which your task is running. The launch type that you specify here must match one of the launch type (compatibilities) of the target task. Default: - 'EC2' if ``isEc2Compatible`` for the ``taskDefinition`` is true, otherwise 'FARGATE'
        :param propagate_tags: Specifies whether to propagate the tags from the task definition to the task. If no value is specified, the tags are not propagated. Default: - Tags will not be propagated
        :param role: Existing IAM role to run the ECS task. Default: - A new IAM role is created
        :param tags: The metadata that you apply to the task to help you categorize and organize them. Each tag consists of a key and an optional value, both of which you define. Default: - No additional tags are applied to the task
        :param task_count: How many tasks should be started when this event is triggered. Default: - 1
        :param dead_letter_queue: The SQS queue to be used as deadLetterQueue. Check out the `considerations for using a dead-letter queue <https://docs.aws.amazon.com/eventbridge/latest/userguide/rule-dlq.html#dlq-considerations>`_. The events not successfully delivered are automatically retried for a specified period of time, depending on the retry policy of the target. If an event is not delivered before all retry attempts are exhausted, it will be sent to the dead letter queue. Default: - no dead-letter queue
        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum value of 60. Maximum value of 86400. Default: Duration.hours(24)
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum value of 0. Maximum value of 185. Default: 185
        '''
        props = EventTargetProps(
            container_overrides=container_overrides,
            enable_execute_command=enable_execute_command,
            launch_type=launch_type,
            propagate_tags=propagate_tags,
            role=role,
            tags=tags,
            task_count=task_count,
            dead_letter_queue=dead_letter_queue,
            max_event_age=max_event_age,
            retry_attempts=retry_attempts,
        )

        return typing.cast(_aws_cdk_aws_events_targets_ceddda9d.EcsTask, jsii.invoke(self, "createRuleTarget", [props]))

    @jsii.member(jsii_name="createStateMachineTask")
    def create_state_machine_task(
        self,
        id: builtins.str,
        *,
        container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        propagated_tag_source: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        revision_number: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.EcsRunTask:
        '''Create a new Step Functions task that launches this ECS task.

        :param id: -
        :param container_overrides: Container setting overrides. Specify the container to use and the overrides to apply. Default: - No overrides
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: false
        :param propagated_tag_source: Specifies whether to propagate the tags from the task definition to the task. An error will be received if you specify the SERVICE option when running a task. Default: - No tags are propagated.
        :param revision_number: The revision number of ECS task definition family. Default: - '$latest'
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85fb243309b374b89bed15793e78468970699ae3408e1bff80b9fea90d384c30)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StateMachineTaskProps(
            container_overrides=container_overrides,
            enable_execute_command=enable_execute_command,
            propagated_tag_source=propagated_tag_source,
            revision_number=revision_number,
            comment=comment,
            credentials=credentials,
            heartbeat=heartbeat,
            heartbeat_timeout=heartbeat_timeout,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            state_name=state_name,
            task_timeout=task_timeout,
            timeout=timeout,
        )

        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.EcsRunTask, jsii.invoke(self, "createStateMachineTask", [id, props]))

    @jsii.member(jsii_name="grantRun")
    def grant_run(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants permission to invoke ecs:RunTask on this task's cluster.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e59c486276b9f2b6a8672a43f0d397ce1022c900e2550b2e738ec1ffc5350624)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRun", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="awsVpcNetworkConfig")
    def aws_vpc_network_config(self) -> FargateAwsVpcConfiguration:
        '''Get the networkConfiguration.awsvpcConfiguration property to run this task.'''
        return typing.cast(FargateAwsVpcConfiguration, jsii.get(self, "awsVpcNetworkConfig"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''The name of the cluster that hosts the service.'''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''The network connections associated with this resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition:
        '''The task definition that can be launched.'''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition, jsii.get(self, "taskDefinition"))


class MysqlDatabase(
    BaseDatabase,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.MysqlDatabase",
):
    '''A MySQL database.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        *,
        admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
        target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Creates a new MysqlDatabase.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param endpoint: The cluster or instance endpoint.
        :param target: The target service or database.
        :param vpc: The VPC where the Lambda function will run.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f8b49e9a462ca68484cf0f82de4d33ebd5834ec487955e46ffc07bde9bd8f48)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MysqlDatabaseProps(
            admin_secret=admin_secret,
            endpoint=endpoint,
            target=target,
            vpc=vpc,
            certificate_authorities_url=certificate_authorities_url,
            character_set=character_set,
            collation=collation,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="forCluster")
    @builtins.classmethod
    def for_cluster(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
        *,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "MysqlDatabase":
        '''Create a new MysqlDatabase inside a DatabaseCluster.

        This method automatically adds the cluster to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param cluster: - The database cluster construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e460fc106dba5a4e51783a91d25e4fe6e9aa747334bed35e69d6d1b46455ac5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = MysqlDatabaseForClusterOptions(
            admin_secret=admin_secret,
            certificate_authorities_url=certificate_authorities_url,
            character_set=character_set,
            collation=collation,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("MysqlDatabase", jsii.sinvoke(cls, "forCluster", [scope, id, cluster, options]))

    @jsii.member(jsii_name="forClusterFromSnapshot")
    @builtins.classmethod
    def for_cluster_from_snapshot(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseClusterFromSnapshot,
        *,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "MysqlDatabase":
        '''Create a new MysqlDatabase inside a DatabaseClusterFromSnapshot.

        This method automatically adds the cluster to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param cluster: - The database cluster construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__551d8ef86fdb714b5f7e76beaf920049f748aef8f6c47f828d1fbd767020e7ac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = MysqlDatabaseForClusterOptions(
            admin_secret=admin_secret,
            certificate_authorities_url=certificate_authorities_url,
            character_set=character_set,
            collation=collation,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("MysqlDatabase", jsii.sinvoke(cls, "forClusterFromSnapshot", [scope, id, cluster, options]))

    @jsii.member(jsii_name="forInstance")
    @builtins.classmethod
    def for_instance(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        instance: _aws_cdk_aws_rds_ceddda9d.DatabaseInstance,
        *,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "MysqlDatabase":
        '''Create a new MysqlDatabase inside a DatabaseInstance.

        This method automatically adds the instance to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param instance: - The database cluster construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__260066f0ec489d929db534ade54503649f22bd4ab6dab8d07f166d73d6620842)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
        options = MysqlDatabaseForClusterOptions(
            admin_secret=admin_secret,
            certificate_authorities_url=certificate_authorities_url,
            character_set=character_set,
            collation=collation,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("MysqlDatabase", jsii.sinvoke(cls, "forInstance", [scope, id, instance, options]))

    @jsii.member(jsii_name="forInstanceFromSnapshot")
    @builtins.classmethod
    def for_instance_from_snapshot(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        instance: _aws_cdk_aws_rds_ceddda9d.DatabaseInstanceFromSnapshot,
        *,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "MysqlDatabase":
        '''Create a new MysqlDatabase inside a DatabaseInstanceFromSnapshot.

        This method automatically adds the instance to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param instance: - The database cluster construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1695b12bdaa415ee8db685b0ee7f8d242277b29c1f985d08d68420d58e5454a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
        options = MysqlDatabaseForClusterOptions(
            admin_secret=admin_secret,
            certificate_authorities_url=certificate_authorities_url,
            character_set=character_set,
            collation=collation,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("MysqlDatabase", jsii.sinvoke(cls, "forInstanceFromSnapshot", [scope, id, instance, options]))

    @jsii.member(jsii_name="forServerlessCluster")
    @builtins.classmethod
    def for_serverless_cluster(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        cluster: _aws_cdk_aws_rds_ceddda9d.ServerlessCluster,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "MysqlDatabase":
        '''Create a new MysqlDatabase inside a DatabaseCluster.

        This method automatically adds the cluster to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param cluster: - The database cluster construct.
        :param vpc: The VPC where the Lambda function will run.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__975dd889f458b8d58eec9946e9ca0200cbde807e7b51c0051384d352a335416c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = MysqlDatabaseForServerlessClusterOptions(
            vpc=vpc,
            admin_secret=admin_secret,
            certificate_authorities_url=certificate_authorities_url,
            character_set=character_set,
            collation=collation,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("MysqlDatabase", jsii.sinvoke(cls, "forServerlessCluster", [scope, id, cluster, options]))

    @jsii.member(jsii_name="forServerlessClusterFromSnapshot")
    @builtins.classmethod
    def for_serverless_cluster_from_snapshot(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        cluster: _aws_cdk_aws_rds_ceddda9d.ServerlessClusterFromSnapshot,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "MysqlDatabase":
        '''Create a new MysqlDatabase inside a DatabaseClusterFromSnapshot.

        This method automatically adds the cluster to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param cluster: - The database cluster construct.
        :param vpc: The VPC where the Lambda function will run.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab6e6a5fae87ee523b61afd29a8cec5bff1377d536d4db1ee21cd72cb69c9204)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = MysqlDatabaseForServerlessClusterOptions(
            vpc=vpc,
            admin_secret=admin_secret,
            certificate_authorities_url=certificate_authorities_url,
            character_set=character_set,
            collation=collation,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("MysqlDatabase", jsii.sinvoke(cls, "forServerlessClusterFromSnapshot", [scope, id, cluster, options]))

    @jsii.member(jsii_name="addUserAsOwner")
    def add_user_as_owner(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned ownership permissions.

        :param secret: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b98832af3053e7681b35efb98c334b02776ce7ff6b904e091d9039ff651dc535)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsOwner", [secret]))

    @jsii.member(jsii_name="addUserAsReader")
    def add_user_as_reader(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned read-only permissions.

        :param secret: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db82561da4bd30262d71d91d7288d4491217ff5d0ee4f1905b44ef1066c5759e)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsReader", [secret]))

    @jsii.member(jsii_name="addUserAsUnprivileged")
    def add_user_as_unprivileged(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user with no permissions.

        :param secret: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__801edc825563ca6c65b0094b4aedc682aae5b85e0b34961344238c6a0d077a57)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsUnprivileged", [secret]))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def _lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="ownerSecrets")
    def _owner_secrets(
        self,
    ) -> typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        return typing.cast(typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], jsii.get(self, "ownerSecrets"))

    @builtins.property
    @jsii.member(jsii_name="readerSecrets")
    def _reader_secrets(
        self,
    ) -> typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        return typing.cast(typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], jsii.get(self, "readerSecrets"))

    @builtins.property
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> _aws_cdk_triggers_ceddda9d.ITrigger:
        '''The CDK Trigger that kicks off the process.

        You can further customize when the trigger fires using ``executeAfter``.
        '''
        return typing.cast(_aws_cdk_triggers_ceddda9d.ITrigger, jsii.get(self, "trigger"))

    @builtins.property
    @jsii.member(jsii_name="unprivilegedSecrets")
    def _unprivileged_secrets(
        self,
    ) -> typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        return typing.cast(typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], jsii.get(self, "unprivilegedSecrets"))


@jsii.data_type(
    jsii_type="shady-island.MysqlDatabaseForClusterOptions",
    jsii_struct_bases=[MysqlDatabaseOptions, BaseDatabaseOptions],
    name_mapping={
        "certificate_authorities_url": "certificateAuthoritiesUrl",
        "character_set": "characterSet",
        "collation": "collation",
        "database_name": "databaseName",
        "security_group": "securityGroup",
        "vpc_subnets": "vpcSubnets",
        "admin_secret": "adminSecret",
    },
)
class MysqlDatabaseForClusterOptions(MysqlDatabaseOptions, BaseDatabaseOptions):
    def __init__(
        self,
        *,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    ) -> None:
        '''Properties to specify when using MysqlDatabase.forCluster().

        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38b6a3cca9f0d2d65164c7888545550422ca286d029d20990c1d75cab32473b6)
            check_type(argname="argument certificate_authorities_url", value=certificate_authorities_url, expected_type=type_hints["certificate_authorities_url"])
            check_type(argname="argument character_set", value=character_set, expected_type=type_hints["character_set"])
            check_type(argname="argument collation", value=collation, expected_type=type_hints["collation"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument admin_secret", value=admin_secret, expected_type=type_hints["admin_secret"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
        }
        if certificate_authorities_url is not None:
            self._values["certificate_authorities_url"] = certificate_authorities_url
        if character_set is not None:
            self._values["character_set"] = character_set
        if collation is not None:
            self._values["collation"] = collation
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if admin_secret is not None:
            self._values["admin_secret"] = admin_secret

    @builtins.property
    def certificate_authorities_url(self) -> typing.Optional[builtins.str]:
        '''The URL to the PEM-encoded Certificate Authority file.

        Normally, we would just assume the Lambda runtime has the certificates to
        trust already installed. Since the current Lambda runtime environments lack
        the newer RDS certificate authority certificates, this option can be used
        to specify a URL to a remote file containing the CAs.

        :default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem

        :see: https://github.com/aws/aws-lambda-base-images/issues/123
        '''
        result = self._values.get("certificate_authorities_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def character_set(self) -> typing.Optional[builtins.str]:
        '''The database default character set to use.

        :default: - "utf8mb4"
        '''
        result = self._values.get("character_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def collation(self) -> typing.Optional[builtins.str]:
        '''The database default collation to use.

        :default: - rely on MySQL to choose the default collation.
        '''
        result = self._values.get("collation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog to create.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group for the Lambda function.

        :default: - a new security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The type of subnets in the VPC where the Lambda function will run.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def admin_secret(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''A Secrets Manager secret that contains administrative credentials.'''
        result = self._values.get("admin_secret")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MysqlDatabaseForClusterOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.MysqlDatabaseForServerlessClusterOptions",
    jsii_struct_bases=[MysqlDatabaseForClusterOptions],
    name_mapping={
        "certificate_authorities_url": "certificateAuthoritiesUrl",
        "character_set": "characterSet",
        "collation": "collation",
        "database_name": "databaseName",
        "security_group": "securityGroup",
        "vpc_subnets": "vpcSubnets",
        "admin_secret": "adminSecret",
        "vpc": "vpc",
    },
)
class MysqlDatabaseForServerlessClusterOptions(MysqlDatabaseForClusterOptions):
    def __init__(
        self,
        *,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    ) -> None:
        '''Properties to specify when using MysqlDatabase.forServerlessCluster().

        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param character_set: The database default character set to use. Default: - "utf8mb4"
        :param collation: The database default collation to use. Default: - rely on MySQL to choose the default collation.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param vpc: The VPC where the Lambda function will run.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__599874e7d6b9afbdc7acf6b8eaeef558257989cbbbffad44bba97a54e0c70115)
            check_type(argname="argument certificate_authorities_url", value=certificate_authorities_url, expected_type=type_hints["certificate_authorities_url"])
            check_type(argname="argument character_set", value=character_set, expected_type=type_hints["character_set"])
            check_type(argname="argument collation", value=collation, expected_type=type_hints["collation"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument admin_secret", value=admin_secret, expected_type=type_hints["admin_secret"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "vpc": vpc,
        }
        if certificate_authorities_url is not None:
            self._values["certificate_authorities_url"] = certificate_authorities_url
        if character_set is not None:
            self._values["character_set"] = character_set
        if collation is not None:
            self._values["collation"] = collation
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if admin_secret is not None:
            self._values["admin_secret"] = admin_secret

    @builtins.property
    def certificate_authorities_url(self) -> typing.Optional[builtins.str]:
        '''The URL to the PEM-encoded Certificate Authority file.

        Normally, we would just assume the Lambda runtime has the certificates to
        trust already installed. Since the current Lambda runtime environments lack
        the newer RDS certificate authority certificates, this option can be used
        to specify a URL to a remote file containing the CAs.

        :default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem

        :see: https://github.com/aws/aws-lambda-base-images/issues/123
        '''
        result = self._values.get("certificate_authorities_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def character_set(self) -> typing.Optional[builtins.str]:
        '''The database default character set to use.

        :default: - "utf8mb4"
        '''
        result = self._values.get("character_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def collation(self) -> typing.Optional[builtins.str]:
        '''The database default collation to use.

        :default: - rely on MySQL to choose the default collation.
        '''
        result = self._values.get("collation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog to create.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group for the Lambda function.

        :default: - a new security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The type of subnets in the VPC where the Lambda function will run.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def admin_secret(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''A Secrets Manager secret that contains administrative credentials.'''
        result = self._values.get("admin_secret")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where the Lambda function will run.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MysqlDatabaseForServerlessClusterOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PostgresqlDatabase(
    BaseDatabase,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.PostgresqlDatabase",
):
    '''A PostgreSQL database.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        *,
        admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
        target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Creates a new PostgresqlDatabase.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param endpoint: The cluster or instance endpoint.
        :param target: The target service or database.
        :param vpc: The VPC where the Lambda function will run.
        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc7e7cc20ce23d3e25489b04f97759542eb520f7e97e0ce6bc18dfaa8e5bbc12)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PostgresqlDatabaseProps(
            admin_secret=admin_secret,
            endpoint=endpoint,
            target=target,
            vpc=vpc,
            owner_secret=owner_secret,
            certificate_authorities_url=certificate_authorities_url,
            encoding=encoding,
            locale=locale,
            schema_name=schema_name,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="forCluster")
    @builtins.classmethod
    def for_cluster(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
        *,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "PostgresqlDatabase":
        '''Create a new PostgresqlDatabase inside a DatabaseCluster.

        This method automatically adds the cluster to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param cluster: - The database cluster construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7a0fe1ede4c3a07ab6cd25b5ab283dc7ff9faec04d2c34c390ad7c913b5a2b4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = PostgresqlDatabaseForClusterOptions(
            admin_secret=admin_secret,
            owner_secret=owner_secret,
            certificate_authorities_url=certificate_authorities_url,
            encoding=encoding,
            locale=locale,
            schema_name=schema_name,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("PostgresqlDatabase", jsii.sinvoke(cls, "forCluster", [scope, id, cluster, options]))

    @jsii.member(jsii_name="forClusterFromSnapshot")
    @builtins.classmethod
    def for_cluster_from_snapshot(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseClusterFromSnapshot,
        *,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "PostgresqlDatabase":
        '''Create a new PostgresqlDatabase inside a DatabaseClusterFromSnapshot.

        This method automatically adds the cluster to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param cluster: - The database cluster construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fa7ada1d9ac65772f2577b8e801f75d7d4c465bb8ce4d6d9c3bd10f81c49bb6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = PostgresqlDatabaseForClusterOptions(
            admin_secret=admin_secret,
            owner_secret=owner_secret,
            certificate_authorities_url=certificate_authorities_url,
            encoding=encoding,
            locale=locale,
            schema_name=schema_name,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("PostgresqlDatabase", jsii.sinvoke(cls, "forClusterFromSnapshot", [scope, id, cluster, options]))

    @jsii.member(jsii_name="forInstance")
    @builtins.classmethod
    def for_instance(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        instance: _aws_cdk_aws_rds_ceddda9d.DatabaseInstance,
        *,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "PostgresqlDatabase":
        '''Create a new PostgresqlDatabase inside a DatabaseInstance.

        This method automatically adds the instance to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param instance: - The database cluster construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b6db24db31da6e6e9ba26e48ffd694f8889fda473eeeeaa5014a06d304aff4e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
        options = PostgresqlDatabaseForClusterOptions(
            admin_secret=admin_secret,
            owner_secret=owner_secret,
            certificate_authorities_url=certificate_authorities_url,
            encoding=encoding,
            locale=locale,
            schema_name=schema_name,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("PostgresqlDatabase", jsii.sinvoke(cls, "forInstance", [scope, id, instance, options]))

    @jsii.member(jsii_name="forInstanceFromSnapshot")
    @builtins.classmethod
    def for_instance_from_snapshot(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        instance: _aws_cdk_aws_rds_ceddda9d.DatabaseInstanceFromSnapshot,
        *,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "PostgresqlDatabase":
        '''Create a new PostgresqlDatabase inside a DatabaseInstanceFromSnapshot.

        This method automatically adds the instance to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param instance: - The database cluster construct.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77dd9c170e142039637aad3ddd270c262643f46b993e5caba8dc52e2aef0e7f7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
        options = PostgresqlDatabaseForClusterOptions(
            admin_secret=admin_secret,
            owner_secret=owner_secret,
            certificate_authorities_url=certificate_authorities_url,
            encoding=encoding,
            locale=locale,
            schema_name=schema_name,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("PostgresqlDatabase", jsii.sinvoke(cls, "forInstanceFromSnapshot", [scope, id, instance, options]))

    @jsii.member(jsii_name="forServerlessCluster")
    @builtins.classmethod
    def for_serverless_cluster(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        cluster: _aws_cdk_aws_rds_ceddda9d.ServerlessCluster,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "PostgresqlDatabase":
        '''Create a new PostgresqlDatabase inside a DatabaseCluster.

        This method automatically adds the cluster to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param cluster: - The database cluster construct.
        :param vpc: The VPC where the Lambda function will run.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3baeaa9e7ce89fe919957c773e4e8bde40b4f16428bf523e1a2143275ca95282)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = PostgresqlDatabaseForServerlessClusterOptions(
            vpc=vpc,
            admin_secret=admin_secret,
            owner_secret=owner_secret,
            certificate_authorities_url=certificate_authorities_url,
            encoding=encoding,
            locale=locale,
            schema_name=schema_name,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("PostgresqlDatabase", jsii.sinvoke(cls, "forServerlessCluster", [scope, id, cluster, options]))

    @jsii.member(jsii_name="forServerlessClusterFromSnapshot")
    @builtins.classmethod
    def for_serverless_cluster_from_snapshot(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        cluster: _aws_cdk_aws_rds_ceddda9d.ServerlessClusterFromSnapshot,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "PostgresqlDatabase":
        '''Create a new PostgresqlDatabase inside a DatabaseClusterFromSnapshot.

        This method automatically adds the cluster to the CloudFormation
        dependencies of the CDK Trigger.

        :param scope: - The Construct that contains this one.
        :param id: - The identifier of this construct.
        :param cluster: - The database cluster construct.
        :param vpc: The VPC where the Lambda function will run.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c90c856101105d45e5cb64879cc947d19cbc687a583e26f9b1485091223bab5e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = PostgresqlDatabaseForServerlessClusterOptions(
            vpc=vpc,
            admin_secret=admin_secret,
            owner_secret=owner_secret,
            certificate_authorities_url=certificate_authorities_url,
            encoding=encoding,
            locale=locale,
            schema_name=schema_name,
            database_name=database_name,
            security_group=security_group,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("PostgresqlDatabase", jsii.sinvoke(cls, "forServerlessClusterFromSnapshot", [scope, id, cluster, options]))

    @jsii.member(jsii_name="addUserAsOwner")
    def add_user_as_owner(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned ownership permissions.

        :param secret: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a37a8c5e6f633566e46baca4056a42db41c18443c08e74dfc3ff552b4cfd428)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsOwner", [secret]))

    @jsii.member(jsii_name="addUserAsReader")
    def add_user_as_reader(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user to be assigned read-only permissions.

        :param secret: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d5540a4c0fc933e9eb3660832f5aa1fe4687fe3fd1cdea48785b115a02b07b5)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsReader", [secret]))

    @jsii.member(jsii_name="addUserAsUnprivileged")
    def add_user_as_unprivileged(
        self,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''Declares a new database user with no permissions.

        :param secret: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a3d237d3b83567103e303ae53ba5a4bfff455e2b4af070dc243258a594b2b71)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(None, jsii.invoke(self, "addUserAsUnprivileged", [secret]))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def _lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="ownerSecrets")
    def _owner_secrets(
        self,
    ) -> typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        return typing.cast(typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], jsii.get(self, "ownerSecrets"))

    @builtins.property
    @jsii.member(jsii_name="readerSecrets")
    def _reader_secrets(
        self,
    ) -> typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        return typing.cast(typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], jsii.get(self, "readerSecrets"))

    @builtins.property
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> _aws_cdk_triggers_ceddda9d.ITrigger:
        '''The CDK Trigger that kicks off the process.

        You can further customize when the trigger fires using ``executeAfter``.
        '''
        return typing.cast(_aws_cdk_triggers_ceddda9d.ITrigger, jsii.get(self, "trigger"))

    @builtins.property
    @jsii.member(jsii_name="unprivilegedSecrets")
    def _unprivileged_secrets(
        self,
    ) -> typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        return typing.cast(typing.List[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], jsii.get(self, "unprivilegedSecrets"))


@jsii.data_type(
    jsii_type="shady-island.PostgresqlDatabaseForClusterOptions",
    jsii_struct_bases=[PostgresqlDatabaseOptions, BaseDatabaseOptions],
    name_mapping={
        "owner_secret": "ownerSecret",
        "certificate_authorities_url": "certificateAuthoritiesUrl",
        "encoding": "encoding",
        "locale": "locale",
        "schema_name": "schemaName",
        "database_name": "databaseName",
        "security_group": "securityGroup",
        "vpc_subnets": "vpcSubnets",
        "admin_secret": "adminSecret",
    },
)
class PostgresqlDatabaseForClusterOptions(
    PostgresqlDatabaseOptions,
    BaseDatabaseOptions,
):
    def __init__(
        self,
        *,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    ) -> None:
        '''Properties to specify when using PostgresqlDatabase.forCluster().

        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8357abd388ea3adc6583c43b42356a112beeaa4310bd6fd47dee13d3d43464b0)
            check_type(argname="argument owner_secret", value=owner_secret, expected_type=type_hints["owner_secret"])
            check_type(argname="argument certificate_authorities_url", value=certificate_authorities_url, expected_type=type_hints["certificate_authorities_url"])
            check_type(argname="argument encoding", value=encoding, expected_type=type_hints["encoding"])
            check_type(argname="argument locale", value=locale, expected_type=type_hints["locale"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument admin_secret", value=admin_secret, expected_type=type_hints["admin_secret"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner_secret": owner_secret,
            "database_name": database_name,
        }
        if certificate_authorities_url is not None:
            self._values["certificate_authorities_url"] = certificate_authorities_url
        if encoding is not None:
            self._values["encoding"] = encoding
        if locale is not None:
            self._values["locale"] = locale
        if schema_name is not None:
            self._values["schema_name"] = schema_name
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if admin_secret is not None:
            self._values["admin_secret"] = admin_secret

    @builtins.property
    def owner_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The Secrets Manager secret for the owner of the schema.'''
        result = self._values.get("owner_secret")
        assert result is not None, "Required property 'owner_secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def certificate_authorities_url(self) -> typing.Optional[builtins.str]:
        '''The URL to the PEM-encoded Certificate Authority file.

        Normally, we would just assume the Lambda runtime has the certificates to
        trust already installed. Since the current Lambda runtime environments lack
        the newer RDS certificate authority certificates, this option can be used
        to specify a URL to a remote file containing the CAs.

        :default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem

        :see: https://github.com/aws/aws-lambda-base-images/issues/123
        '''
        result = self._values.get("certificate_authorities_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encoding(self) -> typing.Optional[builtins.str]:
        '''The database default encoding set to use.

        :default: - "UTF8"
        '''
        result = self._values.get("encoding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locale(self) -> typing.Optional[builtins.str]:
        '''The database default locale to use.

        :default: - rely on PostgreSQL to choose the default locale.
        '''
        result = self._values.get("locale")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''The name of the schema to create.

        :default: - The username of the ownerSecret.
        '''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog to create.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group for the Lambda function.

        :default: - a new security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The type of subnets in the VPC where the Lambda function will run.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def admin_secret(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''A Secrets Manager secret that contains administrative credentials.'''
        result = self._values.get("admin_secret")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PostgresqlDatabaseForClusterOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.PostgresqlDatabaseForServerlessClusterOptions",
    jsii_struct_bases=[PostgresqlDatabaseForClusterOptions],
    name_mapping={
        "owner_secret": "ownerSecret",
        "certificate_authorities_url": "certificateAuthoritiesUrl",
        "encoding": "encoding",
        "locale": "locale",
        "schema_name": "schemaName",
        "database_name": "databaseName",
        "security_group": "securityGroup",
        "vpc_subnets": "vpcSubnets",
        "admin_secret": "adminSecret",
        "vpc": "vpc",
    },
)
class PostgresqlDatabaseForServerlessClusterOptions(
    PostgresqlDatabaseForClusterOptions,
):
    def __init__(
        self,
        *,
        owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        certificate_authorities_url: typing.Optional[builtins.str] = None,
        encoding: typing.Optional[builtins.str] = None,
        locale: typing.Optional[builtins.str] = None,
        schema_name: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    ) -> None:
        '''Properties to specify when using PostgresqlDatabase.forServerlessCluster().

        :param owner_secret: The Secrets Manager secret for the owner of the schema.
        :param certificate_authorities_url: The URL to the PEM-encoded Certificate Authority file. Normally, we would just assume the Lambda runtime has the certificates to trust already installed. Since the current Lambda runtime environments lack the newer RDS certificate authority certificates, this option can be used to specify a URL to a remote file containing the CAs. Default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem
        :param encoding: The database default encoding set to use. Default: - "UTF8"
        :param locale: The database default locale to use. Default: - rely on PostgreSQL to choose the default locale.
        :param schema_name: The name of the schema to create. Default: - The username of the ownerSecret.
        :param database_name: The name of the database/catalog to create.
        :param security_group: The security group for the Lambda function. Default: - a new security group is created
        :param vpc_subnets: The type of subnets in the VPC where the Lambda function will run. Default: - the Vpc default strategy if not specified.
        :param admin_secret: A Secrets Manager secret that contains administrative credentials.
        :param vpc: The VPC where the Lambda function will run.
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4999c984cd9cb820de708151dd169158c8305804e9a212fe428de8aac1ef89a)
            check_type(argname="argument owner_secret", value=owner_secret, expected_type=type_hints["owner_secret"])
            check_type(argname="argument certificate_authorities_url", value=certificate_authorities_url, expected_type=type_hints["certificate_authorities_url"])
            check_type(argname="argument encoding", value=encoding, expected_type=type_hints["encoding"])
            check_type(argname="argument locale", value=locale, expected_type=type_hints["locale"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument admin_secret", value=admin_secret, expected_type=type_hints["admin_secret"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner_secret": owner_secret,
            "database_name": database_name,
            "vpc": vpc,
        }
        if certificate_authorities_url is not None:
            self._values["certificate_authorities_url"] = certificate_authorities_url
        if encoding is not None:
            self._values["encoding"] = encoding
        if locale is not None:
            self._values["locale"] = locale
        if schema_name is not None:
            self._values["schema_name"] = schema_name
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if admin_secret is not None:
            self._values["admin_secret"] = admin_secret

    @builtins.property
    def owner_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The Secrets Manager secret for the owner of the schema.'''
        result = self._values.get("owner_secret")
        assert result is not None, "Required property 'owner_secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def certificate_authorities_url(self) -> typing.Optional[builtins.str]:
        '''The URL to the PEM-encoded Certificate Authority file.

        Normally, we would just assume the Lambda runtime has the certificates to
        trust already installed. Since the current Lambda runtime environments lack
        the newer RDS certificate authority certificates, this option can be used
        to specify a URL to a remote file containing the CAs.

        :default: - https://truststore.pki.rds.amazonaws.com/REGION/REGION-bundle.pem

        :see: https://github.com/aws/aws-lambda-base-images/issues/123
        '''
        result = self._values.get("certificate_authorities_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encoding(self) -> typing.Optional[builtins.str]:
        '''The database default encoding set to use.

        :default: - "UTF8"
        '''
        result = self._values.get("encoding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locale(self) -> typing.Optional[builtins.str]:
        '''The database default locale to use.

        :default: - rely on PostgreSQL to choose the default locale.
        '''
        result = self._values.get("locale")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''The name of the schema to create.

        :default: - The username of the ownerSecret.
        '''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the database/catalog to create.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group for the Lambda function.

        :default: - a new security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The type of subnets in the VPC where the Lambda function will run.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def admin_secret(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''A Secrets Manager secret that contains administrative credentials.'''
        result = self._values.get("admin_secret")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where the Lambda function will run.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PostgresqlDatabaseForServerlessClusterOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AssignOnLaunch",
    "AssignOnLaunchProps",
    "BaseDatabase",
    "BaseDatabaseOptions",
    "BaseDatabaseProps",
    "BaseFargateTaskProps",
    "CidrContext",
    "CidrContextProps",
    "ContextLoader",
    "ContextLoadingStage",
    "ContextLoadingStageProps",
    "DeploymentTierStage",
    "DeploymentTierStageProps",
    "EncryptedFileSystem",
    "EncryptedFileSystemProps",
    "EncryptedLogGroup",
    "EncryptedLogGroupProps",
    "EventTargetProps",
    "FargateAwsVpcConfiguration",
    "FargateTask",
    "FargateTaskImageOptions",
    "FargateTaskProps",
    "IAssignOnLaunch",
    "ICidrContext",
    "IDatabase",
    "IEncryptedFileSystem",
    "IEncryptedLogGroup",
    "IFargateTask",
    "IRunnableFargateTask",
    "MysqlDatabase",
    "MysqlDatabaseForClusterOptions",
    "MysqlDatabaseForServerlessClusterOptions",
    "MysqlDatabaseOptions",
    "MysqlDatabaseProps",
    "PostgresqlDatabase",
    "PostgresqlDatabaseForClusterOptions",
    "PostgresqlDatabaseForServerlessClusterOptions",
    "PostgresqlDatabaseOptions",
    "PostgresqlDatabaseProps",
    "PrioritizedLines",
    "RunnableFargateTask",
    "RunnableFargateTaskProps",
    "StateMachineTaskProps",
    "Tier",
    "TierTagger",
    "UserDataBuilder",
    "Workload",
    "WorkloadProps",
    "automation",
    "configuration",
    "networking",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import automation
from . import configuration
from . import networking

def _typecheckingstub__bf6464fd9d48d82d0db14a3cccbdb92cb250ed4fe6d6bd38b8e06d86417f53f2(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb5a876ef1282aa92f1dad8eb5bf7808d5fb9ec194106c40e9fd2365c63e177(
    *,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__638e3f17e92b33884a123777384d2096ff52784838ea6a387eb453df4acabdf0(
    *,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
    target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2d82fd0175001f3a0180f4788e513f4bb8d14a42ee961f880b1ba5b5ed8e2bc(
    *,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__050e47d5b52c553cfe8b87e6673a27b8787fd0db2253c4e7b62521814ed5ae1d(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    address_pool: typing.Optional[builtins.str] = None,
    assign_address_on_launch: typing.Optional[builtins.bool] = None,
    cidr_block: typing.Optional[builtins.str] = None,
    cidr_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92ecc06c0a44e3636156ab00eb64f42cc69e3471e1fdad7321210a3770b10cfd(
    filename: builtins.str,
    node: _constructs_77d1e7e8.Node,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9e712087c9d94895740eba9c235f48c4ad49d51b9e4dbb62f7a6fd29fb1620(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    context_file: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__277bf43d40bebd128d971cb569404cd830e470eabdf722b84fcad858785a344e(
    *,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
    stage_name: typing.Optional[builtins.str] = None,
    context_file: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f9a764490bae5a194e32e533087b38ed7fd9f77f0cf0c41a14406ab48f535ac(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    tier: Tier,
    add_tag: typing.Optional[builtins.bool] = None,
    context_file: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5542255303c0108ee3ba400c22bcd0da4bf25b7393c820287f49f7738999e86b(
    *,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
    stage_name: typing.Optional[builtins.str] = None,
    context_file: typing.Optional[builtins.str] = None,
    tier: Tier,
    add_tag: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fd1576cc635c21f66d4c77cc0746612de310b047b380081961173028162c533(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_anonymous_access: typing.Optional[builtins.bool] = None,
    enable_automatic_backups: typing.Optional[builtins.bool] = None,
    encrypted: typing.Optional[builtins.bool] = None,
    file_system_name: typing.Optional[builtins.str] = None,
    file_system_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lifecycle_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
    one_zone: typing.Optional[builtins.bool] = None,
    out_of_infrequent_access_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy] = None,
    performance_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode] = None,
    provisioned_throughput_per_second: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_configuration: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationConfiguration] = None,
    replication_overwrite_protection: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    throughput_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode] = None,
    transition_to_archive_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__336d3d15e4b6b1d5a3f1d25302a1b6aa54f3525152e85c4efc9022074bbc84ef(
    *,
    log_group_name: builtins.str,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__897dc07b48a2eb17398fb35f77b60b5ef5a46dc3283b5be7f1587d908f9d4f1a(
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue] = None,
    max_event_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    retry_attempts: typing.Optional[jsii.Number] = None,
    container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    launch_type: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LaunchType] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_events_targets_ceddda9d.Tag, typing.Dict[builtins.str, typing.Any]]]] = None,
    task_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51c80a2d906cd1addfd30d9a8ba48b35ba0ff6bcdacdd5b465c97943ae8633de(
    *,
    assign_public_ip: typing.Optional[builtins.str] = None,
    security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09105b6ea9eae34595c8cb0f3710694a2e074d2c7f093bb2ddc1d83da13a547d(
    *,
    image: _aws_cdk_aws_ecs_ceddda9d.ContainerImage,
    command: typing.Optional[typing.Sequence[builtins.str]] = None,
    container_name: typing.Optional[builtins.str] = None,
    container_port: typing.Optional[jsii.Number] = None,
    docker_labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    enable_logging: typing.Optional[builtins.bool] = None,
    entry_point: typing.Optional[typing.Sequence[builtins.str]] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    family: typing.Optional[builtins.str] = None,
    log_driver: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.LogDriver] = None,
    secrets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]] = None,
    task_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48906dd5b4e8a7c31ff88ad932bf788d1acda56897daf0ddbd9a63f01a440cb3(
    *,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    task_definition: _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa04cb10e6d6f3a14885b573c1500a16f427d23d29420c9282c7b47bf510a8d5(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3afa465271b9422d8a26592c854f527c297eff5926d505012bdcd9c9c73a12c2(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85cd5b491150e098fe53def9ea0f1c89f9845fb5fd9030a27ecc6148e091c23b(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48c037a9d29925d5cc91f797f5826290b380d79fe3f87a6eda42191172d636cc(
    id: builtins.str,
    *,
    container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    propagated_tag_source: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    revision_number: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11d3684d379a3f021959b8059e0a87bd5a4301f03fcadfcfeb09484fc5a6ba68(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d514adc7950cfce4177d69ffd36ac66492872090c9fd306589f40229c06f7659(
    *,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b42b3dc678f48a79d6d0214768d515a19ddc59d87098698b7f0ef95f408ac76b(
    *,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
    target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6710a06e4f6994850322149d3a968d6631f7dee52c2feaa18bec04cfc18126ed(
    *,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74ccdbb57cdd98a0b070eec3cf06b644c97e97df1c05f3475ccf70231f6d0f73(
    *,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
    target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6e48c7b1cd24344a1cdbb27f3f7aea01ec3a2ce2f1bf2ce870bcc01f662aa91(
    *,
    lines: typing.Sequence[builtins.str],
    priority: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dec19256510924858e71ecf29fae220381410f999cfdc1c91b843af29b20b2e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    task_image_options: typing.Optional[typing.Union[FargateTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a0bd282b45a84f20604bbb11f720ffdb12ec08cdb90c52b55e8805df57e3fc9(
    prefix: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cb2fc9c646ea45b7bcc43751c1719285f05896779ef4f2931636d2e5ba77503(
    scope: _constructs_77d1e7e8.Construct,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bc78880d3229e5744813c8ea28556d3cb503c816f71a3d30639005c586811d5(
    *,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    task_image_options: typing.Optional[typing.Union[FargateTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b318285290bae1c9ced1c85c8d15ba99f3be22a5cc9028602343e8d66cac1711(
    *,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    propagated_tag_source: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    revision_number: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__530a177d1cc816f59517c3e52dceeb99d4c7774e513d4d6bf96e414b10eee80f(
    id: builtins.str,
    label: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b29107dd146351897f69274b70bc4ebc35a56ff67af9f9ba3babcc98acfbfcf3(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2f20e1b838706908cb4dc457364ab4d6a3ba246f70b4d648ff5df5ead1e52df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c184966e811a15ee5af7f9b885e27fa53713f5978c027ccfe09f4878a486801(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cf79e20cf3b8dc496886cc4ba33e3e35eb2f7aa6b620c4974179e5aa009b220(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc74e7f1b826ca0249b2f9a045466e09289c315ccc1cc9056778d302475eac52(
    other: Tier,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__990a574adf189a6673820477e428083f72ec0266d44b5e27d24c121fa0e63484(
    tier: Tier,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a15fa1bc21541be12e0110218ecd1f0ad7b7835b2f7f90b8fc12445814d93ef6(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f56dc72e2b8d9e69be937435e41fa771eb82b99df61762e67305a1aa7d1a25cd(
    *commands: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6114eade1a4b4469c7ffa50dbde1b95b36c5b299d356317bbe384e4caf526133(
    priority: jsii.Number,
    *commands: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bc677f9592ce3b6c83e0b51756bcbfa8439cf4279d746c77e45e81d3ac83c74(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    tier: Tier,
    base_domain_name: typing.Optional[builtins.str] = None,
    context_file: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    workload_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96ebb0ba06e254e10fe2379e1883988108104f296135702e61231d2437cee11e(
    x: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e27f5fc4333ac0563c57801a0b496252f1fe2f4b9a122724ccfbfec6d7998dbf(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9ba1202ef7d254e0e9e1f79faf21a7241261ea59fec1d6b565e8f9c5709830b(
    id: builtins.str,
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd2eedf91b5d4e25d97e311a1a26f03b3db1e8d5bba809f0a2bd20df11d9bdfb(
    *stacks: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19f32a870d457362c1bd937f00bb736bfc4263b2f555fd93d34c4bf7dd53f7a7(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46d21735e564e0f2e2aaeb9fd18b82adda3268ccc0278f45c2386e1cb3a55271(
    *,
    tier: Tier,
    base_domain_name: typing.Optional[builtins.str] = None,
    context_file: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    workload_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef34bf6f916957f913c4aa2b3459686556aaef0c4dde4b4cd1da18bd1bdf38e1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdb1e2eeb461f1db3ac370047353ac0ea52393d0b3bd224f768e3785beb6c62f(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    *,
    admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
    target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8321fe7ebfabec2cfb0821b009699253ead41aa4a47ace8c7c1cf6dd0e3316f7(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ded6f3a40e3d6bb06fc7f9e26451f444265c699a2074e084da4b942c563b230(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efc753d3732cabfad2d16ab9d335759b80f3f0ebffd50d1f02ac84e731fca0c9(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b0de4a00dc5c9be3f27b4ab96a0dcd78e40528295ed76dce57eec996acc188c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    address_pool: typing.Optional[builtins.str] = None,
    assign_address_on_launch: typing.Optional[builtins.bool] = None,
    cidr_block: typing.Optional[builtins.str] = None,
    cidr_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b002de4531052fe21d5d3510d0331c20a853e0a42c33e19aabc0f4c089723954(
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cidrs: typing.Sequence[builtins.str],
    cidr_block: _aws_cdk_ceddda9d.CfnResource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7693f240a70888012a03fe0b6a47ff72168fbb02ae5de987a68ac482cbe1a967(
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cidrs: typing.Sequence[builtins.str],
    cidr_block: _aws_cdk_ceddda9d.CfnResource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__824a74b960abc01e0c39abfdf3e11416c999207fb7b170a7c45ff9e6f49b5189(
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cidr_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0265e0783e7671397c96c0da68a8c3724a7f5c6f4f86f1260aca2a10c0d21309(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_anonymous_access: typing.Optional[builtins.bool] = None,
    enable_automatic_backups: typing.Optional[builtins.bool] = None,
    encrypted: typing.Optional[builtins.bool] = None,
    file_system_name: typing.Optional[builtins.str] = None,
    file_system_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lifecycle_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
    one_zone: typing.Optional[builtins.bool] = None,
    out_of_infrequent_access_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy] = None,
    performance_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode] = None,
    provisioned_throughput_per_second: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_configuration: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationConfiguration] = None,
    replication_overwrite_protection: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    throughput_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode] = None,
    transition_to_archive_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49e62c39421d32db71f8755871011ead455af0c78b5896a1837602bdf3019046(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    log_group_name: builtins.str,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__534f146c7e4cc1f3a1c4bde7904c9c4c31d25fc5a4101fe2884c58404e8402e2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    task_definition: _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85fb243309b374b89bed15793e78468970699ae3408e1bff80b9fea90d384c30(
    id: builtins.str,
    *,
    container_overrides: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ContainerOverride, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    propagated_tag_source: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    revision_number: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59c486276b9f2b6a8672a43f0d397ce1022c900e2550b2e738ec1ffc5350624(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f8b49e9a462ca68484cf0f82de4d33ebd5834ec487955e46ffc07bde9bd8f48(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    *,
    admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
    target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e460fc106dba5a4e51783a91d25e4fe6e9aa747334bed35e69d6d1b46455ac5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
    *,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__551d8ef86fdb714b5f7e76beaf920049f748aef8f6c47f828d1fbd767020e7ac(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseClusterFromSnapshot,
    *,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__260066f0ec489d929db534ade54503649f22bd4ab6dab8d07f166d73d6620842(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    instance: _aws_cdk_aws_rds_ceddda9d.DatabaseInstance,
    *,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1695b12bdaa415ee8db685b0ee7f8d242277b29c1f985d08d68420d58e5454a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    instance: _aws_cdk_aws_rds_ceddda9d.DatabaseInstanceFromSnapshot,
    *,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__975dd889f458b8d58eec9946e9ca0200cbde807e7b51c0051384d352a335416c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    cluster: _aws_cdk_aws_rds_ceddda9d.ServerlessCluster,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab6e6a5fae87ee523b61afd29a8cec5bff1377d536d4db1ee21cd72cb69c9204(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    cluster: _aws_cdk_aws_rds_ceddda9d.ServerlessClusterFromSnapshot,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b98832af3053e7681b35efb98c334b02776ce7ff6b904e091d9039ff651dc535(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db82561da4bd30262d71d91d7288d4491217ff5d0ee4f1905b44ef1066c5759e(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__801edc825563ca6c65b0094b4aedc682aae5b85e0b34961344238c6a0d077a57(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38b6a3cca9f0d2d65164c7888545550422ca286d029d20990c1d75cab32473b6(
    *,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__599874e7d6b9afbdc7acf6b8eaeef558257989cbbbffad44bba97a54e0c70115(
    *,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    character_set: typing.Optional[builtins.str] = None,
    collation: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc7e7cc20ce23d3e25489b04f97759542eb520f7e97e0ce6bc18dfaa8e5bbc12(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    *,
    admin_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    endpoint: _aws_cdk_aws_rds_ceddda9d.Endpoint,
    target: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7a0fe1ede4c3a07ab6cd25b5ab283dc7ff9faec04d2c34c390ad7c913b5a2b4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
    *,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fa7ada1d9ac65772f2577b8e801f75d7d4c465bb8ce4d6d9c3bd10f81c49bb6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseClusterFromSnapshot,
    *,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b6db24db31da6e6e9ba26e48ffd694f8889fda473eeeeaa5014a06d304aff4e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    instance: _aws_cdk_aws_rds_ceddda9d.DatabaseInstance,
    *,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77dd9c170e142039637aad3ddd270c262643f46b993e5caba8dc52e2aef0e7f7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    instance: _aws_cdk_aws_rds_ceddda9d.DatabaseInstanceFromSnapshot,
    *,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3baeaa9e7ce89fe919957c773e4e8bde40b4f16428bf523e1a2143275ca95282(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    cluster: _aws_cdk_aws_rds_ceddda9d.ServerlessCluster,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c90c856101105d45e5cb64879cc947d19cbc687a583e26f9b1485091223bab5e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    cluster: _aws_cdk_aws_rds_ceddda9d.ServerlessClusterFromSnapshot,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a37a8c5e6f633566e46baca4056a42db41c18443c08e74dfc3ff552b4cfd428(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d5540a4c0fc933e9eb3660832f5aa1fe4687fe3fd1cdea48785b115a02b07b5(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a3d237d3b83567103e303ae53ba5a4bfff455e2b4af070dc243258a594b2b71(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8357abd388ea3adc6583c43b42356a112beeaa4310bd6fd47dee13d3d43464b0(
    *,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4999c984cd9cb820de708151dd169158c8305804e9a212fe428de8aac1ef89a(
    *,
    owner_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    certificate_authorities_url: typing.Optional[builtins.str] = None,
    encoding: typing.Optional[builtins.str] = None,
    locale: typing.Optional[builtins.str] = None,
    schema_name: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    admin_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
) -> None:
    """Type checking stubs"""
    pass
