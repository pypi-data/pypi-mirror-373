r'''
# `data_cloudflare_zero_trust_access_groups`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_access_groups`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups).
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


class DataCloudflareZeroTrustAccessGroups(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroups",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups cloudflare_zero_trust_access_groups}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        max_items: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        search: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups cloudflare_zero_trust_access_groups} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#account_id DataCloudflareZeroTrustAccessGroups#account_id}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#max_items DataCloudflareZeroTrustAccessGroups#max_items}
        :param name: The name of the group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#name DataCloudflareZeroTrustAccessGroups#name}
        :param search: Search for groups by other listed query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#search DataCloudflareZeroTrustAccessGroups#search}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#zone_id DataCloudflareZeroTrustAccessGroups#zone_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6ac620620861a91a14a53e8ffa4c59a39f45eb7197f290c4a90e7a17d2030c0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustAccessGroupsConfig(
            account_id=account_id,
            max_items=max_items,
            name=name,
            search=search,
            zone_id=zone_id,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustAccessGroups resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustAccessGroups to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustAccessGroups that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustAccessGroups to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a890ff65e15a9d737d1cf8f15c4e9c746e4447e31e3a144afdf9a9d375c6050)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetMaxItems")
    def reset_max_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxItems", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSearch")
    def reset_search(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearch", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

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
    def result(self) -> "DataCloudflareZeroTrustAccessGroupsResultList":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultList", jsii.get(self, "result"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="maxItemsInput")
    def max_items_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxItemsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="searchInput")
    def search_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "searchInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed522c04b10002210917b665626f7aea6153e52f9c6e5f178465f6f3cb65a5ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxItems")
    def max_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxItems"))

    @max_items.setter
    def max_items(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4e1514b9c9f6ca2f04d974e258b89e15f1cd39c294045ef57ae1dff18c28f0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxItems", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7735fc9edc1235ff9dcb8d6b5bfdace46e2666e3278ca868e344f95ac527fd37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="search")
    def search(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "search"))

    @search.setter
    def search(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b2151d7eab5c7cec3aec4ca272b3964c12c6b81090dd83d38a1e800be7c751e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "search", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b635ea7b10d9648e90ef4464da61bb9669b0a73c0de8be5cdbd4c5da9566fd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsConfig",
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
        "name": "name",
        "search": "search",
        "zone_id": "zoneId",
    },
)
class DataCloudflareZeroTrustAccessGroupsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        account_id: typing.Optional[builtins.str] = None,
        max_items: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        search: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#account_id DataCloudflareZeroTrustAccessGroups#account_id}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#max_items DataCloudflareZeroTrustAccessGroups#max_items}
        :param name: The name of the group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#name DataCloudflareZeroTrustAccessGroups#name}
        :param search: Search for groups by other listed query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#search DataCloudflareZeroTrustAccessGroups#search}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#zone_id DataCloudflareZeroTrustAccessGroups#zone_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__749892a8a43bc92fb491ec18ba8075504cc35dc069d1cb83a9837019bbacfb3d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument max_items", value=max_items, expected_type=type_hints["max_items"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument search", value=search, expected_type=type_hints["search"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if max_items is not None:
            self._values["max_items"] = max_items
        if name is not None:
            self._values["name"] = name
        if search is not None:
            self._values["search"] = search
        if zone_id is not None:
            self._values["zone_id"] = zone_id

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
    def account_id(self) -> typing.Optional[builtins.str]:
        '''The Account ID to use for this endpoint. Mutually exclusive with the Zone ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#account_id DataCloudflareZeroTrustAccessGroups#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_items(self) -> typing.Optional[jsii.Number]:
        '''Max items to fetch, default: 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#max_items DataCloudflareZeroTrustAccessGroups#max_items}
        '''
        result = self._values.get("max_items")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#name DataCloudflareZeroTrustAccessGroups#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def search(self) -> typing.Optional[builtins.str]:
        '''Search for groups by other listed query parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#search DataCloudflareZeroTrustAccessGroups#search}
        '''
        result = self._values.get("search")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''The Zone ID to use for this endpoint. Mutually exclusive with the Account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_groups#zone_id DataCloudflareZeroTrustAccessGroups#zone_id}
        '''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExclude",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExclude:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ddfd593e34700191a509fa99a31cf6c92b2cf90aa567393ed26a94c4e046135)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__092e70cf43af5e8b75939743114b30c60afc4e1567fe21083e26e566f55e8683)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__89d1c4bf88ef8a4b9d9d29966dc56566c485a166e2af00e5e4d5bf0f228ab14c)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc09846fa4a4ac029a79b6e4405de60f5557078dc6ddcc699910f966744504ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__74a24059182d6ce88aa1140fa591ac91f09f780be6e130a999e2da30b17e39e5)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95422ee13107717b349612a5b11fcd8a77df81f08ea8f3a829d58a3672e7de9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__df8d4dfca366180fb92d74c8eb68b3f0ab1751e6fac403a8d36487c9ca099382)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2299e7bf71934fb4bfef8866c0d0d0d7559e83e3f351ea30d08aad89a90db7cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__04cdd650a80321b5e26349ffe2c94f04e1a4981ed789d2a1aae91bb7a071ef64)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6456261f8fb8ea8a5df66e8e8b29bcc8f71864a97db7d5d6cd79daf3db261d8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc95d2c15715417ef1944d7ea1bae0700efb8548cc9ff3eae7744c33045dceca)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4d1b6117cba437296cd3ad2593f168a5a8491eebd0a4285fc81120828bb5b41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd499992dc3295d0aeb0a68c6de4b9d4c92b27d0a8db5ffbe1abbae37693ee9a)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a04334328a8051a38248af85742c220ae6b1c472450b3eea9808aff5b195c7b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__400157c781e598f695bf3fabb81c84264cd400e8f34d3cc3685f73a7cdff26ca)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe07a4fa1d0d0d5ecc28bb503db7602be26ab6c8420c4c4dc0b32a621dcf4082)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c623a8e0a306d7f034528270eca6b0422ef2f8c08c1c791bdb1b85a1f1d26a80)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fa5c2e6252e995280330f67f44e6a774b09e018c141b5208e091319cc517bad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultExcludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__02d8b778f7f19e59e097be82b8f1859e39ff1d4ec334a67deb7196c7f79f3782)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b029a6216b805c708c4325950f1ba82aeef012f43ead80366a9530ec0d65b6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e76725d6ec0e80e5c0c9e6bbbb5b27283bb93390aaeb6ad187f58e0fbeca7de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44eef87fa9e1608bb075604566ac607a1a39a1c9182c651cc07b302490f8a0b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__77672746f310de00bc4a2a3d3ac588f044ba7dc9d29e651144553256459bfebe)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e2bb1c1f0e7a31bea09e86f6d9a57988fddd78d9e381bf1519c331e596237af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2615dff3162ed51bcc2d1452e1a2a812d6c192b37fc4e2cf1b95f8cc1db26b79)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f020ece4e9c22fc2c113980d36306f1ad453aea45742938389e11dc08ec4a4b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9b3688a028a7c1fb8112f730129d6cf588abd6da6baf0c9f7b6984fd63825496)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__802cc09ce7008f1bade70f767653a6fc792e563c55112b9c36e2e8510fb3a766)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4564b46d9becd5e55c2d2d715e889d7f398cc2b29be7faa70adbab5d2c8b942a)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b962d01ea0cfa920613256b16dcb893d4d836070ec1ae3a503a66ec1c2a87a8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f253065ca7f9578700a37afddb9661bc7f28e6527e49e3a17de9705e4cf802f5)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71e7fcde06c0bcffc05cf543933df5847cedceb30c65b0a5f7a4a1d1ffd37ff4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__63bbe0cedbd4174222c8642f491a73e2c5ebf68f76b833550fea942d9e3cfebf)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae70a25f87adee67884f8c55285c60b70bdf621c043293d4e237b51a08ce8090)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultExcludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__16cf76a5c0b027598d49267f929de2562e0c4924063cffeba2db17be0efd8edf)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab6f3bc74c7751bb19419c88a72f5b2e59b380dc1ce8dd64072a1ffff1d7610b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bdc933471843ee7f133d4cebc61239d89110fe9cd2b07fde132f3621548fa961)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c54c0ea97d1bc5082eae157be617c9e094f379f0431f71c9f014ddb8d65ff1dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultExcludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1389b0aba9b21203329b9aa76cd92744f2e88ea0dc7e525459dc2923009f058b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultExcludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ffe6e1bbdf49d73e48b9631a118e6ba4cc1044406baea07e51d52368d283f68)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultExcludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__772416980e04a4251f8c8ae10f46c0c3fb40033a51860069eb07d4296cdc715e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3d6ed6fd92636c09284406f7df1bd390e43a49a83e7fd45b5f4d5b477feab683)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e281e1bd9d117f7bd86f4f0be16536ce6d33d51dc976601ce57932e3e61d0d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__55d59e7ee0d5d64e110338fe073eaa0d6ea1d4b5d81a9cc7427cc1a6755f3d29)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c3aa7d38bac0cda6dfc2a1f906513e4968ddbbe8ebf8e6a0b10b1989aa0ea1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e09c6b0369b087b732da1e2933295d06b05021c5e058031d8affe8389252de81)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3c2e39be82fdb8ef01ab25df430856302fdbdb108d253808e291655c0dba7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81e0ce500d255ab289239ee2ce85d78a36c5c042397d79b4b6e43b67abdf95bb)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb604878f3bbb22f44a539baf88d9cdff90185bb79879fab5fc8f996619dc7ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultExcludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32af06ec51e1b1938e7148d329dce41d7f78bd196bb980db4e5e4273831e13d9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> DataCloudflareZeroTrustAccessGroupsResultExcludeGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessGroupsResultExcludeIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultExcludeOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultExcludeSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultExcludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultExcludeServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultExcludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExclude]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExclude], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExclude],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54b7a5381fba5e17dd1c4ff10f4360d4d73570e4f5b24ae96b6773428e20e8ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__60daef9af03e480267833bdb4010fa305fe1c757a5958b05ea565039c46aef58)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f7db55e5d9f66391350499e50c9c63078e50927e1ead4a217365b542f95ba9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultExcludeServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultExcludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultExcludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultExcludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e1eadea4f8cd3766212f2173f5ddbf8ecea1a6b3af486955681123c4cec15fd9)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ac205af8fa9eed49dd259c2767dba7986beb486b16a8629a7e452df222888ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultInclude",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultInclude:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultInclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0264a85173bd193114819871c19aae63972d41e3b950bb7181cd100147de32a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a19880420b0cf5eabdc692db3f144aee900008cd4164c9dc3623ef1333326ae2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e57ece672cc6269dfe36090048ba626613ace6fc4f974e72f0b40fb6a4f8ab3)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__593f38ce303b0838bb266930563fdf97097fdb0c0b30f09f82d1a2dc267c9611)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__732bfa37f7e8fd0106647083b8789b6712e1597a8835b5992973b42069d997b9)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__118fd2231206245b2f68174771b9178e63ab1e2145c0b908356dc0df58de16c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__38026d652bfe2616fcdb89e090d8abf3adc47ec4d91b9bc1f9fd81ddb95a77dd)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d71b5051e66ef4d7081663340a6e8326a7c259ab4eb7a6cfdb8269811e77b55e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd29bc9feb2f8ee170592f240607330802ad786f92aaacf5ba506865d5f0d2af)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24ba4f9138207677098ee98f648bc0a938320060add586afdb58c11418b159c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac7984e2a7e3234c8111419ba2ff76698bec33891a47aa4a1f66406883e08404)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df08fe7233fd7d4224d6e751eb93a6b8bcf07152e73607b855cec518917049cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d069b8bd7c00357efae76d05665b8965395d38d6e22b4c0c5030880150684244)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71ea65c6cb99405fab73624d6ca300ca0e7fd5854e588ce875365096fbf8a1dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__779d65f3544e99aeed668398740c778d697743478155f5cade03b5aec848372e)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__211eb7f84a777f798a8a254dde5bbf6da55519e703c1ec305a20936736962bfe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c522919593b75e184c2dc4c0ce17a26da9f6b7c3a963d7adfa200c8da79f13e5)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faed0c2b86eb8748b1144b61d4c4ee5b2aaa1dfb819df29ee92436db1401749f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultIncludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7860c419c0c6ca2b870247520ab964de8023bcd3830403a57b5190e325baf476)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc2617d2149cb55662f7937f9ee430bdf57adb78337c8da2f976d97d9762b664)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f63c7d5a8580d89dd35d4a4c0721c1d976394b4e7b27453acd44b20b3e30173b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f86a9b3b0870604872e4cafa93e603c59e513ee33a8ee116c71d19928e78167)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__94c115efc8b18c3f206a66c103000134bf16f602c52a4e828b66f40dcf5466d6)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__605aa74f5656a995f5c0e0263d9e43dcf27afeff6bbb6586187a730edada2d6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1fac2a379786fe97a4de67362e9aaab10960b5e573f6e8fc5c8b032937fc91e)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddbd4f2fba54d5d57e2e8da5171718cf628d53091fb80dae1c946fb2232ca2f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe8b31160d7eaa42cd0e762d30ed49a8552b9a752f0f802cf8717420c976c084)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b89862c3b94d261b109c5fe0d026eb34c9efcb85e5a8e862fa62c28eeada191)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__324fb60b4548b853b26e9da3f9b3a48b96f3bd4f44002603d98d5c1806ca04d9)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e7c1d19eeee3f854ec50df414477035a8823b92b81bccbc5a35647372ef8416)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0721923f3954bf2f631754adc04f70bb02bc9fab10dc4ef35d129083b3d63857)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e91bab8dcb7162991f9d0a14928f7ff175e43b09492baba48702d535ccaee52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f12c5e497cd467e845757947ebc2d233d7f54abf1d4c4c900916e1983fa80cd)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2cbb74054dc55ea2bd513e9c3afe4f671cb60c401dc3731a00c861bff432071)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultIncludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__079c1c35c04aeddc0713a42ff08b969cb407b9bf75fae5a36e6c6198664ee34a)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec765db537de47938608ea13f1427d0293fac20e48ae9b91f6faf20a33419b46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4d1bfd9497c4c80dc547689c4c369bdf6456e302991a6dc096c0ae2ebcf8e23b)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41d0d00d32369f3d8817900134c9f9ed9e938ae47078c6284d4d91aa42b5e9b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultIncludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ad9dd4a94ca274c5f0b4139abdd682cd4810ae78d6f91825c5f497699b703a0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultIncludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd02ac985353cf361b190f36fcb913fae91f497244e4a1ad1eabaa62b8ae6dcb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultIncludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78b962bc41de644282cc0c2d1c207b64e302d6ecc82ede91283c11cc214cfedd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f32c27604c77a4d88d62d4e30a32012308eac10435b21a61db5ea3df40fcf53)
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
            type_hints = typing.get_type_hints(_typecheckingstub__78f0fe9c567a6c458156f66c1e1a63241863bb7fce65b8f2fd396168cf3973c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__62d012efd5acc9ce701e080e750086cc1a62e2659071332dcf01abc7e1d5b404)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e620b8c2475b327923bc827de19d279c29f61a7392f5e3cf3d83cf2914f903ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c40be0e14f002b79471a75c27810eaf23e04389c0baf4c389501fd5f3aaaf8aa)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c16c62fd7d5ed6bb91b81e9aa64197d8c34efb5f5e361c913109f3d2cf2bd374)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1236b1ab2cf9d8ff0244c9c6de4b8788df8da6be25b5c79d6bd6fbb586f83a33)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b0630407b5a16222d67cc2ad007a9578610a18eb8ea3ba1ffe5e105c90eb894)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultIncludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__444a77c11797dd3645a3161e899de331e33d245ed7c1b163f914e980c316a1f4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> DataCloudflareZeroTrustAccessGroupsResultIncludeGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessGroupsResultIncludeIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIncludeOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultIncludeSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultIncludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultIncludeServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultIncludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultInclude]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultInclude], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultInclude],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f808781e77f99a740565511e55abd716d53d74513314b19e801ef0c95ad4ea26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b942e3623e27f187d346eaeaf7722583f1603fce3c6d7b9ead89a26dae54493)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__002845bb122c7d82bdd0b0fd60e6a325fb1a7286fc5f5113000655ebc41b3106)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIncludeServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIncludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIncludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIncludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8a1ce6ebc64950d920021ac004b72da8884425f65ea961dfe55eec331835b5e)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__366c3eb3e14f4e639ac1420845cc7f8e1b9508108c8c50b0f58a7e0c7425e229)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefault",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefault:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefault(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__42dd192ed661bc15af3d4085e1094cd0d253f1294dcbad1ed2f5f4df440e9858)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe4f4fd479a8434a8ace59d0891bdf64838e235ebd2201e951b88df9625ca1a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__14cf85fbdb5f461bdeb5763293ddcc8eea8d9a1f9637c0e46a1f8d219848a0c8)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e68a3d79833f5b62c9f04e8659babcb3719762c41e4503e9ab4df340070f2a5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__955941ef2d03eae36b1a782464a0df92ef3471956236b09d5dd85cb3d85999a4)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0521cd63e274fafeb8b791c52ef83b9ece3e764b23986ed2b19055c668f9d91e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b94b32a96293baf8eff78e31882222ea507dfa1bfdd89345ce11b0503808942)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f5bf0348c5998b3802ba05dbfd871753a7b027bbd59ef3b2d3fc36cb52734a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cfb3b36c9d40451c6de6bbd253dec7357a24c40207b8c573781940138857be8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7be22e1f57c5d936c3aab2c7c4cc65a9988578f058da9d5dd1a489855dddbfa3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e459d25358fb9695067bea93a958051ccd16849c2c65e57c09454e19e65980b8)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__101671a37d6401b05c356aaa7b931aecccce20dc2d7c4cc801b1f7f81235cd38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c23f7ecc6953ece221d0c4697e6b2fea76fbd7c368ec17935e03273f1f8c83d)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af40f884d7853afc3a4e399160d2f9b1d3e1c0f090a6a4975dbd4d336faf10b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e4a420dd1f8e3fbd45bccf8d908950514664a84f3e0fb72432213a0794100044)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b988936f50d3fcab9497bca47c7063a2249a5fcdd1125f5baed6fdc689b1a6e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e852d48368c931534f14d67b4feda630b74fabb494f1caf7640d62ff552c9a7)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ba438f807ec60ce30afa59e6dec9c0c8f545f749bb033aee42e9c3b9c548eba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61f561b822490bb59d7de31bcec15231a84f61a08bda8239d8e7e098587d337a)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36182c54862f72f0f78d5897545eef3a16fbe29f9f1a62d90cf7fa021ea95109)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc43c08e5dd02fc570be0416b038f022aa341d1764abdee112002f06de0a7c7a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19a1b12f6fc5adcf78ae69ab7a27d7f923f598850acc8f3f15d976788a204024)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f96a7894a7129235ab7ef5875a8d6601c2722d47f4c49afcbbbf36ad03291b56)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a49043a9eae7f338aa3453c4ed0421fd9c2aaf093358800e0207634b9d34b88c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__82e19d7696e75f78e6fea96194f72df54f7603de4de48381ca4538b7310d9ab8)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f34070a8c030a2886bb614eac9c5348a4a47a04cb6ee5506a978984d44184e9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc91deb55ce424e2c90758bb3532dc395491c20e28f967189bac03059f8b2e0d)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ec7883f568884a8524fd95bfd6d72097c616b0aefeb444d0b41c835c2f1cb33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb2ab1fad6b1df1dfe9447148e7028bec8976997b323db8d93bf721733570161)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__321d09e15a63e7d1d6d11bb470307a044a3a9fe60fe63a6c8337d0541eabd37c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__57b8d72e0bc20f260e33f0e22663e483db82800385493c5669e874e3203dbb7b)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__125534dacf4b45cfe79963e08540c77ccf4e11688d57076e5d97fe5d1b82fd85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__50dc44a58675c67c82d98a9875b5927ebf5a9477044768e1b847d4637cfa40fc)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f35a89a0f522c2d512419cf4b0f25228f266c8bf07e192651a03f0f2a934eaaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ace8a86d5a1650bb1ca7f6499e4c72fe2ad6bb49ea70e1c684ea5dedae77f938)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__307a9d1422c1256666a3df5d1d86c235a1434b8308e149e6dca8ced4f14fdec9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c2abe06633506bb603a2e89778519a2f833b0a1adb72a9158d4845c0370c2f8)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3d21c12fbf0b4f9164773dfbdc5a30542fc0d368ea4f3490f7256810a01ef36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__88eef36bfd18e73c5483d2b7e79922eeb72626ed4e20b75c5e82cb4a96e57a49)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultIsDefaultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e624ae058fd43ac2b13d4fc8dcff3f2839352f2fd6f23be591377f80ffaaf4d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultIsDefaultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1af990b72a7ae59b839106c6215ac6aaa249367b519495010faf98fedf67b361)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf2b9a2a31e8b7fc4f5d895bb5c5ca891b23f4aa8211fb4f15820b60603e4803)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2c71ca93a6637f8e5fa0daff96c506df7334a0ffeb849058fde8e34e7a53261)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e71e7e4d2ca843687e441d34fc8e85810742a561ce8734a29b6fb6c05d01d15c)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3397a7b27ae946a35b00535533b7783a7686ad4b5d07ff6a1390edd69172df29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__340073edd1e38e9c13fb77cce9077c945166a4c34dae0fc27208d2025729fae6)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3801145e918ea4b1b80c8721ddc3b07a9c8dc7d9c2f4ba444dc2eb4e48623b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__00b509c188f6748a9118cdda34385eef959a1ac19c9d0ab1bd31b22bb8107bf6)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c168e435164e4981ff65640f20ffa02f97a1f27965daf8274aea94a00d3ed90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__71f96325c36e6edfd9357722dc3fa6c4097bb224efd17ef771f8a3260d30deff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultIsDefaultSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultIsDefaultSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefault]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefault], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefault],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55a8af77ad23d1eb817e77f4516ab28ad0465084031e8480945e7ca4435cd06a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__30cf5a9685325800b6bf29692cdb863a05da821cb5c75fb6f0c583b0e03e6f38)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b8f87cc775aa60b0160b6c9e7d55adf5a25a2092419d6c28fd0f9efdbc69dc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f4efcf491809107dd76e2934a9f1b8d043b0e154b1246c7a758f499bd675288)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13bfdda849bddaea074b10c7b290eefdd903eb45b9f15e971f675d83343575ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2a2d4f6084937e20f69cf81fe24ded72e72bf8544709d6be528994f79c9adc6b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64bdd5d26e925445ce28cd7d9fec617bf912f919169f791cb19e60ca08056355)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9969bae3ad134492ec5d1033cec27e418b4e3613cdf89e856d0a7ad157163c57)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0edb8b4ae83f1046daca023162694425de156cfff16be2bd88bf849e6da82b1d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1fbadb681ac7de1f6f77dabe64b458da65fa82bd0f665dddf6e61b978c5bfc56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67c9388976e3a4a3e5dcd6e976a1ae87ce8e17ecbac5e629d850dc8a1c4a2cc8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> DataCloudflareZeroTrustAccessGroupsResultExcludeList:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultExcludeList, jsii.get(self, "exclude"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> DataCloudflareZeroTrustAccessGroupsResultIncludeList:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIncludeList, jsii.get(self, "include"))

    @builtins.property
    @jsii.member(jsii_name="isDefault")
    def is_default(self) -> DataCloudflareZeroTrustAccessGroupsResultIsDefaultList:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultIsDefaultList, jsii.get(self, "isDefault"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="require")
    def require(self) -> "DataCloudflareZeroTrustAccessGroupsResultRequireList":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultRequireList", jsii.get(self, "require"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResult]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d62bb1e0ccaa97ae6668281355d371c52515c19e2d6f49b21fb529e631f84b5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequire",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequire:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequire(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__85b7ad2b2ba1bbbebe94eba289829321130268f5377c9caee7ab4f730320b9a4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c082bf9faff38f8c0dcb7c7a9d51ed01c8e88c8ca5321b6a31ff40684aafe90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b90d198c0b7c41fff9be36cbcaff3c52b08169417a514544b18246b52546858)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fc0000629e0c4f19567749f9e0d049bc0ae0ef6b187178185f96bd7df02c7e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3333cd422acbefb4ba5eb46c3299ad43dc2e9b7778fc8aea7838dce65e9bfd54)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eee413fe3f301b4bf1868c6831220cb5579ec9ee087e61e0adcce1dc20ae9e4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__baf6f089853fc8fe7c3c5a7282d5db9d6bfd3c482c5d778f963d8345c2cdbf3d)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f981d1c21711214a3c9759b3273b7d881495291672332bd4e1cbc752c5c9278)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3620a8c20f7df81083783fc5e91a65590523265567386fe74c5160682d025b93)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5497761d3ffbc1a4153a1809a19b656e20ac9cbd67824e7a569a455d15a4ce45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__896eed0c3897f9c0a87786b5ef546aa8d8cb7b95f514213b25fb2e893af693fa)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5b4a9e36797844efbf5f91e9a3dd9eabb4c032101ec292715290974e77efdb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec4a50698691795caf9edb1110531485bf3bafde915dbb269334f0fcdfe20507)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ebf1c0d086a9cadfb6404360a0f756fd1a181f3f499cda6385adc47166ad7d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e38787f46d04bfe1dc50f248726f8486d7e3af4ac488a644699835da1bc9acd)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8869c03ac45d103069c1f211b1600023c4aa39f9f190424ff16b5080d7349a7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__420a76e5169eb3c580c65cda365ec895fc398f7a8e40a9b6f5aa1c8ed5444a4e)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aae830a28d7df334edf52c99efda0a023f392b678c4528af3903d79294d9dd97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultRequireEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6bcf191e1b4c74aa7c47d4c9f6f07d2329df8c5f28c00b326604b3cf02bb9136)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeaf85896056d7151dd87b1e27718f7fc680b9e8e4d5e8e47ae28108ce827fa0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__238df61b4032494304670bc23063b7f0de7621b2262e6d8491c3dcf82e5f8dcc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da8a6b8575838427c0bb289e5fdb0f0c5f90d21289e1c0e35bb2af40e0c7b987)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__000c07a8a6819df3bdc9a1fc0316c69492608317cbab594f2af85be34baab201)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a2b547a2d29d267a3e7ba7395a809deaae73e517f21e104a2d3d5b7a4f45371)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__86b89090e39d49afac57f24c5e395f2c9e3659c0f1b0218fd7c765570ce5ecd6)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9540bae604fcb5fe56444e4e58de77664b53e7b9ebe681617ebba420f73a8ae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fabe21b6a7d4599f1054908414e4e49fa8ad38d199db5d0831d7bf34f0f6724)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__217d9ca3c7e8e8f64623e1546ae4991d29588be7bd9ff259f9a1d03840205851)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__79330a71eae4c94c3ad5c79d6e880648d9a5595f755b5a1b7e5a26ac7681e955)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f94344a39c1f757d489e32a37852342e51d8b8deda6cbbcab923f9b0096a2d42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5c308e46edd5389bf5d5be4f7ff87a747d1b17a2f86965b0de19129bc3c86a2)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bd2bcbde226497245d5970eb362fbb59b15af6c7aa3713fb9bf85f12add4744)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1457e9abf053ad8b47ba72b50c551bbb112416f43078cf8a71bef97cc188060d)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cb453afbdb7456cbc6588afe520b3e8e789cadbf8362af243306e7ee453770d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultRequireIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a4a00a5658972c83513685545a9b625d552a0390adf1ed36b729dcd9c8dcc3cc)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ea3303eeb51e75a06726a8eb49cb1fcf704f494c59dcd1e924a65802eded4fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c7e7141d5cf30f74288918f7efa6db7e9a58c799defb59ebfe91c5c77de0b50)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19f458761e8ea4c8cc84101ef9205fc4c46c1d15863677484a69d78f57829c42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultRequireList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__66934bf0340ed8d3c4d4393efe0f659a3380d7083168277e04d232d58f785c84)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultRequireOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e95a3c62a31b5725b5a93dd708d5a6ceb9a274c91c1c1b27433e433e5159354e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultRequireOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d236001008f80d3bcf940324f928ea4ff3cd858562bd501678e8c0611f0bb84d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__712b14c966e6d230c5a93a51c13c3a6cb0dc05b849fa2b2914accdcf6279b06f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e88e399bd54e32e641d678eae5dc2c624a97514b1e036178e8e8c1007b2af70c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__10bf3f25dbff61b0bd9d70cbfe086e3f90b689ccaae19bf464ecb3dc720cda6f)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5cafbf6996228202f7802b96b5c84ee2e1753bb3e386694ddf70b69112ab234)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a4813dcae7fcd7f3b90ce140b32c00663d6f05b7be87132d7bb0d975f3c8fe3)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9cba089ac15faf171bea1f4739583a66dd8028eda07b5e0dc6474a451c6e056)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e089cc00984c2cc9cccb25386a8f0582a96d2e057f645c2065915d5dff4a913b)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0d69ce0ae917a48fc6bea67aff3f6c4d2a60b59761ecc373428b823c24b5b24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupsResultRequireOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__20aa96d43d08b57b377105c6913521a634ff9debcd4412bc566442cb54e14251)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> DataCloudflareZeroTrustAccessGroupsResultRequireGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessGroupsResultRequireIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupsResultRequireOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupsResultRequireOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultRequireSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultRequireSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupsResultRequireServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupsResultRequireServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequire]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequire], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequire],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__267aeffac6725479370263775d52f5fb8c7c09929364e256e1ec486bf4329be7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3a17768238ea0a301692900e5cc8a5a71bfb41330427d77357e9fb02d01856f)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c21a1dc3928568a16a86e96ce0496a7af1c9a1532519a201829374606693b8f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupsResultRequireServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupsResultRequireServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupsResultRequireServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroups.DataCloudflareZeroTrustAccessGroupsResultRequireServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__375d4eca7b81e3c93dcb119e142ea628abc557f9c2654cccf588b2d49d20bf07)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d29236185d7945860f6fe2193e2ac6cb4a08e23b80dd1c0de413450b7fff3732)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustAccessGroups",
    "DataCloudflareZeroTrustAccessGroupsConfig",
    "DataCloudflareZeroTrustAccessGroupsResult",
    "DataCloudflareZeroTrustAccessGroupsResultExclude",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContext",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethod",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAd",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeCertificate",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeCertificateOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeCommonName",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePosture",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeEmail",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomain",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStruct",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeEmailOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeEveryone",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluation",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeGeo",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeGeoOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganization",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeGroup",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeGroupOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeGsuite",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeIp",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStruct",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeIpOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppToken",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeList",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethod",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeOidc",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeOidcOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeOkta",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeOktaOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeSaml",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeSamlOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeServiceToken",
    "DataCloudflareZeroTrustAccessGroupsResultExcludeServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultInclude",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContext",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethod",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAd",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeCertificate",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeCertificateOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeCommonName",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePosture",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeEmail",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomain",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStruct",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeEmailOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeEveryone",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluation",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeGeo",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeGeoOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganization",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeGroup",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeGroupOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeGsuite",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeIp",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStruct",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeIpOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppToken",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeList",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethod",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeOidc",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeOidcOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeOkta",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeOktaOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeSaml",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeSamlOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeServiceToken",
    "DataCloudflareZeroTrustAccessGroupsResultIncludeServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefault",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContext",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethod",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAd",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificate",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificateOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonName",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePosture",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmail",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomain",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStruct",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryone",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluation",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeo",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeoOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganization",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroup",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroupOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuite",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultIp",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStruct",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppToken",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultList",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethod",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidc",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidcOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultOkta",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultOktaOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultSaml",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultSamlOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceToken",
    "DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultList",
    "DataCloudflareZeroTrustAccessGroupsResultOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequire",
    "DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireAuthContext",
    "DataCloudflareZeroTrustAccessGroupsResultRequireAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethod",
    "DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireAzureAd",
    "DataCloudflareZeroTrustAccessGroupsResultRequireAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireCertificate",
    "DataCloudflareZeroTrustAccessGroupsResultRequireCertificateOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireCommonName",
    "DataCloudflareZeroTrustAccessGroupsResultRequireCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireDevicePosture",
    "DataCloudflareZeroTrustAccessGroupsResultRequireDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireEmail",
    "DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomain",
    "DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStruct",
    "DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireEmailOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireEveryone",
    "DataCloudflareZeroTrustAccessGroupsResultRequireEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluation",
    "DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireGeo",
    "DataCloudflareZeroTrustAccessGroupsResultRequireGeoOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganization",
    "DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireGroup",
    "DataCloudflareZeroTrustAccessGroupsResultRequireGroupOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireGsuite",
    "DataCloudflareZeroTrustAccessGroupsResultRequireGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireIp",
    "DataCloudflareZeroTrustAccessGroupsResultRequireIpListStruct",
    "DataCloudflareZeroTrustAccessGroupsResultRequireIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireIpOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppToken",
    "DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireList",
    "DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethod",
    "DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireOidc",
    "DataCloudflareZeroTrustAccessGroupsResultRequireOidcOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireOkta",
    "DataCloudflareZeroTrustAccessGroupsResultRequireOktaOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireSaml",
    "DataCloudflareZeroTrustAccessGroupsResultRequireSamlOutputReference",
    "DataCloudflareZeroTrustAccessGroupsResultRequireServiceToken",
    "DataCloudflareZeroTrustAccessGroupsResultRequireServiceTokenOutputReference",
]

publication.publish()

def _typecheckingstub__b6ac620620861a91a14a53e8ffa4c59a39f45eb7197f290c4a90e7a17d2030c0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    max_items: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    search: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__3a890ff65e15a9d737d1cf8f15c4e9c746e4447e31e3a144afdf9a9d375c6050(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed522c04b10002210917b665626f7aea6153e52f9c6e5f178465f6f3cb65a5ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4e1514b9c9f6ca2f04d974e258b89e15f1cd39c294045ef57ae1dff18c28f0c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7735fc9edc1235ff9dcb8d6b5bfdace46e2666e3278ca868e344f95ac527fd37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b2151d7eab5c7cec3aec4ca272b3964c12c6b81090dd83d38a1e800be7c751e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b635ea7b10d9648e90ef4464da61bb9669b0a73c0de8be5cdbd4c5da9566fd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__749892a8a43bc92fb491ec18ba8075504cc35dc069d1cb83a9837019bbacfb3d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: typing.Optional[builtins.str] = None,
    max_items: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    search: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ddfd593e34700191a509fa99a31cf6c92b2cf90aa567393ed26a94c4e046135(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__092e70cf43af5e8b75939743114b30c60afc4e1567fe21083e26e566f55e8683(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89d1c4bf88ef8a4b9d9d29966dc56566c485a166e2af00e5e4d5bf0f228ab14c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc09846fa4a4ac029a79b6e4405de60f5557078dc6ddcc699910f966744504ce(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74a24059182d6ce88aa1140fa591ac91f09f780be6e130a999e2da30b17e39e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95422ee13107717b349612a5b11fcd8a77df81f08ea8f3a829d58a3672e7de9f(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df8d4dfca366180fb92d74c8eb68b3f0ab1751e6fac403a8d36487c9ca099382(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2299e7bf71934fb4bfef8866c0d0d0d7559e83e3f351ea30d08aad89a90db7cf(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04cdd650a80321b5e26349ffe2c94f04e1a4981ed789d2a1aae91bb7a071ef64(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6456261f8fb8ea8a5df66e8e8b29bcc8f71864a97db7d5d6cd79daf3db261d8c(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc95d2c15715417ef1944d7ea1bae0700efb8548cc9ff3eae7744c33045dceca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4d1b6117cba437296cd3ad2593f168a5a8491eebd0a4285fc81120828bb5b41(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd499992dc3295d0aeb0a68c6de4b9d4c92b27d0a8db5ffbe1abbae37693ee9a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a04334328a8051a38248af85742c220ae6b1c472450b3eea9808aff5b195c7b0(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__400157c781e598f695bf3fabb81c84264cd400e8f34d3cc3685f73a7cdff26ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe07a4fa1d0d0d5ecc28bb503db7602be26ab6c8420c4c4dc0b32a621dcf4082(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c623a8e0a306d7f034528270eca6b0422ef2f8c08c1c791bdb1b85a1f1d26a80(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fa5c2e6252e995280330f67f44e6a774b09e018c141b5208e091319cc517bad(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02d8b778f7f19e59e097be82b8f1859e39ff1d4ec334a67deb7196c7f79f3782(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b029a6216b805c708c4325950f1ba82aeef012f43ead80366a9530ec0d65b6b(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e76725d6ec0e80e5c0c9e6bbbb5b27283bb93390aaeb6ad187f58e0fbeca7de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44eef87fa9e1608bb075604566ac607a1a39a1c9182c651cc07b302490f8a0b9(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77672746f310de00bc4a2a3d3ac588f044ba7dc9d29e651144553256459bfebe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e2bb1c1f0e7a31bea09e86f6d9a57988fddd78d9e381bf1519c331e596237af(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2615dff3162ed51bcc2d1452e1a2a812d6c192b37fc4e2cf1b95f8cc1db26b79(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f020ece4e9c22fc2c113980d36306f1ad453aea45742938389e11dc08ec4a4b2(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b3688a028a7c1fb8112f730129d6cf588abd6da6baf0c9f7b6984fd63825496(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__802cc09ce7008f1bade70f767653a6fc792e563c55112b9c36e2e8510fb3a766(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4564b46d9becd5e55c2d2d715e889d7f398cc2b29be7faa70adbab5d2c8b942a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b962d01ea0cfa920613256b16dcb893d4d836070ec1ae3a503a66ec1c2a87a8c(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f253065ca7f9578700a37afddb9661bc7f28e6527e49e3a17de9705e4cf802f5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71e7fcde06c0bcffc05cf543933df5847cedceb30c65b0a5f7a4a1d1ffd37ff4(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63bbe0cedbd4174222c8642f491a73e2c5ebf68f76b833550fea942d9e3cfebf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae70a25f87adee67884f8c55285c60b70bdf621c043293d4e237b51a08ce8090(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16cf76a5c0b027598d49267f929de2562e0c4924063cffeba2db17be0efd8edf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab6f3bc74c7751bb19419c88a72f5b2e59b380dc1ce8dd64072a1ffff1d7610b(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdc933471843ee7f133d4cebc61239d89110fe9cd2b07fde132f3621548fa961(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c54c0ea97d1bc5082eae157be617c9e094f379f0431f71c9f014ddb8d65ff1dc(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1389b0aba9b21203329b9aa76cd92744f2e88ea0dc7e525459dc2923009f058b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ffe6e1bbdf49d73e48b9631a118e6ba4cc1044406baea07e51d52368d283f68(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__772416980e04a4251f8c8ae10f46c0c3fb40033a51860069eb07d4296cdc715e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d6ed6fd92636c09284406f7df1bd390e43a49a83e7fd45b5f4d5b477feab683(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e281e1bd9d117f7bd86f4f0be16536ce6d33d51dc976601ce57932e3e61d0d6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55d59e7ee0d5d64e110338fe073eaa0d6ea1d4b5d81a9cc7427cc1a6755f3d29(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c3aa7d38bac0cda6dfc2a1f906513e4968ddbbe8ebf8e6a0b10b1989aa0ea1b(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e09c6b0369b087b732da1e2933295d06b05021c5e058031d8affe8389252de81(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3c2e39be82fdb8ef01ab25df430856302fdbdb108d253808e291655c0dba7a(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81e0ce500d255ab289239ee2ce85d78a36c5c042397d79b4b6e43b67abdf95bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb604878f3bbb22f44a539baf88d9cdff90185bb79879fab5fc8f996619dc7ee(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32af06ec51e1b1938e7148d329dce41d7f78bd196bb980db4e5e4273831e13d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54b7a5381fba5e17dd1c4ff10f4360d4d73570e4f5b24ae96b6773428e20e8ea(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExclude],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60daef9af03e480267833bdb4010fa305fe1c757a5958b05ea565039c46aef58(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f7db55e5d9f66391350499e50c9c63078e50927e1ead4a217365b542f95ba9f(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1eadea4f8cd3766212f2173f5ddbf8ecea1a6b3af486955681123c4cec15fd9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ac205af8fa9eed49dd259c2767dba7986beb486b16a8629a7e452df222888ee(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultExcludeServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0264a85173bd193114819871c19aae63972d41e3b950bb7181cd100147de32a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a19880420b0cf5eabdc692db3f144aee900008cd4164c9dc3623ef1333326ae2(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e57ece672cc6269dfe36090048ba626613ace6fc4f974e72f0b40fb6a4f8ab3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__593f38ce303b0838bb266930563fdf97097fdb0c0b30f09f82d1a2dc267c9611(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__732bfa37f7e8fd0106647083b8789b6712e1597a8835b5992973b42069d997b9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__118fd2231206245b2f68174771b9178e63ab1e2145c0b908356dc0df58de16c5(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38026d652bfe2616fcdb89e090d8abf3adc47ec4d91b9bc1f9fd81ddb95a77dd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d71b5051e66ef4d7081663340a6e8326a7c259ab4eb7a6cfdb8269811e77b55e(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd29bc9feb2f8ee170592f240607330802ad786f92aaacf5ba506865d5f0d2af(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24ba4f9138207677098ee98f648bc0a938320060add586afdb58c11418b159c9(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac7984e2a7e3234c8111419ba2ff76698bec33891a47aa4a1f66406883e08404(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df08fe7233fd7d4224d6e751eb93a6b8bcf07152e73607b855cec518917049cc(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d069b8bd7c00357efae76d05665b8965395d38d6e22b4c0c5030880150684244(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71ea65c6cb99405fab73624d6ca300ca0e7fd5854e588ce875365096fbf8a1dd(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__779d65f3544e99aeed668398740c778d697743478155f5cade03b5aec848372e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__211eb7f84a777f798a8a254dde5bbf6da55519e703c1ec305a20936736962bfe(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c522919593b75e184c2dc4c0ce17a26da9f6b7c3a963d7adfa200c8da79f13e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faed0c2b86eb8748b1144b61d4c4ee5b2aaa1dfb819df29ee92436db1401749f(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7860c419c0c6ca2b870247520ab964de8023bcd3830403a57b5190e325baf476(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc2617d2149cb55662f7937f9ee430bdf57adb78337c8da2f976d97d9762b664(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f63c7d5a8580d89dd35d4a4c0721c1d976394b4e7b27453acd44b20b3e30173b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f86a9b3b0870604872e4cafa93e603c59e513ee33a8ee116c71d19928e78167(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94c115efc8b18c3f206a66c103000134bf16f602c52a4e828b66f40dcf5466d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__605aa74f5656a995f5c0e0263d9e43dcf27afeff6bbb6586187a730edada2d6f(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1fac2a379786fe97a4de67362e9aaab10960b5e573f6e8fc5c8b032937fc91e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddbd4f2fba54d5d57e2e8da5171718cf628d53091fb80dae1c946fb2232ca2f3(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe8b31160d7eaa42cd0e762d30ed49a8552b9a752f0f802cf8717420c976c084(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b89862c3b94d261b109c5fe0d026eb34c9efcb85e5a8e862fa62c28eeada191(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__324fb60b4548b853b26e9da3f9b3a48b96f3bd4f44002603d98d5c1806ca04d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e7c1d19eeee3f854ec50df414477035a8823b92b81bccbc5a35647372ef8416(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0721923f3954bf2f631754adc04f70bb02bc9fab10dc4ef35d129083b3d63857(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e91bab8dcb7162991f9d0a14928f7ff175e43b09492baba48702d535ccaee52(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f12c5e497cd467e845757947ebc2d233d7f54abf1d4c4c900916e1983fa80cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2cbb74054dc55ea2bd513e9c3afe4f671cb60c401dc3731a00c861bff432071(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__079c1c35c04aeddc0713a42ff08b969cb407b9bf75fae5a36e6c6198664ee34a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec765db537de47938608ea13f1427d0293fac20e48ae9b91f6faf20a33419b46(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d1bfd9497c4c80dc547689c4c369bdf6456e302991a6dc096c0ae2ebcf8e23b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41d0d00d32369f3d8817900134c9f9ed9e938ae47078c6284d4d91aa42b5e9b2(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ad9dd4a94ca274c5f0b4139abdd682cd4810ae78d6f91825c5f497699b703a0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd02ac985353cf361b190f36fcb913fae91f497244e4a1ad1eabaa62b8ae6dcb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78b962bc41de644282cc0c2d1c207b64e302d6ecc82ede91283c11cc214cfedd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f32c27604c77a4d88d62d4e30a32012308eac10435b21a61db5ea3df40fcf53(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78f0fe9c567a6c458156f66c1e1a63241863bb7fce65b8f2fd396168cf3973c3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62d012efd5acc9ce701e080e750086cc1a62e2659071332dcf01abc7e1d5b404(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e620b8c2475b327923bc827de19d279c29f61a7392f5e3cf3d83cf2914f903ba(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c40be0e14f002b79471a75c27810eaf23e04389c0baf4c389501fd5f3aaaf8aa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c16c62fd7d5ed6bb91b81e9aa64197d8c34efb5f5e361c913109f3d2cf2bd374(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1236b1ab2cf9d8ff0244c9c6de4b8788df8da6be25b5c79d6bd6fbb586f83a33(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b0630407b5a16222d67cc2ad007a9578610a18eb8ea3ba1ffe5e105c90eb894(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__444a77c11797dd3645a3161e899de331e33d245ed7c1b163f914e980c316a1f4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f808781e77f99a740565511e55abd716d53d74513314b19e801ef0c95ad4ea26(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultInclude],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b942e3623e27f187d346eaeaf7722583f1603fce3c6d7b9ead89a26dae54493(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__002845bb122c7d82bdd0b0fd60e6a325fb1a7286fc5f5113000655ebc41b3106(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a1ce6ebc64950d920021ac004b72da8884425f65ea961dfe55eec331835b5e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__366c3eb3e14f4e639ac1420845cc7f8e1b9508108c8c50b0f58a7e0c7425e229(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIncludeServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42dd192ed661bc15af3d4085e1094cd0d253f1294dcbad1ed2f5f4df440e9858(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe4f4fd479a8434a8ace59d0891bdf64838e235ebd2201e951b88df9625ca1a2(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14cf85fbdb5f461bdeb5763293ddcc8eea8d9a1f9637c0e46a1f8d219848a0c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e68a3d79833f5b62c9f04e8659babcb3719762c41e4503e9ab4df340070f2a5d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__955941ef2d03eae36b1a782464a0df92ef3471956236b09d5dd85cb3d85999a4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0521cd63e274fafeb8b791c52ef83b9ece3e764b23986ed2b19055c668f9d91e(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b94b32a96293baf8eff78e31882222ea507dfa1bfdd89345ce11b0503808942(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f5bf0348c5998b3802ba05dbfd871753a7b027bbd59ef3b2d3fc36cb52734a1(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cfb3b36c9d40451c6de6bbd253dec7357a24c40207b8c573781940138857be8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7be22e1f57c5d936c3aab2c7c4cc65a9988578f058da9d5dd1a489855dddbfa3(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e459d25358fb9695067bea93a958051ccd16849c2c65e57c09454e19e65980b8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__101671a37d6401b05c356aaa7b931aecccce20dc2d7c4cc801b1f7f81235cd38(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c23f7ecc6953ece221d0c4697e6b2fea76fbd7c368ec17935e03273f1f8c83d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af40f884d7853afc3a4e399160d2f9b1d3e1c0f090a6a4975dbd4d336faf10b7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4a420dd1f8e3fbd45bccf8d908950514664a84f3e0fb72432213a0794100044(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b988936f50d3fcab9497bca47c7063a2249a5fcdd1125f5baed6fdc689b1a6e9(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e852d48368c931534f14d67b4feda630b74fabb494f1caf7640d62ff552c9a7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ba438f807ec60ce30afa59e6dec9c0c8f545f749bb033aee42e9c3b9c548eba(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61f561b822490bb59d7de31bcec15231a84f61a08bda8239d8e7e098587d337a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36182c54862f72f0f78d5897545eef3a16fbe29f9f1a62d90cf7fa021ea95109(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc43c08e5dd02fc570be0416b038f022aa341d1764abdee112002f06de0a7c7a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19a1b12f6fc5adcf78ae69ab7a27d7f923f598850acc8f3f15d976788a204024(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f96a7894a7129235ab7ef5875a8d6601c2722d47f4c49afcbbbf36ad03291b56(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a49043a9eae7f338aa3453c4ed0421fd9c2aaf093358800e0207634b9d34b88c(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82e19d7696e75f78e6fea96194f72df54f7603de4de48381ca4538b7310d9ab8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f34070a8c030a2886bb614eac9c5348a4a47a04cb6ee5506a978984d44184e9d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc91deb55ce424e2c90758bb3532dc395491c20e28f967189bac03059f8b2e0d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ec7883f568884a8524fd95bfd6d72097c616b0aefeb444d0b41c835c2f1cb33(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb2ab1fad6b1df1dfe9447148e7028bec8976997b323db8d93bf721733570161(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__321d09e15a63e7d1d6d11bb470307a044a3a9fe60fe63a6c8337d0541eabd37c(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57b8d72e0bc20f260e33f0e22663e483db82800385493c5669e874e3203dbb7b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__125534dacf4b45cfe79963e08540c77ccf4e11688d57076e5d97fe5d1b82fd85(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50dc44a58675c67c82d98a9875b5927ebf5a9477044768e1b847d4637cfa40fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f35a89a0f522c2d512419cf4b0f25228f266c8bf07e192651a03f0f2a934eaaf(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ace8a86d5a1650bb1ca7f6499e4c72fe2ad6bb49ea70e1c684ea5dedae77f938(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__307a9d1422c1256666a3df5d1d86c235a1434b8308e149e6dca8ced4f14fdec9(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c2abe06633506bb603a2e89778519a2f833b0a1adb72a9158d4845c0370c2f8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3d21c12fbf0b4f9164773dfbdc5a30542fc0d368ea4f3490f7256810a01ef36(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88eef36bfd18e73c5483d2b7e79922eeb72626ed4e20b75c5e82cb4a96e57a49(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e624ae058fd43ac2b13d4fc8dcff3f2839352f2fd6f23be591377f80ffaaf4d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af990b72a7ae59b839106c6215ac6aaa249367b519495010faf98fedf67b361(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2b9a2a31e8b7fc4f5d895bb5c5ca891b23f4aa8211fb4f15820b60603e4803(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c71ca93a6637f8e5fa0daff96c506df7334a0ffeb849058fde8e34e7a53261(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e71e7e4d2ca843687e441d34fc8e85810742a561ce8734a29b6fb6c05d01d15c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3397a7b27ae946a35b00535533b7783a7686ad4b5d07ff6a1390edd69172df29(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__340073edd1e38e9c13fb77cce9077c945166a4c34dae0fc27208d2025729fae6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3801145e918ea4b1b80c8721ddc3b07a9c8dc7d9c2f4ba444dc2eb4e48623b5(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00b509c188f6748a9118cdda34385eef959a1ac19c9d0ab1bd31b22bb8107bf6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c168e435164e4981ff65640f20ffa02f97a1f27965daf8274aea94a00d3ed90(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71f96325c36e6edfd9357722dc3fa6c4097bb224efd17ef771f8a3260d30deff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55a8af77ad23d1eb817e77f4516ab28ad0465084031e8480945e7ca4435cd06a(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefault],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30cf5a9685325800b6bf29692cdb863a05da821cb5c75fb6f0c583b0e03e6f38(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b8f87cc775aa60b0160b6c9e7d55adf5a25a2092419d6c28fd0f9efdbc69dc8(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f4efcf491809107dd76e2934a9f1b8d043b0e154b1246c7a758f499bd675288(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13bfdda849bddaea074b10c7b290eefdd903eb45b9f15e971f675d83343575ff(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultIsDefaultServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a2d4f6084937e20f69cf81fe24ded72e72bf8544709d6be528994f79c9adc6b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64bdd5d26e925445ce28cd7d9fec617bf912f919169f791cb19e60ca08056355(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9969bae3ad134492ec5d1033cec27e418b4e3613cdf89e856d0a7ad157163c57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0edb8b4ae83f1046daca023162694425de156cfff16be2bd88bf849e6da82b1d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fbadb681ac7de1f6f77dabe64b458da65fa82bd0f665dddf6e61b978c5bfc56(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67c9388976e3a4a3e5dcd6e976a1ae87ce8e17ecbac5e629d850dc8a1c4a2cc8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d62bb1e0ccaa97ae6668281355d371c52515c19e2d6f49b21fb529e631f84b5d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85b7ad2b2ba1bbbebe94eba289829321130268f5377c9caee7ab4f730320b9a4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c082bf9faff38f8c0dcb7c7a9d51ed01c8e88c8ca5321b6a31ff40684aafe90(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b90d198c0b7c41fff9be36cbcaff3c52b08169417a514544b18246b52546858(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fc0000629e0c4f19567749f9e0d049bc0ae0ef6b187178185f96bd7df02c7e1(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3333cd422acbefb4ba5eb46c3299ad43dc2e9b7778fc8aea7838dce65e9bfd54(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eee413fe3f301b4bf1868c6831220cb5579ec9ee087e61e0adcce1dc20ae9e4c(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baf6f089853fc8fe7c3c5a7282d5db9d6bfd3c482c5d778f963d8345c2cdbf3d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f981d1c21711214a3c9759b3273b7d881495291672332bd4e1cbc752c5c9278(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3620a8c20f7df81083783fc5e91a65590523265567386fe74c5160682d025b93(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5497761d3ffbc1a4153a1809a19b656e20ac9cbd67824e7a569a455d15a4ce45(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__896eed0c3897f9c0a87786b5ef546aa8d8cb7b95f514213b25fb2e893af693fa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5b4a9e36797844efbf5f91e9a3dd9eabb4c032101ec292715290974e77efdb6(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec4a50698691795caf9edb1110531485bf3bafde915dbb269334f0fcdfe20507(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ebf1c0d086a9cadfb6404360a0f756fd1a181f3f499cda6385adc47166ad7d0(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e38787f46d04bfe1dc50f248726f8486d7e3af4ac488a644699835da1bc9acd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8869c03ac45d103069c1f211b1600023c4aa39f9f190424ff16b5080d7349a7a(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__420a76e5169eb3c580c65cda365ec895fc398f7a8e40a9b6f5aa1c8ed5444a4e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aae830a28d7df334edf52c99efda0a023f392b678c4528af3903d79294d9dd97(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bcf191e1b4c74aa7c47d4c9f6f07d2329df8c5f28c00b326604b3cf02bb9136(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeaf85896056d7151dd87b1e27718f7fc680b9e8e4d5e8e47ae28108ce827fa0(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__238df61b4032494304670bc23063b7f0de7621b2262e6d8491c3dcf82e5f8dcc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da8a6b8575838427c0bb289e5fdb0f0c5f90d21289e1c0e35bb2af40e0c7b987(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__000c07a8a6819df3bdc9a1fc0316c69492608317cbab594f2af85be34baab201(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a2b547a2d29d267a3e7ba7395a809deaae73e517f21e104a2d3d5b7a4f45371(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86b89090e39d49afac57f24c5e395f2c9e3659c0f1b0218fd7c765570ce5ecd6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9540bae604fcb5fe56444e4e58de77664b53e7b9ebe681617ebba420f73a8ae7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fabe21b6a7d4599f1054908414e4e49fa8ad38d199db5d0831d7bf34f0f6724(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__217d9ca3c7e8e8f64623e1546ae4991d29588be7bd9ff259f9a1d03840205851(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79330a71eae4c94c3ad5c79d6e880648d9a5595f755b5a1b7e5a26ac7681e955(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f94344a39c1f757d489e32a37852342e51d8b8deda6cbbcab923f9b0096a2d42(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5c308e46edd5389bf5d5be4f7ff87a747d1b17a2f86965b0de19129bc3c86a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bd2bcbde226497245d5970eb362fbb59b15af6c7aa3713fb9bf85f12add4744(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1457e9abf053ad8b47ba72b50c551bbb112416f43078cf8a71bef97cc188060d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cb453afbdb7456cbc6588afe520b3e8e789cadbf8362af243306e7ee453770d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4a00a5658972c83513685545a9b625d552a0390adf1ed36b729dcd9c8dcc3cc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ea3303eeb51e75a06726a8eb49cb1fcf704f494c59dcd1e924a65802eded4fd(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c7e7141d5cf30f74288918f7efa6db7e9a58c799defb59ebfe91c5c77de0b50(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19f458761e8ea4c8cc84101ef9205fc4c46c1d15863677484a69d78f57829c42(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66934bf0340ed8d3c4d4393efe0f659a3380d7083168277e04d232d58f785c84(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e95a3c62a31b5725b5a93dd708d5a6ceb9a274c91c1c1b27433e433e5159354e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d236001008f80d3bcf940324f928ea4ff3cd858562bd501678e8c0611f0bb84d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__712b14c966e6d230c5a93a51c13c3a6cb0dc05b849fa2b2914accdcf6279b06f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e88e399bd54e32e641d678eae5dc2c624a97514b1e036178e8e8c1007b2af70c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10bf3f25dbff61b0bd9d70cbfe086e3f90b689ccaae19bf464ecb3dc720cda6f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5cafbf6996228202f7802b96b5c84ee2e1753bb3e386694ddf70b69112ab234(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a4813dcae7fcd7f3b90ce140b32c00663d6f05b7be87132d7bb0d975f3c8fe3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9cba089ac15faf171bea1f4739583a66dd8028eda07b5e0dc6474a451c6e056(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e089cc00984c2cc9cccb25386a8f0582a96d2e057f645c2065915d5dff4a913b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0d69ce0ae917a48fc6bea67aff3f6c4d2a60b59761ecc373428b823c24b5b24(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20aa96d43d08b57b377105c6913521a634ff9debcd4412bc566442cb54e14251(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__267aeffac6725479370263775d52f5fb8c7c09929364e256e1ec486bf4329be7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequire],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3a17768238ea0a301692900e5cc8a5a71bfb41330427d77357e9fb02d01856f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c21a1dc3928568a16a86e96ce0496a7af1c9a1532519a201829374606693b8f5(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__375d4eca7b81e3c93dcb119e142ea628abc557f9c2654cccf588b2d49d20bf07(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d29236185d7945860f6fe2193e2ac6cb4a08e23b80dd1c0de413450b7fff3732(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupsResultRequireServiceToken],
) -> None:
    """Type checking stubs"""
    pass
