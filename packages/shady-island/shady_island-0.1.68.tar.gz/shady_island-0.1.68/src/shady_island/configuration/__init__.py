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

import aws_cdk.aws_autoscaling as _aws_cdk_aws_autoscaling_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_efs as _aws_cdk_aws_efs_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
from ..networking import Address as _Address_50f6ffbb


@jsii.data_type(
    jsii_type="shady-island.configuration.AddDirectoryOptions",
    jsii_struct_bases=[],
    name_mapping={"group": "group", "mode": "mode", "owner": "owner"},
)
class AddDirectoryOptions:
    def __init__(
        self,
        *,
        group: typing.Optional[builtins.str] = None,
        mode: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Options for the ``ShellCommands.addDirectory`` method.

        :param group: The group name or numeric group ID to assign as the directory group.
        :param mode: The file mode, e.g. 2755, 0400.
        :param owner: The username or numeric user ID to assign as the directory owner.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0994962f0188c33e863c7c3d2a2d000cbf1c469ca2de6b605f8250f4a7331f5)
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if group is not None:
            self._values["group"] = group
        if mode is not None:
            self._values["mode"] = mode
        if owner is not None:
            self._values["owner"] = owner

    @builtins.property
    def group(self) -> typing.Optional[builtins.str]:
        '''The group name or numeric group ID to assign as the directory group.'''
        result = self._values.get("group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''The file mode, e.g. 2755, 0400.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''The username or numeric user ID to assign as the directory owner.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddDirectoryOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="shady-island.configuration.IFirewallRules")
class IFirewallRules(typing_extensions.Protocol):
    '''Used to configure on-instance firewall rules (e.g. iptables, firewalld).'''

    @jsii.member(jsii_name="buildCommands")
    def build_commands(self) -> typing.List[builtins.str]:
        '''Retrieves the shell commands used to configure the instance firewall.

        :return: An array of POSIX shell or PowerShell commands
        '''
        ...

    @jsii.member(jsii_name="inbound")
    def inbound(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
        address: _Address_50f6ffbb,
    ) -> "IFirewallRules":
        '''Declare an inbound rule.

        Only the following protocols are allowed: TCP, UDP, ICMP, and ICMPv6. The
        address can be a single address or a range of addresses in CIDR notation.

        :param port: - The ingress port.
        :param address: - The source address.

        :return: provides a fluent interface
        '''
        ...

    @jsii.member(jsii_name="inboundFromAnyIpv4")
    def inbound_from_any_ipv4(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
    ) -> "IFirewallRules":
        '''Declare an inbound rule that covers all IPv4 addresses.

        Only the following protocols are allowed: TCP, UDP, ICMP, and ICMPv6.

        :param port: - The ingress port.

        :return: provides a fluent interface
        '''
        ...

    @jsii.member(jsii_name="inboundFromAnyIpv6")
    def inbound_from_any_ipv6(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
    ) -> "IFirewallRules":
        '''Declare an inbound rule that covers all IPv6 addresses.

        Only the following protocols are allowed: TCP, UDP, ICMP, and ICMPv6.

        :param port: - The ingress port.

        :return: provides a fluent interface
        '''
        ...

    @jsii.member(jsii_name="outbound")
    def outbound(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
        address: _Address_50f6ffbb,
    ) -> "IFirewallRules":
        '''Declare an outbound rule.

        Only the following protocols are allowed: TCP, UDP, ICMP, and ICMPv6. The
        address can be a single address or a range of addresses in CIDR notation.

        :param port: - The egress port.
        :param address: - The target address.

        :return: provides a fluent interface
        '''
        ...

    @jsii.member(jsii_name="outboundToAnyIpv4")
    def outbound_to_any_ipv4(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
    ) -> "IFirewallRules":
        '''Declare an outbound rule that covers all IPv4 addresses.

        Only the following protocols are allowed: TCP, UDP, and ICMP.

        :param port: - The egress port.

        :return: provides a fluent interface
        '''
        ...

    @jsii.member(jsii_name="outboundToAnyIpv6")
    def outbound_to_any_ipv6(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
    ) -> "IFirewallRules":
        '''Declare an outbound rule that covers all IPv6 addresses.

        Only the following protocols are allowed: TCP, UDP, and ICMPv6.

        :param port: - The egress port.

        :return: provides a fluent interface
        '''
        ...


class _IFirewallRulesProxy:
    '''Used to configure on-instance firewall rules (e.g. iptables, firewalld).'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.configuration.IFirewallRules"

    @jsii.member(jsii_name="buildCommands")
    def build_commands(self) -> typing.List[builtins.str]:
        '''Retrieves the shell commands used to configure the instance firewall.

        :return: An array of POSIX shell or PowerShell commands
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "buildCommands", []))

    @jsii.member(jsii_name="inbound")
    def inbound(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
        address: _Address_50f6ffbb,
    ) -> IFirewallRules:
        '''Declare an inbound rule.

        Only the following protocols are allowed: TCP, UDP, ICMP, and ICMPv6. The
        address can be a single address or a range of addresses in CIDR notation.

        :param port: - The ingress port.
        :param address: - The source address.

        :return: provides a fluent interface
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91e3943c0b96c36c8ab8b6be2bdd62ff3d986bf3ec3203c15d1dc7fb25e84a96)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
        return typing.cast(IFirewallRules, jsii.invoke(self, "inbound", [port, address]))

    @jsii.member(jsii_name="inboundFromAnyIpv4")
    def inbound_from_any_ipv4(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
    ) -> IFirewallRules:
        '''Declare an inbound rule that covers all IPv4 addresses.

        Only the following protocols are allowed: TCP, UDP, ICMP, and ICMPv6.

        :param port: - The ingress port.

        :return: provides a fluent interface
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2057015371541955bb31cf65405c0b9713994c81916fd3bccd7b97fd848f0df5)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        return typing.cast(IFirewallRules, jsii.invoke(self, "inboundFromAnyIpv4", [port]))

    @jsii.member(jsii_name="inboundFromAnyIpv6")
    def inbound_from_any_ipv6(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
    ) -> IFirewallRules:
        '''Declare an inbound rule that covers all IPv6 addresses.

        Only the following protocols are allowed: TCP, UDP, ICMP, and ICMPv6.

        :param port: - The ingress port.

        :return: provides a fluent interface
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55ce83447589e470d2cc13d41477fa6f0c370daf4664197e40594ba4d9e414fe)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        return typing.cast(IFirewallRules, jsii.invoke(self, "inboundFromAnyIpv6", [port]))

    @jsii.member(jsii_name="outbound")
    def outbound(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
        address: _Address_50f6ffbb,
    ) -> IFirewallRules:
        '''Declare an outbound rule.

        Only the following protocols are allowed: TCP, UDP, ICMP, and ICMPv6. The
        address can be a single address or a range of addresses in CIDR notation.

        :param port: - The egress port.
        :param address: - The target address.

        :return: provides a fluent interface
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f650be2501ef56c44c4d3c237130830e8b9c55b6c07f078730f7f4e47a3a8f28)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
        return typing.cast(IFirewallRules, jsii.invoke(self, "outbound", [port, address]))

    @jsii.member(jsii_name="outboundToAnyIpv4")
    def outbound_to_any_ipv4(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
    ) -> IFirewallRules:
        '''Declare an outbound rule that covers all IPv4 addresses.

        Only the following protocols are allowed: TCP, UDP, and ICMP.

        :param port: - The egress port.

        :return: provides a fluent interface
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1aab68ba4f9404800d5febd451de0c3a210d3e0a63c97ae6e8e8298518aca58)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        return typing.cast(IFirewallRules, jsii.invoke(self, "outboundToAnyIpv4", [port]))

    @jsii.member(jsii_name="outboundToAnyIpv6")
    def outbound_to_any_ipv6(
        self,
        port: _aws_cdk_aws_ec2_ceddda9d.Port,
    ) -> IFirewallRules:
        '''Declare an outbound rule that covers all IPv6 addresses.

        Only the following protocols are allowed: TCP, UDP, and ICMPv6.

        :param port: - The egress port.

        :return: provides a fluent interface
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__735c38ccb3fe5ba250ab8fd6ae0f386b6643ba5363c5b9c0fd9b963b5100b8f4)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        return typing.cast(IFirewallRules, jsii.invoke(self, "outboundToAnyIpv6", [port]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFirewallRules).__jsii_proxy_class__ = lambda : _IFirewallRulesProxy


@jsii.interface(jsii_type="shady-island.configuration.IStarterAddOn")
class IStarterAddOn(typing_extensions.Protocol):
    '''A component involved in the startup process of an EC2 instance.'''

    @jsii.member(jsii_name="configure")
    def configure(self, starter: "Starter") -> None:
        '''Any configuration or customization of the virtual machine takes place here.

        :param starter: - The starter that can be configured.

        :return: The scripts to include in the user data
        '''
        ...


class _IStarterAddOnProxy:
    '''A component involved in the startup process of an EC2 instance.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.configuration.IStarterAddOn"

    @jsii.member(jsii_name="configure")
    def configure(self, starter: "Starter") -> None:
        '''Any configuration or customization of the virtual machine takes place here.

        :param starter: - The starter that can be configured.

        :return: The scripts to include in the user data
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3db290b103de206f865b1b4099758cbbe58afe23711deca88441265ae13a107f)
            check_type(argname="argument starter", value=starter, expected_type=type_hints["starter"])
        return typing.cast(None, jsii.invoke(self, "configure", [starter]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStarterAddOn).__jsii_proxy_class__ = lambda : _IStarterAddOnProxy


@jsii.data_type(
    jsii_type="shady-island.configuration.InstallAptPackagesOptions",
    jsii_struct_bases=[],
    name_mapping={"auto_remove": "autoRemove", "repositories": "repositories"},
)
class InstallAptPackagesOptions:
    def __init__(
        self,
        *,
        auto_remove: typing.Optional[builtins.bool] = None,
        repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Constructor properties for AptPackagesAddOn.

        :param auto_remove: Whether to run apt autoremove after installation finishes. Default: - true
        :param repositories: Additional Apt Repositories to enable using add-apt-repository.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0397b2bf916556bae3e2cfaf97a0aa01861e7c2202a16e01b3abc59abf517f97)
            check_type(argname="argument auto_remove", value=auto_remove, expected_type=type_hints["auto_remove"])
            check_type(argname="argument repositories", value=repositories, expected_type=type_hints["repositories"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_remove is not None:
            self._values["auto_remove"] = auto_remove
        if repositories is not None:
            self._values["repositories"] = repositories

    @builtins.property
    def auto_remove(self) -> typing.Optional[builtins.bool]:
        '''Whether to run apt autoremove after installation finishes.

        :default: - true
        '''
        result = self._values.get("auto_remove")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def repositories(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional Apt Repositories to enable using add-apt-repository.'''
        result = self._values.get("repositories")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstallAptPackagesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstanceFirewall(
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.configuration.InstanceFirewall",
):
    '''Produces the appropriate commands to configure an on-instance firewall.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="iptables")
    @builtins.classmethod
    def iptables(cls) -> IFirewallRules:
        '''Define an instance firewall using iptables/ip6tables.

        :return: An iptables-based on-instance firewall
        '''
        return typing.cast(IFirewallRules, jsii.sinvoke(cls, "iptables", []))


@jsii.implements(IStarterAddOn)
class InstanceFirewallAddOn(
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.configuration.InstanceFirewallAddOn",
):
    '''An add-on that configures an on-instance firewall.'''

    def __init__(
        self,
        rules: IFirewallRules,
        *,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''An add-on that configures an on-instance firewall.

        :param rules: - The instance firewall rules.
        :param priority: The priority for the script added by this add-on. Default: - 10
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f22f3bb2e2725b0986b7174b80a109c750ec2a5d373947a6ec8b9787ede528ee)
            check_type(argname="argument rules", value=rules, expected_type=type_hints["rules"])
        props = SinglePriorityProps(priority=priority)

        jsii.create(self.__class__, self, [rules, props])

    @jsii.member(jsii_name="configure")
    def configure(self, starter: "Starter") -> None:
        '''Any configuration or customization of the virtual machine takes place here.

        :param starter: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f44396976f8e149a087bd91b45dcecfdbc5f0402b627a74441e117c099a0b83)
            check_type(argname="argument starter", value=starter, expected_type=type_hints["starter"])
        return typing.cast(None, jsii.invoke(self, "configure", [starter]))


@jsii.data_type(
    jsii_type="shady-island.configuration.OutputFileOptions",
    jsii_struct_bases=[],
    name_mapping={"delimiter": "delimiter", "substitution": "substitution"},
)
class OutputFileOptions:
    def __init__(
        self,
        *,
        delimiter: typing.Optional[builtins.str] = None,
        substitution: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Options for the ``ShellCommands.outputFile`` method.

        :param delimiter: The bash heredoc delimiter. Default: - END_OF_FILE
        :param substitution: Use ``true`` to enable variable and command substitution inside the heredoc. Default: - disabled
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20657a054da386482746d6fa830e9dd3576a6d27d93d9c78a3c3ecae5282748d)
            check_type(argname="argument delimiter", value=delimiter, expected_type=type_hints["delimiter"])
            check_type(argname="argument substitution", value=substitution, expected_type=type_hints["substitution"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if delimiter is not None:
            self._values["delimiter"] = delimiter
        if substitution is not None:
            self._values["substitution"] = substitution

    @builtins.property
    def delimiter(self) -> typing.Optional[builtins.str]:
        '''The bash heredoc delimiter.

        :default: - END_OF_FILE
        '''
        result = self._values.get("delimiter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def substitution(self) -> typing.Optional[builtins.bool]:
        '''Use ``true`` to enable variable and command substitution inside the heredoc.

        :default: - disabled
        '''
        result = self._values.get("substitution")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OutputFileOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ShellCommands(
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.configuration.ShellCommands",
):
    '''A utility class that provides POSIX shell commands for User Data scripts.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="addDirectory")
    @builtins.classmethod
    def add_directory(
        cls,
        name: builtins.str,
        *,
        group: typing.Optional[builtins.str] = None,
        mode: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> typing.List[builtins.str]:
        '''Uses either ``mkdir`` or ``install`` to create a directory.

        :param name: - The name of the directory to create.
        :param group: The group name or numeric group ID to assign as the directory group.
        :param mode: The file mode, e.g. 2755, 0400.
        :param owner: The username or numeric user ID to assign as the directory owner.

        :return: The shell commands.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19e1521624de9cd4f04bc5aa6550677f7d918b1ba4a09f54c46aaecd55b902b7)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        options = AddDirectoryOptions(group=group, mode=mode, owner=owner)

        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "addDirectory", [name, options]))

    @jsii.member(jsii_name="changeOwnership")
    @builtins.classmethod
    def change_ownership(
        cls,
        filename: builtins.str,
        uid: typing.Optional[builtins.str] = None,
        gid: typing.Optional[builtins.str] = None,
    ) -> typing.List[builtins.str]:
        '''Gets a command to change the ownership and/or group membership of a file.

        If both ``uid`` and ``gid`` are provided, this method returns a single
        ``chown`` command to set both values. If just ``uid`` is provided, this method
        returns a single ``chown`` command that sets the owner. If just ``gid`` is
        provided, this method returns a single ``chgrp`` command. If neither are
        provided, this method returns an empty array.

        :param filename: - The local filesystem path to the file or directory.
        :param uid: - Optional. The owner username or uid.
        :param gid: - Optional. The group name or gid.

        :return: The shell commands.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16814cfa23b6c9675dbf36b44def93bb361e99ae2f96a53635ec8bbbd5636bd0)
            check_type(argname="argument filename", value=filename, expected_type=type_hints["filename"])
            check_type(argname="argument uid", value=uid, expected_type=type_hints["uid"])
            check_type(argname="argument gid", value=gid, expected_type=type_hints["gid"])
        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "changeOwnership", [filename, uid, gid]))

    @jsii.member(jsii_name="disableUnattendedUpgrades")
    @builtins.classmethod
    def disable_unattended_upgrades(cls) -> typing.List[builtins.str]:
        '''Gets a command to disable unattended package upgrades on Debian/Ubuntu.

        :return: The shell commands.
        '''
        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "disableUnattendedUpgrades", []))

    @jsii.member(jsii_name="downloadSecret")
    @builtins.classmethod
    def download_secret(
        cls,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        destination: builtins.str,
    ) -> typing.List[builtins.str]:
        '''Gets the command to download a Secrets Manager secret to the filesystem.

        Be sure to grant your autoscaling group or EC2 instance read access.

        :param secret: - The secret to download.
        :param destination: - The local filesystem path where the secret is stored.

        :return: The shell commands.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__326012a0bf58f709bc56dc6438ccb9490964767013b0d3c93d9cb4cc375eb27f)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "downloadSecret", [secret, destination]))

    @jsii.member(jsii_name="installAptPackages")
    @builtins.classmethod
    def install_apt_packages(
        cls,
        packages: typing.Sequence[builtins.str],
        *,
        auto_remove: typing.Optional[builtins.bool] = None,
        repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> typing.List[builtins.str]:
        '''Gets commands to setup APT and install packages.

        :param packages: - The packages to install.
        :param auto_remove: Whether to run apt autoremove after installation finishes. Default: - true
        :param repositories: Additional Apt Repositories to enable using add-apt-repository.

        :return: The shell commands.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d58dadb367e60393a027c3b603593b8ac9a63445aa85e1fa233bf4d96d99bb6)
            check_type(argname="argument packages", value=packages, expected_type=type_hints["packages"])
        options = InstallAptPackagesOptions(
            auto_remove=auto_remove, repositories=repositories
        )

        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "installAptPackages", [packages, options]))

    @jsii.member(jsii_name="mountElasticFileSystem")
    @builtins.classmethod
    def mount_elastic_file_system(
        cls,
        filesystem: _aws_cdk_aws_efs_ceddda9d.IFileSystem,
        destination: builtins.str,
    ) -> typing.List[builtins.str]:
        '''Gets the command to mount an EFS filesystem to a destination path.

        Be sure to grant your autoscaling group or EC2 instance network access.

        :param filesystem: - The EFS filesystem.
        :param destination: - The local filesystem path for the mount point.

        :return: The shell commands.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__587d6ed009cf11ba74cd134ee0e93a285b966d1809d7fa317ad1d96e93091a03)
            check_type(argname="argument filesystem", value=filesystem, expected_type=type_hints["filesystem"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "mountElasticFileSystem", [filesystem, destination]))

    @jsii.member(jsii_name="outputFile")
    @builtins.classmethod
    def output_file(
        cls,
        contents: builtins.str,
        destination: builtins.str,
        *,
        delimiter: typing.Optional[builtins.str] = None,
        substitution: typing.Optional[builtins.bool] = None,
    ) -> typing.List[builtins.str]:
        '''Writes the literal contents of a string to a destination file.

        :param contents: - The file contents.
        :param destination: - The filename to output.
        :param delimiter: The bash heredoc delimiter. Default: - END_OF_FILE
        :param substitution: Use ``true`` to enable variable and command substitution inside the heredoc. Default: - disabled

        :return: The shell commands.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__223cbfb5bcff2bb626b3dd2641d391ed7ca2e762e770d1499154a22b3ea5ccca)
            check_type(argname="argument contents", value=contents, expected_type=type_hints["contents"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        options = OutputFileOptions(delimiter=delimiter, substitution=substitution)

        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "outputFile", [contents, destination, options]))

    @jsii.member(jsii_name="syncFromBucket")
    @builtins.classmethod
    def sync_from_bucket(
        cls,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        destinations: typing.Mapping[builtins.str, builtins.str],
    ) -> typing.List[builtins.str]:
        '''Gets commands to synchronize objects from an S3 bucket to the filesystem.

        e.g. ``syncFromBucket(bucket, {"nginx-config": "/etc/nginx"})``.

        Be sure to grant your autoscaling group or EC2 instance read access.

        :param bucket: - The source bucket.
        :param destinations: - Record with S3 object keys to filesystem path values.

        :return: The shell commands.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__374e266416cc5b0f352fd2dbd94b207a658f7585956ae915ae7dc9eaa04eca4d)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument destinations", value=destinations, expected_type=type_hints["destinations"])
        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "syncFromBucket", [bucket, destinations]))


@jsii.data_type(
    jsii_type="shady-island.configuration.SinglePriorityProps",
    jsii_struct_bases=[],
    name_mapping={"priority": "priority"},
)
class SinglePriorityProps:
    def __init__(self, *, priority: typing.Optional[jsii.Number] = None) -> None:
        '''Properties for starter add-ons that add a single script.

        :param priority: The priority for the script added by this add-on. Default: - 10
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1140c88c4ab6e4bcfd5af654adc94e5ca130af9ab446ea76b209c42bc6780e1)
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''The priority for the script added by this add-on.

        :default: - 10
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SinglePriorityProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_ec2_ceddda9d.IConnectable, _aws_cdk_aws_iam_ceddda9d.IGrantable)
class Starter(metaclass=jsii.JSIIMeta, jsii_type="shady-island.configuration.Starter"):
    '''Orchestrates the startup process of EC2 instances.

    A ``Starter`` is a registry for add-ons. Each add-on can add permissions to the
    role, network rules to the security group, or scripts to the user data.

    Scripts are prioritized, so add-ons can be registered out of order but their
    scripts will appear in the user data in order of priority.
    '''

    @jsii.member(jsii_name="forAutoScalingGroup")
    @builtins.classmethod
    def for_auto_scaling_group(
        cls,
        group: _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup,
    ) -> "Starter":
        '''Create a Starter for an auto-scaling group.

        :param group: - The auto-scaling group.

        :return: a new Starter
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca8b1ff19dfaa4e0b311333a3fdf18ced363bbe98e1fbf7d393985d123b5e8cc)
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
        return typing.cast("Starter", jsii.sinvoke(cls, "forAutoScalingGroup", [group]))

    @jsii.member(jsii_name="forInstance")
    @builtins.classmethod
    def for_instance(cls, instance: _aws_cdk_aws_ec2_ceddda9d.Instance) -> "Starter":
        '''Create a Starter for a single EC2 instance3.

        :param instance: - The instance.

        :return: a new Starter
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fcb204b5111babecf6663a8e2ed3879545400b6f2fc5839dc0c9416f37936fe)
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
        return typing.cast("Starter", jsii.sinvoke(cls, "forInstance", [instance]))

    @jsii.member(jsii_name="forLaunchTemplate")
    @builtins.classmethod
    def for_launch_template(
        cls,
        template: _aws_cdk_aws_ec2_ceddda9d.LaunchTemplate,
    ) -> "Starter":
        '''Create a Starter for a Launch Template.

        The launch template *must* have a defined user data property, or this
        method will throw an error.

        :param template: - The launch template.

        :return: a new Starter

        :throws: Error if the Launch Template user data is undefined
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d23e43ce8a06f5a11f750048d6eede007957b3a3f359d33c89d1b5a87432af8)
            check_type(argname="argument template", value=template, expected_type=type_hints["template"])
        return typing.cast("Starter", jsii.sinvoke(cls, "forLaunchTemplate", [template]))

    @jsii.member(jsii_name="addScript")
    def add_script(self, priority: jsii.Number, *commands: builtins.str) -> "Starter":
        '''Add one or more commands to the user data at a specific priority.

        :param priority: - The priority of these lines (lower executes earlier).
        :param commands: - The lines to add.

        :return: provides a fluent interface
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eac0ce1795dce4e2ea0385ab7ee4a347b890e5310a1c24f9288b95d8cac544a7)
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument commands", value=commands, expected_type=typing.Tuple[type_hints["commands"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("Starter", jsii.invoke(self, "addScript", [priority, *commands]))

    @jsii.member(jsii_name="withAddOns")
    def with_add_ons(self, *addons: IStarterAddOn) -> "Starter":
        '''Register add-ons with this Starter.

        :param addons: - The add-ons to register.

        :return: provides a fluent interface
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c34da54ac51d9ca858bc0387102584854d16cc75d551d938fde90327179da23)
            check_type(argname="argument addons", value=addons, expected_type=typing.Tuple[type_hints["addons"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("Starter", jsii.invoke(self, "withAddOns", [*addons]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''The network connections associated with this resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''The principal to grant permissions to.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="orderedLines")
    def ordered_lines(self) -> typing.List[builtins.str]:
        '''All lines of the startup script in priority order.'''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "orderedLines"))


@jsii.implements(IStarterAddOn)
class UpdateRoute53AddOn(
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.configuration.UpdateRoute53AddOn",
):
    '''An add-on that updates Route 53 with instance public-facing IP addresses.

    This add-on also configures the necessary IAM policy.
    '''

    def __init__(
        self,
        zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        subdomain: builtins.str,
        *,
        ipv4: typing.Optional[builtins.bool] = None,
        ipv6: typing.Optional[builtins.bool] = None,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''An add-on that updates Route 53 with instance public-facing IP addresses.

        This add-on also configures the necessary IAM policy.

        :param zone: - The Route 53 hosted zone.
        :param subdomain: - The subdomain of the DNS record.
        :param ipv4: Whether to create/update an "A" record for the instance. Default: - true
        :param ipv6: Whether to create/update an "AAAA" record for the instance. Default: - false
        :param priority: The priority for the script added by this add-on. Default: - 10
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c8ae078b93dfc8e0a3e0f8002b4e1e1605ac20a5f79bbbcc7fa3dc6731761ce)
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument subdomain", value=subdomain, expected_type=type_hints["subdomain"])
        props = UpdateRoute53AddOnProps(ipv4=ipv4, ipv6=ipv6, priority=priority)

        jsii.create(self.__class__, self, [zone, subdomain, props])

    @jsii.member(jsii_name="configure")
    def configure(self, starter: Starter) -> None:
        '''Any configuration or customization of the virtual machine takes place here.

        :param starter: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b9f0bc8ead5919bb9d950bc0327f3bd2f62a40860d28fb4e7b5e3e85b5bed2a)
            check_type(argname="argument starter", value=starter, expected_type=type_hints["starter"])
        return typing.cast(None, jsii.invoke(self, "configure", [starter]))


@jsii.data_type(
    jsii_type="shady-island.configuration.UpdateRoute53AddOnProps",
    jsii_struct_bases=[SinglePriorityProps],
    name_mapping={"priority": "priority", "ipv4": "ipv4", "ipv6": "ipv6"},
)
class UpdateRoute53AddOnProps(SinglePriorityProps):
    def __init__(
        self,
        *,
        priority: typing.Optional[jsii.Number] = None,
        ipv4: typing.Optional[builtins.bool] = None,
        ipv6: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructor properties for UpdateRoute53AddOn.

        :param priority: The priority for the script added by this add-on. Default: - 10
        :param ipv4: Whether to create/update an "A" record for the instance. Default: - true
        :param ipv6: Whether to create/update an "AAAA" record for the instance. Default: - false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2442b773414e80748752da9466eb7ab315f8bd53031ae593de3540eb58cbf4e6)
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument ipv4", value=ipv4, expected_type=type_hints["ipv4"])
            check_type(argname="argument ipv6", value=ipv6, expected_type=type_hints["ipv6"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if priority is not None:
            self._values["priority"] = priority
        if ipv4 is not None:
            self._values["ipv4"] = ipv4
        if ipv6 is not None:
            self._values["ipv6"] = ipv6

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''The priority for the script added by this add-on.

        :default: - 10
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ipv4(self) -> typing.Optional[builtins.bool]:
        '''Whether to create/update an "A" record for the instance.

        :default: - true
        '''
        result = self._values.get("ipv4")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ipv6(self) -> typing.Optional[builtins.bool]:
        '''Whether to create/update an "AAAA" record for the instance.

        :default: - false
        '''
        result = self._values.get("ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UpdateRoute53AddOnProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IStarterAddOn)
class BucketSyncAddOn(
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.configuration.BucketSyncAddOn",
):
    '''An add-on that synchronizes files from S3 to directories on the instance.

    This add-on also grants read access to the bucket.
    '''

    def __init__(
        self,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        destinations: typing.Mapping[builtins.str, builtins.str],
        *,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''An add-on that synchronizes files from S3 to directories on the instance.

        This add-on also grants read access to the bucket.

        :param bucket: - The S3 bucket from which files can be downloaded.
        :param destinations: - An object where keys are S3 object key prefixes and values are filesystem directories.
        :param priority: The priority for the script added by this add-on. Default: - 10
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe1ea833a8db5d708589dca1758f5f31a7e3bfefddbb537028a52e18535e8696)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument destinations", value=destinations, expected_type=type_hints["destinations"])
        props = SinglePriorityProps(priority=priority)

        jsii.create(self.__class__, self, [bucket, destinations, props])

    @jsii.member(jsii_name="configure")
    def configure(self, starter: Starter) -> None:
        '''Any configuration or customization of the virtual machine takes place here.

        :param starter: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a4a2b1d3fde17504d591c8176936d7cc0d9dfd8f59e25bc13ea004b57ab7103)
            check_type(argname="argument starter", value=starter, expected_type=type_hints["starter"])
        return typing.cast(None, jsii.invoke(self, "configure", [starter]))


@jsii.implements(IStarterAddOn)
class ElasticFileSystemAddOn(
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.configuration.ElasticFileSystemAddOn",
):
    '''An add-on that configures a mount point for an EFS filesystem.

    This add-on will produce a startup script to:

    - Create the mount directory
    - Mount the NFS filesystem to the mount point
    - Optionally change the mode or ownership of the mount point

    This visitor also configures the Security Groups on both ends.
    '''

    def __init__(
        self,
        filesystem: _aws_cdk_aws_efs_ceddda9d.IFileSystem,
        destination: builtins.str,
        *,
        chgrp: typing.Optional[builtins.str] = None,
        chmod: typing.Optional[jsii.Number] = None,
        chown: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''An add-on that configures a mount point for an EFS filesystem.

        This add-on will produce a startup script to:

        - Create the mount directory
        - Mount the NFS filesystem to the mount point
        - Optionally change the mode or ownership of the mount point

        This add-on also configures the Security Groups on both ends.

        :param filesystem: - The elastic filesystem to mount.
        :param destination: - The directory to use as the mount point.
        :param chgrp: The intended Linux group name or ID of the group of the mounted directory. Default: - No chrp command is executed
        :param chmod: The intended file mode of the mounted directory. Default: - No chmod command is executed
        :param chown: The intended Linux username or ID of the owner of the mounted directory. Default: - No chown command is executed
        :param priority: The priority for the script added by this add-on. Default: - 10
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__950573ef3414b641c4c65e8de78314f118b632bcf66a7a9aaeb278e52df4c460)
            check_type(argname="argument filesystem", value=filesystem, expected_type=type_hints["filesystem"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        props = ElasticFileSystemAddOnProps(
            chgrp=chgrp, chmod=chmod, chown=chown, priority=priority
        )

        jsii.create(self.__class__, self, [filesystem, destination, props])

    @jsii.member(jsii_name="configure")
    def configure(self, starter: Starter) -> None:
        '''Any configuration or customization of the virtual machine takes place here.

        :param starter: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__276bbe28672c139e7ff2727019370f9354683a710cad3cf9097fc8c92d9d9494)
            check_type(argname="argument starter", value=starter, expected_type=type_hints["starter"])
        return typing.cast(None, jsii.invoke(self, "configure", [starter]))


@jsii.data_type(
    jsii_type="shady-island.configuration.ElasticFileSystemAddOnProps",
    jsii_struct_bases=[SinglePriorityProps],
    name_mapping={
        "priority": "priority",
        "chgrp": "chgrp",
        "chmod": "chmod",
        "chown": "chown",
    },
)
class ElasticFileSystemAddOnProps(SinglePriorityProps):
    def __init__(
        self,
        *,
        priority: typing.Optional[jsii.Number] = None,
        chgrp: typing.Optional[builtins.str] = None,
        chmod: typing.Optional[jsii.Number] = None,
        chown: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructor properties for ElasticFileSystemAddOn.

        :param priority: The priority for the script added by this add-on. Default: - 10
        :param chgrp: The intended Linux group name or ID of the group of the mounted directory. Default: - No chrp command is executed
        :param chmod: The intended file mode of the mounted directory. Default: - No chmod command is executed
        :param chown: The intended Linux username or ID of the owner of the mounted directory. Default: - No chown command is executed
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__350dd31036678df69f56ca2ddd7d6fd3b7b6c55b8a3a8bc659f26b57c94958a0)
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument chgrp", value=chgrp, expected_type=type_hints["chgrp"])
            check_type(argname="argument chmod", value=chmod, expected_type=type_hints["chmod"])
            check_type(argname="argument chown", value=chown, expected_type=type_hints["chown"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if priority is not None:
            self._values["priority"] = priority
        if chgrp is not None:
            self._values["chgrp"] = chgrp
        if chmod is not None:
            self._values["chmod"] = chmod
        if chown is not None:
            self._values["chown"] = chown

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''The priority for the script added by this add-on.

        :default: - 10
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def chgrp(self) -> typing.Optional[builtins.str]:
        '''The intended Linux group name or ID of the group of the mounted directory.

        :default: - No chrp command is executed
        '''
        result = self._values.get("chgrp")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def chmod(self) -> typing.Optional[jsii.Number]:
        '''The intended file mode of the mounted directory.

        :default: - No chmod command is executed
        '''
        result = self._values.get("chmod")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def chown(self) -> typing.Optional[builtins.str]:
        '''The intended Linux username or ID of the owner of the mounted directory.

        :default: - No chown command is executed
        '''
        result = self._values.get("chown")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticFileSystemAddOnProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AddDirectoryOptions",
    "BucketSyncAddOn",
    "ElasticFileSystemAddOn",
    "ElasticFileSystemAddOnProps",
    "IFirewallRules",
    "IStarterAddOn",
    "InstallAptPackagesOptions",
    "InstanceFirewall",
    "InstanceFirewallAddOn",
    "OutputFileOptions",
    "ShellCommands",
    "SinglePriorityProps",
    "Starter",
    "UpdateRoute53AddOn",
    "UpdateRoute53AddOnProps",
]

publication.publish()

def _typecheckingstub__b0994962f0188c33e863c7c3d2a2d000cbf1c469ca2de6b605f8250f4a7331f5(
    *,
    group: typing.Optional[builtins.str] = None,
    mode: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91e3943c0b96c36c8ab8b6be2bdd62ff3d986bf3ec3203c15d1dc7fb25e84a96(
    port: _aws_cdk_aws_ec2_ceddda9d.Port,
    address: _Address_50f6ffbb,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2057015371541955bb31cf65405c0b9713994c81916fd3bccd7b97fd848f0df5(
    port: _aws_cdk_aws_ec2_ceddda9d.Port,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55ce83447589e470d2cc13d41477fa6f0c370daf4664197e40594ba4d9e414fe(
    port: _aws_cdk_aws_ec2_ceddda9d.Port,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f650be2501ef56c44c4d3c237130830e8b9c55b6c07f078730f7f4e47a3a8f28(
    port: _aws_cdk_aws_ec2_ceddda9d.Port,
    address: _Address_50f6ffbb,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1aab68ba4f9404800d5febd451de0c3a210d3e0a63c97ae6e8e8298518aca58(
    port: _aws_cdk_aws_ec2_ceddda9d.Port,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__735c38ccb3fe5ba250ab8fd6ae0f386b6643ba5363c5b9c0fd9b963b5100b8f4(
    port: _aws_cdk_aws_ec2_ceddda9d.Port,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3db290b103de206f865b1b4099758cbbe58afe23711deca88441265ae13a107f(
    starter: Starter,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0397b2bf916556bae3e2cfaf97a0aa01861e7c2202a16e01b3abc59abf517f97(
    *,
    auto_remove: typing.Optional[builtins.bool] = None,
    repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f22f3bb2e2725b0986b7174b80a109c750ec2a5d373947a6ec8b9787ede528ee(
    rules: IFirewallRules,
    *,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f44396976f8e149a087bd91b45dcecfdbc5f0402b627a74441e117c099a0b83(
    starter: Starter,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20657a054da386482746d6fa830e9dd3576a6d27d93d9c78a3c3ecae5282748d(
    *,
    delimiter: typing.Optional[builtins.str] = None,
    substitution: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19e1521624de9cd4f04bc5aa6550677f7d918b1ba4a09f54c46aaecd55b902b7(
    name: builtins.str,
    *,
    group: typing.Optional[builtins.str] = None,
    mode: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16814cfa23b6c9675dbf36b44def93bb361e99ae2f96a53635ec8bbbd5636bd0(
    filename: builtins.str,
    uid: typing.Optional[builtins.str] = None,
    gid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__326012a0bf58f709bc56dc6438ccb9490964767013b0d3c93d9cb4cc375eb27f(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d58dadb367e60393a027c3b603593b8ac9a63445aa85e1fa233bf4d96d99bb6(
    packages: typing.Sequence[builtins.str],
    *,
    auto_remove: typing.Optional[builtins.bool] = None,
    repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__587d6ed009cf11ba74cd134ee0e93a285b966d1809d7fa317ad1d96e93091a03(
    filesystem: _aws_cdk_aws_efs_ceddda9d.IFileSystem,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__223cbfb5bcff2bb626b3dd2641d391ed7ca2e762e770d1499154a22b3ea5ccca(
    contents: builtins.str,
    destination: builtins.str,
    *,
    delimiter: typing.Optional[builtins.str] = None,
    substitution: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__374e266416cc5b0f352fd2dbd94b207a658f7585956ae915ae7dc9eaa04eca4d(
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    destinations: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1140c88c4ab6e4bcfd5af654adc94e5ca130af9ab446ea76b209c42bc6780e1(
    *,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca8b1ff19dfaa4e0b311333a3fdf18ced363bbe98e1fbf7d393985d123b5e8cc(
    group: _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fcb204b5111babecf6663a8e2ed3879545400b6f2fc5839dc0c9416f37936fe(
    instance: _aws_cdk_aws_ec2_ceddda9d.Instance,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d23e43ce8a06f5a11f750048d6eede007957b3a3f359d33c89d1b5a87432af8(
    template: _aws_cdk_aws_ec2_ceddda9d.LaunchTemplate,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eac0ce1795dce4e2ea0385ab7ee4a347b890e5310a1c24f9288b95d8cac544a7(
    priority: jsii.Number,
    *commands: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c34da54ac51d9ca858bc0387102584854d16cc75d551d938fde90327179da23(
    *addons: IStarterAddOn,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c8ae078b93dfc8e0a3e0f8002b4e1e1605ac20a5f79bbbcc7fa3dc6731761ce(
    zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    subdomain: builtins.str,
    *,
    ipv4: typing.Optional[builtins.bool] = None,
    ipv6: typing.Optional[builtins.bool] = None,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b9f0bc8ead5919bb9d950bc0327f3bd2f62a40860d28fb4e7b5e3e85b5bed2a(
    starter: Starter,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2442b773414e80748752da9466eb7ab315f8bd53031ae593de3540eb58cbf4e6(
    *,
    priority: typing.Optional[jsii.Number] = None,
    ipv4: typing.Optional[builtins.bool] = None,
    ipv6: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe1ea833a8db5d708589dca1758f5f31a7e3bfefddbb537028a52e18535e8696(
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    destinations: typing.Mapping[builtins.str, builtins.str],
    *,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a4a2b1d3fde17504d591c8176936d7cc0d9dfd8f59e25bc13ea004b57ab7103(
    starter: Starter,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__950573ef3414b641c4c65e8de78314f118b632bcf66a7a9aaeb278e52df4c460(
    filesystem: _aws_cdk_aws_efs_ceddda9d.IFileSystem,
    destination: builtins.str,
    *,
    chgrp: typing.Optional[builtins.str] = None,
    chmod: typing.Optional[jsii.Number] = None,
    chown: typing.Optional[builtins.str] = None,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__276bbe28672c139e7ff2727019370f9354683a710cad3cf9097fc8c92d9d9494(
    starter: Starter,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__350dd31036678df69f56ca2ddd7d6fd3b7b6c55b8a3a8bc659f26b57c94958a0(
    *,
    priority: typing.Optional[jsii.Number] = None,
    chgrp: typing.Optional[builtins.str] = None,
    chmod: typing.Optional[jsii.Number] = None,
    chown: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
