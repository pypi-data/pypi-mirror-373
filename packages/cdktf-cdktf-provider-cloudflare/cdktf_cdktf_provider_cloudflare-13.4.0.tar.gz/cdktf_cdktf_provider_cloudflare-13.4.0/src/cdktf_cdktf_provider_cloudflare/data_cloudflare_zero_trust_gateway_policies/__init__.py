r'''
# `data_cloudflare_zero_trust_gateway_policies`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_gateway_policies`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies).
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


class DataCloudflareZeroTrustGatewayPolicies(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPolicies",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies cloudflare_zero_trust_gateway_policies}.'''

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
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies cloudflare_zero_trust_gateway_policies} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies#account_id DataCloudflareZeroTrustGatewayPolicies#account_id}.
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies#max_items DataCloudflareZeroTrustGatewayPolicies#max_items}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b6268f6b22db0900ec9ee67b3a8d05cb78961b9b48ef1811826a941325281a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustGatewayPoliciesConfig(
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustGatewayPolicies resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustGatewayPolicies to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustGatewayPolicies that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustGatewayPolicies to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8da2fba1330ed9e6e48ce217207d23554a3dd90b0efb4baddb4abe9c9312aa4c)
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
    def result(self) -> "DataCloudflareZeroTrustGatewayPoliciesResultList":
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultList", jsii.get(self, "result"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__0c83900fe15a58fba69e241e7da48f6aa36e1b5ec54e8760d360c5966beb460d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxItems")
    def max_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxItems"))

    @max_items.setter
    def max_items(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adb157558a71026bd81606421b4820e5c2b4ad059724e66b35a9bda750542697)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxItems", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesConfig",
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
class DataCloudflareZeroTrustGatewayPoliciesConfig(
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
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies#account_id DataCloudflareZeroTrustGatewayPolicies#account_id}.
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies#max_items DataCloudflareZeroTrustGatewayPolicies#max_items}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d96a632c482fefadf8cea9d7a0277aee8ccc09f61fb31dabf014fa4b80afb4e2)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies#account_id DataCloudflareZeroTrustGatewayPolicies#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_items(self) -> typing.Optional[jsii.Number]:
        '''Max items to fetch, default: 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policies#max_items DataCloudflareZeroTrustGatewayPolicies#max_items}
        '''
        result = self._values.get("max_items")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultExpiration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultExpiration:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultExpiration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultExpirationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultExpirationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2fba18bb1a53d44b4a6d949de68c755f46566f83972d2ef246136dd6f0be435)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @builtins.property
    @jsii.member(jsii_name="expired")
    def expired(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "expired"))

    @builtins.property
    @jsii.member(jsii_name="expiresAt")
    def expires_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiresAt"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultExpiration]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultExpiration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultExpiration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f91cbbdad3457f28b2af9f2688e6e386216fcdb2cd6f84a23df0115bee18b08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPoliciesResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__79d45cf7d87ee2fc5981d0b248c8cdd3b65344593ad46ac586376ece72c8d63b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__142a3ac970866b69b51a6025f269edd9d499828ff8e337af4ea9adb7c42150e2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f122fa254b2318f0efc8d36e5250ad8e4f2a8e60ee9aab9b56ddacf87c94ef2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6028fa6756f556949d94e220ff959d07753a6a615211f8c575044bbe02e1d071)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f30277bd266c9f00709eb4c61307fcd8cc8649092b73596e6a0194a6bd497db0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPoliciesResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8612deb149ddf48e465fbca8265d16dc94b935e76d17f87ef865f73356a6e115)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="expiration")
    def expiration(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultExpirationOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultExpirationOutputReference, jsii.get(self, "expiration"))

    @builtins.property
    @jsii.member(jsii_name="filters")
    def filters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "filters"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="identity")
    def identity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identity"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="notSharable")
    def not_sharable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "notSharable"))

    @builtins.property
    @jsii.member(jsii_name="precedence")
    def precedence(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precedence"))

    @builtins.property
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "readOnly"))

    @builtins.property
    @jsii.member(jsii_name="ruleSettings")
    def rule_settings(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsOutputReference", jsii.get(self, "ruleSettings"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultScheduleOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="sourceAccount")
    def source_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceAccount"))

    @builtins.property
    @jsii.member(jsii_name="traffic")
    def traffic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "traffic"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="warningStatus")
    def warning_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warningStatus"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResult]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5e6580db4560b2038add49da24473c1b5603ca0a6925eb0f34be63e54901253)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSsh",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSsh:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSsh(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSshOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSshOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b77c398b4381a644aab2afb6ba04a1a1d90da87cc66da026584975c8fa14782)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="commandLogging")
    def command_logging(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "commandLogging"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSsh]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSsh], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSsh],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7632c96eb4098267b1095cddc1b0c2bcdb8584a9de97e9d331c70f0b98b2ddae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControls",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControls:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControlsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControlsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__71399613df674f48aa5e3ae32ce8c0c7a63b2d5cf063d854fae1493b9a1b837a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="copy")
    def copy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copy"))

    @builtins.property
    @jsii.member(jsii_name="dcp")
    def dcp(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "dcp"))

    @builtins.property
    @jsii.member(jsii_name="dd")
    def dd(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "dd"))

    @builtins.property
    @jsii.member(jsii_name="dk")
    def dk(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "dk"))

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "download"))

    @builtins.property
    @jsii.member(jsii_name="dp")
    def dp(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "dp"))

    @builtins.property
    @jsii.member(jsii_name="du")
    def du(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "du"))

    @builtins.property
    @jsii.member(jsii_name="keyboard")
    def keyboard(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyboard"))

    @builtins.property
    @jsii.member(jsii_name="paste")
    def paste(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "paste"))

    @builtins.property
    @jsii.member(jsii_name="printing")
    def printing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "printing"))

    @builtins.property
    @jsii.member(jsii_name="upload")
    def upload(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "upload"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControls]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControls], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControls],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48bd17dc5ab1d1ef95b5dba905f1b995d11633c10fb243ce32c29ac5a979c4b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPage",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPage:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9261de2175edb182908a00629bf4a095df238ac12c923883116580a23b13fb8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="includeContext")
    def include_context(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "includeContext"))

    @builtins.property
    @jsii.member(jsii_name="targetUri")
    def target_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetUri"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPage]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fde548f457674cdcd28ea35cceedffd9e6b06ee232332344fb55f14574581c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSession",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSession:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSession(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSessionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSessionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fdb834b9812a8f9a694c28c7a8a3e740c54c5de01de94d1a51d14ca04a2a42b0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @builtins.property
    @jsii.member(jsii_name="enforce")
    def enforce(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enforce"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSession]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSession], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSession],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0948ce2f9d1ed94270edcf29300d087f621850ea934b92b2662b861545011121)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolvers",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolvers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolvers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4List(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4List",
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
            type_hints = typing.get_type_hints(_typecheckingstub__701fe26d533f993ed0f776e71dca70f4fd35951ded127c944234549b74945b7e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56302ef3cedba855e3d40cdff99654dd85be6f9ff47d5398c69c7105feeb511b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4OutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6993c6a2f6e98109de1a917454ed165ef2440a07b7939a6d0859b49f474ed1ea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1aa150b4531b640adbce872da555801d42ac9d2728b7d094a81fb2d5989e601)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d63b9604e8d80d14290470d36b06561ee59605bbb404929aaddae645e8a579db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0441266defb652a3a40439106718176f8b42cbad39b04686048950601943d302)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="routeThroughPrivateNetwork")
    def route_through_private_network(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "routeThroughPrivateNetwork"))

    @builtins.property
    @jsii.member(jsii_name="vnetId")
    def vnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vnetId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fec7d8a3523174d926e6735be59ba0bf5ed5201f15bf2bf2d6dc0dbd0a2b707)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6List(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6List",
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
            type_hints = typing.get_type_hints(_typecheckingstub__faf5c4121532c8932e0b42eabe5dd21f5647fe56bb4f8ba0f522aa88245cfb72)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf846bd3b8df2ebd624800ac4fb91cca2c645450b632595e116c0a5c57b317c6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6OutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e9637973493abd47933c814a85fe1a2ec5c8dc8df7bc6ad8125312bea78c5b9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7068cfbe2620d4be2779c667f849b84aecd189712adbb11c2a008983773eec42)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d164f7fc330a308f0f9ce2e1c721a7ef0336db15dec3613ce81be69d2d481aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__011f2361ac014a19e6f02ecdec31dc61ec218634974c843d4cd26e5a1abf3ea0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="routeThroughPrivateNetwork")
    def route_through_private_network(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "routeThroughPrivateNetwork"))

    @builtins.property
    @jsii.member(jsii_name="vnetId")
    def vnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vnetId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87f0b87cac7d383eb368fa5833818a9308deb58b0f8534948223e0ff1dce2ba2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__96815029f21bd68be5ecbc19a17fa066945b57b9d314648e86df8cecdf7f556e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipv4")
    def ipv4(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4List:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4List, jsii.get(self, "ipv4"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6List:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6List, jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolvers]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolvers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolvers],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02903b763c32923ea4aa814f0d44a900c0a0f7fa900a98dfe80a0723a3b2cbf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b5f79b37ee659661e964cbf3c8d29a0afd317ff6c15758304ed332f0fe59528)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipv4")
    def ipv4(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4"))

    @builtins.property
    @jsii.member(jsii_name="ipv4Fallback")
    def ipv4_fallback(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Fallback"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgress]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a91e8e410ce7977e91edf114e0f5fd99ce3cec0e8103050e3323b4fc0c47015)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4Override",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4Override:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4Override(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4OverrideOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4OverrideOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce0f6dbff61fce3f9409ca6acd706afd1b6d6344dfc8e8a2b89b563a77a1aea4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4Override]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4Override], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4Override],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e63d6f71faedd7ee242b7534eb730b23f06e1ac107f89310a268fa453ec502f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1cbfd09d337fb47619d0ca3ebddffe40a5fd25e675d6c25a81bc17e0acebe59f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="includeContext")
    def include_context(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "includeContext"))

    @builtins.property
    @jsii.member(jsii_name="msg")
    def msg(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "msg"))

    @builtins.property
    @jsii.member(jsii_name="supportUrl")
    def support_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "supportUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettings]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__244ba11c0beb70790345213f2754b26fd3c725d313ca85322a97debd0f2582e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ffb56b31ab6b9081d9f4f1aabd992c0a0b26f0b1d92f1094007c1adff0d931ee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="addHeaders")
    def add_headers(self) -> _cdktf_9a9027ec.StringListMap:
        return typing.cast(_cdktf_9a9027ec.StringListMap, jsii.get(self, "addHeaders"))

    @builtins.property
    @jsii.member(jsii_name="allowChildBypass")
    def allow_child_bypass(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowChildBypass"))

    @builtins.property
    @jsii.member(jsii_name="auditSsh")
    def audit_ssh(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSshOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSshOutputReference, jsii.get(self, "auditSsh"))

    @builtins.property
    @jsii.member(jsii_name="bisoAdminControls")
    def biso_admin_controls(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControlsOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControlsOutputReference, jsii.get(self, "bisoAdminControls"))

    @builtins.property
    @jsii.member(jsii_name="blockPage")
    def block_page(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPageOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPageOutputReference, jsii.get(self, "blockPage"))

    @builtins.property
    @jsii.member(jsii_name="blockPageEnabled")
    def block_page_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "blockPageEnabled"))

    @builtins.property
    @jsii.member(jsii_name="blockReason")
    def block_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "blockReason"))

    @builtins.property
    @jsii.member(jsii_name="bypassParentRule")
    def bypass_parent_rule(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "bypassParentRule"))

    @builtins.property
    @jsii.member(jsii_name="checkSession")
    def check_session(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSessionOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSessionOutputReference, jsii.get(self, "checkSession"))

    @builtins.property
    @jsii.member(jsii_name="dnsResolvers")
    def dns_resolvers(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversOutputReference, jsii.get(self, "dnsResolvers"))

    @builtins.property
    @jsii.member(jsii_name="egress")
    def egress(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgressOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgressOutputReference, jsii.get(self, "egress"))

    @builtins.property
    @jsii.member(jsii_name="ignoreCnameCategoryMatches")
    def ignore_cname_category_matches(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ignoreCnameCategoryMatches"))

    @builtins.property
    @jsii.member(jsii_name="insecureDisableDnssecValidation")
    def insecure_disable_dnssec_validation(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "insecureDisableDnssecValidation"))

    @builtins.property
    @jsii.member(jsii_name="ipCategories")
    def ip_categories(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ipCategories"))

    @builtins.property
    @jsii.member(jsii_name="ipIndicatorFeeds")
    def ip_indicator_feeds(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ipIndicatorFeeds"))

    @builtins.property
    @jsii.member(jsii_name="l4Override")
    def l4_override(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4OverrideOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4OverrideOutputReference, jsii.get(self, "l4Override"))

    @builtins.property
    @jsii.member(jsii_name="notificationSettings")
    def notification_settings(
        self,
    ) -> DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettingsOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettingsOutputReference, jsii.get(self, "notificationSettings"))

    @builtins.property
    @jsii.member(jsii_name="overrideHost")
    def override_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overrideHost"))

    @builtins.property
    @jsii.member(jsii_name="overrideIps")
    def override_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "overrideIps"))

    @builtins.property
    @jsii.member(jsii_name="payloadLog")
    def payload_log(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLogOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLogOutputReference", jsii.get(self, "payloadLog"))

    @builtins.property
    @jsii.member(jsii_name="quarantine")
    def quarantine(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantineOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantineOutputReference", jsii.get(self, "quarantine"))

    @builtins.property
    @jsii.member(jsii_name="redirect")
    def redirect(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirectOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirectOutputReference", jsii.get(self, "redirect"))

    @builtins.property
    @jsii.member(jsii_name="resolveDnsInternally")
    def resolve_dns_internally(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternallyOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternallyOutputReference", jsii.get(self, "resolveDnsInternally"))

    @builtins.property
    @jsii.member(jsii_name="resolveDnsThroughCloudflare")
    def resolve_dns_through_cloudflare(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "resolveDnsThroughCloudflare"))

    @builtins.property
    @jsii.member(jsii_name="untrustedCert")
    def untrusted_cert(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCertOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCertOutputReference", jsii.get(self, "untrustedCert"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettings]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66e89dcac7455542275bff93a1ccbd77fe47a8e35350160f8c1ebefadc477561)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLog",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLog:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4696bded42d18882d5b027103f1d788774d516e9c53a2e52a6c362f9f6e890ac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLog]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f08318bbfc82792f696406d911123489098197bb3f3fc360ad3690f4cfca461d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantine",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantine:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantine(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantineOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantineOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1934cedd6d290b702e8f54a2d6c73c4716af77c5194ad61ffa46afb50ad5bd42)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="fileTypes")
    def file_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "fileTypes"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantine]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantine], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantine],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6ac9c8b32fdeb20a55db45360aeb810d808f668e1a7af6bb057e05ded7cea21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirect",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirect:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirect(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirectOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirectOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__76811ab42e39d922aac27ab3ad055024f7ecb7278f6a65765a2cf29f5fa25209)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="includeContext")
    def include_context(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "includeContext"))

    @builtins.property
    @jsii.member(jsii_name="preservePathAndQuery")
    def preserve_path_and_query(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "preservePathAndQuery"))

    @builtins.property
    @jsii.member(jsii_name="targetUri")
    def target_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetUri"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirect]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirect], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirect],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f3a7f12352e86d8305fa6fdcb64823ffa85e3bea217f75e2d2f8b4c608ffb5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternally",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternally:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternally(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternallyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternallyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fbbc9192e20ada69616127f376e27eee2ce4fcaf5c47e529416d1c2bdf367e1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="fallback")
    def fallback(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fallback"))

    @builtins.property
    @jsii.member(jsii_name="viewId")
    def view_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "viewId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternally]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternally], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternally],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__661567626158ef3e19b3cebd05df969eb4645fe57cc25065b3ba5b4c24f3895e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCert",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCert:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCert(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCertOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCertOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b642814b13b7b6297a8d76dae327250ac55e22f893fc567674337131fd6d970c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCert]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCert], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCert],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b4f434fb91e096e1126ee999efbab3bdf5ffb5df0ccd169dfafbd3f3f7fa12f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultSchedule",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPoliciesResultSchedule:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPoliciesResultSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPoliciesResultScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicies.DataCloudflareZeroTrustGatewayPoliciesResultScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3674435dbd8c0f0c2a6303c308764f7123ac0e1212c5ec4c166bc08bda234484)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="fri")
    def fri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fri"))

    @builtins.property
    @jsii.member(jsii_name="mon")
    def mon(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mon"))

    @builtins.property
    @jsii.member(jsii_name="sat")
    def sat(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sat"))

    @builtins.property
    @jsii.member(jsii_name="sun")
    def sun(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sun"))

    @builtins.property
    @jsii.member(jsii_name="thu")
    def thu(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thu"))

    @builtins.property
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZone"))

    @builtins.property
    @jsii.member(jsii_name="tue")
    def tue(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tue"))

    @builtins.property
    @jsii.member(jsii_name="wed")
    def wed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wed"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultSchedule]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultSchedule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e51668d618992c5622d5a3075d32ffbda2dc47f70e2f402d81db28de9743c3cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustGatewayPolicies",
    "DataCloudflareZeroTrustGatewayPoliciesConfig",
    "DataCloudflareZeroTrustGatewayPoliciesResult",
    "DataCloudflareZeroTrustGatewayPoliciesResultExpiration",
    "DataCloudflareZeroTrustGatewayPoliciesResultExpirationOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultList",
    "DataCloudflareZeroTrustGatewayPoliciesResultOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettings",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSsh",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSshOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControls",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControlsOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPage",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPageOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSession",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSessionOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolvers",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4List",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4OutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6List",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6OutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgress",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgressOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4Override",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4OverrideOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettings",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettingsOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLog",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLogOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantine",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantineOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirect",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirectOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternally",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternallyOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCert",
    "DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCertOutputReference",
    "DataCloudflareZeroTrustGatewayPoliciesResultSchedule",
    "DataCloudflareZeroTrustGatewayPoliciesResultScheduleOutputReference",
]

publication.publish()

def _typecheckingstub__1b6268f6b22db0900ec9ee67b3a8d05cb78961b9b48ef1811826a941325281a7(
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

def _typecheckingstub__8da2fba1330ed9e6e48ce217207d23554a3dd90b0efb4baddb4abe9c9312aa4c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c83900fe15a58fba69e241e7da48f6aa36e1b5ec54e8760d360c5966beb460d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adb157558a71026bd81606421b4820e5c2b4ad059724e66b35a9bda750542697(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d96a632c482fefadf8cea9d7a0277aee8ccc09f61fb31dabf014fa4b80afb4e2(
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

def _typecheckingstub__e2fba18bb1a53d44b4a6d949de68c755f46566f83972d2ef246136dd6f0be435(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f91cbbdad3457f28b2af9f2688e6e386216fcdb2cd6f84a23df0115bee18b08(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultExpiration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79d45cf7d87ee2fc5981d0b248c8cdd3b65344593ad46ac586376ece72c8d63b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__142a3ac970866b69b51a6025f269edd9d499828ff8e337af4ea9adb7c42150e2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f122fa254b2318f0efc8d36e5250ad8e4f2a8e60ee9aab9b56ddacf87c94ef2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6028fa6756f556949d94e220ff959d07753a6a615211f8c575044bbe02e1d071(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f30277bd266c9f00709eb4c61307fcd8cc8649092b73596e6a0194a6bd497db0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8612deb149ddf48e465fbca8265d16dc94b935e76d17f87ef865f73356a6e115(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5e6580db4560b2038add49da24473c1b5603ca0a6925eb0f34be63e54901253(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b77c398b4381a644aab2afb6ba04a1a1d90da87cc66da026584975c8fa14782(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7632c96eb4098267b1095cddc1b0c2bcdb8584a9de97e9d331c70f0b98b2ddae(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsAuditSsh],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71399613df674f48aa5e3ae32ce8c0c7a63b2d5cf063d854fae1493b9a1b837a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48bd17dc5ab1d1ef95b5dba905f1b995d11633c10fb243ce32c29ac5a979c4b1(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBisoAdminControls],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9261de2175edb182908a00629bf4a095df238ac12c923883116580a23b13fb8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fde548f457674cdcd28ea35cceedffd9e6b06ee232332344fb55f14574581c5(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsBlockPage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdb834b9812a8f9a694c28c7a8a3e740c54c5de01de94d1a51d14ca04a2a42b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0948ce2f9d1ed94270edcf29300d087f621850ea934b92b2662b861545011121(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsCheckSession],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__701fe26d533f993ed0f776e71dca70f4fd35951ded127c944234549b74945b7e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56302ef3cedba855e3d40cdff99654dd85be6f9ff47d5398c69c7105feeb511b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6993c6a2f6e98109de1a917454ed165ef2440a07b7939a6d0859b49f474ed1ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1aa150b4531b640adbce872da555801d42ac9d2728b7d094a81fb2d5989e601(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d63b9604e8d80d14290470d36b06561ee59605bbb404929aaddae645e8a579db(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0441266defb652a3a40439106718176f8b42cbad39b04686048950601943d302(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fec7d8a3523174d926e6735be59ba0bf5ed5201f15bf2bf2d6dc0dbd0a2b707(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv4],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faf5c4121532c8932e0b42eabe5dd21f5647fe56bb4f8ba0f522aa88245cfb72(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf846bd3b8df2ebd624800ac4fb91cca2c645450b632595e116c0a5c57b317c6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e9637973493abd47933c814a85fe1a2ec5c8dc8df7bc6ad8125312bea78c5b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7068cfbe2620d4be2779c667f849b84aecd189712adbb11c2a008983773eec42(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d164f7fc330a308f0f9ce2e1c721a7ef0336db15dec3613ce81be69d2d481aa(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__011f2361ac014a19e6f02ecdec31dc61ec218634974c843d4cd26e5a1abf3ea0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87f0b87cac7d383eb368fa5833818a9308deb58b0f8534948223e0ff1dce2ba2(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolversIpv6],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96815029f21bd68be5ecbc19a17fa066945b57b9d314648e86df8cecdf7f556e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02903b763c32923ea4aa814f0d44a900c0a0f7fa900a98dfe80a0723a3b2cbf5(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsDnsResolvers],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b5f79b37ee659661e964cbf3c8d29a0afd317ff6c15758304ed332f0fe59528(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a91e8e410ce7977e91edf114e0f5fd99ce3cec0e8103050e3323b4fc0c47015(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsEgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce0f6dbff61fce3f9409ca6acd706afd1b6d6344dfc8e8a2b89b563a77a1aea4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e63d6f71faedd7ee242b7534eb730b23f06e1ac107f89310a268fa453ec502f6(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsL4Override],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cbfd09d337fb47619d0ca3ebddffe40a5fd25e675d6c25a81bc17e0acebe59f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__244ba11c0beb70790345213f2754b26fd3c725d313ca85322a97debd0f2582e8(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsNotificationSettings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffb56b31ab6b9081d9f4f1aabd992c0a0b26f0b1d92f1094007c1adff0d931ee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66e89dcac7455542275bff93a1ccbd77fe47a8e35350160f8c1ebefadc477561(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4696bded42d18882d5b027103f1d788774d516e9c53a2e52a6c362f9f6e890ac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f08318bbfc82792f696406d911123489098197bb3f3fc360ad3690f4cfca461d(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsPayloadLog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1934cedd6d290b702e8f54a2d6c73c4716af77c5194ad61ffa46afb50ad5bd42(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6ac9c8b32fdeb20a55db45360aeb810d808f668e1a7af6bb057e05ded7cea21(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsQuarantine],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76811ab42e39d922aac27ab3ad055024f7ecb7278f6a65765a2cf29f5fa25209(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f3a7f12352e86d8305fa6fdcb64823ffa85e3bea217f75e2d2f8b4c608ffb5b(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsRedirect],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fbbc9192e20ada69616127f376e27eee2ce4fcaf5c47e529416d1c2bdf367e1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__661567626158ef3e19b3cebd05df969eb4645fe57cc25065b3ba5b4c24f3895e(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsResolveDnsInternally],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b642814b13b7b6297a8d76dae327250ac55e22f893fc567674337131fd6d970c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b4f434fb91e096e1126ee999efbab3bdf5ffb5df0ccd169dfafbd3f3f7fa12f(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultRuleSettingsUntrustedCert],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3674435dbd8c0f0c2a6303c308764f7123ac0e1212c5ec4c166bc08bda234484(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e51668d618992c5622d5a3075d32ffbda2dc47f70e2f402d81db28de9743c3cb(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPoliciesResultSchedule],
) -> None:
    """Type checking stubs"""
    pass
