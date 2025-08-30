r'''
# `data_cloudflare_load_balancers`

Refer to the Terraform Registry for docs: [`data_cloudflare_load_balancers`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers).
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


class DataCloudflareLoadBalancers(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancers",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers cloudflare_load_balancers}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        zone_id: builtins.str,
        max_items: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers cloudflare_load_balancers} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#zone_id DataCloudflareLoadBalancers#zone_id}.
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#max_items DataCloudflareLoadBalancers#max_items}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8f9173acf2fd3ec519a3896abc30055f6ebed2b98f059505f19ac7ad5cbb0d1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareLoadBalancersConfig(
            zone_id=zone_id,
            max_items=max_items,
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
        '''Generates CDKTF code for importing a DataCloudflareLoadBalancers resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareLoadBalancers to import.
        :param import_from_id: The id of the existing DataCloudflareLoadBalancers that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareLoadBalancers to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6ee7a4be4b1dc13b5f7d0e64646ae75738e1b3dc0114855534c5b7e2300cc1b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetMaxItems")
    def reset_max_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxItems", []))

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
    @jsii.member(jsii_name="result")
    def result(self) -> "DataCloudflareLoadBalancersResultList":
        return typing.cast("DataCloudflareLoadBalancersResultList", jsii.get(self, "result"))

    @builtins.property
    @jsii.member(jsii_name="maxItemsInput")
    def max_items_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxItemsInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="maxItems")
    def max_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxItems"))

    @max_items.setter
    def max_items(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4972f3d76ede43de6f312a0b0fd67e3807cc55016b86b6299335eec682304bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxItems", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8dfb195c46a89676328535111053ac50e154ceb2328022f5ed32c324e91f667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersConfig",
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
        "max_items": "maxItems",
    },
)
class DataCloudflareLoadBalancersConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        max_items: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#zone_id DataCloudflareLoadBalancers#zone_id}.
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#max_items DataCloudflareLoadBalancers#max_items}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef818e91f5e28b378def0ab67989ae3b1b4995dc321b2e6210f88538ddc75daa)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument max_items", value=max_items, expected_type=type_hints["max_items"])
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
        if max_items is not None:
            self._values["max_items"] = max_items

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#zone_id DataCloudflareLoadBalancers#zone_id}.'''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_items(self) -> typing.Optional[jsii.Number]:
        '''Max items to fetch, default: 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#max_items DataCloudflareLoadBalancers#max_items}
        '''
        result = self._values.get("max_items")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResult",
    jsii_struct_bases=[],
    name_mapping={
        "country_pools": "countryPools",
        "pop_pools": "popPools",
        "region_pools": "regionPools",
    },
)
class DataCloudflareLoadBalancersResult:
    def __init__(
        self,
        *,
        country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    ) -> None:
        '''
        :param country_pools: A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country. Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#country_pools DataCloudflareLoadBalancers#country_pools}
        :param pop_pools: Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter). Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#pop_pools DataCloudflareLoadBalancers#pop_pools}
        :param region_pools: A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region. Any regions not explicitly defined will fall back to using default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#region_pools DataCloudflareLoadBalancers#region_pools}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cf38618086a7fb91ede3f3242f3883b5dcef1f0313cfcf3f873f39d0d536593)
            check_type(argname="argument country_pools", value=country_pools, expected_type=type_hints["country_pools"])
            check_type(argname="argument pop_pools", value=pop_pools, expected_type=type_hints["pop_pools"])
            check_type(argname="argument region_pools", value=region_pools, expected_type=type_hints["region_pools"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if country_pools is not None:
            self._values["country_pools"] = country_pools
        if pop_pools is not None:
            self._values["pop_pools"] = pop_pools
        if region_pools is not None:
            self._values["region_pools"] = region_pools

    @builtins.property
    def country_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country.

        Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#country_pools DataCloudflareLoadBalancers#country_pools}
        '''
        result = self._values.get("country_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def pop_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter).

        Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#pop_pools DataCloudflareLoadBalancers#pop_pools}
        '''
        result = self._values.get("pop_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def region_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region.

        Any regions not explicitly defined will fall back to using default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#region_pools DataCloudflareLoadBalancers#region_pools}
        '''
        result = self._values.get("region_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultAdaptiveRouting",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancersResultAdaptiveRouting:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultAdaptiveRouting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancersResultAdaptiveRoutingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultAdaptiveRoutingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e86ef0328355659cb11b33aaccda1671b41ea4d2490f33dde6b8ddb89bd7666)
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
    ) -> typing.Optional[DataCloudflareLoadBalancersResultAdaptiveRouting]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultAdaptiveRouting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultAdaptiveRouting],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25fe289e3b5e78f234e1cdc931f5ea5159717129add72fbe5c30c858deff2d71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareLoadBalancersResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e223ddc1778473ea78d3cdeb4157e07664f9e6c54d970b1ff9237a479cc5e85)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareLoadBalancersResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a763cb3b15d70da803f2c96754582118c78804a10e3002271295c503b4cce94c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareLoadBalancersResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8234f05e692c7a0576f27a67afa7cbcbfe3b04bfb8766f82447134ccc26fc725)
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
            type_hints = typing.get_type_hints(_typecheckingstub__687768607362bf99e0f94236ad09956fed985e59f5363ec1b15ba8133c0570ab)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dbd799a03bfb191884e4e49f82e9df577adf6ad208447d3004627050255907c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataCloudflareLoadBalancersResult]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataCloudflareLoadBalancersResult]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataCloudflareLoadBalancersResult]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8699a745e5e679f4ea4832200f42de2e4677c9e359250ce6a0a4ab96503eedc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultLocationStrategy",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancersResultLocationStrategy:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultLocationStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancersResultLocationStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultLocationStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4d74e5719a8ab535182f4b829bd5a2b90df74859d63f2fe3256241fa0649b147)
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
    ) -> typing.Optional[DataCloudflareLoadBalancersResultLocationStrategy]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultLocationStrategy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultLocationStrategy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__340cecdbadd3c78f66caccee4e25bb9922187cb783c2ac3b0b1d3ae1a5ef7397)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareLoadBalancersResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad921ed48d5ec8ee014c9ab76ae4bc01464c3602aea17e0f03de10f8bbf9c5e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCountryPools")
    def reset_country_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountryPools", []))

    @jsii.member(jsii_name="resetPopPools")
    def reset_pop_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPopPools", []))

    @jsii.member(jsii_name="resetRegionPools")
    def reset_region_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionPools", []))

    @builtins.property
    @jsii.member(jsii_name="adaptiveRouting")
    def adaptive_routing(
        self,
    ) -> DataCloudflareLoadBalancersResultAdaptiveRoutingOutputReference:
        return typing.cast(DataCloudflareLoadBalancersResultAdaptiveRoutingOutputReference, jsii.get(self, "adaptiveRouting"))

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
    ) -> DataCloudflareLoadBalancersResultLocationStrategyOutputReference:
        return typing.cast(DataCloudflareLoadBalancersResultLocationStrategyOutputReference, jsii.get(self, "locationStrategy"))

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
    ) -> "DataCloudflareLoadBalancersResultRandomSteeringOutputReference":
        return typing.cast("DataCloudflareLoadBalancersResultRandomSteeringOutputReference", jsii.get(self, "randomSteering"))

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> "DataCloudflareLoadBalancersResultRulesList":
        return typing.cast("DataCloudflareLoadBalancersResultRulesList", jsii.get(self, "rules"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinity")
    def session_affinity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionAffinity"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityAttributes")
    def session_affinity_attributes(
        self,
    ) -> "DataCloudflareLoadBalancersResultSessionAffinityAttributesOutputReference":
        return typing.cast("DataCloudflareLoadBalancersResultSessionAffinityAttributesOutputReference", jsii.get(self, "sessionAffinityAttributes"))

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
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @builtins.property
    @jsii.member(jsii_name="countryPoolsInput")
    def country_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "countryPoolsInput"))

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
    @jsii.member(jsii_name="countryPools")
    def country_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "countryPools"))

    @country_pools.setter
    def country_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5b1b5efdaca79c214ab0191990c6374c1c11b12904f18a46ffbf2e222b1e1a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryPools", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__403a0420da30536183cf09a5d72b167985c3d5290d80eac84448a503bec42d65)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0bb58b9e00926650f82ed4cf8923b4bb9d01f48844c6cdb1606ab2867aa0a9a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataCloudflareLoadBalancersResult]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2ebc82a6772ede3e97729c5bcf54ed206af9b545c405a58566bcf52903f90c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRandomSteering",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancersResultRandomSteering:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultRandomSteering(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancersResultRandomSteeringOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRandomSteeringOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2546a12ab6ffbb16c669894b0b2c15cbb4f3a038085a7c84b327758c8a648a0)
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
    ) -> typing.Optional[DataCloudflareLoadBalancersResultRandomSteering]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultRandomSteering], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultRandomSteering],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bf3c96adc6e61cc11d0b6b6bc6945337737b2ffe16145ead8619bd5267d4298)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRules",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancersResultRules:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesFixedResponse",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancersResultRulesFixedResponse:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultRulesFixedResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancersResultRulesFixedResponseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesFixedResponseOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1176406adcffcda8eb037a70091f2b76e2d7c7df9cfafb9ba509a36537a80690)
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
    ) -> typing.Optional[DataCloudflareLoadBalancersResultRulesFixedResponse]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultRulesFixedResponse], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultRulesFixedResponse],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce116b38b3f365ef1f55b18c5b043bce5875f9547778003016c936e2ec6eb056)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareLoadBalancersResultRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0e2965968e584e22d882e5d845467ec4b7aa6c25811021bce4657a512c5f559)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareLoadBalancersResultRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29a79177419bd771fa7031477b59c6e7a69caa8484994896c76bf14d230cc185)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareLoadBalancersResultRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efa06a7b6983f0214df41254584562c2b5c78a566dea7de3a1d38ab7d5aed61b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4233e0c07597976f4df0c8ffac2aa003891f45b4a5e73ac7873e4f31f3c41ff4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b833fea23b767bc75b48f9abcbbaf02e679533ca6c166c7bacf8d6ea8fe5173)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareLoadBalancersResultRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e46414ec37131f61dca867f0fecf4d90a6401291d882238f1cf8ed5047b2a9c)
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
    ) -> DataCloudflareLoadBalancersResultRulesFixedResponseOutputReference:
        return typing.cast(DataCloudflareLoadBalancersResultRulesFixedResponseOutputReference, jsii.get(self, "fixedResponse"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="overrides")
    def overrides(
        self,
    ) -> "DataCloudflareLoadBalancersResultRulesOverridesOutputReference":
        return typing.cast("DataCloudflareLoadBalancersResultRulesOverridesOutputReference", jsii.get(self, "overrides"))

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
    def internal_value(self) -> typing.Optional[DataCloudflareLoadBalancersResultRules]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultRules],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dde9337467a1dc51b84bf7d4f851b9dea6374956ee96fac0dab98251cd296b7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverrides",
    jsii_struct_bases=[],
    name_mapping={
        "country_pools": "countryPools",
        "pop_pools": "popPools",
        "region_pools": "regionPools",
    },
)
class DataCloudflareLoadBalancersResultRulesOverrides:
    def __init__(
        self,
        *,
        country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    ) -> None:
        '''
        :param country_pools: A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country. Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#country_pools DataCloudflareLoadBalancers#country_pools}
        :param pop_pools: Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter). Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#pop_pools DataCloudflareLoadBalancers#pop_pools}
        :param region_pools: A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region. Any regions not explicitly defined will fall back to using default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#region_pools DataCloudflareLoadBalancers#region_pools}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__748af9a9f547c085f2b836314be65e2a93332a9034553db3a3cc8c9e6855fdc6)
            check_type(argname="argument country_pools", value=country_pools, expected_type=type_hints["country_pools"])
            check_type(argname="argument pop_pools", value=pop_pools, expected_type=type_hints["pop_pools"])
            check_type(argname="argument region_pools", value=region_pools, expected_type=type_hints["region_pools"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if country_pools is not None:
            self._values["country_pools"] = country_pools
        if pop_pools is not None:
            self._values["pop_pools"] = pop_pools
        if region_pools is not None:
            self._values["region_pools"] = region_pools

    @builtins.property
    def country_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country.

        Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#country_pools DataCloudflareLoadBalancers#country_pools}
        '''
        result = self._values.get("country_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def pop_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter).

        Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#pop_pools DataCloudflareLoadBalancers#pop_pools}
        '''
        result = self._values.get("pop_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def region_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region.

        Any regions not explicitly defined will fall back to using default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#region_pools DataCloudflareLoadBalancers#region_pools}
        '''
        result = self._values.get("region_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultRulesOverrides(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRouting",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRouting:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRouting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRoutingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRoutingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1711a6f2c5dfdc1f0199e0da43896e3b521c524d2cd8a4d5623a7e95ab3ab69c)
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
    ) -> typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRouting]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRouting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRouting],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7686ea1b76e87ec769c67c093b7c5ff3ddd9871dece6591811a99e7b3b5c6da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverridesLocationStrategy",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancersResultRulesOverridesLocationStrategy:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultRulesOverridesLocationStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancersResultRulesOverridesLocationStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverridesLocationStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2649d69519a81a85b0f35533f114e5249a91b07850f805532fd8022db292e7e)
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
    ) -> typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesLocationStrategy]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesLocationStrategy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesLocationStrategy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df4f602a1b29701bc3e10e6892664d2a4805a89831f690dd665dd21c2679b68a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareLoadBalancersResultRulesOverridesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverridesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea1436342fa62a2a5e5a475bbc21b02e627b0b96cf7a596d6ddce068998f135e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCountryPools")
    def reset_country_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountryPools", []))

    @jsii.member(jsii_name="resetPopPools")
    def reset_pop_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPopPools", []))

    @jsii.member(jsii_name="resetRegionPools")
    def reset_region_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionPools", []))

    @builtins.property
    @jsii.member(jsii_name="adaptiveRouting")
    def adaptive_routing(
        self,
    ) -> DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRoutingOutputReference:
        return typing.cast(DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRoutingOutputReference, jsii.get(self, "adaptiveRouting"))

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
    ) -> DataCloudflareLoadBalancersResultRulesOverridesLocationStrategyOutputReference:
        return typing.cast(DataCloudflareLoadBalancersResultRulesOverridesLocationStrategyOutputReference, jsii.get(self, "locationStrategy"))

    @builtins.property
    @jsii.member(jsii_name="randomSteering")
    def random_steering(
        self,
    ) -> "DataCloudflareLoadBalancersResultRulesOverridesRandomSteeringOutputReference":
        return typing.cast("DataCloudflareLoadBalancersResultRulesOverridesRandomSteeringOutputReference", jsii.get(self, "randomSteering"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinity")
    def session_affinity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionAffinity"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityAttributes")
    def session_affinity_attributes(
        self,
    ) -> "DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributesOutputReference":
        return typing.cast("DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributesOutputReference", jsii.get(self, "sessionAffinityAttributes"))

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
    @jsii.member(jsii_name="countryPoolsInput")
    def country_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "countryPoolsInput"))

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
    @jsii.member(jsii_name="countryPools")
    def country_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "countryPools"))

    @country_pools.setter
    def country_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8db4e63ec31d86cffb8da0f6503b9f1356ba70f97f5f16cb2fd14aa16996751d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryPools", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__d2662ace04a36668135c3564cd0568e392f5dc92c9acf16812ab26b049b7ec3f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__da540db2fb8594c7a6e15f7a178606416908c7ad2fc0873f7800781dbeea8134)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancersResultRulesOverrides]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultRulesOverrides], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverrides],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__728c580734cf6ea3a9b807c35d064c36e7fa5ade959aac45c1c2bbc2cf742e3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverridesRandomSteering",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareLoadBalancersResultRulesOverridesRandomSteering:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultRulesOverridesRandomSteering(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancersResultRulesOverridesRandomSteeringOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverridesRandomSteeringOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee363c3d46d336680950a7398a03b13e131597e26151a3961117a0d703979a7f)
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
    ) -> typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesRandomSteering]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesRandomSteering], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesRandomSteering],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cef216dd5eb81fbb3de09acf25e416024ab603b5d7c637eade60321fd71f7f0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributes",
    jsii_struct_bases=[],
    name_mapping={"drain_duration": "drainDuration"},
)
class DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributes:
    def __init__(self, *, drain_duration: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param drain_duration: Configures the drain duration in seconds. This field is only used when session affinity is enabled on the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#drain_duration DataCloudflareLoadBalancers#drain_duration}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49fef3bd78827e29ece3486ff9d73a5df8ac601e9eb4e192bdbd8b780bb4046f)
            check_type(argname="argument drain_duration", value=drain_duration, expected_type=type_hints["drain_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if drain_duration is not None:
            self._values["drain_duration"] = drain_duration

    @builtins.property
    def drain_duration(self) -> typing.Optional[jsii.Number]:
        '''Configures the drain duration in seconds.

        This field is only used when session affinity is enabled on the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#drain_duration DataCloudflareLoadBalancers#drain_duration}
        '''
        result = self._values.get("drain_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9d8f24f6abad8c4a1af66ce614a11fa0c7b629079f39d6c48824bb238c63235e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__41e51ccb18a0fbf2b3b933fe9fc93fdca2b3b110ce9862ec9986b15b9bfc7324)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributes]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa67324cbbba7d722049e04fdd8ec4eb072c409cbcb5081093b147c75dc65d80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultSessionAffinityAttributes",
    jsii_struct_bases=[],
    name_mapping={"drain_duration": "drainDuration"},
)
class DataCloudflareLoadBalancersResultSessionAffinityAttributes:
    def __init__(self, *, drain_duration: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param drain_duration: Configures the drain duration in seconds. This field is only used when session affinity is enabled on the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#drain_duration DataCloudflareLoadBalancers#drain_duration}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f88713d5c5a401e58534c66612ccce44655c6ef7eebdab4289a8384b562b506)
            check_type(argname="argument drain_duration", value=drain_duration, expected_type=type_hints["drain_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if drain_duration is not None:
            self._values["drain_duration"] = drain_duration

    @builtins.property
    def drain_duration(self) -> typing.Optional[jsii.Number]:
        '''Configures the drain duration in seconds.

        This field is only used when session affinity is enabled on the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/load_balancers#drain_duration DataCloudflareLoadBalancers#drain_duration}
        '''
        result = self._values.get("drain_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareLoadBalancersResultSessionAffinityAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareLoadBalancersResultSessionAffinityAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareLoadBalancers.DataCloudflareLoadBalancersResultSessionAffinityAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f717252df6ea8c4fef7e5f1368b75e0bf865ba92b2a53758eeb4fe2bd6bcff1f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b60c7d33679c09ee6d9e2bedbde4f697d107ad1819c5472a561b8344bbaf48c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareLoadBalancersResultSessionAffinityAttributes]:
        return typing.cast(typing.Optional[DataCloudflareLoadBalancersResultSessionAffinityAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareLoadBalancersResultSessionAffinityAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad1f4deea08222e2c327d47c9d0a53a3b83218fd178b2a3a9367d2f320ff2616)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareLoadBalancers",
    "DataCloudflareLoadBalancersConfig",
    "DataCloudflareLoadBalancersResult",
    "DataCloudflareLoadBalancersResultAdaptiveRouting",
    "DataCloudflareLoadBalancersResultAdaptiveRoutingOutputReference",
    "DataCloudflareLoadBalancersResultList",
    "DataCloudflareLoadBalancersResultLocationStrategy",
    "DataCloudflareLoadBalancersResultLocationStrategyOutputReference",
    "DataCloudflareLoadBalancersResultOutputReference",
    "DataCloudflareLoadBalancersResultRandomSteering",
    "DataCloudflareLoadBalancersResultRandomSteeringOutputReference",
    "DataCloudflareLoadBalancersResultRules",
    "DataCloudflareLoadBalancersResultRulesFixedResponse",
    "DataCloudflareLoadBalancersResultRulesFixedResponseOutputReference",
    "DataCloudflareLoadBalancersResultRulesList",
    "DataCloudflareLoadBalancersResultRulesOutputReference",
    "DataCloudflareLoadBalancersResultRulesOverrides",
    "DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRouting",
    "DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRoutingOutputReference",
    "DataCloudflareLoadBalancersResultRulesOverridesLocationStrategy",
    "DataCloudflareLoadBalancersResultRulesOverridesLocationStrategyOutputReference",
    "DataCloudflareLoadBalancersResultRulesOverridesOutputReference",
    "DataCloudflareLoadBalancersResultRulesOverridesRandomSteering",
    "DataCloudflareLoadBalancersResultRulesOverridesRandomSteeringOutputReference",
    "DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributes",
    "DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributesOutputReference",
    "DataCloudflareLoadBalancersResultSessionAffinityAttributes",
    "DataCloudflareLoadBalancersResultSessionAffinityAttributesOutputReference",
]

publication.publish()

def _typecheckingstub__a8f9173acf2fd3ec519a3896abc30055f6ebed2b98f059505f19ac7ad5cbb0d1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    zone_id: builtins.str,
    max_items: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__c6ee7a4be4b1dc13b5f7d0e64646ae75738e1b3dc0114855534c5b7e2300cc1b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4972f3d76ede43de6f312a0b0fd67e3807cc55016b86b6299335eec682304bf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8dfb195c46a89676328535111053ac50e154ceb2328022f5ed32c324e91f667(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef818e91f5e28b378def0ab67989ae3b1b4995dc321b2e6210f88538ddc75daa(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: builtins.str,
    max_items: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cf38618086a7fb91ede3f3242f3883b5dcef1f0313cfcf3f873f39d0d536593(
    *,
    country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e86ef0328355659cb11b33aaccda1671b41ea4d2490f33dde6b8ddb89bd7666(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25fe289e3b5e78f234e1cdc931f5ea5159717129add72fbe5c30c858deff2d71(
    value: typing.Optional[DataCloudflareLoadBalancersResultAdaptiveRouting],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e223ddc1778473ea78d3cdeb4157e07664f9e6c54d970b1ff9237a479cc5e85(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a763cb3b15d70da803f2c96754582118c78804a10e3002271295c503b4cce94c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8234f05e692c7a0576f27a67afa7cbcbfe3b04bfb8766f82447134ccc26fc725(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__687768607362bf99e0f94236ad09956fed985e59f5363ec1b15ba8133c0570ab(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbd799a03bfb191884e4e49f82e9df577adf6ad208447d3004627050255907c0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8699a745e5e679f4ea4832200f42de2e4677c9e359250ce6a0a4ab96503eedc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataCloudflareLoadBalancersResult]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d74e5719a8ab535182f4b829bd5a2b90df74859d63f2fe3256241fa0649b147(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__340cecdbadd3c78f66caccee4e25bb9922187cb783c2ac3b0b1d3ae1a5ef7397(
    value: typing.Optional[DataCloudflareLoadBalancersResultLocationStrategy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad921ed48d5ec8ee014c9ab76ae4bc01464c3602aea17e0f03de10f8bbf9c5e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5b1b5efdaca79c214ab0191990c6374c1c11b12904f18a46ffbf2e222b1e1a3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__403a0420da30536183cf09a5d72b167985c3d5290d80eac84448a503bec42d65(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bb58b9e00926650f82ed4cf8923b4bb9d01f48844c6cdb1606ab2867aa0a9a9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2ebc82a6772ede3e97729c5bcf54ed206af9b545c405a58566bcf52903f90c0(
    value: typing.Optional[DataCloudflareLoadBalancersResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2546a12ab6ffbb16c669894b0b2c15cbb4f3a038085a7c84b327758c8a648a0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bf3c96adc6e61cc11d0b6b6bc6945337737b2ffe16145ead8619bd5267d4298(
    value: typing.Optional[DataCloudflareLoadBalancersResultRandomSteering],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1176406adcffcda8eb037a70091f2b76e2d7c7df9cfafb9ba509a36537a80690(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce116b38b3f365ef1f55b18c5b043bce5875f9547778003016c936e2ec6eb056(
    value: typing.Optional[DataCloudflareLoadBalancersResultRulesFixedResponse],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0e2965968e584e22d882e5d845467ec4b7aa6c25811021bce4657a512c5f559(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29a79177419bd771fa7031477b59c6e7a69caa8484994896c76bf14d230cc185(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efa06a7b6983f0214df41254584562c2b5c78a566dea7de3a1d38ab7d5aed61b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4233e0c07597976f4df0c8ffac2aa003891f45b4a5e73ac7873e4f31f3c41ff4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b833fea23b767bc75b48f9abcbbaf02e679533ca6c166c7bacf8d6ea8fe5173(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e46414ec37131f61dca867f0fecf4d90a6401291d882238f1cf8ed5047b2a9c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dde9337467a1dc51b84bf7d4f851b9dea6374956ee96fac0dab98251cd296b7e(
    value: typing.Optional[DataCloudflareLoadBalancersResultRules],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__748af9a9f547c085f2b836314be65e2a93332a9034553db3a3cc8c9e6855fdc6(
    *,
    country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1711a6f2c5dfdc1f0199e0da43896e3b521c524d2cd8a4d5623a7e95ab3ab69c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7686ea1b76e87ec769c67c093b7c5ff3ddd9871dece6591811a99e7b3b5c6da(
    value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesAdaptiveRouting],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2649d69519a81a85b0f35533f114e5249a91b07850f805532fd8022db292e7e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df4f602a1b29701bc3e10e6892664d2a4805a89831f690dd665dd21c2679b68a(
    value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesLocationStrategy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea1436342fa62a2a5e5a475bbc21b02e627b0b96cf7a596d6ddce068998f135e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8db4e63ec31d86cffb8da0f6503b9f1356ba70f97f5f16cb2fd14aa16996751d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2662ace04a36668135c3564cd0568e392f5dc92c9acf16812ab26b049b7ec3f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da540db2fb8594c7a6e15f7a178606416908c7ad2fc0873f7800781dbeea8134(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__728c580734cf6ea3a9b807c35d064c36e7fa5ade959aac45c1c2bbc2cf742e3d(
    value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverrides],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee363c3d46d336680950a7398a03b13e131597e26151a3961117a0d703979a7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cef216dd5eb81fbb3de09acf25e416024ab603b5d7c637eade60321fd71f7f0a(
    value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesRandomSteering],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49fef3bd78827e29ece3486ff9d73a5df8ac601e9eb4e192bdbd8b780bb4046f(
    *,
    drain_duration: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d8f24f6abad8c4a1af66ce614a11fa0c7b629079f39d6c48824bb238c63235e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41e51ccb18a0fbf2b3b933fe9fc93fdca2b3b110ce9862ec9986b15b9bfc7324(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa67324cbbba7d722049e04fdd8ec4eb072c409cbcb5081093b147c75dc65d80(
    value: typing.Optional[DataCloudflareLoadBalancersResultRulesOverridesSessionAffinityAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f88713d5c5a401e58534c66612ccce44655c6ef7eebdab4289a8384b562b506(
    *,
    drain_duration: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f717252df6ea8c4fef7e5f1368b75e0bf865ba92b2a53758eeb4fe2bd6bcff1f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b60c7d33679c09ee6d9e2bedbde4f697d107ad1819c5472a561b8344bbaf48c8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad1f4deea08222e2c327d47c9d0a53a3b83218fd178b2a3a9367d2f320ff2616(
    value: typing.Optional[DataCloudflareLoadBalancersResultSessionAffinityAttributes],
) -> None:
    """Type checking stubs"""
    pass
