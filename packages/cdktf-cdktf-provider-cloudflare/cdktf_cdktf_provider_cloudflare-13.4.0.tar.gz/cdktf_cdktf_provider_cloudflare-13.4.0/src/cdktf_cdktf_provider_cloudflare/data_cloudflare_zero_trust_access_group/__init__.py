r'''
# `data_cloudflare_zero_trust_access_group`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_access_group`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group).
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


class DataCloudflareZeroTrustAccessGroup(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroup",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group cloudflare_zero_trust_access_group}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        filter: typing.Optional[typing.Union["DataCloudflareZeroTrustAccessGroupFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        group_id: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group cloudflare_zero_trust_access_group} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#account_id DataCloudflareZeroTrustAccessGroup#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#filter DataCloudflareZeroTrustAccessGroup#filter}.
        :param group_id: UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#group_id DataCloudflareZeroTrustAccessGroup#group_id}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#zone_id DataCloudflareZeroTrustAccessGroup#zone_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc51ed4c1304a7e7e40ce32dd7595dc7840e74481a2f6c78037921ab2a6b8bd0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustAccessGroupConfig(
            account_id=account_id,
            filter=filter,
            group_id=group_id,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustAccessGroup resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustAccessGroup to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustAccessGroup that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustAccessGroup to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf042d790b279ab44db69a01815f7b25db1cbe0e866b4a31d73baa4176381a22)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        search: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#name DataCloudflareZeroTrustAccessGroup#name}
        :param search: Search for groups by other listed query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#search DataCloudflareZeroTrustAccessGroup#search}
        '''
        value = DataCloudflareZeroTrustAccessGroupFilter(name=name, search=search)

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetGroupId")
    def reset_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupId", []))

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
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> "DataCloudflareZeroTrustAccessGroupExcludeList":
        return typing.cast("DataCloudflareZeroTrustAccessGroupExcludeList", jsii.get(self, "exclude"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataCloudflareZeroTrustAccessGroupFilterOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> "DataCloudflareZeroTrustAccessGroupIncludeList":
        return typing.cast("DataCloudflareZeroTrustAccessGroupIncludeList", jsii.get(self, "include"))

    @builtins.property
    @jsii.member(jsii_name="isDefault")
    def is_default(self) -> "DataCloudflareZeroTrustAccessGroupIsDefaultList":
        return typing.cast("DataCloudflareZeroTrustAccessGroupIsDefaultList", jsii.get(self, "isDefault"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="require")
    def require(self) -> "DataCloudflareZeroTrustAccessGroupRequireList":
        return typing.cast("DataCloudflareZeroTrustAccessGroupRequireList", jsii.get(self, "require"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareZeroTrustAccessGroupFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareZeroTrustAccessGroupFilter"]], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="groupIdInput")
    def group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupIdInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__21c4d845e18b3ba400f3d3ec47f49b4e6a86560a0bbbf0d67006ae45d609a6a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @group_id.setter
    def group_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b507b0976f2640b6ef871adbf3e9c382df0f89faa8752b5a7a21f9579d29a43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5cfaf1582d304ab4d8c167dd466d6d95e392ba9f2e97b56575389a424b56b1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupConfig",
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
        "group_id": "groupId",
        "zone_id": "zoneId",
    },
)
class DataCloudflareZeroTrustAccessGroupConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        filter: typing.Optional[typing.Union["DataCloudflareZeroTrustAccessGroupFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        group_id: typing.Optional[builtins.str] = None,
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
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#account_id DataCloudflareZeroTrustAccessGroup#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#filter DataCloudflareZeroTrustAccessGroup#filter}.
        :param group_id: UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#group_id DataCloudflareZeroTrustAccessGroup#group_id}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#zone_id DataCloudflareZeroTrustAccessGroup#zone_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = DataCloudflareZeroTrustAccessGroupFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a580d9d2a2b92a92ffb0017a690f61fb7ae2be7b7953e1098aa5eb9564a08b4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument group_id", value=group_id, expected_type=type_hints["group_id"])
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
        if filter is not None:
            self._values["filter"] = filter
        if group_id is not None:
            self._values["group_id"] = group_id
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#account_id DataCloudflareZeroTrustAccessGroup#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filter(self) -> typing.Optional["DataCloudflareZeroTrustAccessGroupFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#filter DataCloudflareZeroTrustAccessGroup#filter}.'''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["DataCloudflareZeroTrustAccessGroupFilter"], result)

    @builtins.property
    def group_id(self) -> typing.Optional[builtins.str]:
        '''UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#group_id DataCloudflareZeroTrustAccessGroup#group_id}
        '''
        result = self._values.get("group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''The Zone ID to use for this endpoint. Mutually exclusive with the Account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#zone_id DataCloudflareZeroTrustAccessGroup#zone_id}
        '''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExclude",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExclude:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__242c6871d0adff988f7523769d55be989a069cd594c1b6daa3838ddab63c2fbd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94733030c590973d4136b4881b676f7a852d2e3f95573f7ba5c821a367131161)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ac9a31c7e7a83774298a9cb1ad4407c85e62307adf296a6f52064a74a6db0d9)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c045e3fb1b67313ae953d55ec386ccbc33ede07ff54c53c1b9ea0fac32efde5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e56834a866bd8031303bbee1b4a61f7f0c1f0febba7b08c25d123eb44a68aed7)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed4d6ae046d34e112052230e1e9473dffba7784d9b8325dd12b8f02ad0f40565)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c427276a5e4aa138c44e5313c23d36e85842e820cb5085d4fe738b75d331678)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae5706a27ae4b3f5211b8f6c88ee069474e105feea49546e59bde0d8a1c91836)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe6a9807ceb649a13e6e571b9eb0821098179c514f8485fa5dc61932194f1424)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b03aa06c729eb9778c0d1607747916e22403aba31400cdde0e0716e43da9cd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5eeacd3c40f65c9f5b7374e7eeb3a8f27441dd318b360daddca2588e8887dbe0)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6a003f2e195c86102eca343b8b7b15e6aea0323c459f451a0450585bc62f8a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bfa0cf67b760c04b14bcd407b519e77e397fa09618e5f38b7c2ce4679bc7495f)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4692ee4b2a779789ed06b7f962d837c7c8020bdad39be100a544a944d1eb7d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7672516fa1cbcdd058b325340ef5d7e3b8b0699d0480b9b252453a6970d17e91)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d78d1ccd55362f0fc3f7d2032175a282236c96499ced7d696048ec4d19bd675)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e32dbcd799c65536f972944026c6887206f131cf7ff342caca560737585c254)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcfeba9fce77a53d5843fa4cf26c6a854987331f5f9205a3d14ab67cadd4bc8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupExcludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1fc32a5a0151456a2c56437405d949be2d0f96359fdc10703a55738c3a6d6712)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43b6f383e974455bf135b006d2a762f3638530430105001e69bee879da094053)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6fd33885120ad86fdda7e801cbf4c7178d52a18abfb9046581fb8bb057f80f29)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7dd72f31f314cdcfc5ff6e45dbba805f8af3aa87724d9ef0ed18cc93bdb735e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ece0ac8df6c10286c136b421c6baae9f024f70d2fcfd2b85e5233905650f63d)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54380a0eeb02cdd3ace7763ff02d5d31f46017f918b0c47f98257d5af17ba533)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__14bff72248f9cc2af0011c3e8d051802350470fb33ab17a7f201d754b1e643eb)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1dc1e87115d93c963221b9d703106e3dacd31663fbd13a4c26802d726de358e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c7da0880bc2e025e1f0123b8997b4eefd13f6459a27d94ffc79ad6da14c99b9)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b3caa8422e1f9501afcee80200bd5e6edfc98af336c6fbd137e2499d45958f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1fd86bdb322c90f152bfefec85a9e4b9131b8d81b20c15c122f728ae5847fdfc)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4ae30b0c248be0fa817375f3930d603dae9af8a06ce3525910a4971ef624364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2214e7f77796676d7705d655a15cc10e75c3f258a8e97181acdc2426fda85eef)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c199594b6372ef7fc168305f3d4f40f7eb2ed7360c065a3002060993ede9d3c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8faccec9dd9590e8e431d5e25031ee2e34a057eb47ec2bae761d8f5997011764)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d5fec7f9939b1b4f0362954a05a9743dc99a9611bafe26c19f79b778de31ea2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupExcludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8335ef8eb52c899829d8b108c2764d331730529e48eea0b79bfc335875e1fbf3)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0fca63c4987d13e9ee45c5cf0c2d094404f81a73dfc96647893c4dbf9adacaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca36f36fdf9d0cb95fecfa3f0863c204e67ef133e0ef5df2d1530f05e2c9a3a9)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fed2b78029fe46981b40d8a11baaa6206d10c45283741c7df24af36cfe1315e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupExcludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__24a88db79342a3192e504a4c373284432eb4d3a5c9165aa7b1ad389ac731cbca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessGroupExcludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08a4d639eb0d4833ebe7e15e272049a9a5e4dc567d5554b588dc9ca6fad23510)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessGroupExcludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__106706fdba458939017a733c5b71dd90af1b7e504fbfb04c4127b365e28b3b17)
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
            type_hints = typing.get_type_hints(_typecheckingstub__88a71478412352cd75609bf878efd0cc6164c99eb69754423de8f7bce075de46)
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
            type_hints = typing.get_type_hints(_typecheckingstub__890f5faf314a43a26bdbd7aa2e286bf7b0d170b63ad1d9a6fafa7ea9288f84d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__955277fb4e527490d18f6248b60558f357e2f00b0f078f639626b4a651ec7d11)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__743d0a0567c0884d3b3b7f66e51fca3bd7a61b2b16539ebff8e735e44802ec77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__34a8be4c0d3c509a93cc46fa33b579ae8d99cf7272e038f538272a08cd086812)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9b59d840dc8cd54f582864c9d75f7ac7e369003d31eed2b667dd07f5f769b74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6cbf8d00d36c22e0b2a51da7460961dd14b0428a8c308c529db688f14d10ab6)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6105da068966f27b52f49811d284dadb8670a87348e234dd5309d90e10aec9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupExcludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__10cd2e21f00a477d954edb3d49d60e73b955e843ee0cacaf9ca2456671712131)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> DataCloudflareZeroTrustAccessGroupExcludeEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> DataCloudflareZeroTrustAccessGroupExcludeGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> DataCloudflareZeroTrustAccessGroupExcludeGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(self) -> DataCloudflareZeroTrustAccessGroupExcludeGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessGroupExcludeIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupExcludeLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> DataCloudflareZeroTrustAccessGroupExcludeOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> DataCloudflareZeroTrustAccessGroupExcludeOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupExcludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "DataCloudflareZeroTrustAccessGroupExcludeSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupExcludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupExcludeServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupExcludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExclude]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExclude], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExclude],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b064e2171d3c821103f00f46d136c63a3fb021bf7ceca1f31e568f420f692d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a65ecc0ef9ec4bec371d8ce7eaaa61b9d7e4acdabad03c1afbce6d7917626699)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edce8ba1231d6e8355ab42249b6961a129dc5a0fc6ae3a819432cbefab588f14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupExcludeServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupExcludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupExcludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupExcludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__66ec5bfb81eb2ec3dfaf1507f32b9b6d6ae3315e279c718d2b6d05554c7a75f0)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ed5cd64ffc2d9a461ba831e5cc808af76852404b7a0948f766bd8da03eb3c7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupFilter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "search": "search"},
)
class DataCloudflareZeroTrustAccessGroupFilter:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        search: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#name DataCloudflareZeroTrustAccessGroup#name}
        :param search: Search for groups by other listed query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#search DataCloudflareZeroTrustAccessGroup#search}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__028d0ea244dba1350cfc840316ed2d147c51423af9a6686cf943053a5696a975)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument search", value=search, expected_type=type_hints["search"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if search is not None:
            self._values["search"] = search

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#name DataCloudflareZeroTrustAccessGroup#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def search(self) -> typing.Optional[builtins.str]:
        '''Search for groups by other listed query parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_group#search DataCloudflareZeroTrustAccessGroup#search}
        '''
        result = self._values.get("search")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__76f2de05ccf7cf11a7a37a6c655cc790e9fdf174c3b65254c04f209e4b168c4f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSearch")
    def reset_search(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearch", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="searchInput")
    def search_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "searchInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6db987319d0360f8819beed5ff554637e0ea283e021c3a38886db9dfcc9194d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="search")
    def search(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "search"))

    @search.setter
    def search(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb906d3ef47b661a9ebef13dafa8ff86a3199b362b260f1b2deb8b325530d1fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "search", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustAccessGroupFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustAccessGroupFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustAccessGroupFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a690337c381ec75268267ece4081f07758022179624a1fba4c8e5beb87bd9430)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupInclude",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupInclude:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupInclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__924253d35ce9c1ef789e24b2eb73aebe38d11ce6bee75ce1c89081fe4a9f397a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36d9056f490b8b0082431292328f9a7d776610b17dee656c68492b4853b19d7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4931db936bcd2afb01fe79dbef49b74ad6f3b4091dbc5aaef9eb992eea25a577)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1033a33a0b11cafb32eb31d1e2dbd5b936166c8199e324e001e88bbc43a1d590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa471dc360630997cc1f1e2b42784aa4e67512ff58771b3f2f187b078de8226a)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1c64a03ce816d84cb44656d18f5a77bd153676c2f4f1955839e2a22c646238e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f5dfb14264184d3b76f9754370a39aae422713f96c01772a625917dbd633c86)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e546ff56f4b36c5e4f0af96f38a3294ceb52e88dc60f9ed4c5ac7f252841bee4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8fbfa703727de99e42899ba9c188eda100f8b742cd7af82afe206e4a504b6759)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f98f4cf1be01936f47d2ad944d4ceaf6c91cc7a9f5a0726df14c97f00001a51d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__afa0ff36e2c3f7c779a42ba114e740ab0f649c33b1923724d72b11fef69e5dac)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__760274533acd02affeacff7978216688822c0dcd06190070d81f71c4dcb5f195)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f16b12e631b3be3f7f1649024edc6f6c83a645b119786177ccbfe2ab1b03abc)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39957b1ddd2a4dbe8560a2a8f5940ed5903668920bce1a00d5a8a0ca80c33bfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d5cfffedb8e70c4ca7cae2d635448e6674d00f38e354566c1ef3e49e80649c0)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2fb49b5f891af7805d98be915348545874c582c50450f9e11dab0ce6e579bff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f504fe431fcfbc2ff364836cf8a46e86452b92f3d4bf04c927b712325b330afd)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__771cef4103b809e46df02cc466a1403874163ecd1602ec0adfa32737c71050c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupIncludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa8c68a54f035bbd80c6cca532d24355d50c65b06fa49326a70adf9122d471f7)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbdca675c785d29792f6b8b0dcf6c4b0792287eccd11d3bbd6488abe3fcd7e13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__05475d879ea01c2179619063743958ecaa50b0e9c92d2e86e976e78b678f9e57)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bef43b77e66f93abc1f57e8dee3be73edaaf74f9acfb94c4c150bc7eba1f7a31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b8aec39528c3a1ea6a80c1fd03808ee6ff7b272ef9e911020811f390095d7c99)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__378a1f5717973e6c0ebef502876ee27de0cfe2fa34c8b6f189fccf40e38d0349)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4eb896b4d48bfcaebc2f5830b463c91506dea6ad0644c8e36a4ad1ed438aca6)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db965f5c1a27d701d0030da0a81c12d9d8d9b7fb5ac005dbf7674b7a9c0e8ed9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__007d4138456e851e9aeabb0fd6697a8f434e1b5bbeec5ebe7a6430cb3778f106)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f5862bd0e0b3127cd4a6415c921625f5d55ec923cc482aa2614b25c9b383867)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a86a1da1157bec7c54aeea8f6538e23daac197161103ed4994b561c5d11ea3c)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6fcc180143c701492a52b64b7a2fe6ab45c776cfa0ad53e476fcc830e2bba62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c219fff55b522a9452083aacba02a6ac9662f2dc7029b0fd3145dad2c4d19cc)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dca160333f94ace5771cf2a23c28e5a33368527cd2ab0bcc9211aeadd413b494)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aee53c524f2c35a4c132e4016dcf6600f995b3a00f8e5c28f07570ad42f0f7c8)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ace101c73b1418b72ef42730f998de936c3b83c80834b595a0f69fbc7d9342f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupIncludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c956ff65309b83e69cde7029c2cadd8d3dab07762b45b457cf288ee4384d4f0)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f8606dd308c30f5fff81bc43e8fa4effbee8654566ac121cd6a8efde7b77ed7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__12eb8960c5c5525615f4f99c12b0a8598b8a4574257ebd68b81026e9a3144088)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cef8f6e2f14529629e4fd53c456c1f583eabf1c78f47b42751b6ed9aa0991d8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupIncludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac7743be89f77748a6ff3e9ad5b0e54436297c6d5327621d2b8a205afdfcee4b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessGroupIncludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9e4a4b2844fbf948fdd4b3e6cdca8b481026293ae6575fd9bda05581d87bad8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessGroupIncludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__665eb596f7e69605b33a62cde41fa345cb45eea156bd0abc4a8c6ab0f2e9ec6d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc1162a4d7f2e96107e025e8658bfca16769371ec669ad3907a0b3357cf45253)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3fd6a90b6ddd79ebbfe42c19d7461bae91d3d84b9f957051c6c4194a0d2351b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e62d6bb3f362ee20f3b773ff7d177ada173ffbd7a3e78ef8d5b9cc78527d761b)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd65204e8405e152ee686a609d9560f60bb066f350562420822279ac45ad10b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a700841f461ef2e142b3b9e8df757e4a22d977326c7cd7ca3e0030660c0daef)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f57e624bbf7058654a7ae42a0c1df08f536529f1e79f923dedbf66161d2c44e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__450722563e973e868a4a7b89c5c93ebbc87fa909a1597c83f78c8c5f24d26849)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c128e239dd02307b3bb8f7dce2040d472a98b413f434cbb4391f846d766bd46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupIncludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b008553a4571d6ceecfad469e2efbadb3809dd349979aad6ec365bde5ff6b11)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> DataCloudflareZeroTrustAccessGroupIncludeEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> DataCloudflareZeroTrustAccessGroupIncludeGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> DataCloudflareZeroTrustAccessGroupIncludeGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(self) -> DataCloudflareZeroTrustAccessGroupIncludeGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessGroupIncludeIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIncludeLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> DataCloudflareZeroTrustAccessGroupIncludeOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> DataCloudflareZeroTrustAccessGroupIncludeOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIncludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "DataCloudflareZeroTrustAccessGroupIncludeSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupIncludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupIncludeServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupIncludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupInclude]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupInclude], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupInclude],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe39da51b606580a30c4676cfe342714b837dbba646998d4b43f384d62af1bee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__41e2b7ae8d582c6f9b89780fc7704169b46426a8f6a915127780939e4cdb4314)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a456fbbdd331b5b0d39d42b8fc045641ab36d2433e7895fdf457bcefdc98a48d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIncludeServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIncludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIncludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIncludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2fd1d088dc233fcecded8f09a232ac8d708ce5ae35959a951f536fd42c04b967)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72c0cc239e18305f840595fac3a577ea2a76e1e08c63d4268076d33acae3d077)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefault",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefault:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefault(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec6848d54fa8c40d1bac6100e8a05dd46d075e430282ed972b8b8b6c30f6bc37)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38c113b85e76de6582db0e912fe45dc46cf55e6ff8cda934c7624517dff3e88b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e97f22818f0def45dfa4e414e0639f9272dc95822cf98105c3927c16a68c067a)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e983672a0a1daebdbe340d4420d41a5ed6da5a5b9576a8d345b552a3d6d7140c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef30f28f9e7420b3c6ce3b6467541b6471a79249754364b7b6bfb404859d80de)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc631e90f19a6b2717a90869999c67e9733f221a06468074e31ed9d0ce943198)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e69d0bf64bf8a1af97cb0ca970b3fb86504aa7517a18dca47425c0c36074b0ba)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83eeec0bae9094c5f9b5e92c2bb1f0d035cbfbd9ca5e5b4a80412029a5a653f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e819950ffd647a3968f0d513f928f743024518868304c75c9688ec81f0136cd2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83e77731f7ad60dad36585334d421fa3cb368b05e9257c249b5e43ce9b5be398)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4212f62e4aebb179619cafe0b9032156fadd9dd213a447ee7f24a9b6501fb537)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__381f442db14a89db5f43467a66f871de0d20f086f9ba2eb770aa7a155c6791d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__21a2a79bc61899f55092b40bbf93a7cede8b843cb68054af1c661f62911e4dbd)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0cb7fb83ef091d28c98b8a7085032bebd1d8e38f5b1776e969299f91cbad9e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__946997fea0769c31833dfe89780a23e65aaeec1e1dfa2b04dea9971a0ced605f)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aadaaa04ef10403696df786c1711804ebb8f34fd06e66958a984515398e523b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b3ee76075a8e8833a4600063a6370ef1b86d9c27db3f8c7cba798806eb2ddaf)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51d7a53f0bf5351c40c058348ff1bb3d070dd3a74f816e70d599cff8ba5d533e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupIsDefaultEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b555f1a1380f5d467cd8ac0f723ef8ed6e53861b4d046cda4df59bd4daecd57)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd21b0ddcbadd605893d2851758bf0a610f88894eee37f2cded0a914cba61fbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__147cedf88e80a64636724d0c46ea77e5bb84d17e700df8ab1865543f9718d8b1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2bd59b99544eae730076de80b0770747fedabfba6e401e92b1a39814b004d00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7495737521159bf49d8855416475c46ea5af2300ddbfff66d7dcde88e8b7f49b)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a96f6a285056c2bb212a117698802b8a846eb2501953cfc75e1f37a054e2c6d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ebb4fee35c18132097bf26c0df7a956fb0098ea319356cac1c5b6cc75e61d22)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e8e3e4a902d1b91900871448017681398571c7401aecbdf93da98e62d46c405)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f0c8e1e6608e87d6c94008a302c15561abcf3f3b40f3b032bc827f6458c291c)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__628bf359c35cf3c63961773b1b62979512106d1e3987e320a335b15c3d9ec2a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da821aae1153908501029237dae3e2d78071b80ce4607c274d7191faf6448710)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5259d9cd96c68c36876f2687f2f1d78ccda4ae46194650791af5c997d41fc6da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed9c4eff81e28a3c887802c07e72393225f5fcfae5d0901bd26add18adf1b0d6)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd56a5958fd2e6a168f782281af987cd6e4391206291cc8bc17d013c50df509d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e3d83057392708f39add5cccf856ed77b628b9c608d2113f84a706df3d1ab77)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c06164224053f674b4f492bb18a5e4336639b4c94e822023f4461edd27d9244)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupIsDefaultIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ff2cabfa0ca4f4de175599ec91c16cde5067ebcac8b958a6913143dedc4daef)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea387be8a69525a7f952fe36b4853a37fd0a88b0757e83c6464b9fa07025b66b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__edda1c0ea9240fa3d9fbecb3c0e6b2375b561e874aebdd9a84dcbe0eb41cecfa)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b42c874bd40d903fb5207ff96c6d937b76782f15869a36f1ff2e303f31abc5cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupIsDefaultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__118e08ea0644ba65c9d8a964e4b615a1a1350325e2979fc2b86feec27075154d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessGroupIsDefaultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30ea8afc9e6733ca3f937f992e64ad964f2612d15b8289a8b35d9f866fcc9ba4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessGroupIsDefaultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d8968dbd0708f593bf1cc20b5146b30ed7623fc04927de40fdaa7279414da27)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8277a93d2bcaf1e9f630c2916d037e67af5fc53fb1fdc1952d58687eb82c3d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__963bf5f37c160f28eeda629f9c0d686931e8986958f0c34d8f5a93c261741872)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a701d1cf0c1dc983bd8ffd78b4842a66ae3716b790fd33e659d0bbb2819f1bd3)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee1b137113dc233d8bdd09d64c147c1a1169f689c197e7c34409a6519c8ee116)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f21fa8e02b935ea7d677a232fdeb5b8ee414ab23536218de7ec2283c63ce6a61)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9e748bf5229ff12a7d2bd962ae31924cccfb89f23581804800b3015773b8e5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eed26d1dfbbf066d5ced1ec06618803af618e907ef7890ed0ca271138704c6b2)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df8b80b6fe3cb7f4f84c67085bbfd5aaf6ddc8ad98c11010bd4e20171126282d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupIsDefaultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2cf8170374c6e120a0b9919dad58458c4c6f7696caf67aa2c4a6854e1d7c4eab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> DataCloudflareZeroTrustAccessGroupIsDefaultEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> DataCloudflareZeroTrustAccessGroupIsDefaultGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> DataCloudflareZeroTrustAccessGroupIsDefaultGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessGroupIsDefaultIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> DataCloudflareZeroTrustAccessGroupIsDefaultOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> DataCloudflareZeroTrustAccessGroupIsDefaultOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupIsDefaultOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "DataCloudflareZeroTrustAccessGroupIsDefaultSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupIsDefaultSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupIsDefaultServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupIsDefaultServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefault]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefault], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefault],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abd2f5189fe7d28ab2a4bdc066bc383ccbb6906fd3a2a67b29ee096b8bac45e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c0a78ef63d3f276807e8dfefb6c081b527841b26f720cd615f14f8f679d6b27)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b08449a430789ca56ae8584aa72bc8c786c182c310991bcac8fe39416863a7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupIsDefaultServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupIsDefaultServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupIsDefaultServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupIsDefaultServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__29d09113d3696f7dd577c57757fca4c24b8b65de5eed61fb437627bcf7328c6c)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c16d6b319c4f4f00c19709cba65027fe2cb5a17d2ba5b5e016dbcb56c1ef45a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequire",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequire:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequire(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2b82e2d2c76d7835968723c9ce90a4cef23938d85971080b3430fc72ae00dc3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25709ddc7553e0a3b8a9d3da4f799a694a420e2bdd09ae927ad552ea068b45f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a79169ca98e279541e131adf7df8f54c044631eba2d99867e8383d612bc70db)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df1bf4bd7d57f8b570a8e326f9783fd35a70b2fbdf8f8e380d9e91aa531f5b87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c4d248853ea1800bc87b6b2daef0f5dcdbb36992bcf7508b14f712babb77389)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f8128d1c21987d16646962dcf53cfc251d1302f6c2dc9802c20cb9081cbb9d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4af48b8a6a23525f97fb456ffc56fe0c2e91fefd26d23b72fffd1e3656c0aa1e)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ccea7d8ca5ee0dabcd6bddb757bba5375d11decea9d55b598cd09d217b891ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__465489f6127fba06ceb2add781603be747fcf92789902d194a578a334f614533)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa25326d8c1bdc2272cb02a4df7d4f2d21ceec7627cc657d1ff7c1c678dbfabd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd07ac65bd8e915ba590d52777b30740dce6bbf961de9cbf637d2a27f0f84837)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c26fe5ad6913bc81c704db19588896d8dd3d010ca27fe88e262c2b395ed0e6bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d06510ed9d8986c67b34a5d870312e393927dbddd3f27a40ca70f818f9d4db1)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fbef6681f05d0f11f880de902f3923e66ed1f3c5e4e01d53a3f2ec0aefa16c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e68a2a240f66edc314004443967526ca7127a97701bd5f5fb06988871cf939fc)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4acfb20df3497252785c3ad4c3a373d0be268f48c4f67bcc8f5681601ee8592)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__75509b6e03f0ef1179e2daba438c42c52f6ab9a300b3bd0f012e8c1d638892d5)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dac4abaa72a9e63d01110e8c4acfbb0fcd2913a579f8c0513c78e9215fe8f072)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupRequireEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f15310a8631fdad192dc362fb346a1a9c1a2df92aca9a42a7bedad5d85b234f)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f11c02589b7a2e30548e60c4be62978dfd89a797acbb92382b9375487613fb52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__677fcdb4fa7b2725260df175f5c331073e8444b3b8ec7ff24a666be8f3b5f3de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__885193a98c44f4868dc47cc71bcc88f6fdf336219d191f7468dd9d9414d9c318)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6bbcf6a523e42ecb21da280276f41ef52613825f710595c64764a52017802277)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6073c7b96be243d249c2ca2bf5f725cbfc00bbdcd3df29dd58084ff9c8ad8ac2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c24fec7de40d55e7eaf4825dcb9a1531730d006ff4e3505fe8197d63fac68f0f)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b8f8060315bc9b418fb690216b140e43335edffc9788a433b723f424eeda7f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__92b03baa0a65aa3d71feacbbf7ffdb4faec62989591a402870f9944fff087c90)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2adcbada2225b09049ea8b93baf5dc6d23b886a25fc802aa35059b20109cf3d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd49fad87dd0f654bb6a77b97c933baf637a0dc24a6f2c781b5c092a49b881b0)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd16e8c4f1da8b4405dfcd07dd799e5285727f00825db8fc2a44edf0d86aa59f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67407f39f61bcd72564e10267f499600ee477f82ea6e3e7d1653a1f30182e8bc)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be8c0b128ef56a5d48c4b9a2f9f121a27fda01372e908db08557c6a05e3fc682)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d353463bebfe6cc8c8c6af662ea395fd486178913d7a60fbd715567877da5c0)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa2c1d47c86c7696d8abe71bf1685aa33d0b2d93305d1b5972f9052321fa9bba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupRequireIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6719f3bc52e8cfd2df7651ffa90783fb066ec6fbd11e8837c9ff7d14c4eb69a3)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16474e16481b9a0488d27238ad20b45a924fc0ea300ff8858ae9bd4734b88427)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc34453d5e52bd3a4d9987378e34b45e10a3aded3bb256a59284b6e38e1c14e7)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__409175e066bbafcff516543ced543073a75e74b1b80a86fad448bcf3abc5af87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupRequireList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae0c04074c66c9d32cbe1bc9b4f7a5853acdd6a6424fcbe8432daf04d0895f52)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessGroupRequireOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__247b6dae3474911f1321556b26cdd3bfc45c9ad7d65e3a327f23acc244c74129)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessGroupRequireOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19649a0bcb58ccbf4ff2d0b6d0496fc0f43e1d70e639b3d907eb75dcd82ed351)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a973690702084fb4fa276d878d21d46f4f0f6a5f0d49350b7415ee636bdca12)
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
            type_hints = typing.get_type_hints(_typecheckingstub__474d602df21fb419a4c98d8e7ceec0febc248078f9fc214047bd7a429e77ab33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be34559995302938d5ee3b90fe3ed7582010efac61d150a3e95f9da1da30f2dc)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74876c99a5d910d5fc2092e65153862e08daa69fe02e0ad448b79be52f749b7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef072c04c872a1db87a2530eca1a3122dd6056474ace4c06242043ea8a5d87d1)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f79deb007bf8746836b5d659fd0c87c4736eb893c6df81706a7528ab953aa24a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__85e42d6fd9c61eca563aade45a2ad92a11654be222ccea79ab72362933d03925)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22eb163be9c11a1e006bd9cb1e2a372a8a04e1512a8e80409a7e0e8d2d8f5490)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessGroupRequireOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7981dc0a893ed774297452440ce710f66d23ace594eb00b5555187eb2060a37)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> DataCloudflareZeroTrustAccessGroupRequireEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> DataCloudflareZeroTrustAccessGroupRequireGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> DataCloudflareZeroTrustAccessGroupRequireGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(self) -> DataCloudflareZeroTrustAccessGroupRequireGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> DataCloudflareZeroTrustAccessGroupRequireIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessGroupRequireLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> DataCloudflareZeroTrustAccessGroupRequireOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> DataCloudflareZeroTrustAccessGroupRequireOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessGroupRequireOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "DataCloudflareZeroTrustAccessGroupRequireSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupRequireSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessGroupRequireServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessGroupRequireServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequire]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequire], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequire],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d17a4069ae764dbf58e07baabd8a9873419d904c85284ff745c06c5439f2f023)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__90512aa3924754410536bc7f6e97f207883c3aa32ca5615bfc6dc836335318ce)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5da2bbb982bc16225a32413aeccd0136a90763958c048eefdafcd0203143dda0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessGroupRequireServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessGroupRequireServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessGroupRequireServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessGroup.DataCloudflareZeroTrustAccessGroupRequireServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8074d3fe677a511a3188193456605091b13f7cab5557528c6908a7bbeb6ed08b)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessGroupRequireServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessGroupRequireServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf24b40717c6e867d79125c4674618b05937ba3db5a5131c7c7070887a0d4519)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustAccessGroup",
    "DataCloudflareZeroTrustAccessGroupConfig",
    "DataCloudflareZeroTrustAccessGroupExclude",
    "DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeAuthContext",
    "DataCloudflareZeroTrustAccessGroupExcludeAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeAuthMethod",
    "DataCloudflareZeroTrustAccessGroupExcludeAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeAzureAd",
    "DataCloudflareZeroTrustAccessGroupExcludeAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeCertificate",
    "DataCloudflareZeroTrustAccessGroupExcludeCertificateOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeCommonName",
    "DataCloudflareZeroTrustAccessGroupExcludeCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeDevicePosture",
    "DataCloudflareZeroTrustAccessGroupExcludeDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeEmail",
    "DataCloudflareZeroTrustAccessGroupExcludeEmailDomain",
    "DataCloudflareZeroTrustAccessGroupExcludeEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeEmailListStruct",
    "DataCloudflareZeroTrustAccessGroupExcludeEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeEmailOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeEveryone",
    "DataCloudflareZeroTrustAccessGroupExcludeEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluation",
    "DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeGeo",
    "DataCloudflareZeroTrustAccessGroupExcludeGeoOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeGithubOrganization",
    "DataCloudflareZeroTrustAccessGroupExcludeGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeGroup",
    "DataCloudflareZeroTrustAccessGroupExcludeGroupOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeGsuite",
    "DataCloudflareZeroTrustAccessGroupExcludeGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeIp",
    "DataCloudflareZeroTrustAccessGroupExcludeIpListStruct",
    "DataCloudflareZeroTrustAccessGroupExcludeIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeIpOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeLinkedAppToken",
    "DataCloudflareZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeList",
    "DataCloudflareZeroTrustAccessGroupExcludeLoginMethod",
    "DataCloudflareZeroTrustAccessGroupExcludeLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeOidc",
    "DataCloudflareZeroTrustAccessGroupExcludeOidcOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeOkta",
    "DataCloudflareZeroTrustAccessGroupExcludeOktaOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeSaml",
    "DataCloudflareZeroTrustAccessGroupExcludeSamlOutputReference",
    "DataCloudflareZeroTrustAccessGroupExcludeServiceToken",
    "DataCloudflareZeroTrustAccessGroupExcludeServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupFilter",
    "DataCloudflareZeroTrustAccessGroupFilterOutputReference",
    "DataCloudflareZeroTrustAccessGroupInclude",
    "DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeAuthContext",
    "DataCloudflareZeroTrustAccessGroupIncludeAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeAuthMethod",
    "DataCloudflareZeroTrustAccessGroupIncludeAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeAzureAd",
    "DataCloudflareZeroTrustAccessGroupIncludeAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeCertificate",
    "DataCloudflareZeroTrustAccessGroupIncludeCertificateOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeCommonName",
    "DataCloudflareZeroTrustAccessGroupIncludeCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeDevicePosture",
    "DataCloudflareZeroTrustAccessGroupIncludeDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeEmail",
    "DataCloudflareZeroTrustAccessGroupIncludeEmailDomain",
    "DataCloudflareZeroTrustAccessGroupIncludeEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeEmailListStruct",
    "DataCloudflareZeroTrustAccessGroupIncludeEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeEmailOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeEveryone",
    "DataCloudflareZeroTrustAccessGroupIncludeEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluation",
    "DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeGeo",
    "DataCloudflareZeroTrustAccessGroupIncludeGeoOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeGithubOrganization",
    "DataCloudflareZeroTrustAccessGroupIncludeGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeGroup",
    "DataCloudflareZeroTrustAccessGroupIncludeGroupOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeGsuite",
    "DataCloudflareZeroTrustAccessGroupIncludeGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeIp",
    "DataCloudflareZeroTrustAccessGroupIncludeIpListStruct",
    "DataCloudflareZeroTrustAccessGroupIncludeIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeIpOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeLinkedAppToken",
    "DataCloudflareZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeList",
    "DataCloudflareZeroTrustAccessGroupIncludeLoginMethod",
    "DataCloudflareZeroTrustAccessGroupIncludeLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeOidc",
    "DataCloudflareZeroTrustAccessGroupIncludeOidcOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeOkta",
    "DataCloudflareZeroTrustAccessGroupIncludeOktaOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeSaml",
    "DataCloudflareZeroTrustAccessGroupIncludeSamlOutputReference",
    "DataCloudflareZeroTrustAccessGroupIncludeServiceToken",
    "DataCloudflareZeroTrustAccessGroupIncludeServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefault",
    "DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultAuthContext",
    "DataCloudflareZeroTrustAccessGroupIsDefaultAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethod",
    "DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultAzureAd",
    "DataCloudflareZeroTrustAccessGroupIsDefaultAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultCertificate",
    "DataCloudflareZeroTrustAccessGroupIsDefaultCertificateOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultCommonName",
    "DataCloudflareZeroTrustAccessGroupIsDefaultCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultDevicePosture",
    "DataCloudflareZeroTrustAccessGroupIsDefaultDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultEmail",
    "DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomain",
    "DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStruct",
    "DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultEmailOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultEveryone",
    "DataCloudflareZeroTrustAccessGroupIsDefaultEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluation",
    "DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultGeo",
    "DataCloudflareZeroTrustAccessGroupIsDefaultGeoOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganization",
    "DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultGroup",
    "DataCloudflareZeroTrustAccessGroupIsDefaultGroupOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultGsuite",
    "DataCloudflareZeroTrustAccessGroupIsDefaultGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultIp",
    "DataCloudflareZeroTrustAccessGroupIsDefaultIpListStruct",
    "DataCloudflareZeroTrustAccessGroupIsDefaultIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultIpOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppToken",
    "DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultList",
    "DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethod",
    "DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultOidc",
    "DataCloudflareZeroTrustAccessGroupIsDefaultOidcOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultOkta",
    "DataCloudflareZeroTrustAccessGroupIsDefaultOktaOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultSaml",
    "DataCloudflareZeroTrustAccessGroupIsDefaultSamlOutputReference",
    "DataCloudflareZeroTrustAccessGroupIsDefaultServiceToken",
    "DataCloudflareZeroTrustAccessGroupIsDefaultServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequire",
    "DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireAuthContext",
    "DataCloudflareZeroTrustAccessGroupRequireAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireAuthMethod",
    "DataCloudflareZeroTrustAccessGroupRequireAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireAzureAd",
    "DataCloudflareZeroTrustAccessGroupRequireAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireCertificate",
    "DataCloudflareZeroTrustAccessGroupRequireCertificateOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireCommonName",
    "DataCloudflareZeroTrustAccessGroupRequireCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireDevicePosture",
    "DataCloudflareZeroTrustAccessGroupRequireDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireEmail",
    "DataCloudflareZeroTrustAccessGroupRequireEmailDomain",
    "DataCloudflareZeroTrustAccessGroupRequireEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireEmailListStruct",
    "DataCloudflareZeroTrustAccessGroupRequireEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireEmailOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireEveryone",
    "DataCloudflareZeroTrustAccessGroupRequireEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireExternalEvaluation",
    "DataCloudflareZeroTrustAccessGroupRequireExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireGeo",
    "DataCloudflareZeroTrustAccessGroupRequireGeoOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireGithubOrganization",
    "DataCloudflareZeroTrustAccessGroupRequireGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireGroup",
    "DataCloudflareZeroTrustAccessGroupRequireGroupOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireGsuite",
    "DataCloudflareZeroTrustAccessGroupRequireGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireIp",
    "DataCloudflareZeroTrustAccessGroupRequireIpListStruct",
    "DataCloudflareZeroTrustAccessGroupRequireIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireIpOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireLinkedAppToken",
    "DataCloudflareZeroTrustAccessGroupRequireLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireList",
    "DataCloudflareZeroTrustAccessGroupRequireLoginMethod",
    "DataCloudflareZeroTrustAccessGroupRequireLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireOidc",
    "DataCloudflareZeroTrustAccessGroupRequireOidcOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireOkta",
    "DataCloudflareZeroTrustAccessGroupRequireOktaOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireSaml",
    "DataCloudflareZeroTrustAccessGroupRequireSamlOutputReference",
    "DataCloudflareZeroTrustAccessGroupRequireServiceToken",
    "DataCloudflareZeroTrustAccessGroupRequireServiceTokenOutputReference",
]

publication.publish()

def _typecheckingstub__bc51ed4c1304a7e7e40ce32dd7595dc7840e74481a2f6c78037921ab2a6b8bd0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    filter: typing.Optional[typing.Union[DataCloudflareZeroTrustAccessGroupFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    group_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__bf042d790b279ab44db69a01815f7b25db1cbe0e866b4a31d73baa4176381a22(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21c4d845e18b3ba400f3d3ec47f49b4e6a86560a0bbbf0d67006ae45d609a6a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b507b0976f2640b6ef871adbf3e9c382df0f89faa8752b5a7a21f9579d29a43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5cfaf1582d304ab4d8c167dd466d6d95e392ba9f2e97b56575389a424b56b1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a580d9d2a2b92a92ffb0017a690f61fb7ae2be7b7953e1098aa5eb9564a08b4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: typing.Optional[builtins.str] = None,
    filter: typing.Optional[typing.Union[DataCloudflareZeroTrustAccessGroupFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    group_id: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__242c6871d0adff988f7523769d55be989a069cd594c1b6daa3838ddab63c2fbd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94733030c590973d4136b4881b676f7a852d2e3f95573f7ba5c821a367131161(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ac9a31c7e7a83774298a9cb1ad4407c85e62307adf296a6f52064a74a6db0d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c045e3fb1b67313ae953d55ec386ccbc33ede07ff54c53c1b9ea0fac32efde5(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e56834a866bd8031303bbee1b4a61f7f0c1f0febba7b08c25d123eb44a68aed7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed4d6ae046d34e112052230e1e9473dffba7784d9b8325dd12b8f02ad0f40565(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c427276a5e4aa138c44e5313c23d36e85842e820cb5085d4fe738b75d331678(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae5706a27ae4b3f5211b8f6c88ee069474e105feea49546e59bde0d8a1c91836(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe6a9807ceb649a13e6e571b9eb0821098179c514f8485fa5dc61932194f1424(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b03aa06c729eb9778c0d1607747916e22403aba31400cdde0e0716e43da9cd4(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eeacd3c40f65c9f5b7374e7eeb3a8f27441dd318b360daddca2588e8887dbe0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6a003f2e195c86102eca343b8b7b15e6aea0323c459f451a0450585bc62f8a7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfa0cf67b760c04b14bcd407b519e77e397fa09618e5f38b7c2ce4679bc7495f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4692ee4b2a779789ed06b7f962d837c7c8020bdad39be100a544a944d1eb7d5(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7672516fa1cbcdd058b325340ef5d7e3b8b0699d0480b9b252453a6970d17e91(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d78d1ccd55362f0fc3f7d2032175a282236c96499ced7d696048ec4d19bd675(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e32dbcd799c65536f972944026c6887206f131cf7ff342caca560737585c254(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcfeba9fce77a53d5843fa4cf26c6a854987331f5f9205a3d14ab67cadd4bc8f(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fc32a5a0151456a2c56437405d949be2d0f96359fdc10703a55738c3a6d6712(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43b6f383e974455bf135b006d2a762f3638530430105001e69bee879da094053(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd33885120ad86fdda7e801cbf4c7178d52a18abfb9046581fb8bb057f80f29(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7dd72f31f314cdcfc5ff6e45dbba805f8af3aa87724d9ef0ed18cc93bdb735e(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ece0ac8df6c10286c136b421c6baae9f024f70d2fcfd2b85e5233905650f63d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54380a0eeb02cdd3ace7763ff02d5d31f46017f918b0c47f98257d5af17ba533(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14bff72248f9cc2af0011c3e8d051802350470fb33ab17a7f201d754b1e643eb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1dc1e87115d93c963221b9d703106e3dacd31663fbd13a4c26802d726de358e(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c7da0880bc2e025e1f0123b8997b4eefd13f6459a27d94ffc79ad6da14c99b9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b3caa8422e1f9501afcee80200bd5e6edfc98af336c6fbd137e2499d45958f9(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fd86bdb322c90f152bfefec85a9e4b9131b8d81b20c15c122f728ae5847fdfc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4ae30b0c248be0fa817375f3930d603dae9af8a06ce3525910a4971ef624364(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2214e7f77796676d7705d655a15cc10e75c3f258a8e97181acdc2426fda85eef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c199594b6372ef7fc168305f3d4f40f7eb2ed7360c065a3002060993ede9d3c8(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8faccec9dd9590e8e431d5e25031ee2e34a057eb47ec2bae761d8f5997011764(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d5fec7f9939b1b4f0362954a05a9743dc99a9611bafe26c19f79b778de31ea2(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8335ef8eb52c899829d8b108c2764d331730529e48eea0b79bfc335875e1fbf3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0fca63c4987d13e9ee45c5cf0c2d094404f81a73dfc96647893c4dbf9adacaf(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca36f36fdf9d0cb95fecfa3f0863c204e67ef133e0ef5df2d1530f05e2c9a3a9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fed2b78029fe46981b40d8a11baaa6206d10c45283741c7df24af36cfe1315e8(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24a88db79342a3192e504a4c373284432eb4d3a5c9165aa7b1ad389ac731cbca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08a4d639eb0d4833ebe7e15e272049a9a5e4dc567d5554b588dc9ca6fad23510(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__106706fdba458939017a733c5b71dd90af1b7e504fbfb04c4127b365e28b3b17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88a71478412352cd75609bf878efd0cc6164c99eb69754423de8f7bce075de46(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__890f5faf314a43a26bdbd7aa2e286bf7b0d170b63ad1d9a6fafa7ea9288f84d6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__955277fb4e527490d18f6248b60558f357e2f00b0f078f639626b4a651ec7d11(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__743d0a0567c0884d3b3b7f66e51fca3bd7a61b2b16539ebff8e735e44802ec77(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34a8be4c0d3c509a93cc46fa33b579ae8d99cf7272e038f538272a08cd086812(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9b59d840dc8cd54f582864c9d75f7ac7e369003d31eed2b667dd07f5f769b74(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6cbf8d00d36c22e0b2a51da7460961dd14b0428a8c308c529db688f14d10ab6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6105da068966f27b52f49811d284dadb8670a87348e234dd5309d90e10aec9c(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10cd2e21f00a477d954edb3d49d60e73b955e843ee0cacaf9ca2456671712131(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b064e2171d3c821103f00f46d136c63a3fb021bf7ceca1f31e568f420f692d1(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExclude],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a65ecc0ef9ec4bec371d8ce7eaaa61b9d7e4acdabad03c1afbce6d7917626699(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edce8ba1231d6e8355ab42249b6961a129dc5a0fc6ae3a819432cbefab588f14(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66ec5bfb81eb2ec3dfaf1507f32b9b6d6ae3315e279c718d2b6d05554c7a75f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ed5cd64ffc2d9a461ba831e5cc808af76852404b7a0948f766bd8da03eb3c7c(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupExcludeServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__028d0ea244dba1350cfc840316ed2d147c51423af9a6686cf943053a5696a975(
    *,
    name: typing.Optional[builtins.str] = None,
    search: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76f2de05ccf7cf11a7a37a6c655cc790e9fdf174c3b65254c04f209e4b168c4f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6db987319d0360f8819beed5ff554637e0ea283e021c3a38886db9dfcc9194d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb906d3ef47b661a9ebef13dafa8ff86a3199b362b260f1b2deb8b325530d1fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a690337c381ec75268267ece4081f07758022179624a1fba4c8e5beb87bd9430(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustAccessGroupFilter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__924253d35ce9c1ef789e24b2eb73aebe38d11ce6bee75ce1c89081fe4a9f397a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36d9056f490b8b0082431292328f9a7d776610b17dee656c68492b4853b19d7a(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4931db936bcd2afb01fe79dbef49b74ad6f3b4091dbc5aaef9eb992eea25a577(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1033a33a0b11cafb32eb31d1e2dbd5b936166c8199e324e001e88bbc43a1d590(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa471dc360630997cc1f1e2b42784aa4e67512ff58771b3f2f187b078de8226a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1c64a03ce816d84cb44656d18f5a77bd153676c2f4f1955839e2a22c646238e(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f5dfb14264184d3b76f9754370a39aae422713f96c01772a625917dbd633c86(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e546ff56f4b36c5e4f0af96f38a3294ceb52e88dc60f9ed4c5ac7f252841bee4(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fbfa703727de99e42899ba9c188eda100f8b742cd7af82afe206e4a504b6759(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f98f4cf1be01936f47d2ad944d4ceaf6c91cc7a9f5a0726df14c97f00001a51d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afa0ff36e2c3f7c779a42ba114e740ab0f649c33b1923724d72b11fef69e5dac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__760274533acd02affeacff7978216688822c0dcd06190070d81f71c4dcb5f195(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f16b12e631b3be3f7f1649024edc6f6c83a645b119786177ccbfe2ab1b03abc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39957b1ddd2a4dbe8560a2a8f5940ed5903668920bce1a00d5a8a0ca80c33bfc(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d5cfffedb8e70c4ca7cae2d635448e6674d00f38e354566c1ef3e49e80649c0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2fb49b5f891af7805d98be915348545874c582c50450f9e11dab0ce6e579bff(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f504fe431fcfbc2ff364836cf8a46e86452b92f3d4bf04c927b712325b330afd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__771cef4103b809e46df02cc466a1403874163ecd1602ec0adfa32737c71050c1(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa8c68a54f035bbd80c6cca532d24355d50c65b06fa49326a70adf9122d471f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbdca675c785d29792f6b8b0dcf6c4b0792287eccd11d3bbd6488abe3fcd7e13(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05475d879ea01c2179619063743958ecaa50b0e9c92d2e86e976e78b678f9e57(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bef43b77e66f93abc1f57e8dee3be73edaaf74f9acfb94c4c150bc7eba1f7a31(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8aec39528c3a1ea6a80c1fd03808ee6ff7b272ef9e911020811f390095d7c99(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__378a1f5717973e6c0ebef502876ee27de0cfe2fa34c8b6f189fccf40e38d0349(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4eb896b4d48bfcaebc2f5830b463c91506dea6ad0644c8e36a4ad1ed438aca6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db965f5c1a27d701d0030da0a81c12d9d8d9b7fb5ac005dbf7674b7a9c0e8ed9(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__007d4138456e851e9aeabb0fd6697a8f434e1b5bbeec5ebe7a6430cb3778f106(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f5862bd0e0b3127cd4a6415c921625f5d55ec923cc482aa2614b25c9b383867(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a86a1da1157bec7c54aeea8f6538e23daac197161103ed4994b561c5d11ea3c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6fcc180143c701492a52b64b7a2fe6ab45c776cfa0ad53e476fcc830e2bba62(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c219fff55b522a9452083aacba02a6ac9662f2dc7029b0fd3145dad2c4d19cc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dca160333f94ace5771cf2a23c28e5a33368527cd2ab0bcc9211aeadd413b494(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aee53c524f2c35a4c132e4016dcf6600f995b3a00f8e5c28f07570ad42f0f7c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ace101c73b1418b72ef42730f998de936c3b83c80834b595a0f69fbc7d9342f7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c956ff65309b83e69cde7029c2cadd8d3dab07762b45b457cf288ee4384d4f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f8606dd308c30f5fff81bc43e8fa4effbee8654566ac121cd6a8efde7b77ed7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12eb8960c5c5525615f4f99c12b0a8598b8a4574257ebd68b81026e9a3144088(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cef8f6e2f14529629e4fd53c456c1f583eabf1c78f47b42751b6ed9aa0991d8d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac7743be89f77748a6ff3e9ad5b0e54436297c6d5327621d2b8a205afdfcee4b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9e4a4b2844fbf948fdd4b3e6cdca8b481026293ae6575fd9bda05581d87bad8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__665eb596f7e69605b33a62cde41fa345cb45eea156bd0abc4a8c6ab0f2e9ec6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc1162a4d7f2e96107e025e8658bfca16769371ec669ad3907a0b3357cf45253(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3fd6a90b6ddd79ebbfe42c19d7461bae91d3d84b9f957051c6c4194a0d2351b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e62d6bb3f362ee20f3b773ff7d177ada173ffbd7a3e78ef8d5b9cc78527d761b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd65204e8405e152ee686a609d9560f60bb066f350562420822279ac45ad10b4(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a700841f461ef2e142b3b9e8df757e4a22d977326c7cd7ca3e0030660c0daef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f57e624bbf7058654a7ae42a0c1df08f536529f1e79f923dedbf66161d2c44e(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__450722563e973e868a4a7b89c5c93ebbc87fa909a1597c83f78c8c5f24d26849(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c128e239dd02307b3bb8f7dce2040d472a98b413f434cbb4391f846d766bd46(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b008553a4571d6ceecfad469e2efbadb3809dd349979aad6ec365bde5ff6b11(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe39da51b606580a30c4676cfe342714b837dbba646998d4b43f384d62af1bee(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupInclude],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41e2b7ae8d582c6f9b89780fc7704169b46426a8f6a915127780939e4cdb4314(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a456fbbdd331b5b0d39d42b8fc045641ab36d2433e7895fdf457bcefdc98a48d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fd1d088dc233fcecded8f09a232ac8d708ce5ae35959a951f536fd42c04b967(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72c0cc239e18305f840595fac3a577ea2a76e1e08c63d4268076d33acae3d077(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIncludeServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec6848d54fa8c40d1bac6100e8a05dd46d075e430282ed972b8b8b6c30f6bc37(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38c113b85e76de6582db0e912fe45dc46cf55e6ff8cda934c7624517dff3e88b(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e97f22818f0def45dfa4e414e0639f9272dc95822cf98105c3927c16a68c067a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e983672a0a1daebdbe340d4420d41a5ed6da5a5b9576a8d345b552a3d6d7140c(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef30f28f9e7420b3c6ce3b6467541b6471a79249754364b7b6bfb404859d80de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc631e90f19a6b2717a90869999c67e9733f221a06468074e31ed9d0ce943198(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e69d0bf64bf8a1af97cb0ca970b3fb86504aa7517a18dca47425c0c36074b0ba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83eeec0bae9094c5f9b5e92c2bb1f0d035cbfbd9ca5e5b4a80412029a5a653f8(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e819950ffd647a3968f0d513f928f743024518868304c75c9688ec81f0136cd2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83e77731f7ad60dad36585334d421fa3cb368b05e9257c249b5e43ce9b5be398(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4212f62e4aebb179619cafe0b9032156fadd9dd213a447ee7f24a9b6501fb537(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__381f442db14a89db5f43467a66f871de0d20f086f9ba2eb770aa7a155c6791d1(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21a2a79bc61899f55092b40bbf93a7cede8b843cb68054af1c661f62911e4dbd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0cb7fb83ef091d28c98b8a7085032bebd1d8e38f5b1776e969299f91cbad9e0(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__946997fea0769c31833dfe89780a23e65aaeec1e1dfa2b04dea9971a0ced605f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aadaaa04ef10403696df786c1711804ebb8f34fd06e66958a984515398e523b5(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b3ee76075a8e8833a4600063a6370ef1b86d9c27db3f8c7cba798806eb2ddaf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51d7a53f0bf5351c40c058348ff1bb3d070dd3a74f816e70d599cff8ba5d533e(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b555f1a1380f5d467cd8ac0f723ef8ed6e53861b4d046cda4df59bd4daecd57(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd21b0ddcbadd605893d2851758bf0a610f88894eee37f2cded0a914cba61fbf(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__147cedf88e80a64636724d0c46ea77e5bb84d17e700df8ab1865543f9718d8b1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2bd59b99544eae730076de80b0770747fedabfba6e401e92b1a39814b004d00(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7495737521159bf49d8855416475c46ea5af2300ddbfff66d7dcde88e8b7f49b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a96f6a285056c2bb212a117698802b8a846eb2501953cfc75e1f37a054e2c6d7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ebb4fee35c18132097bf26c0df7a956fb0098ea319356cac1c5b6cc75e61d22(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e8e3e4a902d1b91900871448017681398571c7401aecbdf93da98e62d46c405(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f0c8e1e6608e87d6c94008a302c15561abcf3f3b40f3b032bc827f6458c291c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__628bf359c35cf3c63961773b1b62979512106d1e3987e320a335b15c3d9ec2a6(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da821aae1153908501029237dae3e2d78071b80ce4607c274d7191faf6448710(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5259d9cd96c68c36876f2687f2f1d78ccda4ae46194650791af5c997d41fc6da(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed9c4eff81e28a3c887802c07e72393225f5fcfae5d0901bd26add18adf1b0d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd56a5958fd2e6a168f782281af987cd6e4391206291cc8bc17d013c50df509d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e3d83057392708f39add5cccf856ed77b628b9c608d2113f84a706df3d1ab77(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c06164224053f674b4f492bb18a5e4336639b4c94e822023f4461edd27d9244(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ff2cabfa0ca4f4de175599ec91c16cde5067ebcac8b958a6913143dedc4daef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea387be8a69525a7f952fe36b4853a37fd0a88b0757e83c6464b9fa07025b66b(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edda1c0ea9240fa3d9fbecb3c0e6b2375b561e874aebdd9a84dcbe0eb41cecfa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b42c874bd40d903fb5207ff96c6d937b76782f15869a36f1ff2e303f31abc5cd(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__118e08ea0644ba65c9d8a964e4b615a1a1350325e2979fc2b86feec27075154d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30ea8afc9e6733ca3f937f992e64ad964f2612d15b8289a8b35d9f866fcc9ba4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d8968dbd0708f593bf1cc20b5146b30ed7623fc04927de40fdaa7279414da27(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8277a93d2bcaf1e9f630c2916d037e67af5fc53fb1fdc1952d58687eb82c3d6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__963bf5f37c160f28eeda629f9c0d686931e8986958f0c34d8f5a93c261741872(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a701d1cf0c1dc983bd8ffd78b4842a66ae3716b790fd33e659d0bbb2819f1bd3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee1b137113dc233d8bdd09d64c147c1a1169f689c197e7c34409a6519c8ee116(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f21fa8e02b935ea7d677a232fdeb5b8ee414ab23536218de7ec2283c63ce6a61(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9e748bf5229ff12a7d2bd962ae31924cccfb89f23581804800b3015773b8e5f(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eed26d1dfbbf066d5ced1ec06618803af618e907ef7890ed0ca271138704c6b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df8b80b6fe3cb7f4f84c67085bbfd5aaf6ddc8ad98c11010bd4e20171126282d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cf8170374c6e120a0b9919dad58458c4c6f7696caf67aa2c4a6854e1d7c4eab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abd2f5189fe7d28ab2a4bdc066bc383ccbb6906fd3a2a67b29ee096b8bac45e3(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefault],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c0a78ef63d3f276807e8dfefb6c081b527841b26f720cd615f14f8f679d6b27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b08449a430789ca56ae8584aa72bc8c786c182c310991bcac8fe39416863a7a(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29d09113d3696f7dd577c57757fca4c24b8b65de5eed61fb437627bcf7328c6c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c16d6b319c4f4f00c19709cba65027fe2cb5a17d2ba5b5e016dbcb56c1ef45a6(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupIsDefaultServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2b82e2d2c76d7835968723c9ce90a4cef23938d85971080b3430fc72ae00dc3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25709ddc7553e0a3b8a9d3da4f799a694a420e2bdd09ae927ad552ea068b45f2(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a79169ca98e279541e131adf7df8f54c044631eba2d99867e8383d612bc70db(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df1bf4bd7d57f8b570a8e326f9783fd35a70b2fbdf8f8e380d9e91aa531f5b87(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c4d248853ea1800bc87b6b2daef0f5dcdbb36992bcf7508b14f712babb77389(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f8128d1c21987d16646962dcf53cfc251d1302f6c2dc9802c20cb9081cbb9d5(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4af48b8a6a23525f97fb456ffc56fe0c2e91fefd26d23b72fffd1e3656c0aa1e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ccea7d8ca5ee0dabcd6bddb757bba5375d11decea9d55b598cd09d217b891ba(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__465489f6127fba06ceb2add781603be747fcf92789902d194a578a334f614533(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa25326d8c1bdc2272cb02a4df7d4f2d21ceec7627cc657d1ff7c1c678dbfabd(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd07ac65bd8e915ba590d52777b30740dce6bbf961de9cbf637d2a27f0f84837(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c26fe5ad6913bc81c704db19588896d8dd3d010ca27fe88e262c2b395ed0e6bc(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d06510ed9d8986c67b34a5d870312e393927dbddd3f27a40ca70f818f9d4db1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fbef6681f05d0f11f880de902f3923e66ed1f3c5e4e01d53a3f2ec0aefa16c7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e68a2a240f66edc314004443967526ca7127a97701bd5f5fb06988871cf939fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4acfb20df3497252785c3ad4c3a373d0be268f48c4f67bcc8f5681601ee8592(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75509b6e03f0ef1179e2daba438c42c52f6ab9a300b3bd0f012e8c1d638892d5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dac4abaa72a9e63d01110e8c4acfbb0fcd2913a579f8c0513c78e9215fe8f072(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f15310a8631fdad192dc362fb346a1a9c1a2df92aca9a42a7bedad5d85b234f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f11c02589b7a2e30548e60c4be62978dfd89a797acbb92382b9375487613fb52(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__677fcdb4fa7b2725260df175f5c331073e8444b3b8ec7ff24a666be8f3b5f3de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__885193a98c44f4868dc47cc71bcc88f6fdf336219d191f7468dd9d9414d9c318(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bbcf6a523e42ecb21da280276f41ef52613825f710595c64764a52017802277(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6073c7b96be243d249c2ca2bf5f725cbfc00bbdcd3df29dd58084ff9c8ad8ac2(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c24fec7de40d55e7eaf4825dcb9a1531730d006ff4e3505fe8197d63fac68f0f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b8f8060315bc9b418fb690216b140e43335edffc9788a433b723f424eeda7f7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b03baa0a65aa3d71feacbbf7ffdb4faec62989591a402870f9944fff087c90(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2adcbada2225b09049ea8b93baf5dc6d23b886a25fc802aa35059b20109cf3d7(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd49fad87dd0f654bb6a77b97c933baf637a0dc24a6f2c781b5c092a49b881b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd16e8c4f1da8b4405dfcd07dd799e5285727f00825db8fc2a44edf0d86aa59f(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67407f39f61bcd72564e10267f499600ee477f82ea6e3e7d1653a1f30182e8bc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be8c0b128ef56a5d48c4b9a2f9f121a27fda01372e908db08557c6a05e3fc682(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d353463bebfe6cc8c8c6af662ea395fd486178913d7a60fbd715567877da5c0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa2c1d47c86c7696d8abe71bf1685aa33d0b2d93305d1b5972f9052321fa9bba(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6719f3bc52e8cfd2df7651ffa90783fb066ec6fbd11e8837c9ff7d14c4eb69a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16474e16481b9a0488d27238ad20b45a924fc0ea300ff8858ae9bd4734b88427(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc34453d5e52bd3a4d9987378e34b45e10a3aded3bb256a59284b6e38e1c14e7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__409175e066bbafcff516543ced543073a75e74b1b80a86fad448bcf3abc5af87(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae0c04074c66c9d32cbe1bc9b4f7a5853acdd6a6424fcbe8432daf04d0895f52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__247b6dae3474911f1321556b26cdd3bfc45c9ad7d65e3a327f23acc244c74129(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19649a0bcb58ccbf4ff2d0b6d0496fc0f43e1d70e639b3d907eb75dcd82ed351(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a973690702084fb4fa276d878d21d46f4f0f6a5f0d49350b7415ee636bdca12(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__474d602df21fb419a4c98d8e7ceec0febc248078f9fc214047bd7a429e77ab33(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be34559995302938d5ee3b90fe3ed7582010efac61d150a3e95f9da1da30f2dc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74876c99a5d910d5fc2092e65153862e08daa69fe02e0ad448b79be52f749b7d(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef072c04c872a1db87a2530eca1a3122dd6056474ace4c06242043ea8a5d87d1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f79deb007bf8746836b5d659fd0c87c4736eb893c6df81706a7528ab953aa24a(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85e42d6fd9c61eca563aade45a2ad92a11654be222ccea79ab72362933d03925(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22eb163be9c11a1e006bd9cb1e2a372a8a04e1512a8e80409a7e0e8d2d8f5490(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7981dc0a893ed774297452440ce710f66d23ace594eb00b5555187eb2060a37(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d17a4069ae764dbf58e07baabd8a9873419d904c85284ff745c06c5439f2f023(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequire],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90512aa3924754410536bc7f6e97f207883c3aa32ca5615bfc6dc836335318ce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5da2bbb982bc16225a32413aeccd0136a90763958c048eefdafcd0203143dda0(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8074d3fe677a511a3188193456605091b13f7cab5557528c6908a7bbeb6ed08b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf24b40717c6e867d79125c4674618b05937ba3db5a5131c7c7070887a0d4519(
    value: typing.Optional[DataCloudflareZeroTrustAccessGroupRequireServiceToken],
) -> None:
    """Type checking stubs"""
    pass
