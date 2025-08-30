r'''
# `data_cloudflare_zero_trust_access_policies`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_access_policies`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies).
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


class DataCloudflareZeroTrustAccessPolicies(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPolicies",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies cloudflare_zero_trust_access_policies}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        max_items: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies cloudflare_zero_trust_access_policies} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies#account_id DataCloudflareZeroTrustAccessPolicies#account_id}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies#max_items DataCloudflareZeroTrustAccessPolicies#max_items}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59c074b60d731cb86890f4579f6845d61c180aeff4cba864c6d96d071ed18db5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustAccessPoliciesConfig(
            account_id=account_id,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustAccessPolicies resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustAccessPolicies to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustAccessPolicies that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustAccessPolicies to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d890e9ce752804ea4911790c3bcda9d2bb952db163d150367d09f9ce0c188208)
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
    def result(self) -> "DataCloudflareZeroTrustAccessPoliciesResultList":
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultList", jsii.get(self, "result"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="maxItemsInput")
    def max_items_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxItemsInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2710605826f7a926df7df198531cef27474880d9ac0a0ed27560a871017b89c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxItems")
    def max_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxItems"))

    @max_items.setter
    def max_items(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a01eda5d8d16189b6462894feb6e5fd0a2d2d2a22903d3a3b537ddddf62a14a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxItems", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesConfig",
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
        "max_items": "maxItems",
    },
)
class DataCloudflareZeroTrustAccessPoliciesConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies#account_id DataCloudflareZeroTrustAccessPolicies#account_id}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies#max_items DataCloudflareZeroTrustAccessPolicies#max_items}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3873650d1478549c4dbda7ba7618eda5b740a576951cdf65d52d6a5126a8d859)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument max_items", value=max_items, expected_type=type_hints["max_items"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
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
    def account_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies#account_id DataCloudflareZeroTrustAccessPolicies#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_items(self) -> typing.Optional[jsii.Number]:
        '''Max items to fetch, default: 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_policies#max_items DataCloudflareZeroTrustAccessPolicies#max_items}
        '''
        result = self._values.get("max_items")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultApprovalGroups",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultApprovalGroups:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultApprovalGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__86935878d67e9ce2c8956ebf2106b911eca2faa3ae2e6bd187839c33fcaa6202)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a247f7d9b851a470e8ae9bb0d2667a547bb00d2978e8fba7bc486bb6e72d78a2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__589407939071f3bdadb65ee25482ae620c7e3b7d590d4368fe7414ac0d6d0518)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e7746cbf7c4ed308651972bc7990ea2f305a77121d18aa85aa0c94adc6a30ce)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1bb9e340e5120693da6b8d6d4dfe6790c27b8fc2b9cba62c914f88e66b490d61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c84f59eff04ce123f22cf0b60011d689c226555847bda6fbe14709ee546406d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="approvalsNeeded")
    def approvals_needed(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "approvalsNeeded"))

    @builtins.property
    @jsii.member(jsii_name="emailAddresses")
    def email_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "emailAddresses"))

    @builtins.property
    @jsii.member(jsii_name="emailListUuid")
    def email_list_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailListUuid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultApprovalGroups]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultApprovalGroups], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultApprovalGroups],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be1bd196ea9d7d1569fba1ed5ef8850236bd8938d5c954781d5b23fa16ffe4f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExclude",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExclude:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1ea7bf0fc93076b71262b87ec83c7ab32c82c876a485494bad156fa6a1b276a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__082622491da8d9b93ddf99565b036fdac868c4c71df942869636f6cf603a8314)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__25867eba9c9ac8f2488e49b1da9e91491e05882a1f4731ae1862dd7c0e899e60)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="acId")
    def ac_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acId"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69092ffc4c1a1d253c7d4f33eecc1778a5a2112ec097d7baa8277afb555ae68b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac1c0084d11cc96708d4e2f230136f4aea285ee5fdbb68836cffc2bf5d1a78e0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c82f4cb9cb48b07b988978c10b0d82b6f74d8e6230c8459675fd552f19fb512)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3021d5d630c62e00ef93ac125d3738eb3a872de7a3fad113984ec5225befc1c2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfb3fbc2d00695519caf642e2b910aae8b68aca47b6e8df5f834b0b5d6a2ba48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd073de104b7742af7ae3c005f077859a3d35f1392f5d11ec030bc245f3e9aef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86181fb036c4fb067dd8c32848c80af4a1ee493c7f357807d3f6468f20ed2fb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__46caaf32be8cfbb504a24de253791c95da266a3ff4ccb2cc0c52c80389bcceed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7a27c44b8e2de71dfc762ce54c19269eec988305d842aff358f44c13017e1df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32914e068d363ebbed5c79bc65f6cb732982819d517e8b0700f3af9f40374fec)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="integrationUid")
    def integration_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationUid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__345e0661cd0e4082d46d6bc93af717dd7e39807686bab84542230a55af83f42a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__456087e90a13edc5853c40a464f11d5104faca020f51e3deab86a0a40c4bbb17)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3332716f56519bbc856c3d79860deb937c9f34d9c58ab18217cb582aab3c7ca9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b100e96d392183fd2c901be0543e1a8f57171b6864a5b1e4b74397115251ce9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39b79a17cdb36bddc5d50931435bdc363e52ee59fc793e0a0643da97a98985dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab5dcb7f11054ddc68c5aef9234e98564de96dfa6f5329fd9fc9266e31c93ddd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67cef74280cc34ea7878ad2d0e60b6fe6f8122f45a94014d90f6b94327acd496)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e9e00a3cbf05c8d5d5779c59e20965e1b5e9bfac4965cc847eaf218c9e326e2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__495828837349475f200e32f7090ebbe248ea89aae54a42f4ce8e8c1d4244f515)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26b6966ab0ebabc94cc3c85234d8d8c7ca72a7e1992dea379d2e2d6327911018)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="evaluateUrl")
    def evaluate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evaluateUrl"))

    @builtins.property
    @jsii.member(jsii_name="keysUrl")
    def keys_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keysUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5dd82293c5bc0365c1861f576ac90a1dcf248366ce7c6d35ed398680de64236)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__55360ddf99ef448622ac26e05ae98769ccffb050a7dc8faf9fb13d980599d609)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="countryCode")
    def country_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "countryCode"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90f4e8cc9e986cc484047fef56ff5e7eb95a444bd51d4cbe94d3b78102ecf297)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b369aafcc309267c7dcce5fba78b0a03c593674fc10811087f9fe9108a0dffcf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35d2bccfe9624dd68053050fcab2d0f4e42e3b9c41c9b54f382c002f8fe4efde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf9eeec465e0aafd4b3caec7b66761474809a9b9a966ec32c1c372b40899bcd0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2a27c744dffe3ea8bf6db5f6bdf064e1abc5304266d8eacfa1d73b5fc9966b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc45840dd952f33c1e124461f71515c810367131c32964fec67b5911c292558b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9393bc1348d7fe7cfa9eca4aed0b4f7a21639a665d496c91e9be148df8c537b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__72599a34707747c3cefab5d6913a1408adf75a7a857628624ec5b546e62faccf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09caf3a5ad2a887687cba72410b45fa792006b40cd4f18834cf7fdcd57902590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultExcludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe93abbb7a3cb404c042f1446939bb65d3ff4f32f7213e8d632a4f101df62e0b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd4fce6ca62c48595e244f1c63f8886af4a5e3bb20dda52b45d03d812e2a5e0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdeddf8cd19105abca8590ecb766df30abb86d0adaf4742394e00a5644054d89)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="appUid")
    def app_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appUid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95166891bd153fa406fcefc0a7bba30092eb336a9ee4b26690d2745d9473dbf3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultExcludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9101a10f8ee053d02d6fe546d3c18d0815050c791136a76f3a97435cc4d353c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultExcludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd9a1394cae1c47c51cb64fe8a1b515d2fad9dd9b74513dfbcca3c74173df3c7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultExcludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05236494337061574e0314c11338c0c82dd785cc42004f16937781c13c9ff5f6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__69b7a453ee71afb2417339bf94d66f6d361c74e560b652be636780148f7bd1bb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c198bec35b3fde9f016266f80cfb12576df7a337a4c5c59a141d6a5469b4b02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7580e92d88a9a2ebdfda81b53ae28f11c8f9e3725bbe37ea159be9acba041c5d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__674ea656783d17842c6238a12a5c8a6bebad850e9cd0c8ea84b5c0f034a17931)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b85f3bef89f0baa586a3784da1020e5a607b48bb8aaf7af9d7f8014bc0836cda)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="claimName")
    def claim_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimName"))

    @builtins.property
    @jsii.member(jsii_name="claimValue")
    def claim_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimValue"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1bcd25496a035d7d4c7ca56533edec2d69cc584867cec9c6075531504f682ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4504e79655c274f9acdb1d20ac9b6151167dd5d9344e2da5c3da5e393e50da12)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efaa8ec35fe118ac5a711d5661f1ee090abe6748dc03e37a1fad18c58700a3e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultExcludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__54088db2cf574bea92cff7dd0eac77d8a517d12b51fc5e16c97cf0f6b583e481)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultExcludeSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultExcludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExclude]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExclude], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExclude],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c30d33d2ef710a60f06fcfc3dfb9ef044e5119412d53e20256a3652f005fc7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81212ddfa9dee834a23a3708aeb71f698333565dfb4ae269ce2e33df6bcfca5e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeName"))

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeValue"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d6dcf1355220aeee521cf1f38ee7a2bd957b5012a0719c3b914317b7c5118f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__676c3de0f91b9cbb4aae89a2705ba3a699798c10da814042c82d66786ab942b5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="tokenId")
    def token_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7903674eeda6aabcd5ee401db46d3dbccb2032de1e1205a27a890ed8eaa27b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultInclude",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultInclude:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultInclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__17d7a6ea8892caa91323be4cc035bf0f2fd95fd9ea4e46508c2befc3991e521b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4799394696b5becef9d35be0aec03691046cba6bc3e4521452c187e122c06f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__72e2ca3b33fd7474c5a0f28518f0c021d7159d1665b2264cdf27101b203252a9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="acId")
    def ac_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acId"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bda6d18f7eac961556672b8a932561e05557b431961077e307331e2e0802df3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__20d67e49036635db8c0ce9c5a228fe2eb72fc5f5680bf5cc451aed36cef98a4f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cee7cc3b12a259f2eba7286f7e0fa0837968c4f0869f4b34d2a7aa0c43b5774a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3703349c4d30974ff899ca8c3a0937c957232f94433c37e89cb42da4269077a7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e18e701ec22330560713e8a24d977e69ea7003a97f2fd9a5a5abf598273c95fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c2cf7f5bbc6d0eafbbf223b0eb1b9f517dfeab4223dadb0620ff7d19c4b8951)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa53c6dfffe3e5cb596a0e1faa5e4aa004625ecb2ffd26c70089ab4d80a7f320)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e10ba3039796f5329b6be4cc88d2affa6828d1f9fdf0dcaee15813590b38a81)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4250809b0c86a9c2969b75666979b99d66a91436604b5b92c1059d4f12ae8bb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca6e6fdf5c3bc23836a0259dc5d6c896f062f7d875ddb25326f18e9afbbaebaa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="integrationUid")
    def integration_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationUid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd79040c5c09f63fed0a2321a170cd4687a3947d010a9e1e9fec01c9aa41d438)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f12112f91e01511e36e4d50ef014cfb1934da37eed2c954c384cec44e0785a7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f313dd0fb9cbe79232b264b6b6ffb87abe8ec5d27bfa61709ce6008a55f87d67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a16bfbf744d4c29063ea060a6dc2c269baa904457bcd82324b5fbaff37fd8792)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e6ee784c3fbb8135f5d26e9038ab649a678ac95ca7469b319a9fbca70b742ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9d783f8e3160ffc2cba214d45ecdb01760df7a04ba7416f0f468d78eebb5624a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58dd1abd0b50c47e2272ceab27bc76d4f55c80f8d00cef1a0cecbd64944b8217)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__062f23c6eec64e8aa7b8bdf0f5546b96c81823e8b9668d7ca34fe62c64eec8f6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b45f76efadf5d40c1610b21851c2508b58ecf8d3a799ad6f8063aba25161518f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__98738a9532f00b8f4ec786f13196cd0a4af72f48a570481f2f6401a9ff545b7b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="evaluateUrl")
    def evaluate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evaluateUrl"))

    @builtins.property
    @jsii.member(jsii_name="keysUrl")
    def keys_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keysUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25f7269cd4883c3a1d2a8eafcd394798fb13ae3cc11a2e24908f86bba762af96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__911da75fc8e3eee9378cdd654366082143f8a8574e1dc4b0a85354f4fc90c92a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="countryCode")
    def country_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "countryCode"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36fae3e7a984f3884ea762a2505fdb6313708ef2d2c321076fcc6af6f0a1bc94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1761a155eb538c47d3af8f31373ff778bf69c70c104c67633ce356a3fa9f6e24)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d0c6bc8191b89dd6b139fea315b64ccbfaa2a41366e14329827896d4b9efaa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0483e42f657de567dea1dddc9e913eb540acf6d2d0655d9f0e747d1ecc7bc6d9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f13c0b6641c44fa84f143ccc644bf82b9e3bdd7d30dbc5f9fc353f79a78790f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ccbf80db9a1ac87f307d89355c936df0dd234b3042b94ecd6c1b223b92d89f95)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed3998b4c84abb05e2055f847601568c4f73fc91f3b13f056c6a938b9d32e4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ad98fc63a930c4ab0bf3556f5cae75fe481158663beed8ee7d3ab81034c7d7c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99c55638803b06e300f6c3baf967144ccf5c0257845deb8756768729d6f482ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultIncludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da8cddf8792511c8b565a25a30140be0767d4af23d157af7aa9d54b8d855ea40)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3701607b3fea3409846980968ecf3f485b6e5560d2f0ce0e93f3d1dcf9c9ed51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b370313e1b3e57823b735bf2dad60dc367d61ee6662a9455757bc896321831d9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="appUid")
    def app_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appUid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3c172052cc0db66bfedb0e111dff067af8ea58ac2c51dec5582e9fcef11de2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultIncludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__662d0a80001875742686dd15aff4f680b7bfc280dd667b55cf1dac05fe06465a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultIncludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c721abfc941343c65e4c60d72dccc3eb8baa0848d79d76f3773d76090c2489b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultIncludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfad1bb5024d4ac45813330162024763d64d0f97f6ba9236a9c7f4b18b9164da)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bfd03c4d7504fdf45ac2fca4b5b918bc995b3fe79fc6f17ef802200c0b40ad82)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7005ce3188f53daf2306e0b30a5c1c19c429413ff560805fdaeba86e4badab2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8ddb4f7742a2016b0a8a4757635caab44ef62159702a4a76c8d19326463df0a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3626f12e9237411692d93db9511e4779a30d1d5d476c9f4c2c0283eb7647e40e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__65266b179dfdce40af835bd6f26581e691e70cb9042eb058f70df5f6dd561412)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="claimName")
    def claim_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimName"))

    @builtins.property
    @jsii.member(jsii_name="claimValue")
    def claim_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimValue"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e09321decc28223ec99c748d1f672afddca81a250cdc60f89c414553188b62ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e64eeeef16f0369c7cda5072fdf24c0b93e2920fb3d5433dbeba3de20a2ab9f8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ffafc89948b71abe8d3653f7fda377dbfeeeb1ebac82ce87752ca24605c4445)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultIncludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1dd5d0d62caee1405933f3169b0e5aba3b33364b0851f4aae81eaae1804888e1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultIncludeSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultIncludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultInclude]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultInclude], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultInclude],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a3512a7a25ece3c6dbd126ebd9c0ca999321622bdab4b760cb2fb9bc71b91ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69cf1b22008ba885b32756f16a512dfd4cff1ecff148cd9fa706d45557768472)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeName"))

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeValue"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d64693cbde2c78df6b1098fd13835e8389120a3844825bb18a98dacad9ecb51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e25458c97b1791282585eb00f06b3dc0fd5c10f71345e4411046657fa3b4108)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="tokenId")
    def token_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__091f26f835e5329df81041f935ab4b1a72799c7ea95ff34a615b42d98d19e030)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8aafa96216414cf765f2b1712ceeedfcec9cbb83c8530afa3e79cc8c3a20d4b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a758ec8c34b8e16148e766567b904177ef4af6f1d99d2baf2d242dadbf7d946a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38eb48acaf81621398915465444131825afbecdd4ece33d5eb1f13f6a4fb75fd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fcf15eb7f91d0b7bc70e16bbd878a826d8bb718f930645f2d1110bd98c39efc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__22abc667f62bf412773d7480646486075aa14af1003a7f2be1896711c6e5c945)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7580ec32d1b62c5da3704c6f89aaceed345e389f4b26f5e1c07b498ef8d5ce56)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="appCount")
    def app_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "appCount"))

    @builtins.property
    @jsii.member(jsii_name="approvalGroups")
    def approval_groups(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsList:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsList, jsii.get(self, "approvalGroups"))

    @builtins.property
    @jsii.member(jsii_name="approvalRequired")
    def approval_required(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "approvalRequired"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="decision")
    def decision(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "decision"))

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> DataCloudflareZeroTrustAccessPoliciesResultExcludeList:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultExcludeList, jsii.get(self, "exclude"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> DataCloudflareZeroTrustAccessPoliciesResultIncludeList:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultIncludeList, jsii.get(self, "include"))

    @builtins.property
    @jsii.member(jsii_name="isolationRequired")
    def isolation_required(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "isolationRequired"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="purposeJustificationPrompt")
    def purpose_justification_prompt(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "purposeJustificationPrompt"))

    @builtins.property
    @jsii.member(jsii_name="purposeJustificationRequired")
    def purpose_justification_required(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "purposeJustificationRequired"))

    @builtins.property
    @jsii.member(jsii_name="require")
    def require(self) -> "DataCloudflareZeroTrustAccessPoliciesResultRequireList":
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultRequireList", jsii.get(self, "require"))

    @builtins.property
    @jsii.member(jsii_name="reusable")
    def reusable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "reusable"))

    @builtins.property
    @jsii.member(jsii_name="sessionDuration")
    def session_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionDuration"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResult]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25e03b1173992cee48c84cacb0a1bf9a2894eb7c7df2c19cfd3c53c47ce1149b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequire",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequire:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequire(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__07e2d420d677a8032bee65a58ed3f31cb74ec8bbab9cd6f2f1e6082a41de9c5b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27e2930eb5340ec87db2825ba539d9355b0eb7382099034c3a232129cf96029a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e91fc55ffdee238e09b99b33f64e978062a55fa0e9429b494d4c6e44d25efd9e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="acId")
    def ac_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acId"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__815da7b9dbf8bda1fa4264878737063a444779b5e177330ddfde30216b7bac09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e1e323ff679c567fcf0fee15fbf693a67a841c15c39420b02515368c859dc031)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9216614f6657bc4aabf53ab4969192aa5cc005fd93f8ed267285bb892a2bac8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e57805e4db44c04b9e854957cef673adcc2195baf45bf603162aeb24b64c13b8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84f1bbf6f4ccc115e35983e37a83d9f71f5dcb295eff5094eaecb88206c731d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91bfc511f4c7bffb6fcb9e72021e23b486b908e728d167c5440b2af8a7dc4b88)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0583e72df366936e303ade48f8e90daeeb9bb65931c0c09c341d2c959b4f086)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__83a02423721fcc100254b5bf1bd912c0cc40d5f4f5366e8a302b35b1187175e4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d56501fe12f367775444bcf81f0b9b9e045bee03dca7783e41fe45ef56e41592)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e7214839023d5da2cdc5922521dc003b4f29b2d09dfc1d5e9e24fcb9c63beb7e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="integrationUid")
    def integration_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationUid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ded99af028796d381b989684dcb2954e93baa738c940318af3c669305c93d4a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eff3259cf54373d48e06f802b8b7325373e57db0632a130fb31ab3d823ab3997)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61504c4b60211a29c6596e99053f25e715bb962df47567f77b9ff9a4eedfe42c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__96926b82424ee3e9aa3eaadcae1b9f0a9d28ea98ba7768e481ff6100099bc2c8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fcd199235de9017e759e4bd2be3c66f9736a8434a1afbe8ed528a4ae0659896)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultRequireEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a96676ba8d5b62a529d2361fb5d6e89b763b7ac5d98a6caa60b18497ea9e42b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6023dc7b35931d9ce3f58f6913a323c5dc5cc336acc251d0f2caefceb7e44dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__23a219dced703f8215cd9956c30035b975e695bca6b78c3eb32bd6314dd08021)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6aec48604a013068f190374485aaffd5c8fb112fc43a3e9f2102bf8f5df3a4d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2c8ee3157d78e04be0b24c5e19e710bbc94deea77665c5a9b355b93835d6a52f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="evaluateUrl")
    def evaluate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evaluateUrl"))

    @builtins.property
    @jsii.member(jsii_name="keysUrl")
    def keys_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keysUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05599cdd552f963d38df12b5043e7804acb17550c42e19eb2805e666f8c82600)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c45a33ce775c0ae4228b557f0b60d460e398f43efbaa6ad6191d4c4c22bae11)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="countryCode")
    def country_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "countryCode"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06b3e314487a41ab5eeacf2b6f2c6fcde8b21de81ee0200c91a11e9b58c48ce9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__191b8367b398e9c6ebb1fe46fd17fcc125f06b2b410897c59db6e1da48b92872)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6019f74b7f8cd3aa528f738e02d8d0ed45cb58bf19c7784393455d2f185a6ad5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__100f02e8906c6b1938279c3a2742e6ba2e1adc352de6e84da44701195e5bb423)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__103f33f554c8ab3b632ad36e3db6f6bd30df7b4984f3fd74e3b1337ecc7f8911)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64ab798767c7fa7110ebd33e79d955fc0adbf37c27867a068d604a71b01011e2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d45bab5cd2cd5e2f7066b46660eeaed5cfa80fed0b4bd63887ebf488f3d1cdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91f6d22a5d72f821fa0d89e8c0cba8ae7fb074bb0d0011b9290d3a8b84ee620c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c451b15e0b3ae04edca3116e4658c60de1c0357eb8681817b7efb69091f5a57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultRequireIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8e66780e08389560f045aa9e2ceb3b824794f14ea3e5b0e1c9e8885f7c8b455)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d13913f28db3f97028cff322e9061c41980d944967f9c7260950fbe0e184b654)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f973d3c292c4fb747df062c0de9db63a9e73272c0c348246f6011e13ec99bbe3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="appUid")
    def app_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appUid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ce10c5a2b5a0bdcbf232209b9a7a2c764dc0d4f1ec3a08cc56c6cebf5054fa7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultRequireList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0782a3044f748a2a255b4cba38a964fb3e8634c96562786986808f0a0cb1118)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultRequireOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63dcee183715759e46985e96f336fbd079337be4043fbef054b422d020cbf38b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultRequireOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5de3366eeb6541d0a1575f71bea9a4bcf40b053a7ac2624a7bd1b4c5dd173b03)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3e0ba0061cb9ea874d408a83223917246865fb156c7b59987b3d7ca21284d1b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b1c7bc351d67a5162d4eb4c4ae61e426399a1a646cf9b62f813d6159a81d205)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fdfb6f949da564001464f6162ac9a6645ad80dd4812345bd80cc280839ad51f4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00f00cf0633b5480eec20dfc34f6ed3abd6e526f206942e6424b9fb3c3134ac2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e257827199521ce83ed80a0f87e3919f19244aeb9e13a7dd2d72afdab5352d97)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="claimName")
    def claim_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimName"))

    @builtins.property
    @jsii.member(jsii_name="claimValue")
    def claim_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimValue"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c4bd230c86416c8e7ce108723599f13b5b38e8dae3a2ab21c825c2e3b7ae22d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__953c37bf875b27935121cb34a868f2e25018f68b7258d396c50e41337c1fba76)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__827f7f622f1cfa0b056377ee2f2207cce4f7097825829ac4dce857a7ea091842)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessPoliciesResultRequireOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7494492bd7165400ca5f706d1a41ff38f73869078f6b2bf34ef39d7baaa668f6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessPoliciesResultRequireIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessPoliciesResultRequireOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessPoliciesResultRequireOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultRequireSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultRequireSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessPoliciesResultRequireServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessPoliciesResultRequireServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequire]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequire], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequire],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37d8b5b1da9cb0fa9c36d5bb881f5db64923a40008c88847fba4b0fc4c12d986)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e299e6e35f00d51fbd70347176e8b2b831c9863ff473c58db2106e900f28dd5c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeName"))

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeValue"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a0dd50cd4b22aeb71385fd91272177d18cccf4d70969b80beb53b16a107b84d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessPoliciesResultRequireServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessPoliciesResultRequireServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessPoliciesResultRequireServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessPolicies.DataCloudflareZeroTrustAccessPoliciesResultRequireServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f3e648fcc7f543de84cb6c57d2eee24e5e5fe43f8eee9b1c13dcfa3b985f6a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="tokenId")
    def token_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97f8042870ceca3368cc4f1febc3cc8cbecb958bdc9e0c1f7f86415c4ec99b54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustAccessPolicies",
    "DataCloudflareZeroTrustAccessPoliciesConfig",
    "DataCloudflareZeroTrustAccessPoliciesResult",
    "DataCloudflareZeroTrustAccessPoliciesResultApprovalGroups",
    "DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsList",
    "DataCloudflareZeroTrustAccessPoliciesResultApprovalGroupsOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExclude",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContext",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethod",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAd",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificate",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificateOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonName",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePosture",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeEmail",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomain",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStruct",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryone",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluation",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeGeo",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeGeoOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganization",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeGroup",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeGroupOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuite",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeIp",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStruct",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeIpOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppToken",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeList",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethod",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeOidc",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeOidcOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeOkta",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeOktaOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeSaml",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeSamlOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceToken",
    "DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultInclude",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContext",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethod",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAd",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificate",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificateOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonName",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePosture",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeEmail",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomain",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStruct",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryone",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluation",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeGeo",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeGeoOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganization",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeGroup",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeGroupOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuite",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeIp",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStruct",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeIpOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppToken",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeList",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethod",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeOidc",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeOidcOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeOkta",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeOktaOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeSaml",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeSamlOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceToken",
    "DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultList",
    "DataCloudflareZeroTrustAccessPoliciesResultOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequire",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContext",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethod",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAd",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireCertificate",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireCertificateOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireCommonName",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePosture",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireEmail",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomain",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStruct",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireEmailOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireEveryone",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluation",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireGeo",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireGeoOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganization",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireGroup",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireGroupOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireGsuite",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireIp",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStruct",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireIpOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppToken",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireList",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethod",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireOidc",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireOidcOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireOkta",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireOktaOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireSaml",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireSamlOutputReference",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireServiceToken",
    "DataCloudflareZeroTrustAccessPoliciesResultRequireServiceTokenOutputReference",
]

publication.publish()

def _typecheckingstub__59c074b60d731cb86890f4579f6845d61c180aeff4cba864c6d96d071ed18db5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
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

def _typecheckingstub__d890e9ce752804ea4911790c3bcda9d2bb952db163d150367d09f9ce0c188208(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2710605826f7a926df7df198531cef27474880d9ac0a0ed27560a871017b89c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a01eda5d8d16189b6462894feb6e5fd0a2d2d2a22903d3a3b537ddddf62a14a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3873650d1478549c4dbda7ba7618eda5b740a576951cdf65d52d6a5126a8d859(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    max_items: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86935878d67e9ce2c8956ebf2106b911eca2faa3ae2e6bd187839c33fcaa6202(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a247f7d9b851a470e8ae9bb0d2667a547bb00d2978e8fba7bc486bb6e72d78a2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__589407939071f3bdadb65ee25482ae620c7e3b7d590d4368fe7414ac0d6d0518(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e7746cbf7c4ed308651972bc7990ea2f305a77121d18aa85aa0c94adc6a30ce(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bb9e340e5120693da6b8d6d4dfe6790c27b8fc2b9cba62c914f88e66b490d61(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c84f59eff04ce123f22cf0b60011d689c226555847bda6fbe14709ee546406d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be1bd196ea9d7d1569fba1ed5ef8850236bd8938d5c954781d5b23fa16ffe4f0(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultApprovalGroups],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1ea7bf0fc93076b71262b87ec83c7ab32c82c876a485494bad156fa6a1b276a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__082622491da8d9b93ddf99565b036fdac868c4c71df942869636f6cf603a8314(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25867eba9c9ac8f2488e49b1da9e91491e05882a1f4731ae1862dd7c0e899e60(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69092ffc4c1a1d253c7d4f33eecc1778a5a2112ec097d7baa8277afb555ae68b(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac1c0084d11cc96708d4e2f230136f4aea285ee5fdbb68836cffc2bf5d1a78e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c82f4cb9cb48b07b988978c10b0d82b6f74d8e6230c8459675fd552f19fb512(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3021d5d630c62e00ef93ac125d3738eb3a872de7a3fad113984ec5225befc1c2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfb3fbc2d00695519caf642e2b910aae8b68aca47b6e8df5f834b0b5d6a2ba48(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd073de104b7742af7ae3c005f077859a3d35f1392f5d11ec030bc245f3e9aef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86181fb036c4fb067dd8c32848c80af4a1ee493c7f357807d3f6468f20ed2fb7(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46caaf32be8cfbb504a24de253791c95da266a3ff4ccb2cc0c52c80389bcceed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7a27c44b8e2de71dfc762ce54c19269eec988305d842aff358f44c13017e1df(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32914e068d363ebbed5c79bc65f6cb732982819d517e8b0700f3af9f40374fec(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__345e0661cd0e4082d46d6bc93af717dd7e39807686bab84542230a55af83f42a(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__456087e90a13edc5853c40a464f11d5104faca020f51e3deab86a0a40c4bbb17(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3332716f56519bbc856c3d79860deb937c9f34d9c58ab18217cb582aab3c7ca9(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b100e96d392183fd2c901be0543e1a8f57171b6864a5b1e4b74397115251ce9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39b79a17cdb36bddc5d50931435bdc363e52ee59fc793e0a0643da97a98985dd(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab5dcb7f11054ddc68c5aef9234e98564de96dfa6f5329fd9fc9266e31c93ddd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67cef74280cc34ea7878ad2d0e60b6fe6f8122f45a94014d90f6b94327acd496(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e9e00a3cbf05c8d5d5779c59e20965e1b5e9bfac4965cc847eaf218c9e326e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__495828837349475f200e32f7090ebbe248ea89aae54a42f4ce8e8c1d4244f515(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26b6966ab0ebabc94cc3c85234d8d8c7ca72a7e1992dea379d2e2d6327911018(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5dd82293c5bc0365c1861f576ac90a1dcf248366ce7c6d35ed398680de64236(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55360ddf99ef448622ac26e05ae98769ccffb050a7dc8faf9fb13d980599d609(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f4e8cc9e986cc484047fef56ff5e7eb95a444bd51d4cbe94d3b78102ecf297(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b369aafcc309267c7dcce5fba78b0a03c593674fc10811087f9fe9108a0dffcf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35d2bccfe9624dd68053050fcab2d0f4e42e3b9c41c9b54f382c002f8fe4efde(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf9eeec465e0aafd4b3caec7b66761474809a9b9a966ec32c1c372b40899bcd0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2a27c744dffe3ea8bf6db5f6bdf064e1abc5304266d8eacfa1d73b5fc9966b9(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc45840dd952f33c1e124461f71515c810367131c32964fec67b5911c292558b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9393bc1348d7fe7cfa9eca4aed0b4f7a21639a665d496c91e9be148df8c537b(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72599a34707747c3cefab5d6913a1408adf75a7a857628624ec5b546e62faccf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09caf3a5ad2a887687cba72410b45fa792006b40cd4f18834cf7fdcd57902590(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe93abbb7a3cb404c042f1446939bb65d3ff4f32f7213e8d632a4f101df62e0b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd4fce6ca62c48595e244f1c63f8886af4a5e3bb20dda52b45d03d812e2a5e0a(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdeddf8cd19105abca8590ecb766df30abb86d0adaf4742394e00a5644054d89(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95166891bd153fa406fcefc0a7bba30092eb336a9ee4b26690d2745d9473dbf3(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9101a10f8ee053d02d6fe546d3c18d0815050c791136a76f3a97435cc4d353c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd9a1394cae1c47c51cb64fe8a1b515d2fad9dd9b74513dfbcca3c74173df3c7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05236494337061574e0314c11338c0c82dd785cc42004f16937781c13c9ff5f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69b7a453ee71afb2417339bf94d66f6d361c74e560b652be636780148f7bd1bb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c198bec35b3fde9f016266f80cfb12576df7a337a4c5c59a141d6a5469b4b02(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7580e92d88a9a2ebdfda81b53ae28f11c8f9e3725bbe37ea159be9acba041c5d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__674ea656783d17842c6238a12a5c8a6bebad850e9cd0c8ea84b5c0f034a17931(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b85f3bef89f0baa586a3784da1020e5a607b48bb8aaf7af9d7f8014bc0836cda(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1bcd25496a035d7d4c7ca56533edec2d69cc584867cec9c6075531504f682ef(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4504e79655c274f9acdb1d20ac9b6151167dd5d9344e2da5c3da5e393e50da12(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efaa8ec35fe118ac5a711d5661f1ee090abe6748dc03e37a1fad18c58700a3e3(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54088db2cf574bea92cff7dd0eac77d8a517d12b51fc5e16c97cf0f6b583e481(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c30d33d2ef710a60f06fcfc3dfb9ef044e5119412d53e20256a3652f005fc7e(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExclude],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81212ddfa9dee834a23a3708aeb71f698333565dfb4ae269ce2e33df6bcfca5e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d6dcf1355220aeee521cf1f38ee7a2bd957b5012a0719c3b914317b7c5118f7(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__676c3de0f91b9cbb4aae89a2705ba3a699798c10da814042c82d66786ab942b5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7903674eeda6aabcd5ee401db46d3dbccb2032de1e1205a27a890ed8eaa27b5(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultExcludeServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17d7a6ea8892caa91323be4cc035bf0f2fd95fd9ea4e46508c2befc3991e521b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4799394696b5becef9d35be0aec03691046cba6bc3e4521452c187e122c06f3(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72e2ca3b33fd7474c5a0f28518f0c021d7159d1665b2264cdf27101b203252a9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bda6d18f7eac961556672b8a932561e05557b431961077e307331e2e0802df3(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20d67e49036635db8c0ce9c5a228fe2eb72fc5f5680bf5cc451aed36cef98a4f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cee7cc3b12a259f2eba7286f7e0fa0837968c4f0869f4b34d2a7aa0c43b5774a(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3703349c4d30974ff899ca8c3a0937c957232f94433c37e89cb42da4269077a7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e18e701ec22330560713e8a24d977e69ea7003a97f2fd9a5a5abf598273c95fb(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c2cf7f5bbc6d0eafbbf223b0eb1b9f517dfeab4223dadb0620ff7d19c4b8951(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa53c6dfffe3e5cb596a0e1faa5e4aa004625ecb2ffd26c70089ab4d80a7f320(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e10ba3039796f5329b6be4cc88d2affa6828d1f9fdf0dcaee15813590b38a81(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4250809b0c86a9c2969b75666979b99d66a91436604b5b92c1059d4f12ae8bb3(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca6e6fdf5c3bc23836a0259dc5d6c896f062f7d875ddb25326f18e9afbbaebaa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd79040c5c09f63fed0a2321a170cd4687a3947d010a9e1e9fec01c9aa41d438(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f12112f91e01511e36e4d50ef014cfb1934da37eed2c954c384cec44e0785a7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f313dd0fb9cbe79232b264b6b6ffb87abe8ec5d27bfa61709ce6008a55f87d67(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a16bfbf744d4c29063ea060a6dc2c269baa904457bcd82324b5fbaff37fd8792(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e6ee784c3fbb8135f5d26e9038ab649a678ac95ca7469b319a9fbca70b742ce(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d783f8e3160ffc2cba214d45ecdb01760df7a04ba7416f0f468d78eebb5624a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58dd1abd0b50c47e2272ceab27bc76d4f55c80f8d00cef1a0cecbd64944b8217(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__062f23c6eec64e8aa7b8bdf0f5546b96c81823e8b9668d7ca34fe62c64eec8f6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b45f76efadf5d40c1610b21851c2508b58ecf8d3a799ad6f8063aba25161518f(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98738a9532f00b8f4ec786f13196cd0a4af72f48a570481f2f6401a9ff545b7b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25f7269cd4883c3a1d2a8eafcd394798fb13ae3cc11a2e24908f86bba762af96(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__911da75fc8e3eee9378cdd654366082143f8a8574e1dc4b0a85354f4fc90c92a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36fae3e7a984f3884ea762a2505fdb6313708ef2d2c321076fcc6af6f0a1bc94(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1761a155eb538c47d3af8f31373ff778bf69c70c104c67633ce356a3fa9f6e24(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d0c6bc8191b89dd6b139fea315b64ccbfaa2a41366e14329827896d4b9efaa4(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0483e42f657de567dea1dddc9e913eb540acf6d2d0655d9f0e747d1ecc7bc6d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f13c0b6641c44fa84f143ccc644bf82b9e3bdd7d30dbc5f9fc353f79a78790f8(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccbf80db9a1ac87f307d89355c936df0dd234b3042b94ecd6c1b223b92d89f95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed3998b4c84abb05e2055f847601568c4f73fc91f3b13f056c6a938b9d32e4c(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ad98fc63a930c4ab0bf3556f5cae75fe481158663beed8ee7d3ab81034c7d7c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99c55638803b06e300f6c3baf967144ccf5c0257845deb8756768729d6f482ba(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da8cddf8792511c8b565a25a30140be0767d4af23d157af7aa9d54b8d855ea40(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3701607b3fea3409846980968ecf3f485b6e5560d2f0ce0e93f3d1dcf9c9ed51(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b370313e1b3e57823b735bf2dad60dc367d61ee6662a9455757bc896321831d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3c172052cc0db66bfedb0e111dff067af8ea58ac2c51dec5582e9fcef11de2d(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__662d0a80001875742686dd15aff4f680b7bfc280dd667b55cf1dac05fe06465a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c721abfc941343c65e4c60d72dccc3eb8baa0848d79d76f3773d76090c2489b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfad1bb5024d4ac45813330162024763d64d0f97f6ba9236a9c7f4b18b9164da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfd03c4d7504fdf45ac2fca4b5b918bc995b3fe79fc6f17ef802200c0b40ad82(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7005ce3188f53daf2306e0b30a5c1c19c429413ff560805fdaeba86e4badab2c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8ddb4f7742a2016b0a8a4757635caab44ef62159702a4a76c8d19326463df0a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3626f12e9237411692d93db9511e4779a30d1d5d476c9f4c2c0283eb7647e40e(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65266b179dfdce40af835bd6f26581e691e70cb9042eb058f70df5f6dd561412(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e09321decc28223ec99c748d1f672afddca81a250cdc60f89c414553188b62ad(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e64eeeef16f0369c7cda5072fdf24c0b93e2920fb3d5433dbeba3de20a2ab9f8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ffafc89948b71abe8d3653f7fda377dbfeeeb1ebac82ce87752ca24605c4445(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dd5d0d62caee1405933f3169b0e5aba3b33364b0851f4aae81eaae1804888e1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a3512a7a25ece3c6dbd126ebd9c0ca999321622bdab4b760cb2fb9bc71b91ad(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultInclude],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69cf1b22008ba885b32756f16a512dfd4cff1ecff148cd9fa706d45557768472(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d64693cbde2c78df6b1098fd13835e8389120a3844825bb18a98dacad9ecb51(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e25458c97b1791282585eb00f06b3dc0fd5c10f71345e4411046657fa3b4108(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__091f26f835e5329df81041f935ab4b1a72799c7ea95ff34a615b42d98d19e030(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultIncludeServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8aafa96216414cf765f2b1712ceeedfcec9cbb83c8530afa3e79cc8c3a20d4b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a758ec8c34b8e16148e766567b904177ef4af6f1d99d2baf2d242dadbf7d946a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38eb48acaf81621398915465444131825afbecdd4ece33d5eb1f13f6a4fb75fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fcf15eb7f91d0b7bc70e16bbd878a826d8bb718f930645f2d1110bd98c39efc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22abc667f62bf412773d7480646486075aa14af1003a7f2be1896711c6e5c945(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7580ec32d1b62c5da3704c6f89aaceed345e389f4b26f5e1c07b498ef8d5ce56(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25e03b1173992cee48c84cacb0a1bf9a2894eb7c7df2c19cfd3c53c47ce1149b(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07e2d420d677a8032bee65a58ed3f31cb74ec8bbab9cd6f2f1e6082a41de9c5b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27e2930eb5340ec87db2825ba539d9355b0eb7382099034c3a232129cf96029a(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e91fc55ffdee238e09b99b33f64e978062a55fa0e9429b494d4c6e44d25efd9e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__815da7b9dbf8bda1fa4264878737063a444779b5e177330ddfde30216b7bac09(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1e323ff679c567fcf0fee15fbf693a67a841c15c39420b02515368c859dc031(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9216614f6657bc4aabf53ab4969192aa5cc005fd93f8ed267285bb892a2bac8f(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e57805e4db44c04b9e854957cef673adcc2195baf45bf603162aeb24b64c13b8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84f1bbf6f4ccc115e35983e37a83d9f71f5dcb295eff5094eaecb88206c731d5(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91bfc511f4c7bffb6fcb9e72021e23b486b908e728d167c5440b2af8a7dc4b88(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0583e72df366936e303ade48f8e90daeeb9bb65931c0c09c341d2c959b4f086(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83a02423721fcc100254b5bf1bd912c0cc40d5f4f5366e8a302b35b1187175e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d56501fe12f367775444bcf81f0b9b9e045bee03dca7783e41fe45ef56e41592(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7214839023d5da2cdc5922521dc003b4f29b2d09dfc1d5e9e24fcb9c63beb7e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ded99af028796d381b989684dcb2954e93baa738c940318af3c669305c93d4a0(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eff3259cf54373d48e06f802b8b7325373e57db0632a130fb31ab3d823ab3997(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61504c4b60211a29c6596e99053f25e715bb962df47567f77b9ff9a4eedfe42c(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96926b82424ee3e9aa3eaadcae1b9f0a9d28ea98ba7768e481ff6100099bc2c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fcd199235de9017e759e4bd2be3c66f9736a8434a1afbe8ed528a4ae0659896(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a96676ba8d5b62a529d2361fb5d6e89b763b7ac5d98a6caa60b18497ea9e42b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6023dc7b35931d9ce3f58f6913a323c5dc5cc336acc251d0f2caefceb7e44dd(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23a219dced703f8215cd9956c30035b975e695bca6b78c3eb32bd6314dd08021(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6aec48604a013068f190374485aaffd5c8fb112fc43a3e9f2102bf8f5df3a4d2(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c8ee3157d78e04be0b24c5e19e710bbc94deea77665c5a9b355b93835d6a52f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05599cdd552f963d38df12b5043e7804acb17550c42e19eb2805e666f8c82600(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c45a33ce775c0ae4228b557f0b60d460e398f43efbaa6ad6191d4c4c22bae11(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06b3e314487a41ab5eeacf2b6f2c6fcde8b21de81ee0200c91a11e9b58c48ce9(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__191b8367b398e9c6ebb1fe46fd17fcc125f06b2b410897c59db6e1da48b92872(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6019f74b7f8cd3aa528f738e02d8d0ed45cb58bf19c7784393455d2f185a6ad5(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__100f02e8906c6b1938279c3a2742e6ba2e1adc352de6e84da44701195e5bb423(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__103f33f554c8ab3b632ad36e3db6f6bd30df7b4984f3fd74e3b1337ecc7f8911(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ab798767c7fa7110ebd33e79d955fc0adbf37c27867a068d604a71b01011e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d45bab5cd2cd5e2f7066b46660eeaed5cfa80fed0b4bd63887ebf488f3d1cdc(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f6d22a5d72f821fa0d89e8c0cba8ae7fb074bb0d0011b9290d3a8b84ee620c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c451b15e0b3ae04edca3116e4658c60de1c0357eb8681817b7efb69091f5a57(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8e66780e08389560f045aa9e2ceb3b824794f14ea3e5b0e1c9e8885f7c8b455(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d13913f28db3f97028cff322e9061c41980d944967f9c7260950fbe0e184b654(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f973d3c292c4fb747df062c0de9db63a9e73272c0c348246f6011e13ec99bbe3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ce10c5a2b5a0bdcbf232209b9a7a2c764dc0d4f1ec3a08cc56c6cebf5054fa7(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0782a3044f748a2a255b4cba38a964fb3e8634c96562786986808f0a0cb1118(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63dcee183715759e46985e96f336fbd079337be4043fbef054b422d020cbf38b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5de3366eeb6541d0a1575f71bea9a4bcf40b053a7ac2624a7bd1b4c5dd173b03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3e0ba0061cb9ea874d408a83223917246865fb156c7b59987b3d7ca21284d1b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b1c7bc351d67a5162d4eb4c4ae61e426399a1a646cf9b62f813d6159a81d205(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdfb6f949da564001464f6162ac9a6645ad80dd4812345bd80cc280839ad51f4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00f00cf0633b5480eec20dfc34f6ed3abd6e526f206942e6424b9fb3c3134ac2(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e257827199521ce83ed80a0f87e3919f19244aeb9e13a7dd2d72afdab5352d97(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c4bd230c86416c8e7ce108723599f13b5b38e8dae3a2ab21c825c2e3b7ae22d(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__953c37bf875b27935121cb34a868f2e25018f68b7258d396c50e41337c1fba76(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827f7f622f1cfa0b056377ee2f2207cce4f7097825829ac4dce857a7ea091842(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7494492bd7165400ca5f706d1a41ff38f73869078f6b2bf34ef39d7baaa668f6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37d8b5b1da9cb0fa9c36d5bb881f5db64923a40008c88847fba4b0fc4c12d986(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequire],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e299e6e35f00d51fbd70347176e8b2b831c9863ff473c58db2106e900f28dd5c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a0dd50cd4b22aeb71385fd91272177d18cccf4d70969b80beb53b16a107b84d(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f3e648fcc7f543de84cb6c57d2eee24e5e5fe43f8eee9b1c13dcfa3b985f6a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97f8042870ceca3368cc4f1febc3cc8cbecb958bdc9e0c1f7f86415c4ec99b54(
    value: typing.Optional[DataCloudflareZeroTrustAccessPoliciesResultRequireServiceToken],
) -> None:
    """Type checking stubs"""
    pass
