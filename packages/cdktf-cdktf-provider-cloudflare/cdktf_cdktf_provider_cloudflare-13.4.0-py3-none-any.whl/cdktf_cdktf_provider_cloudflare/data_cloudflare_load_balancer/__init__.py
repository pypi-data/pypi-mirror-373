r'''
# `data_cloudflare_load_balancer`

Refer to the Terraform Registry for docs: [`data_cloudflare_load_balancer`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer).
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


class DataCloudflareLoadBalancer(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancer",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer cloudflare_load_balancer}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        zone_id: builtins.str,
        load_balancer_id: typing.Optional[builtins.str] = None,
        pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer cloudflare_load_balancer} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#zone_id DataCloudflareLoadBalancer#zone_id}.
        :param load_balancer_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#load_balancer_id DataCloudflareLoadBalancer#load_balancer_id}.
        :param pop_pools: Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter). Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#pop_pools DataCloudflareLoadBalancer#pop_pools}
        :param region_pools: A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region. Any regions not explicitly defined will fall back to using default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#region_pools DataCloudflareLoadBalancer#region_pools}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__228c23b5cf249916f6c1a265fd5b4a547690b96262b03c26f158f1db4b7482e6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareLoadBalancerConfig(
            zone_id=zone_id,
            load_balancer_id=load_balancer_id,
            pop_pools=pop_pools,
            region_pools=region_pools,
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
        '''Generates CDKTF code for importing a DataCloudflareLoadBalancer resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareLoadBalancer to import.
        :param import_from_id: The id of the existing DataCloudflareLoadBalancer that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareLoadBalancer to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b54f40e785caf0889b0a42fb17c19adbacf09dcc7ab4db32f741c3af99a1911)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetLoadBalancerId")
    def reset_load_balancer_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoadBalancerId", []))

    @jsii.member(jsii_name="resetPopPools")
    def reset_pop_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPopPools", []))

    @jsii.member(jsii_name="resetRegionPools")
    def reset_region_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionPools", []))

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
    @jsii.member(jsii_name="adaptiveRouting")
    def adaptive_routing(
        self,
    ) -> "DataCloudflareLoadBalancerAdaptiveRoutingOutputReference":
        return typing.cast("DataCloudflareLoadBalancerAdaptiveRoutingOutputReference", jsii.get(self, "adaptiveRouting"))

    @builtins.property
    @jsii.member(jsii_name="countryPools")
    def country_pools(self) -> _cdktf_9a9027ec.StringListMap:
        return typing.cast(_cdktf_9a9027ec.StringListMap, jsii.get(self, "countryPools"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="defaultPools")
    def default_pools(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "defaultPools"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="fallbackPool")
    def fallback_pool(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fallbackPool"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="locationStrategy")
    def location_strategy(
        self,
    ) -> "DataCloudflareLoadBalancerLocationStrategyOutputReference":
        return typing.cast("DataCloudflareLoadBalancerLocationStrategyOutputReference", jsii.get(self, "locationStrategy"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="networks")
    def networks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networks"))

    @builtins.property
    @jsii.member(jsii_name="proxied")
    def proxied(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "proxied"))

    @builtins.property
    @jsii.member(jsii_name="randomSteering")
    def random_steering(
        self,
    ) -> "DataCloudflareLoadBalancerRandomSteeringOutputReference":
        return typing.cast("DataCloudflareLoadBalancerRandomSteeringOutputReference", jsii.get(self, "randomSteering"))

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> "DataCloudflareLoadBalancerRulesList":
        return typing.cast("DataCloudflareLoadBalancerRulesList", jsii.get(self, "rules"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinity")
    def session_affinity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionAffinity"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityAttributes")
    def session_affinity_attributes(
        self,
    ) -> "DataCloudflareLoadBalancerSessionAffinityAttributesOutputReference":
        return typing.cast("DataCloudflareLoadBalancerSessionAffinityAttributesOutputReference", jsii.get(self, "sessionAffinityAttributes"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityTtl")
    def session_affinity_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sessionAffinityTtl"))

    @builtins.property
    @jsii.member(jsii_name="steeringPolicy")
    def steering_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "steeringPolicy"))

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancerIdInput")
    def load_balancer_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loadBalancerIdInput"))

    @builtins.property
    @jsii.member(jsii_name="popPoolsInput")
    def pop_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "popPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="regionPoolsInput")
    def region_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "regionPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancerId")
    def load_balancer_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loadBalancerId"))

    @load_balancer_id.setter
    def load_balancer_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bfc82f3a8a63537948b319aae39974ab8689603a110691b51f1f11eab1acfb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loadBalancerId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="popPools")
    def pop_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "popPools"))

    @pop_pools.setter
    def pop_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__507006ae688ed970e451df9802cbe674dacbbcd229e612bd96122863178cf376)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "popPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionPools")
    def region_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "regionPools"))

    @region_pools.setter
    def region_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec31bf1e3fdbbf09428d9cf860728f994330dcac818a598b4368c498dbc59fc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5da01379a60f8ec4a5f54d89cafcc6f0970940f09e2c9e398c5c8264b18e6570)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerAdaptiveRouting",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancerAdaptiveRouting:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerAdaptiveRouting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancerAdaptiveRoutingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerAdaptiveRoutingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f726f9deacadf7c0f967b26d52b10bd9ed90dac1777777191c05365887f89e1e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="failoverAcrossPools")
    def failover_across_pools(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "failoverAcrossPools"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerAdaptiveRouting]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerAdaptiveRouting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerAdaptiveRouting],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf87d493245df32a0263472c8eb0649d3dafc4d1fdd1ba23a1681f9f7ffb936e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "zone_id": "zoneId",
        "load_balancer_id": "loadBalancerId",
        "pop_pools": "popPools",
        "region_pools": "regionPools",
    },
)
class DataCloudflareLoadBalancerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        zone_id: builtins.str,
        load_balancer_id: typing.Optional[builtins.str] = None,
        pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#zone_id DataCloudflareLoadBalancer#zone_id}.
        :param load_balancer_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#load_balancer_id DataCloudflareLoadBalancer#load_balancer_id}.
        :param pop_pools: Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter). Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#pop_pools DataCloudflareLoadBalancer#pop_pools}
        :param region_pools: A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region. Any regions not explicitly defined will fall back to using default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#region_pools DataCloudflareLoadBalancer#region_pools}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__add0817d466d09d580b593785bd67496c737aca11fb94bd54300b22d0888e9d3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument load_balancer_id", value=load_balancer_id, expected_type=type_hints["load_balancer_id"])
            check_type(argname="argument pop_pools", value=pop_pools, expected_type=type_hints["pop_pools"])
            check_type(argname="argument region_pools", value=region_pools, expected_type=type_hints["region_pools"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "zone_id": zone_id,
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
        if load_balancer_id is not None:
            self._values["load_balancer_id"] = load_balancer_id
        if pop_pools is not None:
            self._values["pop_pools"] = pop_pools
        if region_pools is not None:
            self._values["region_pools"] = region_pools

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
    def zone_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#zone_id DataCloudflareLoadBalancer#zone_id}.'''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def load_balancer_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#load_balancer_id DataCloudflareLoadBalancer#load_balancer_id}.'''
        result = self._values.get("load_balancer_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pop_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter).

        Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#pop_pools DataCloudflareLoadBalancer#pop_pools}
        '''
        result = self._values.get("pop_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def region_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region.

        Any regions not explicitly defined will fall back to using default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#region_pools DataCloudflareLoadBalancer#region_pools}
        '''
        result = self._values.get("region_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerLocationStrategy",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancerLocationStrategy:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerLocationStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancerLocationStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerLocationStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4dde90654dae7df012caf6229dc63108ae2b74eaff57463a296383ff9c25551f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @builtins.property
    @jsii.member(jsii_name="preferEcs")
    def prefer_ecs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferEcs"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerLocationStrategy]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerLocationStrategy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerLocationStrategy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f562b4150009642dca4f7b29f520413785aff6e0a48b24800ec0603922a132a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRandomSteering",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancerRandomSteering:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerRandomSteering(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancerRandomSteeringOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRandomSteeringOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0cea49206a166bf7f3c8811d0d6f9c066cc1edcfecc847bb8bd67c8933c7aa46)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="defaultWeight")
    def default_weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultWeight"))

    @builtins.property
    @jsii.member(jsii_name="poolWeights")
    def pool_weights(self) -> _cdktf_9a9027ec.NumberMap:
        return typing.cast(_cdktf_9a9027ec.NumberMap, jsii.get(self, "poolWeights"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerRandomSteering]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerRandomSteering], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerRandomSteering],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dda78b2ab0bfab8e735b948c4743046c834c3fb5f1570c2d4343a716f684d3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRules",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancerRules:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesFixedResponse",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancerRulesFixedResponse:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerRulesFixedResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancerRulesFixedResponseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesFixedResponseOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8be4d9bafcbe4aad1550a96985e64d5a0486a4013a6f5b308eb05db848105185)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @builtins.property
    @jsii.member(jsii_name="messageBody")
    def message_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageBody"))

    @builtins.property
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "statusCode"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerRulesFixedResponse]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerRulesFixedResponse], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerRulesFixedResponse],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86592daa3f4537195c145f2ddaf90f7c08df876ddc86f933a8cfe27726552130)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareLoadBalancerRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1155f47f91d532ad72a8452cbdc097abc751b67f0140aa47bfece1bf71ae7e15)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareLoadBalancerRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b75cc88e3022039af7ca2e05eb52eb70b31cc15040d9bf06bbe1636e622e9f86)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareLoadBalancerRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0b932699f83f9a987add957d2261013750f1e5a14052279620664ed61f50c01)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef0969d6be5eeb57c9f6bd915d7e7a3fd1a5a1c931fd430ad2af7c2a3589259d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__efa0ad90aeb0e2b355850508c8be108caf90c2f5c261efb73162f81e4ed090db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareLoadBalancerRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c3cb5c321a8e5360917f168dfbf92e59b4a18f87643c5f998ea775a5f6b32bb1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "condition"))

    @builtins.property
    @jsii.member(jsii_name="disabled")
    def disabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "disabled"))

    @builtins.property
    @jsii.member(jsii_name="fixedResponse")
    def fixed_response(
        self,
    ) -> DataCloudflareLoadBalancerRulesFixedResponseOutputReference:
        return typing.cast(DataCloudflareLoadBalancerRulesFixedResponseOutputReference, jsii.get(self, "fixedResponse"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="overrides")
    def overrides(self) -> "DataCloudflareLoadBalancerRulesOverridesOutputReference":
        return typing.cast("DataCloudflareLoadBalancerRulesOverridesOutputReference", jsii.get(self, "overrides"))

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @builtins.property
    @jsii.member(jsii_name="terminates")
    def terminates(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "terminates"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataCloudflareLoadBalancerRules]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerRules],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db50182f08c4e22b167773f4a9c18fad173899eca2d3f804c1199a46cefe88e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverrides",
    jsii_struct_bases=[],
    name_mapping={"pop_pools": "popPools"},
)
class DataCloudflareLoadBalancerRulesOverrides:
    def __init__(
        self,
        *,
        pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    ) -> None:
        '''
        :param pop_pools: Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter). Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#pop_pools DataCloudflareLoadBalancer#pop_pools}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bb4e3de6c2ce63a6d4b6fbdbc4390cf1d7ef601b04c32a74e4218d54759038e)
            check_type(argname="argument pop_pools", value=pop_pools, expected_type=type_hints["pop_pools"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if pop_pools is not None:
            self._values["pop_pools"] = pop_pools

    @builtins.property
    def pop_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter).

        Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#pop_pools DataCloudflareLoadBalancer#pop_pools}
        '''
        result = self._values.get("pop_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerRulesOverrides(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverridesAdaptiveRouting",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancerRulesOverridesAdaptiveRouting:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerRulesOverridesAdaptiveRouting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancerRulesOverridesAdaptiveRoutingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverridesAdaptiveRoutingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9029722192b826f612e50955d74356433f11572d16c8d207d4f5b8b4318c51e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="failoverAcrossPools")
    def failover_across_pools(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "failoverAcrossPools"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerRulesOverridesAdaptiveRouting]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerRulesOverridesAdaptiveRouting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerRulesOverridesAdaptiveRouting],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dec93ac23a5554e796f52eab00877f55160dd1eb030e36c1afbac8d039f92fd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverridesLocationStrategy",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancerRulesOverridesLocationStrategy:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerRulesOverridesLocationStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancerRulesOverridesLocationStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverridesLocationStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__86a4ce35f0a20fc2472a86df1c3f0d89c2e8508fbb3f94209f2aebc88c9a4941)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @builtins.property
    @jsii.member(jsii_name="preferEcs")
    def prefer_ecs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferEcs"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerRulesOverridesLocationStrategy]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerRulesOverridesLocationStrategy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerRulesOverridesLocationStrategy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__393824875a5d73ce7410c0ca0d5ffa10debf65cc3fe84a33894a95f757354260)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareLoadBalancerRulesOverridesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverridesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2845a275180c99ec85abd29480978773c7ada544d889816d051c41549fb9324)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPopPools")
    def reset_pop_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPopPools", []))

    @builtins.property
    @jsii.member(jsii_name="adaptiveRouting")
    def adaptive_routing(
        self,
    ) -> DataCloudflareLoadBalancerRulesOverridesAdaptiveRoutingOutputReference:
        return typing.cast(DataCloudflareLoadBalancerRulesOverridesAdaptiveRoutingOutputReference, jsii.get(self, "adaptiveRouting"))

    @builtins.property
    @jsii.member(jsii_name="countryPools")
    def country_pools(self) -> _cdktf_9a9027ec.StringListMap:
        return typing.cast(_cdktf_9a9027ec.StringListMap, jsii.get(self, "countryPools"))

    @builtins.property
    @jsii.member(jsii_name="defaultPools")
    def default_pools(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "defaultPools"))

    @builtins.property
    @jsii.member(jsii_name="fallbackPool")
    def fallback_pool(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fallbackPool"))

    @builtins.property
    @jsii.member(jsii_name="locationStrategy")
    def location_strategy(
        self,
    ) -> DataCloudflareLoadBalancerRulesOverridesLocationStrategyOutputReference:
        return typing.cast(DataCloudflareLoadBalancerRulesOverridesLocationStrategyOutputReference, jsii.get(self, "locationStrategy"))

    @builtins.property
    @jsii.member(jsii_name="randomSteering")
    def random_steering(
        self,
    ) -> "DataCloudflareLoadBalancerRulesOverridesRandomSteeringOutputReference":
        return typing.cast("DataCloudflareLoadBalancerRulesOverridesRandomSteeringOutputReference", jsii.get(self, "randomSteering"))

    @builtins.property
    @jsii.member(jsii_name="regionPools")
    def region_pools(self) -> _cdktf_9a9027ec.StringListMap:
        return typing.cast(_cdktf_9a9027ec.StringListMap, jsii.get(self, "regionPools"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinity")
    def session_affinity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionAffinity"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityAttributes")
    def session_affinity_attributes(
        self,
    ) -> "DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributesOutputReference":
        return typing.cast("DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributesOutputReference", jsii.get(self, "sessionAffinityAttributes"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityTtl")
    def session_affinity_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sessionAffinityTtl"))

    @builtins.property
    @jsii.member(jsii_name="steeringPolicy")
    def steering_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "steeringPolicy"))

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @builtins.property
    @jsii.member(jsii_name="popPoolsInput")
    def pop_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "popPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="popPools")
    def pop_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "popPools"))

    @pop_pools.setter
    def pop_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf81b7305ea0c7c1d7d9b5d6f3699b6c3feede0ab78b5bfe43ebfe990383e1aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "popPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerRulesOverrides]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerRulesOverrides], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerRulesOverrides],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db2469986f6beb3fe0ad4ca3f09719414846740ea8a7442f57131f5e79fccc79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverridesRandomSteering",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancerRulesOverridesRandomSteering:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerRulesOverridesRandomSteering(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancerRulesOverridesRandomSteeringOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverridesRandomSteeringOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a635aa637200a6285e6c53d37c792048af8328ba9c33f717bba2fda2b48b6f6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="defaultWeight")
    def default_weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultWeight"))

    @builtins.property
    @jsii.member(jsii_name="poolWeights")
    def pool_weights(self) -> _cdktf_9a9027ec.NumberMap:
        return typing.cast(_cdktf_9a9027ec.NumberMap, jsii.get(self, "poolWeights"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerRulesOverridesRandomSteering]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerRulesOverridesRandomSteering], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerRulesOverridesRandomSteering],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66bd42a7ac3ff4dbb1bde3d5a1128adee423b79b2f1bbaaa99df9105964f78d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributes",
    jsii_struct_bases=[],
    name_mapping={"drain_duration": "drainDuration"},
)
class DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributes:
    def __init__(self, *, drain_duration: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param drain_duration: Configures the drain duration in seconds. This field is only used when session affinity is enabled on the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#drain_duration DataCloudflareLoadBalancer#drain_duration}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ef6f9f83a3886c25202b703f8e1615c1f83088fbc820f7cd09b61dee9c56145)
            check_type(argname="argument drain_duration", value=drain_duration, expected_type=type_hints["drain_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if drain_duration is not None:
            self._values["drain_duration"] = drain_duration

    @builtins.property
    def drain_duration(self) -> typing.Optional[jsii.Number]:
        '''Configures the drain duration in seconds.

        This field is only used when session affinity is enabled on the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#drain_duration DataCloudflareLoadBalancer#drain_duration}
        '''
        result = self._values.get("drain_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__85f505f8184d0f16cf09c944dbf4560f0d8104aabaf5fcf940554ba1473fa7a0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDrainDuration")
    def reset_drain_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainDuration", []))

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "headers"))

    @builtins.property
    @jsii.member(jsii_name="requireAllHeaders")
    def require_all_headers(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "requireAllHeaders"))

    @builtins.property
    @jsii.member(jsii_name="samesite")
    def samesite(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samesite"))

    @builtins.property
    @jsii.member(jsii_name="secure")
    def secure(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secure"))

    @builtins.property
    @jsii.member(jsii_name="zeroDowntimeFailover")
    def zero_downtime_failover(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zeroDowntimeFailover"))

    @builtins.property
    @jsii.member(jsii_name="drainDurationInput")
    def drain_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="drainDuration")
    def drain_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainDuration"))

    @drain_duration.setter
    def drain_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7bbf2f7909c1d4e08f272ed8a52eaa1697a819a8bf8d8094f9f75faff0d767b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributes]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1bdda3fd8de0679ae4b9de18665e24020cf050cbdf4268ba2222c8b512aa5fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerSessionAffinityAttributes",
    jsii_struct_bases=[],
    name_mapping={"drain_duration": "drainDuration"},
)
class DataCloudflareLoadBalancerSessionAffinityAttributes:
    def __init__(self, *, drain_duration: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param drain_duration: Configures the drain duration in seconds. This field is only used when session affinity is enabled on the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#drain_duration DataCloudflareLoadBalancer#drain_duration}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce184ffaadce0894bfd17d4e7b2aa13946d61ae571995a564c7cf64fd8d572df)
            check_type(argname="argument drain_duration", value=drain_duration, expected_type=type_hints["drain_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if drain_duration is not None:
            self._values["drain_duration"] = drain_duration

    @builtins.property
    def drain_duration(self) -> typing.Optional[jsii.Number]:
        '''Configures the drain duration in seconds.

        This field is only used when session affinity is enabled on the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancer#drain_duration DataCloudflareLoadBalancer#drain_duration}
        '''
        result = self._values.get("drain_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancerSessionAffinityAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancerSessionAffinityAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancer.DataCloudflareLoadBalancerSessionAffinityAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c93b951a062aff7be55ec2be7a13ac8ec958ad792f377d7651c6177e9cc28a0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDrainDuration")
    def reset_drain_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainDuration", []))

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "headers"))

    @builtins.property
    @jsii.member(jsii_name="requireAllHeaders")
    def require_all_headers(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "requireAllHeaders"))

    @builtins.property
    @jsii.member(jsii_name="samesite")
    def samesite(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samesite"))

    @builtins.property
    @jsii.member(jsii_name="secure")
    def secure(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secure"))

    @builtins.property
    @jsii.member(jsii_name="zeroDowntimeFailover")
    def zero_downtime_failover(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zeroDowntimeFailover"))

    @builtins.property
    @jsii.member(jsii_name="drainDurationInput")
    def drain_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="drainDuration")
    def drain_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainDuration"))

    @drain_duration.setter
    def drain_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd2112e2bc67049fb2305465b01c8dea70ee70e73123fffca68f31f8262e717c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancerSessionAffinityAttributes]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancerSessionAffinityAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancerSessionAffinityAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5163d4adc5f15977ea0b6986953031d647a85229aacb3c1069b14435aa043d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareLoadBalancer",
    "DataCloudflareLoadBalancerAdaptiveRouting",
    "DataCloudflareLoadBalancerAdaptiveRoutingOutputReference",
    "DataCloudflareLoadBalancerConfig",
    "DataCloudflareLoadBalancerLocationStrategy",
    "DataCloudflareLoadBalancerLocationStrategyOutputReference",
    "DataCloudflareLoadBalancerRandomSteering",
    "DataCloudflareLoadBalancerRandomSteeringOutputReference",
    "DataCloudflareLoadBalancerRules",
    "DataCloudflareLoadBalancerRulesFixedResponse",
    "DataCloudflareLoadBalancerRulesFixedResponseOutputReference",
    "DataCloudflareLoadBalancerRulesList",
    "DataCloudflareLoadBalancerRulesOutputReference",
    "DataCloudflareLoadBalancerRulesOverrides",
    "DataCloudflareLoadBalancerRulesOverridesAdaptiveRouting",
    "DataCloudflareLoadBalancerRulesOverridesAdaptiveRoutingOutputReference",
    "DataCloudflareLoadBalancerRulesOverridesLocationStrategy",
    "DataCloudflareLoadBalancerRulesOverridesLocationStrategyOutputReference",
    "DataCloudflareLoadBalancerRulesOverridesOutputReference",
    "DataCloudflareLoadBalancerRulesOverridesRandomSteering",
    "DataCloudflareLoadBalancerRulesOverridesRandomSteeringOutputReference",
    "DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributes",
    "DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributesOutputReference",
    "DataCloudflareLoadBalancerSessionAffinityAttributes",
    "DataCloudflareLoadBalancerSessionAffinityAttributesOutputReference",
]

publication.publish()

def _typecheckingstub__228c23b5cf249916f6c1a265fd5b4a547690b96262b03c26f158f1db4b7482e6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    zone_id: builtins.str,
    load_balancer_id: typing.Optional[builtins.str] = None,
    pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
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

def _typecheckingstub__8b54f40e785caf0889b0a42fb17c19adbacf09dcc7ab4db32f741c3af99a1911(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bfc82f3a8a63537948b319aae39974ab8689603a110691b51f1f11eab1acfb0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__507006ae688ed970e451df9802cbe674dacbbcd229e612bd96122863178cf376(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec31bf1e3fdbbf09428d9cf860728f994330dcac818a598b4368c498dbc59fc1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5da01379a60f8ec4a5f54d89cafcc6f0970940f09e2c9e398c5c8264b18e6570(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f726f9deacadf7c0f967b26d52b10bd9ed90dac1777777191c05365887f89e1e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf87d493245df32a0263472c8eb0649d3dafc4d1fdd1ba23a1681f9f7ffb936e(
    value: typing.Optional[DataCloudflareLoadBalancerAdaptiveRouting],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__add0817d466d09d580b593785bd67496c737aca11fb94bd54300b22d0888e9d3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: builtins.str,
    load_balancer_id: typing.Optional[builtins.str] = None,
    pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dde90654dae7df012caf6229dc63108ae2b74eaff57463a296383ff9c25551f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f562b4150009642dca4f7b29f520413785aff6e0a48b24800ec0603922a132a(
    value: typing.Optional[DataCloudflareLoadBalancerLocationStrategy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cea49206a166bf7f3c8811d0d6f9c066cc1edcfecc847bb8bd67c8933c7aa46(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dda78b2ab0bfab8e735b948c4743046c834c3fb5f1570c2d4343a716f684d3d(
    value: typing.Optional[DataCloudflareLoadBalancerRandomSteering],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8be4d9bafcbe4aad1550a96985e64d5a0486a4013a6f5b308eb05db848105185(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86592daa3f4537195c145f2ddaf90f7c08df876ddc86f933a8cfe27726552130(
    value: typing.Optional[DataCloudflareLoadBalancerRulesFixedResponse],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1155f47f91d532ad72a8452cbdc097abc751b67f0140aa47bfece1bf71ae7e15(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b75cc88e3022039af7ca2e05eb52eb70b31cc15040d9bf06bbe1636e622e9f86(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0b932699f83f9a987add957d2261013750f1e5a14052279620664ed61f50c01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef0969d6be5eeb57c9f6bd915d7e7a3fd1a5a1c931fd430ad2af7c2a3589259d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efa0ad90aeb0e2b355850508c8be108caf90c2f5c261efb73162f81e4ed090db(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3cb5c321a8e5360917f168dfbf92e59b4a18f87643c5f998ea775a5f6b32bb1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db50182f08c4e22b167773f4a9c18fad173899eca2d3f804c1199a46cefe88e4(
    value: typing.Optional[DataCloudflareLoadBalancerRules],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bb4e3de6c2ce63a6d4b6fbdbc4390cf1d7ef601b04c32a74e4218d54759038e(
    *,
    pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9029722192b826f612e50955d74356433f11572d16c8d207d4f5b8b4318c51e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dec93ac23a5554e796f52eab00877f55160dd1eb030e36c1afbac8d039f92fd1(
    value: typing.Optional[DataCloudflareLoadBalancerRulesOverridesAdaptiveRouting],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86a4ce35f0a20fc2472a86df1c3f0d89c2e8508fbb3f94209f2aebc88c9a4941(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__393824875a5d73ce7410c0ca0d5ffa10debf65cc3fe84a33894a95f757354260(
    value: typing.Optional[DataCloudflareLoadBalancerRulesOverridesLocationStrategy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2845a275180c99ec85abd29480978773c7ada544d889816d051c41549fb9324(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf81b7305ea0c7c1d7d9b5d6f3699b6c3feede0ab78b5bfe43ebfe990383e1aa(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db2469986f6beb3fe0ad4ca3f09719414846740ea8a7442f57131f5e79fccc79(
    value: typing.Optional[DataCloudflareLoadBalancerRulesOverrides],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a635aa637200a6285e6c53d37c792048af8328ba9c33f717bba2fda2b48b6f6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66bd42a7ac3ff4dbb1bde3d5a1128adee423b79b2f1bbaaa99df9105964f78d9(
    value: typing.Optional[DataCloudflareLoadBalancerRulesOverridesRandomSteering],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ef6f9f83a3886c25202b703f8e1615c1f83088fbc820f7cd09b61dee9c56145(
    *,
    drain_duration: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85f505f8184d0f16cf09c944dbf4560f0d8104aabaf5fcf940554ba1473fa7a0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7bbf2f7909c1d4e08f272ed8a52eaa1697a819a8bf8d8094f9f75faff0d767b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1bdda3fd8de0679ae4b9de18665e24020cf050cbdf4268ba2222c8b512aa5fc(
    value: typing.Optional[DataCloudflareLoadBalancerRulesOverridesSessionAffinityAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce184ffaadce0894bfd17d4e7b2aa13946d61ae571995a564c7cf64fd8d572df(
    *,
    drain_duration: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c93b951a062aff7be55ec2be7a13ac8ec958ad792f377d7651c6177e9cc28a0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd2112e2bc67049fb2305465b01c8dea70ee70e73123fffca68f31f8262e717c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5163d4adc5f15977ea0b6986953031d647a85229aacb3c1069b14435aa043d2(
    value: typing.Optional[DataCloudflareLoadBalancerSessionAffinityAttributes],
) -> None:
    """Type checking stubs"""
    pass
