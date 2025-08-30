r'''
# `cloudflare_zero_trust_dns_location`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_dns_location`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location).
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


class ZeroTrustDnsLocation(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocation",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location cloudflare_zero_trust_dns_location}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        name: builtins.str,
        client_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dns_destination_ips_id: typing.Optional[builtins.str] = None,
        ecs_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        endpoints: typing.Optional[typing.Union["ZeroTrustDnsLocationEndpoints", typing.Dict[builtins.str, typing.Any]]] = None,
        networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDnsLocationNetworks", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location cloudflare_zero_trust_dns_location} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#account_id ZeroTrustDnsLocation#account_id}.
        :param name: The name of the location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#name ZeroTrustDnsLocation#name}
        :param client_default: True if the location is the default location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#client_default ZeroTrustDnsLocation#client_default}
        :param dns_destination_ips_id: The identifier of the pair of IPv4 addresses assigned to this location. When creating a location, if this field is absent or set with null, the pair of shared IPv4 addresses (0e4a32c6-6fb8-4858-9296-98f51631e8e6) is auto-assigned. When updating a location, if the field is absent or set with null, the pre-assigned pair remains unchanged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#dns_destination_ips_id ZeroTrustDnsLocation#dns_destination_ips_id}
        :param ecs_support: True if the location needs to resolve EDNS queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#ecs_support ZeroTrustDnsLocation#ecs_support}
        :param endpoints: The destination endpoints configured for this location. When updating a location, if this field is absent or set with null, the endpoints configuration remains unchanged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#endpoints ZeroTrustDnsLocation#endpoints}
        :param networks: A list of network ranges that requests from this location would originate from. A non-empty list is only effective if the ipv4 endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8378e43d896096705cac4de6b885b2a7feba340a7c77345eeb5367167ab96139)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustDnsLocationConfig(
            account_id=account_id,
            name=name,
            client_default=client_default,
            dns_destination_ips_id=dns_destination_ips_id,
            ecs_support=ecs_support,
            endpoints=endpoints,
            networks=networks,
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
        '''Generates CDKTF code for importing a ZeroTrustDnsLocation resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustDnsLocation to import.
        :param import_from_id: The id of the existing ZeroTrustDnsLocation that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustDnsLocation to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35c955cf1376901d6ec94078a0be1951af4d12730c0404fc1f6374d87e3ac113)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEndpoints")
    def put_endpoints(
        self,
        *,
        doh: typing.Union["ZeroTrustDnsLocationEndpointsDoh", typing.Dict[builtins.str, typing.Any]],
        dot: typing.Union["ZeroTrustDnsLocationEndpointsDot", typing.Dict[builtins.str, typing.Any]],
        ipv4: typing.Union["ZeroTrustDnsLocationEndpointsIpv4", typing.Dict[builtins.str, typing.Any]],
        ipv6: typing.Union["ZeroTrustDnsLocationEndpointsIpv6", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param doh: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#doh ZeroTrustDnsLocation#doh}.
        :param dot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#dot ZeroTrustDnsLocation#dot}.
        :param ipv4: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#ipv4 ZeroTrustDnsLocation#ipv4}.
        :param ipv6: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#ipv6 ZeroTrustDnsLocation#ipv6}.
        '''
        value = ZeroTrustDnsLocationEndpoints(doh=doh, dot=dot, ipv4=ipv4, ipv6=ipv6)

        return typing.cast(None, jsii.invoke(self, "putEndpoints", [value]))

    @jsii.member(jsii_name="putNetworks")
    def put_networks(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDnsLocationNetworks", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31b0ab08dd1cb9f6cb7b2901a64958683fcf5a888f22543401cea5a83a3b9db2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworks", [value]))

    @jsii.member(jsii_name="resetClientDefault")
    def reset_client_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientDefault", []))

    @jsii.member(jsii_name="resetDnsDestinationIpsId")
    def reset_dns_destination_ips_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsDestinationIpsId", []))

    @jsii.member(jsii_name="resetEcsSupport")
    def reset_ecs_support(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEcsSupport", []))

    @jsii.member(jsii_name="resetEndpoints")
    def reset_endpoints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoints", []))

    @jsii.member(jsii_name="resetNetworks")
    def reset_networks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworks", []))

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
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="dnsDestinationIpv6BlockId")
    def dns_destination_ipv6_block_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsDestinationIpv6BlockId"))

    @builtins.property
    @jsii.member(jsii_name="dohSubdomain")
    def doh_subdomain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dohSubdomain"))

    @builtins.property
    @jsii.member(jsii_name="endpoints")
    def endpoints(self) -> "ZeroTrustDnsLocationEndpointsOutputReference":
        return typing.cast("ZeroTrustDnsLocationEndpointsOutputReference", jsii.get(self, "endpoints"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipv4Destination")
    def ipv4_destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Destination"))

    @builtins.property
    @jsii.member(jsii_name="ipv4DestinationBackup")
    def ipv4_destination_backup(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4DestinationBackup"))

    @builtins.property
    @jsii.member(jsii_name="networks")
    def networks(self) -> "ZeroTrustDnsLocationNetworksList":
        return typing.cast("ZeroTrustDnsLocationNetworksList", jsii.get(self, "networks"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientDefaultInput")
    def client_default_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "clientDefaultInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsDestinationIpsIdInput")
    def dns_destination_ips_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dnsDestinationIpsIdInput"))

    @builtins.property
    @jsii.member(jsii_name="ecsSupportInput")
    def ecs_support_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ecsSupportInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointsInput")
    def endpoints_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustDnsLocationEndpoints"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustDnsLocationEndpoints"]], jsii.get(self, "endpointsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networksInput")
    def networks_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationNetworks"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationNetworks"]]], jsii.get(self, "networksInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18cf59cb0f41ff40ba1c73e6548e0fd53bde676991f030bb16d3a8ec4c90bdfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientDefault")
    def client_default(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "clientDefault"))

    @client_default.setter
    def client_default(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__526385fabd180e99f8dea808cb996d391efc0a2a559ba5b936cf9a3d4d004cde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientDefault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dnsDestinationIpsId")
    def dns_destination_ips_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsDestinationIpsId"))

    @dns_destination_ips_id.setter
    def dns_destination_ips_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb951972827eb8db7bc7137940ad839fd2a6f6eb0a71391d3f76975d6d8f480c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsDestinationIpsId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ecsSupport")
    def ecs_support(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ecsSupport"))

    @ecs_support.setter
    def ecs_support(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07ffd1c69795e459c4ebe5ae4e12e77a6cea6ddffefd5313dec10d0639b4e6ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ecsSupport", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86d4061d933b5cf045685b41593907e46c00ea42ac51f76e057d2a03a123f48d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationConfig",
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
        "name": "name",
        "client_default": "clientDefault",
        "dns_destination_ips_id": "dnsDestinationIpsId",
        "ecs_support": "ecsSupport",
        "endpoints": "endpoints",
        "networks": "networks",
    },
)
class ZeroTrustDnsLocationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        client_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dns_destination_ips_id: typing.Optional[builtins.str] = None,
        ecs_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        endpoints: typing.Optional[typing.Union["ZeroTrustDnsLocationEndpoints", typing.Dict[builtins.str, typing.Any]]] = None,
        networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDnsLocationNetworks", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#account_id ZeroTrustDnsLocation#account_id}.
        :param name: The name of the location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#name ZeroTrustDnsLocation#name}
        :param client_default: True if the location is the default location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#client_default ZeroTrustDnsLocation#client_default}
        :param dns_destination_ips_id: The identifier of the pair of IPv4 addresses assigned to this location. When creating a location, if this field is absent or set with null, the pair of shared IPv4 addresses (0e4a32c6-6fb8-4858-9296-98f51631e8e6) is auto-assigned. When updating a location, if the field is absent or set with null, the pre-assigned pair remains unchanged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#dns_destination_ips_id ZeroTrustDnsLocation#dns_destination_ips_id}
        :param ecs_support: True if the location needs to resolve EDNS queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#ecs_support ZeroTrustDnsLocation#ecs_support}
        :param endpoints: The destination endpoints configured for this location. When updating a location, if this field is absent or set with null, the endpoints configuration remains unchanged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#endpoints ZeroTrustDnsLocation#endpoints}
        :param networks: A list of network ranges that requests from this location would originate from. A non-empty list is only effective if the ipv4 endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(endpoints, dict):
            endpoints = ZeroTrustDnsLocationEndpoints(**endpoints)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70d62cfd505aea7c51923de8211dea9db41d655c0107ed143af4f3209526cc63)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument client_default", value=client_default, expected_type=type_hints["client_default"])
            check_type(argname="argument dns_destination_ips_id", value=dns_destination_ips_id, expected_type=type_hints["dns_destination_ips_id"])
            check_type(argname="argument ecs_support", value=ecs_support, expected_type=type_hints["ecs_support"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
            check_type(argname="argument networks", value=networks, expected_type=type_hints["networks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
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
        if client_default is not None:
            self._values["client_default"] = client_default
        if dns_destination_ips_id is not None:
            self._values["dns_destination_ips_id"] = dns_destination_ips_id
        if ecs_support is not None:
            self._values["ecs_support"] = ecs_support
        if endpoints is not None:
            self._values["endpoints"] = endpoints
        if networks is not None:
            self._values["networks"] = networks

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#account_id ZeroTrustDnsLocation#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#name ZeroTrustDnsLocation#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_default(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the location is the default location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#client_default ZeroTrustDnsLocation#client_default}
        '''
        result = self._values.get("client_default")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dns_destination_ips_id(self) -> typing.Optional[builtins.str]:
        '''The identifier of the pair of IPv4 addresses assigned to this location.

        When creating a location, if this field is absent or set with null, the pair of shared IPv4 addresses (0e4a32c6-6fb8-4858-9296-98f51631e8e6) is auto-assigned. When updating a location, if the field is absent or set with null, the pre-assigned pair remains unchanged.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#dns_destination_ips_id ZeroTrustDnsLocation#dns_destination_ips_id}
        '''
        result = self._values.get("dns_destination_ips_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecs_support(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the location needs to resolve EDNS queries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#ecs_support ZeroTrustDnsLocation#ecs_support}
        '''
        result = self._values.get("ecs_support")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def endpoints(self) -> typing.Optional["ZeroTrustDnsLocationEndpoints"]:
        '''The destination endpoints configured for this location.

        When updating a location, if this field is absent or set with null, the endpoints configuration remains unchanged.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#endpoints ZeroTrustDnsLocation#endpoints}
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional["ZeroTrustDnsLocationEndpoints"], result)

    @builtins.property
    def networks(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationNetworks"]]]:
        '''A list of network ranges that requests from this location would originate from.

        A non-empty list is only effective if the ipv4 endpoint is enabled for this location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        '''
        result = self._values.get("networks")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationNetworks"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpoints",
    jsii_struct_bases=[],
    name_mapping={"doh": "doh", "dot": "dot", "ipv4": "ipv4", "ipv6": "ipv6"},
)
class ZeroTrustDnsLocationEndpoints:
    def __init__(
        self,
        *,
        doh: typing.Union["ZeroTrustDnsLocationEndpointsDoh", typing.Dict[builtins.str, typing.Any]],
        dot: typing.Union["ZeroTrustDnsLocationEndpointsDot", typing.Dict[builtins.str, typing.Any]],
        ipv4: typing.Union["ZeroTrustDnsLocationEndpointsIpv4", typing.Dict[builtins.str, typing.Any]],
        ipv6: typing.Union["ZeroTrustDnsLocationEndpointsIpv6", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param doh: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#doh ZeroTrustDnsLocation#doh}.
        :param dot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#dot ZeroTrustDnsLocation#dot}.
        :param ipv4: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#ipv4 ZeroTrustDnsLocation#ipv4}.
        :param ipv6: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#ipv6 ZeroTrustDnsLocation#ipv6}.
        '''
        if isinstance(doh, dict):
            doh = ZeroTrustDnsLocationEndpointsDoh(**doh)
        if isinstance(dot, dict):
            dot = ZeroTrustDnsLocationEndpointsDot(**dot)
        if isinstance(ipv4, dict):
            ipv4 = ZeroTrustDnsLocationEndpointsIpv4(**ipv4)
        if isinstance(ipv6, dict):
            ipv6 = ZeroTrustDnsLocationEndpointsIpv6(**ipv6)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e70d2f8ee02b6fff75773ed2a1f68870de72c3a54ea4f8e8d3b7c6084dc3da5d)
            check_type(argname="argument doh", value=doh, expected_type=type_hints["doh"])
            check_type(argname="argument dot", value=dot, expected_type=type_hints["dot"])
            check_type(argname="argument ipv4", value=ipv4, expected_type=type_hints["ipv4"])
            check_type(argname="argument ipv6", value=ipv6, expected_type=type_hints["ipv6"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "doh": doh,
            "dot": dot,
            "ipv4": ipv4,
            "ipv6": ipv6,
        }

    @builtins.property
    def doh(self) -> "ZeroTrustDnsLocationEndpointsDoh":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#doh ZeroTrustDnsLocation#doh}.'''
        result = self._values.get("doh")
        assert result is not None, "Required property 'doh' is missing"
        return typing.cast("ZeroTrustDnsLocationEndpointsDoh", result)

    @builtins.property
    def dot(self) -> "ZeroTrustDnsLocationEndpointsDot":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#dot ZeroTrustDnsLocation#dot}.'''
        result = self._values.get("dot")
        assert result is not None, "Required property 'dot' is missing"
        return typing.cast("ZeroTrustDnsLocationEndpointsDot", result)

    @builtins.property
    def ipv4(self) -> "ZeroTrustDnsLocationEndpointsIpv4":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#ipv4 ZeroTrustDnsLocation#ipv4}.'''
        result = self._values.get("ipv4")
        assert result is not None, "Required property 'ipv4' is missing"
        return typing.cast("ZeroTrustDnsLocationEndpointsIpv4", result)

    @builtins.property
    def ipv6(self) -> "ZeroTrustDnsLocationEndpointsIpv6":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#ipv6 ZeroTrustDnsLocation#ipv6}.'''
        result = self._values.get("ipv6")
        assert result is not None, "Required property 'ipv6' is missing"
        return typing.cast("ZeroTrustDnsLocationEndpointsIpv6", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDoh",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "networks": "networks",
        "require_token": "requireToken",
    },
)
class ZeroTrustDnsLocationEndpointsDoh:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDnsLocationEndpointsDohNetworks", typing.Dict[builtins.str, typing.Any]]]]] = None,
        require_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: True if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        :param networks: A list of allowed source IP network ranges for this endpoint. When empty, all source IPs are allowed. A non-empty list is only effective if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        :param require_token: True if the endpoint requires `user identity <https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/agentless/dns/dns-over-https/#filter-doh-requests-by-user>`_ authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#require_token ZeroTrustDnsLocation#require_token}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4253f80e5288447807b06bdfe765bdf363868a147e617ea71781286e633c7a2a)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument networks", value=networks, expected_type=type_hints["networks"])
            check_type(argname="argument require_token", value=require_token, expected_type=type_hints["require_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if networks is not None:
            self._values["networks"] = networks
        if require_token is not None:
            self._values["require_token"] = require_token

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the endpoint is enabled for this location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def networks(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationEndpointsDohNetworks"]]]:
        '''A list of allowed source IP network ranges for this endpoint.

        When empty, all source IPs are allowed. A non-empty list is only effective if the endpoint is enabled for this location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        '''
        result = self._values.get("networks")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationEndpointsDohNetworks"]]], result)

    @builtins.property
    def require_token(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the endpoint requires `user identity <https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/agentless/dns/dns-over-https/#filter-doh-requests-by-user>`_ authentication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#require_token ZeroTrustDnsLocation#require_token}
        '''
        result = self._values.get("require_token")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationEndpointsDoh(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDohNetworks",
    jsii_struct_bases=[],
    name_mapping={"network": "network"},
)
class ZeroTrustDnsLocationEndpointsDohNetworks:
    def __init__(self, *, network: builtins.str) -> None:
        '''
        :param network: The IP address or IP CIDR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#network ZeroTrustDnsLocation#network}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c4d214264ac7bf7633e699229b367d8100e53965aed5e8b0e891d73a2514a65)
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network": network,
        }

    @builtins.property
    def network(self) -> builtins.str:
        '''The IP address or IP CIDR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#network ZeroTrustDnsLocation#network}
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationEndpointsDohNetworks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDnsLocationEndpointsDohNetworksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDohNetworksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2388d58fe047cc80d55af1995fced1a6c7c7c6f0bf3d0f8ada725361b80d6caa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDnsLocationEndpointsDohNetworksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcd54ecc486d6b45db6b65455f144b573dc99635e2dc61197c8125064cd98cb4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDnsLocationEndpointsDohNetworksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71d69426d1fdadcf2c488d33c1fdcfeab14904595d1ba0efcd26734bbb63ebbe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a123d83fa5a82cd86a98dbd6e320ef94ff0627cfac67453a3015d765e4f62d92)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b8732d504a86bba8a0349cdd90a7f054b6479c99fac775c3f69e672523b16655)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDohNetworks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDohNetworks]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDohNetworks]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc14e9b4a01b11552ce4ac0b0c06fc2c6884057188cfc4623f7c48200169565d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDnsLocationEndpointsDohNetworksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDohNetworksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__15dc685461b9a3cb25825f45e77fce11ae067a3faa7657f4543750c7aa3a70fa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1d9faef4d3246c5b7a2f1269894e65bced30c674f6f1951817bd445945d0dce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDohNetworks]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDohNetworks]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDohNetworks]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e86cb5569771f40246a5704dd74bd32fb07c05b1596d883eb17f8ee65550d6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDnsLocationEndpointsDohOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDohOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__60be59199eae99d956e7dd77141d9674b1a60fb2df0765212fc7f643393ad409)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNetworks")
    def put_networks(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsDohNetworks, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cbd64cd0ee2f9c8f8426ab5943c036ebfaba935d721f3bb883feb0774c88c62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworks", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetNetworks")
    def reset_networks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworks", []))

    @jsii.member(jsii_name="resetRequireToken")
    def reset_require_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireToken", []))

    @builtins.property
    @jsii.member(jsii_name="networks")
    def networks(self) -> ZeroTrustDnsLocationEndpointsDohNetworksList:
        return typing.cast(ZeroTrustDnsLocationEndpointsDohNetworksList, jsii.get(self, "networks"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="networksInput")
    def networks_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDohNetworks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDohNetworks]]], jsii.get(self, "networksInput"))

    @builtins.property
    @jsii.member(jsii_name="requireTokenInput")
    def require_token_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requireTokenInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__6e2a73d45560cc38fad7f0667fec9d9e45ae5c78324bd8d5e3cb523846f45e99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requireToken")
    def require_token(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "requireToken"))

    @require_token.setter
    def require_token(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62daca8dea324327efefd80ba1c52b27a709f320863ae1414b35d24ccb35e3e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDoh]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDoh]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDoh]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7415134ac78ce1bf05e33a7a05ebcfa0b36955db58ddf220c96badcf7c9e36d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDot",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "networks": "networks"},
)
class ZeroTrustDnsLocationEndpointsDot:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDnsLocationEndpointsDotNetworks", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param enabled: True if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        :param networks: A list of allowed source IP network ranges for this endpoint. When empty, all source IPs are allowed. A non-empty list is only effective if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04abb288965df336321473fe7f5d9d660bd869f1c5ae38f663be2ed7e0661044)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument networks", value=networks, expected_type=type_hints["networks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if networks is not None:
            self._values["networks"] = networks

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the endpoint is enabled for this location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def networks(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationEndpointsDotNetworks"]]]:
        '''A list of allowed source IP network ranges for this endpoint.

        When empty, all source IPs are allowed. A non-empty list is only effective if the endpoint is enabled for this location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        '''
        result = self._values.get("networks")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationEndpointsDotNetworks"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationEndpointsDot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDotNetworks",
    jsii_struct_bases=[],
    name_mapping={"network": "network"},
)
class ZeroTrustDnsLocationEndpointsDotNetworks:
    def __init__(self, *, network: builtins.str) -> None:
        '''
        :param network: The IP address or IP CIDR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#network ZeroTrustDnsLocation#network}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41dc8364a862b2bc88832b9187690ede9828c6fbfe06786e3ae49fc3d8b0d0ea)
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network": network,
        }

    @builtins.property
    def network(self) -> builtins.str:
        '''The IP address or IP CIDR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#network ZeroTrustDnsLocation#network}
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationEndpointsDotNetworks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDnsLocationEndpointsDotNetworksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDotNetworksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2991a85049ffb751c76018da9a08cbf40b0233a61a9b465e4eef995393ba0cd4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDnsLocationEndpointsDotNetworksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3abab34a516a463076c64b7b7e5774853768421cf11fb0de0911980f3fa94210)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDnsLocationEndpointsDotNetworksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53f5d1a0d5f14d25854af22cd2a0f59b1f6928c5375c4b18f7c077325ce29ee0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__373176233e21c63d9a550d4ef82f8e8191f34aaef151ef7d00b4b65ca93ff5d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__306b3af8ed13815f4b21d432f3b868d70524e6ae5995646242c46a544a94e83f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDotNetworks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDotNetworks]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDotNetworks]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__decb8e031c3cbd738b2b3c8e4ac852e3d1f9ace65adc87ceadaff7898da0004c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDnsLocationEndpointsDotNetworksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDotNetworksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8e76f540888368f08d4c1a73c49b912cb228af4c842421a1d7dd842815fb692)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5660f7a17ed2cde22f6340943dbaaf344ce24c427afd314d869733674af67b44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDotNetworks]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDotNetworks]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDotNetworks]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e17d9a10567384e0302966e8dcc010346e810009a5a260b5152bea591f0c442)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDnsLocationEndpointsDotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsDotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e86b4d97ad9c1ecf49f3d97ea662d8d002d7abea31a3f27a3e02b3313468b6b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNetworks")
    def put_networks(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsDotNetworks, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46a31f7312160b5dbed67be049a22e0bd736a8b406c22f3cb9a79064a9e1e2fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworks", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetNetworks")
    def reset_networks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworks", []))

    @builtins.property
    @jsii.member(jsii_name="networks")
    def networks(self) -> ZeroTrustDnsLocationEndpointsDotNetworksList:
        return typing.cast(ZeroTrustDnsLocationEndpointsDotNetworksList, jsii.get(self, "networks"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="networksInput")
    def networks_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDotNetworks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDotNetworks]]], jsii.get(self, "networksInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__631570046b5f7a355aee6ae51ec56ca7fba8cc91dff1f2de69ad2334162f39c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDot]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDot]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDot]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d90b7eae7fd41b0d2b20e2ff35f1cc8560c82737c6c42af138a266f47dd534ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsIpv4",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ZeroTrustDnsLocationEndpointsIpv4:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: True if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3ee05223720f07592d8c29b79d08e1cb50a47106a990ab44d1b7a9858d5fa3f)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the endpoint is enabled for this location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationEndpointsIpv4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDnsLocationEndpointsIpv4OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsIpv4OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6d86a3e71b21cc7c7b8b607dea66e3fe6438732c87299107cad26b884bd43de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__506438d9b0a793bafcb5ecaf6317c11639596d6c0a0c72227ffa16ed9e4c1c1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv4]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv4]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv4]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41cea4f15fa93a21898199c675f9f683d84c61649dd0d728d77c3ab11896accf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsIpv6",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "networks": "networks"},
)
class ZeroTrustDnsLocationEndpointsIpv6:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDnsLocationEndpointsIpv6Networks", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param enabled: True if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        :param networks: A list of allowed source IPv6 network ranges for this endpoint. When empty, all source IPs are allowed. A non-empty list is only effective if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__508e1ec3c41192e3b5430038d8a13656345832c17781c8cccb9c0d28801271b3)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument networks", value=networks, expected_type=type_hints["networks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if networks is not None:
            self._values["networks"] = networks

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the endpoint is enabled for this location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def networks(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationEndpointsIpv6Networks"]]]:
        '''A list of allowed source IPv6 network ranges for this endpoint.

        When empty, all source IPs are allowed. A non-empty list is only effective if the endpoint is enabled for this location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        '''
        result = self._values.get("networks")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDnsLocationEndpointsIpv6Networks"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationEndpointsIpv6(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsIpv6Networks",
    jsii_struct_bases=[],
    name_mapping={"network": "network"},
)
class ZeroTrustDnsLocationEndpointsIpv6Networks:
    def __init__(self, *, network: builtins.str) -> None:
        '''
        :param network: The IPv6 address or IPv6 CIDR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#network ZeroTrustDnsLocation#network}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8d6a5eaf0ac668bcacbd9669ded172dfef1dc583ba8979fe1b03da8a5c1b3f8)
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network": network,
        }

    @builtins.property
    def network(self) -> builtins.str:
        '''The IPv6 address or IPv6 CIDR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#network ZeroTrustDnsLocation#network}
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationEndpointsIpv6Networks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDnsLocationEndpointsIpv6NetworksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsIpv6NetworksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3af7148a7fc5e5c181d25aaa456da0e55d878e546bcdcff3b09745a557d8da79)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDnsLocationEndpointsIpv6NetworksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c229086fe465e429651dfed54e13ee595b30d05094e3c82ad72c74a92b64fa11)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDnsLocationEndpointsIpv6NetworksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43cd8ba669d452a6f92278dc8598f3cdd48e343cec96b64a5443e6e779926398)
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
            type_hints = typing.get_type_hints(_typecheckingstub__534b9c794a257fcbb5a9667ed90cd4481e5c6697ccca7902d61115bd3f830a02)
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
            type_hints = typing.get_type_hints(_typecheckingstub__883259513fda8e07c1fbf5fc855ddfd9ceeb1508235c83e35e814f39c6f17688)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsIpv6Networks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsIpv6Networks]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsIpv6Networks]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21f81f6a8602ab8875f877c03763e105176c3095292b43d007316360d80ee4a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDnsLocationEndpointsIpv6NetworksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsIpv6NetworksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__08b62548f4d78e9f1585624a1033e7f2fae829a6895fd4f3c2b7eddeae917389)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7b50d8cc3406900b1a666865fbba8e74a7c88825e3763c6cdc4c8152de5f617)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6Networks]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6Networks]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6Networks]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c24a9b996614bbaa76b18fc6af0a2f65f61eb47da804771e5a8e595236c1a277)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDnsLocationEndpointsIpv6OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsIpv6OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c6f6f2698ea8e42051b245a6cb78210c6d820705702b2f145e287e2e3fd02cad)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNetworks")
    def put_networks(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsIpv6Networks, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cf644dc3ad699982774b092f5eb901c80864d9e5963d1391c474e512b9fc87a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworks", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetNetworks")
    def reset_networks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworks", []))

    @builtins.property
    @jsii.member(jsii_name="networks")
    def networks(self) -> ZeroTrustDnsLocationEndpointsIpv6NetworksList:
        return typing.cast(ZeroTrustDnsLocationEndpointsIpv6NetworksList, jsii.get(self, "networks"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="networksInput")
    def networks_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsIpv6Networks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsIpv6Networks]]], jsii.get(self, "networksInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__0abc77ad4f83c2ce5098452c22c2bf6bb27f3fb7e73a62f579e7a40911705da7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93c84cfc9caa75b8fdd601ce41adfaed3d2e3f13e93eebd0637728c91329e3c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDnsLocationEndpointsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationEndpointsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb4647d3d58ce6b2f9e08a350b658ef7f4a18af3d29540feb72689c22571efbd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDoh")
    def put_doh(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsDohNetworks, typing.Dict[builtins.str, typing.Any]]]]] = None,
        require_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: True if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        :param networks: A list of allowed source IP network ranges for this endpoint. When empty, all source IPs are allowed. A non-empty list is only effective if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        :param require_token: True if the endpoint requires `user identity <https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/agentless/dns/dns-over-https/#filter-doh-requests-by-user>`_ authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#require_token ZeroTrustDnsLocation#require_token}
        '''
        value = ZeroTrustDnsLocationEndpointsDoh(
            enabled=enabled, networks=networks, require_token=require_token
        )

        return typing.cast(None, jsii.invoke(self, "putDoh", [value]))

    @jsii.member(jsii_name="putDot")
    def put_dot(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsDotNetworks, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param enabled: True if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        :param networks: A list of allowed source IP network ranges for this endpoint. When empty, all source IPs are allowed. A non-empty list is only effective if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        '''
        value = ZeroTrustDnsLocationEndpointsDot(enabled=enabled, networks=networks)

        return typing.cast(None, jsii.invoke(self, "putDot", [value]))

    @jsii.member(jsii_name="putIpv4")
    def put_ipv4(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: True if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        '''
        value = ZeroTrustDnsLocationEndpointsIpv4(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putIpv4", [value]))

    @jsii.member(jsii_name="putIpv6")
    def put_ipv6(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsIpv6Networks, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param enabled: True if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#enabled ZeroTrustDnsLocation#enabled}
        :param networks: A list of allowed source IPv6 network ranges for this endpoint. When empty, all source IPs are allowed. A non-empty list is only effective if the endpoint is enabled for this location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#networks ZeroTrustDnsLocation#networks}
        '''
        value = ZeroTrustDnsLocationEndpointsIpv6(enabled=enabled, networks=networks)

        return typing.cast(None, jsii.invoke(self, "putIpv6", [value]))

    @builtins.property
    @jsii.member(jsii_name="doh")
    def doh(self) -> ZeroTrustDnsLocationEndpointsDohOutputReference:
        return typing.cast(ZeroTrustDnsLocationEndpointsDohOutputReference, jsii.get(self, "doh"))

    @builtins.property
    @jsii.member(jsii_name="dot")
    def dot(self) -> ZeroTrustDnsLocationEndpointsDotOutputReference:
        return typing.cast(ZeroTrustDnsLocationEndpointsDotOutputReference, jsii.get(self, "dot"))

    @builtins.property
    @jsii.member(jsii_name="ipv4")
    def ipv4(self) -> ZeroTrustDnsLocationEndpointsIpv4OutputReference:
        return typing.cast(ZeroTrustDnsLocationEndpointsIpv4OutputReference, jsii.get(self, "ipv4"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> ZeroTrustDnsLocationEndpointsIpv6OutputReference:
        return typing.cast(ZeroTrustDnsLocationEndpointsIpv6OutputReference, jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="dohInput")
    def doh_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDoh]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDoh]], jsii.get(self, "dohInput"))

    @builtins.property
    @jsii.member(jsii_name="dotInput")
    def dot_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDot]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDot]], jsii.get(self, "dotInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv4Input")
    def ipv4_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv4]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv4]], jsii.get(self, "ipv4Input"))

    @builtins.property
    @jsii.member(jsii_name="ipv6Input")
    def ipv6_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6]], jsii.get(self, "ipv6Input"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpoints]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpoints]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpoints]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fc4b48aebb26eb19289a4fa84cef7d9fe6211f4bc1edc36dbaa80d0cbd4972f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationNetworks",
    jsii_struct_bases=[],
    name_mapping={"network": "network"},
)
class ZeroTrustDnsLocationNetworks:
    def __init__(self, *, network: builtins.str) -> None:
        '''
        :param network: The IPv4 address or IPv4 CIDR. IPv4 CIDRs are limited to a maximum of /24. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#network ZeroTrustDnsLocation#network}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ab01bdc87f6e68458b4404a0e8aa63264784b6fdcc49cf045813e2254a833f1)
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network": network,
        }

    @builtins.property
    def network(self) -> builtins.str:
        '''The IPv4 address or IPv4 CIDR. IPv4 CIDRs are limited to a maximum of /24.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_dns_location#network ZeroTrustDnsLocation#network}
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDnsLocationNetworks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDnsLocationNetworksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationNetworksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__437e142a653ca6a2d055683cedf140c1cb4c7a419ddad0ecf1d84548dd85d849)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ZeroTrustDnsLocationNetworksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc5d034b597cdd438a7ecf1f99583e953da055ed42dc2a49124ef825c55e3e30)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDnsLocationNetworksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78bf3ed3c61f72b71cbd6c2efd0086b4274712c6be390fb199337fb88fef193c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__be518155031eb88ee5388525bbca42e7fd39617e06cc7f0b30d956f848782570)
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
            type_hints = typing.get_type_hints(_typecheckingstub__df1963d81c27bef5c334beb9c629c7177f7c85be35522ae91ee58f06c23dbcb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationNetworks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationNetworks]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationNetworks]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b55b96c5a9a03c03988a170169ac70b5dd590721139f542e7605aa98c88d314b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDnsLocationNetworksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDnsLocation.ZeroTrustDnsLocationNetworksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__627971a3fee5519d0c666b2634553466b601d3977ee61871e688fcb4a58dcc63)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46079daf0914220c05e95f46764e505d977bf820f9ae3b796918dd9969ae6ffc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationNetworks]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationNetworks]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationNetworks]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f5efe06c991d25cbde9f943e0e5c73d9bf143eb751f3594d588d69e67ecf191)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustDnsLocation",
    "ZeroTrustDnsLocationConfig",
    "ZeroTrustDnsLocationEndpoints",
    "ZeroTrustDnsLocationEndpointsDoh",
    "ZeroTrustDnsLocationEndpointsDohNetworks",
    "ZeroTrustDnsLocationEndpointsDohNetworksList",
    "ZeroTrustDnsLocationEndpointsDohNetworksOutputReference",
    "ZeroTrustDnsLocationEndpointsDohOutputReference",
    "ZeroTrustDnsLocationEndpointsDot",
    "ZeroTrustDnsLocationEndpointsDotNetworks",
    "ZeroTrustDnsLocationEndpointsDotNetworksList",
    "ZeroTrustDnsLocationEndpointsDotNetworksOutputReference",
    "ZeroTrustDnsLocationEndpointsDotOutputReference",
    "ZeroTrustDnsLocationEndpointsIpv4",
    "ZeroTrustDnsLocationEndpointsIpv4OutputReference",
    "ZeroTrustDnsLocationEndpointsIpv6",
    "ZeroTrustDnsLocationEndpointsIpv6Networks",
    "ZeroTrustDnsLocationEndpointsIpv6NetworksList",
    "ZeroTrustDnsLocationEndpointsIpv6NetworksOutputReference",
    "ZeroTrustDnsLocationEndpointsIpv6OutputReference",
    "ZeroTrustDnsLocationEndpointsOutputReference",
    "ZeroTrustDnsLocationNetworks",
    "ZeroTrustDnsLocationNetworksList",
    "ZeroTrustDnsLocationNetworksOutputReference",
]

publication.publish()

def _typecheckingstub__8378e43d896096705cac4de6b885b2a7feba340a7c77345eeb5367167ab96139(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    name: builtins.str,
    client_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dns_destination_ips_id: typing.Optional[builtins.str] = None,
    ecs_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    endpoints: typing.Optional[typing.Union[ZeroTrustDnsLocationEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationNetworks, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__35c955cf1376901d6ec94078a0be1951af4d12730c0404fc1f6374d87e3ac113(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31b0ab08dd1cb9f6cb7b2901a64958683fcf5a888f22543401cea5a83a3b9db2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationNetworks, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18cf59cb0f41ff40ba1c73e6548e0fd53bde676991f030bb16d3a8ec4c90bdfb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__526385fabd180e99f8dea808cb996d391efc0a2a559ba5b936cf9a3d4d004cde(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb951972827eb8db7bc7137940ad839fd2a6f6eb0a71391d3f76975d6d8f480c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07ffd1c69795e459c4ebe5ae4e12e77a6cea6ddffefd5313dec10d0639b4e6ae(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86d4061d933b5cf045685b41593907e46c00ea42ac51f76e057d2a03a123f48d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70d62cfd505aea7c51923de8211dea9db41d655c0107ed143af4f3209526cc63(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    name: builtins.str,
    client_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dns_destination_ips_id: typing.Optional[builtins.str] = None,
    ecs_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    endpoints: typing.Optional[typing.Union[ZeroTrustDnsLocationEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationNetworks, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e70d2f8ee02b6fff75773ed2a1f68870de72c3a54ea4f8e8d3b7c6084dc3da5d(
    *,
    doh: typing.Union[ZeroTrustDnsLocationEndpointsDoh, typing.Dict[builtins.str, typing.Any]],
    dot: typing.Union[ZeroTrustDnsLocationEndpointsDot, typing.Dict[builtins.str, typing.Any]],
    ipv4: typing.Union[ZeroTrustDnsLocationEndpointsIpv4, typing.Dict[builtins.str, typing.Any]],
    ipv6: typing.Union[ZeroTrustDnsLocationEndpointsIpv6, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4253f80e5288447807b06bdfe765bdf363868a147e617ea71781286e633c7a2a(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsDohNetworks, typing.Dict[builtins.str, typing.Any]]]]] = None,
    require_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c4d214264ac7bf7633e699229b367d8100e53965aed5e8b0e891d73a2514a65(
    *,
    network: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2388d58fe047cc80d55af1995fced1a6c7c7c6f0bf3d0f8ada725361b80d6caa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcd54ecc486d6b45db6b65455f144b573dc99635e2dc61197c8125064cd98cb4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d69426d1fdadcf2c488d33c1fdcfeab14904595d1ba0efcd26734bbb63ebbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a123d83fa5a82cd86a98dbd6e320ef94ff0627cfac67453a3015d765e4f62d92(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8732d504a86bba8a0349cdd90a7f054b6479c99fac775c3f69e672523b16655(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc14e9b4a01b11552ce4ac0b0c06fc2c6884057188cfc4623f7c48200169565d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDohNetworks]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15dc685461b9a3cb25825f45e77fce11ae067a3faa7657f4543750c7aa3a70fa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1d9faef4d3246c5b7a2f1269894e65bced30c674f6f1951817bd445945d0dce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e86cb5569771f40246a5704dd74bd32fb07c05b1596d883eb17f8ee65550d6b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDohNetworks]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60be59199eae99d956e7dd77141d9674b1a60fb2df0765212fc7f643393ad409(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cbd64cd0ee2f9c8f8426ab5943c036ebfaba935d721f3bb883feb0774c88c62(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsDohNetworks, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e2a73d45560cc38fad7f0667fec9d9e45ae5c78324bd8d5e3cb523846f45e99(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62daca8dea324327efefd80ba1c52b27a709f320863ae1414b35d24ccb35e3e8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7415134ac78ce1bf05e33a7a05ebcfa0b36955db58ddf220c96badcf7c9e36d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDoh]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04abb288965df336321473fe7f5d9d660bd869f1c5ae38f663be2ed7e0661044(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsDotNetworks, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41dc8364a862b2bc88832b9187690ede9828c6fbfe06786e3ae49fc3d8b0d0ea(
    *,
    network: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2991a85049ffb751c76018da9a08cbf40b0233a61a9b465e4eef995393ba0cd4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3abab34a516a463076c64b7b7e5774853768421cf11fb0de0911980f3fa94210(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53f5d1a0d5f14d25854af22cd2a0f59b1f6928c5375c4b18f7c077325ce29ee0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__373176233e21c63d9a550d4ef82f8e8191f34aaef151ef7d00b4b65ca93ff5d7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__306b3af8ed13815f4b21d432f3b868d70524e6ae5995646242c46a544a94e83f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__decb8e031c3cbd738b2b3c8e4ac852e3d1f9ace65adc87ceadaff7898da0004c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsDotNetworks]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8e76f540888368f08d4c1a73c49b912cb228af4c842421a1d7dd842815fb692(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5660f7a17ed2cde22f6340943dbaaf344ce24c427afd314d869733674af67b44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e17d9a10567384e0302966e8dcc010346e810009a5a260b5152bea591f0c442(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDotNetworks]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e86b4d97ad9c1ecf49f3d97ea662d8d002d7abea31a3f27a3e02b3313468b6b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46a31f7312160b5dbed67be049a22e0bd736a8b406c22f3cb9a79064a9e1e2fe(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsDotNetworks, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__631570046b5f7a355aee6ae51ec56ca7fba8cc91dff1f2de69ad2334162f39c0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d90b7eae7fd41b0d2b20e2ff35f1cc8560c82737c6c42af138a266f47dd534ff(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsDot]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3ee05223720f07592d8c29b79d08e1cb50a47106a990ab44d1b7a9858d5fa3f(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6d86a3e71b21cc7c7b8b607dea66e3fe6438732c87299107cad26b884bd43de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__506438d9b0a793bafcb5ecaf6317c11639596d6c0a0c72227ffa16ed9e4c1c1c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41cea4f15fa93a21898199c675f9f683d84c61649dd0d728d77c3ab11896accf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv4]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__508e1ec3c41192e3b5430038d8a13656345832c17781c8cccb9c0d28801271b3(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    networks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsIpv6Networks, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8d6a5eaf0ac668bcacbd9669ded172dfef1dc583ba8979fe1b03da8a5c1b3f8(
    *,
    network: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3af7148a7fc5e5c181d25aaa456da0e55d878e546bcdcff3b09745a557d8da79(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c229086fe465e429651dfed54e13ee595b30d05094e3c82ad72c74a92b64fa11(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43cd8ba669d452a6f92278dc8598f3cdd48e343cec96b64a5443e6e779926398(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__534b9c794a257fcbb5a9667ed90cd4481e5c6697ccca7902d61115bd3f830a02(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__883259513fda8e07c1fbf5fc855ddfd9ceeb1508235c83e35e814f39c6f17688(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21f81f6a8602ab8875f877c03763e105176c3095292b43d007316360d80ee4a8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationEndpointsIpv6Networks]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08b62548f4d78e9f1585624a1033e7f2fae829a6895fd4f3c2b7eddeae917389(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7b50d8cc3406900b1a666865fbba8e74a7c88825e3763c6cdc4c8152de5f617(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c24a9b996614bbaa76b18fc6af0a2f65f61eb47da804771e5a8e595236c1a277(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6Networks]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6f6f2698ea8e42051b245a6cb78210c6d820705702b2f145e287e2e3fd02cad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cf644dc3ad699982774b092f5eb901c80864d9e5963d1391c474e512b9fc87a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDnsLocationEndpointsIpv6Networks, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0abc77ad4f83c2ce5098452c22c2bf6bb27f3fb7e73a62f579e7a40911705da7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93c84cfc9caa75b8fdd601ce41adfaed3d2e3f13e93eebd0637728c91329e3c4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpointsIpv6]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb4647d3d58ce6b2f9e08a350b658ef7f4a18af3d29540feb72689c22571efbd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fc4b48aebb26eb19289a4fa84cef7d9fe6211f4bc1edc36dbaa80d0cbd4972f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationEndpoints]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ab01bdc87f6e68458b4404a0e8aa63264784b6fdcc49cf045813e2254a833f1(
    *,
    network: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__437e142a653ca6a2d055683cedf140c1cb4c7a419ddad0ecf1d84548dd85d849(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc5d034b597cdd438a7ecf1f99583e953da055ed42dc2a49124ef825c55e3e30(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78bf3ed3c61f72b71cbd6c2efd0086b4274712c6be390fb199337fb88fef193c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be518155031eb88ee5388525bbca42e7fd39617e06cc7f0b30d956f848782570(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df1963d81c27bef5c334beb9c629c7177f7c85be35522ae91ee58f06c23dbcb9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b55b96c5a9a03c03988a170169ac70b5dd590721139f542e7605aa98c88d314b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDnsLocationNetworks]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__627971a3fee5519d0c666b2634553466b601d3977ee61871e688fcb4a58dcc63(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46079daf0914220c05e95f46764e505d977bf820f9ae3b796918dd9969ae6ffc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f5efe06c991d25cbde9f943e0e5c73d9bf143eb751f3594d588d69e67ecf191(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDnsLocationNetworks]],
) -> None:
    """Type checking stubs"""
    pass
