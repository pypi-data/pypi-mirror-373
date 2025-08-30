r'''
# `cloudflare_magic_wan_gre_tunnel`

Refer to the Terraform Registry for docs: [`cloudflare_magic_wan_gre_tunnel`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel).
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


class MagicWanGreTunnel(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicWanGreTunnel.MagicWanGreTunnel",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel cloudflare_magic_wan_gre_tunnel}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        cloudflare_gre_endpoint: builtins.str,
        customer_gre_endpoint: builtins.str,
        interface_address: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        health_check: typing.Optional[typing.Union["MagicWanGreTunnelHealthCheck", typing.Dict[builtins.str, typing.Any]]] = None,
        interface_address6: typing.Optional[builtins.str] = None,
        mtu: typing.Optional[jsii.Number] = None,
        ttl: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel cloudflare_magic_wan_gre_tunnel} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#account_id MagicWanGreTunnel#account_id}
        :param cloudflare_gre_endpoint: The IP address assigned to the Cloudflare side of the GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#cloudflare_gre_endpoint MagicWanGreTunnel#cloudflare_gre_endpoint}
        :param customer_gre_endpoint: The IP address assigned to the customer side of the GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#customer_gre_endpoint MagicWanGreTunnel#customer_gre_endpoint}
        :param interface_address: A 31-bit prefix (/31 in CIDR notation) supporting two hosts, one for each side of the tunnel. Select the subnet from the following private IP space: 10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255, 192.168.0.0–192.168.255.255. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#interface_address MagicWanGreTunnel#interface_address}
        :param name: The name of the tunnel. The name cannot contain spaces or special characters, must be 15 characters or less, and cannot share a name with another GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#name MagicWanGreTunnel#name}
        :param description: An optional description of the GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#description MagicWanGreTunnel#description}
        :param health_check: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#health_check MagicWanGreTunnel#health_check}.
        :param interface_address6: A 127 bit IPV6 prefix from within the virtual_subnet6 prefix space with the address being the first IP of the subnet and not same as the address of virtual_subnet6. Eg if virtual_subnet6 is 2606:54c1:7:0:a9fe:12d2::/127 , interface_address6 could be 2606:54c1:7:0:a9fe:12d2:1:200/127 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#interface_address6 MagicWanGreTunnel#interface_address6}
        :param mtu: Maximum Transmission Unit (MTU) in bytes for the GRE tunnel. The minimum value is 576. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#mtu MagicWanGreTunnel#mtu}
        :param ttl: Time To Live (TTL) in number of hops of the GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#ttl MagicWanGreTunnel#ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__021afd1f2c9cb9ab09f14b2d262952d61c6e756ea4255b9a67adb055618108e2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = MagicWanGreTunnelConfig(
            account_id=account_id,
            cloudflare_gre_endpoint=cloudflare_gre_endpoint,
            customer_gre_endpoint=customer_gre_endpoint,
            interface_address=interface_address,
            name=name,
            description=description,
            health_check=health_check,
            interface_address6=interface_address6,
            mtu=mtu,
            ttl=ttl,
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
        '''Generates CDKTF code for importing a MagicWanGreTunnel resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MagicWanGreTunnel to import.
        :param import_from_id: The id of the existing MagicWanGreTunnel that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MagicWanGreTunnel to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d06765414224d7bc61fe6d40b3b81f240d21918cdba8abab53e60a284631d83)
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
        target: typing.Optional[typing.Union["MagicWanGreTunnelHealthCheckTarget", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param direction: The direction of the flow of the healthcheck. Either unidirectional, where the probe comes to you via the tunnel and the result comes back to Cloudflare via the open Internet, or bidirectional where both the probe and result come and go via the tunnel. Available values: "unidirectional", "bidirectional". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#direction MagicWanGreTunnel#direction}
        :param enabled: Determines whether to run healthchecks for a tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#enabled MagicWanGreTunnel#enabled}
        :param rate: How frequent the health check is run. The default value is ``mid``. Available values: "low", "mid", "high". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#rate MagicWanGreTunnel#rate}
        :param target: The destination address in a request type health check. After the healthcheck is decapsulated at the customer end of the tunnel, the ICMP echo will be forwarded to this address. This field defaults to ``customer_gre_endpoint address``. This field is ignored for bidirectional healthchecks as the interface_address (not assigned to the Cloudflare side of the tunnel) is used as the target. Must be in object form if the x-magic-new-hc-target header is set to true and string form if x-magic-new-hc-target is absent or set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#target MagicWanGreTunnel#target}
        :param type: The type of healthcheck to run, reply or request. The default value is ``reply``. Available values: "reply", "request". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#type MagicWanGreTunnel#type}
        '''
        value = MagicWanGreTunnelHealthCheck(
            direction=direction, enabled=enabled, rate=rate, target=target, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putHealthCheck", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetHealthCheck")
    def reset_health_check(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheck", []))

    @jsii.member(jsii_name="resetInterfaceAddress6")
    def reset_interface_address6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterfaceAddress6", []))

    @jsii.member(jsii_name="resetMtu")
    def reset_mtu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMtu", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

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
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="healthCheck")
    def health_check(self) -> "MagicWanGreTunnelHealthCheckOutputReference":
        return typing.cast("MagicWanGreTunnelHealthCheckOutputReference", jsii.get(self, "healthCheck"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudflareGreEndpointInput")
    def cloudflare_gre_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudflareGreEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="customerGreEndpointInput")
    def customer_gre_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerGreEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckInput")
    def health_check_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicWanGreTunnelHealthCheck"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicWanGreTunnelHealthCheck"]], jsii.get(self, "healthCheckInput"))

    @builtins.property
    @jsii.member(jsii_name="interfaceAddress6Input")
    def interface_address6_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "interfaceAddress6Input"))

    @builtins.property
    @jsii.member(jsii_name="interfaceAddressInput")
    def interface_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "interfaceAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="mtuInput")
    def mtu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "mtuInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2db28b4e981fa051508c13afaf6a949c902dd1add99ee4c55d250533385eec2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cloudflareGreEndpoint")
    def cloudflare_gre_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudflareGreEndpoint"))

    @cloudflare_gre_endpoint.setter
    def cloudflare_gre_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5fa4d5dc3a09a2f5653a16454dc03bba6f5025662d55c83d2b6b5d88df7f4d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudflareGreEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customerGreEndpoint")
    def customer_gre_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerGreEndpoint"))

    @customer_gre_endpoint.setter
    def customer_gre_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0fd5e1fc7a3f682f42edd242ca24988df279a237a90aca74916b3df4dd255d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customerGreEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a186c09b75b28850c1fac3461e701050407f01e152c3452c139303aa825fef5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interfaceAddress")
    def interface_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interfaceAddress"))

    @interface_address.setter
    def interface_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e31573ce91993487a57e216616804ec1c2b011954ebe5156b23dd8209b22e68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interfaceAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interfaceAddress6")
    def interface_address6(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interfaceAddress6"))

    @interface_address6.setter
    def interface_address6(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffa9b0dbe3525c930820f7f88e009f98d74ec0c55a34561126e354959578d38e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interfaceAddress6", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mtu")
    def mtu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mtu"))

    @mtu.setter
    def mtu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6079e685bc786341c19766b069c76c544a46869054a1c3e8cf041a6ae8317c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mtu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c3d7c42f27ff48a7f4b7861e64ea8ea421e7040d31ad6dd12d21908a6aa1b5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3bef542a8ce75986c9787f6df98634caed4ff6096f70225e9dc60cea9e5d444)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicWanGreTunnel.MagicWanGreTunnelConfig",
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
        "cloudflare_gre_endpoint": "cloudflareGreEndpoint",
        "customer_gre_endpoint": "customerGreEndpoint",
        "interface_address": "interfaceAddress",
        "name": "name",
        "description": "description",
        "health_check": "healthCheck",
        "interface_address6": "interfaceAddress6",
        "mtu": "mtu",
        "ttl": "ttl",
    },
)
class MagicWanGreTunnelConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cloudflare_gre_endpoint: builtins.str,
        customer_gre_endpoint: builtins.str,
        interface_address: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        health_check: typing.Optional[typing.Union["MagicWanGreTunnelHealthCheck", typing.Dict[builtins.str, typing.Any]]] = None,
        interface_address6: typing.Optional[builtins.str] = None,
        mtu: typing.Optional[jsii.Number] = None,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#account_id MagicWanGreTunnel#account_id}
        :param cloudflare_gre_endpoint: The IP address assigned to the Cloudflare side of the GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#cloudflare_gre_endpoint MagicWanGreTunnel#cloudflare_gre_endpoint}
        :param customer_gre_endpoint: The IP address assigned to the customer side of the GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#customer_gre_endpoint MagicWanGreTunnel#customer_gre_endpoint}
        :param interface_address: A 31-bit prefix (/31 in CIDR notation) supporting two hosts, one for each side of the tunnel. Select the subnet from the following private IP space: 10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255, 192.168.0.0–192.168.255.255. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#interface_address MagicWanGreTunnel#interface_address}
        :param name: The name of the tunnel. The name cannot contain spaces or special characters, must be 15 characters or less, and cannot share a name with another GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#name MagicWanGreTunnel#name}
        :param description: An optional description of the GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#description MagicWanGreTunnel#description}
        :param health_check: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#health_check MagicWanGreTunnel#health_check}.
        :param interface_address6: A 127 bit IPV6 prefix from within the virtual_subnet6 prefix space with the address being the first IP of the subnet and not same as the address of virtual_subnet6. Eg if virtual_subnet6 is 2606:54c1:7:0:a9fe:12d2::/127 , interface_address6 could be 2606:54c1:7:0:a9fe:12d2:1:200/127 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#interface_address6 MagicWanGreTunnel#interface_address6}
        :param mtu: Maximum Transmission Unit (MTU) in bytes for the GRE tunnel. The minimum value is 576. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#mtu MagicWanGreTunnel#mtu}
        :param ttl: Time To Live (TTL) in number of hops of the GRE tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#ttl MagicWanGreTunnel#ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(health_check, dict):
            health_check = MagicWanGreTunnelHealthCheck(**health_check)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a28890a7c0624b85547ae0472bec5fd2ef6a10044c143bca94d66c8682d0a89)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument cloudflare_gre_endpoint", value=cloudflare_gre_endpoint, expected_type=type_hints["cloudflare_gre_endpoint"])
            check_type(argname="argument customer_gre_endpoint", value=customer_gre_endpoint, expected_type=type_hints["customer_gre_endpoint"])
            check_type(argname="argument interface_address", value=interface_address, expected_type=type_hints["interface_address"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument interface_address6", value=interface_address6, expected_type=type_hints["interface_address6"])
            check_type(argname="argument mtu", value=mtu, expected_type=type_hints["mtu"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "cloudflare_gre_endpoint": cloudflare_gre_endpoint,
            "customer_gre_endpoint": customer_gre_endpoint,
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
        if description is not None:
            self._values["description"] = description
        if health_check is not None:
            self._values["health_check"] = health_check
        if interface_address6 is not None:
            self._values["interface_address6"] = interface_address6
        if mtu is not None:
            self._values["mtu"] = mtu
        if ttl is not None:
            self._values["ttl"] = ttl

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#account_id MagicWanGreTunnel#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloudflare_gre_endpoint(self) -> builtins.str:
        '''The IP address assigned to the Cloudflare side of the GRE tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#cloudflare_gre_endpoint MagicWanGreTunnel#cloudflare_gre_endpoint}
        '''
        result = self._values.get("cloudflare_gre_endpoint")
        assert result is not None, "Required property 'cloudflare_gre_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def customer_gre_endpoint(self) -> builtins.str:
        '''The IP address assigned to the customer side of the GRE tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#customer_gre_endpoint MagicWanGreTunnel#customer_gre_endpoint}
        '''
        result = self._values.get("customer_gre_endpoint")
        assert result is not None, "Required property 'customer_gre_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def interface_address(self) -> builtins.str:
        '''A 31-bit prefix (/31 in CIDR notation) supporting two hosts, one for each side of the tunnel.

        Select the subnet from the following private IP space: 10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255, 192.168.0.0–192.168.255.255.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#interface_address MagicWanGreTunnel#interface_address}
        '''
        result = self._values.get("interface_address")
        assert result is not None, "Required property 'interface_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the tunnel.

        The name cannot contain spaces or special characters, must be 15 characters or less, and cannot share a name with another GRE tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#name MagicWanGreTunnel#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''An optional description of the GRE tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#description MagicWanGreTunnel#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def health_check(self) -> typing.Optional["MagicWanGreTunnelHealthCheck"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#health_check MagicWanGreTunnel#health_check}.'''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional["MagicWanGreTunnelHealthCheck"], result)

    @builtins.property
    def interface_address6(self) -> typing.Optional[builtins.str]:
        '''A 127 bit IPV6 prefix from within the virtual_subnet6 prefix space with the address being the first IP of the subnet and not same as the address of virtual_subnet6.

        Eg if virtual_subnet6 is 2606:54c1:7:0:a9fe:12d2::/127 , interface_address6 could be 2606:54c1:7:0:a9fe:12d2:1:200/127

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#interface_address6 MagicWanGreTunnel#interface_address6}
        '''
        result = self._values.get("interface_address6")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mtu(self) -> typing.Optional[jsii.Number]:
        '''Maximum Transmission Unit (MTU) in bytes for the GRE tunnel. The minimum value is 576.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#mtu MagicWanGreTunnel#mtu}
        '''
        result = self._values.get("mtu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''Time To Live (TTL) in number of hops of the GRE tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#ttl MagicWanGreTunnel#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicWanGreTunnelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicWanGreTunnel.MagicWanGreTunnelHealthCheck",
    jsii_struct_bases=[],
    name_mapping={
        "direction": "direction",
        "enabled": "enabled",
        "rate": "rate",
        "target": "target",
        "type": "type",
    },
)
class MagicWanGreTunnelHealthCheck:
    def __init__(
        self,
        *,
        direction: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        rate: typing.Optional[builtins.str] = None,
        target: typing.Optional[typing.Union["MagicWanGreTunnelHealthCheckTarget", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param direction: The direction of the flow of the healthcheck. Either unidirectional, where the probe comes to you via the tunnel and the result comes back to Cloudflare via the open Internet, or bidirectional where both the probe and result come and go via the tunnel. Available values: "unidirectional", "bidirectional". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#direction MagicWanGreTunnel#direction}
        :param enabled: Determines whether to run healthchecks for a tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#enabled MagicWanGreTunnel#enabled}
        :param rate: How frequent the health check is run. The default value is ``mid``. Available values: "low", "mid", "high". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#rate MagicWanGreTunnel#rate}
        :param target: The destination address in a request type health check. After the healthcheck is decapsulated at the customer end of the tunnel, the ICMP echo will be forwarded to this address. This field defaults to ``customer_gre_endpoint address``. This field is ignored for bidirectional healthchecks as the interface_address (not assigned to the Cloudflare side of the tunnel) is used as the target. Must be in object form if the x-magic-new-hc-target header is set to true and string form if x-magic-new-hc-target is absent or set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#target MagicWanGreTunnel#target}
        :param type: The type of healthcheck to run, reply or request. The default value is ``reply``. Available values: "reply", "request". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#type MagicWanGreTunnel#type}
        '''
        if isinstance(target, dict):
            target = MagicWanGreTunnelHealthCheckTarget(**target)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c26be87d4b18a8d891c4581e9e418e78835382f807b817819f52fa9c1ea0985)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#direction MagicWanGreTunnel#direction}
        '''
        result = self._values.get("direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines whether to run healthchecks for a tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#enabled MagicWanGreTunnel#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def rate(self) -> typing.Optional[builtins.str]:
        '''How frequent the health check is run. The default value is ``mid``. Available values: "low", "mid", "high".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#rate MagicWanGreTunnel#rate}
        '''
        result = self._values.get("rate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional["MagicWanGreTunnelHealthCheckTarget"]:
        '''The destination address in a request type health check.

        After the healthcheck is decapsulated at the customer end of the tunnel, the ICMP echo will be forwarded to this address. This field defaults to ``customer_gre_endpoint address``. This field is ignored for bidirectional healthchecks as the interface_address (not assigned to the Cloudflare side of the tunnel) is used as the target. Must be in object form if the x-magic-new-hc-target header is set to true and string form if x-magic-new-hc-target is absent or set to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#target MagicWanGreTunnel#target}
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional["MagicWanGreTunnelHealthCheckTarget"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of healthcheck to run, reply or request. The default value is ``reply``. Available values: "reply", "request".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#type MagicWanGreTunnel#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicWanGreTunnelHealthCheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicWanGreTunnelHealthCheckOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicWanGreTunnel.MagicWanGreTunnelHealthCheckOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8dbdd18ed3a96fddb705a46e6a40c7ed05502a19c61f000e2b7c50b939dd6413)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTarget")
    def put_target(self, *, saved: typing.Optional[builtins.str] = None) -> None:
        '''
        :param saved: The saved health check target. Setting the value to the empty string indicates that the calculated default value will be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#saved MagicWanGreTunnel#saved}
        '''
        value = MagicWanGreTunnelHealthCheckTarget(saved=saved)

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
    def target(self) -> "MagicWanGreTunnelHealthCheckTargetOutputReference":
        return typing.cast("MagicWanGreTunnelHealthCheckTargetOutputReference", jsii.get(self, "target"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicWanGreTunnelHealthCheckTarget"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicWanGreTunnelHealthCheckTarget"]], jsii.get(self, "targetInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__4129e5162cd62c437f6d4162270c1f0a2604d46bcd2463c29bac809fc2b6c8df)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00576839205ce251908d1c76b6dfc380ac3fd657ca64be4fa8215595ef91662c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rate")
    def rate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rate"))

    @rate.setter
    def rate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ed2d438f01ddefe7dd3f06d9ef2f48d41334bbb9815232870f8977670579953)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f8bd5f8f7e482e9ee87b53b0b9d7324e9ac5138a6c7868c41ad5b7779296db0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanGreTunnelHealthCheck]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanGreTunnelHealthCheck]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanGreTunnelHealthCheck]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac2258f75969ec954a5ebc2cb2f337c6183bcd3676703a99bc5580723a6362f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicWanGreTunnel.MagicWanGreTunnelHealthCheckTarget",
    jsii_struct_bases=[],
    name_mapping={"saved": "saved"},
)
class MagicWanGreTunnelHealthCheckTarget:
    def __init__(self, *, saved: typing.Optional[builtins.str] = None) -> None:
        '''
        :param saved: The saved health check target. Setting the value to the empty string indicates that the calculated default value will be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#saved MagicWanGreTunnel#saved}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9971fe48143664d08b4fb425d027ee4af6ff04e981d4dd8919d02daac6a75dc4)
            check_type(argname="argument saved", value=saved, expected_type=type_hints["saved"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if saved is not None:
            self._values["saved"] = saved

    @builtins.property
    def saved(self) -> typing.Optional[builtins.str]:
        '''The saved health check target.

        Setting the value to the empty string indicates that the calculated default value will be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_wan_gre_tunnel#saved MagicWanGreTunnel#saved}
        '''
        result = self._values.get("saved")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicWanGreTunnelHealthCheckTarget(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicWanGreTunnelHealthCheckTargetOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicWanGreTunnel.MagicWanGreTunnelHealthCheckTargetOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e6ac6b1f3369efdcff0a522a71125d718980bf87fa1cf32d5da68db6b9d9338)
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
            type_hints = typing.get_type_hints(_typecheckingstub__172646462725aff0e8332fadf650b37eed48566c821ade3a6d4e5e2b8d118ccb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "saved", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanGreTunnelHealthCheckTarget]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanGreTunnelHealthCheckTarget]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanGreTunnelHealthCheckTarget]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e4cd75a14e172822df0153d1fef55e6b55bdd0325d6aca879995fb115520034)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "MagicWanGreTunnel",
    "MagicWanGreTunnelConfig",
    "MagicWanGreTunnelHealthCheck",
    "MagicWanGreTunnelHealthCheckOutputReference",
    "MagicWanGreTunnelHealthCheckTarget",
    "MagicWanGreTunnelHealthCheckTargetOutputReference",
]

publication.publish()

def _typecheckingstub__021afd1f2c9cb9ab09f14b2d262952d61c6e756ea4255b9a67adb055618108e2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    cloudflare_gre_endpoint: builtins.str,
    customer_gre_endpoint: builtins.str,
    interface_address: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    health_check: typing.Optional[typing.Union[MagicWanGreTunnelHealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    interface_address6: typing.Optional[builtins.str] = None,
    mtu: typing.Optional[jsii.Number] = None,
    ttl: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__4d06765414224d7bc61fe6d40b3b81f240d21918cdba8abab53e60a284631d83(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2db28b4e981fa051508c13afaf6a949c902dd1add99ee4c55d250533385eec2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5fa4d5dc3a09a2f5653a16454dc03bba6f5025662d55c83d2b6b5d88df7f4d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0fd5e1fc7a3f682f42edd242ca24988df279a237a90aca74916b3df4dd255d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a186c09b75b28850c1fac3461e701050407f01e152c3452c139303aa825fef5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e31573ce91993487a57e216616804ec1c2b011954ebe5156b23dd8209b22e68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffa9b0dbe3525c930820f7f88e009f98d74ec0c55a34561126e354959578d38e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6079e685bc786341c19766b069c76c544a46869054a1c3e8cf041a6ae8317c5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c3d7c42f27ff48a7f4b7861e64ea8ea421e7040d31ad6dd12d21908a6aa1b5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3bef542a8ce75986c9787f6df98634caed4ff6096f70225e9dc60cea9e5d444(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a28890a7c0624b85547ae0472bec5fd2ef6a10044c143bca94d66c8682d0a89(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    cloudflare_gre_endpoint: builtins.str,
    customer_gre_endpoint: builtins.str,
    interface_address: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    health_check: typing.Optional[typing.Union[MagicWanGreTunnelHealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    interface_address6: typing.Optional[builtins.str] = None,
    mtu: typing.Optional[jsii.Number] = None,
    ttl: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c26be87d4b18a8d891c4581e9e418e78835382f807b817819f52fa9c1ea0985(
    *,
    direction: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    rate: typing.Optional[builtins.str] = None,
    target: typing.Optional[typing.Union[MagicWanGreTunnelHealthCheckTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dbdd18ed3a96fddb705a46e6a40c7ed05502a19c61f000e2b7c50b939dd6413(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4129e5162cd62c437f6d4162270c1f0a2604d46bcd2463c29bac809fc2b6c8df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00576839205ce251908d1c76b6dfc380ac3fd657ca64be4fa8215595ef91662c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ed2d438f01ddefe7dd3f06d9ef2f48d41334bbb9815232870f8977670579953(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f8bd5f8f7e482e9ee87b53b0b9d7324e9ac5138a6c7868c41ad5b7779296db0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac2258f75969ec954a5ebc2cb2f337c6183bcd3676703a99bc5580723a6362f5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanGreTunnelHealthCheck]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9971fe48143664d08b4fb425d027ee4af6ff04e981d4dd8919d02daac6a75dc4(
    *,
    saved: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e6ac6b1f3369efdcff0a522a71125d718980bf87fa1cf32d5da68db6b9d9338(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__172646462725aff0e8332fadf650b37eed48566c821ade3a6d4e5e2b8d118ccb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e4cd75a14e172822df0153d1fef55e6b55bdd0325d6aca879995fb115520034(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicWanGreTunnelHealthCheckTarget]],
) -> None:
    """Type checking stubs"""
    pass
