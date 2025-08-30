r'''
# `data_cloudflare_api_shield_operation`

Refer to the Terraform Registry for docs: [`data_cloudflare_api_shield_operation`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation).
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


class DataCloudflareApiShieldOperation(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperation",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation cloudflare_api_shield_operation}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        zone_id: builtins.str,
        feature: typing.Optional[typing.Sequence[builtins.str]] = None,
        filter: typing.Optional[typing.Union["DataCloudflareApiShieldOperationFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        operation_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation cloudflare_api_shield_operation} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#zone_id DataCloudflareApiShieldOperation#zone_id}
        :param feature: Add feature(s) to the results. The feature name that is given here corresponds to the resulting feature object. Have a look at the top-level object description for more details on the specific meaning. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#feature DataCloudflareApiShieldOperation#feature}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#filter DataCloudflareApiShieldOperation#filter}.
        :param operation_id: UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#operation_id DataCloudflareApiShieldOperation#operation_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3403ae635eee7dfffeb4d72f5c54c4c9aaef6daa0b02af613a830f2e2321ef3d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareApiShieldOperationConfig(
            zone_id=zone_id,
            feature=feature,
            filter=filter,
            operation_id=operation_id,
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
        '''Generates CDKTF code for importing a DataCloudflareApiShieldOperation resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareApiShieldOperation to import.
        :param import_from_id: The id of the existing DataCloudflareApiShieldOperation that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareApiShieldOperation to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c52df77884850cbf65f7f5a60f61737034b58b91ac2316e44ebb76edde1f025)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        direction: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        feature: typing.Optional[typing.Sequence[builtins.str]] = None,
        host: typing.Optional[typing.Sequence[builtins.str]] = None,
        method: typing.Optional[typing.Sequence[builtins.str]] = None,
        order: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param direction: Direction to order results. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#direction DataCloudflareApiShieldOperation#direction}
        :param endpoint: Filter results to only include endpoints containing this pattern. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#endpoint DataCloudflareApiShieldOperation#endpoint}
        :param feature: Add feature(s) to the results. The feature name that is given here corresponds to the resulting feature object. Have a look at the top-level object description for more details on the specific meaning. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#feature DataCloudflareApiShieldOperation#feature}
        :param host: Filter results to only include the specified hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#host DataCloudflareApiShieldOperation#host}
        :param method: Filter results to only include the specified HTTP methods. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#method DataCloudflareApiShieldOperation#method}
        :param order: Field to order by. When requesting a feature, the feature keys are available for ordering as well, e.g., ``thresholds.suggested_threshold``. Available values: "method", "host", "endpoint", "thresholds.$key". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#order DataCloudflareApiShieldOperation#order}
        '''
        value = DataCloudflareApiShieldOperationFilter(
            direction=direction,
            endpoint=endpoint,
            feature=feature,
            host=host,
            method=method,
            order=order,
        )

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFeature")
    def reset_feature(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFeature", []))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetOperationId")
    def reset_operation_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationId", []))

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
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="features")
    def features(self) -> "DataCloudflareApiShieldOperationFeaturesOutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFeaturesOutputReference", jsii.get(self, "features"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataCloudflareApiShieldOperationFilterOutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdated")
    def last_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdated"))

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @builtins.property
    @jsii.member(jsii_name="featureInput")
    def feature_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "featureInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareApiShieldOperationFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareApiShieldOperationFilter"]], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="operationIdInput")
    def operation_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="feature")
    def feature(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "feature"))

    @feature.setter
    def feature(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__728e855c2992ccefd7af0b3a3e3072e447304eb207bd29e3a745c3250f201718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "feature", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationId")
    def operation_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operationId"))

    @operation_id.setter
    def operation_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0426e7128fb97ff51ba06316517d7da437c8e50f77817a8848ddc7f86a2a3ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ef24991815a52dbd248bbf953091db545c331753e83b36faa2a764dd8704d35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationConfig",
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
        "feature": "feature",
        "filter": "filter",
        "operation_id": "operationId",
    },
)
class DataCloudflareApiShieldOperationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        feature: typing.Optional[typing.Sequence[builtins.str]] = None,
        filter: typing.Optional[typing.Union["DataCloudflareApiShieldOperationFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        operation_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#zone_id DataCloudflareApiShieldOperation#zone_id}
        :param feature: Add feature(s) to the results. The feature name that is given here corresponds to the resulting feature object. Have a look at the top-level object description for more details on the specific meaning. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#feature DataCloudflareApiShieldOperation#feature}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#filter DataCloudflareApiShieldOperation#filter}.
        :param operation_id: UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#operation_id DataCloudflareApiShieldOperation#operation_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = DataCloudflareApiShieldOperationFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b663c6494d6839b08668ca6c0a2171c4b99a7102b12808f56aa2010faf56ae3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument feature", value=feature, expected_type=type_hints["feature"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument operation_id", value=operation_id, expected_type=type_hints["operation_id"])
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
        if feature is not None:
            self._values["feature"] = feature
        if filter is not None:
            self._values["filter"] = filter
        if operation_id is not None:
            self._values["operation_id"] = operation_id

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
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#zone_id DataCloudflareApiShieldOperation#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def feature(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Add feature(s) to the results.

        The feature name that is given here corresponds to the resulting feature object. Have a look at the top-level object description for more details on the specific meaning.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#feature DataCloudflareApiShieldOperation#feature}
        '''
        result = self._values.get("feature")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def filter(self) -> typing.Optional["DataCloudflareApiShieldOperationFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#filter DataCloudflareApiShieldOperation#filter}.'''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["DataCloudflareApiShieldOperationFilter"], result)

    @builtins.property
    def operation_id(self) -> typing.Optional[builtins.str]:
        '''UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#operation_id DataCloudflareApiShieldOperation#operation_id}
        '''
        result = self._values.get("operation_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeatures",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeatures:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeatures(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesApiRouting",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesApiRouting:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesApiRouting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesApiRoutingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesApiRoutingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ece82fb8b3dbd1263aecff6ce4677f6ed9483a93491a8986ee5ffbcfddd551ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lastUpdated")
    def last_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdated"))

    @builtins.property
    @jsii.member(jsii_name="route")
    def route(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "route"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesApiRouting]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesApiRouting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesApiRouting],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22cfeebba1509e2764712cf394463fc37118f4857a650b157a79ea029a557bee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervals",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesConfidenceIntervals:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesConfidenceIntervals(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a06735b0465b7f2a533920d08f7f5409d8d629083c3a5a6c9a69254e37cf505)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lastUpdated")
    def last_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdated"))

    @builtins.property
    @jsii.member(jsii_name="suggestedThreshold")
    def suggested_threshold(
        self,
    ) -> "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdOutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdOutputReference", jsii.get(self, "suggestedThreshold"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervals]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervals], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervals],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__230c4fddd9d9f213003728b025b7c48fd0846700d015a4703f5d7cbb4dbc21c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThreshold",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThreshold:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThreshold(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervals",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervals:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervals(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e380f0ac5741c99f7c4411a59fdecca4c19130db1f498866de3165cc9648c653)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="p90")
    def p90(
        self,
    ) -> "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90OutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90OutputReference", jsii.get(self, "p90"))

    @builtins.property
    @jsii.member(jsii_name="p95")
    def p95(
        self,
    ) -> "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95OutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95OutputReference", jsii.get(self, "p95"))

    @builtins.property
    @jsii.member(jsii_name="p99")
    def p99(
        self,
    ) -> "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99OutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99OutputReference", jsii.get(self, "p99"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervals]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervals], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervals],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2818fc86695735b3ba7804a171c21ae9ce2a84881347bc8b301d113b9f26bcbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91ec41ee8c31289508654f4bc74ac46057b06c224ac6a9c66a3895b9d62648d9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lower")
    def lower(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lower"))

    @builtins.property
    @jsii.member(jsii_name="upper")
    def upper(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "upper"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc48311f6ac3d04687ad7512e646b4cab899236eea6b600c20d466d53d175511)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__97da680e62d80bfda1d9c5268fa3d11f007d389dfef561c17f23f50b13500b47)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lower")
    def lower(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lower"))

    @builtins.property
    @jsii.member(jsii_name="upper")
    def upper(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "upper"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3179677a1332b72773560d662a7d9618967b4fec984896cf5673ed505ec69ae9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__77359c7dc75b48cd628b8e11525fcc53b48dddd8ceef758e184837daa63b79eb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lower")
    def lower(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lower"))

    @builtins.property
    @jsii.member(jsii_name="upper")
    def upper(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "upper"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70c2a17e0984537b508a1fb91ef78f5a36994a11018971bf96facd3cfb8ed2c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1647465ca96a3353c315f5644ebfa6a8bcf9f5901d5b34d0836274a136cf355)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="confidenceIntervals")
    def confidence_intervals(
        self,
    ) -> DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsOutputReference:
        return typing.cast(DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsOutputReference, jsii.get(self, "confidenceIntervals"))

    @builtins.property
    @jsii.member(jsii_name="mean")
    def mean(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mean"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThreshold]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThreshold], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThreshold],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be042186a079fd8e85cff9ea31479e34357b801ffb33cbbbcd8189448e2b8cfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareApiShieldOperationFeaturesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8f505a32d195a2e41336732d5f47c018f754fce9272d7d06a45dcc95213ec0a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="apiRouting")
    def api_routing(
        self,
    ) -> DataCloudflareApiShieldOperationFeaturesApiRoutingOutputReference:
        return typing.cast(DataCloudflareApiShieldOperationFeaturesApiRoutingOutputReference, jsii.get(self, "apiRouting"))

    @builtins.property
    @jsii.member(jsii_name="confidenceIntervals")
    def confidence_intervals(
        self,
    ) -> DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsOutputReference:
        return typing.cast(DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsOutputReference, jsii.get(self, "confidenceIntervals"))

    @builtins.property
    @jsii.member(jsii_name="parameterSchemas")
    def parameter_schemas(
        self,
    ) -> "DataCloudflareApiShieldOperationFeaturesParameterSchemasOutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFeaturesParameterSchemasOutputReference", jsii.get(self, "parameterSchemas"))

    @builtins.property
    @jsii.member(jsii_name="schemaInfo")
    def schema_info(
        self,
    ) -> "DataCloudflareApiShieldOperationFeaturesSchemaInfoOutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFeaturesSchemaInfoOutputReference", jsii.get(self, "schemaInfo"))

    @builtins.property
    @jsii.member(jsii_name="thresholds")
    def thresholds(
        self,
    ) -> "DataCloudflareApiShieldOperationFeaturesThresholdsOutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFeaturesThresholdsOutputReference", jsii.get(self, "thresholds"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeatures]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeatures], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeatures],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__414ccd60902e8cd0f54d6c28779211391d5127346e81af84a0d65096c666baf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesParameterSchemas",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesParameterSchemas:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesParameterSchemas(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesParameterSchemasOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesParameterSchemasOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1671c549293c263c4f7adca57a6b201fb19a3ff5e8a5b2fa7d0790cc4ae48b3d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lastUpdated")
    def last_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdated"))

    @builtins.property
    @jsii.member(jsii_name="parameterSchemas")
    def parameter_schemas(
        self,
    ) -> "DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemasOutputReference":
        return typing.cast("DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemasOutputReference", jsii.get(self, "parameterSchemas"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesParameterSchemas]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesParameterSchemas], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesParameterSchemas],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccc6ae3be81922d6e2b44c0c0159e277227700369f908452c81cbff3a3dadf52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemas",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemas:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemas(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemasOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemasOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e65d965e858875fe3293f2bf6f03879bbc1a0ceb01189fd51885a53407af88c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "parameters"))

    @builtins.property
    @jsii.member(jsii_name="responses")
    def responses(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responses"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemas]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemas], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemas],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45e92dd57fb63d905d8471a38ab903251763e07c190ac8c22e5d8f1cb5dab31e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesSchemaInfo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesSchemaInfo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesSchemaInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchema",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchema:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchema(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchemaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchemaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a37d83108152a5c0dac0b841af734b75922624a5342b551f4514d6c2b175a0a3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="isLearned")
    def is_learned(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "isLearned"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchema]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchema], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchema],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f0d468ce63df51573759d84327a973604878fc76ae5c4fb77d0632e7f3efe7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareApiShieldOperationFeaturesSchemaInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesSchemaInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3335b7e604930cfa45dc55f1d185b52347a152c89bad4e134bcb3aa1fe51d63e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="activeSchema")
    def active_schema(
        self,
    ) -> DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchemaOutputReference:
        return typing.cast(DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchemaOutputReference, jsii.get(self, "activeSchema"))

    @builtins.property
    @jsii.member(jsii_name="learnedAvailable")
    def learned_available(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "learnedAvailable"))

    @builtins.property
    @jsii.member(jsii_name="mitigationAction")
    def mitigation_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mitigationAction"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesSchemaInfo]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesSchemaInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesSchemaInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74339863d3996193c54db5a463f5df02dc9f6b438e7c0a0af5d1a3512fdf876a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesThresholds",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareApiShieldOperationFeaturesThresholds:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFeaturesThresholds(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFeaturesThresholdsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFeaturesThresholdsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ea193ac5b629481af3a1336df811ad3f703bd166f28aaac883c2a4ea01584e1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authIdTokens")
    def auth_id_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "authIdTokens"))

    @builtins.property
    @jsii.member(jsii_name="dataPoints")
    def data_points(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "dataPoints"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdated")
    def last_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdated"))

    @builtins.property
    @jsii.member(jsii_name="p50")
    def p50(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "p50"))

    @builtins.property
    @jsii.member(jsii_name="p90")
    def p90(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "p90"))

    @builtins.property
    @jsii.member(jsii_name="p99")
    def p99(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "p99"))

    @builtins.property
    @jsii.member(jsii_name="periodSeconds")
    def period_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "periodSeconds"))

    @builtins.property
    @jsii.member(jsii_name="requests")
    def requests(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "requests"))

    @builtins.property
    @jsii.member(jsii_name="suggestedThreshold")
    def suggested_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "suggestedThreshold"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareApiShieldOperationFeaturesThresholds]:
        return typing.cast(typing.Optional[DataCloudflareApiShieldOperationFeaturesThresholds], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareApiShieldOperationFeaturesThresholds],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d1c4d335bd7558cd9d5ca516f96be01c4c02803212f6de9de29d9ad95079ede)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFilter",
    jsii_struct_bases=[],
    name_mapping={
        "direction": "direction",
        "endpoint": "endpoint",
        "feature": "feature",
        "host": "host",
        "method": "method",
        "order": "order",
    },
)
class DataCloudflareApiShieldOperationFilter:
    def __init__(
        self,
        *,
        direction: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        feature: typing.Optional[typing.Sequence[builtins.str]] = None,
        host: typing.Optional[typing.Sequence[builtins.str]] = None,
        method: typing.Optional[typing.Sequence[builtins.str]] = None,
        order: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param direction: Direction to order results. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#direction DataCloudflareApiShieldOperation#direction}
        :param endpoint: Filter results to only include endpoints containing this pattern. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#endpoint DataCloudflareApiShieldOperation#endpoint}
        :param feature: Add feature(s) to the results. The feature name that is given here corresponds to the resulting feature object. Have a look at the top-level object description for more details on the specific meaning. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#feature DataCloudflareApiShieldOperation#feature}
        :param host: Filter results to only include the specified hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#host DataCloudflareApiShieldOperation#host}
        :param method: Filter results to only include the specified HTTP methods. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#method DataCloudflareApiShieldOperation#method}
        :param order: Field to order by. When requesting a feature, the feature keys are available for ordering as well, e.g., ``thresholds.suggested_threshold``. Available values: "method", "host", "endpoint", "thresholds.$key". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#order DataCloudflareApiShieldOperation#order}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__428c1245d254840827b3536d8f2dd5852cc9e9f2b7ab3d55b777bcc45e6dedfd)
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument feature", value=feature, expected_type=type_hints["feature"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument order", value=order, expected_type=type_hints["order"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if direction is not None:
            self._values["direction"] = direction
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if feature is not None:
            self._values["feature"] = feature
        if host is not None:
            self._values["host"] = host
        if method is not None:
            self._values["method"] = method
        if order is not None:
            self._values["order"] = order

    @builtins.property
    def direction(self) -> typing.Optional[builtins.str]:
        '''Direction to order results. Available values: "asc", "desc".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#direction DataCloudflareApiShieldOperation#direction}
        '''
        result = self._values.get("direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint(self) -> typing.Optional[builtins.str]:
        '''Filter results to only include endpoints containing this pattern.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#endpoint DataCloudflareApiShieldOperation#endpoint}
        '''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def feature(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Add feature(s) to the results.

        The feature name that is given here corresponds to the resulting feature object. Have a look at the top-level object description for more details on the specific meaning.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#feature DataCloudflareApiShieldOperation#feature}
        '''
        result = self._values.get("feature")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Filter results to only include the specified hosts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#host DataCloudflareApiShieldOperation#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def method(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Filter results to only include the specified HTTP methods.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#method DataCloudflareApiShieldOperation#method}
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''Field to order by.

        When requesting a feature, the feature keys are available for ordering as well, e.g., ``thresholds.suggested_threshold``.
        Available values: "method", "host", "endpoint", "thresholds.$key".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/api_shield_operation#order DataCloudflareApiShieldOperation#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareApiShieldOperationFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareApiShieldOperationFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareApiShieldOperation.DataCloudflareApiShieldOperationFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b51ee2463a0f57186c4d43df21c1cde43b582568a95de0795fd2eb10cbdd468f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDirection")
    def reset_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirection", []))

    @jsii.member(jsii_name="resetEndpoint")
    def reset_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoint", []))

    @jsii.member(jsii_name="resetFeature")
    def reset_feature(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFeature", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetMethod")
    def reset_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMethod", []))

    @jsii.member(jsii_name="resetOrder")
    def reset_order(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrder", []))

    @builtins.property
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property
    @jsii.member(jsii_name="featureInput")
    def feature_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "featureInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="methodInput")
    def method_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "methodInput"))

    @builtins.property
    @jsii.member(jsii_name="orderInput")
    def order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orderInput"))

    @builtins.property
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18164be50ad4d5794e0eb621585e27a45cae435f12dae36de3c4b237152f9f83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fa42b70132ce4dfd2bfc80c24c8938ccaee20aa9d936d1f4123487deae4ae2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="feature")
    def feature(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "feature"))

    @feature.setter
    def feature(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8416ce6dbb8b6cc178322851fb7585862593673460bc38dbd4bb3e7cf8cdcd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "feature", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "host"))

    @host.setter
    def host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2d0d81a7d4136eb3074a6ef998fb103edfa3ce937113bbebe81db11e2402163)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "method"))

    @method.setter
    def method(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9052cd6f313975545c0b5d2c361685f964f846513abf98156b67ade15c6206ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="order")
    def order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "order"))

    @order.setter
    def order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b59b54c25289ca5cbbc94516db6dd616ac2ad4ef55d514e595018444d6b4006)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "order", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareApiShieldOperationFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareApiShieldOperationFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareApiShieldOperationFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1178caefa91e643514ab595afd54e956b216d2bff30bf32de8ffb68695b83763)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareApiShieldOperation",
    "DataCloudflareApiShieldOperationConfig",
    "DataCloudflareApiShieldOperationFeatures",
    "DataCloudflareApiShieldOperationFeaturesApiRouting",
    "DataCloudflareApiShieldOperationFeaturesApiRoutingOutputReference",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervals",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsOutputReference",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThreshold",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervals",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsOutputReference",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90OutputReference",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95OutputReference",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99OutputReference",
    "DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdOutputReference",
    "DataCloudflareApiShieldOperationFeaturesOutputReference",
    "DataCloudflareApiShieldOperationFeaturesParameterSchemas",
    "DataCloudflareApiShieldOperationFeaturesParameterSchemasOutputReference",
    "DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemas",
    "DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemasOutputReference",
    "DataCloudflareApiShieldOperationFeaturesSchemaInfo",
    "DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchema",
    "DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchemaOutputReference",
    "DataCloudflareApiShieldOperationFeaturesSchemaInfoOutputReference",
    "DataCloudflareApiShieldOperationFeaturesThresholds",
    "DataCloudflareApiShieldOperationFeaturesThresholdsOutputReference",
    "DataCloudflareApiShieldOperationFilter",
    "DataCloudflareApiShieldOperationFilterOutputReference",
]

publication.publish()

def _typecheckingstub__3403ae635eee7dfffeb4d72f5c54c4c9aaef6daa0b02af613a830f2e2321ef3d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    zone_id: builtins.str,
    feature: typing.Optional[typing.Sequence[builtins.str]] = None,
    filter: typing.Optional[typing.Union[DataCloudflareApiShieldOperationFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    operation_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__2c52df77884850cbf65f7f5a60f61737034b58b91ac2316e44ebb76edde1f025(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__728e855c2992ccefd7af0b3a3e3072e447304eb207bd29e3a745c3250f201718(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0426e7128fb97ff51ba06316517d7da437c8e50f77817a8848ddc7f86a2a3ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ef24991815a52dbd248bbf953091db545c331753e83b36faa2a764dd8704d35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b663c6494d6839b08668ca6c0a2171c4b99a7102b12808f56aa2010faf56ae3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: builtins.str,
    feature: typing.Optional[typing.Sequence[builtins.str]] = None,
    filter: typing.Optional[typing.Union[DataCloudflareApiShieldOperationFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    operation_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ece82fb8b3dbd1263aecff6ce4677f6ed9483a93491a8986ee5ffbcfddd551ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22cfeebba1509e2764712cf394463fc37118f4857a650b157a79ea029a557bee(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesApiRouting],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a06735b0465b7f2a533920d08f7f5409d8d629083c3a5a6c9a69254e37cf505(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__230c4fddd9d9f213003728b025b7c48fd0846700d015a4703f5d7cbb4dbc21c0(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervals],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e380f0ac5741c99f7c4411a59fdecca4c19130db1f498866de3165cc9648c653(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2818fc86695735b3ba7804a171c21ae9ce2a84881347bc8b301d113b9f26bcbf(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervals],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91ec41ee8c31289508654f4bc74ac46057b06c224ac6a9c66a3895b9d62648d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc48311f6ac3d04687ad7512e646b4cab899236eea6b600c20d466d53d175511(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP90],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97da680e62d80bfda1d9c5268fa3d11f007d389dfef561c17f23f50b13500b47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3179677a1332b72773560d662a7d9618967b4fec984896cf5673ed505ec69ae9(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP95],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77359c7dc75b48cd628b8e11525fcc53b48dddd8ceef758e184837daa63b79eb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70c2a17e0984537b508a1fb91ef78f5a36994a11018971bf96facd3cfb8ed2c2(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThresholdConfidenceIntervalsP99],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1647465ca96a3353c315f5644ebfa6a8bcf9f5901d5b34d0836274a136cf355(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be042186a079fd8e85cff9ea31479e34357b801ffb33cbbbcd8189448e2b8cfb(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesConfidenceIntervalsSuggestedThreshold],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8f505a32d195a2e41336732d5f47c018f754fce9272d7d06a45dcc95213ec0a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__414ccd60902e8cd0f54d6c28779211391d5127346e81af84a0d65096c666baf1(
    value: typing.Optional[DataCloudflareApiShieldOperationFeatures],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1671c549293c263c4f7adca57a6b201fb19a3ff5e8a5b2fa7d0790cc4ae48b3d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccc6ae3be81922d6e2b44c0c0159e277227700369f908452c81cbff3a3dadf52(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesParameterSchemas],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e65d965e858875fe3293f2bf6f03879bbc1a0ceb01189fd51885a53407af88c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45e92dd57fb63d905d8471a38ab903251763e07c190ac8c22e5d8f1cb5dab31e(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesParameterSchemasParameterSchemas],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a37d83108152a5c0dac0b841af734b75922624a5342b551f4514d6c2b175a0a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f0d468ce63df51573759d84327a973604878fc76ae5c4fb77d0632e7f3efe7b(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesSchemaInfoActiveSchema],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3335b7e604930cfa45dc55f1d185b52347a152c89bad4e134bcb3aa1fe51d63e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74339863d3996193c54db5a463f5df02dc9f6b438e7c0a0af5d1a3512fdf876a(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesSchemaInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ea193ac5b629481af3a1336df811ad3f703bd166f28aaac883c2a4ea01584e1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d1c4d335bd7558cd9d5ca516f96be01c4c02803212f6de9de29d9ad95079ede(
    value: typing.Optional[DataCloudflareApiShieldOperationFeaturesThresholds],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__428c1245d254840827b3536d8f2dd5852cc9e9f2b7ab3d55b777bcc45e6dedfd(
    *,
    direction: typing.Optional[builtins.str] = None,
    endpoint: typing.Optional[builtins.str] = None,
    feature: typing.Optional[typing.Sequence[builtins.str]] = None,
    host: typing.Optional[typing.Sequence[builtins.str]] = None,
    method: typing.Optional[typing.Sequence[builtins.str]] = None,
    order: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b51ee2463a0f57186c4d43df21c1cde43b582568a95de0795fd2eb10cbdd468f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18164be50ad4d5794e0eb621585e27a45cae435f12dae36de3c4b237152f9f83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fa42b70132ce4dfd2bfc80c24c8938ccaee20aa9d936d1f4123487deae4ae2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8416ce6dbb8b6cc178322851fb7585862593673460bc38dbd4bb3e7cf8cdcd8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d0d81a7d4136eb3074a6ef998fb103edfa3ce937113bbebe81db11e2402163(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9052cd6f313975545c0b5d2c361685f964f846513abf98156b67ade15c6206ba(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b59b54c25289ca5cbbc94516db6dd616ac2ad4ef55d514e595018444d6b4006(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1178caefa91e643514ab595afd54e956b216d2bff30bf32de8ffb68695b83763(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareApiShieldOperationFilter]],
) -> None:
    """Type checking stubs"""
    pass
