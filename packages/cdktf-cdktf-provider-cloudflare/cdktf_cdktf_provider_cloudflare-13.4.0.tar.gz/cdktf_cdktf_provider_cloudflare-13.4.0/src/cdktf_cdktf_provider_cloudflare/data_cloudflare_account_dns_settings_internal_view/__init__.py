r'''
# `data_cloudflare_account_dns_settings_internal_view`

Refer to the Terraform Registry for docs: [`data_cloudflare_account_dns_settings_internal_view`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view).
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


class DataCloudflareAccountDnsSettingsInternalView(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareAccountDnsSettingsInternalView.DataCloudflareAccountDnsSettingsInternalView",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view cloudflare_account_dns_settings_internal_view}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        filter: typing.Optional[typing.Union["DataCloudflareAccountDnsSettingsInternalViewFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        view_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view cloudflare_account_dns_settings_internal_view} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#account_id DataCloudflareAccountDnsSettingsInternalView#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#filter DataCloudflareAccountDnsSettingsInternalView#filter}.
        :param view_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#view_id DataCloudflareAccountDnsSettingsInternalView#view_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__855a7e6ab7840771c14d88e33b89998b3dbea43d645952b16658f265a94151b1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareAccountDnsSettingsInternalViewConfig(
            account_id=account_id,
            filter=filter,
            view_id=view_id,
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
        '''Generates CDKTF code for importing a DataCloudflareAccountDnsSettingsInternalView resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareAccountDnsSettingsInternalView to import.
        :param import_from_id: The id of the existing DataCloudflareAccountDnsSettingsInternalView that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareAccountDnsSettingsInternalView to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__905bdfbfe05fac8a71ab8ad50d33f034b174d7078963e56a5383e814d7834280)
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
        match: typing.Optional[builtins.str] = None,
        name: typing.Optional[typing.Union["DataCloudflareAccountDnsSettingsInternalViewFilterName", typing.Dict[builtins.str, typing.Any]]] = None,
        order: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
        zone_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param direction: Direction to order DNS views in. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#direction DataCloudflareAccountDnsSettingsInternalView#direction}
        :param match: Whether to match all search requirements or at least one (any). If set to ``all``, acts like a logical AND between filters. If set to ``any``, acts like a logical OR instead. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#match DataCloudflareAccountDnsSettingsInternalView#match}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#name DataCloudflareAccountDnsSettingsInternalView#name}.
        :param order: Field to order DNS views by. Available values: "name", "created_on", "modified_on". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#order DataCloudflareAccountDnsSettingsInternalView#order}
        :param zone_id: A zone ID that exists in the zones list for the view. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#zone_id DataCloudflareAccountDnsSettingsInternalView#zone_id}
        :param zone_name: A zone name that exists in the zones list for the view. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#zone_name DataCloudflareAccountDnsSettingsInternalView#zone_name}
        '''
        value = DataCloudflareAccountDnsSettingsInternalViewFilter(
            direction=direction,
            match=match,
            name=name,
            order=order,
            zone_id=zone_id,
            zone_name=zone_name,
        )

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetViewId")
    def reset_view_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViewId", []))

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
    @jsii.member(jsii_name="createdTime")
    def created_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdTime"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(
        self,
    ) -> "DataCloudflareAccountDnsSettingsInternalViewFilterOutputReference":
        return typing.cast("DataCloudflareAccountDnsSettingsInternalViewFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="modifiedTime")
    def modified_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedTime"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="zones")
    def zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "zones"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareAccountDnsSettingsInternalViewFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareAccountDnsSettingsInternalViewFilter"]], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="viewIdInput")
    def view_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "viewIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9b548a2edf1163fd6213f2decb1d3937283a0153e8d331df6ccfd1fd9c09a38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="viewId")
    def view_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "viewId"))

    @view_id.setter
    def view_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20926c059dbaa28868f405eab8a3fa187ff7d32a2c73c4dc70cc1729f2772903)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "viewId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareAccountDnsSettingsInternalView.DataCloudflareAccountDnsSettingsInternalViewConfig",
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
        "filter": "filter",
        "view_id": "viewId",
    },
)
class DataCloudflareAccountDnsSettingsInternalViewConfig(
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
        filter: typing.Optional[typing.Union["DataCloudflareAccountDnsSettingsInternalViewFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        view_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#account_id DataCloudflareAccountDnsSettingsInternalView#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#filter DataCloudflareAccountDnsSettingsInternalView#filter}.
        :param view_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#view_id DataCloudflareAccountDnsSettingsInternalView#view_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = DataCloudflareAccountDnsSettingsInternalViewFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__699ea9ae1f8bb4ffc2473f97479c923bfcc4fd61d13f24d09f2756df3c7006bf)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument view_id", value=view_id, expected_type=type_hints["view_id"])
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
        if filter is not None:
            self._values["filter"] = filter
        if view_id is not None:
            self._values["view_id"] = view_id

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#account_id DataCloudflareAccountDnsSettingsInternalView#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(
        self,
    ) -> typing.Optional["DataCloudflareAccountDnsSettingsInternalViewFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#filter DataCloudflareAccountDnsSettingsInternalView#filter}.'''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["DataCloudflareAccountDnsSettingsInternalViewFilter"], result)

    @builtins.property
    def view_id(self) -> typing.Optional[builtins.str]:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#view_id DataCloudflareAccountDnsSettingsInternalView#view_id}
        '''
        result = self._values.get("view_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareAccountDnsSettingsInternalViewConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareAccountDnsSettingsInternalView.DataCloudflareAccountDnsSettingsInternalViewFilter",
    jsii_struct_bases=[],
    name_mapping={
        "direction": "direction",
        "match": "match",
        "name": "name",
        "order": "order",
        "zone_id": "zoneId",
        "zone_name": "zoneName",
    },
)
class DataCloudflareAccountDnsSettingsInternalViewFilter:
    def __init__(
        self,
        *,
        direction: typing.Optional[builtins.str] = None,
        match: typing.Optional[builtins.str] = None,
        name: typing.Optional[typing.Union["DataCloudflareAccountDnsSettingsInternalViewFilterName", typing.Dict[builtins.str, typing.Any]]] = None,
        order: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
        zone_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param direction: Direction to order DNS views in. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#direction DataCloudflareAccountDnsSettingsInternalView#direction}
        :param match: Whether to match all search requirements or at least one (any). If set to ``all``, acts like a logical AND between filters. If set to ``any``, acts like a logical OR instead. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#match DataCloudflareAccountDnsSettingsInternalView#match}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#name DataCloudflareAccountDnsSettingsInternalView#name}.
        :param order: Field to order DNS views by. Available values: "name", "created_on", "modified_on". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#order DataCloudflareAccountDnsSettingsInternalView#order}
        :param zone_id: A zone ID that exists in the zones list for the view. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#zone_id DataCloudflareAccountDnsSettingsInternalView#zone_id}
        :param zone_name: A zone name that exists in the zones list for the view. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#zone_name DataCloudflareAccountDnsSettingsInternalView#zone_name}
        '''
        if isinstance(name, dict):
            name = DataCloudflareAccountDnsSettingsInternalViewFilterName(**name)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7130a5d472dcd1371deff1990dc0c8b20f7c168a713dde2a498b0cd9664518f7)
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument match", value=match, expected_type=type_hints["match"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument order", value=order, expected_type=type_hints["order"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument zone_name", value=zone_name, expected_type=type_hints["zone_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if direction is not None:
            self._values["direction"] = direction
        if match is not None:
            self._values["match"] = match
        if name is not None:
            self._values["name"] = name
        if order is not None:
            self._values["order"] = order
        if zone_id is not None:
            self._values["zone_id"] = zone_id
        if zone_name is not None:
            self._values["zone_name"] = zone_name

    @builtins.property
    def direction(self) -> typing.Optional[builtins.str]:
        '''Direction to order DNS views in. Available values: "asc", "desc".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#direction DataCloudflareAccountDnsSettingsInternalView#direction}
        '''
        result = self._values.get("direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def match(self) -> typing.Optional[builtins.str]:
        '''Whether to match all search requirements or at least one (any).

        If set to ``all``, acts like a logical AND between filters. If set to ``any``, acts like a logical OR instead.
        Available values: "any", "all".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#match DataCloudflareAccountDnsSettingsInternalView#match}
        '''
        result = self._values.get("match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(
        self,
    ) -> typing.Optional["DataCloudflareAccountDnsSettingsInternalViewFilterName"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#name DataCloudflareAccountDnsSettingsInternalView#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional["DataCloudflareAccountDnsSettingsInternalViewFilterName"], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''Field to order DNS views by. Available values: "name", "created_on", "modified_on".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#order DataCloudflareAccountDnsSettingsInternalView#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''A zone ID that exists in the zones list for the view.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#zone_id DataCloudflareAccountDnsSettingsInternalView#zone_id}
        '''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_name(self) -> typing.Optional[builtins.str]:
        '''A zone name that exists in the zones list for the view.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#zone_name DataCloudflareAccountDnsSettingsInternalView#zone_name}
        '''
        result = self._values.get("zone_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareAccountDnsSettingsInternalViewFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareAccountDnsSettingsInternalView.DataCloudflareAccountDnsSettingsInternalViewFilterName",
    jsii_struct_bases=[],
    name_mapping={
        "contains": "contains",
        "endswith": "endswith",
        "exact": "exact",
        "startswith": "startswith",
    },
)
class DataCloudflareAccountDnsSettingsInternalViewFilterName:
    def __init__(
        self,
        *,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param contains: Substring of the DNS view name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#contains DataCloudflareAccountDnsSettingsInternalView#contains}
        :param endswith: Suffix of the DNS view name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#endswith DataCloudflareAccountDnsSettingsInternalView#endswith}
        :param exact: Exact value of the DNS view name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#exact DataCloudflareAccountDnsSettingsInternalView#exact}
        :param startswith: Prefix of the DNS view name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#startswith DataCloudflareAccountDnsSettingsInternalView#startswith}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8da8af2463661dbcc491aa43733678b63e242d4e077c8fa0a42dda1235950d63)
            check_type(argname="argument contains", value=contains, expected_type=type_hints["contains"])
            check_type(argname="argument endswith", value=endswith, expected_type=type_hints["endswith"])
            check_type(argname="argument exact", value=exact, expected_type=type_hints["exact"])
            check_type(argname="argument startswith", value=startswith, expected_type=type_hints["startswith"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if contains is not None:
            self._values["contains"] = contains
        if endswith is not None:
            self._values["endswith"] = endswith
        if exact is not None:
            self._values["exact"] = exact
        if startswith is not None:
            self._values["startswith"] = startswith

    @builtins.property
    def contains(self) -> typing.Optional[builtins.str]:
        '''Substring of the DNS view name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#contains DataCloudflareAccountDnsSettingsInternalView#contains}
        '''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endswith(self) -> typing.Optional[builtins.str]:
        '''Suffix of the DNS view name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#endswith DataCloudflareAccountDnsSettingsInternalView#endswith}
        '''
        result = self._values.get("endswith")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Exact value of the DNS view name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#exact DataCloudflareAccountDnsSettingsInternalView#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startswith(self) -> typing.Optional[builtins.str]:
        '''Prefix of the DNS view name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#startswith DataCloudflareAccountDnsSettingsInternalView#startswith}
        '''
        result = self._values.get("startswith")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareAccountDnsSettingsInternalViewFilterName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareAccountDnsSettingsInternalViewFilterNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareAccountDnsSettingsInternalView.DataCloudflareAccountDnsSettingsInternalViewFilterNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2a44ad5bb6148ca01fb01d578548f65156b49be37a04cf279a1a9744433a9a4e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetContains")
    def reset_contains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContains", []))

    @jsii.member(jsii_name="resetEndswith")
    def reset_endswith(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndswith", []))

    @jsii.member(jsii_name="resetExact")
    def reset_exact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExact", []))

    @jsii.member(jsii_name="resetStartswith")
    def reset_startswith(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartswith", []))

    @builtins.property
    @jsii.member(jsii_name="containsInput")
    def contains_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containsInput"))

    @builtins.property
    @jsii.member(jsii_name="endswithInput")
    def endswith_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endswithInput"))

    @builtins.property
    @jsii.member(jsii_name="exactInput")
    def exact_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "exactInput"))

    @builtins.property
    @jsii.member(jsii_name="startswithInput")
    def startswith_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startswithInput"))

    @builtins.property
    @jsii.member(jsii_name="contains")
    def contains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contains"))

    @contains.setter
    def contains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e82265588f20709ff7efdfadaf7548fc8f994003ce666809c0f496f2c4f1aced)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endswith")
    def endswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endswith"))

    @endswith.setter
    def endswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70768c107edfb8d1e0dd37de8fded4e6d9b21f4d0227742d17c6c3274a64ae5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__493c0f26fe956247bba6acbf7d0d6d854d030e352e0060cae0724eff90b36c2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startswith")
    def startswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startswith"))

    @startswith.setter
    def startswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d111f704efbb9bdc77a9980182a66dab10cf2a76a4223424929bcdb65e02649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilterName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilterName]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilterName]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3838dd4c44d035846f28aa45e8d76d4661ac87839c3d82033310f5741e5e88a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareAccountDnsSettingsInternalViewFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareAccountDnsSettingsInternalView.DataCloudflareAccountDnsSettingsInternalViewFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0438aa8b29d2b2ef9e090e0f69d33522fc9457c2169016dfe208bb67831f770)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putName")
    def put_name(
        self,
        *,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param contains: Substring of the DNS view name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#contains DataCloudflareAccountDnsSettingsInternalView#contains}
        :param endswith: Suffix of the DNS view name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#endswith DataCloudflareAccountDnsSettingsInternalView#endswith}
        :param exact: Exact value of the DNS view name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#exact DataCloudflareAccountDnsSettingsInternalView#exact}
        :param startswith: Prefix of the DNS view name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/account_dns_settings_internal_view#startswith DataCloudflareAccountDnsSettingsInternalView#startswith}
        '''
        value = DataCloudflareAccountDnsSettingsInternalViewFilterName(
            contains=contains, endswith=endswith, exact=exact, startswith=startswith
        )

        return typing.cast(None, jsii.invoke(self, "putName", [value]))

    @jsii.member(jsii_name="resetDirection")
    def reset_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirection", []))

    @jsii.member(jsii_name="resetMatch")
    def reset_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatch", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOrder")
    def reset_order(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrder", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

    @jsii.member(jsii_name="resetZoneName")
    def reset_zone_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneName", []))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(
        self,
    ) -> DataCloudflareAccountDnsSettingsInternalViewFilterNameOutputReference:
        return typing.cast(DataCloudflareAccountDnsSettingsInternalViewFilterNameOutputReference, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property
    @jsii.member(jsii_name="matchInput")
    def match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "matchInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilterName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilterName]], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="orderInput")
    def order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orderInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneNameInput")
    def zone_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneNameInput"))

    @builtins.property
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0831fb1299e5a3bf6794d15393e5399d0694437be81542b22b33f4f0adb14f8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="match")
    def match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "match"))

    @match.setter
    def match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62c6d5fc9475a4860a43fca4dc2a523c589bd1b4e55f16d041a14d9b0113ca03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "match", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="order")
    def order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "order"))

    @order.setter
    def order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce35ea093e9590f31183223e4fc31d7c638ad5adab777e25d2a64b69a66cce76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "order", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c24a6e97bc582a90d4d04dc45cd9351e17c1b3502d91fe5de78b5a9576ee05d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @zone_name.setter
    def zone_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c10a402bf94d718d10bc1170aba85a45b28f3e0805f09a308f53624d923cde1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2727a1abd31eaaa4182b68bc7ebd3d1c5aa822f3802e88037cd36c1cac9cec3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareAccountDnsSettingsInternalView",
    "DataCloudflareAccountDnsSettingsInternalViewConfig",
    "DataCloudflareAccountDnsSettingsInternalViewFilter",
    "DataCloudflareAccountDnsSettingsInternalViewFilterName",
    "DataCloudflareAccountDnsSettingsInternalViewFilterNameOutputReference",
    "DataCloudflareAccountDnsSettingsInternalViewFilterOutputReference",
]

publication.publish()

def _typecheckingstub__855a7e6ab7840771c14d88e33b89998b3dbea43d645952b16658f265a94151b1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareAccountDnsSettingsInternalViewFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    view_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__905bdfbfe05fac8a71ab8ad50d33f034b174d7078963e56a5383e814d7834280(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9b548a2edf1163fd6213f2decb1d3937283a0153e8d331df6ccfd1fd9c09a38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20926c059dbaa28868f405eab8a3fa187ff7d32a2c73c4dc70cc1729f2772903(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__699ea9ae1f8bb4ffc2473f97479c923bfcc4fd61d13f24d09f2756df3c7006bf(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareAccountDnsSettingsInternalViewFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    view_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7130a5d472dcd1371deff1990dc0c8b20f7c168a713dde2a498b0cd9664518f7(
    *,
    direction: typing.Optional[builtins.str] = None,
    match: typing.Optional[builtins.str] = None,
    name: typing.Optional[typing.Union[DataCloudflareAccountDnsSettingsInternalViewFilterName, typing.Dict[builtins.str, typing.Any]]] = None,
    order: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
    zone_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8da8af2463661dbcc491aa43733678b63e242d4e077c8fa0a42dda1235950d63(
    *,
    contains: typing.Optional[builtins.str] = None,
    endswith: typing.Optional[builtins.str] = None,
    exact: typing.Optional[builtins.str] = None,
    startswith: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a44ad5bb6148ca01fb01d578548f65156b49be37a04cf279a1a9744433a9a4e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e82265588f20709ff7efdfadaf7548fc8f994003ce666809c0f496f2c4f1aced(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70768c107edfb8d1e0dd37de8fded4e6d9b21f4d0227742d17c6c3274a64ae5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__493c0f26fe956247bba6acbf7d0d6d854d030e352e0060cae0724eff90b36c2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d111f704efbb9bdc77a9980182a66dab10cf2a76a4223424929bcdb65e02649(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3838dd4c44d035846f28aa45e8d76d4661ac87839c3d82033310f5741e5e88a8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilterName]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0438aa8b29d2b2ef9e090e0f69d33522fc9457c2169016dfe208bb67831f770(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0831fb1299e5a3bf6794d15393e5399d0694437be81542b22b33f4f0adb14f8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62c6d5fc9475a4860a43fca4dc2a523c589bd1b4e55f16d041a14d9b0113ca03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce35ea093e9590f31183223e4fc31d7c638ad5adab777e25d2a64b69a66cce76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c24a6e97bc582a90d4d04dc45cd9351e17c1b3502d91fe5de78b5a9576ee05d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c10a402bf94d718d10bc1170aba85a45b28f3e0805f09a308f53624d923cde1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2727a1abd31eaaa4182b68bc7ebd3d1c5aa822f3802e88037cd36c1cac9cec3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareAccountDnsSettingsInternalViewFilter]],
) -> None:
    """Type checking stubs"""
    pass
