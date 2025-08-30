r'''
# `cloudflare_dns_firewall`

Refer to the Terraform Registry for docs: [`cloudflare_dns_firewall`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall).
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


class DnsFirewall(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dnsFirewall.DnsFirewall",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall cloudflare_dns_firewall}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        name: builtins.str,
        upstream_ips: typing.Sequence[builtins.str],
        attack_mitigation: typing.Optional[typing.Union["DnsFirewallAttackMitigation", typing.Dict[builtins.str, typing.Any]]] = None,
        deprecate_any_requests: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ecs_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        maximum_cache_ttl: typing.Optional[jsii.Number] = None,
        minimum_cache_ttl: typing.Optional[jsii.Number] = None,
        negative_cache_ttl: typing.Optional[jsii.Number] = None,
        ratelimit: typing.Optional[jsii.Number] = None,
        retries: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall cloudflare_dns_firewall} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#account_id DnsFirewall#account_id}
        :param name: DNS Firewall cluster name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#name DnsFirewall#name}
        :param upstream_ips: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#upstream_ips DnsFirewall#upstream_ips}.
        :param attack_mitigation: Attack mitigation settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#attack_mitigation DnsFirewall#attack_mitigation}
        :param deprecate_any_requests: Whether to refuse to answer queries for the ANY type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#deprecate_any_requests DnsFirewall#deprecate_any_requests}
        :param ecs_fallback: Whether to forward client IP (resolver) subnet if no EDNS Client Subnet is sent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#ecs_fallback DnsFirewall#ecs_fallback}
        :param maximum_cache_ttl: Maximum DNS cache TTL This setting sets an upper bound on DNS TTLs for purposes of caching between DNS Firewall and the upstream servers. Higher TTLs will be decreased to the maximum defined here for caching purposes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#maximum_cache_ttl DnsFirewall#maximum_cache_ttl}
        :param minimum_cache_ttl: Minimum DNS cache TTL This setting sets a lower bound on DNS TTLs for purposes of caching between DNS Firewall and the upstream servers. Lower TTLs will be increased to the minimum defined here for caching purposes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#minimum_cache_ttl DnsFirewall#minimum_cache_ttl}
        :param negative_cache_ttl: Negative DNS cache TTL This setting controls how long DNS Firewall should cache negative responses (e.g., NXDOMAIN) from the upstream servers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#negative_cache_ttl DnsFirewall#negative_cache_ttl}
        :param ratelimit: Ratelimit in queries per second per datacenter (applies to DNS queries sent to the upstream nameservers configured on the cluster). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#ratelimit DnsFirewall#ratelimit}
        :param retries: Number of retries for fetching DNS responses from upstream nameservers (not counting the initial attempt). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#retries DnsFirewall#retries}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cc118448fbaabd9eb73073fdbd77140a2a5d419563797ebb8e800c9acd6dcc0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DnsFirewallConfig(
            account_id=account_id,
            name=name,
            upstream_ips=upstream_ips,
            attack_mitigation=attack_mitigation,
            deprecate_any_requests=deprecate_any_requests,
            ecs_fallback=ecs_fallback,
            maximum_cache_ttl=maximum_cache_ttl,
            minimum_cache_ttl=minimum_cache_ttl,
            negative_cache_ttl=negative_cache_ttl,
            ratelimit=ratelimit,
            retries=retries,
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
        '''Generates CDKTF code for importing a DnsFirewall resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DnsFirewall to import.
        :param import_from_id: The id of the existing DnsFirewall that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DnsFirewall to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9402ba172092ec62cafabaf6be1bc22a5055f96c4829148ce60569c45d69c29)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAttackMitigation")
    def put_attack_mitigation(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        only_when_upstream_unhealthy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: When enabled, automatically mitigate random-prefix attacks to protect upstream DNS servers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#enabled DnsFirewall#enabled}
        :param only_when_upstream_unhealthy: Only mitigate attacks when upstream servers seem unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#only_when_upstream_unhealthy DnsFirewall#only_when_upstream_unhealthy}
        '''
        value = DnsFirewallAttackMitigation(
            enabled=enabled, only_when_upstream_unhealthy=only_when_upstream_unhealthy
        )

        return typing.cast(None, jsii.invoke(self, "putAttackMitigation", [value]))

    @jsii.member(jsii_name="resetAttackMitigation")
    def reset_attack_mitigation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttackMitigation", []))

    @jsii.member(jsii_name="resetDeprecateAnyRequests")
    def reset_deprecate_any_requests(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeprecateAnyRequests", []))

    @jsii.member(jsii_name="resetEcsFallback")
    def reset_ecs_fallback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEcsFallback", []))

    @jsii.member(jsii_name="resetMaximumCacheTtl")
    def reset_maximum_cache_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumCacheTtl", []))

    @jsii.member(jsii_name="resetMinimumCacheTtl")
    def reset_minimum_cache_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumCacheTtl", []))

    @jsii.member(jsii_name="resetNegativeCacheTtl")
    def reset_negative_cache_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNegativeCacheTtl", []))

    @jsii.member(jsii_name="resetRatelimit")
    def reset_ratelimit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRatelimit", []))

    @jsii.member(jsii_name="resetRetries")
    def reset_retries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetries", []))

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
    @jsii.member(jsii_name="attackMitigation")
    def attack_mitigation(self) -> "DnsFirewallAttackMitigationOutputReference":
        return typing.cast("DnsFirewallAttackMitigationOutputReference", jsii.get(self, "attackMitigation"))

    @builtins.property
    @jsii.member(jsii_name="dnsFirewallIps")
    def dns_firewall_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsFirewallIps"))

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
    @jsii.member(jsii_name="attackMitigationInput")
    def attack_mitigation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DnsFirewallAttackMitigation"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DnsFirewallAttackMitigation"]], jsii.get(self, "attackMitigationInput"))

    @builtins.property
    @jsii.member(jsii_name="deprecateAnyRequestsInput")
    def deprecate_any_requests_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deprecateAnyRequestsInput"))

    @builtins.property
    @jsii.member(jsii_name="ecsFallbackInput")
    def ecs_fallback_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ecsFallbackInput"))

    @builtins.property
    @jsii.member(jsii_name="maximumCacheTtlInput")
    def maximum_cache_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximumCacheTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumCacheTtlInput")
    def minimum_cache_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimumCacheTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="negativeCacheTtlInput")
    def negative_cache_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "negativeCacheTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="ratelimitInput")
    def ratelimit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ratelimitInput"))

    @builtins.property
    @jsii.member(jsii_name="retriesInput")
    def retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retriesInput"))

    @builtins.property
    @jsii.member(jsii_name="upstreamIpsInput")
    def upstream_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "upstreamIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b564c534639368c017273b0144e0c3375e0e9e255abe6365626c45b92ffee3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deprecateAnyRequests")
    def deprecate_any_requests(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deprecateAnyRequests"))

    @deprecate_any_requests.setter
    def deprecate_any_requests(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ca3a83b1e1b819ce5e0103e4413c912b0088721450d9ed5a3c2c0912e53d8fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deprecateAnyRequests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ecsFallback")
    def ecs_fallback(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ecsFallback"))

    @ecs_fallback.setter
    def ecs_fallback(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3453e48f7a6e106de58f6a4e10c65a80413b1309dc6fc96953b9e7440f16fa2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ecsFallback", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maximumCacheTtl")
    def maximum_cache_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maximumCacheTtl"))

    @maximum_cache_ttl.setter
    def maximum_cache_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e7ef70c7b2df7029d6b79d2a07fd6787da283978998b4b5401c6a1223ed42f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximumCacheTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimumCacheTtl")
    def minimum_cache_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minimumCacheTtl"))

    @minimum_cache_ttl.setter
    def minimum_cache_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06a6393551cf621b3712ba19c1e9ad54b0149254a356aa61fc68d88a7dcbd62f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimumCacheTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f89800fde03d6b6dc09bf52ec60bf4552c49d15521226d868e3a9d66e10fd448)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="negativeCacheTtl")
    def negative_cache_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "negativeCacheTtl"))

    @negative_cache_ttl.setter
    def negative_cache_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17c77521f61115e3cc658fed6aa4bb070b21475843356df4ee07d15a6e30ec56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "negativeCacheTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ratelimit")
    def ratelimit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ratelimit"))

    @ratelimit.setter
    def ratelimit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3d0fc86071333f39fc93735e9f890bae0c824f827475a4405af3f9218a6fe5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ratelimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retries")
    def retries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retries"))

    @retries.setter
    def retries(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de91587bc1c4e47a327b0f4132baa7e8b0ad6119a1216fb2d9cb8441a39d2b22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="upstreamIps")
    def upstream_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "upstreamIps"))

    @upstream_ips.setter
    def upstream_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b86abeeb3cc343940288938ed5a6738f6b392e36a00da96d4e4094a8e74560b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "upstreamIps", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dnsFirewall.DnsFirewallAttackMitigation",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "only_when_upstream_unhealthy": "onlyWhenUpstreamUnhealthy",
    },
)
class DnsFirewallAttackMitigation:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        only_when_upstream_unhealthy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: When enabled, automatically mitigate random-prefix attacks to protect upstream DNS servers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#enabled DnsFirewall#enabled}
        :param only_when_upstream_unhealthy: Only mitigate attacks when upstream servers seem unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#only_when_upstream_unhealthy DnsFirewall#only_when_upstream_unhealthy}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3419cdcc38148df98b1a70e677c280c249318b78ebca1f3ae1ff63e22f718b3)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument only_when_upstream_unhealthy", value=only_when_upstream_unhealthy, expected_type=type_hints["only_when_upstream_unhealthy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if only_when_upstream_unhealthy is not None:
            self._values["only_when_upstream_unhealthy"] = only_when_upstream_unhealthy

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When enabled, automatically mitigate random-prefix attacks to protect upstream DNS servers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#enabled DnsFirewall#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def only_when_upstream_unhealthy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Only mitigate attacks when upstream servers seem unhealthy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#only_when_upstream_unhealthy DnsFirewall#only_when_upstream_unhealthy}
        '''
        result = self._values.get("only_when_upstream_unhealthy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DnsFirewallAttackMitigation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DnsFirewallAttackMitigationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dnsFirewall.DnsFirewallAttackMitigationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2357f236c734729851536e7c81185bf84f0f407dc8370332f83f9562846e6bf0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetOnlyWhenUpstreamUnhealthy")
    def reset_only_when_upstream_unhealthy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnlyWhenUpstreamUnhealthy", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="onlyWhenUpstreamUnhealthyInput")
    def only_when_upstream_unhealthy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "onlyWhenUpstreamUnhealthyInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__12413b9a7d52260ebbbf6ea62b8c73e4452509ccf2b38515e36655b9b5f19abd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onlyWhenUpstreamUnhealthy")
    def only_when_upstream_unhealthy(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "onlyWhenUpstreamUnhealthy"))

    @only_when_upstream_unhealthy.setter
    def only_when_upstream_unhealthy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__950bcb1bf922365e382203a3373f2cb888df6a0059e39cb94df881a08f440ba1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onlyWhenUpstreamUnhealthy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsFirewallAttackMitigation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsFirewallAttackMitigation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsFirewallAttackMitigation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2848334fab3adb41723cead2ecce378c46200eb0043a3e35404739306942d5e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dnsFirewall.DnsFirewallConfig",
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
        "upstream_ips": "upstreamIps",
        "attack_mitigation": "attackMitigation",
        "deprecate_any_requests": "deprecateAnyRequests",
        "ecs_fallback": "ecsFallback",
        "maximum_cache_ttl": "maximumCacheTtl",
        "minimum_cache_ttl": "minimumCacheTtl",
        "negative_cache_ttl": "negativeCacheTtl",
        "ratelimit": "ratelimit",
        "retries": "retries",
    },
)
class DnsFirewallConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        upstream_ips: typing.Sequence[builtins.str],
        attack_mitigation: typing.Optional[typing.Union[DnsFirewallAttackMitigation, typing.Dict[builtins.str, typing.Any]]] = None,
        deprecate_any_requests: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ecs_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        maximum_cache_ttl: typing.Optional[jsii.Number] = None,
        minimum_cache_ttl: typing.Optional[jsii.Number] = None,
        negative_cache_ttl: typing.Optional[jsii.Number] = None,
        ratelimit: typing.Optional[jsii.Number] = None,
        retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#account_id DnsFirewall#account_id}
        :param name: DNS Firewall cluster name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#name DnsFirewall#name}
        :param upstream_ips: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#upstream_ips DnsFirewall#upstream_ips}.
        :param attack_mitigation: Attack mitigation settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#attack_mitigation DnsFirewall#attack_mitigation}
        :param deprecate_any_requests: Whether to refuse to answer queries for the ANY type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#deprecate_any_requests DnsFirewall#deprecate_any_requests}
        :param ecs_fallback: Whether to forward client IP (resolver) subnet if no EDNS Client Subnet is sent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#ecs_fallback DnsFirewall#ecs_fallback}
        :param maximum_cache_ttl: Maximum DNS cache TTL This setting sets an upper bound on DNS TTLs for purposes of caching between DNS Firewall and the upstream servers. Higher TTLs will be decreased to the maximum defined here for caching purposes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#maximum_cache_ttl DnsFirewall#maximum_cache_ttl}
        :param minimum_cache_ttl: Minimum DNS cache TTL This setting sets a lower bound on DNS TTLs for purposes of caching between DNS Firewall and the upstream servers. Lower TTLs will be increased to the minimum defined here for caching purposes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#minimum_cache_ttl DnsFirewall#minimum_cache_ttl}
        :param negative_cache_ttl: Negative DNS cache TTL This setting controls how long DNS Firewall should cache negative responses (e.g., NXDOMAIN) from the upstream servers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#negative_cache_ttl DnsFirewall#negative_cache_ttl}
        :param ratelimit: Ratelimit in queries per second per datacenter (applies to DNS queries sent to the upstream nameservers configured on the cluster). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#ratelimit DnsFirewall#ratelimit}
        :param retries: Number of retries for fetching DNS responses from upstream nameservers (not counting the initial attempt). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#retries DnsFirewall#retries}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(attack_mitigation, dict):
            attack_mitigation = DnsFirewallAttackMitigation(**attack_mitigation)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__030b8253ecd68fa22bb250739f21686558576d5eb9f15ccd58aae98a9fd7a6ba)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument upstream_ips", value=upstream_ips, expected_type=type_hints["upstream_ips"])
            check_type(argname="argument attack_mitigation", value=attack_mitigation, expected_type=type_hints["attack_mitigation"])
            check_type(argname="argument deprecate_any_requests", value=deprecate_any_requests, expected_type=type_hints["deprecate_any_requests"])
            check_type(argname="argument ecs_fallback", value=ecs_fallback, expected_type=type_hints["ecs_fallback"])
            check_type(argname="argument maximum_cache_ttl", value=maximum_cache_ttl, expected_type=type_hints["maximum_cache_ttl"])
            check_type(argname="argument minimum_cache_ttl", value=minimum_cache_ttl, expected_type=type_hints["minimum_cache_ttl"])
            check_type(argname="argument negative_cache_ttl", value=negative_cache_ttl, expected_type=type_hints["negative_cache_ttl"])
            check_type(argname="argument ratelimit", value=ratelimit, expected_type=type_hints["ratelimit"])
            check_type(argname="argument retries", value=retries, expected_type=type_hints["retries"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "name": name,
            "upstream_ips": upstream_ips,
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
        if attack_mitigation is not None:
            self._values["attack_mitigation"] = attack_mitigation
        if deprecate_any_requests is not None:
            self._values["deprecate_any_requests"] = deprecate_any_requests
        if ecs_fallback is not None:
            self._values["ecs_fallback"] = ecs_fallback
        if maximum_cache_ttl is not None:
            self._values["maximum_cache_ttl"] = maximum_cache_ttl
        if minimum_cache_ttl is not None:
            self._values["minimum_cache_ttl"] = minimum_cache_ttl
        if negative_cache_ttl is not None:
            self._values["negative_cache_ttl"] = negative_cache_ttl
        if ratelimit is not None:
            self._values["ratelimit"] = ratelimit
        if retries is not None:
            self._values["retries"] = retries

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#account_id DnsFirewall#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''DNS Firewall cluster name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#name DnsFirewall#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def upstream_ips(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#upstream_ips DnsFirewall#upstream_ips}.'''
        result = self._values.get("upstream_ips")
        assert result is not None, "Required property 'upstream_ips' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def attack_mitigation(self) -> typing.Optional[DnsFirewallAttackMitigation]:
        '''Attack mitigation settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#attack_mitigation DnsFirewall#attack_mitigation}
        '''
        result = self._values.get("attack_mitigation")
        return typing.cast(typing.Optional[DnsFirewallAttackMitigation], result)

    @builtins.property
    def deprecate_any_requests(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to refuse to answer queries for the ANY type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#deprecate_any_requests DnsFirewall#deprecate_any_requests}
        '''
        result = self._values.get("deprecate_any_requests")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ecs_fallback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to forward client IP (resolver) subnet if no EDNS Client Subnet is sent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#ecs_fallback DnsFirewall#ecs_fallback}
        '''
        result = self._values.get("ecs_fallback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def maximum_cache_ttl(self) -> typing.Optional[jsii.Number]:
        '''Maximum DNS cache TTL This setting sets an upper bound on DNS TTLs for purposes of caching between DNS Firewall and the upstream servers.

        Higher TTLs will be decreased to the maximum defined here for caching purposes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#maximum_cache_ttl DnsFirewall#maximum_cache_ttl}
        '''
        result = self._values.get("maximum_cache_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minimum_cache_ttl(self) -> typing.Optional[jsii.Number]:
        '''Minimum DNS cache TTL This setting sets a lower bound on DNS TTLs for purposes of caching between DNS Firewall and the upstream servers.

        Lower TTLs will be increased to the minimum defined here for caching purposes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#minimum_cache_ttl DnsFirewall#minimum_cache_ttl}
        '''
        result = self._values.get("minimum_cache_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def negative_cache_ttl(self) -> typing.Optional[jsii.Number]:
        '''Negative DNS cache TTL This setting controls how long DNS Firewall should cache negative responses (e.g., NXDOMAIN) from the upstream servers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#negative_cache_ttl DnsFirewall#negative_cache_ttl}
        '''
        result = self._values.get("negative_cache_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ratelimit(self) -> typing.Optional[jsii.Number]:
        '''Ratelimit in queries per second per datacenter (applies to DNS queries sent to the upstream nameservers configured on the cluster).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#ratelimit DnsFirewall#ratelimit}
        '''
        result = self._values.get("ratelimit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retries(self) -> typing.Optional[jsii.Number]:
        '''Number of retries for fetching DNS responses from upstream nameservers (not counting the initial attempt).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_firewall#retries DnsFirewall#retries}
        '''
        result = self._values.get("retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DnsFirewallConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DnsFirewall",
    "DnsFirewallAttackMitigation",
    "DnsFirewallAttackMitigationOutputReference",
    "DnsFirewallConfig",
]

publication.publish()

def _typecheckingstub__8cc118448fbaabd9eb73073fdbd77140a2a5d419563797ebb8e800c9acd6dcc0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    name: builtins.str,
    upstream_ips: typing.Sequence[builtins.str],
    attack_mitigation: typing.Optional[typing.Union[DnsFirewallAttackMitigation, typing.Dict[builtins.str, typing.Any]]] = None,
    deprecate_any_requests: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ecs_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    maximum_cache_ttl: typing.Optional[jsii.Number] = None,
    minimum_cache_ttl: typing.Optional[jsii.Number] = None,
    negative_cache_ttl: typing.Optional[jsii.Number] = None,
    ratelimit: typing.Optional[jsii.Number] = None,
    retries: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__f9402ba172092ec62cafabaf6be1bc22a5055f96c4829148ce60569c45d69c29(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b564c534639368c017273b0144e0c3375e0e9e255abe6365626c45b92ffee3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ca3a83b1e1b819ce5e0103e4413c912b0088721450d9ed5a3c2c0912e53d8fd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3453e48f7a6e106de58f6a4e10c65a80413b1309dc6fc96953b9e7440f16fa2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e7ef70c7b2df7029d6b79d2a07fd6787da283978998b4b5401c6a1223ed42f7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06a6393551cf621b3712ba19c1e9ad54b0149254a356aa61fc68d88a7dcbd62f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f89800fde03d6b6dc09bf52ec60bf4552c49d15521226d868e3a9d66e10fd448(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17c77521f61115e3cc658fed6aa4bb070b21475843356df4ee07d15a6e30ec56(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3d0fc86071333f39fc93735e9f890bae0c824f827475a4405af3f9218a6fe5b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de91587bc1c4e47a327b0f4132baa7e8b0ad6119a1216fb2d9cb8441a39d2b22(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b86abeeb3cc343940288938ed5a6738f6b392e36a00da96d4e4094a8e74560b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3419cdcc38148df98b1a70e677c280c249318b78ebca1f3ae1ff63e22f718b3(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    only_when_upstream_unhealthy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2357f236c734729851536e7c81185bf84f0f407dc8370332f83f9562846e6bf0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12413b9a7d52260ebbbf6ea62b8c73e4452509ccf2b38515e36655b9b5f19abd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__950bcb1bf922365e382203a3373f2cb888df6a0059e39cb94df881a08f440ba1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2848334fab3adb41723cead2ecce378c46200eb0043a3e35404739306942d5e9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsFirewallAttackMitigation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__030b8253ecd68fa22bb250739f21686558576d5eb9f15ccd58aae98a9fd7a6ba(
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
    upstream_ips: typing.Sequence[builtins.str],
    attack_mitigation: typing.Optional[typing.Union[DnsFirewallAttackMitigation, typing.Dict[builtins.str, typing.Any]]] = None,
    deprecate_any_requests: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ecs_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    maximum_cache_ttl: typing.Optional[jsii.Number] = None,
    minimum_cache_ttl: typing.Optional[jsii.Number] = None,
    negative_cache_ttl: typing.Optional[jsii.Number] = None,
    ratelimit: typing.Optional[jsii.Number] = None,
    retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
