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
import aws_cdk.aws_autoscaling as _aws_cdk_aws_autoscaling_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


class Address(metaclass=jsii.JSIIMeta, jsii_type="shady-island.networking.Address"):
    '''An IPv4 or IPv6 address (or range of addresses).'''

    @jsii.member(jsii_name="anyIpv4")
    @builtins.classmethod
    def any_ipv4(cls) -> "Address":
        '''Creates an address that represents the entire IPv4 addressing space.

        :return: The IPv4 network address
        '''
        return typing.cast("Address", jsii.sinvoke(cls, "anyIpv4", []))

    @jsii.member(jsii_name="anyIpv6")
    @builtins.classmethod
    def any_ipv6(cls) -> "Address":
        '''Creates an address that represents the entire IPv4 addressing space.

        :return: The IPv4 network address
        '''
        return typing.cast("Address", jsii.sinvoke(cls, "anyIpv6", []))

    @jsii.member(jsii_name="ipv4")
    @builtins.classmethod
    def ipv4(cls, address: builtins.str) -> "Address":
        '''Creates an IPv4 network address (either a single address or a range).

        :param address: - The IP address (with optional netmask).

        :return: The IPv4 network address
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a987c1ff9ba835df538a008b65cb8eb591f8caa74f1db2104b731c619dee7b8)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
        return typing.cast("Address", jsii.sinvoke(cls, "ipv4", [address]))

    @jsii.member(jsii_name="ipv6")
    @builtins.classmethod
    def ipv6(cls, address: builtins.str) -> "Address":
        '''Creates an IPv6 network address (either a single address or a range).

        :param address: - The IP address (with optional prefix length).

        :return: The IPv6 network address
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c94a54535c07938766b16900ce0d84b06136bc5847f54b6161c4ebecaa3763e0)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
        return typing.cast("Address", jsii.sinvoke(cls, "ipv6", [address]))

    @jsii.member(jsii_name="isAny")
    def is_any(self) -> builtins.bool:
        '''Whether this address represents everything in the addressing space.

        :return: True if this address represents all addresses
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "isAny", []))

    @jsii.member(jsii_name="isIpv4")
    def is_ipv4(self) -> builtins.bool:
        '''Whether this address is an IPv4 address.

        :return: True if this is an IPv4 address
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "isIpv4", []))

    @jsii.member(jsii_name="isIpv6")
    def is_ipv6(self) -> builtins.bool:
        '''Whether this address is an IPv6 address.

        :return: True if this is an IPv6 address
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "isIpv6", []))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))


class AddressingV4(
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.AddressingV4",
):
    '''Used to assign IPv4 addresses to a Network Interface.'''

    @jsii.member(jsii_name="prefixCount")
    @builtins.classmethod
    def prefix_count(cls, count: jsii.Number) -> "AddressingV4":
        '''Specify a number of IPv4 delegated prefixes to automatically assign.

        :param count: - The number of automatic IPv4 delegated prefixes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2cddb2547e4ed3f4826e1acff079d40a4ba476ac141e3281f8b106c7455a04f)
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
        return typing.cast("AddressingV4", jsii.sinvoke(cls, "prefixCount", [count]))

    @jsii.member(jsii_name="prefixes")
    @builtins.classmethod
    def prefixes(cls, prefixes: typing.Sequence[builtins.str]) -> "AddressingV4":
        '''Specify one or more IPv4 delegated prefixes to assign.

        IPv4 prefixes must be within a CIDR of /28.

        :param prefixes: - The IPv4 delegated prefixes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01734a2088506c2015ca7bad849bebf81f4652662c5abd2af6e22d7e89d72a62)
            check_type(argname="argument prefixes", value=prefixes, expected_type=type_hints["prefixes"])
        return typing.cast("AddressingV4", jsii.sinvoke(cls, "prefixes", [prefixes]))

    @jsii.member(jsii_name="privateAddress")
    @builtins.classmethod
    def private_address(cls, ip: builtins.str) -> "AddressingV4":
        '''Specify a private IPv4 address.

        :param ip: - The actual IP address.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a558c981ad684205ae14b30ac86b63891341637e8de2255215f0d7fa9890c208)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
        return typing.cast("AddressingV4", jsii.sinvoke(cls, "privateAddress", [ip]))

    @jsii.member(jsii_name="privateAddressAndSecondaryCount")
    @builtins.classmethod
    def private_address_and_secondary_count(
        cls,
        primary: builtins.str,
        count: jsii.Number,
    ) -> "AddressingV4":
        '''Specify a primary IPv4 address and a number of secondary addresses.

        :param primary: - The primary address.
        :param count: - The number of secondary addresses.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbd385d7d0a4b0a0306d6f92007994dc4caacd4f45b60696b74868ae7d9af7dc)
            check_type(argname="argument primary", value=primary, expected_type=type_hints["primary"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
        return typing.cast("AddressingV4", jsii.sinvoke(cls, "privateAddressAndSecondaryCount", [primary, count]))

    @jsii.member(jsii_name="privateAddresses")
    @builtins.classmethod
    def private_addresses(
        cls,
        primary: builtins.str,
        *secondary: builtins.str,
    ) -> "AddressingV4":
        '''Specify a primary IPv4 address and one or more secondary IPv4 addresses.

        :param primary: - The primary address.
        :param secondary: - Any secondary addresses.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__116c136600050bf89a1560721d3862fb3f20a3f55eeb11598bcf8676ad8363f8)
            check_type(argname="argument primary", value=primary, expected_type=type_hints["primary"])
            check_type(argname="argument secondary", value=secondary, expected_type=typing.Tuple[type_hints["secondary"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("AddressingV4", jsii.sinvoke(cls, "privateAddresses", [primary, *secondary]))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "props"))


class AddressingV6(
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.AddressingV6",
):
    '''Used to assign IPv6 addresses to a Network Interface.'''

    @jsii.member(jsii_name="addressCount")
    @builtins.classmethod
    def address_count(
        cls,
        count: jsii.Number,
        enable_primary: typing.Optional[builtins.bool] = None,
    ) -> "AddressingV6":
        '''Specify a number of IPv6 addresses to automatically assign.

        :param count: - The number of automatic IPv6 addresses.
        :param enable_primary: - Whether to enable a primary IPv6 GUA (default: no).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ed7da7903260aeba9877acff158981d9b2220d2610bb60c1601ce4a1cd07c80)
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument enable_primary", value=enable_primary, expected_type=type_hints["enable_primary"])
        return typing.cast("AddressingV6", jsii.sinvoke(cls, "addressCount", [count, enable_primary]))

    @jsii.member(jsii_name="addresses")
    @builtins.classmethod
    def addresses(
        cls,
        ips: typing.Sequence[builtins.str],
        enable_primary: typing.Optional[builtins.bool] = None,
    ) -> "AddressingV6":
        '''Specify one or more IPv6 addresses to assign.

        :param ips: - The IPv6 addresses.
        :param enable_primary: - Whether to enable a primary IPv6 GUA (default: no).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16d92cdccfc5fcd12837debeb037bdf436f91a88257fd9f12e9dbea4b9846925)
            check_type(argname="argument ips", value=ips, expected_type=type_hints["ips"])
            check_type(argname="argument enable_primary", value=enable_primary, expected_type=type_hints["enable_primary"])
        return typing.cast("AddressingV6", jsii.sinvoke(cls, "addresses", [ips, enable_primary]))

    @jsii.member(jsii_name="prefixCount")
    @builtins.classmethod
    def prefix_count(
        cls,
        count: jsii.Number,
        enable_primary: typing.Optional[builtins.bool] = None,
    ) -> "AddressingV6":
        '''Specify a number of IPv6 delegated prefixes to automatically assign.

        :param count: - The number of automatic IPv6 delegated prefixes.
        :param enable_primary: - Whether to enable a primary IPv6 GUA (default: no).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cd14df44bfcf87b8b5d2f04ad616f4497ecc8908a4f4f91379e46248a6772ee)
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument enable_primary", value=enable_primary, expected_type=type_hints["enable_primary"])
        return typing.cast("AddressingV6", jsii.sinvoke(cls, "prefixCount", [count, enable_primary]))

    @jsii.member(jsii_name="prefixes")
    @builtins.classmethod
    def prefixes(
        cls,
        prefixes: typing.Sequence[builtins.str],
        enable_primary: typing.Optional[builtins.bool] = None,
    ) -> "AddressingV6":
        '''Specify one or more IPv6 delegated prefixes to assign.

        IPv6 prefixes must be within a CIDR of /80.

        :param prefixes: - The IPv6 delegated prefixes.
        :param enable_primary: - Whether to enable a primary IPv6 GUA (default: no).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4a8ad5afeb3637eae637f3afd75db4bc00b4274d8a8d486fdf734229f61687f)
            check_type(argname="argument prefixes", value=prefixes, expected_type=type_hints["prefixes"])
            check_type(argname="argument enable_primary", value=enable_primary, expected_type=type_hints["enable_primary"])
        return typing.cast("AddressingV6", jsii.sinvoke(cls, "prefixes", [prefixes, enable_primary]))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="shady-island.networking.CrossAccountDelegationDomainProps",
    jsii_struct_bases=[],
    name_mapping={
        "delegation_role": "delegationRole",
        "subdomain": "subdomain",
        "assume_role_region": "assumeRoleRegion",
        "parent_hosted_zone_id": "parentHostedZoneId",
        "parent_hosted_zone_name": "parentHostedZoneName",
        "removal_policy": "removalPolicy",
        "ttl": "ttl",
    },
)
class CrossAccountDelegationDomainProps:
    def __init__(
        self,
        *,
        delegation_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        subdomain: builtins.str,
        assume_role_region: typing.Optional[builtins.str] = None,
        parent_hosted_zone_id: typing.Optional[builtins.str] = None,
        parent_hosted_zone_name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''Constructor properties for CrossAccountDelegationDomain.

        :param delegation_role: The delegation role in the parent account.
        :param subdomain: The subdomain in the parent hosted zone.
        :param assume_role_region: Region from which to obtain temporary credentials. Default: - the Route53 signing region in the current partition
        :param parent_hosted_zone_id: The hosted zone id in the parent account. Default: - hosted zone ID will be looked up based on the zone name
        :param parent_hosted_zone_name: The hosted zone name in the parent account. Default: - no zone name
        :param removal_policy: The removal policy to apply. Default: RemovalPolicy.DESTROY
        :param ttl: The resource record cache time to live (TTL). Default: Duration.days(2)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9136690bd7d16bb7a371b715fe1211443861d3a8d6541eaab01cf4170ca77d17)
            check_type(argname="argument delegation_role", value=delegation_role, expected_type=type_hints["delegation_role"])
            check_type(argname="argument subdomain", value=subdomain, expected_type=type_hints["subdomain"])
            check_type(argname="argument assume_role_region", value=assume_role_region, expected_type=type_hints["assume_role_region"])
            check_type(argname="argument parent_hosted_zone_id", value=parent_hosted_zone_id, expected_type=type_hints["parent_hosted_zone_id"])
            check_type(argname="argument parent_hosted_zone_name", value=parent_hosted_zone_name, expected_type=type_hints["parent_hosted_zone_name"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "delegation_role": delegation_role,
            "subdomain": subdomain,
        }
        if assume_role_region is not None:
            self._values["assume_role_region"] = assume_role_region
        if parent_hosted_zone_id is not None:
            self._values["parent_hosted_zone_id"] = parent_hosted_zone_id
        if parent_hosted_zone_name is not None:
            self._values["parent_hosted_zone_name"] = parent_hosted_zone_name
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def delegation_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The delegation role in the parent account.'''
        result = self._values.get("delegation_role")
        assert result is not None, "Required property 'delegation_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def subdomain(self) -> builtins.str:
        '''The subdomain in the parent hosted zone.'''
        result = self._values.get("subdomain")
        assert result is not None, "Required property 'subdomain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assume_role_region(self) -> typing.Optional[builtins.str]:
        '''Region from which to obtain temporary credentials.

        :default: - the Route53 signing region in the current partition
        '''
        result = self._values.get("assume_role_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_hosted_zone_id(self) -> typing.Optional[builtins.str]:
        '''The hosted zone id in the parent account.

        :default: - hosted zone ID will be looked up based on the zone name
        '''
        result = self._values.get("parent_hosted_zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_hosted_zone_name(self) -> typing.Optional[builtins.str]:
        '''The hosted zone name in the parent account.

        :default: - no zone name
        '''
        result = self._values.get("parent_hosted_zone_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def ttl(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The resource record cache time to live (TTL).

        :default: Duration.days(2)
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossAccountDelegationDomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.networking.DelegationDomainProps",
    jsii_struct_bases=[],
    name_mapping={
        "parent_hosted_zone": "parentHostedZone",
        "subdomain": "subdomain",
        "removal_policy": "removalPolicy",
    },
)
class DelegationDomainProps:
    def __init__(
        self,
        *,
        parent_hosted_zone: _aws_cdk_aws_route53_ceddda9d.IPublicHostedZone,
        subdomain: builtins.str,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Constructor properties for DelegationDomain.

        :param parent_hosted_zone: The parent/delegating hosted zone. The "zone name" is needed.
        :param subdomain: The subdomain in the parent hosted zone.
        :param removal_policy: The removal policy to apply. Default: RemovalPolicy.DESTROY
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4959679e489c9a86ddc074b02e8395bd95d85831305854ba5e2983fd01410095)
            check_type(argname="argument parent_hosted_zone", value=parent_hosted_zone, expected_type=type_hints["parent_hosted_zone"])
            check_type(argname="argument subdomain", value=subdomain, expected_type=type_hints["subdomain"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "parent_hosted_zone": parent_hosted_zone,
            "subdomain": subdomain,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def parent_hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IPublicHostedZone:
        '''The parent/delegating hosted zone.

        The "zone name" is needed.
        '''
        result = self._values.get("parent_hosted_zone")
        assert result is not None, "Required property 'parent_hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IPublicHostedZone, result)

    @builtins.property
    def subdomain(self) -> builtins.str:
        '''The subdomain in the parent hosted zone.'''
        result = self._values.get("subdomain")
        assert result is not None, "Required property 'subdomain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DelegationDomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.networking.DomainAttributes",
    jsii_struct_bases=[],
    name_mapping={"certificate": "certificate", "hosted_zone": "hostedZone"},
)
class DomainAttributes:
    def __init__(
        self,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    ) -> None:
        '''A domain in the Domain Name System.

        :param certificate: The wildcard certificate for resources in this domain.
        :param hosted_zone: The hosted zone that contains records for this domain.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6063b0bee2cb1ea0569318144a7399ce89a581edb845cbd7a6cdc1927a9dbf3d)
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate": certificate,
            "hosted_zone": hosted_zone,
        }

    @builtins.property
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''The wildcard certificate for resources in this domain.'''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, result)

    @builtins.property
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone that contains records for this domain.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.networking.ElasticIpProps",
    jsii_struct_bases=[],
    name_mapping={"removal_policy": "removalPolicy"},
)
class ElasticIpProps:
    def __init__(
        self,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Constructor properties for ElasticIp.

        :param removal_policy: The removal policy for this resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e06451a98b33ab08a35c0a78b3d4d4c1c765f25e0a9ce8b560db827f5e389a61)
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for this resource.'''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticIpProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.networking.ExistingZoneDomainProps",
    jsii_struct_bases=[],
    name_mapping={"hosted_zone": "hostedZone"},
)
class ExistingZoneDomainProps:
    def __init__(
        self,
        *,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    ) -> None:
        '''Constructor properties for ExistingZoneDomain.

        :param hosted_zone: The hosted zone that contains records for this domain.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db55134202f24932d26262ae10603b62237d295d85be8c87b7c06977a616ad6f)
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosted_zone": hosted_zone,
        }

    @builtins.property
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone that contains records for this domain.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExistingZoneDomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="shady-island.networking.IDomain")
class IDomain(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''A DNS domain and its wildcard X.509 certificate.'''

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''The wildcard certificate for resources in this domain.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone that contains records for this domain.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The fully-qualified domain name of the hosted zone.'''
        ...


class _IDomainProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''A DNS domain and its wildcard X.509 certificate.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.networking.IDomain"

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''The wildcard certificate for resources in this domain.'''
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone that contains records for this domain.'''
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, jsii.get(self, "hostedZone"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The fully-qualified domain name of the hosted zone.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDomain).__jsii_proxy_class__ = lambda : _IDomainProxy


@jsii.interface(jsii_type="shady-island.networking.IElasticIp")
class IElasticIp(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''An EC2 Elastic IP address.'''

    @builtins.property
    @jsii.member(jsii_name="allocationId")
    def allocation_id(self) -> builtins.str:
        '''The allocation ID of the Elastic IP address.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="elasticIpArn")
    def elastic_ip_arn(self) -> builtins.str:
        '''The ARN of the Elastic IP address.'''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant the given identity custom permissions.

        e.g. ``ec2:AssociateAddress``, ``ec2:DisableAddressTransfer``,
        ``ec2:DisassociateAddress``, ``ec2:EnableAddressTransfer``, among others.

        :param identity: - The resource with a grantPrincipal property.
        :param actions: - The IAM actions to allow.

        :return: The new Grant
        '''
        ...


class _IElasticIpProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''An EC2 Elastic IP address.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.networking.IElasticIp"

    @builtins.property
    @jsii.member(jsii_name="allocationId")
    def allocation_id(self) -> builtins.str:
        '''The allocation ID of the Elastic IP address.'''
        return typing.cast(builtins.str, jsii.get(self, "allocationId"))

    @builtins.property
    @jsii.member(jsii_name="elasticIpArn")
    def elastic_ip_arn(self) -> builtins.str:
        '''The ARN of the Elastic IP address.'''
        return typing.cast(builtins.str, jsii.get(self, "elasticIpArn"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant the given identity custom permissions.

        e.g. ``ec2:AssociateAddress``, ``ec2:DisableAddressTransfer``,
        ``ec2:DisassociateAddress``, ``ec2:EnableAddressTransfer``, among others.

        :param identity: - The resource with a grantPrincipal property.
        :param actions: - The IAM actions to allow.

        :return: The new Grant
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c038201c2cdaabf12b23bf40d541b0618f6bd20657383b850c9ff3a6d96fdfb)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [identity, *actions]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IElasticIp).__jsii_proxy_class__ = lambda : _IElasticIpProxy


@jsii.interface(jsii_type="shady-island.networking.INetworkInterface")
class INetworkInterface(
    _constructs_77d1e7e8.IConstruct,
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    typing_extensions.Protocol,
):
    '''An Elastic Network Interface.'''

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> builtins.str:
        '''The ID of this Network Interface.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="subnet")
    def subnet(self) -> _aws_cdk_aws_ec2_ceddda9d.ISubnet:
        '''The subnet of this Network Interface.'''
        ...


class _INetworkInterfaceProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
):
    '''An Elastic Network Interface.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.networking.INetworkInterface"

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> builtins.str:
        '''The ID of this Network Interface.'''
        return typing.cast(builtins.str, jsii.get(self, "networkInterfaceId"))

    @builtins.property
    @jsii.member(jsii_name="subnet")
    def subnet(self) -> _aws_cdk_aws_ec2_ceddda9d.ISubnet:
        '''The subnet of this Network Interface.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISubnet, jsii.get(self, "subnet"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INetworkInterface).__jsii_proxy_class__ = lambda : _INetworkInterfaceProxy


@jsii.interface(jsii_type="shady-island.networking.ISecretHttpHeader")
class ISecretHttpHeader(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''Interface for SecretHttpHeader.'''

    @builtins.property
    @jsii.member(jsii_name="headerName")
    def header_name(self) -> builtins.str:
        '''The name of the secret header.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="headerValue")
    def header_value(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''The value of the secret header.'''
        ...

    @jsii.member(jsii_name="createListenerCondition")
    def create_listener_condition(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition:
        '''Get a ListenerCondition that represents this secret header.

        :return: The appropriate ListenerCondition.
        '''
        ...

    @jsii.member(jsii_name="createOriginCustomHeaders")
    def create_origin_custom_headers(
        self,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''Gets the custom headers for a CloudFront origin configuration.

        :return: An object with the header name and header value.
        '''
        ...


class _ISecretHttpHeaderProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''Interface for SecretHttpHeader.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.networking.ISecretHttpHeader"

    @builtins.property
    @jsii.member(jsii_name="headerName")
    def header_name(self) -> builtins.str:
        '''The name of the secret header.'''
        return typing.cast(builtins.str, jsii.get(self, "headerName"))

    @builtins.property
    @jsii.member(jsii_name="headerValue")
    def header_value(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''The value of the secret header.'''
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, jsii.get(self, "headerValue"))

    @jsii.member(jsii_name="createListenerCondition")
    def create_listener_condition(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition:
        '''Get a ListenerCondition that represents this secret header.

        :return: The appropriate ListenerCondition.
        '''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition, jsii.invoke(self, "createListenerCondition", []))

    @jsii.member(jsii_name="createOriginCustomHeaders")
    def create_origin_custom_headers(
        self,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''Gets the custom headers for a CloudFront origin configuration.

        :return: An object with the header name and header value.
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.invoke(self, "createOriginCustomHeaders", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISecretHttpHeader).__jsii_proxy_class__ = lambda : _ISecretHttpHeaderProxy


@jsii.enum(jsii_type="shady-island.networking.InterfaceType")
class InterfaceType(enum.Enum):
    '''The type of Network Interface.'''

    INTERFACE = "INTERFACE"
    '''A standard ENI.'''
    EFA = "EFA"
    '''An Elastic Fabric Adapter ENI.'''
    TRUNK = "TRUNK"
    '''An ENI for use with ECS awsvpc trunking.'''


@jsii.implements(INetworkInterface)
class NetworkInterface(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.NetworkInterface",
):
    '''A Network Interface.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        description: typing.Optional[builtins.str] = None,
        elastic_ip: typing.Optional[IElasticIp] = None,
        enable_source_dest_check: typing.Optional[builtins.bool] = None,
        interface_type: typing.Optional[InterfaceType] = None,
        ipv4: typing.Optional[AddressingV4] = None,
        ipv6: typing.Optional[AddressingV6] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    ) -> None:
        '''Creates a new Example.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param subnet: The subnet where this Network Interface will be created.
        :param vpc: The VPC where this Network Interface will be created.
        :param description: A description for this Network Interface.
        :param elastic_ip: An Elastic IP Address to associate with this Network Interface. Provding an Elastic IP
        :param enable_source_dest_check: Enable the source/destination check. Default: - true
        :param interface_type: The type of interface (i.e. interface, efa, trunk). Default: - InterfaceType.INTERFACE
        :param ipv4: How to assign IPv4 addresses. The default behavior depends on the VPC. If it's a dual stack VPC, EC2 will allocate a single private IP address from the VPC IPv4 CIDR range. If it's IPv6-only, EC2 won't allocate an IPv4 address. Default: - Dependent on VPC settings
        :param ipv6: How to assign IPv6 addresses. The default behavior depends on the VPC. If there are no IPv6 CIDRs defined for the VPC, EC2 won't allocate an IPv6 address. If it's a dual stack or an IPv6-only VPC, EC2 will allocate an IPv6 address if the subnet auto-assigns one. Default: - Dependent on VPC and subnet settings.
        :param removal_policy: The removal policy for this resource.
        :param security_groups: The security groups to assign to the Network Interface. Default: - A new one is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7881cbf5a93f60fb5d54843bd46460258c8f6351f8714f9e0bf51936cfb33a8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NetworkInterfaceProps(
            subnet=subnet,
            vpc=vpc,
            description=description,
            elastic_ip=elastic_ip,
            enable_source_dest_check=enable_source_dest_check,
            interface_type=interface_type,
            ipv4=ipv4,
            ipv6=ipv6,
            removal_policy=removal_policy,
            security_groups=security_groups,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromNetworkInterfaceAttributes")
    @builtins.classmethod
    def from_network_interface_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        network_interface_id: builtins.str,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
    ) -> INetworkInterface:
        '''Import an existing Network Interface from the given attributes.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param network_interface_id: The ID of this Network Interface.
        :param security_groups: The security groups assigned to the Network Interface.
        :param subnet: The subnet where this Network Interface will be created.

        :return: The imported Network Interface
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba90bf577e30a95879b04adea6a10e02d8003e632a56c3750ac72371cd4c3c19)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attribs = NetworkInterfaceAttributes(
            network_interface_id=network_interface_id,
            security_groups=security_groups,
            subnet=subnet,
        )

        return typing.cast(INetworkInterface, jsii.sinvoke(cls, "fromNetworkInterfaceAttributes", [scope, id, attribs]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''The network connections associated with this resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="ipv6Address")
    def ipv6_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Address"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> builtins.str:
        '''The ID of this Network Interface.'''
        return typing.cast(builtins.str, jsii.get(self, "networkInterfaceId"))

    @builtins.property
    @jsii.member(jsii_name="privateIpv4Address")
    def private_ipv4_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateIpv4Address"))

    @builtins.property
    @jsii.member(jsii_name="subnet")
    def subnet(self) -> _aws_cdk_aws_ec2_ceddda9d.ISubnet:
        '''The subnet of this Network Interface.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISubnet, jsii.get(self, "subnet"))


@jsii.data_type(
    jsii_type="shady-island.networking.NetworkInterfaceAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "network_interface_id": "networkInterfaceId",
        "security_groups": "securityGroups",
        "subnet": "subnet",
    },
)
class NetworkInterfaceAttributes:
    def __init__(
        self,
        *,
        network_interface_id: builtins.str,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
    ) -> None:
        '''Attributes to import an existing Network Interface.

        :param network_interface_id: The ID of this Network Interface.
        :param security_groups: The security groups assigned to the Network Interface.
        :param subnet: The subnet where this Network Interface will be created.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__872ccdb97fb0caa6e086ac3826a89fb56cf8c89635737fdeec3c5edba3585c2e)
            check_type(argname="argument network_interface_id", value=network_interface_id, expected_type=type_hints["network_interface_id"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network_interface_id": network_interface_id,
            "security_groups": security_groups,
            "subnet": subnet,
        }

    @builtins.property
    def network_interface_id(self) -> builtins.str:
        '''The ID of this Network Interface.'''
        result = self._values.get("network_interface_id")
        assert result is not None, "Required property 'network_interface_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_groups(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security groups assigned to the Network Interface.'''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def subnet(self) -> _aws_cdk_aws_ec2_ceddda9d.ISubnet:
        '''The subnet where this Network Interface will be created.'''
        result = self._values.get("subnet")
        assert result is not None, "Required property 'subnet' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISubnet, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkInterfaceAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.networking.NetworkInterfaceProps",
    jsii_struct_bases=[],
    name_mapping={
        "subnet": "subnet",
        "vpc": "vpc",
        "description": "description",
        "elastic_ip": "elasticIp",
        "enable_source_dest_check": "enableSourceDestCheck",
        "interface_type": "interfaceType",
        "ipv4": "ipv4",
        "ipv6": "ipv6",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
    },
)
class NetworkInterfaceProps:
    def __init__(
        self,
        *,
        subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        description: typing.Optional[builtins.str] = None,
        elastic_ip: typing.Optional[IElasticIp] = None,
        enable_source_dest_check: typing.Optional[builtins.bool] = None,
        interface_type: typing.Optional[InterfaceType] = None,
        ipv4: typing.Optional[AddressingV4] = None,
        ipv6: typing.Optional[AddressingV6] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    ) -> None:
        '''Constructor properties for NetworkInterface.

        :param subnet: The subnet where this Network Interface will be created.
        :param vpc: The VPC where this Network Interface will be created.
        :param description: A description for this Network Interface.
        :param elastic_ip: An Elastic IP Address to associate with this Network Interface. Provding an Elastic IP
        :param enable_source_dest_check: Enable the source/destination check. Default: - true
        :param interface_type: The type of interface (i.e. interface, efa, trunk). Default: - InterfaceType.INTERFACE
        :param ipv4: How to assign IPv4 addresses. The default behavior depends on the VPC. If it's a dual stack VPC, EC2 will allocate a single private IP address from the VPC IPv4 CIDR range. If it's IPv6-only, EC2 won't allocate an IPv4 address. Default: - Dependent on VPC settings
        :param ipv6: How to assign IPv6 addresses. The default behavior depends on the VPC. If there are no IPv6 CIDRs defined for the VPC, EC2 won't allocate an IPv6 address. If it's a dual stack or an IPv6-only VPC, EC2 will allocate an IPv6 address if the subnet auto-assigns one. Default: - Dependent on VPC and subnet settings.
        :param removal_policy: The removal policy for this resource.
        :param security_groups: The security groups to assign to the Network Interface. Default: - A new one is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ad8d033df0b3a5892f2030211876beee3fab00f8b29e23f9591cb251b26d102)
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument elastic_ip", value=elastic_ip, expected_type=type_hints["elastic_ip"])
            check_type(argname="argument enable_source_dest_check", value=enable_source_dest_check, expected_type=type_hints["enable_source_dest_check"])
            check_type(argname="argument interface_type", value=interface_type, expected_type=type_hints["interface_type"])
            check_type(argname="argument ipv4", value=ipv4, expected_type=type_hints["ipv4"])
            check_type(argname="argument ipv6", value=ipv6, expected_type=type_hints["ipv6"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "subnet": subnet,
            "vpc": vpc,
        }
        if description is not None:
            self._values["description"] = description
        if elastic_ip is not None:
            self._values["elastic_ip"] = elastic_ip
        if enable_source_dest_check is not None:
            self._values["enable_source_dest_check"] = enable_source_dest_check
        if interface_type is not None:
            self._values["interface_type"] = interface_type
        if ipv4 is not None:
            self._values["ipv4"] = ipv4
        if ipv6 is not None:
            self._values["ipv6"] = ipv6
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups

    @builtins.property
    def subnet(self) -> _aws_cdk_aws_ec2_ceddda9d.ISubnet:
        '''The subnet where this Network Interface will be created.'''
        result = self._values.get("subnet")
        assert result is not None, "Required property 'subnet' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISubnet, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where this Network Interface will be created.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description for this Network Interface.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elastic_ip(self) -> typing.Optional[IElasticIp]:
        '''An Elastic IP Address to associate with this Network Interface.

        Provding an Elastic IP
        '''
        result = self._values.get("elastic_ip")
        return typing.cast(typing.Optional[IElasticIp], result)

    @builtins.property
    def enable_source_dest_check(self) -> typing.Optional[builtins.bool]:
        '''Enable the source/destination check.

        :default: - true
        '''
        result = self._values.get("enable_source_dest_check")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def interface_type(self) -> typing.Optional[InterfaceType]:
        '''The type of interface (i.e. interface, efa, trunk).

        :default: - InterfaceType.INTERFACE
        '''
        result = self._values.get("interface_type")
        return typing.cast(typing.Optional[InterfaceType], result)

    @builtins.property
    def ipv4(self) -> typing.Optional[AddressingV4]:
        '''How to assign IPv4 addresses.

        The default behavior depends on the VPC. If it's a dual stack VPC, EC2 will
        allocate a single private IP address from the VPC IPv4 CIDR range. If it's
        IPv6-only, EC2 won't allocate an IPv4 address.

        :default: - Dependent on VPC settings
        '''
        result = self._values.get("ipv4")
        return typing.cast(typing.Optional[AddressingV4], result)

    @builtins.property
    def ipv6(self) -> typing.Optional[AddressingV6]:
        '''How to assign IPv6 addresses.

        The default behavior depends on the VPC. If there are no IPv6 CIDRs defined
        for the VPC, EC2 won't allocate an IPv6 address. If it's a dual stack or an
        IPv6-only VPC, EC2 will allocate an IPv6 address if the subnet auto-assigns
        one.

        :default: - Dependent on VPC and subnet settings.
        '''
        result = self._values.get("ipv6")
        return typing.cast(typing.Optional[AddressingV6], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for this resource.'''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to assign to the Network Interface.

        :default: - A new one is created
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkInterfaceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ISecretHttpHeader)
class SecretHttpHeader(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.SecretHttpHeader",
):
    '''Configure a secret header an ALB can require for every request.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        header_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new SecretHttpHeader.

        :param scope: - The parent scope.
        :param id: - The construct identifier.
        :param header_name: The name of the secret HTTP header. Default: - X-Secret-Passphrase
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__150cf8e22f1e7d05a47117e8f77da25561199d5daa7118eb196893fa55cfd796)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SecretHttpHeaderProps(header_name=header_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecret")
    @builtins.classmethod
    def from_secret(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> ISecretHttpHeader:
        '''Create a SecretHttpHeader from an existing Secrets Manager secret.

        The secret must be in JSON format and have two fields: ``name`` and ``value``.

        :param scope: - The parent scope.
        :param id: - The ID for the new construct.
        :param secret: - The existing Secrets Manager secret.

        :return: The new ISecretHttpHeader
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40fccea94b7e684de60e1f55e353e1a03b85c56db9135f4d67a939d5448d4694)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(ISecretHttpHeader, jsii.sinvoke(cls, "fromSecret", [scope, id, secret]))

    @jsii.member(jsii_name="createListenerCondition")
    def create_listener_condition(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition:
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition, jsii.invoke(self, "createListenerCondition", []))

    @jsii.member(jsii_name="createOriginCustomHeaders")
    def create_origin_custom_headers(
        self,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.invoke(self, "createOriginCustomHeaders", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="defaultHeaderName")
    def default_header_name(cls) -> builtins.str:
        '''Gets the default header name.

        :return: the default header name
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "defaultHeaderName"))

    @builtins.property
    @jsii.member(jsii_name="headerName")
    def header_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerName"))

    @builtins.property
    @jsii.member(jsii_name="headerValue")
    def header_value(self) -> _aws_cdk_ceddda9d.SecretValue:
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, jsii.get(self, "headerValue"))

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The Secrets Manager secret that contains the name and value of the header.'''
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.get(self, "secret"))


@jsii.data_type(
    jsii_type="shady-island.networking.SecretHttpHeaderProps",
    jsii_struct_bases=[],
    name_mapping={"header_name": "headerName"},
)
class SecretHttpHeaderProps:
    def __init__(self, *, header_name: typing.Optional[builtins.str] = None) -> None:
        '''Properties for the SecretHttpHeader constructor.

        :param header_name: The name of the secret HTTP header. Default: - X-Secret-Passphrase
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c95f74423d937b8be51b1b147dac2d7c254b40cc4b250c45909e61f91bd46e8)
            check_type(argname="argument header_name", value=header_name, expected_type=type_hints["header_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if header_name is not None:
            self._values["header_name"] = header_name

    @builtins.property
    def header_name(self) -> typing.Optional[builtins.str]:
        '''The name of the secret HTTP header.

        :default: - X-Secret-Passphrase
        '''
        result = self._values.get("header_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretHttpHeaderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SingletonLaunchTemplate(
    _aws_cdk_aws_ec2_ceddda9d.LaunchTemplate,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.SingletonLaunchTemplate",
):
    '''A launch template bound to a single Elastic Network Interface.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        network_interface: INetworkInterface,
        associate_public_ip_address: typing.Optional[builtins.bool] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        cpu_credits: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
        detailed_monitoring: typing.Optional[builtins.bool] = None,
        disable_api_termination: typing.Optional[builtins.bool] = None,
        ebs_optimized: typing.Optional[builtins.bool] = None,
        hibernation_configured: typing.Optional[builtins.bool] = None,
        http_endpoint: typing.Optional[builtins.bool] = None,
        http_protocol_ipv6: typing.Optional[builtins.bool] = None,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        http_tokens: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateHttpTokens] = None,
        instance_initiated_shutdown_behavior: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior] = None,
        instance_metadata_tags: typing.Optional[builtins.bool] = None,
        instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        launch_template_name: typing.Optional[builtins.str] = None,
        machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        nitro_enclave_enabled: typing.Optional[builtins.bool] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        spot_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateSpotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
        version_description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new SingletonLaunchTemplate.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param network_interface: The Elastic Network Interface to use.
        :param associate_public_ip_address: Whether instances should have a public IP addresses associated with them. Default: - Use subnet settings
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param cpu_credits: CPU credit type for burstable EC2 instance types. Default: - No credit type is specified in the Launch Template.
        :param detailed_monitoring: If set to true, then detailed monitoring will be enabled on instances created with this launch template. Default: False - Detailed monitoring is disabled.
        :param disable_api_termination: If you set this parameter to true, you cannot terminate the instances launched with this launch template using the Amazon EC2 console, CLI, or API; otherwise, you can. Default: - The API termination setting is not specified in the Launch Template.
        :param ebs_optimized: Indicates whether the instances are optimized for Amazon EBS I/O. This optimization provides dedicated throughput to Amazon EBS and an optimized configuration stack to provide optimal Amazon EBS I/O performance. This optimization isn't available with all instance types. Additional usage charges apply when using an EBS-optimized instance. Default: - EBS optimization is not specified in the launch template.
        :param hibernation_configured: If you set this parameter to true, the instance is enabled for hibernation. Default: - Hibernation configuration is not specified in the launch template; defaulting to false.
        :param http_endpoint: Enables or disables the HTTP metadata endpoint on your instances. Default: true
        :param http_protocol_ipv6: Enables or disables the IPv6 endpoint for the instance metadata service. Default: true
        :param http_put_response_hop_limit: The desired HTTP PUT response hop limit for instance metadata requests. The larger the number, the further instance metadata requests can travel. Default: 1
        :param http_tokens: The state of token usage for your instance metadata requests. The default state is ``optional`` if not specified. However, if requireImdsv2 is true, the state must be ``required``. Default: LaunchTemplateHttpTokens.OPTIONAL
        :param instance_initiated_shutdown_behavior: Indicates whether an instance stops or terminates when you initiate shutdown from the instance (using the operating system command for system shutdown). Default: - Shutdown behavior is not specified in the launch template; defaults to STOP.
        :param instance_metadata_tags: Set to enabled to allow access to instance tags from the instance metadata. Set to disabled to turn off access to instance tags from the instance metadata. Default: false
        :param instance_profile: The instance profile used to pass role information to EC2 instances. Note: You can provide an instanceProfile or a role, but not both. Default: - No instance profile
        :param instance_type: Type of instance to launch. Default: - This Launch Template does not specify a default Instance Type.
        :param key_name: (deprecated) Name of SSH keypair to grant access to instance. Default: - No SSH access will be possible.
        :param key_pair: The SSH keypair to grant access to the instance. Default: - No SSH access will be possible.
        :param launch_template_name: Name for this launch template. Default: Automatically generated name
        :param machine_image: The AMI that will be used by instances. Default: - This Launch Template does not specify a default AMI.
        :param nitro_enclave_enabled: If this parameter is set to true, the instance is enabled for AWS Nitro Enclaves; otherwise, it is not enabled for AWS Nitro Enclaves. Default: - Enablement of Nitro enclaves is not specified in the launch template; defaulting to false.
        :param require_imdsv2: Whether IMDSv2 should be required on launched instances. Default: - false
        :param role: An IAM role to associate with the instance profile that is used by instances. The role must be assumable by the service principal ``ec2.amazonaws.com``. Note: You can provide an instanceProfile or a role, but not both. Default: - No new role is created.
        :param security_group: Security group to assign to instances created with the launch template. Default: No security group is assigned.
        :param spot_options: If this property is defined, then the Launch Template's InstanceMarketOptions will be set to use Spot instances, and the options for the Spot instances will be as defined. Default: - Instance launched with this template will not be spot instances.
        :param user_data: The AMI that will be used by instances. Default: - This Launch Template creates a UserData based on the type of provided machineImage; no UserData is created if a machineImage is not provided
        :param version_description: A description for the first version of the launch template. The version description must be maximum 255 characters long. Default: - No description
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f92671cecad94d42b87c6acda72bcbcbade0768d3a7cf14c24da4ac77dc8f82a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SingletonLaunchTemplateProps(
            network_interface=network_interface,
            associate_public_ip_address=associate_public_ip_address,
            block_devices=block_devices,
            cpu_credits=cpu_credits,
            detailed_monitoring=detailed_monitoring,
            disable_api_termination=disable_api_termination,
            ebs_optimized=ebs_optimized,
            hibernation_configured=hibernation_configured,
            http_endpoint=http_endpoint,
            http_protocol_ipv6=http_protocol_ipv6,
            http_put_response_hop_limit=http_put_response_hop_limit,
            http_tokens=http_tokens,
            instance_initiated_shutdown_behavior=instance_initiated_shutdown_behavior,
            instance_metadata_tags=instance_metadata_tags,
            instance_profile=instance_profile,
            instance_type=instance_type,
            key_name=key_name,
            key_pair=key_pair,
            launch_template_name=launch_template_name,
            machine_image=machine_image,
            nitro_enclave_enabled=nitro_enclave_enabled,
            require_imdsv2=require_imdsv2,
            role=role,
            security_group=security_group,
            spot_options=spot_options,
            user_data=user_data,
            version_description=version_description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addSecurityGroup")
    def add_security_group(
        self,
        security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    ) -> None:
        '''Add the security group to the instance.

        :param security_group: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fad5ad29510611b1ba296adad47fb6ec9c8138487f35967841a16b49dc03e726)
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
        return typing.cast(None, jsii.invoke(self, "addSecurityGroup", [security_group]))

    @jsii.member(jsii_name="createAutoScalingGroup")
    def create_auto_scaling_group(
        self,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
        init_options: typing.Optional[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        launch_template: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate] = None,
        machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        max_healthy_percentage: typing.Optional[jsii.Number] = None,
        min_healthy_percentage: typing.Optional[jsii.Number] = None,
        mixed_instances_policy: typing.Optional[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.MixedInstancesPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        associate_public_ip_address: typing.Optional[builtins.bool] = None,
        auto_scaling_group_name: typing.Optional[builtins.str] = None,
        az_capacity_distribution_strategy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.CapacityDistributionStrategy] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        capacity_rebalance: typing.Optional[builtins.bool] = None,
        cooldown: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        default_instance_warmup: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        group_metrics: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.GroupMetrics]] = None,
        health_check: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthCheck] = None,
        ignore_unmodified_size_properties: typing.Optional[builtins.bool] = None,
        instance_monitoring: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Monitoring] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_instance_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        new_instances_protected_from_scale_in: typing.Optional[builtins.bool] = None,
        notifications: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.NotificationConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        signals: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Signals] = None,
        spot_price: typing.Optional[builtins.str] = None,
        ssm_session_permissions: typing.Optional[builtins.bool] = None,
        termination_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.TerminationPolicy]] = None,
        termination_policy_custom_lambda_function_arn: typing.Optional[builtins.str] = None,
        update_policy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.UpdatePolicy] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup:
        '''Creates an auto-scaling group for this launch template.

        The following properties are ignored (if specified): ``launchTemplate``,
        ``minCapacity``, and ``maxCapacity``.

        :param id: - The ID of the auto-scaling group.
        :param vpc: VPC to launch these instances in.
        :param init: Apply the given CloudFormation Init configuration to the instances in the AutoScalingGroup at startup. If you specify ``init``, you must also specify ``signals`` to configure the number of instances to wait for and the timeout for waiting for the init process. Default: - no CloudFormation init
        :param init_options: Use the given options for applying CloudFormation Init. Describes the configsets to use and the timeout to wait Default: - default options
        :param instance_type: Type of instance to launch. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Do not provide any instance type
        :param launch_template: Launch template to use. Launch configuration related settings and MixedInstancesPolicy must not be specified when a launch template is specified. Default: - Do not provide any launch template
        :param machine_image: AMI to launch. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Do not provide any machine image
        :param max_healthy_percentage: Specifies the upper threshold as a percentage of the desired capacity of the Auto Scaling group. It represents the maximum percentage of the group that can be in service and healthy, or pending, to support your workload when replacing instances. Value range is 0 to 100. After it's set, both ``minHealthyPercentage`` and ``maxHealthyPercentage`` to -1 will clear the previously set value. Both or neither of ``minHealthyPercentage`` and ``maxHealthyPercentage`` must be specified, and the difference between them cannot be greater than 100. A large range increases the number of instances that can be replaced at the same time. Default: - No instance maintenance policy.
        :param min_healthy_percentage: Specifies the lower threshold as a percentage of the desired capacity of the Auto Scaling group. It represents the minimum percentage of the group to keep in service, healthy, and ready to use to support your workload when replacing instances. Value range is 0 to 100. After it's set, both ``minHealthyPercentage`` and ``maxHealthyPercentage`` to -1 will clear the previously set value. Both or neither of ``minHealthyPercentage`` and ``maxHealthyPercentage`` must be specified, and the difference between them cannot be greater than 100. A large range increases the number of instances that can be replaced at the same time. Default: - No instance maintenance policy.
        :param mixed_instances_policy: Mixed Instances Policy to use. Launch configuration related settings and Launch Template must not be specified when a MixedInstancesPolicy is specified. Default: - Do not provide any MixedInstancesPolicy
        :param require_imdsv2: Whether IMDSv2 should be required on launched instances. Default: false
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security group to launch the instances in. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - A SecurityGroup will be created if none is specified.
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - A UserData object appropriate for the MachineImage's Operating System is created.
        :param allow_all_outbound: Whether the instances can initiate connections to anywhere by default. Default: true
        :param associate_public_ip_address: Whether instances in the Auto Scaling Group should have public IP addresses associated with them. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Use subnet setting.
        :param auto_scaling_group_name: The name of the Auto Scaling group. This name must be unique per Region per account. Default: - Auto generated by CloudFormation
        :param az_capacity_distribution_strategy: The strategy for distributing instances across Availability Zones. Default: None
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Uses the block device mapping of the AMI
        :param capacity_rebalance: Indicates whether Capacity Rebalancing is enabled. When you turn on Capacity Rebalancing, Amazon EC2 Auto Scaling attempts to launch a Spot Instance whenever Amazon EC2 notifies that a Spot Instance is at an elevated risk of interruption. After launching a new instance, it then terminates an old instance. Default: false
        :param cooldown: Default scaling cooldown for this AutoScalingGroup. Default: Duration.minutes(5)
        :param default_instance_warmup: The amount of time, in seconds, until a newly launched instance can contribute to the Amazon CloudWatch metrics. This delay lets an instance finish initializing before Amazon EC2 Auto Scaling aggregates instance metrics, resulting in more reliable usage data. Set this value equal to the amount of time that it takes for resource consumption to become stable after an instance reaches the InService state. To optimize the performance of scaling policies that scale continuously, such as target tracking and step scaling policies, we strongly recommend that you enable the default instance warmup, even if its value is set to 0 seconds Default instance warmup will not be added if no value is specified Default: None
        :param desired_capacity: Initial amount of instances in the fleet. If this is set to a number, every deployment will reset the amount of instances to this number. It is recommended to leave this value blank. Default: minCapacity, and leave unchanged during deployment
        :param group_metrics: Enable monitoring for group metrics, these metrics describe the group rather than any of its instances. To report all group metrics use ``GroupMetrics.all()`` Group metrics are reported in a granularity of 1 minute at no additional charge. Default: - no group metrics will be reported
        :param health_check: Configuration for health checks. Default: - HealthCheck.ec2 with no grace period
        :param ignore_unmodified_size_properties: If the ASG has scheduled actions, don't reset unchanged group sizes. Only used if the ASG has scheduled actions (which may scale your ASG up or down regardless of cdk deployments). If true, the size of the group will only be reset if it has been changed in the CDK app. If false, the sizes will always be changed back to what they were in the CDK app on deployment. Default: true
        :param instance_monitoring: Controls whether instances in this group are launched with detailed or basic monitoring. When detailed monitoring is enabled, Amazon CloudWatch generates metrics every minute and your account is charged a fee. When you disable detailed monitoring, CloudWatch generates metrics every 5 minutes. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Monitoring.DETAILED
        :param key_name: (deprecated) Name of SSH keypair to grant access to instances. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified You can either specify ``keyPair`` or ``keyName``, not both. Default: - No SSH access will be possible.
        :param key_pair: The SSH keypair to grant access to the instance. Feature flag ``AUTOSCALING_GENERATE_LAUNCH_TEMPLATE`` must be enabled to use this property. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified. You can either specify ``keyPair`` or ``keyName``, not both. Default: - No SSH access will be possible.
        :param max_capacity: Maximum number of instances in the fleet. Default: desiredCapacity
        :param max_instance_lifetime: The maximum amount of time that an instance can be in service. The maximum duration applies to all current and future instances in the group. As an instance approaches its maximum duration, it is terminated and replaced, and cannot be used again. You must specify a value of at least 604,800 seconds (7 days). To clear a previously set value, leave this property undefined. Default: none
        :param min_capacity: Minimum number of instances in the fleet. Default: 1
        :param new_instances_protected_from_scale_in: Whether newly-launched instances are protected from termination by Amazon EC2 Auto Scaling when scaling in. By default, Auto Scaling can terminate an instance at any time after launch when scaling in an Auto Scaling Group, subject to the group's termination policy. However, you may wish to protect newly-launched instances from being scaled in if they are going to run critical applications that should not be prematurely terminated. This flag must be enabled if the Auto Scaling Group will be associated with an ECS Capacity Provider with managed termination protection. Default: false
        :param notifications: Configure autoscaling group to send notifications about fleet changes to an SNS topic(s). Default: - No fleet change notifications will be sent.
        :param signals: Configure waiting for signals during deployment. Use this to pause the CloudFormation deployment to wait for the instances in the AutoScalingGroup to report successful startup during creation and updates. The UserData script needs to invoke ``cfn-signal`` with a success or failure code after it is done setting up the instance. Without waiting for signals, the CloudFormation deployment will proceed as soon as the AutoScalingGroup has been created or updated but before the instances in the group have been started. For example, to have instances wait for an Elastic Load Balancing health check before they signal success, add a health-check verification by using the cfn-init helper script. For an example, see the verify_instance_health command in the Auto Scaling rolling updates sample template: https://github.com/awslabs/aws-cloudformation-templates/blob/master/aws/services/AutoScaling/AutoScalingRollingUpdates.yaml Default: - Do not wait for signals
        :param spot_price: The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request. Spot Instances are launched when the price you specify exceeds the current Spot market price. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: none
        :param ssm_session_permissions: Add SSM session permissions to the instance role. Setting this to ``true`` adds the necessary permissions to connect to the instance using SSM Session Manager. You can do this from the AWS Console. NOTE: Setting this flag to ``true`` may not be enough by itself. You must also use an AMI that comes with the SSM Agent, or install the SSM Agent yourself. See `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_ in the SSM Developer Guide. Default: false
        :param termination_policies: A policy or a list of policies that are used to select the instances to terminate. The policies are executed in the order that you list them. Default: - ``TerminationPolicy.DEFAULT``
        :param termination_policy_custom_lambda_function_arn: A lambda function Arn that can be used as a custom termination policy to select the instances to terminate. This property must be specified if the TerminationPolicy.CUSTOM_LAMBDA_FUNCTION is used. Default: - No lambda function Arn will be supplied
        :param update_policy: What to do when an AutoScalingGroup's instance configuration is changed. This is applied when any of the settings on the ASG are changed that affect how the instances should be created (VPC, instance type, startup scripts, etc.). It indicates how the existing instances should be replaced with new instances matching the new config. By default, nothing is done and only new instances are launched with the new config. Default: - ``UpdatePolicy.rollingUpdate()`` if using ``init``, ``UpdatePolicy.none()`` otherwise
        :param vpc_subnets: Where to place instances within the VPC. Default: - All Private subnets.

        :return: A new auto-scaling group
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba33fd6777c800d1923d7cc2b7309329ddda3c297188eea52d9c0fed6e4499d6)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroupProps(
            vpc=vpc,
            init=init,
            init_options=init_options,
            instance_type=instance_type,
            launch_template=launch_template,
            machine_image=machine_image,
            max_healthy_percentage=max_healthy_percentage,
            min_healthy_percentage=min_healthy_percentage,
            mixed_instances_policy=mixed_instances_policy,
            require_imdsv2=require_imdsv2,
            role=role,
            security_group=security_group,
            user_data=user_data,
            allow_all_outbound=allow_all_outbound,
            associate_public_ip_address=associate_public_ip_address,
            auto_scaling_group_name=auto_scaling_group_name,
            az_capacity_distribution_strategy=az_capacity_distribution_strategy,
            block_devices=block_devices,
            capacity_rebalance=capacity_rebalance,
            cooldown=cooldown,
            default_instance_warmup=default_instance_warmup,
            desired_capacity=desired_capacity,
            group_metrics=group_metrics,
            health_check=health_check,
            ignore_unmodified_size_properties=ignore_unmodified_size_properties,
            instance_monitoring=instance_monitoring,
            key_name=key_name,
            key_pair=key_pair,
            max_capacity=max_capacity,
            max_instance_lifetime=max_instance_lifetime,
            min_capacity=min_capacity,
            new_instances_protected_from_scale_in=new_instances_protected_from_scale_in,
            notifications=notifications,
            signals=signals,
            spot_price=spot_price,
            ssm_session_permissions=ssm_session_permissions,
            termination_policies=termination_policies,
            termination_policy_custom_lambda_function_arn=termination_policy_custom_lambda_function_arn,
            update_policy=update_policy,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast(_aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup, jsii.invoke(self, "createAutoScalingGroup", [id, props]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''Allows specifying security group connections for the instance.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="networkInterface")
    def network_interface(self) -> INetworkInterface:
        '''The network interface used by this launch template.'''
        return typing.cast(INetworkInterface, jsii.get(self, "networkInterface"))


@jsii.data_type(
    jsii_type="shady-island.networking.SingletonLaunchTemplateProps",
    jsii_struct_bases=[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateProps],
    name_mapping={
        "associate_public_ip_address": "associatePublicIpAddress",
        "block_devices": "blockDevices",
        "cpu_credits": "cpuCredits",
        "detailed_monitoring": "detailedMonitoring",
        "disable_api_termination": "disableApiTermination",
        "ebs_optimized": "ebsOptimized",
        "hibernation_configured": "hibernationConfigured",
        "http_endpoint": "httpEndpoint",
        "http_protocol_ipv6": "httpProtocolIpv6",
        "http_put_response_hop_limit": "httpPutResponseHopLimit",
        "http_tokens": "httpTokens",
        "instance_initiated_shutdown_behavior": "instanceInitiatedShutdownBehavior",
        "instance_metadata_tags": "instanceMetadataTags",
        "instance_profile": "instanceProfile",
        "instance_type": "instanceType",
        "key_name": "keyName",
        "key_pair": "keyPair",
        "launch_template_name": "launchTemplateName",
        "machine_image": "machineImage",
        "nitro_enclave_enabled": "nitroEnclaveEnabled",
        "require_imdsv2": "requireImdsv2",
        "role": "role",
        "security_group": "securityGroup",
        "spot_options": "spotOptions",
        "user_data": "userData",
        "version_description": "versionDescription",
        "network_interface": "networkInterface",
    },
)
class SingletonLaunchTemplateProps(_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateProps):
    def __init__(
        self,
        *,
        associate_public_ip_address: typing.Optional[builtins.bool] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        cpu_credits: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
        detailed_monitoring: typing.Optional[builtins.bool] = None,
        disable_api_termination: typing.Optional[builtins.bool] = None,
        ebs_optimized: typing.Optional[builtins.bool] = None,
        hibernation_configured: typing.Optional[builtins.bool] = None,
        http_endpoint: typing.Optional[builtins.bool] = None,
        http_protocol_ipv6: typing.Optional[builtins.bool] = None,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        http_tokens: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateHttpTokens] = None,
        instance_initiated_shutdown_behavior: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior] = None,
        instance_metadata_tags: typing.Optional[builtins.bool] = None,
        instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        launch_template_name: typing.Optional[builtins.str] = None,
        machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        nitro_enclave_enabled: typing.Optional[builtins.bool] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        spot_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateSpotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
        version_description: typing.Optional[builtins.str] = None,
        network_interface: INetworkInterface,
    ) -> None:
        '''Constructor properties for SingletonLaunchTemplate.

        :param associate_public_ip_address: Whether instances should have a public IP addresses associated with them. Default: - Use subnet settings
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param cpu_credits: CPU credit type for burstable EC2 instance types. Default: - No credit type is specified in the Launch Template.
        :param detailed_monitoring: If set to true, then detailed monitoring will be enabled on instances created with this launch template. Default: False - Detailed monitoring is disabled.
        :param disable_api_termination: If you set this parameter to true, you cannot terminate the instances launched with this launch template using the Amazon EC2 console, CLI, or API; otherwise, you can. Default: - The API termination setting is not specified in the Launch Template.
        :param ebs_optimized: Indicates whether the instances are optimized for Amazon EBS I/O. This optimization provides dedicated throughput to Amazon EBS and an optimized configuration stack to provide optimal Amazon EBS I/O performance. This optimization isn't available with all instance types. Additional usage charges apply when using an EBS-optimized instance. Default: - EBS optimization is not specified in the launch template.
        :param hibernation_configured: If you set this parameter to true, the instance is enabled for hibernation. Default: - Hibernation configuration is not specified in the launch template; defaulting to false.
        :param http_endpoint: Enables or disables the HTTP metadata endpoint on your instances. Default: true
        :param http_protocol_ipv6: Enables or disables the IPv6 endpoint for the instance metadata service. Default: true
        :param http_put_response_hop_limit: The desired HTTP PUT response hop limit for instance metadata requests. The larger the number, the further instance metadata requests can travel. Default: 1
        :param http_tokens: The state of token usage for your instance metadata requests. The default state is ``optional`` if not specified. However, if requireImdsv2 is true, the state must be ``required``. Default: LaunchTemplateHttpTokens.OPTIONAL
        :param instance_initiated_shutdown_behavior: Indicates whether an instance stops or terminates when you initiate shutdown from the instance (using the operating system command for system shutdown). Default: - Shutdown behavior is not specified in the launch template; defaults to STOP.
        :param instance_metadata_tags: Set to enabled to allow access to instance tags from the instance metadata. Set to disabled to turn off access to instance tags from the instance metadata. Default: false
        :param instance_profile: The instance profile used to pass role information to EC2 instances. Note: You can provide an instanceProfile or a role, but not both. Default: - No instance profile
        :param instance_type: Type of instance to launch. Default: - This Launch Template does not specify a default Instance Type.
        :param key_name: (deprecated) Name of SSH keypair to grant access to instance. Default: - No SSH access will be possible.
        :param key_pair: The SSH keypair to grant access to the instance. Default: - No SSH access will be possible.
        :param launch_template_name: Name for this launch template. Default: Automatically generated name
        :param machine_image: The AMI that will be used by instances. Default: - This Launch Template does not specify a default AMI.
        :param nitro_enclave_enabled: If this parameter is set to true, the instance is enabled for AWS Nitro Enclaves; otherwise, it is not enabled for AWS Nitro Enclaves. Default: - Enablement of Nitro enclaves is not specified in the launch template; defaulting to false.
        :param require_imdsv2: Whether IMDSv2 should be required on launched instances. Default: - false
        :param role: An IAM role to associate with the instance profile that is used by instances. The role must be assumable by the service principal ``ec2.amazonaws.com``. Note: You can provide an instanceProfile or a role, but not both. Default: - No new role is created.
        :param security_group: Security group to assign to instances created with the launch template. Default: No security group is assigned.
        :param spot_options: If this property is defined, then the Launch Template's InstanceMarketOptions will be set to use Spot instances, and the options for the Spot instances will be as defined. Default: - Instance launched with this template will not be spot instances.
        :param user_data: The AMI that will be used by instances. Default: - This Launch Template creates a UserData based on the type of provided machineImage; no UserData is created if a machineImage is not provided
        :param version_description: A description for the first version of the launch template. The version description must be maximum 255 characters long. Default: - No description
        :param network_interface: The Elastic Network Interface to use.
        '''
        if isinstance(spot_options, dict):
            spot_options = _aws_cdk_aws_ec2_ceddda9d.LaunchTemplateSpotOptions(**spot_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3bd5bd8420370bd8e386843b6b8d74e4ceb6ba66a5f5570c7ea46da5ad3f17f)
            check_type(argname="argument associate_public_ip_address", value=associate_public_ip_address, expected_type=type_hints["associate_public_ip_address"])
            check_type(argname="argument block_devices", value=block_devices, expected_type=type_hints["block_devices"])
            check_type(argname="argument cpu_credits", value=cpu_credits, expected_type=type_hints["cpu_credits"])
            check_type(argname="argument detailed_monitoring", value=detailed_monitoring, expected_type=type_hints["detailed_monitoring"])
            check_type(argname="argument disable_api_termination", value=disable_api_termination, expected_type=type_hints["disable_api_termination"])
            check_type(argname="argument ebs_optimized", value=ebs_optimized, expected_type=type_hints["ebs_optimized"])
            check_type(argname="argument hibernation_configured", value=hibernation_configured, expected_type=type_hints["hibernation_configured"])
            check_type(argname="argument http_endpoint", value=http_endpoint, expected_type=type_hints["http_endpoint"])
            check_type(argname="argument http_protocol_ipv6", value=http_protocol_ipv6, expected_type=type_hints["http_protocol_ipv6"])
            check_type(argname="argument http_put_response_hop_limit", value=http_put_response_hop_limit, expected_type=type_hints["http_put_response_hop_limit"])
            check_type(argname="argument http_tokens", value=http_tokens, expected_type=type_hints["http_tokens"])
            check_type(argname="argument instance_initiated_shutdown_behavior", value=instance_initiated_shutdown_behavior, expected_type=type_hints["instance_initiated_shutdown_behavior"])
            check_type(argname="argument instance_metadata_tags", value=instance_metadata_tags, expected_type=type_hints["instance_metadata_tags"])
            check_type(argname="argument instance_profile", value=instance_profile, expected_type=type_hints["instance_profile"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument key_name", value=key_name, expected_type=type_hints["key_name"])
            check_type(argname="argument key_pair", value=key_pair, expected_type=type_hints["key_pair"])
            check_type(argname="argument launch_template_name", value=launch_template_name, expected_type=type_hints["launch_template_name"])
            check_type(argname="argument machine_image", value=machine_image, expected_type=type_hints["machine_image"])
            check_type(argname="argument nitro_enclave_enabled", value=nitro_enclave_enabled, expected_type=type_hints["nitro_enclave_enabled"])
            check_type(argname="argument require_imdsv2", value=require_imdsv2, expected_type=type_hints["require_imdsv2"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument spot_options", value=spot_options, expected_type=type_hints["spot_options"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
            check_type(argname="argument version_description", value=version_description, expected_type=type_hints["version_description"])
            check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network_interface": network_interface,
        }
        if associate_public_ip_address is not None:
            self._values["associate_public_ip_address"] = associate_public_ip_address
        if block_devices is not None:
            self._values["block_devices"] = block_devices
        if cpu_credits is not None:
            self._values["cpu_credits"] = cpu_credits
        if detailed_monitoring is not None:
            self._values["detailed_monitoring"] = detailed_monitoring
        if disable_api_termination is not None:
            self._values["disable_api_termination"] = disable_api_termination
        if ebs_optimized is not None:
            self._values["ebs_optimized"] = ebs_optimized
        if hibernation_configured is not None:
            self._values["hibernation_configured"] = hibernation_configured
        if http_endpoint is not None:
            self._values["http_endpoint"] = http_endpoint
        if http_protocol_ipv6 is not None:
            self._values["http_protocol_ipv6"] = http_protocol_ipv6
        if http_put_response_hop_limit is not None:
            self._values["http_put_response_hop_limit"] = http_put_response_hop_limit
        if http_tokens is not None:
            self._values["http_tokens"] = http_tokens
        if instance_initiated_shutdown_behavior is not None:
            self._values["instance_initiated_shutdown_behavior"] = instance_initiated_shutdown_behavior
        if instance_metadata_tags is not None:
            self._values["instance_metadata_tags"] = instance_metadata_tags
        if instance_profile is not None:
            self._values["instance_profile"] = instance_profile
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if key_name is not None:
            self._values["key_name"] = key_name
        if key_pair is not None:
            self._values["key_pair"] = key_pair
        if launch_template_name is not None:
            self._values["launch_template_name"] = launch_template_name
        if machine_image is not None:
            self._values["machine_image"] = machine_image
        if nitro_enclave_enabled is not None:
            self._values["nitro_enclave_enabled"] = nitro_enclave_enabled
        if require_imdsv2 is not None:
            self._values["require_imdsv2"] = require_imdsv2
        if role is not None:
            self._values["role"] = role
        if security_group is not None:
            self._values["security_group"] = security_group
        if spot_options is not None:
            self._values["spot_options"] = spot_options
        if user_data is not None:
            self._values["user_data"] = user_data
        if version_description is not None:
            self._values["version_description"] = version_description

    @builtins.property
    def associate_public_ip_address(self) -> typing.Optional[builtins.bool]:
        '''Whether instances should have a public IP addresses associated with them.

        :default: - Use subnet settings
        '''
        result = self._values.get("associate_public_ip_address")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def block_devices(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.BlockDevice]]:
        '''Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes.

        Each instance that is launched has an associated root device volume,
        either an Amazon EBS volume or an instance store volume.
        You can use block device mappings to specify additional EBS volumes or
        instance store volumes to attach to an instance when it is launched.

        :default: - Uses the block device mapping of the AMI

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html
        '''
        result = self._values.get("block_devices")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.BlockDevice]], result)

    @builtins.property
    def cpu_credits(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits]:
        '''CPU credit type for burstable EC2 instance types.

        :default: - No credit type is specified in the Launch Template.

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-performance-instances.html
        '''
        result = self._values.get("cpu_credits")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits], result)

    @builtins.property
    def detailed_monitoring(self) -> typing.Optional[builtins.bool]:
        '''If set to true, then detailed monitoring will be enabled on instances created with this launch template.

        :default: False - Detailed monitoring is disabled.

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-cloudwatch-new.html
        '''
        result = self._values.get("detailed_monitoring")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_api_termination(self) -> typing.Optional[builtins.bool]:
        '''If you set this parameter to true, you cannot terminate the instances launched with this launch template using the Amazon EC2 console, CLI, or API;

        otherwise, you can.

        :default: - The API termination setting is not specified in the Launch Template.
        '''
        result = self._values.get("disable_api_termination")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ebs_optimized(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the instances are optimized for Amazon EBS I/O.

        This optimization provides dedicated throughput
        to Amazon EBS and an optimized configuration stack to provide optimal Amazon EBS I/O performance. This optimization
        isn't available with all instance types. Additional usage charges apply when using an EBS-optimized instance.

        :default: - EBS optimization is not specified in the launch template.
        '''
        result = self._values.get("ebs_optimized")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def hibernation_configured(self) -> typing.Optional[builtins.bool]:
        '''If you set this parameter to true, the instance is enabled for hibernation.

        :default: - Hibernation configuration is not specified in the launch template; defaulting to false.
        '''
        result = self._values.get("hibernation_configured")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def http_endpoint(self) -> typing.Optional[builtins.bool]:
        '''Enables or disables the HTTP metadata endpoint on your instances.

        :default: true

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-metadataoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-metadataoptions-httpendpoint
        '''
        result = self._values.get("http_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def http_protocol_ipv6(self) -> typing.Optional[builtins.bool]:
        '''Enables or disables the IPv6 endpoint for the instance metadata service.

        :default: true

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-metadataoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-metadataoptions-httpprotocolipv6
        '''
        result = self._values.get("http_protocol_ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def http_put_response_hop_limit(self) -> typing.Optional[jsii.Number]:
        '''The desired HTTP PUT response hop limit for instance metadata requests.

        The larger the number, the further instance metadata requests can travel.

        :default: 1

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-metadataoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-metadataoptions-httpputresponsehoplimit
        '''
        result = self._values.get("http_put_response_hop_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_tokens(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateHttpTokens]:
        '''The state of token usage for your instance metadata requests.

        The default state is ``optional`` if not specified. However,
        if requireImdsv2 is true, the state must be ``required``.

        :default: LaunchTemplateHttpTokens.OPTIONAL

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-metadataoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-metadataoptions-httptokens
        '''
        result = self._values.get("http_tokens")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateHttpTokens], result)

    @builtins.property
    def instance_initiated_shutdown_behavior(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior]:
        '''Indicates whether an instance stops or terminates when you initiate shutdown from the instance (using the operating system command for system shutdown).

        :default: - Shutdown behavior is not specified in the launch template; defaults to STOP.

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/terminating-instances.html#Using_ChangingInstanceInitiatedShutdownBehavior
        '''
        result = self._values.get("instance_initiated_shutdown_behavior")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior], result)

    @builtins.property
    def instance_metadata_tags(self) -> typing.Optional[builtins.bool]:
        '''Set to enabled to allow access to instance tags from the instance metadata.

        Set to disabled to turn off access to instance tags from the instance metadata.

        :default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-metadataoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-metadataoptions-instancemetadatatags
        '''
        result = self._values.get("instance_metadata_tags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_profile(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile]:
        '''The instance profile used to pass role information to EC2 instances.

        Note: You can provide an instanceProfile or a role, but not both.

        :default: - No instance profile
        '''
        result = self._values.get("instance_profile")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''Type of instance to launch.

        :default: - This Launch Template does not specify a default Instance Type.
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Name of SSH keypair to grant access to instance.

        :default: - No SSH access will be possible.

        :deprecated: - Use ``keyPair`` instead - https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2-readme.html#using-an-existing-ec2-key-pair

        :stability: deprecated
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_pair(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair]:
        '''The SSH keypair to grant access to the instance.

        :default: - No SSH access will be possible.
        '''
        result = self._values.get("key_pair")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair], result)

    @builtins.property
    def launch_template_name(self) -> typing.Optional[builtins.str]:
        '''Name for this launch template.

        :default: Automatically generated name
        '''
        result = self._values.get("launch_template_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def machine_image(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage]:
        '''The AMI that will be used by instances.

        :default: - This Launch Template does not specify a default AMI.
        '''
        result = self._values.get("machine_image")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage], result)

    @builtins.property
    def nitro_enclave_enabled(self) -> typing.Optional[builtins.bool]:
        '''If this parameter is set to true, the instance is enabled for AWS Nitro Enclaves;

        otherwise, it is not enabled for AWS Nitro Enclaves.

        :default: - Enablement of Nitro enclaves is not specified in the launch template; defaulting to false.
        '''
        result = self._values.get("nitro_enclave_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_imdsv2(self) -> typing.Optional[builtins.bool]:
        '''Whether IMDSv2 should be required on launched instances.

        :default: - false
        '''
        result = self._values.get("require_imdsv2")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''An IAM role to associate with the instance profile that is used by instances.

        The role must be assumable by the service principal ``ec2.amazonaws.com``.
        Note: You can provide an instanceProfile or a role, but not both.

        :default: - No new role is created.

        Example::

            const role = new iam.Role(this, 'MyRole', {
              assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com')
            });
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''Security group to assign to instances created with the launch template.

        :default: No security group is assigned.
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def spot_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateSpotOptions]:
        '''If this property is defined, then the Launch Template's InstanceMarketOptions will be set to use Spot instances, and the options for the Spot instances will be as defined.

        :default: - Instance launched with this template will not be spot instances.
        '''
        result = self._values.get("spot_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateSpotOptions], result)

    @builtins.property
    def user_data(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData]:
        '''The AMI that will be used by instances.

        :default:

        - This Launch Template creates a UserData based on the type of provided
        machineImage; no UserData is created if a machineImage is not provided
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData], result)

    @builtins.property
    def version_description(self) -> typing.Optional[builtins.str]:
        '''A description for the first version of the launch template.

        The version description must be maximum 255 characters long.

        :default: - No description

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html#cfn-ec2-launchtemplate-versiondescription
        '''
        result = self._values.get("version_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_interface(self) -> INetworkInterface:
        '''The Elastic Network Interface to use.'''
        result = self._values.get("network_interface")
        assert result is not None, "Required property 'network_interface' is missing"
        return typing.cast(INetworkInterface, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SingletonLaunchTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.networking.TargetOptions",
    jsii_struct_bases=[
        _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroupProps
    ],
    name_mapping={
        "cross_zone_enabled": "crossZoneEnabled",
        "deregistration_delay": "deregistrationDelay",
        "health_check": "healthCheck",
        "ip_address_type": "ipAddressType",
        "target_group_name": "targetGroupName",
        "target_type": "targetType",
        "vpc": "vpc",
        "enable_anomaly_mitigation": "enableAnomalyMitigation",
        "load_balancing_algorithm_type": "loadBalancingAlgorithmType",
        "port": "port",
        "protocol": "protocol",
        "protocol_version": "protocolVersion",
        "slow_start": "slowStart",
        "stickiness_cookie_duration": "stickinessCookieDuration",
        "stickiness_cookie_name": "stickinessCookieName",
        "targets": "targets",
        "hostnames": "hostnames",
        "priority": "priority",
    },
)
class TargetOptions(
    _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroupProps,
):
    def __init__(
        self,
        *,
        cross_zone_enabled: typing.Optional[builtins.bool] = None,
        deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupIpAddressType] = None,
        target_group_name: typing.Optional[builtins.str] = None,
        target_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        enable_anomaly_mitigation: typing.Optional[builtins.bool] = None,
        load_balancing_algorithm_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType] = None,
        port: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        slow_start: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        stickiness_cookie_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        stickiness_cookie_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]] = None,
        hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Options for adding a new target group.

        :param cross_zone_enabled: Indicates whether cross zone load balancing is enabled. Default: - use load balancer configuration
        :param deregistration_delay: The amount of time for Elastic Load Balancing to wait before deregistering a target. The range is 0-3600 seconds. Default: 300
        :param health_check: Health check configuration. Default: - The default value for each property in this configuration varies depending on the target.
        :param ip_address_type: The type of IP addresses of the targets registered with the target group. Default: undefined - ELB defaults to IPv4
        :param target_group_name: The name of the target group. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen. Default: - Automatically generated.
        :param target_type: The type of targets registered to this TargetGroup, either IP or Instance. All targets registered into the group must be of this type. If you register targets to the TargetGroup in the CDK app, the TargetType is determined automatically. Default: - Determined automatically.
        :param vpc: The virtual private cloud (VPC). only if ``TargetType`` is ``Ip`` or ``InstanceId`` Default: - undefined
        :param enable_anomaly_mitigation: Indicates whether anomaly mitigation is enabled. Only available when ``loadBalancingAlgorithmType`` is ``TargetGroupLoadBalancingAlgorithmType.WEIGHTED_RANDOM`` Default: false
        :param load_balancing_algorithm_type: The load balancing algorithm to select targets for routing requests. Default: TargetGroupLoadBalancingAlgorithmType.ROUND_ROBIN
        :param port: The port on which the target receives traffic. This is not applicable for Lambda targets. Default: - Determined from protocol if known
        :param protocol: The protocol used for communication with the target. This is not applicable for Lambda targets. Default: - Determined from port if known
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param slow_start: The time period during which the load balancer sends a newly registered target a linearly increasing share of the traffic to the target group. The range is 30-900 seconds (15 minutes). Default: 0
        :param stickiness_cookie_duration: The stickiness cookie expiration period. Setting this value enables load balancer stickiness. After this period, the cookie is considered stale. The minimum value is 1 second and the maximum value is 7 days (604800 seconds). Default: - Stickiness is disabled
        :param stickiness_cookie_name: The name of an application-based stickiness cookie. Names that start with the following prefixes are not allowed: AWSALB, AWSALBAPP, and AWSALBTG; they're reserved for use by the load balancer. Note: ``stickinessCookieName`` parameter depends on the presence of ``stickinessCookieDuration`` parameter. If ``stickinessCookieDuration`` is not set, ``stickinessCookieName`` will be omitted. Default: - If ``stickinessCookieDuration`` is set, a load-balancer generated cookie is used. Otherwise, no stickiness is defined.
        :param targets: The targets to add to this target group. Can be ``Instance``, ``IPAddress``, or any self-registering load balancing target. If you use either ``Instance`` or ``IPAddress`` as targets, all target must be of the same type. Default: - No targets.
        :param hostnames: The hostnames on which traffic is served.
        :param priority: The priority of the listener rule. Default: - Automatically determined
        '''
        if isinstance(health_check, dict):
            health_check = _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck(**health_check)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efa2d39cd1f01bf3758addd640ec7d1a822d75c3cc97424ddff8b739dca8d900)
            check_type(argname="argument cross_zone_enabled", value=cross_zone_enabled, expected_type=type_hints["cross_zone_enabled"])
            check_type(argname="argument deregistration_delay", value=deregistration_delay, expected_type=type_hints["deregistration_delay"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument ip_address_type", value=ip_address_type, expected_type=type_hints["ip_address_type"])
            check_type(argname="argument target_group_name", value=target_group_name, expected_type=type_hints["target_group_name"])
            check_type(argname="argument target_type", value=target_type, expected_type=type_hints["target_type"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument enable_anomaly_mitigation", value=enable_anomaly_mitigation, expected_type=type_hints["enable_anomaly_mitigation"])
            check_type(argname="argument load_balancing_algorithm_type", value=load_balancing_algorithm_type, expected_type=type_hints["load_balancing_algorithm_type"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument protocol_version", value=protocol_version, expected_type=type_hints["protocol_version"])
            check_type(argname="argument slow_start", value=slow_start, expected_type=type_hints["slow_start"])
            check_type(argname="argument stickiness_cookie_duration", value=stickiness_cookie_duration, expected_type=type_hints["stickiness_cookie_duration"])
            check_type(argname="argument stickiness_cookie_name", value=stickiness_cookie_name, expected_type=type_hints["stickiness_cookie_name"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument hostnames", value=hostnames, expected_type=type_hints["hostnames"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cross_zone_enabled is not None:
            self._values["cross_zone_enabled"] = cross_zone_enabled
        if deregistration_delay is not None:
            self._values["deregistration_delay"] = deregistration_delay
        if health_check is not None:
            self._values["health_check"] = health_check
        if ip_address_type is not None:
            self._values["ip_address_type"] = ip_address_type
        if target_group_name is not None:
            self._values["target_group_name"] = target_group_name
        if target_type is not None:
            self._values["target_type"] = target_type
        if vpc is not None:
            self._values["vpc"] = vpc
        if enable_anomaly_mitigation is not None:
            self._values["enable_anomaly_mitigation"] = enable_anomaly_mitigation
        if load_balancing_algorithm_type is not None:
            self._values["load_balancing_algorithm_type"] = load_balancing_algorithm_type
        if port is not None:
            self._values["port"] = port
        if protocol is not None:
            self._values["protocol"] = protocol
        if protocol_version is not None:
            self._values["protocol_version"] = protocol_version
        if slow_start is not None:
            self._values["slow_start"] = slow_start
        if stickiness_cookie_duration is not None:
            self._values["stickiness_cookie_duration"] = stickiness_cookie_duration
        if stickiness_cookie_name is not None:
            self._values["stickiness_cookie_name"] = stickiness_cookie_name
        if targets is not None:
            self._values["targets"] = targets
        if hostnames is not None:
            self._values["hostnames"] = hostnames
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def cross_zone_enabled(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether cross zone load balancing is enabled.

        :default: - use load balancer configuration

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-targetgroup-targetgroupattribute.html
        '''
        result = self._values.get("cross_zone_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deregistration_delay(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The amount of time for Elastic Load Balancing to wait before deregistering a target.

        The range is 0-3600 seconds.

        :default: 300
        '''
        result = self._values.get("deregistration_delay")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def health_check(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck]:
        '''Health check configuration.

        :default: - The default value for each property in this configuration varies depending on the target.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-targetgroup.html#aws-resource-elasticloadbalancingv2-targetgroup-properties
        '''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck], result)

    @builtins.property
    def ip_address_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupIpAddressType]:
        '''The type of IP addresses of the targets registered with the target group.

        :default: undefined - ELB defaults to IPv4
        '''
        result = self._values.get("ip_address_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupIpAddressType], result)

    @builtins.property
    def target_group_name(self) -> typing.Optional[builtins.str]:
        '''The name of the target group.

        This name must be unique per region per account, can have a maximum of
        32 characters, must contain only alphanumeric characters or hyphens, and
        must not begin or end with a hyphen.

        :default: - Automatically generated.
        '''
        result = self._values.get("target_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType]:
        '''The type of targets registered to this TargetGroup, either IP or Instance.

        All targets registered into the group must be of this type. If you
        register targets to the TargetGroup in the CDK app, the TargetType is
        determined automatically.

        :default: - Determined automatically.
        '''
        result = self._values.get("target_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The virtual private cloud (VPC).

        only if ``TargetType`` is ``Ip`` or ``InstanceId``

        :default: - undefined
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def enable_anomaly_mitigation(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether anomaly mitigation is enabled.

        Only available when ``loadBalancingAlgorithmType`` is ``TargetGroupLoadBalancingAlgorithmType.WEIGHTED_RANDOM``

        :default: false

        :see: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html#automatic-target-weights
        '''
        result = self._values.get("enable_anomaly_mitigation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def load_balancing_algorithm_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType]:
        '''The load balancing algorithm to select targets for routing requests.

        :default: TargetGroupLoadBalancingAlgorithmType.ROUND_ROBIN
        '''
        result = self._values.get("load_balancing_algorithm_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The port on which the target receives traffic.

        This is not applicable for Lambda targets.

        :default: - Determined from protocol if known
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol used for communication with the target.

        This is not applicable for Lambda targets.

        :default: - Determined from port if known
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def protocol_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion]:
        '''The protocol version to use.

        :default: ApplicationProtocolVersion.HTTP1
        '''
        result = self._values.get("protocol_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion], result)

    @builtins.property
    def slow_start(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The time period during which the load balancer sends a newly registered target a linearly increasing share of the traffic to the target group.

        The range is 30-900 seconds (15 minutes).

        :default: 0
        '''
        result = self._values.get("slow_start")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def stickiness_cookie_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The stickiness cookie expiration period.

        Setting this value enables load balancer stickiness.

        After this period, the cookie is considered stale. The minimum value is
        1 second and the maximum value is 7 days (604800 seconds).

        :default: - Stickiness is disabled
        '''
        result = self._values.get("stickiness_cookie_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def stickiness_cookie_name(self) -> typing.Optional[builtins.str]:
        '''The name of an application-based stickiness cookie.

        Names that start with the following prefixes are not allowed: AWSALB, AWSALBAPP,
        and AWSALBTG; they're reserved for use by the load balancer.

        Note: ``stickinessCookieName`` parameter depends on the presence of ``stickinessCookieDuration`` parameter.
        If ``stickinessCookieDuration`` is not set, ``stickinessCookieName`` will be omitted.

        :default: - If ``stickinessCookieDuration`` is set, a load-balancer generated cookie is used. Otherwise, no stickiness is defined.

        :see: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/sticky-sessions.html
        '''
        result = self._values.get("stickiness_cookie_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]]:
        '''The targets to add to this target group.

        Can be ``Instance``, ``IPAddress``, or any self-registering load balancing
        target. If you use either ``Instance`` or ``IPAddress`` as targets, all
        target must be of the same type.

        :default: - No targets.
        '''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]], result)

    @builtins.property
    def hostnames(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The hostnames on which traffic is served.'''
        result = self._values.get("hostnames")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''The priority of the listener rule.

        :default: - Automatically determined
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebLoadBalancing(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.WebLoadBalancing",
):
    '''A utility for creating a public-facing Application Load Balancer.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
        require_known_hostname: typing.Optional[builtins.bool] = None,
        require_secret_header: typing.Optional[builtins.bool] = None,
        secret_header_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    ) -> None:
        '''Creates a new WebLoadBalancing.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param certificates: The certificate to attach to the load balancer and CloudFront distribution.
        :param vpc: The VPC where these resources should be deployed.
        :param idle_timeout: The load balancer idle timeout, in seconds. If you have a reverse proxy in front of this load balancer, such as CloudFront, this number should be less than the reverse proxy's request timeout. Default: - 59 seconds
        :param ip_address_type: The type of IP addresses to use (IPv4 or Dual Stack). Default: - IPv4 only
        :param require_known_hostname: Forbid requests that ask for an unknown hostname. Requests for an unknown hostname will receive an HTTP 421 status response. Default: - false
        :param require_secret_header: Forbid requests that are missing an HTTP header with a specific value. If this option is set to ``true``, this construct will provide a new ``SecretHttpHeader`` accessible on the ``secretHeader`` property. Requests without the correct header name and value will receive an HTTP 421 status response. Default: - false
        :param secret_header_name: The name of the secret HTTP header. Providing this option implies that ``requireSecretHeader`` is ``true``. Default: - X-Secret-Passphrase
        :param security_group: A security group for the load balancer itself. Default: - A new security group will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56342186b82314e198297a3e5364d68b3f8d14f18d4e2c17b5f18a47bffc93d3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebLoadBalancingProps(
            certificates=certificates,
            vpc=vpc,
            idle_timeout=idle_timeout,
            ip_address_type=ip_address_type,
            require_known_hostname=require_known_hostname,
            require_secret_header=require_secret_header,
            secret_header_name=secret_header_name,
            security_group=security_group,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addTarget")
    def add_target(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget,
        *,
        hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
        priority: typing.Optional[jsii.Number] = None,
        enable_anomaly_mitigation: typing.Optional[builtins.bool] = None,
        load_balancing_algorithm_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType] = None,
        port: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        slow_start: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        stickiness_cookie_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        stickiness_cookie_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]] = None,
        cross_zone_enabled: typing.Optional[builtins.bool] = None,
        deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupIpAddressType] = None,
        target_group_name: typing.Optional[builtins.str] = None,
        target_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup:
        '''Adds a target to the listener.

        If the following options are left undefined, these defaults will be used.

        - ``port``: 443
        - ``protocol``: HTTPS
        - ``deregistrationDelay``: load balancer idle timeout
        - ``healthCheck.path``: /
        - ``healthCheck.healthyThresholdCount``: 2
        - ``healthCheck.interval``: 30 seconds
        - ``healthCheck.timeout``: 29 seconds

        :param id: - The ID of the new target group.
        :param target: - The load balancing target to receive traffic.
        :param hostnames: The hostnames on which traffic is served.
        :param priority: The priority of the listener rule. Default: - Automatically determined
        :param enable_anomaly_mitigation: Indicates whether anomaly mitigation is enabled. Only available when ``loadBalancingAlgorithmType`` is ``TargetGroupLoadBalancingAlgorithmType.WEIGHTED_RANDOM`` Default: false
        :param load_balancing_algorithm_type: The load balancing algorithm to select targets for routing requests. Default: TargetGroupLoadBalancingAlgorithmType.ROUND_ROBIN
        :param port: The port on which the target receives traffic. This is not applicable for Lambda targets. Default: - Determined from protocol if known
        :param protocol: The protocol used for communication with the target. This is not applicable for Lambda targets. Default: - Determined from port if known
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param slow_start: The time period during which the load balancer sends a newly registered target a linearly increasing share of the traffic to the target group. The range is 30-900 seconds (15 minutes). Default: 0
        :param stickiness_cookie_duration: The stickiness cookie expiration period. Setting this value enables load balancer stickiness. After this period, the cookie is considered stale. The minimum value is 1 second and the maximum value is 7 days (604800 seconds). Default: - Stickiness is disabled
        :param stickiness_cookie_name: The name of an application-based stickiness cookie. Names that start with the following prefixes are not allowed: AWSALB, AWSALBAPP, and AWSALBTG; they're reserved for use by the load balancer. Note: ``stickinessCookieName`` parameter depends on the presence of ``stickinessCookieDuration`` parameter. If ``stickinessCookieDuration`` is not set, ``stickinessCookieName`` will be omitted. Default: - If ``stickinessCookieDuration`` is set, a load-balancer generated cookie is used. Otherwise, no stickiness is defined.
        :param targets: The targets to add to this target group. Can be ``Instance``, ``IPAddress``, or any self-registering load balancing target. If you use either ``Instance`` or ``IPAddress`` as targets, all target must be of the same type. Default: - No targets.
        :param cross_zone_enabled: Indicates whether cross zone load balancing is enabled. Default: - use load balancer configuration
        :param deregistration_delay: The amount of time for Elastic Load Balancing to wait before deregistering a target. The range is 0-3600 seconds. Default: 300
        :param health_check: Health check configuration. Default: - The default value for each property in this configuration varies depending on the target.
        :param ip_address_type: The type of IP addresses of the targets registered with the target group. Default: undefined - ELB defaults to IPv4
        :param target_group_name: The name of the target group. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen. Default: - Automatically generated.
        :param target_type: The type of targets registered to this TargetGroup, either IP or Instance. All targets registered into the group must be of this type. If you register targets to the TargetGroup in the CDK app, the TargetType is determined automatically. Default: - Determined automatically.
        :param vpc: The virtual private cloud (VPC). only if ``TargetType`` is ``Ip`` or ``InstanceId`` Default: - undefined

        :return: The new Application Target Group
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7e0fb1b7097e928299c71e17989f2f1e1385330c18446d1a211d9b57fa16cc8)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = TargetOptions(
            hostnames=hostnames,
            priority=priority,
            enable_anomaly_mitigation=enable_anomaly_mitigation,
            load_balancing_algorithm_type=load_balancing_algorithm_type,
            port=port,
            protocol=protocol,
            protocol_version=protocol_version,
            slow_start=slow_start,
            stickiness_cookie_duration=stickiness_cookie_duration,
            stickiness_cookie_name=stickiness_cookie_name,
            targets=targets,
            cross_zone_enabled=cross_zone_enabled,
            deregistration_delay=deregistration_delay,
            health_check=health_check,
            ip_address_type=ip_address_type,
            target_group_name=target_group_name,
            target_type=target_type,
            vpc=vpc,
        )

        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup, jsii.invoke(self, "addTarget", [id, target, options]))

    @builtins.property
    @jsii.member(jsii_name="listener")
    def listener(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener:
        '''The HTTPS listener.'''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener, jsii.get(self, "listener"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer:
        '''The load balancer itself.'''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer, jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="secretHeader")
    def secret_header(self) -> typing.Optional[ISecretHttpHeader]:
        '''The secret header (if ``requireSecretHeader`` was set to ``true``).'''
        return typing.cast(typing.Optional[ISecretHttpHeader], jsii.get(self, "secretHeader"))


@jsii.data_type(
    jsii_type="shady-island.networking.WebLoadBalancingProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificates": "certificates",
        "vpc": "vpc",
        "idle_timeout": "idleTimeout",
        "ip_address_type": "ipAddressType",
        "require_known_hostname": "requireKnownHostname",
        "require_secret_header": "requireSecretHeader",
        "secret_header_name": "secretHeaderName",
        "security_group": "securityGroup",
    },
)
class WebLoadBalancingProps:
    def __init__(
        self,
        *,
        certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
        require_known_hostname: typing.Optional[builtins.bool] = None,
        require_secret_header: typing.Optional[builtins.bool] = None,
        secret_header_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    ) -> None:
        '''Constructor properties for WebLoadBalancing.

        :param certificates: The certificate to attach to the load balancer and CloudFront distribution.
        :param vpc: The VPC where these resources should be deployed.
        :param idle_timeout: The load balancer idle timeout, in seconds. If you have a reverse proxy in front of this load balancer, such as CloudFront, this number should be less than the reverse proxy's request timeout. Default: - 59 seconds
        :param ip_address_type: The type of IP addresses to use (IPv4 or Dual Stack). Default: - IPv4 only
        :param require_known_hostname: Forbid requests that ask for an unknown hostname. Requests for an unknown hostname will receive an HTTP 421 status response. Default: - false
        :param require_secret_header: Forbid requests that are missing an HTTP header with a specific value. If this option is set to ``true``, this construct will provide a new ``SecretHttpHeader`` accessible on the ``secretHeader`` property. Requests without the correct header name and value will receive an HTTP 421 status response. Default: - false
        :param secret_header_name: The name of the secret HTTP header. Providing this option implies that ``requireSecretHeader`` is ``true``. Default: - X-Secret-Passphrase
        :param security_group: A security group for the load balancer itself. Default: - A new security group will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cf2c4b4f6d95905cc594637cb1f8523593a0d81a22f8200dc8eec640482dee1)
            check_type(argname="argument certificates", value=certificates, expected_type=type_hints["certificates"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument ip_address_type", value=ip_address_type, expected_type=type_hints["ip_address_type"])
            check_type(argname="argument require_known_hostname", value=require_known_hostname, expected_type=type_hints["require_known_hostname"])
            check_type(argname="argument require_secret_header", value=require_secret_header, expected_type=type_hints["require_secret_header"])
            check_type(argname="argument secret_header_name", value=secret_header_name, expected_type=type_hints["secret_header_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificates": certificates,
            "vpc": vpc,
        }
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if ip_address_type is not None:
            self._values["ip_address_type"] = ip_address_type
        if require_known_hostname is not None:
            self._values["require_known_hostname"] = require_known_hostname
        if require_secret_header is not None:
            self._values["require_secret_header"] = require_secret_header
        if secret_header_name is not None:
            self._values["secret_header_name"] = secret_header_name
        if security_group is not None:
            self._values["security_group"] = security_group

    @builtins.property
    def certificates(
        self,
    ) -> typing.List[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''The certificate to attach to the load balancer and CloudFront distribution.'''
        result = self._values.get("certificates")
        assert result is not None, "Required property 'certificates' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where these resources should be deployed.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The load balancer idle timeout, in seconds.

        If you have a reverse proxy in front of this load balancer, such as
        CloudFront, this number should be less than the reverse proxy's request
        timeout.

        :default: - 59 seconds
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def ip_address_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType]:
        '''The type of IP addresses to use (IPv4 or Dual Stack).

        :default: - IPv4 only
        '''
        result = self._values.get("ip_address_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType], result)

    @builtins.property
    def require_known_hostname(self) -> typing.Optional[builtins.bool]:
        '''Forbid requests that ask for an unknown hostname.

        Requests for an unknown hostname will receive an HTTP 421 status response.

        :default: - false
        '''
        result = self._values.get("require_known_hostname")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_secret_header(self) -> typing.Optional[builtins.bool]:
        '''Forbid requests that are missing an HTTP header with a specific value.

        If this option is set to ``true``, this construct will provide a new
        ``SecretHttpHeader`` accessible on the ``secretHeader`` property.

        Requests without the correct header name and value will receive an HTTP 421
        status response.

        :default: - false
        '''
        result = self._values.get("require_secret_header")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def secret_header_name(self) -> typing.Optional[builtins.str]:
        '''The name of the secret HTTP header.

        Providing this option implies that ``requireSecretHeader`` is ``true``.

        :default: - X-Secret-Passphrase
        '''
        result = self._values.get("secret_header_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''A security group for the load balancer itself.

        :default: - A new security group will be created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebLoadBalancingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IDomain)
class BaseDomain(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="shady-island.networking.BaseDomain",
):
    '''A DNS domain and its wildcard X.509 certificate.'''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10552300e8f97cdf7fb31b39d6f0ccd45aa560ac32634a146e2c4f13e6e0ecd2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property
    @jsii.member(jsii_name="certificate")
    @abc.abstractmethod
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''The wildcard certificate for resources in this domain.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="hostedZone")
    @abc.abstractmethod
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone that contains records for this domain.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    @abc.abstractmethod
    def name(self) -> builtins.str:
        '''The fully-qualified domain name of the hosted zone.'''
        ...


class _BaseDomainProxy(BaseDomain):
    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''The wildcard certificate for resources in this domain.'''
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone that contains records for this domain.'''
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, jsii.get(self, "hostedZone"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The fully-qualified domain name of the hosted zone.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseDomain).__jsii_proxy_class__ = lambda : _BaseDomainProxy


class CrossAccountDelegationDomain(
    BaseDomain,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.CrossAccountDelegationDomain",
):
    '''Provides a domain using delegation from a parent zone in another account.

    This construct creates a new Route 53 hosted zone for the subdomain, a zone
    delegation record, and a new wildcard ACM certificate for the subdomain.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        delegation_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        subdomain: builtins.str,
        assume_role_region: typing.Optional[builtins.str] = None,
        parent_hosted_zone_id: typing.Optional[builtins.str] = None,
        parent_hosted_zone_name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param delegation_role: The delegation role in the parent account.
        :param subdomain: The subdomain in the parent hosted zone.
        :param assume_role_region: Region from which to obtain temporary credentials. Default: - the Route53 signing region in the current partition
        :param parent_hosted_zone_id: The hosted zone id in the parent account. Default: - hosted zone ID will be looked up based on the zone name
        :param parent_hosted_zone_name: The hosted zone name in the parent account. Default: - no zone name
        :param removal_policy: The removal policy to apply. Default: RemovalPolicy.DESTROY
        :param ttl: The resource record cache time to live (TTL). Default: Duration.days(2)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7304c09f1b06d2d920c724dcf3ff3fceb9fc47af8746c6da6f888c8d57808849)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrossAccountDelegationDomainProps(
            delegation_role=delegation_role,
            subdomain=subdomain,
            assume_role_region=assume_role_region,
            parent_hosted_zone_id=parent_hosted_zone_id,
            parent_hosted_zone_name=parent_hosted_zone_name,
            removal_policy=removal_policy,
            ttl=ttl,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''The wildcard certificate for resources in this domain.'''
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone that contains records for this domain.'''
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, jsii.get(self, "hostedZone"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The fully-qualified domain name of the hosted zone.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))


class DelegationDomain(
    BaseDomain,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.DelegationDomain",
):
    '''Provides a domain using delegation from a parent zone in the same account.

    This construct creates a new Route 53 hosted zone for the subdomain, a zone
    delegation record, and a new wildcard ACM certificate for the subdomain.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        parent_hosted_zone: _aws_cdk_aws_route53_ceddda9d.IPublicHostedZone,
        subdomain: builtins.str,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param parent_hosted_zone: The parent/delegating hosted zone. The "zone name" is needed.
        :param subdomain: The subdomain in the parent hosted zone.
        :param removal_policy: The removal policy to apply. Default: RemovalPolicy.DESTROY
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bc124d22b2b560d8ad6016cf5d0292be2f09e4a6659b58e2c166110dbd561c1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DelegationDomainProps(
            parent_hosted_zone=parent_hosted_zone,
            subdomain=subdomain,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="applyRemovalPolicy")
    def apply_removal_policy(self, policy: _aws_cdk_ceddda9d.RemovalPolicy) -> None:
        '''
        :param policy: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7866a53522992f55bdc325d1838ef58974b20f4f752692262b9d8a7a24aa6c4)
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
        return typing.cast(None, jsii.invoke(self, "applyRemovalPolicy", [policy]))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''The wildcard certificate for resources in this domain.'''
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone that contains records for this domain.'''
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, jsii.get(self, "hostedZone"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The fully-qualified domain name of the hosted zone.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))


@jsii.implements(IElasticIp)
class ElasticIp(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.ElasticIp",
):
    '''An EC2 Elastic IP address.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Creates a new Elastic IP address.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param removal_policy: The removal policy for this resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__329313caf887f63821d7884bee2092f3a6d442a6c1c96f75770081998a95873e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ElasticIpProps(removal_policy=removal_policy)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAllocationId")
    @builtins.classmethod
    def from_allocation_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        allocation_id: builtins.str,
    ) -> IElasticIp:
        '''Import an existing EIP from the given allocation ID.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param allocation_id: - The EIP allocation ID.

        :return: The imported Elastic IP
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e82bf067154d978cd348f21fa71899f0687720ef3d7622a28287b58a275f1dd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument allocation_id", value=allocation_id, expected_type=type_hints["allocation_id"])
        return typing.cast(IElasticIp, jsii.sinvoke(cls, "fromAllocationId", [scope, id, allocation_id]))

    @jsii.member(jsii_name="fromElasticIpArn")
    @builtins.classmethod
    def from_elastic_ip_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> IElasticIp:
        '''Import an existing EIP from its ARN.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param arn: - The EIP ARN.

        :return: The imported Elastic IP
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__935c29310156a369b6e7213f9c82204a5cb0f35b37e585a9b48489f94e73980c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast(IElasticIp, jsii.sinvoke(cls, "fromElasticIpArn", [scope, id, arn]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant the given identity custom permissions.

        e.g. ``ec2:AssociateAddress``, ``ec2:DisableAddressTransfer``,
        ``ec2:DisassociateAddress``, ``ec2:EnableAddressTransfer``, among others.

        :param identity: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__610789115b0fd3b9297114da0749e7767d3eeff76e4daa1ede9a061ac66887d0)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [identity, *actions]))

    @builtins.property
    @jsii.member(jsii_name="allocationId")
    def allocation_id(self) -> builtins.str:
        '''The allocation ID of the Elastic IP address.'''
        return typing.cast(builtins.str, jsii.get(self, "allocationId"))

    @builtins.property
    @jsii.member(jsii_name="elasticIpArn")
    def elastic_ip_arn(self) -> builtins.str:
        '''The ARN of the Elastic IP address.'''
        return typing.cast(builtins.str, jsii.get(self, "elasticIpArn"))

    @builtins.property
    @jsii.member(jsii_name="publicIp")
    def public_ip(self) -> builtins.str:
        '''The IPv4 address.'''
        return typing.cast(builtins.str, jsii.get(self, "publicIp"))


class ExistingZoneDomain(
    BaseDomain,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.ExistingZoneDomain",
):
    '''Provides a domain using an existing hosted zone.

    This construct will create a new wildcard ACM certificate using the existing
    hosted zone name.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: The hosted zone that contains records for this domain.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3fd35c400f55d4fdfc3d9c58d10af525a284162188c631752bc5a18bccb9d30)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ExistingZoneDomainProps(hosted_zone=hosted_zone)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromDomainAttributes")
    @builtins.classmethod
    def from_domain_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    ) -> IDomain:
        '''Returns an ExistingZoneDomain using the provided attributes.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param certificate: The wildcard certificate for resources in this domain.
        :param hosted_zone: The hosted zone that contains records for this domain.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68321a0ac14d003a13037e7f7cd1855d87f43d63ce3a00bfc39b8bfa7b0c2e76)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = DomainAttributes(certificate=certificate, hosted_zone=hosted_zone)

        return typing.cast(IDomain, jsii.sinvoke(cls, "fromDomainAttributes", [scope, id, attrs]))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''The wildcard certificate for resources in this domain.'''
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone that contains records for this domain.'''
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, jsii.get(self, "hostedZone"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The fully-qualified domain name of the hosted zone.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))


__all__ = [
    "Address",
    "AddressingV4",
    "AddressingV6",
    "BaseDomain",
    "CrossAccountDelegationDomain",
    "CrossAccountDelegationDomainProps",
    "DelegationDomain",
    "DelegationDomainProps",
    "DomainAttributes",
    "ElasticIp",
    "ElasticIpProps",
    "ExistingZoneDomain",
    "ExistingZoneDomainProps",
    "IDomain",
    "IElasticIp",
    "INetworkInterface",
    "ISecretHttpHeader",
    "InterfaceType",
    "NetworkInterface",
    "NetworkInterfaceAttributes",
    "NetworkInterfaceProps",
    "SecretHttpHeader",
    "SecretHttpHeaderProps",
    "SingletonLaunchTemplate",
    "SingletonLaunchTemplateProps",
    "TargetOptions",
    "WebLoadBalancing",
    "WebLoadBalancingProps",
]

publication.publish()

def _typecheckingstub__7a987c1ff9ba835df538a008b65cb8eb591f8caa74f1db2104b731c619dee7b8(
    address: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c94a54535c07938766b16900ce0d84b06136bc5847f54b6161c4ebecaa3763e0(
    address: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2cddb2547e4ed3f4826e1acff079d40a4ba476ac141e3281f8b106c7455a04f(
    count: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01734a2088506c2015ca7bad849bebf81f4652662c5abd2af6e22d7e89d72a62(
    prefixes: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a558c981ad684205ae14b30ac86b63891341637e8de2255215f0d7fa9890c208(
    ip: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbd385d7d0a4b0a0306d6f92007994dc4caacd4f45b60696b74868ae7d9af7dc(
    primary: builtins.str,
    count: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__116c136600050bf89a1560721d3862fb3f20a3f55eeb11598bcf8676ad8363f8(
    primary: builtins.str,
    *secondary: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ed7da7903260aeba9877acff158981d9b2220d2610bb60c1601ce4a1cd07c80(
    count: jsii.Number,
    enable_primary: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16d92cdccfc5fcd12837debeb037bdf436f91a88257fd9f12e9dbea4b9846925(
    ips: typing.Sequence[builtins.str],
    enable_primary: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cd14df44bfcf87b8b5d2f04ad616f4497ecc8908a4f4f91379e46248a6772ee(
    count: jsii.Number,
    enable_primary: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4a8ad5afeb3637eae637f3afd75db4bc00b4274d8a8d486fdf734229f61687f(
    prefixes: typing.Sequence[builtins.str],
    enable_primary: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9136690bd7d16bb7a371b715fe1211443861d3a8d6541eaab01cf4170ca77d17(
    *,
    delegation_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    subdomain: builtins.str,
    assume_role_region: typing.Optional[builtins.str] = None,
    parent_hosted_zone_id: typing.Optional[builtins.str] = None,
    parent_hosted_zone_name: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4959679e489c9a86ddc074b02e8395bd95d85831305854ba5e2983fd01410095(
    *,
    parent_hosted_zone: _aws_cdk_aws_route53_ceddda9d.IPublicHostedZone,
    subdomain: builtins.str,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6063b0bee2cb1ea0569318144a7399ce89a581edb845cbd7a6cdc1927a9dbf3d(
    *,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e06451a98b33ab08a35c0a78b3d4d4c1c765f25e0a9ce8b560db827f5e389a61(
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db55134202f24932d26262ae10603b62237d295d85be8c87b7c06977a616ad6f(
    *,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c038201c2cdaabf12b23bf40d541b0618f6bd20657383b850c9ff3a6d96fdfb(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7881cbf5a93f60fb5d54843bd46460258c8f6351f8714f9e0bf51936cfb33a8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    description: typing.Optional[builtins.str] = None,
    elastic_ip: typing.Optional[IElasticIp] = None,
    enable_source_dest_check: typing.Optional[builtins.bool] = None,
    interface_type: typing.Optional[InterfaceType] = None,
    ipv4: typing.Optional[AddressingV4] = None,
    ipv6: typing.Optional[AddressingV6] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba90bf577e30a95879b04adea6a10e02d8003e632a56c3750ac72371cd4c3c19(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    network_interface_id: builtins.str,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__872ccdb97fb0caa6e086ac3826a89fb56cf8c89635737fdeec3c5edba3585c2e(
    *,
    network_interface_id: builtins.str,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ad8d033df0b3a5892f2030211876beee3fab00f8b29e23f9591cb251b26d102(
    *,
    subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    description: typing.Optional[builtins.str] = None,
    elastic_ip: typing.Optional[IElasticIp] = None,
    enable_source_dest_check: typing.Optional[builtins.bool] = None,
    interface_type: typing.Optional[InterfaceType] = None,
    ipv4: typing.Optional[AddressingV4] = None,
    ipv6: typing.Optional[AddressingV6] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__150cf8e22f1e7d05a47117e8f77da25561199d5daa7118eb196893fa55cfd796(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    header_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40fccea94b7e684de60e1f55e353e1a03b85c56db9135f4d67a939d5448d4694(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c95f74423d937b8be51b1b147dac2d7c254b40cc4b250c45909e61f91bd46e8(
    *,
    header_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f92671cecad94d42b87c6acda72bcbcbade0768d3a7cf14c24da4ac77dc8f82a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    network_interface: INetworkInterface,
    associate_public_ip_address: typing.Optional[builtins.bool] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    cpu_credits: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
    detailed_monitoring: typing.Optional[builtins.bool] = None,
    disable_api_termination: typing.Optional[builtins.bool] = None,
    ebs_optimized: typing.Optional[builtins.bool] = None,
    hibernation_configured: typing.Optional[builtins.bool] = None,
    http_endpoint: typing.Optional[builtins.bool] = None,
    http_protocol_ipv6: typing.Optional[builtins.bool] = None,
    http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
    http_tokens: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateHttpTokens] = None,
    instance_initiated_shutdown_behavior: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior] = None,
    instance_metadata_tags: typing.Optional[builtins.bool] = None,
    instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    launch_template_name: typing.Optional[builtins.str] = None,
    machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    nitro_enclave_enabled: typing.Optional[builtins.bool] = None,
    require_imdsv2: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    spot_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateSpotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
    version_description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fad5ad29510611b1ba296adad47fb6ec9c8138487f35967841a16b49dc03e726(
    security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba33fd6777c800d1923d7cc2b7309329ddda3c297188eea52d9c0fed6e4499d6(
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
    init_options: typing.Optional[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    launch_template: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate] = None,
    machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    max_healthy_percentage: typing.Optional[jsii.Number] = None,
    min_healthy_percentage: typing.Optional[jsii.Number] = None,
    mixed_instances_policy: typing.Optional[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.MixedInstancesPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    require_imdsv2: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    associate_public_ip_address: typing.Optional[builtins.bool] = None,
    auto_scaling_group_name: typing.Optional[builtins.str] = None,
    az_capacity_distribution_strategy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.CapacityDistributionStrategy] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    capacity_rebalance: typing.Optional[builtins.bool] = None,
    cooldown: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    default_instance_warmup: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    group_metrics: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.GroupMetrics]] = None,
    health_check: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthCheck] = None,
    ignore_unmodified_size_properties: typing.Optional[builtins.bool] = None,
    instance_monitoring: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Monitoring] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    max_capacity: typing.Optional[jsii.Number] = None,
    max_instance_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    min_capacity: typing.Optional[jsii.Number] = None,
    new_instances_protected_from_scale_in: typing.Optional[builtins.bool] = None,
    notifications: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.NotificationConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    signals: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Signals] = None,
    spot_price: typing.Optional[builtins.str] = None,
    ssm_session_permissions: typing.Optional[builtins.bool] = None,
    termination_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.TerminationPolicy]] = None,
    termination_policy_custom_lambda_function_arn: typing.Optional[builtins.str] = None,
    update_policy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.UpdatePolicy] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3bd5bd8420370bd8e386843b6b8d74e4ceb6ba66a5f5570c7ea46da5ad3f17f(
    *,
    associate_public_ip_address: typing.Optional[builtins.bool] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    cpu_credits: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
    detailed_monitoring: typing.Optional[builtins.bool] = None,
    disable_api_termination: typing.Optional[builtins.bool] = None,
    ebs_optimized: typing.Optional[builtins.bool] = None,
    hibernation_configured: typing.Optional[builtins.bool] = None,
    http_endpoint: typing.Optional[builtins.bool] = None,
    http_protocol_ipv6: typing.Optional[builtins.bool] = None,
    http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
    http_tokens: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateHttpTokens] = None,
    instance_initiated_shutdown_behavior: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior] = None,
    instance_metadata_tags: typing.Optional[builtins.bool] = None,
    instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    launch_template_name: typing.Optional[builtins.str] = None,
    machine_image: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    nitro_enclave_enabled: typing.Optional[builtins.bool] = None,
    require_imdsv2: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    spot_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.LaunchTemplateSpotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
    version_description: typing.Optional[builtins.str] = None,
    network_interface: INetworkInterface,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efa2d39cd1f01bf3758addd640ec7d1a822d75c3cc97424ddff8b739dca8d900(
    *,
    cross_zone_enabled: typing.Optional[builtins.bool] = None,
    deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupIpAddressType] = None,
    target_group_name: typing.Optional[builtins.str] = None,
    target_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    enable_anomaly_mitigation: typing.Optional[builtins.bool] = None,
    load_balancing_algorithm_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType] = None,
    port: typing.Optional[jsii.Number] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    slow_start: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    stickiness_cookie_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    stickiness_cookie_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]] = None,
    hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56342186b82314e198297a3e5364d68b3f8d14f18d4e2c17b5f18a47bffc93d3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
    require_known_hostname: typing.Optional[builtins.bool] = None,
    require_secret_header: typing.Optional[builtins.bool] = None,
    secret_header_name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7e0fb1b7097e928299c71e17989f2f1e1385330c18446d1a211d9b57fa16cc8(
    id: builtins.str,
    target: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget,
    *,
    hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
    priority: typing.Optional[jsii.Number] = None,
    enable_anomaly_mitigation: typing.Optional[builtins.bool] = None,
    load_balancing_algorithm_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType] = None,
    port: typing.Optional[jsii.Number] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    slow_start: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    stickiness_cookie_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    stickiness_cookie_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]] = None,
    cross_zone_enabled: typing.Optional[builtins.bool] = None,
    deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupIpAddressType] = None,
    target_group_name: typing.Optional[builtins.str] = None,
    target_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cf2c4b4f6d95905cc594637cb1f8523593a0d81a22f8200dc8eec640482dee1(
    *,
    certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
    require_known_hostname: typing.Optional[builtins.bool] = None,
    require_secret_header: typing.Optional[builtins.bool] = None,
    secret_header_name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10552300e8f97cdf7fb31b39d6f0ccd45aa560ac32634a146e2c4f13e6e0ecd2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7304c09f1b06d2d920c724dcf3ff3fceb9fc47af8746c6da6f888c8d57808849(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    delegation_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    subdomain: builtins.str,
    assume_role_region: typing.Optional[builtins.str] = None,
    parent_hosted_zone_id: typing.Optional[builtins.str] = None,
    parent_hosted_zone_name: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bc124d22b2b560d8ad6016cf5d0292be2f09e4a6659b58e2c166110dbd561c1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    parent_hosted_zone: _aws_cdk_aws_route53_ceddda9d.IPublicHostedZone,
    subdomain: builtins.str,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7866a53522992f55bdc325d1838ef58974b20f4f752692262b9d8a7a24aa6c4(
    policy: _aws_cdk_ceddda9d.RemovalPolicy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__329313caf887f63821d7884bee2092f3a6d442a6c1c96f75770081998a95873e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e82bf067154d978cd348f21fa71899f0687720ef3d7622a28287b58a275f1dd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    allocation_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__935c29310156a369b6e7213f9c82204a5cb0f35b37e585a9b48489f94e73980c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__610789115b0fd3b9297114da0749e7767d3eeff76e4daa1ede9a061ac66887d0(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3fd35c400f55d4fdfc3d9c58d10af525a284162188c631752bc5a18bccb9d30(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68321a0ac14d003a13037e7f7cd1855d87f43d63ce3a00bfc39b8bfa7b0c2e76(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
) -> None:
    """Type checking stubs"""
    pass
