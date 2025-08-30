r'''
# `cloudflare_magic_transit_site_lan`

Refer to the Terraform Registry for docs: [`cloudflare_magic_transit_site_lan`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class MagicTransitSiteLan(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLan",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan cloudflare_magic_transit_site_lan}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        physport: jsii.Number,
        site_id: builtins.str,
        ha_link: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        nat: typing.Optional[typing.Union["MagicTransitSiteLanNat", typing.Dict[builtins.str, typing.Any]]] = None,
        routed_subnets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MagicTransitSiteLanRoutedSubnets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        static_addressing: typing.Optional[typing.Union["MagicTransitSiteLanStaticAddressing", typing.Dict[builtins.str, typing.Any]]] = None,
        vlan_tag: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan cloudflare_magic_transit_site_lan} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#account_id MagicTransitSiteLan#account_id}
        :param physport: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#physport MagicTransitSiteLan#physport}.
        :param site_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#site_id MagicTransitSiteLan#site_id}
        :param ha_link: mark true to use this LAN for HA probing. only works for site with HA turned on. only one LAN can be set as the ha_link. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#ha_link MagicTransitSiteLan#ha_link}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#name MagicTransitSiteLan#name}.
        :param nat: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#nat MagicTransitSiteLan#nat}.
        :param routed_subnets: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#routed_subnets MagicTransitSiteLan#routed_subnets}.
        :param static_addressing: If the site is not configured in high availability mode, this configuration is optional (if omitted, use DHCP). However, if in high availability mode, static_address is required along with secondary and virtual address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#static_addressing MagicTransitSiteLan#static_addressing}
        :param vlan_tag: VLAN ID. Use zero for untagged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#vlan_tag MagicTransitSiteLan#vlan_tag}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73c712ecc9b90ed1ecc43201f5fe9826c3ea151b664e6bdba5252f6aaf74a4b8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = MagicTransitSiteLanConfig(
            account_id=account_id,
            physport=physport,
            site_id=site_id,
            ha_link=ha_link,
            name=name,
            nat=nat,
            routed_subnets=routed_subnets,
            static_addressing=static_addressing,
            vlan_tag=vlan_tag,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a MagicTransitSiteLan resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MagicTransitSiteLan to import.
        :param import_from_id: The id of the existing MagicTransitSiteLan that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MagicTransitSiteLan to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1108fa794cd7cc1b90408821fbea67cea8646649296199390e6cce9d151b772)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putNat")
    def put_nat(self, *, static_prefix: typing.Optional[builtins.str] = None) -> None:
        '''
        :param static_prefix: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#static_prefix MagicTransitSiteLan#static_prefix}
        '''
        value = MagicTransitSiteLanNat(static_prefix=static_prefix)

        return typing.cast(None, jsii.invoke(self, "putNat", [value]))

    @jsii.member(jsii_name="putRoutedSubnets")
    def put_routed_subnets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MagicTransitSiteLanRoutedSubnets", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a22429c8ed0a0df172de3bed1cb769b91ccbf482cf5e2d40bc482cc40ccec823)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRoutedSubnets", [value]))

    @jsii.member(jsii_name="putStaticAddressing")
    def put_static_addressing(
        self,
        *,
        address: builtins.str,
        dhcp_relay: typing.Optional[typing.Union["MagicTransitSiteLanStaticAddressingDhcpRelay", typing.Dict[builtins.str, typing.Any]]] = None,
        dhcp_server: typing.Optional[typing.Union["MagicTransitSiteLanStaticAddressingDhcpServer", typing.Dict[builtins.str, typing.Any]]] = None,
        secondary_address: typing.Optional[builtins.str] = None,
        virtual_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#address MagicTransitSiteLan#address}
        :param dhcp_relay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_relay MagicTransitSiteLan#dhcp_relay}.
        :param dhcp_server: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_server MagicTransitSiteLan#dhcp_server}.
        :param secondary_address: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#secondary_address MagicTransitSiteLan#secondary_address}
        :param virtual_address: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#virtual_address MagicTransitSiteLan#virtual_address}
        '''
        value = MagicTransitSiteLanStaticAddressing(
            address=address,
            dhcp_relay=dhcp_relay,
            dhcp_server=dhcp_server,
            secondary_address=secondary_address,
            virtual_address=virtual_address,
        )

        return typing.cast(None, jsii.invoke(self, "putStaticAddressing", [value]))

    @jsii.member(jsii_name="resetHaLink")
    def reset_ha_link(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaLink", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNat")
    def reset_nat(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNat", []))

    @jsii.member(jsii_name="resetRoutedSubnets")
    def reset_routed_subnets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutedSubnets", []))

    @jsii.member(jsii_name="resetStaticAddressing")
    def reset_static_addressing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaticAddressing", []))

    @jsii.member(jsii_name="resetVlanTag")
    def reset_vlan_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVlanTag", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="nat")
    def nat(self) -> "MagicTransitSiteLanNatOutputReference":
        return typing.cast("MagicTransitSiteLanNatOutputReference", jsii.get(self, "nat"))

    @builtins.property
    @jsii.member(jsii_name="routedSubnets")
    def routed_subnets(self) -> "MagicTransitSiteLanRoutedSubnetsList":
        return typing.cast("MagicTransitSiteLanRoutedSubnetsList", jsii.get(self, "routedSubnets"))

    @builtins.property
    @jsii.member(jsii_name="staticAddressing")
    def static_addressing(self) -> "MagicTransitSiteLanStaticAddressingOutputReference":
        return typing.cast("MagicTransitSiteLanStaticAddressingOutputReference", jsii.get(self, "staticAddressing"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="haLinkInput")
    def ha_link_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "haLinkInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="natInput")
    def nat_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicTransitSiteLanNat"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicTransitSiteLanNat"]], jsii.get(self, "natInput"))

    @builtins.property
    @jsii.member(jsii_name="physportInput")
    def physport_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "physportInput"))

    @builtins.property
    @jsii.member(jsii_name="routedSubnetsInput")
    def routed_subnets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MagicTransitSiteLanRoutedSubnets"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MagicTransitSiteLanRoutedSubnets"]]], jsii.get(self, "routedSubnetsInput"))

    @builtins.property
    @jsii.member(jsii_name="siteIdInput")
    def site_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "siteIdInput"))

    @builtins.property
    @jsii.member(jsii_name="staticAddressingInput")
    def static_addressing_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicTransitSiteLanStaticAddressing"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicTransitSiteLanStaticAddressing"]], jsii.get(self, "staticAddressingInput"))

    @builtins.property
    @jsii.member(jsii_name="vlanTagInput")
    def vlan_tag_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vlanTagInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6e8f39e6ef1ccbde67141ae71d2ec4e3cb74414ff27043c0a1f85e323f35009)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haLink")
    def ha_link(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "haLink"))

    @ha_link.setter
    def ha_link(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91878d41a834e76fc34779f884c211907cb4d7e420b2151926097dee9a2f7e94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haLink", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63e88755ecbe1adf7641f6aff76fb154712b4b6494da73817839866ce5517547)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="physport")
    def physport(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "physport"))

    @physport.setter
    def physport(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce7dba194bdc2d663ef5060f42c0c005e9402bfd338e79d760db109660c0656b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "physport", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="siteId")
    def site_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "siteId"))

    @site_id.setter
    def site_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4c38bdcd6f49273741cbc32f40d73d2a63f4b278d06092b25815ad5f4e33f48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "siteId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vlanTag")
    def vlan_tag(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vlanTag"))

    @vlan_tag.setter
    def vlan_tag(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2536c86e8a1beb69269e350219321532384fdb48bb9d78c573ae30779dfc2952)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vlanTag", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_id": "accountId",
        "physport": "physport",
        "site_id": "siteId",
        "ha_link": "haLink",
        "name": "name",
        "nat": "nat",
        "routed_subnets": "routedSubnets",
        "static_addressing": "staticAddressing",
        "vlan_tag": "vlanTag",
    },
)
class MagicTransitSiteLanConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        account_id: builtins.str,
        physport: jsii.Number,
        site_id: builtins.str,
        ha_link: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        nat: typing.Optional[typing.Union["MagicTransitSiteLanNat", typing.Dict[builtins.str, typing.Any]]] = None,
        routed_subnets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MagicTransitSiteLanRoutedSubnets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        static_addressing: typing.Optional[typing.Union["MagicTransitSiteLanStaticAddressing", typing.Dict[builtins.str, typing.Any]]] = None,
        vlan_tag: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#account_id MagicTransitSiteLan#account_id}
        :param physport: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#physport MagicTransitSiteLan#physport}.
        :param site_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#site_id MagicTransitSiteLan#site_id}
        :param ha_link: mark true to use this LAN for HA probing. only works for site with HA turned on. only one LAN can be set as the ha_link. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#ha_link MagicTransitSiteLan#ha_link}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#name MagicTransitSiteLan#name}.
        :param nat: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#nat MagicTransitSiteLan#nat}.
        :param routed_subnets: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#routed_subnets MagicTransitSiteLan#routed_subnets}.
        :param static_addressing: If the site is not configured in high availability mode, this configuration is optional (if omitted, use DHCP). However, if in high availability mode, static_address is required along with secondary and virtual address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#static_addressing MagicTransitSiteLan#static_addressing}
        :param vlan_tag: VLAN ID. Use zero for untagged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#vlan_tag MagicTransitSiteLan#vlan_tag}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(nat, dict):
            nat = MagicTransitSiteLanNat(**nat)
        if isinstance(static_addressing, dict):
            static_addressing = MagicTransitSiteLanStaticAddressing(**static_addressing)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f2650b680c6c62a17865f013c11ccce9bbabdf80e552ad8fb51a3973082b59c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument physport", value=physport, expected_type=type_hints["physport"])
            check_type(argname="argument site_id", value=site_id, expected_type=type_hints["site_id"])
            check_type(argname="argument ha_link", value=ha_link, expected_type=type_hints["ha_link"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument nat", value=nat, expected_type=type_hints["nat"])
            check_type(argname="argument routed_subnets", value=routed_subnets, expected_type=type_hints["routed_subnets"])
            check_type(argname="argument static_addressing", value=static_addressing, expected_type=type_hints["static_addressing"])
            check_type(argname="argument vlan_tag", value=vlan_tag, expected_type=type_hints["vlan_tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "physport": physport,
            "site_id": site_id,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if ha_link is not None:
            self._values["ha_link"] = ha_link
        if name is not None:
            self._values["name"] = name
        if nat is not None:
            self._values["nat"] = nat
        if routed_subnets is not None:
            self._values["routed_subnets"] = routed_subnets
        if static_addressing is not None:
            self._values["static_addressing"] = static_addressing
        if vlan_tag is not None:
            self._values["vlan_tag"] = vlan_tag

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def account_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#account_id MagicTransitSiteLan#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def physport(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#physport MagicTransitSiteLan#physport}.'''
        result = self._values.get("physport")
        assert result is not None, "Required property 'physport' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def site_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#site_id MagicTransitSiteLan#site_id}
        '''
        result = self._values.get("site_id")
        assert result is not None, "Required property 'site_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ha_link(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''mark true to use this LAN for HA probing.

        only works for site with HA turned on. only one LAN can be set as the ha_link.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#ha_link MagicTransitSiteLan#ha_link}
        '''
        result = self._values.get("ha_link")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#name MagicTransitSiteLan#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nat(self) -> typing.Optional["MagicTransitSiteLanNat"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#nat MagicTransitSiteLan#nat}.'''
        result = self._values.get("nat")
        return typing.cast(typing.Optional["MagicTransitSiteLanNat"], result)

    @builtins.property
    def routed_subnets(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MagicTransitSiteLanRoutedSubnets"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#routed_subnets MagicTransitSiteLan#routed_subnets}.'''
        result = self._values.get("routed_subnets")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MagicTransitSiteLanRoutedSubnets"]]], result)

    @builtins.property
    def static_addressing(
        self,
    ) -> typing.Optional["MagicTransitSiteLanStaticAddressing"]:
        '''If the site is not configured in high availability mode, this configuration is optional (if omitted, use DHCP).

        However, if in high availability mode, static_address is required along with secondary and virtual address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#static_addressing MagicTransitSiteLan#static_addressing}
        '''
        result = self._values.get("static_addressing")
        return typing.cast(typing.Optional["MagicTransitSiteLanStaticAddressing"], result)

    @builtins.property
    def vlan_tag(self) -> typing.Optional[jsii.Number]:
        '''VLAN ID. Use zero for untagged.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#vlan_tag MagicTransitSiteLan#vlan_tag}
        '''
        result = self._values.get("vlan_tag")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteLanConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanNat",
    jsii_struct_bases=[],
    name_mapping={"static_prefix": "staticPrefix"},
)
class MagicTransitSiteLanNat:
    def __init__(self, *, static_prefix: typing.Optional[builtins.str] = None) -> None:
        '''
        :param static_prefix: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#static_prefix MagicTransitSiteLan#static_prefix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e68b90baf48371cbcd2acdafde1476d2f2e402946cdcbf9bddd5ea88213fcbb8)
            check_type(argname="argument static_prefix", value=static_prefix, expected_type=type_hints["static_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if static_prefix is not None:
            self._values["static_prefix"] = static_prefix

    @builtins.property
    def static_prefix(self) -> typing.Optional[builtins.str]:
        '''A valid CIDR notation representing an IP range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#static_prefix MagicTransitSiteLan#static_prefix}
        '''
        result = self._values.get("static_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteLanNat(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicTransitSiteLanNatOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanNatOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02b0beffb6f08f588295953be8ddcbd2877343cf850d81f12de36ffcbc69262b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetStaticPrefix")
    def reset_static_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaticPrefix", []))

    @builtins.property
    @jsii.member(jsii_name="staticPrefixInput")
    def static_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "staticPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="staticPrefix")
    def static_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "staticPrefix"))

    @static_prefix.setter
    def static_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__722bdabf971aa1bf4ab20c53c15ae8d944b7a3ee8f07bf42b3d1dcd25e7c88e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staticPrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanNat]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanNat]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanNat]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a64e72e3d7a48065eecbad33de503c365bb5b0457f001b979451cb5df06cc5d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanRoutedSubnets",
    jsii_struct_bases=[],
    name_mapping={"next_hop": "nextHop", "prefix": "prefix", "nat": "nat"},
)
class MagicTransitSiteLanRoutedSubnets:
    def __init__(
        self,
        *,
        next_hop: builtins.str,
        prefix: builtins.str,
        nat: typing.Optional[typing.Union["MagicTransitSiteLanRoutedSubnetsNat", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param next_hop: A valid IPv4 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#next_hop MagicTransitSiteLan#next_hop}
        :param prefix: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#prefix MagicTransitSiteLan#prefix}
        :param nat: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#nat MagicTransitSiteLan#nat}.
        '''
        if isinstance(nat, dict):
            nat = MagicTransitSiteLanRoutedSubnetsNat(**nat)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b678219da71d5fe426e1aa29f3ac8e85fd873def2c3dcc3e6e60e60c49f3e1ac)
            check_type(argname="argument next_hop", value=next_hop, expected_type=type_hints["next_hop"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument nat", value=nat, expected_type=type_hints["nat"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "next_hop": next_hop,
            "prefix": prefix,
        }
        if nat is not None:
            self._values["nat"] = nat

    @builtins.property
    def next_hop(self) -> builtins.str:
        '''A valid IPv4 address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#next_hop MagicTransitSiteLan#next_hop}
        '''
        result = self._values.get("next_hop")
        assert result is not None, "Required property 'next_hop' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> builtins.str:
        '''A valid CIDR notation representing an IP range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#prefix MagicTransitSiteLan#prefix}
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nat(self) -> typing.Optional["MagicTransitSiteLanRoutedSubnetsNat"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#nat MagicTransitSiteLan#nat}.'''
        result = self._values.get("nat")
        return typing.cast(typing.Optional["MagicTransitSiteLanRoutedSubnetsNat"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteLanRoutedSubnets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicTransitSiteLanRoutedSubnetsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanRoutedSubnetsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae6431b295d15187e0e34a428a76e880b3e888c4adb67251392d8a431691d6c8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MagicTransitSiteLanRoutedSubnetsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8172aada4a64efcdb675df4ff0f252e72412998d909f67d5c8e1d3adec928512)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MagicTransitSiteLanRoutedSubnetsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a82347c9b7636098f923f5fa6b991673efc57f3e231038a2f62d2e4f83a2db3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35e74521d9614dec34623a67f2b5851ded89b00d5c34060d5b12210facb6f746)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87bd7833d0ef86d144b3f79951568d152e592c9220b91b1dd40c15163fc9e8f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MagicTransitSiteLanRoutedSubnets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MagicTransitSiteLanRoutedSubnets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MagicTransitSiteLanRoutedSubnets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dce58480c60348672a9a9001235c516eed1cb2e630121192951c3af40ba4291)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanRoutedSubnetsNat",
    jsii_struct_bases=[],
    name_mapping={"static_prefix": "staticPrefix"},
)
class MagicTransitSiteLanRoutedSubnetsNat:
    def __init__(self, *, static_prefix: typing.Optional[builtins.str] = None) -> None:
        '''
        :param static_prefix: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#static_prefix MagicTransitSiteLan#static_prefix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4be237d28c87e160b0abbcc2c34adc87bb75bdb89f3e05803d0c613f7fea6c8)
            check_type(argname="argument static_prefix", value=static_prefix, expected_type=type_hints["static_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if static_prefix is not None:
            self._values["static_prefix"] = static_prefix

    @builtins.property
    def static_prefix(self) -> typing.Optional[builtins.str]:
        '''A valid CIDR notation representing an IP range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#static_prefix MagicTransitSiteLan#static_prefix}
        '''
        result = self._values.get("static_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteLanRoutedSubnetsNat(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicTransitSiteLanRoutedSubnetsNatOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanRoutedSubnetsNatOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a18800298500e1298b14e60d51f9f43256b9c132ab9dcaf147311e98102ef5d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetStaticPrefix")
    def reset_static_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaticPrefix", []))

    @builtins.property
    @jsii.member(jsii_name="staticPrefixInput")
    def static_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "staticPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="staticPrefix")
    def static_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "staticPrefix"))

    @static_prefix.setter
    def static_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfe902eef4a6f3b84c9ff7827fc77a154b4c40d591db0971d444762133f241cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staticPrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnetsNat]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnetsNat]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnetsNat]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d6d65fab4f6cefc85537bb1628ee75a0cd5fec63801e907714db0647323a638)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MagicTransitSiteLanRoutedSubnetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanRoutedSubnetsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f60783efdf6198f342f0521b2129b2462d097882c0097fe2c847470560bf5dc0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNat")
    def put_nat(self, *, static_prefix: typing.Optional[builtins.str] = None) -> None:
        '''
        :param static_prefix: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#static_prefix MagicTransitSiteLan#static_prefix}
        '''
        value = MagicTransitSiteLanRoutedSubnetsNat(static_prefix=static_prefix)

        return typing.cast(None, jsii.invoke(self, "putNat", [value]))

    @jsii.member(jsii_name="resetNat")
    def reset_nat(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNat", []))

    @builtins.property
    @jsii.member(jsii_name="nat")
    def nat(self) -> MagicTransitSiteLanRoutedSubnetsNatOutputReference:
        return typing.cast(MagicTransitSiteLanRoutedSubnetsNatOutputReference, jsii.get(self, "nat"))

    @builtins.property
    @jsii.member(jsii_name="natInput")
    def nat_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnetsNat]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnetsNat]], jsii.get(self, "natInput"))

    @builtins.property
    @jsii.member(jsii_name="nextHopInput")
    def next_hop_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nextHopInput"))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="nextHop")
    def next_hop(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nextHop"))

    @next_hop.setter
    def next_hop(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fe66b5c252c4cc3f8e110b4919f9cffd867d1c1318048bb02251fab1d20cc16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nextHop", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bef0851efd8a4d8c3c7f02d3b8c03700512f1c118b99412f36805cf347bf48ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__018f367e221ab3fe3fbf4b9bdeeae992f0ad0f1e4bf05e13715e110709d51f47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanStaticAddressing",
    jsii_struct_bases=[],
    name_mapping={
        "address": "address",
        "dhcp_relay": "dhcpRelay",
        "dhcp_server": "dhcpServer",
        "secondary_address": "secondaryAddress",
        "virtual_address": "virtualAddress",
    },
)
class MagicTransitSiteLanStaticAddressing:
    def __init__(
        self,
        *,
        address: builtins.str,
        dhcp_relay: typing.Optional[typing.Union["MagicTransitSiteLanStaticAddressingDhcpRelay", typing.Dict[builtins.str, typing.Any]]] = None,
        dhcp_server: typing.Optional[typing.Union["MagicTransitSiteLanStaticAddressingDhcpServer", typing.Dict[builtins.str, typing.Any]]] = None,
        secondary_address: typing.Optional[builtins.str] = None,
        virtual_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#address MagicTransitSiteLan#address}
        :param dhcp_relay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_relay MagicTransitSiteLan#dhcp_relay}.
        :param dhcp_server: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_server MagicTransitSiteLan#dhcp_server}.
        :param secondary_address: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#secondary_address MagicTransitSiteLan#secondary_address}
        :param virtual_address: A valid CIDR notation representing an IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#virtual_address MagicTransitSiteLan#virtual_address}
        '''
        if isinstance(dhcp_relay, dict):
            dhcp_relay = MagicTransitSiteLanStaticAddressingDhcpRelay(**dhcp_relay)
        if isinstance(dhcp_server, dict):
            dhcp_server = MagicTransitSiteLanStaticAddressingDhcpServer(**dhcp_server)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c826b0532d676b9d6f5e1b3fddfece6ff45b050cea9d2fde09f8ee829411f25a)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument dhcp_relay", value=dhcp_relay, expected_type=type_hints["dhcp_relay"])
            check_type(argname="argument dhcp_server", value=dhcp_server, expected_type=type_hints["dhcp_server"])
            check_type(argname="argument secondary_address", value=secondary_address, expected_type=type_hints["secondary_address"])
            check_type(argname="argument virtual_address", value=virtual_address, expected_type=type_hints["virtual_address"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
        }
        if dhcp_relay is not None:
            self._values["dhcp_relay"] = dhcp_relay
        if dhcp_server is not None:
            self._values["dhcp_server"] = dhcp_server
        if secondary_address is not None:
            self._values["secondary_address"] = secondary_address
        if virtual_address is not None:
            self._values["virtual_address"] = virtual_address

    @builtins.property
    def address(self) -> builtins.str:
        '''A valid CIDR notation representing an IP range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#address MagicTransitSiteLan#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dhcp_relay(
        self,
    ) -> typing.Optional["MagicTransitSiteLanStaticAddressingDhcpRelay"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_relay MagicTransitSiteLan#dhcp_relay}.'''
        result = self._values.get("dhcp_relay")
        return typing.cast(typing.Optional["MagicTransitSiteLanStaticAddressingDhcpRelay"], result)

    @builtins.property
    def dhcp_server(
        self,
    ) -> typing.Optional["MagicTransitSiteLanStaticAddressingDhcpServer"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_server MagicTransitSiteLan#dhcp_server}.'''
        result = self._values.get("dhcp_server")
        return typing.cast(typing.Optional["MagicTransitSiteLanStaticAddressingDhcpServer"], result)

    @builtins.property
    def secondary_address(self) -> typing.Optional[builtins.str]:
        '''A valid CIDR notation representing an IP range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#secondary_address MagicTransitSiteLan#secondary_address}
        '''
        result = self._values.get("secondary_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def virtual_address(self) -> typing.Optional[builtins.str]:
        '''A valid CIDR notation representing an IP range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#virtual_address MagicTransitSiteLan#virtual_address}
        '''
        result = self._values.get("virtual_address")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteLanStaticAddressing(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanStaticAddressingDhcpRelay",
    jsii_struct_bases=[],
    name_mapping={"server_addresses": "serverAddresses"},
)
class MagicTransitSiteLanStaticAddressingDhcpRelay:
    def __init__(
        self,
        *,
        server_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param server_addresses: List of DHCP server IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#server_addresses MagicTransitSiteLan#server_addresses}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1138c77e82c4b09af9801e4252a72fb6584c3202fcc9c80936e8705dc13cb7cd)
            check_type(argname="argument server_addresses", value=server_addresses, expected_type=type_hints["server_addresses"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if server_addresses is not None:
            self._values["server_addresses"] = server_addresses

    @builtins.property
    def server_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of DHCP server IPs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#server_addresses MagicTransitSiteLan#server_addresses}
        '''
        result = self._values.get("server_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteLanStaticAddressingDhcpRelay(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicTransitSiteLanStaticAddressingDhcpRelayOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanStaticAddressingDhcpRelayOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3e99cc4deb5efc023a61bc1c7ca4c428e83bf8370f9929d6741d5825706cc17)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetServerAddresses")
    def reset_server_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerAddresses", []))

    @builtins.property
    @jsii.member(jsii_name="serverAddressesInput")
    def server_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "serverAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="serverAddresses")
    def server_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "serverAddresses"))

    @server_addresses.setter
    def server_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a3ea656f4513d51aa6d81e4033c4d2021aa8d1ca5f57e918381b8c213b285cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverAddresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpRelay]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpRelay]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpRelay]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c74764a3d796dd2ef8e4dcf82889a20ec8ab6a0307b5beefc42ada9d4d2cc22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanStaticAddressingDhcpServer",
    jsii_struct_bases=[],
    name_mapping={
        "dhcp_pool_end": "dhcpPoolEnd",
        "dhcp_pool_start": "dhcpPoolStart",
        "dns_server": "dnsServer",
        "dns_servers": "dnsServers",
        "reservations": "reservations",
    },
)
class MagicTransitSiteLanStaticAddressingDhcpServer:
    def __init__(
        self,
        *,
        dhcp_pool_end: typing.Optional[builtins.str] = None,
        dhcp_pool_start: typing.Optional[builtins.str] = None,
        dns_server: typing.Optional[builtins.str] = None,
        dns_servers: typing.Optional[typing.Sequence[builtins.str]] = None,
        reservations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param dhcp_pool_end: A valid IPv4 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_pool_end MagicTransitSiteLan#dhcp_pool_end}
        :param dhcp_pool_start: A valid IPv4 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_pool_start MagicTransitSiteLan#dhcp_pool_start}
        :param dns_server: A valid IPv4 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dns_server MagicTransitSiteLan#dns_server}
        :param dns_servers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dns_servers MagicTransitSiteLan#dns_servers}.
        :param reservations: Mapping of MAC addresses to IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#reservations MagicTransitSiteLan#reservations}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ad249a96588444599bc97328a6f3cc2991ccd6d871f7f1ce62993cced282205)
            check_type(argname="argument dhcp_pool_end", value=dhcp_pool_end, expected_type=type_hints["dhcp_pool_end"])
            check_type(argname="argument dhcp_pool_start", value=dhcp_pool_start, expected_type=type_hints["dhcp_pool_start"])
            check_type(argname="argument dns_server", value=dns_server, expected_type=type_hints["dns_server"])
            check_type(argname="argument dns_servers", value=dns_servers, expected_type=type_hints["dns_servers"])
            check_type(argname="argument reservations", value=reservations, expected_type=type_hints["reservations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dhcp_pool_end is not None:
            self._values["dhcp_pool_end"] = dhcp_pool_end
        if dhcp_pool_start is not None:
            self._values["dhcp_pool_start"] = dhcp_pool_start
        if dns_server is not None:
            self._values["dns_server"] = dns_server
        if dns_servers is not None:
            self._values["dns_servers"] = dns_servers
        if reservations is not None:
            self._values["reservations"] = reservations

    @builtins.property
    def dhcp_pool_end(self) -> typing.Optional[builtins.str]:
        '''A valid IPv4 address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_pool_end MagicTransitSiteLan#dhcp_pool_end}
        '''
        result = self._values.get("dhcp_pool_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dhcp_pool_start(self) -> typing.Optional[builtins.str]:
        '''A valid IPv4 address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_pool_start MagicTransitSiteLan#dhcp_pool_start}
        '''
        result = self._values.get("dhcp_pool_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns_server(self) -> typing.Optional[builtins.str]:
        '''A valid IPv4 address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dns_server MagicTransitSiteLan#dns_server}
        '''
        result = self._values.get("dns_server")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns_servers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dns_servers MagicTransitSiteLan#dns_servers}.'''
        result = self._values.get("dns_servers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def reservations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Mapping of MAC addresses to IP addresses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#reservations MagicTransitSiteLan#reservations}
        '''
        result = self._values.get("reservations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteLanStaticAddressingDhcpServer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicTransitSiteLanStaticAddressingDhcpServerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanStaticAddressingDhcpServerOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8546f24037ce9681aa07295f862c0e5abf94eeb795a08f053a32cf3e76a739ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDhcpPoolEnd")
    def reset_dhcp_pool_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcpPoolEnd", []))

    @jsii.member(jsii_name="resetDhcpPoolStart")
    def reset_dhcp_pool_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcpPoolStart", []))

    @jsii.member(jsii_name="resetDnsServer")
    def reset_dns_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsServer", []))

    @jsii.member(jsii_name="resetDnsServers")
    def reset_dns_servers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsServers", []))

    @jsii.member(jsii_name="resetReservations")
    def reset_reservations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReservations", []))

    @builtins.property
    @jsii.member(jsii_name="dhcpPoolEndInput")
    def dhcp_pool_end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dhcpPoolEndInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcpPoolStartInput")
    def dhcp_pool_start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dhcpPoolStartInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsServerInput")
    def dns_server_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dnsServerInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsServersInput")
    def dns_servers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsServersInput"))

    @builtins.property
    @jsii.member(jsii_name="reservationsInput")
    def reservations_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "reservationsInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcpPoolEnd")
    def dhcp_pool_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dhcpPoolEnd"))

    @dhcp_pool_end.setter
    def dhcp_pool_end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58171847e2aaec6c7daec33eb599a05c0804e8d900a3ea2a9ba6856010383be9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcpPoolEnd", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dhcpPoolStart")
    def dhcp_pool_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dhcpPoolStart"))

    @dhcp_pool_start.setter
    def dhcp_pool_start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cf5a03dcbf0f33ce2465924fffb900005945cf139a5d3f5af3720bf8d5b6e46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcpPoolStart", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dnsServer")
    def dns_server(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsServer"))

    @dns_server.setter
    def dns_server(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e222d14411a7820b5b082e70f54e7d754c7abb407a911771752c3dfcde69d83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsServer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dnsServers")
    def dns_servers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsServers"))

    @dns_servers.setter
    def dns_servers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b079777e3f57e9b36f708ab237da07a5281d23d0cd7a6130637edbba723df6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsServers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reservations")
    def reservations(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "reservations"))

    @reservations.setter
    def reservations(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ce7b01e0bb549cb4be4f52d40729d175356b07e49ac9ddd09c5e7e6bb5181ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reservations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpServer]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpServer]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpServer]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2ecf9e3b22655725f8727614ba7278295e44265d7815a759fea55eceff63df2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MagicTransitSiteLanStaticAddressingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteLan.MagicTransitSiteLanStaticAddressingOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20ba4b6633ac71c572d018c1e926a1a450241125f37931e1d7edd7ebd93aa1ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDhcpRelay")
    def put_dhcp_relay(
        self,
        *,
        server_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param server_addresses: List of DHCP server IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#server_addresses MagicTransitSiteLan#server_addresses}
        '''
        value = MagicTransitSiteLanStaticAddressingDhcpRelay(
            server_addresses=server_addresses
        )

        return typing.cast(None, jsii.invoke(self, "putDhcpRelay", [value]))

    @jsii.member(jsii_name="putDhcpServer")
    def put_dhcp_server(
        self,
        *,
        dhcp_pool_end: typing.Optional[builtins.str] = None,
        dhcp_pool_start: typing.Optional[builtins.str] = None,
        dns_server: typing.Optional[builtins.str] = None,
        dns_servers: typing.Optional[typing.Sequence[builtins.str]] = None,
        reservations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param dhcp_pool_end: A valid IPv4 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_pool_end MagicTransitSiteLan#dhcp_pool_end}
        :param dhcp_pool_start: A valid IPv4 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dhcp_pool_start MagicTransitSiteLan#dhcp_pool_start}
        :param dns_server: A valid IPv4 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dns_server MagicTransitSiteLan#dns_server}
        :param dns_servers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#dns_servers MagicTransitSiteLan#dns_servers}.
        :param reservations: Mapping of MAC addresses to IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_lan#reservations MagicTransitSiteLan#reservations}
        '''
        value = MagicTransitSiteLanStaticAddressingDhcpServer(
            dhcp_pool_end=dhcp_pool_end,
            dhcp_pool_start=dhcp_pool_start,
            dns_server=dns_server,
            dns_servers=dns_servers,
            reservations=reservations,
        )

        return typing.cast(None, jsii.invoke(self, "putDhcpServer", [value]))

    @jsii.member(jsii_name="resetDhcpRelay")
    def reset_dhcp_relay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcpRelay", []))

    @jsii.member(jsii_name="resetDhcpServer")
    def reset_dhcp_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcpServer", []))

    @jsii.member(jsii_name="resetSecondaryAddress")
    def reset_secondary_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryAddress", []))

    @jsii.member(jsii_name="resetVirtualAddress")
    def reset_virtual_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualAddress", []))

    @builtins.property
    @jsii.member(jsii_name="dhcpRelay")
    def dhcp_relay(self) -> MagicTransitSiteLanStaticAddressingDhcpRelayOutputReference:
        return typing.cast(MagicTransitSiteLanStaticAddressingDhcpRelayOutputReference, jsii.get(self, "dhcpRelay"))

    @builtins.property
    @jsii.member(jsii_name="dhcpServer")
    def dhcp_server(
        self,
    ) -> MagicTransitSiteLanStaticAddressingDhcpServerOutputReference:
        return typing.cast(MagicTransitSiteLanStaticAddressingDhcpServerOutputReference, jsii.get(self, "dhcpServer"))

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcpRelayInput")
    def dhcp_relay_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpRelay]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpRelay]], jsii.get(self, "dhcpRelayInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcpServerInput")
    def dhcp_server_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpServer]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpServer]], jsii.get(self, "dhcpServerInput"))

    @builtins.property
    @jsii.member(jsii_name="secondaryAddressInput")
    def secondary_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secondaryAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualAddressInput")
    def virtual_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6c93214344e1897698a7af23372112425584043402d8dd8b8fc5be63faf1ac3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secondaryAddress")
    def secondary_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secondaryAddress"))

    @secondary_address.setter
    def secondary_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52125402b354bd43dbb5a8668a6ec808f908c06bbd4dc5ff2834a4a7755473ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualAddress")
    def virtual_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualAddress"))

    @virtual_address.setter
    def virtual_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5882285a731e3f9da521199b54ea7d4647a4c8ad07054f15d7d0c38ea933b5dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressing]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressing]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressing]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__301b0b0ef38e680bf1fef8ecb88925ce0b005f93e3b5e7a3bfd694fc7607bb33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "MagicTransitSiteLan",
    "MagicTransitSiteLanConfig",
    "MagicTransitSiteLanNat",
    "MagicTransitSiteLanNatOutputReference",
    "MagicTransitSiteLanRoutedSubnets",
    "MagicTransitSiteLanRoutedSubnetsList",
    "MagicTransitSiteLanRoutedSubnetsNat",
    "MagicTransitSiteLanRoutedSubnetsNatOutputReference",
    "MagicTransitSiteLanRoutedSubnetsOutputReference",
    "MagicTransitSiteLanStaticAddressing",
    "MagicTransitSiteLanStaticAddressingDhcpRelay",
    "MagicTransitSiteLanStaticAddressingDhcpRelayOutputReference",
    "MagicTransitSiteLanStaticAddressingDhcpServer",
    "MagicTransitSiteLanStaticAddressingDhcpServerOutputReference",
    "MagicTransitSiteLanStaticAddressingOutputReference",
]

publication.publish()

def _typecheckingstub__73c712ecc9b90ed1ecc43201f5fe9826c3ea151b664e6bdba5252f6aaf74a4b8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    physport: jsii.Number,
    site_id: builtins.str,
    ha_link: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    nat: typing.Optional[typing.Union[MagicTransitSiteLanNat, typing.Dict[builtins.str, typing.Any]]] = None,
    routed_subnets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MagicTransitSiteLanRoutedSubnets, typing.Dict[builtins.str, typing.Any]]]]] = None,
    static_addressing: typing.Optional[typing.Union[MagicTransitSiteLanStaticAddressing, typing.Dict[builtins.str, typing.Any]]] = None,
    vlan_tag: typing.Optional[jsii.Number] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1108fa794cd7cc1b90408821fbea67cea8646649296199390e6cce9d151b772(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a22429c8ed0a0df172de3bed1cb769b91ccbf482cf5e2d40bc482cc40ccec823(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MagicTransitSiteLanRoutedSubnets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6e8f39e6ef1ccbde67141ae71d2ec4e3cb74414ff27043c0a1f85e323f35009(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91878d41a834e76fc34779f884c211907cb4d7e420b2151926097dee9a2f7e94(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63e88755ecbe1adf7641f6aff76fb154712b4b6494da73817839866ce5517547(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce7dba194bdc2d663ef5060f42c0c005e9402bfd338e79d760db109660c0656b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4c38bdcd6f49273741cbc32f40d73d2a63f4b278d06092b25815ad5f4e33f48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2536c86e8a1beb69269e350219321532384fdb48bb9d78c573ae30779dfc2952(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f2650b680c6c62a17865f013c11ccce9bbabdf80e552ad8fb51a3973082b59c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    physport: jsii.Number,
    site_id: builtins.str,
    ha_link: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    nat: typing.Optional[typing.Union[MagicTransitSiteLanNat, typing.Dict[builtins.str, typing.Any]]] = None,
    routed_subnets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MagicTransitSiteLanRoutedSubnets, typing.Dict[builtins.str, typing.Any]]]]] = None,
    static_addressing: typing.Optional[typing.Union[MagicTransitSiteLanStaticAddressing, typing.Dict[builtins.str, typing.Any]]] = None,
    vlan_tag: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e68b90baf48371cbcd2acdafde1476d2f2e402946cdcbf9bddd5ea88213fcbb8(
    *,
    static_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02b0beffb6f08f588295953be8ddcbd2877343cf850d81f12de36ffcbc69262b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__722bdabf971aa1bf4ab20c53c15ae8d944b7a3ee8f07bf42b3d1dcd25e7c88e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a64e72e3d7a48065eecbad33de503c365bb5b0457f001b979451cb5df06cc5d8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanNat]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b678219da71d5fe426e1aa29f3ac8e85fd873def2c3dcc3e6e60e60c49f3e1ac(
    *,
    next_hop: builtins.str,
    prefix: builtins.str,
    nat: typing.Optional[typing.Union[MagicTransitSiteLanRoutedSubnetsNat, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae6431b295d15187e0e34a428a76e880b3e888c4adb67251392d8a431691d6c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8172aada4a64efcdb675df4ff0f252e72412998d909f67d5c8e1d3adec928512(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a82347c9b7636098f923f5fa6b991673efc57f3e231038a2f62d2e4f83a2db3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35e74521d9614dec34623a67f2b5851ded89b00d5c34060d5b12210facb6f746(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87bd7833d0ef86d144b3f79951568d152e592c9220b91b1dd40c15163fc9e8f1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dce58480c60348672a9a9001235c516eed1cb2e630121192951c3af40ba4291(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MagicTransitSiteLanRoutedSubnets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4be237d28c87e160b0abbcc2c34adc87bb75bdb89f3e05803d0c613f7fea6c8(
    *,
    static_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a18800298500e1298b14e60d51f9f43256b9c132ab9dcaf147311e98102ef5d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfe902eef4a6f3b84c9ff7827fc77a154b4c40d591db0971d444762133f241cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d6d65fab4f6cefc85537bb1628ee75a0cd5fec63801e907714db0647323a638(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnetsNat]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f60783efdf6198f342f0521b2129b2462d097882c0097fe2c847470560bf5dc0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fe66b5c252c4cc3f8e110b4919f9cffd867d1c1318048bb02251fab1d20cc16(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bef0851efd8a4d8c3c7f02d3b8c03700512f1c118b99412f36805cf347bf48ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__018f367e221ab3fe3fbf4b9bdeeae992f0ad0f1e4bf05e13715e110709d51f47(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanRoutedSubnets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c826b0532d676b9d6f5e1b3fddfece6ff45b050cea9d2fde09f8ee829411f25a(
    *,
    address: builtins.str,
    dhcp_relay: typing.Optional[typing.Union[MagicTransitSiteLanStaticAddressingDhcpRelay, typing.Dict[builtins.str, typing.Any]]] = None,
    dhcp_server: typing.Optional[typing.Union[MagicTransitSiteLanStaticAddressingDhcpServer, typing.Dict[builtins.str, typing.Any]]] = None,
    secondary_address: typing.Optional[builtins.str] = None,
    virtual_address: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1138c77e82c4b09af9801e4252a72fb6584c3202fcc9c80936e8705dc13cb7cd(
    *,
    server_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3e99cc4deb5efc023a61bc1c7ca4c428e83bf8370f9929d6741d5825706cc17(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a3ea656f4513d51aa6d81e4033c4d2021aa8d1ca5f57e918381b8c213b285cb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c74764a3d796dd2ef8e4dcf82889a20ec8ab6a0307b5beefc42ada9d4d2cc22(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpRelay]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ad249a96588444599bc97328a6f3cc2991ccd6d871f7f1ce62993cced282205(
    *,
    dhcp_pool_end: typing.Optional[builtins.str] = None,
    dhcp_pool_start: typing.Optional[builtins.str] = None,
    dns_server: typing.Optional[builtins.str] = None,
    dns_servers: typing.Optional[typing.Sequence[builtins.str]] = None,
    reservations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8546f24037ce9681aa07295f862c0e5abf94eeb795a08f053a32cf3e76a739ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58171847e2aaec6c7daec33eb599a05c0804e8d900a3ea2a9ba6856010383be9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cf5a03dcbf0f33ce2465924fffb900005945cf139a5d3f5af3720bf8d5b6e46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e222d14411a7820b5b082e70f54e7d754c7abb407a911771752c3dfcde69d83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b079777e3f57e9b36f708ab237da07a5281d23d0cd7a6130637edbba723df6a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ce7b01e0bb549cb4be4f52d40729d175356b07e49ac9ddd09c5e7e6bb5181ba(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2ecf9e3b22655725f8727614ba7278295e44265d7815a759fea55eceff63df2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressingDhcpServer]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20ba4b6633ac71c572d018c1e926a1a450241125f37931e1d7edd7ebd93aa1ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6c93214344e1897698a7af23372112425584043402d8dd8b8fc5be63faf1ac3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52125402b354bd43dbb5a8668a6ec808f908c06bbd4dc5ff2834a4a7755473ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5882285a731e3f9da521199b54ea7d4647a4c8ad07054f15d7d0c38ea933b5dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__301b0b0ef38e680bf1fef8ecb88925ce0b005f93e3b5e7a3bfd694fc7607bb33(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteLanStaticAddressing]],
) -> None:
    """Type checking stubs"""
    pass
