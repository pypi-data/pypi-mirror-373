r'''
# `cloudflare_magic_wan_ipsec_tunnel`

Refer to the Terraform Registry for docs: [`cloudflare_magic_wan_ipsec_tunnel`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel).
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


class MagicWanIpsecTunnel(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicWanIpsecTunnel.MagicWanIpsecTunnel",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel cloudflare_magic_wan_ipsec_tunnel}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        cloudflare_endpoint: builtins.str,
        interface_address: builtins.str,
        name: builtins.str,
        customer_endpoint: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        health_check: typing.Optional[typing.Union["MagicWanIpsecTunnelHealthCheck", typing.Dict[builtins.str, typing.Any]]] = None,
        interface_address6: typing.Optional[builtins.str] = None,
        psk: typing.Optional[builtins.str] = None,
        replay_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel cloudflare_magic_wan_ipsec_tunnel} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#account_id MagicWanIpsecTunnel#account_id}
        :param cloudflare_endpoint: The IP address assigned to the Cloudflare side of the IPsec tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#cloudflare_endpoint MagicWanIpsecTunnel#cloudflare_endpoint}
        :param interface_address: A 31-bit prefix (/31 in CIDR notation) supporting two hosts, one for each side of the tunnel. Select the subnet from the following private IP space: 10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255, 192.168.0.0–192.168.255.255. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#interface_address MagicWanIpsecTunnel#interface_address}
        :param name: The name of the IPsec tunnel. The name cannot share a name with other tunnels. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#name MagicWanIpsecTunnel#name}
        :param customer_endpoint: The IP address assigned to the customer side of the IPsec tunnel. Not required, but must be set for proactive traceroutes to work. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#customer_endpoint MagicWanIpsecTunnel#customer_endpoint}
        :param description: An optional description forthe IPsec tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#description MagicWanIpsecTunnel#description}
        :param health_check: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#health_check MagicWanIpsecTunnel#health_check}.
        :param interface_address6: A 127 bit IPV6 prefix from within the virtual_subnet6 prefix space with the address being the first IP of the subnet and not same as the address of virtual_subnet6. Eg if virtual_subnet6 is 2606:54c1:7:0:a9fe:12d2::/127 , interface_address6 could be 2606:54c1:7:0:a9fe:12d2:1:200/127 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#interface_address6 MagicWanIpsecTunnel#interface_address6}
        :param psk: A randomly generated or provided string for use in the IPsec tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#psk MagicWanIpsecTunnel#psk}
        :param replay_protection: If ``true``, then IPsec replay protection will be supported in the Cloudflare-to-customer direction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#replay_protection MagicWanIpsecTunnel#replay_protection}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07f1fe5e75a852e61f1152817182fc7f3c460e7c5413cd76a378cfde02f3182f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = MagicWanIpsecTunnelConfig(
            account_id=account_id,
            cloudflare_endpoint=cloudflare_endpoint,
            interface_address=interface_address,
            name=name,
            customer_endpoint=customer_endpoint,
            description=description,
            health_check=health_check,
            interface_address6=interface_address6,
            psk=psk,
            replay_protection=replay_protection,
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
        '''Generates CDKTF code for importing a MagicWanIpsecTunnel resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MagicWanIpsecTunnel to import.
        :param import_from_id: The id of the existing MagicWanIpsecTunnel that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MagicWanIpsecTunnel to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee6d93a5d2eae08a29b3f6faf432d82d8f0864b071555a85d5b5b9d1eae7e983)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putHealthCheck")
    def put_health_check(
        self,
        *,
        direction: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        rate: typing.Optional[builtins.str] = None,
        target: typing.Optional[typing.Union["MagicWanIpsecTunnelHealthCheckTarget", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param direction: The direction of the flow of the healthcheck. Either unidirectional, where the probe comes to you via the tunnel and the result comes back to Cloudflare via the open Internet, or bidirectional where both the probe and result come and go via the tunnel. Available values: "unidirectional", "bidirectional". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#direction MagicWanIpsecTunnel#direction}
        :param enabled: Determines whether to run healthchecks for a tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#enabled MagicWanIpsecTunnel#enabled}
        :param rate: How frequent the health check is run. The default value is ``mid``. Available values: "low", "mid", "high". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#rate MagicWanIpsecTunnel#rate}
        :param target: The destination address in a request type health check. After the healthcheck is decapsulated at the customer end of the tunnel, the ICMP echo will be forwarded to this address. This field defaults to ``customer_gre_endpoint address``. This field is ignored for bidirectional healthchecks as the interface_address (not assigned to the Cloudflare side of the tunnel) is used as the target. Must be in object form if the x-magic-new-hc-target header is set to true and string form if x-magic-new-hc-target is absent or set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#target MagicWanIpsecTunnel#target}
        :param type: The type of healthcheck to run, reply or request. The default value is ``reply``. Available values: "reply", "request". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#type MagicWanIpsecTunnel#type}
        '''
        value = MagicWanIpsecTunnelHealthCheck(
            direction=direction, enabled=enabled, rate=rate, target=target, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putHealthCheck", [value]))

    @jsii.member(jsii_name="resetCustomerEndpoint")
    def reset_customer_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomerEndpoint", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetHealthCheck")
    def reset_health_check(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheck", []))

    @jsii.member(jsii_name="resetInterfaceAddress6")
    def reset_interface_address6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterfaceAddress6", []))

    @jsii.member(jsii_name="resetPsk")
    def reset_psk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPsk", []))

    @jsii.member(jsii_name="resetReplayProtection")
    def reset_replay_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplayProtection", []))

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
    @jsii.member(jsii_name="allowNullCipher")
    def allow_null_cipher(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowNullCipher"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="healthCheck")
    def health_check(self) -> "MagicWanIpsecTunnelHealthCheckOutputReference":
        return typing.cast("MagicWanIpsecTunnelHealthCheckOutputReference", jsii.get(self, "healthCheck"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="pskMetadata")
    def psk_metadata(self) -> "MagicWanIpsecTunnelPskMetadataOutputReference":
        return typing.cast("MagicWanIpsecTunnelPskMetadataOutputReference", jsii.get(self, "pskMetadata"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudflareEndpointInput")
    def cloudflare_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudflareEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="customerEndpointInput")
    def customer_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckInput")
    def health_check_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicWanIpsecTunnelHealthCheck"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicWanIpsecTunnelHealthCheck"]], jsii.get(self, "healthCheckInput"))

    @builtins.property
    @jsii.member(jsii_name="interfaceAddress6Input")
    def interface_address6_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "interfaceAddress6Input"))

    @builtins.property
    @jsii.member(jsii_name="interfaceAddressInput")
    def interface_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "interfaceAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="pskInput")
    def psk_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pskInput"))

    @builtins.property
    @jsii.member(jsii_name="replayProtectionInput")
    def replay_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "replayProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__866a448aaf0700a10a0c6c76bdb0144f76fbd46eb74fb043de5f2f62a2f5acf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cloudflareEndpoint")
    def cloudflare_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudflareEndpoint"))

    @cloudflare_endpoint.setter
    def cloudflare_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0d52d3ae271abdefc733424184ed1f7673d2752613f044f4165f26305dfdffc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudflareEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customerEndpoint")
    def customer_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerEndpoint"))

    @customer_endpoint.setter
    def customer_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3732fb5fad013e6c715dbaa24931b2a81a1d8473cad0c611f241363dd8304bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customerEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb6b112485e2bc5ff223d63eeb22853fd3ec9e54a7ffc89165769b5f6a4fcbcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interfaceAddress")
    def interface_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interfaceAddress"))

    @interface_address.setter
    def interface_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0201d238fe30cd014cd1b34a6380166d26155fcbc0ca78bb2fdd25872b7a7410)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interfaceAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interfaceAddress6")
    def interface_address6(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interfaceAddress6"))

    @interface_address6.setter
    def interface_address6(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36dc0afd3c072aff3d48617e1fae08158efec04f3a50d245ed5fadc3334a9ff4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interfaceAddress6", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48e5991012ada9de51f5d52cae81dcce77af9c09ad3cf72b31e102e61e398263)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="psk")
    def psk(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "psk"))

    @psk.setter
    def psk(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29186ec283b1927eeb264de6b7676b7da548cd8d15f8361aa6c2a0c3e6b838a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "psk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replayProtection")
    def replay_protection(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "replayProtection"))

    @replay_protection.setter
    def replay_protection(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5dd721dc971cf8e1e7d768951455ff3eabb7a5d782840f14b182f25212b5595)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replayProtection", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicWanIpsecTunnel.MagicWanIpsecTunnelConfig",
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
        "cloudflare_endpoint": "cloudflareEndpoint",
        "interface_address": "interfaceAddress",
        "name": "name",
        "customer_endpoint": "customerEndpoint",
        "description": "description",
        "health_check": "healthCheck",
        "interface_address6": "interfaceAddress6",
        "psk": "psk",
        "replay_protection": "replayProtection",
    },
)
class MagicWanIpsecTunnelConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cloudflare_endpoint: builtins.str,
        interface_address: builtins.str,
        name: builtins.str,
        customer_endpoint: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        health_check: typing.Optional[typing.Union["MagicWanIpsecTunnelHealthCheck", typing.Dict[builtins.str, typing.Any]]] = None,
        interface_address6: typing.Optional[builtins.str] = None,
        psk: typing.Optional[builtins.str] = None,
        replay_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#account_id MagicWanIpsecTunnel#account_id}
        :param cloudflare_endpoint: The IP address assigned to the Cloudflare side of the IPsec tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#cloudflare_endpoint MagicWanIpsecTunnel#cloudflare_endpoint}
        :param interface_address: A 31-bit prefix (/31 in CIDR notation) supporting two hosts, one for each side of the tunnel. Select the subnet from the following private IP space: 10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255, 192.168.0.0–192.168.255.255. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#interface_address MagicWanIpsecTunnel#interface_address}
        :param name: The name of the IPsec tunnel. The name cannot share a name with other tunnels. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#name MagicWanIpsecTunnel#name}
        :param customer_endpoint: The IP address assigned to the customer side of the IPsec tunnel. Not required, but must be set for proactive traceroutes to work. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#customer_endpoint MagicWanIpsecTunnel#customer_endpoint}
        :param description: An optional description forthe IPsec tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#description MagicWanIpsecTunnel#description}
        :param health_check: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#health_check MagicWanIpsecTunnel#health_check}.
        :param interface_address6: A 127 bit IPV6 prefix from within the virtual_subnet6 prefix space with the address being the first IP of the subnet and not same as the address of virtual_subnet6. Eg if virtual_subnet6 is 2606:54c1:7:0:a9fe:12d2::/127 , interface_address6 could be 2606:54c1:7:0:a9fe:12d2:1:200/127 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#interface_address6 MagicWanIpsecTunnel#interface_address6}
        :param psk: A randomly generated or provided string for use in the IPsec tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#psk MagicWanIpsecTunnel#psk}
        :param replay_protection: If ``true``, then IPsec replay protection will be supported in the Cloudflare-to-customer direction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#replay_protection MagicWanIpsecTunnel#replay_protection}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(health_check, dict):
            health_check = MagicWanIpsecTunnelHealthCheck(**health_check)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3e2d1f9b38e27a904863c5ae9a55e291e01f2b09c4186662501f6e0cb52ced4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument cloudflare_endpoint", value=cloudflare_endpoint, expected_type=type_hints["cloudflare_endpoint"])
            check_type(argname="argument interface_address", value=interface_address, expected_type=type_hints["interface_address"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument customer_endpoint", value=customer_endpoint, expected_type=type_hints["customer_endpoint"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument interface_address6", value=interface_address6, expected_type=type_hints["interface_address6"])
            check_type(argname="argument psk", value=psk, expected_type=type_hints["psk"])
            check_type(argname="argument replay_protection", value=replay_protection, expected_type=type_hints["replay_protection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "cloudflare_endpoint": cloudflare_endpoint,
            "interface_address": interface_address,
            "name": name,
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
        if customer_endpoint is not None:
            self._values["customer_endpoint"] = customer_endpoint
        if description is not None:
            self._values["description"] = description
        if health_check is not None:
            self._values["health_check"] = health_check
        if interface_address6 is not None:
            self._values["interface_address6"] = interface_address6
        if psk is not None:
            self._values["psk"] = psk
        if replay_protection is not None:
            self._values["replay_protection"] = replay_protection

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#account_id MagicWanIpsecTunnel#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloudflare_endpoint(self) -> builtins.str:
        '''The IP address assigned to the Cloudflare side of the IPsec tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#cloudflare_endpoint MagicWanIpsecTunnel#cloudflare_endpoint}
        '''
        result = self._values.get("cloudflare_endpoint")
        assert result is not None, "Required property 'cloudflare_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def interface_address(self) -> builtins.str:
        '''A 31-bit prefix (/31 in CIDR notation) supporting two hosts, one for each side of the tunnel.

        Select the subnet from the following private IP space: 10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255, 192.168.0.0–192.168.255.255.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#interface_address MagicWanIpsecTunnel#interface_address}
        '''
        result = self._values.get("interface_address")
        assert result is not None, "Required property 'interface_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the IPsec tunnel. The name cannot share a name with other tunnels.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#name MagicWanIpsecTunnel#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def customer_endpoint(self) -> typing.Optional[builtins.str]:
        '''The IP address assigned to the customer side of the IPsec tunnel.

        Not required, but must be set for proactive traceroutes to work.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#customer_endpoint MagicWanIpsecTunnel#customer_endpoint}
        '''
        result = self._values.get("customer_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''An optional description forthe IPsec tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#description MagicWanIpsecTunnel#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def health_check(self) -> typing.Optional["MagicWanIpsecTunnelHealthCheck"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#health_check MagicWanIpsecTunnel#health_check}.'''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional["MagicWanIpsecTunnelHealthCheck"], result)

    @builtins.property
    def interface_address6(self) -> typing.Optional[builtins.str]:
        '''A 127 bit IPV6 prefix from within the virtual_subnet6 prefix space with the address being the first IP of the subnet and not same as the address of virtual_subnet6.

        Eg if virtual_subnet6 is 2606:54c1:7:0:a9fe:12d2::/127 , interface_address6 could be 2606:54c1:7:0:a9fe:12d2:1:200/127

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#interface_address6 MagicWanIpsecTunnel#interface_address6}
        '''
        result = self._values.get("interface_address6")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def psk(self) -> typing.Optional[builtins.str]:
        '''A randomly generated or provided string for use in the IPsec tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#psk MagicWanIpsecTunnel#psk}
        '''
        result = self._values.get("psk")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replay_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If ``true``, then IPsec replay protection will be supported in the Cloudflare-to-customer direction.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#replay_protection MagicWanIpsecTunnel#replay_protection}
        '''
        result = self._values.get("replay_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicWanIpsecTunnelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicWanIpsecTunnel.MagicWanIpsecTunnelHealthCheck",
    jsii_struct_bases=[],
    name_mapping={
        "direction": "direction",
        "enabled": "enabled",
        "rate": "rate",
        "target": "target",
        "type": "type",
    },
)
class MagicWanIpsecTunnelHealthCheck:
    def __init__(
        self,
        *,
        direction: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        rate: typing.Optional[builtins.str] = None,
        target: typing.Optional[typing.Union["MagicWanIpsecTunnelHealthCheckTarget", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param direction: The direction of the flow of the healthcheck. Either unidirectional, where the probe comes to you via the tunnel and the result comes back to Cloudflare via the open Internet, or bidirectional where both the probe and result come and go via the tunnel. Available values: "unidirectional", "bidirectional". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#direction MagicWanIpsecTunnel#direction}
        :param enabled: Determines whether to run healthchecks for a tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#enabled MagicWanIpsecTunnel#enabled}
        :param rate: How frequent the health check is run. The default value is ``mid``. Available values: "low", "mid", "high". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#rate MagicWanIpsecTunnel#rate}
        :param target: The destination address in a request type health check. After the healthcheck is decapsulated at the customer end of the tunnel, the ICMP echo will be forwarded to this address. This field defaults to ``customer_gre_endpoint address``. This field is ignored for bidirectional healthchecks as the interface_address (not assigned to the Cloudflare side of the tunnel) is used as the target. Must be in object form if the x-magic-new-hc-target header is set to true and string form if x-magic-new-hc-target is absent or set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#target MagicWanIpsecTunnel#target}
        :param type: The type of healthcheck to run, reply or request. The default value is ``reply``. Available values: "reply", "request". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#type MagicWanIpsecTunnel#type}
        '''
        if isinstance(target, dict):
            target = MagicWanIpsecTunnelHealthCheckTarget(**target)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5c7366a792df55f01bf43edeea8973e983813ed9972d70a9af4ecb50f0585e0)
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument rate", value=rate, expected_type=type_hints["rate"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if direction is not None:
            self._values["direction"] = direction
        if enabled is not None:
            self._values["enabled"] = enabled
        if rate is not None:
            self._values["rate"] = rate
        if target is not None:
            self._values["target"] = target
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def direction(self) -> typing.Optional[builtins.str]:
        '''The direction of the flow of the healthcheck.

        Either unidirectional, where the probe comes to you via the tunnel and the result comes back to Cloudflare via the open Internet, or bidirectional where both the probe and result come and go via the tunnel.
        Available values: "unidirectional", "bidirectional".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#direction MagicWanIpsecTunnel#direction}
        '''
        result = self._values.get("direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines whether to run healthchecks for a tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#enabled MagicWanIpsecTunnel#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def rate(self) -> typing.Optional[builtins.str]:
        '''How frequent the health check is run. The default value is ``mid``. Available values: "low", "mid", "high".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#rate MagicWanIpsecTunnel#rate}
        '''
        result = self._values.get("rate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional["MagicWanIpsecTunnelHealthCheckTarget"]:
        '''The destination address in a request type health check.

        After the healthcheck is decapsulated at the customer end of the tunnel, the ICMP echo will be forwarded to this address. This field defaults to ``customer_gre_endpoint address``. This field is ignored for bidirectional healthchecks as the interface_address (not assigned to the Cloudflare side of the tunnel) is used as the target. Must be in object form if the x-magic-new-hc-target header is set to true and string form if x-magic-new-hc-target is absent or set to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#target MagicWanIpsecTunnel#target}
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional["MagicWanIpsecTunnelHealthCheckTarget"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of healthcheck to run, reply or request. The default value is ``reply``. Available values: "reply", "request".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#type MagicWanIpsecTunnel#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicWanIpsecTunnelHealthCheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicWanIpsecTunnelHealthCheckOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicWanIpsecTunnel.MagicWanIpsecTunnelHealthCheckOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c355cf98abd9325cd3ba4c47cd844b66c73a76cb545589c6f90a71d6711fe142)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTarget")
    def put_target(self, *, saved: typing.Optional[builtins.str] = None) -> None:
        '''
        :param saved: The saved health check target. Setting the value to the empty string indicates that the calculated default value will be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#saved MagicWanIpsecTunnel#saved}
        '''
        value = MagicWanIpsecTunnelHealthCheckTarget(saved=saved)

        return typing.cast(None, jsii.invoke(self, "putTarget", [value]))

    @jsii.member(jsii_name="resetDirection")
    def reset_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirection", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetRate")
    def reset_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRate", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> "MagicWanIpsecTunnelHealthCheckTargetOutputReference":
        return typing.cast("MagicWanIpsecTunnelHealthCheckTargetOutputReference", jsii.get(self, "target"))

    @builtins.property
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="rateInput")
    def rate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rateInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicWanIpsecTunnelHealthCheckTarget"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicWanIpsecTunnelHealthCheckTarget"]], jsii.get(self, "targetInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d2fb2c85804a71e219945636545e6a2528aca745fcb2bfc1d22f190eb533715)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad16d9ef8730a382ef2bb5025e82ec4f77afab349cf0966e4e8f161bc3e36153)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rate")
    def rate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rate"))

    @rate.setter
    def rate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15bf758a9c44eb5f7a244aa2d3b6c9aee1e56bcf3ec404565163d60d92395a3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87d62a9588bb1add7741fe4da459b59aa0e825ef0373e19be87e83419dec97d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanIpsecTunnelHealthCheck]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanIpsecTunnelHealthCheck]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanIpsecTunnelHealthCheck]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__601917032936155ca7e141c9a014af64b64d772f0f675ed878eaebc674bce624)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicWanIpsecTunnel.MagicWanIpsecTunnelHealthCheckTarget",
    jsii_struct_bases=[],
    name_mapping={"saved": "saved"},
)
class MagicWanIpsecTunnelHealthCheckTarget:
    def __init__(self, *, saved: typing.Optional[builtins.str] = None) -> None:
        '''
        :param saved: The saved health check target. Setting the value to the empty string indicates that the calculated default value will be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#saved MagicWanIpsecTunnel#saved}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e184db03a3a88166c7aad8c8d708c59c3f8d0de8e7574300faadae112b29a6f)
            check_type(argname="argument saved", value=saved, expected_type=type_hints["saved"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if saved is not None:
            self._values["saved"] = saved

    @builtins.property
    def saved(self) -> typing.Optional[builtins.str]:
        '''The saved health check target.

        Setting the value to the empty string indicates that the calculated default value will be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_ipsec_tunnel#saved MagicWanIpsecTunnel#saved}
        '''
        result = self._values.get("saved")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicWanIpsecTunnelHealthCheckTarget(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicWanIpsecTunnelHealthCheckTargetOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicWanIpsecTunnel.MagicWanIpsecTunnelHealthCheckTargetOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c50aa616c122a05d2f9380fa7a4f4236096bde1f4618531b154602216499a489)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSaved")
    def reset_saved(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaved", []))

    @builtins.property
    @jsii.member(jsii_name="effective")
    def effective(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effective"))

    @builtins.property
    @jsii.member(jsii_name="savedInput")
    def saved_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "savedInput"))

    @builtins.property
    @jsii.member(jsii_name="saved")
    def saved(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "saved"))

    @saved.setter
    def saved(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13d455f66ff00f993b0205ace1ff23a699c76705d9ec605026519a863e3b1c6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "saved", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanIpsecTunnelHealthCheckTarget]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanIpsecTunnelHealthCheckTarget]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanIpsecTunnelHealthCheckTarget]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__755770606922002e38918155dd08403b2a55999ab176cd4e4870e2d0475fb53a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicWanIpsecTunnel.MagicWanIpsecTunnelPskMetadata",
    jsii_struct_bases=[],
    name_mapping={},
)
class MagicWanIpsecTunnelPskMetadata:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicWanIpsecTunnelPskMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicWanIpsecTunnelPskMetadataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicWanIpsecTunnel.MagicWanIpsecTunnelPskMetadataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__abdc8e0242b83e8415cfc724e246fe20e475a552778007b78bc69204cdd4b620)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lastGeneratedOn")
    def last_generated_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastGeneratedOn"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MagicWanIpsecTunnelPskMetadata]:
        return typing.cast(typing.Optional[MagicWanIpsecTunnelPskMetadata], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MagicWanIpsecTunnelPskMetadata],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cf08ad63d2e326ac275f0aa2329e920548c5994fe1b7c2460edda0c03359fcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "MagicWanIpsecTunnel",
    "MagicWanIpsecTunnelConfig",
    "MagicWanIpsecTunnelHealthCheck",
    "MagicWanIpsecTunnelHealthCheckOutputReference",
    "MagicWanIpsecTunnelHealthCheckTarget",
    "MagicWanIpsecTunnelHealthCheckTargetOutputReference",
    "MagicWanIpsecTunnelPskMetadata",
    "MagicWanIpsecTunnelPskMetadataOutputReference",
]

publication.publish()

def _typecheckingstub__07f1fe5e75a852e61f1152817182fc7f3c460e7c5413cd76a378cfde02f3182f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    cloudflare_endpoint: builtins.str,
    interface_address: builtins.str,
    name: builtins.str,
    customer_endpoint: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    health_check: typing.Optional[typing.Union[MagicWanIpsecTunnelHealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    interface_address6: typing.Optional[builtins.str] = None,
    psk: typing.Optional[builtins.str] = None,
    replay_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__ee6d93a5d2eae08a29b3f6faf432d82d8f0864b071555a85d5b5b9d1eae7e983(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__866a448aaf0700a10a0c6c76bdb0144f76fbd46eb74fb043de5f2f62a2f5acf4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0d52d3ae271abdefc733424184ed1f7673d2752613f044f4165f26305dfdffc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3732fb5fad013e6c715dbaa24931b2a81a1d8473cad0c611f241363dd8304bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb6b112485e2bc5ff223d63eeb22853fd3ec9e54a7ffc89165769b5f6a4fcbcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0201d238fe30cd014cd1b34a6380166d26155fcbc0ca78bb2fdd25872b7a7410(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36dc0afd3c072aff3d48617e1fae08158efec04f3a50d245ed5fadc3334a9ff4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48e5991012ada9de51f5d52cae81dcce77af9c09ad3cf72b31e102e61e398263(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29186ec283b1927eeb264de6b7676b7da548cd8d15f8361aa6c2a0c3e6b838a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5dd721dc971cf8e1e7d768951455ff3eabb7a5d782840f14b182f25212b5595(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3e2d1f9b38e27a904863c5ae9a55e291e01f2b09c4186662501f6e0cb52ced4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    cloudflare_endpoint: builtins.str,
    interface_address: builtins.str,
    name: builtins.str,
    customer_endpoint: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    health_check: typing.Optional[typing.Union[MagicWanIpsecTunnelHealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    interface_address6: typing.Optional[builtins.str] = None,
    psk: typing.Optional[builtins.str] = None,
    replay_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5c7366a792df55f01bf43edeea8973e983813ed9972d70a9af4ecb50f0585e0(
    *,
    direction: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    rate: typing.Optional[builtins.str] = None,
    target: typing.Optional[typing.Union[MagicWanIpsecTunnelHealthCheckTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c355cf98abd9325cd3ba4c47cd844b66c73a76cb545589c6f90a71d6711fe142(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d2fb2c85804a71e219945636545e6a2528aca745fcb2bfc1d22f190eb533715(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad16d9ef8730a382ef2bb5025e82ec4f77afab349cf0966e4e8f161bc3e36153(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15bf758a9c44eb5f7a244aa2d3b6c9aee1e56bcf3ec404565163d60d92395a3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87d62a9588bb1add7741fe4da459b59aa0e825ef0373e19be87e83419dec97d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__601917032936155ca7e141c9a014af64b64d772f0f675ed878eaebc674bce624(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanIpsecTunnelHealthCheck]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e184db03a3a88166c7aad8c8d708c59c3f8d0de8e7574300faadae112b29a6f(
    *,
    saved: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c50aa616c122a05d2f9380fa7a4f4236096bde1f4618531b154602216499a489(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13d455f66ff00f993b0205ace1ff23a699c76705d9ec605026519a863e3b1c6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__755770606922002e38918155dd08403b2a55999ab176cd4e4870e2d0475fb53a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanIpsecTunnelHealthCheckTarget]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abdc8e0242b83e8415cfc724e246fe20e475a552778007b78bc69204cdd4b620(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cf08ad63d2e326ac275f0aa2329e920548c5994fe1b7c2460edda0c03359fcf(
    value: typing.Optional[MagicWanIpsecTunnelPskMetadata],
) -> None:
    """Type checking stubs"""
    pass
