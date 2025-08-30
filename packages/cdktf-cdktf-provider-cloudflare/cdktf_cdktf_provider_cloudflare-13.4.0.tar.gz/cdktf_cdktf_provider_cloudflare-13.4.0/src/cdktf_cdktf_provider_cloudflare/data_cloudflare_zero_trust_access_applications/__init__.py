r'''
# `data_cloudflare_zero_trust_access_applications`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_access_applications`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications).
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


class DataCloudflareZeroTrustAccessApplications(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplications",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications cloudflare_zero_trust_access_applications}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        aud: typing.Optional[builtins.str] = None,
        domain: typing.Optional[builtins.str] = None,
        exact: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications cloudflare_zero_trust_access_applications} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#account_id DataCloudflareZeroTrustAccessApplications#account_id}
        :param aud: The aud of the app. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#aud DataCloudflareZeroTrustAccessApplications#aud}
        :param domain: The domain of the app. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#domain DataCloudflareZeroTrustAccessApplications#domain}
        :param exact: True for only exact string matches against passed name/domain query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#exact DataCloudflareZeroTrustAccessApplications#exact}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#max_items DataCloudflareZeroTrustAccessApplications#max_items}
        :param name: The name of the app. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#name DataCloudflareZeroTrustAccessApplications#name}
        :param search: Search for apps by other listed query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#search DataCloudflareZeroTrustAccessApplications#search}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#zone_id DataCloudflareZeroTrustAccessApplications#zone_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ff3771254b8ba08ffaff62fb08c4fa424d6e52716cb187e953448a9426ab5b8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustAccessApplicationsConfig(
            account_id=account_id,
            aud=aud,
            domain=domain,
            exact=exact,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustAccessApplications resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustAccessApplications to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustAccessApplications that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustAccessApplications to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60466979d23ceae4e9baab35cd32a62fd0cf469addeffac38a9a73f1ef01b624)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetAud")
    def reset_aud(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAud", []))

    @jsii.member(jsii_name="resetDomain")
    def reset_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomain", []))

    @jsii.member(jsii_name="resetExact")
    def reset_exact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExact", []))

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
    def result(self) -> "DataCloudflareZeroTrustAccessApplicationsResultList":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultList", jsii.get(self, "result"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="audInput")
    def aud_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audInput"))

    @builtins.property
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property
    @jsii.member(jsii_name="exactInput")
    def exact_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "exactInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__e0a66ac112262ee717e3dee43f661568ff5af6e72dd508e20519f595ba094557)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="aud")
    def aud(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aud"))

    @aud.setter
    def aud(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c385e03f38f03c26366937776c9d0c1f75c6db3df49376399b4668f3a74456d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aud", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3964e49ceddc58501239640a8211edd36c8b46d0c6114763cad63c66f08548e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "exact"))

    @exact.setter
    def exact(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d9fe33e8a0822cdf46f80d22074103eee7e6a39c1a2331ae45163e6e3bdeae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxItems")
    def max_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxItems"))

    @max_items.setter
    def max_items(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__286f99d9127186f4fbdd29c234ffe605ef307b86663570fe669e6f46ae51e158)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxItems", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__843df41dc744476032495b77529bc7fd7705aa5cef4541abac4f4f3d73afcc76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="search")
    def search(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "search"))

    @search.setter
    def search(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93c1cf463bd51bec464a70b8bedc919b1a2de4bc96127194d97959631a7d64c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "search", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb92fab3569e8bc784c496119269161c766afa32300a82cb4c4f73317a03277d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsConfig",
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
        "aud": "aud",
        "domain": "domain",
        "exact": "exact",
        "max_items": "maxItems",
        "name": "name",
        "search": "search",
        "zone_id": "zoneId",
    },
)
class DataCloudflareZeroTrustAccessApplicationsConfig(
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
        account_id: typing.Optional[builtins.str] = None,
        aud: typing.Optional[builtins.str] = None,
        domain: typing.Optional[builtins.str] = None,
        exact: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#account_id DataCloudflareZeroTrustAccessApplications#account_id}
        :param aud: The aud of the app. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#aud DataCloudflareZeroTrustAccessApplications#aud}
        :param domain: The domain of the app. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#domain DataCloudflareZeroTrustAccessApplications#domain}
        :param exact: True for only exact string matches against passed name/domain query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#exact DataCloudflareZeroTrustAccessApplications#exact}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#max_items DataCloudflareZeroTrustAccessApplications#max_items}
        :param name: The name of the app. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#name DataCloudflareZeroTrustAccessApplications#name}
        :param search: Search for apps by other listed query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#search DataCloudflareZeroTrustAccessApplications#search}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#zone_id DataCloudflareZeroTrustAccessApplications#zone_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fae49596d00e4db3452dc71e9de8cba76f54daf3747b858206c7890d81537d0b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument aud", value=aud, expected_type=type_hints["aud"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument exact", value=exact, expected_type=type_hints["exact"])
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
        if aud is not None:
            self._values["aud"] = aud
        if domain is not None:
            self._values["domain"] = domain
        if exact is not None:
            self._values["exact"] = exact
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#account_id DataCloudflareZeroTrustAccessApplications#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aud(self) -> typing.Optional[builtins.str]:
        '''The aud of the app.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#aud DataCloudflareZeroTrustAccessApplications#aud}
        '''
        result = self._values.get("aud")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''The domain of the app.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#domain DataCloudflareZeroTrustAccessApplications#domain}
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True for only exact string matches against passed name/domain query parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#exact DataCloudflareZeroTrustAccessApplications#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_items(self) -> typing.Optional[jsii.Number]:
        '''Max items to fetch, default: 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#max_items DataCloudflareZeroTrustAccessApplications#max_items}
        '''
        result = self._values.get("max_items")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the app.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#name DataCloudflareZeroTrustAccessApplications#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def search(self) -> typing.Optional[builtins.str]:
        '''Search for apps by other listed query parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#search DataCloudflareZeroTrustAccessApplications#search}
        '''
        result = self._values.get("search")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''The Zone ID to use for this endpoint. Mutually exclusive with the Account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_applications#zone_id DataCloudflareZeroTrustAccessApplications#zone_id}
        '''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultCorsHeaders",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultCorsHeaders:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultCorsHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultCorsHeadersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultCorsHeadersOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8145575df6d0d29a35ceff44c530d5c25a53256d3d575a1876d3cd937773b57)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="allowAllHeaders")
    def allow_all_headers(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowAllHeaders"))

    @builtins.property
    @jsii.member(jsii_name="allowAllMethods")
    def allow_all_methods(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowAllMethods"))

    @builtins.property
    @jsii.member(jsii_name="allowAllOrigins")
    def allow_all_origins(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowAllOrigins"))

    @builtins.property
    @jsii.member(jsii_name="allowCredentials")
    def allow_credentials(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowCredentials"))

    @builtins.property
    @jsii.member(jsii_name="allowedHeaders")
    def allowed_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedHeaders"))

    @builtins.property
    @jsii.member(jsii_name="allowedMethods")
    def allowed_methods(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedMethods"))

    @builtins.property
    @jsii.member(jsii_name="allowedOrigins")
    def allowed_origins(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOrigins"))

    @builtins.property
    @jsii.member(jsii_name="maxAge")
    def max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAge"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultCorsHeaders]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultCorsHeaders], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultCorsHeaders],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7ef5a73b75202e70c7a20643d9fbd431419b74344055619e73403ef5c248470)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultDestinations",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultDestinations:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b9ad2afbb319479afc3a7d6bb366d22815ce747afe2cebd59283a1983ca6d2a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e00a7e7670af183232cfdf6f076f56bea61ce0cecc715edcef2aba0d06f964b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5acfa2cd2c0ce5058a8d64027641fb31a6655ebddc0994d6e8fdb34b5bfc76ae)
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
            type_hints = typing.get_type_hints(_typecheckingstub__315e897227d4039c268cf4d41169d05d74b9fa3d33315bc555d862f4911c8094)
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
            type_hints = typing.get_type_hints(_typecheckingstub__06a87d47346cf0791889b1aac3904163cae18e51ea27bc867c8499863ea6424c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__10c7e4097a27230822bf08174ec9887a7ba0b6b9ea595f169873caebe247f5d2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="cidr")
    def cidr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cidr"))

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @builtins.property
    @jsii.member(jsii_name="l4Protocol")
    def l4_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "l4Protocol"))

    @builtins.property
    @jsii.member(jsii_name="portRange")
    def port_range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "portRange"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property
    @jsii.member(jsii_name="vnetId")
    def vnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vnetId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultDestinations]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultDestinations], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultDestinations],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2677fbc0f6b4da09e72a4d49612c48e02e51a4a393dba0efb194d9893365b247)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultFooterLinks",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultFooterLinks:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultFooterLinks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultFooterLinksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultFooterLinksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7fb8825065eb1fb0ed3f866ba007a49adf5eb74c25a8cf42432e0c76cac5cedb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultFooterLinksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ab5aa962d73513549d74b3d6ac9cc836afb9f915bbd2c86351164f2b7f5a41e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultFooterLinksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cb37e480f3259b1a7657582419f539f6ca54dfc08b3ed5808c1dfe485cc2137)
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
            type_hints = typing.get_type_hints(_typecheckingstub__af923b5813ff8fb9ded22e20da496944ac0df45589de65685b68dc54ef7e8a05)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9eda3f3637becf337868a86e6f09dbdfe372a2d4b9eda07da353c7969f59db8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultFooterLinksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultFooterLinksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__59f8612f6d1778dcab2e57d4d7155f5cb2534f5d6831527690a6387e8807a1f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultFooterLinks]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultFooterLinks], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultFooterLinks],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8fa842c824919528fb06f82d7b0c907395ca8e7f01ddcddcb47ada263009600)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesign",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesign:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesign(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesignOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesignOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__738fdd54d0b8ef004c0752d15067d78cb492d3c85d51f717ff2f5c1a8e127793)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="buttonColor")
    def button_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buttonColor"))

    @builtins.property
    @jsii.member(jsii_name="buttonTextColor")
    def button_text_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buttonTextColor"))

    @builtins.property
    @jsii.member(jsii_name="imageUrl")
    def image_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageUrl"))

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesign]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesign], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesign],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c5c56209b05eaaa6e95477640c0fc9e477b65a946607287db534f8204622865)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce710c0a914ba143b7250440cee8d9b0b1037dcb1d18d096472c511e55296d37)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d7ef214529b3f37555fdac6ad538b82b51e405b460af572ce6783030f73774b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f256570141cff0790a5cc43b8195846275d418242457ef282ab691f9725dda9a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5e0ff793b866899d5210b552801856f9600d470c567b76773a77c20d7d080f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__de415919334bee3a780ca07b5d9de68625bb8d7615236badaccd655e5101e896)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cba4ee94df3d215f8e78c2487f825147798f5a06b4fcdabb9ec3bd2ee43b1ce5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="allowAuthenticateViaWarp")
    def allow_authenticate_via_warp(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowAuthenticateViaWarp"))

    @builtins.property
    @jsii.member(jsii_name="allowedIdps")
    def allowed_idps(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedIdps"))

    @builtins.property
    @jsii.member(jsii_name="allowIframe")
    def allow_iframe(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowIframe"))

    @builtins.property
    @jsii.member(jsii_name="appLauncherLogoUrl")
    def app_launcher_logo_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appLauncherLogoUrl"))

    @builtins.property
    @jsii.member(jsii_name="appLauncherVisible")
    def app_launcher_visible(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "appLauncherVisible"))

    @builtins.property
    @jsii.member(jsii_name="aud")
    def aud(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aud"))

    @builtins.property
    @jsii.member(jsii_name="autoRedirectToIdentity")
    def auto_redirect_to_identity(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "autoRedirectToIdentity"))

    @builtins.property
    @jsii.member(jsii_name="bgColor")
    def bg_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bgColor"))

    @builtins.property
    @jsii.member(jsii_name="corsHeaders")
    def cors_headers(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultCorsHeadersOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultCorsHeadersOutputReference, jsii.get(self, "corsHeaders"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="customDenyMessage")
    def custom_deny_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDenyMessage"))

    @builtins.property
    @jsii.member(jsii_name="customDenyUrl")
    def custom_deny_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDenyUrl"))

    @builtins.property
    @jsii.member(jsii_name="customNonIdentityDenyUrl")
    def custom_non_identity_deny_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customNonIdentityDenyUrl"))

    @builtins.property
    @jsii.member(jsii_name="customPages")
    def custom_pages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customPages"))

    @builtins.property
    @jsii.member(jsii_name="destinations")
    def destinations(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultDestinationsList:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultDestinationsList, jsii.get(self, "destinations"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @builtins.property
    @jsii.member(jsii_name="enableBindingCookie")
    def enable_binding_cookie(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enableBindingCookie"))

    @builtins.property
    @jsii.member(jsii_name="footerLinks")
    def footer_links(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultFooterLinksList:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultFooterLinksList, jsii.get(self, "footerLinks"))

    @builtins.property
    @jsii.member(jsii_name="headerBgColor")
    def header_bg_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerBgColor"))

    @builtins.property
    @jsii.member(jsii_name="httpOnlyCookieAttribute")
    def http_only_cookie_attribute(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "httpOnlyCookieAttribute"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="landingPageDesign")
    def landing_page_design(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesignOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesignOutputReference, jsii.get(self, "landingPageDesign"))

    @builtins.property
    @jsii.member(jsii_name="logoUrl")
    def logo_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logoUrl"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="optionsPreflightBypass")
    def options_preflight_bypass(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "optionsPreflightBypass"))

    @builtins.property
    @jsii.member(jsii_name="pathCookieAttribute")
    def path_cookie_attribute(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "pathCookieAttribute"))

    @builtins.property
    @jsii.member(jsii_name="policies")
    def policies(self) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesList":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesList", jsii.get(self, "policies"))

    @builtins.property
    @jsii.member(jsii_name="readServiceTokensFromHeader")
    def read_service_tokens_from_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readServiceTokensFromHeader"))

    @builtins.property
    @jsii.member(jsii_name="saasApp")
    def saas_app(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultSaasAppOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultSaasAppOutputReference", jsii.get(self, "saasApp"))

    @builtins.property
    @jsii.member(jsii_name="sameSiteCookieAttribute")
    def same_site_cookie_attribute(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sameSiteCookieAttribute"))

    @builtins.property
    @jsii.member(jsii_name="scimConfig")
    def scim_config(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultScimConfigOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultScimConfigOutputReference", jsii.get(self, "scimConfig"))

    @builtins.property
    @jsii.member(jsii_name="selfHostedDomains")
    def self_hosted_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "selfHostedDomains"))

    @builtins.property
    @jsii.member(jsii_name="serviceAuth401Redirect")
    def service_auth401_redirect(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "serviceAuth401Redirect"))

    @builtins.property
    @jsii.member(jsii_name="sessionDuration")
    def session_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionDuration"))

    @builtins.property
    @jsii.member(jsii_name="skipAppLauncherLoginPage")
    def skip_app_launcher_login_page(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "skipAppLauncherLoginPage"))

    @builtins.property
    @jsii.member(jsii_name="skipInterstitial")
    def skip_interstitial(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "skipInterstitial"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="targetCriteria")
    def target_criteria(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaList":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaList", jsii.get(self, "targetCriteria"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResult]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f3ccf301183b1e57edf5da95b5bd05be07af0c48b45962b354da6f26af24792)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPolicies",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPolicies:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroups",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroups:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__89e72aaf4c3df92f02c4c12942673053b2e04744a322d732ea46ca2890f8a32e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b931743f1252c21eba92cc11a68864073ca36565e3aa9de11be40153857e6350)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f926a98e94bd330597d0fdf14225a0c15b222e801f7fc12aac4b89126b4fad8a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__08eff9b6a768c0245f66c84a7c60520b3280974623dbb8f256159b0d36936e0b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ec09a46a4798beaeb265f7052cb98a2946352cf5c7e6afa185666690aa926fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__acabc5c9254258666060fd4225c17c54a8f4eeec41c6c37731981d774f233527)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroups]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroups], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroups],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25214386d6b07bafaca81ab056f341ebf884c39be8d55fd95642f38120c3e014)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRules",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRules:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db3201b31650c1b3fa51f2656adfd932935ef265894e222f2d74c94d1e1950e0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ssh")
    def ssh(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSshOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSshOutputReference", jsii.get(self, "ssh"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRules]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRules],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff0854f0d34dfe78b578d980059533fd679115b59991f8af47697990bc3b8dbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSsh",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSsh:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSsh(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSshOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSshOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d6f2c417ee15f4d4b09b6f444479ccbcdb3ee18bb905988f98461767440fd38)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="allowEmailAlias")
    def allow_email_alias(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowEmailAlias"))

    @builtins.property
    @jsii.member(jsii_name="usernames")
    def usernames(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usernames"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSsh]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSsh], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSsh],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__968325158a527a9580752114901481621941d428d2eb36eeafab923b7e1ebc47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExclude",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExclude:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceTokenOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8aa442ad61c445eac4d83f502e0ea7618b2b617d4b5618004149b60b9258eaf3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5741cebffc5888f88732e85fa73c34de30bb91142e5ae4a31c57a51ba5dc553)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContextOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5de4e61a2a65947080bfdc3d590d0b3ec8606f86a00a345c94f46c5389536359)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20c0d48e6a553c4a6112cb5c23c6f097361286d06f8b38f8f85f75c7157e223d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethodOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a631c411afea76394535f6f28538523d5c60a0e4ffa8f4fa9dbbe30701ee05e)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b46a0d1ab936aa525209034653e22ebfd322e5fba5051681df005710c14d90b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAdOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6643907d55586af18a5b8050982274e0336e54ae9711550bb3caf41ce42c2fb0)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__764e01fd1a34801cf0206d414f5fd607c96c96a64b0fa63ba0b2db8cbd6772d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificateOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cab548d01a4937b054352ec0c66d97b059802e9973e5d7765f025814573fc26)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d2562cbb5790dc16c159430b4bf65fff19e670b930b5675927d36cfa98510a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonNameOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1d551f5daa31d14747a8104097e4183d2b073a50da2cb546d44e1d9c0f35e59)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__700b9bf39eeb1525572d1959e6c3c98bbf286c97fc5c720c5a27b83ed86a5857)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePostureOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cde8481909cfcb562b164a045bb861fd8baae70343656351f3acb29b5ee13b9)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b224b543308cd024ce6a4ab21cdaf208349831cfda7c9d85e015c22e4f579260)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomainOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b0853339001a6c5fd79255c6a79187420d59da63a11bce1dbd916f7781603c1)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8002eae3a45640e4996916e295a9148012deadeb850cb5ea5bae19fb8bfcbe8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStructOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d602488b3aafc9846866ba04b663869bd0d8928901dd0e6394552eb977bb8739)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0d7fbbe7279c7115ad69e4ff4a13cc36e2d611816074bf59dc54b2aeb14600b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd5ad530c522612ac69c2af0dee6db3eaca05594910e3037c854031907721f65)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a287bbefbc47a41092e923d48b8ff073ec6c0cfadbaf2a9f3b8e4cef8b6f9055)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryoneOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e6d0adf4f2fe405ca6136b84e63b59f4dff54e3d901b6bbc41081bb70f60006)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bf76580d52bf760fbf7fd7cfae061e48c360ca43361ac871f567bdac0dda364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cd94f9b62c448210d38274bd8fb14f668fdda247fc554ac8a9564cf06697b1e)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a7ac51e5aa02f19374d0452fc6d672f522fc5e1d3ef1e623e59fb1c9d5ec540)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeoOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62f56ad9e9e0a15d640baeca9c5c26998d4029e98a2f53ede0fbc4d96ef54f27)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac90eb55ea527571eb432907145b9c4629f27a098d4a6ac2f2527fc3b858ec5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganizationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f82066a468a5c111f7ef2461fd8be04860e98fdb1002e473986e54cbb30461df)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce37dfe013861a5046194e1fe87e8dcc19f5600cfa70832140970b06f490ee88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroupOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b482592e1acdd1512a4ee4699e5020d48963b8db7bcfcde2247696155d1b855)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f515149159e6e30af6ed833057d280117619d4f81ce699430c8092c84ee9449)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuiteOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35eeb1e269765d3c1e2069cc461cf344c30862e5d54ad4f5767de3e5a1dcc443)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f98cd58314a9ff69839e42d9e4ba9b4fb593cc7ac75e5bec3c01d99cde793064)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStructOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26c881b21d7790c2de50b7e81102cec8647eb68ac83193fc5e74e62c680f4aeb)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__077f1a1cfed3676fc59832f10d4b4b9c9a0b2357c97dcf3295b0336167bf83d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1f303a8a5d653b0b1f7a89f5223f54eec8f83a297a9aa3d32c21f85960b7dfd)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0a361bffe7f634e6630b2af7710159a0d0890c67fd697c7d809722aaab0a5a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppTokenOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03d23b59eee36660259782359f2d7a74588293c36d594c33cd7920b3d84a9bc3)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ddbfd14e8b53cedad4fc1517b2c03cfb562371a3e7cbc82efbdbf42b7c81ef2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3cdee223b498e417e1ffd44f6cc4688ec68e7269a9c730384d5723a84e648cf4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23e9f677cabdb675b21198d6df9e4da62358d541131e9c9376b5a81ae0fc9db6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9eb502446b12176da2f60b201f85072958a66f6986a965281ebc1d10afb5df42)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8bb5020a3d0aa3333bfce20e58f04ab228ea5a032a956aed72783fd1b036194)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e6e9782ced2f755be07c0c1f03bdde772649705ac1560a0462b236ce8b70d6ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethodOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aef07d77a0e0c3dda3dbd5b411146d08c6c728e9708ebc02b017dcfab0ada99)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b9198f56348aa33259349f358d45e25d93912e57ff44f8b1dcd1ec55fbcf637)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidcOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fa5a55762e4c615e6d8afd28b9e314c4785e7ce1f1b7fa2581616e3f166d253)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8416692f6ee6f729e68920cab0deaa63725282d73a3d99968a12feda82a79cfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOktaOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52ac0fe6992750a79e77b92be95d78490623d0989c1a4d4bb2f9f6687750bbc8)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2223092dffd46daab435ee1adb9c87f29a0c4caa25d072db222fa9a88d6e928)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7e6534231cc380e527f0131acb93402f575da05ffd54050d4f818d3806e666f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExclude]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExclude], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExclude],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfc1fe07365c43ffd67606fc291cf5b7479dd4d36bf3f37afb19489ece4f37d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSamlOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ef11aa1c6e40c5780e1485417ebb16bad7ea90d46155dd04695654340ab183c)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9757681992468f768b4cf8ec933830ad7f3fb03ecdd5528306121fa4adaec30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceTokenOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25ac1797e1c3e328a4e1ef1c56fa18e6ce30b22ab02157000a5bb62a041f8cff)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b27f93a60252d117f156721acc6317e9b443d6a97e78ab4773ea9727e0752010)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesInclude",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesInclude:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesInclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceTokenOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__031315bc5459f182f1083eaaeeba8713fea0b1a5ca4aa29fcb13942d7972924a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dba43e51befe3ea07155104fc3ef2ab4e2dd749318847e53a2e0646cedd9bd1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContextOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83fb653c0a5d6dfbab4b4fc981eeabe621bd5049077b9c730471918da5ac230a)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7211dc6e0091b87bb38d4c719f72a59ddcdb682cacc7268902f702ebb06bad5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethodOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fbb70e21ebe22022878331fc829491a98377b8bba411205f9668bd7fb94b8ee)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__157f044c29ff3999692f89cad78e3f77fa61ac3667c4301a61e3a64096a91e1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAdOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4658fbf4fbbf0bf6f9c6d4e971e4f677856f9c8e447925fd17b61f5e8064fb1)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd4f3f8b055d20f8ff217d0dace8d38b24f121c499d9885ed7fb0cc4accbe974)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificateOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b71cae12b64bc45f575f277cd8f8ddd6d4506bc32338fc0fd7fd850870940ce)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__126bc2c9bbfc92340545e10a3c9d8db481bdd2ab5092ea00ecae9f0e2f72c094)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonNameOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6e4c73569ffe63d8aeb85ccbb946d788d3f17ed9d16fa083751eb9457bb49bb)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__847a10a5c743e01cbb9ae9401ad4b1938c0a0660d80bea324b4e1ae8a6a5b4d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePostureOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080824b6b882e42921cf199b33ca3d8b1abbef7d8b4c1d7a2c76cb1222df6950)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2507b5f3fc70e0e2204b53e2a4b22b64352cd2f73cceb6815bf894ca4a5b576)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomainOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6807a1795cefbf4d84d96e02cbf5c857f573ad6542c8f519ddd1d6eb16e15fc2)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42b63eb7f699cad177e3ed0929b15b3313cb48343952f12939e5531e078037d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStructOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cec1f26099351dac442617d32833d14f24040d8196de010a9b7799d95c67911)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09518cadc75dd075542b5c637497049679a77e3e6650ff41c7de762c5aae40cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a40bca7a0f6ab1c2b0c7d54b755dcf0cdae96f5429debb170fa13d7d66d78401)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7421287c1467a2151783b3e5e61a340f423be9d6ad3e4bb035046c8461efe04e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryoneOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4abf3fc7c7b9570012ee85a9a0b894dbbba5150264e796cb7c61f187090a8065)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a4f25db12d14ee6909432832422e5421e53f82701529a1784cb07b1ad83317e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__164e29868185010617150eaf01bb9a6568ffba5d00abed45e46726d4011bf340)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baac8a9be7540e0424783673db7f1ffa6df961f33b131708db0ce80e17793470)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeoOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0635131668f44d5bf9a5515d81b91006c9a7b061f1a28936d2f1213cc6847d5)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080750a6b0371ca0e683d618e20163c9508ea5d54229f5167c4ec35e80b12138)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganizationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aae85c04cb405e5080318b747368162fe14d1de4a44b4c3a70576ab964534a73)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ea3b7ea2ad0f7ab215f634b3cb47a4fa321fc5e61293a5b5da7c2fcce0eb841)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroupOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89f673c726cc33d0e90a864e85681e38028a153fb9fe3b048ed76afb05837699)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b375d32c8a4a5a591ed36a94580bbe4d2832ffa2905c8b61cf5f3a7f4488e29b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuiteOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa2facbda86c77a96e1d8d9254c83d8a423750c3d823d271e7580c0156e246b0)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2f6c340534f1f214d4e6072063818a6b481aef372b9e5bb8e1f5b3e4b78c06a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStructOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6b2e12dff2a84025c02701e11cc201e8a73ed4796312d32bb4ae6f195d06dfa)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__812df8261c592b2e109a74adbb0194d37160c0971335c71c2338ccf16ed906d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3fe21dc355eaf66780c7954dafe73bd8adc52b2e601dac18f8282d6d88c2368)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2784502b551c1a65524b8736a2e5680b192faaa94c408ee8068372b820ed0dd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppTokenOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c1c68b4b5a3127ccbb3c1489251a56827b8e6a23479dcb0794bd686d37bb2ce)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d46ea4dc9d2787ed33e1d88a19bcc82203fe81af55067faddc2238c9c202add1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__56ead0768904b1b329573ab5dfd46f4511a53ce75875de219a1230af98d9e748)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2abee5fed0f48c92e35afcab7992e5b6d229228d6a6c89f19e284908d9a2082)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9cb8bcc60f1cbcc8234383156850ce097b5a0d2d7a73384e559750d8e07b498)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2aaffcc65dd63a017c528c456657a63d8582ca4607eae70185d48a2659065373)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7619f2b194e81c2f64621019639934e84433a09e5ed46a9aaa93dd68bffddf6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethodOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f50eea03c97d14528a4e1bc8bd0078e0315e9b28537c7596c02aaad7b25be89)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5e2bc2f924744891f6530b7556294964e2a7227095f5f8d20150dce7e3d1e23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidcOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fdb3a1b4803cc9124057d1b0ccbb20d258ff60cf5b2510124aaeb349d8930fd)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b894093be7f34d35a19585606f88edd79edbe12ff421fb17242b5732088f05e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOktaOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c281c8a77840f4cf841565c337ac020c619317d01a207ba989f224e22c2bfa10)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad7c0c9628d102c75cabe8fd69634e17705fd7021d45b04e3f0db9bddf148cd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a5f45a00c6e1c913bc0de56a65346c8ea88008c046a930534b32d6deff24072)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesInclude]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesInclude], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesInclude],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f90dda4ae4453cc29ebc0545a6b399399319632fca87573d9ec7c6ed5b19fd8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSamlOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f762bae572e9048bb03307286102f28f9b2f31e076bfcf8bc8c60e7cca92b22)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6b9b1a02e15f616dbf55c7a9fc72c47e49ae7d035ef66487d5cb203dece718f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceTokenOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b1986fbfd33fe49ef7df88ba004731f0c87215b31a00e60bff2b0eda6dd8158)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcb8e90f60b0c263b6e03a6800bb0c08ee86085fc03bb49d93b4b227b8a0c1cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ac12fa3ce3b709247caaa17c53e772cbd58e17e0c26f558eb973dc2592c2642)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b60526b0f7b4e440fc8c1e91d65578a9953ed7f979385efca2f9bdf1bf3978b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fde79744423805a41c12fcac8e87e096786ab871c38fe48cf1644461a20e485)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4b17e9a4d42db257d3b3dbf911ad2cf0ecfba3683f420794c8750087336c603)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7468911c4255074dc623bf051773004bc5b04e62a338bc3acc61baa52a303be0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed6da59e337f0d64d266e1dc2a989680cb2f960a38337c48b5867137117addfd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="approvalGroups")
    def approval_groups(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsList:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsList, jsii.get(self, "approvalGroups"))

    @builtins.property
    @jsii.member(jsii_name="approvalRequired")
    def approval_required(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "approvalRequired"))

    @builtins.property
    @jsii.member(jsii_name="connectionRules")
    def connection_rules(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesOutputReference, jsii.get(self, "connectionRules"))

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
    def exclude(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeList:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeList, jsii.get(self, "exclude"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeList:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeList, jsii.get(self, "include"))

    @builtins.property
    @jsii.member(jsii_name="isolationRequired")
    def isolation_required(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "isolationRequired"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="precedence")
    def precedence(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precedence"))

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
    def require(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireList":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireList", jsii.get(self, "require"))

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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPolicies]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPolicies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPolicies],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3969a946e36cc736207ff92eab6ef524156d9b4b5097d5b538216ce9df137677)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequire",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequire:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequire(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceTokenOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ed69a4d97c976f4e08a6ef250fdaea17cb7527cf05f94be302d8f43098c5c86)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c98dd324c8790f46cf6c00f9a3e3d33db732dca31aa3806eae2bed845d21a5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContext",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContext:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContextOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab705c15d8fcf506111a89e335fc7bafd133b336aeeb776f4ed14f37ac27e89e)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContext]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContext],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__261259572fa66c9aa38415cd0595d013fbc15ac23517c598b891b08a8b508086)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethodOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc564aa71f8fda333f95ac662ce7837d9a4da5a4454d4d0d68c2e90490f93eb3)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfaa8c8f45977c17350271c35182478e8974432215ad6777621064edf78afaa6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAd",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAd:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAdOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85ddc22f51a2d1e010b5092949e1bcda81edc1a7a4adabc50bcb72da0d34df47)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAd]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAd],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af3e3e24274282f7023ffd7c860ceeec4bf38d4c0ac92f1f0214c594feb92a15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificateOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc627d17269bee27991cdcb0f2168bea2d4e0fc022dce0c392fe21db3ba2e511)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificate]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93fb4dedab3dfb1983291a4c13bb27feacbbdfdcc179e87f432863c3de7ed129)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonName",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonName:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonNameOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e476220dfe5590e24dc59f5d1068c26c776896939612f40af3a4e343de2ff30b)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonName]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonName], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonName],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef6f732f4f297b6705d10ba215d64866e3d4f00ac8b433eb5873440cefeac768)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePosture",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePosture:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePostureOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ca0cb64ed4a460aa1a4a67a302ef3aba2e0c9fb2bbce06b6a310ef88635a8f3)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePosture]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePosture], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePosture],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9002f3dcb0046b36c72399571567e08943527c94656a5aa73785c1312ad981d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmail",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmail:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomain",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomain:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomainOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c338d0347603026560a5191f1f7e0f522cec1cfd3ff3c93704cdeb95a442a5e5)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomain]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomain], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomain],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4a9e61c6f64ce92c274b8f5051fb0aa33890146987d94ed742113c4cf7fbdd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStructOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4104775d378a04af89c4d8d3d92e806494e24f80ccc7b29493bc6c2dc7372f7)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfd721b76c326f6427aa149ce3986dc97bf3bf229155a58bbb9224457f99e634)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8af5e83262e190fef823b3d3a31b6c935cd17977d907c7469a57c7aff463af78)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmail]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4e532305063b129021d6c4a92fc5614a59ad5502c753a718ee296d6c4e4c6c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryoneOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6de6e3a190ba05f50637609d2ca31ac3d0b9bd52470a9c083383bd953141561e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryone]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryone],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2202e58f65d29b8b122b11f4ca8ed8ddee81c140a15906591c0db641d1af1c1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4655c0d90002cf9010e963e483da8a2636be7cc38a0a3490370d074608a420af)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluation]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e49d499113a521cc6be65c1c8d3337995339b002d14fef944006e40fb62723e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeoOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c2839415fafda10b065eabafd5c885f372cd3f9c20a2bbbee8af8e172ee4b2f)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeo]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a63b7a078595bd6652cd62078be768acac4ae00729da0dde0e897be62f357ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganizationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39f8b3962a8c313287b1dd50418749898aa8f6e9bf2e80e9e9e27a9e1d9d50d2)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganization]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c5ea4c1ee51876d4df650a21687c29c1da00e012ae3d9122c54892aeb0bc190)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroup",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroup:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroupOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d1ed9c3366a0ba60117ff7e1a215f8d003d8f0934e47ea211b02f630b24015a)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroup]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8a1f1d63652352bb0e20cf2fc96a2a50699a1a83a58eaef40a7bf0366a96cbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuite",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuite:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuiteOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cc6037b549a8bb146e62f68670a224c0b864480beff22b1c22bc376b3e3aac0)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuite]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuite],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6f67f8310cfd7b0c31b797ce6e7725b1f03a14e57c37c269006fd7f7e71fa0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStruct",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStruct:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStructOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93b28c75bb326ce917af3fbefde051b56b280c37e72f9d4d653e0caa5cb72c20)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStruct]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStruct], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStruct],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3e8a8f724e64b32b9cdd55e799c4df51ec707ec98256097e2ce10dc9e6266b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec690e5bf8397d831a6166957b016649e27876ca0b9228a418c6a8f654d21fd4)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__280103c8bdd561e7e872470021d28ed1b2cf69d15cb7412ebf18f0a57907e0da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppTokenOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f76e1e049daa30f851bf27eb0c2314909fd42696a79b477cdf0da023e46d2b7b)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a09e564a9e6ce2fa52e242e3b49cd6cb507211a92a39a86d89017ebb32dcbe1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee9ea661f40be4f69b0d583bdab2580d354589010f19b9b7d531d1dc2502b58d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b00a64b65abc1025ea458c4bf478d449b38f34350133f21402caaf808d0338e6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b81de931e18f4d070906dddbf886dbd967631fe959688bd410672d2a8a8772a1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ae3995301b7222e20ba1b7e2865068450f3407abccb73d2950309af1690bc1b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcb3f4b3c7692faaeea705b2efb18c45768d79400189568ebe1e7809fe51119c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethod:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethodOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ff73796a0f695792c26c728b3697c5811aa1622610d59aa8d9695b3bcf57edb)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethod]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethod],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1589791c6ad7e83a8a5754f74f05e957dc29f8a3c57f78d18ca216b5a1234e8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidc",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidcOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bb862a0b8243346b10aeb11097af6847c849409154ff22f91e56023d5710709)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidc]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efe98e85192fb36386d5d0003256a402b6bc97b8a58985882876dc7de53faa52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOkta",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOkta:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOktaOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2fd1009f641dcfc400ce27993d6f6e90cc59beff73024ab18254c07584d7876)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOkta]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOkta], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOkta],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9a9af6652daef5fe01bdd059987ed888db48295dcbd89f68351dadc16bc8c1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f0a0bc5e6af38852ca5c827085221cb7fb0e6f837d343ea54ce90e1e75cef48c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContextOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAdOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificateOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonNameOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePostureOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomainOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryoneOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeoOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganizationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroupOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuiteOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStructOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppTokenOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethodOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidcOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOktaOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSamlOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceTokenOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequire]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequire], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequire],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab70962124035863ab02a2b04a35a58bc51ab384a8409a6410a09c8c95dcc550)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSaml",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSaml:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSamlOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f79c3853b4cf4f1065ac4c38c2b83d4a23d935aaae37878e0232e3ca4e9488e)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSaml]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23a0c111532e8d6f25bbf232632d370a2f0b822fbadda4a20a71d6ddec436829)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceTokenOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__568e404b67fc0360cfdb9845b6bf87e46c8b6fa56da7b0e449e7c41162481601)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceToken]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceToken],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__276dc1407e2d88cc3bfd0b2f95bf890e468397cb304b340b7689cf83e14022b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasApp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultSaasApp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultSaasApp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributes",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributes:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__807d9bdaa02cce5ae59227b6a0b1ec896d80d0b5ab3b28beb394b7f3d948e4d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5114ae473ef8b137d1b0131faedd4205ce43dfb4a248b7cb389c63e14905637)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef39406e45904101c11f491d2294bf47c426feb990fb292e264597417f5f25da)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2fd1afdf1679d7f39b3d5b1ff370142495f55781f764fe36a2714d3900282168)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b3e712e5dc3d240b6614c17e0b20dee1a43f0a34dff542ab793ba5979907f77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1e33c7b46db93493a83eb9414b6e985637a7a281b0f01a9d13b9e5cce04996e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="friendlyName")
    def friendly_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "friendlyName"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="nameFormat")
    def name_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameFormat"))

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "required"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributes]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b16c8b60f1fea2c40d55047dfa0bee343d9ee5a557a24ecc17dba73af11b919)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSource",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSource:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1156edec229fb2d2787152988e447853722491a849e0a7e476a47c1798cc3411)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06568c2951246aa364eb5699eaa978730edeaf424530b4a7eb113c1430a5a19f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13f53c8dbf1e2626ebe81f77620fd874da92488fff29958229f11763b57d302d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0702318c874c63a996ce3619139f701e58c36a588ffa7280ccc9ce5d1bab768)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef3e9ad9577effedee637528fded47014c3d9f622b6a8ef4fdc0bfda3715283f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32fff38aab2eb013e95f74a8fd77546be577ff88025aa6a10591e74b01618fd0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="idpId")
    def idp_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpId"))

    @builtins.property
    @jsii.member(jsii_name="sourceName")
    def source_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f8923b2585cb33e0011b014002a6c0dc3beb61f43ad688b43dbf108ef0cafcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38a5ffac086a28d584f5cc0dbed0799b7341335af6e508d3c2c4654ea4e9b329)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="nameByIdp")
    def name_by_idp(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpList:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpList, jsii.get(self, "nameByIdp"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSource]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeb7a75f01e0afc3768988e8654993a31a5c7fbea4b11c2d52d1167557cf5c53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaims",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaims:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaims(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9df3e56575922e663faed5764965933eb41254caa748d4297f3ddd9161b668a7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af79f8e0f30ca80daad00a9fc9ea1b3876225283ca262f4f015d0d62ae1478db)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef07d41bfa7b7297f85ce5d8c0e015237a61e2c7fd1ec5d6c188c7f4c01d85f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f52596e335e64bc3f55994ccd08eee27d4f5f4b8cf94f653e55ea906892d7b0f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__98914de7bb9dce06d02213f09cb777acf25608df9d49f4a1bab8367dfe428b91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7bee0686a740e5f19ef3c2f34083feb67619ac9fcb9fb650590b82675b19366a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "required"))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSourceOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaims]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaims], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaims],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73242db2c3295cced3feedaf2aec9b12cb6dfd1053d5ef425684aa2f725aa505)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSource",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSource:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSourceOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ffcca649fd4679b055e6b97eda64009519c97278275bcfb8915c3e18aee9434)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="nameByIdp")
    def name_by_idp(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "nameByIdp"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSource]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d3604caee533652048bfe28535027d2b80f10f00b1d137dcc877fc2d75a22d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptions:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23154d9f37cff1f0f478ce028c579b339e5163f57a10160c6fb2904fbe312304)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="returnAccessTokenFromAuthorizationEndpoint")
    def return_access_token_from_authorization_endpoint(
        self,
    ) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "returnAccessTokenFromAuthorizationEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="returnIdTokenFromAuthorizationEndpoint")
    def return_id_token_from_authorization_endpoint(
        self,
    ) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "returnIdTokenFromAuthorizationEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptions]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21df8fad1cc1951f921b1cfcac29b0ecc280bdcd4f68faa1e80dade5bafe15a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a61cff3de6083b460942547d10cba8d3d96aa09c046b9b85d5945a6b77f5f41)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="accessTokenLifetime")
    def access_token_lifetime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessTokenLifetime"))

    @builtins.property
    @jsii.member(jsii_name="allowPkceWithoutClientSecret")
    def allow_pkce_without_client_secret(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowPkceWithoutClientSecret"))

    @builtins.property
    @jsii.member(jsii_name="appLauncherUrl")
    def app_launcher_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appLauncherUrl"))

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @builtins.property
    @jsii.member(jsii_name="consumerServiceUrl")
    def consumer_service_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "consumerServiceUrl"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="customAttributes")
    def custom_attributes(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesList:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesList, jsii.get(self, "customAttributes"))

    @builtins.property
    @jsii.member(jsii_name="customClaims")
    def custom_claims(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsList:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsList, jsii.get(self, "customClaims"))

    @builtins.property
    @jsii.member(jsii_name="defaultRelayState")
    def default_relay_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultRelayState"))

    @builtins.property
    @jsii.member(jsii_name="grantTypes")
    def grant_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "grantTypes"))

    @builtins.property
    @jsii.member(jsii_name="groupFilterRegex")
    def group_filter_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupFilterRegex"))

    @builtins.property
    @jsii.member(jsii_name="hybridAndImplicitOptions")
    def hybrid_and_implicit_options(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptionsOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptionsOutputReference, jsii.get(self, "hybridAndImplicitOptions"))

    @builtins.property
    @jsii.member(jsii_name="idpEntityId")
    def idp_entity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpEntityId"))

    @builtins.property
    @jsii.member(jsii_name="nameIdFormat")
    def name_id_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameIdFormat"))

    @builtins.property
    @jsii.member(jsii_name="nameIdTransformJsonata")
    def name_id_transform_jsonata(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameIdTransformJsonata"))

    @builtins.property
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @builtins.property
    @jsii.member(jsii_name="redirectUris")
    def redirect_uris(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "redirectUris"))

    @builtins.property
    @jsii.member(jsii_name="refreshTokenOptions")
    def refresh_token_options(
        self,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptionsOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptionsOutputReference", jsii.get(self, "refreshTokenOptions"))

    @builtins.property
    @jsii.member(jsii_name="samlAttributeTransformJsonata")
    def saml_attribute_transform_jsonata(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samlAttributeTransformJsonata"))

    @builtins.property
    @jsii.member(jsii_name="scopes")
    def scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "scopes"))

    @builtins.property
    @jsii.member(jsii_name="spEntityId")
    def sp_entity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spEntityId"))

    @builtins.property
    @jsii.member(jsii_name="ssoEndpoint")
    def sso_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ssoEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasApp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasApp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasApp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4028b4c6452ae47c7008bcc2c0d8f8cf1af0ed1b68f48666e0cced0455d7f314)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptions:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93c0d3de69badce57902f281b9461478e43385fbcfcab3354281dc49dde38361)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lifetime")
    def lifetime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lifetime"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptions]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65ae99c088489aa3781913da9b3ee1a0fd09bba69e97e2de51a401443d4af125)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultScimConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultScimConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultScimConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthentication",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthentication:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthentication(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthenticationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthenticationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1daeb49ded03dd43703ce50dca43aebcd41f072b2a1a37cbd77e50177062e590)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authorizationUrl")
    def authorization_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizationUrl"))

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @builtins.property
    @jsii.member(jsii_name="scheme")
    def scheme(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheme"))

    @builtins.property
    @jsii.member(jsii_name="scopes")
    def scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "scopes"))

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @builtins.property
    @jsii.member(jsii_name="tokenUrl")
    def token_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenUrl"))

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthentication]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthentication], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthentication],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cca9afdc14eafc7f636c838fc13f511d133a10838b5d4b8a712c02dc1919aa2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c612836c9e99760d5eefa3becf8a0a1966718a98c3dbf829ad2e52372c7ac33)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83713bbeb2a858fedf9df76e9977e21ac5cce8bddcb2e4c090fcdecf06e2c789)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d72729fc140aa4f2bbbca47188b61020fbbd06d5bf09e090bc5413b198f045d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f13b061e1e325a5502aefda122143a2e278a1368e4cb7d0103779ee830b29225)
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
            type_hints = typing.get_type_hints(_typecheckingstub__55dda19b1daa1bea360efe736210d12ed8bfb31b7763ef7d2b781f9855ef6d07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperations",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperations:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperationsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__116e77d5027b08b04e48975f905b923c60a622baf422916a4674a5698b5e7ece)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "create"))

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "delete"))

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "update"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperations]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperations], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperations],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56c0945c0c1c3ca081ffbe7b2303f71a41e807acc68a8843f4876818e3b4c8d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3060261a3e799fd08f1d7dbee5adacdd6cbccedcc28af80a223689d1cb75f1d8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="operations")
    def operations(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperationsOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperationsOutputReference, jsii.get(self, "operations"))

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @builtins.property
    @jsii.member(jsii_name="strictness")
    def strictness(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "strictness"))

    @builtins.property
    @jsii.member(jsii_name="transformJsonata")
    def transform_jsonata(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "transformJsonata"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappings]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5d6072af19bd039dbe781ad85ad585ec9cdc26ee1634ea96cfd80b2a9bb06d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultScimConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultScimConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4840045f4b5d6f9dbf0fbccc0f7c00c842b14aa8873eeeb76403406cd25b08c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authentication")
    def authentication(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthenticationOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthenticationOutputReference, jsii.get(self, "authentication"))

    @builtins.property
    @jsii.member(jsii_name="deactivateOnDelete")
    def deactivate_on_delete(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "deactivateOnDelete"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="idpUid")
    def idp_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpUid"))

    @builtins.property
    @jsii.member(jsii_name="mappings")
    def mappings(
        self,
    ) -> DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsList:
        return typing.cast(DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsList, jsii.get(self, "mappings"))

    @builtins.property
    @jsii.member(jsii_name="remoteUri")
    def remote_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "remoteUri"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfig]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e7f5434800821c849d17500de5c8fadd66bf3c3bc2951e65879e2ac945f2057)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultTargetCriteria",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessApplicationsResultTargetCriteria:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessApplicationsResultTargetCriteria(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0815e1151a15cb3ce203d0d9607011017bf0d33e35f52f6c9d6a050c8faac6d2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51bfa95bd21469d0ff0e03d3908c0bd17041e31bd0c8563aa6a24605251c3061)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d420519d8bb5c3dd2b90c6812551d98b2e6351d456332e4227b4400327494b99)
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
            type_hints = typing.get_type_hints(_typecheckingstub__46dc83761e862a97c7396c69bd9f03b563a49326e78f360969abd97115c031dd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__02f354d2f16bb9512ae2d39d7a6671330b51ff38b1ca7d813de6e935b790f81d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessApplications.DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__454096038234836a76b7fdfb06a4a40983c29ade5c1a3fa1afee7a2a0c11589f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @builtins.property
    @jsii.member(jsii_name="targetAttributes")
    def target_attributes(self) -> _cdktf_9a9027ec.StringListMap:
        return typing.cast(_cdktf_9a9027ec.StringListMap, jsii.get(self, "targetAttributes"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultTargetCriteria]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultTargetCriteria], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultTargetCriteria],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d56aeff4609af5a0a08113b3caa41fb3c7cc582e93da42239b25e126ed685d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustAccessApplications",
    "DataCloudflareZeroTrustAccessApplicationsConfig",
    "DataCloudflareZeroTrustAccessApplicationsResult",
    "DataCloudflareZeroTrustAccessApplicationsResultCorsHeaders",
    "DataCloudflareZeroTrustAccessApplicationsResultCorsHeadersOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultDestinations",
    "DataCloudflareZeroTrustAccessApplicationsResultDestinationsList",
    "DataCloudflareZeroTrustAccessApplicationsResultDestinationsOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultFooterLinks",
    "DataCloudflareZeroTrustAccessApplicationsResultFooterLinksList",
    "DataCloudflareZeroTrustAccessApplicationsResultFooterLinksOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesign",
    "DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesignOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultList",
    "DataCloudflareZeroTrustAccessApplicationsResultOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPolicies",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroups",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsList",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroupsOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRules",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSsh",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSshOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExclude",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContext",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethod",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAd",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificate",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificateOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonName",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePosture",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmail",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomain",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStruct",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryone",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluation",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeo",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeoOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganization",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroup",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroupOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuite",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIp",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStruct",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppToken",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeList",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethod",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidc",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidcOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOkta",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOktaOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSaml",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSamlOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceToken",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesInclude",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContext",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethod",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAd",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificate",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificateOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonName",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePosture",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmail",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomain",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStruct",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryone",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluation",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeo",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeoOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganization",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroup",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroupOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuite",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIp",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStruct",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppToken",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeList",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethod",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidc",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidcOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOkta",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOktaOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSaml",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSamlOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceToken",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesList",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequire",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceToken",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContext",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContextOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethod",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethodOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAd",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAdOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificate",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificateOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonName",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonNameOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePosture",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePostureOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmail",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomain",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomainOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStruct",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStructOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryone",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryoneOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluation",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluationOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeo",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeoOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganization",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganizationOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroup",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroupOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuite",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuiteOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIp",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStruct",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStructOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppToken",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppTokenOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireList",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethod",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethodOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidc",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidcOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOkta",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOktaOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSaml",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSamlOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceToken",
    "DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceTokenOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasApp",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributes",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesList",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSource",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdp",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpList",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdpOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaims",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsList",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSource",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSourceOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptions",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptionsOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptions",
    "DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptionsOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultScimConfig",
    "DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthentication",
    "DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthenticationOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappings",
    "DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsList",
    "DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperations",
    "DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperationsOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultScimConfigOutputReference",
    "DataCloudflareZeroTrustAccessApplicationsResultTargetCriteria",
    "DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaList",
    "DataCloudflareZeroTrustAccessApplicationsResultTargetCriteriaOutputReference",
]

publication.publish()

def _typecheckingstub__5ff3771254b8ba08ffaff62fb08c4fa424d6e52716cb187e953448a9426ab5b8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    aud: typing.Optional[builtins.str] = None,
    domain: typing.Optional[builtins.str] = None,
    exact: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__60466979d23ceae4e9baab35cd32a62fd0cf469addeffac38a9a73f1ef01b624(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0a66ac112262ee717e3dee43f661568ff5af6e72dd508e20519f595ba094557(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c385e03f38f03c26366937776c9d0c1f75c6db3df49376399b4668f3a74456d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3964e49ceddc58501239640a8211edd36c8b46d0c6114763cad63c66f08548e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d9fe33e8a0822cdf46f80d22074103eee7e6a39c1a2331ae45163e6e3bdeae7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__286f99d9127186f4fbdd29c234ffe605ef307b86663570fe669e6f46ae51e158(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__843df41dc744476032495b77529bc7fd7705aa5cef4541abac4f4f3d73afcc76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93c1cf463bd51bec464a70b8bedc919b1a2de4bc96127194d97959631a7d64c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb92fab3569e8bc784c496119269161c766afa32300a82cb4c4f73317a03277d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fae49596d00e4db3452dc71e9de8cba76f54daf3747b858206c7890d81537d0b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: typing.Optional[builtins.str] = None,
    aud: typing.Optional[builtins.str] = None,
    domain: typing.Optional[builtins.str] = None,
    exact: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_items: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    search: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8145575df6d0d29a35ceff44c530d5c25a53256d3d575a1876d3cd937773b57(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7ef5a73b75202e70c7a20643d9fbd431419b74344055619e73403ef5c248470(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultCorsHeaders],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9ad2afbb319479afc3a7d6bb366d22815ce747afe2cebd59283a1983ca6d2a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e00a7e7670af183232cfdf6f076f56bea61ce0cecc715edcef2aba0d06f964b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5acfa2cd2c0ce5058a8d64027641fb31a6655ebddc0994d6e8fdb34b5bfc76ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__315e897227d4039c268cf4d41169d05d74b9fa3d33315bc555d862f4911c8094(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06a87d47346cf0791889b1aac3904163cae18e51ea27bc867c8499863ea6424c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10c7e4097a27230822bf08174ec9887a7ba0b6b9ea595f169873caebe247f5d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2677fbc0f6b4da09e72a4d49612c48e02e51a4a393dba0efb194d9893365b247(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultDestinations],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fb8825065eb1fb0ed3f866ba007a49adf5eb74c25a8cf42432e0c76cac5cedb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ab5aa962d73513549d74b3d6ac9cc836afb9f915bbd2c86351164f2b7f5a41e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cb37e480f3259b1a7657582419f539f6ca54dfc08b3ed5808c1dfe485cc2137(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af923b5813ff8fb9ded22e20da496944ac0df45589de65685b68dc54ef7e8a05(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eda3f3637becf337868a86e6f09dbdfe372a2d4b9eda07da353c7969f59db8f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59f8612f6d1778dcab2e57d4d7155f5cb2534f5d6831527690a6387e8807a1f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8fa842c824919528fb06f82d7b0c907395ca8e7f01ddcddcb47ada263009600(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultFooterLinks],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__738fdd54d0b8ef004c0752d15067d78cb492d3c85d51f717ff2f5c1a8e127793(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c5c56209b05eaaa6e95477640c0fc9e477b65a946607287db534f8204622865(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultLandingPageDesign],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce710c0a914ba143b7250440cee8d9b0b1037dcb1d18d096472c511e55296d37(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d7ef214529b3f37555fdac6ad538b82b51e405b460af572ce6783030f73774b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f256570141cff0790a5cc43b8195846275d418242457ef282ab691f9725dda9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5e0ff793b866899d5210b552801856f9600d470c567b76773a77c20d7d080f4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de415919334bee3a780ca07b5d9de68625bb8d7615236badaccd655e5101e896(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cba4ee94df3d215f8e78c2487f825147798f5a06b4fcdabb9ec3bd2ee43b1ce5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f3ccf301183b1e57edf5da95b5bd05be07af0c48b45962b354da6f26af24792(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89e72aaf4c3df92f02c4c12942673053b2e04744a322d732ea46ca2890f8a32e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b931743f1252c21eba92cc11a68864073ca36565e3aa9de11be40153857e6350(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f926a98e94bd330597d0fdf14225a0c15b222e801f7fc12aac4b89126b4fad8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08eff9b6a768c0245f66c84a7c60520b3280974623dbb8f256159b0d36936e0b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ec09a46a4798beaeb265f7052cb98a2946352cf5c7e6afa185666690aa926fd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acabc5c9254258666060fd4225c17c54a8f4eeec41c6c37731981d774f233527(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25214386d6b07bafaca81ab056f341ebf884c39be8d55fd95642f38120c3e014(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesApprovalGroups],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db3201b31650c1b3fa51f2656adfd932935ef265894e222f2d74c94d1e1950e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff0854f0d34dfe78b578d980059533fd679115b59991f8af47697990bc3b8dbb(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRules],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d6f2c417ee15f4d4b09b6f444479ccbcdb3ee18bb905988f98461767440fd38(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__968325158a527a9580752114901481621941d428d2eb36eeafab923b7e1ebc47(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesConnectionRulesSsh],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8aa442ad61c445eac4d83f502e0ea7618b2b617d4b5618004149b60b9258eaf3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5741cebffc5888f88732e85fa73c34de30bb91142e5ae4a31c57a51ba5dc553(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5de4e61a2a65947080bfdc3d590d0b3ec8606f86a00a345c94f46c5389536359(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20c0d48e6a553c4a6112cb5c23c6f097361286d06f8b38f8f85f75c7157e223d(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a631c411afea76394535f6f28538523d5c60a0e4ffa8f4fa9dbbe30701ee05e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b46a0d1ab936aa525209034653e22ebfd322e5fba5051681df005710c14d90b4(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6643907d55586af18a5b8050982274e0336e54ae9711550bb3caf41ce42c2fb0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__764e01fd1a34801cf0206d414f5fd607c96c96a64b0fa63ba0b2db8cbd6772d6(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cab548d01a4937b054352ec0c66d97b059802e9973e5d7765f025814573fc26(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d2562cbb5790dc16c159430b4bf65fff19e670b930b5675927d36cfa98510a9(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1d551f5daa31d14747a8104097e4183d2b073a50da2cb546d44e1d9c0f35e59(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__700b9bf39eeb1525572d1959e6c3c98bbf286c97fc5c720c5a27b83ed86a5857(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cde8481909cfcb562b164a045bb861fd8baae70343656351f3acb29b5ee13b9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b224b543308cd024ce6a4ab21cdaf208349831cfda7c9d85e015c22e4f579260(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b0853339001a6c5fd79255c6a79187420d59da63a11bce1dbd916f7781603c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8002eae3a45640e4996916e295a9148012deadeb850cb5ea5bae19fb8bfcbe8f(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d602488b3aafc9846866ba04b663869bd0d8928901dd0e6394552eb977bb8739(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0d7fbbe7279c7115ad69e4ff4a13cc36e2d611816074bf59dc54b2aeb14600b(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd5ad530c522612ac69c2af0dee6db3eaca05594910e3037c854031907721f65(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a287bbefbc47a41092e923d48b8ff073ec6c0cfadbaf2a9f3b8e4cef8b6f9055(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e6d0adf4f2fe405ca6136b84e63b59f4dff54e3d901b6bbc41081bb70f60006(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bf76580d52bf760fbf7fd7cfae061e48c360ca43361ac871f567bdac0dda364(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cd94f9b62c448210d38274bd8fb14f668fdda247fc554ac8a9564cf06697b1e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a7ac51e5aa02f19374d0452fc6d672f522fc5e1d3ef1e623e59fb1c9d5ec540(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62f56ad9e9e0a15d640baeca9c5c26998d4029e98a2f53ede0fbc4d96ef54f27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac90eb55ea527571eb432907145b9c4629f27a098d4a6ac2f2527fc3b858ec5f(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f82066a468a5c111f7ef2461fd8be04860e98fdb1002e473986e54cbb30461df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce37dfe013861a5046194e1fe87e8dcc19f5600cfa70832140970b06f490ee88(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b482592e1acdd1512a4ee4699e5020d48963b8db7bcfcde2247696155d1b855(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f515149159e6e30af6ed833057d280117619d4f81ce699430c8092c84ee9449(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35eeb1e269765d3c1e2069cc461cf344c30862e5d54ad4f5767de3e5a1dcc443(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f98cd58314a9ff69839e42d9e4ba9b4fb593cc7ac75e5bec3c01d99cde793064(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26c881b21d7790c2de50b7e81102cec8647eb68ac83193fc5e74e62c680f4aeb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__077f1a1cfed3676fc59832f10d4b4b9c9a0b2357c97dcf3295b0336167bf83d3(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1f303a8a5d653b0b1f7a89f5223f54eec8f83a297a9aa3d32c21f85960b7dfd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0a361bffe7f634e6630b2af7710159a0d0890c67fd697c7d809722aaab0a5a0(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03d23b59eee36660259782359f2d7a74588293c36d594c33cd7920b3d84a9bc3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ddbfd14e8b53cedad4fc1517b2c03cfb562371a3e7cbc82efbdbf42b7c81ef2(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cdee223b498e417e1ffd44f6cc4688ec68e7269a9c730384d5723a84e648cf4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23e9f677cabdb675b21198d6df9e4da62358d541131e9c9376b5a81ae0fc9db6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eb502446b12176da2f60b201f85072958a66f6986a965281ebc1d10afb5df42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8bb5020a3d0aa3333bfce20e58f04ab228ea5a032a956aed72783fd1b036194(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6e9782ced2f755be07c0c1f03bdde772649705ac1560a0462b236ce8b70d6ec(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aef07d77a0e0c3dda3dbd5b411146d08c6c728e9708ebc02b017dcfab0ada99(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b9198f56348aa33259349f358d45e25d93912e57ff44f8b1dcd1ec55fbcf637(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fa5a55762e4c615e6d8afd28b9e314c4785e7ce1f1b7fa2581616e3f166d253(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8416692f6ee6f729e68920cab0deaa63725282d73a3d99968a12feda82a79cfd(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52ac0fe6992750a79e77b92be95d78490623d0989c1a4d4bb2f9f6687750bbc8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2223092dffd46daab435ee1adb9c87f29a0c4caa25d072db222fa9a88d6e928(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7e6534231cc380e527f0131acb93402f575da05ffd54050d4f818d3806e666f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfc1fe07365c43ffd67606fc291cf5b7479dd4d36bf3f37afb19489ece4f37d7(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExclude],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ef11aa1c6e40c5780e1485417ebb16bad7ea90d46155dd04695654340ab183c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9757681992468f768b4cf8ec933830ad7f3fb03ecdd5528306121fa4adaec30(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25ac1797e1c3e328a4e1ef1c56fa18e6ce30b22ab02157000a5bb62a041f8cff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b27f93a60252d117f156721acc6317e9b443d6a97e78ab4773ea9727e0752010(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesExcludeServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__031315bc5459f182f1083eaaeeba8713fea0b1a5ca4aa29fcb13942d7972924a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dba43e51befe3ea07155104fc3ef2ab4e2dd749318847e53a2e0646cedd9bd1d(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83fb653c0a5d6dfbab4b4fc981eeabe621bd5049077b9c730471918da5ac230a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7211dc6e0091b87bb38d4c719f72a59ddcdb682cacc7268902f702ebb06bad5(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fbb70e21ebe22022878331fc829491a98377b8bba411205f9668bd7fb94b8ee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157f044c29ff3999692f89cad78e3f77fa61ac3667c4301a61e3a64096a91e1e(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4658fbf4fbbf0bf6f9c6d4e971e4f677856f9c8e447925fd17b61f5e8064fb1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd4f3f8b055d20f8ff217d0dace8d38b24f121c499d9885ed7fb0cc4accbe974(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b71cae12b64bc45f575f277cd8f8ddd6d4506bc32338fc0fd7fd850870940ce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__126bc2c9bbfc92340545e10a3c9d8db481bdd2ab5092ea00ecae9f0e2f72c094(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6e4c73569ffe63d8aeb85ccbb946d788d3f17ed9d16fa083751eb9457bb49bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__847a10a5c743e01cbb9ae9401ad4b1938c0a0660d80bea324b4e1ae8a6a5b4d1(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080824b6b882e42921cf199b33ca3d8b1abbef7d8b4c1d7a2c76cb1222df6950(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2507b5f3fc70e0e2204b53e2a4b22b64352cd2f73cceb6815bf894ca4a5b576(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6807a1795cefbf4d84d96e02cbf5c857f573ad6542c8f519ddd1d6eb16e15fc2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42b63eb7f699cad177e3ed0929b15b3313cb48343952f12939e5531e078037d1(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cec1f26099351dac442617d32833d14f24040d8196de010a9b7799d95c67911(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09518cadc75dd075542b5c637497049679a77e3e6650ff41c7de762c5aae40cb(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a40bca7a0f6ab1c2b0c7d54b755dcf0cdae96f5429debb170fa13d7d66d78401(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7421287c1467a2151783b3e5e61a340f423be9d6ad3e4bb035046c8461efe04e(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4abf3fc7c7b9570012ee85a9a0b894dbbba5150264e796cb7c61f187090a8065(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a4f25db12d14ee6909432832422e5421e53f82701529a1784cb07b1ad83317e(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__164e29868185010617150eaf01bb9a6568ffba5d00abed45e46726d4011bf340(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baac8a9be7540e0424783673db7f1ffa6df961f33b131708db0ce80e17793470(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0635131668f44d5bf9a5515d81b91006c9a7b061f1a28936d2f1213cc6847d5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080750a6b0371ca0e683d618e20163c9508ea5d54229f5167c4ec35e80b12138(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aae85c04cb405e5080318b747368162fe14d1de4a44b4c3a70576ab964534a73(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ea3b7ea2ad0f7ab215f634b3cb47a4fa321fc5e61293a5b5da7c2fcce0eb841(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89f673c726cc33d0e90a864e85681e38028a153fb9fe3b048ed76afb05837699(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b375d32c8a4a5a591ed36a94580bbe4d2832ffa2905c8b61cf5f3a7f4488e29b(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa2facbda86c77a96e1d8d9254c83d8a423750c3d823d271e7580c0156e246b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f6c340534f1f214d4e6072063818a6b481aef372b9e5bb8e1f5b3e4b78c06a(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6b2e12dff2a84025c02701e11cc201e8a73ed4796312d32bb4ae6f195d06dfa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__812df8261c592b2e109a74adbb0194d37160c0971335c71c2338ccf16ed906d6(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3fe21dc355eaf66780c7954dafe73bd8adc52b2e601dac18f8282d6d88c2368(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2784502b551c1a65524b8736a2e5680b192faaa94c408ee8068372b820ed0dd6(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c1c68b4b5a3127ccbb3c1489251a56827b8e6a23479dcb0794bd686d37bb2ce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d46ea4dc9d2787ed33e1d88a19bcc82203fe81af55067faddc2238c9c202add1(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56ead0768904b1b329573ab5dfd46f4511a53ce75875de219a1230af98d9e748(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2abee5fed0f48c92e35afcab7992e5b6d229228d6a6c89f19e284908d9a2082(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9cb8bcc60f1cbcc8234383156850ce097b5a0d2d7a73384e559750d8e07b498(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aaffcc65dd63a017c528c456657a63d8582ca4607eae70185d48a2659065373(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7619f2b194e81c2f64621019639934e84433a09e5ed46a9aaa93dd68bffddf6d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f50eea03c97d14528a4e1bc8bd0078e0315e9b28537c7596c02aaad7b25be89(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5e2bc2f924744891f6530b7556294964e2a7227095f5f8d20150dce7e3d1e23(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fdb3a1b4803cc9124057d1b0ccbb20d258ff60cf5b2510124aaeb349d8930fd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b894093be7f34d35a19585606f88edd79edbe12ff421fb17242b5732088f05e(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c281c8a77840f4cf841565c337ac020c619317d01a207ba989f224e22c2bfa10(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad7c0c9628d102c75cabe8fd69634e17705fd7021d45b04e3f0db9bddf148cd6(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a5f45a00c6e1c913bc0de56a65346c8ea88008c046a930534b32d6deff24072(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f90dda4ae4453cc29ebc0545a6b399399319632fca87573d9ec7c6ed5b19fd8e(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesInclude],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f762bae572e9048bb03307286102f28f9b2f31e076bfcf8bc8c60e7cca92b22(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6b9b1a02e15f616dbf55c7a9fc72c47e49ae7d035ef66487d5cb203dece718f(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b1986fbfd33fe49ef7df88ba004731f0c87215b31a00e60bff2b0eda6dd8158(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcb8e90f60b0c263b6e03a6800bb0c08ee86085fc03bb49d93b4b227b8a0c1cf(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesIncludeServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ac12fa3ce3b709247caaa17c53e772cbd58e17e0c26f558eb973dc2592c2642(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b60526b0f7b4e440fc8c1e91d65578a9953ed7f979385efca2f9bdf1bf3978b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fde79744423805a41c12fcac8e87e096786ab871c38fe48cf1644461a20e485(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4b17e9a4d42db257d3b3dbf911ad2cf0ecfba3683f420794c8750087336c603(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7468911c4255074dc623bf051773004bc5b04e62a338bc3acc61baa52a303be0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed6da59e337f0d64d266e1dc2a989680cb2f960a38337c48b5867137117addfd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3969a946e36cc736207ff92eab6ef524156d9b4b5097d5b538216ce9df137677(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPolicies],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ed69a4d97c976f4e08a6ef250fdaea17cb7527cf05f94be302d8f43098c5c86(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c98dd324c8790f46cf6c00f9a3e3d33db732dca31aa3806eae2bed845d21a5b(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAnyValidServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab705c15d8fcf506111a89e335fc7bafd133b336aeeb776f4ed14f37ac27e89e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__261259572fa66c9aa38415cd0595d013fbc15ac23517c598b891b08a8b508086(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc564aa71f8fda333f95ac662ce7837d9a4da5a4454d4d0d68c2e90490f93eb3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfaa8c8f45977c17350271c35182478e8974432215ad6777621064edf78afaa6(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAuthMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85ddc22f51a2d1e010b5092949e1bcda81edc1a7a4adabc50bcb72da0d34df47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af3e3e24274282f7023ffd7c860ceeec4bf38d4c0ac92f1f0214c594feb92a15(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireAzureAd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc627d17269bee27991cdcb0f2168bea2d4e0fc022dce0c392fe21db3ba2e511(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93fb4dedab3dfb1983291a4c13bb27feacbbdfdcc179e87f432863c3de7ed129(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCertificate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e476220dfe5590e24dc59f5d1068c26c776896939612f40af3a4e343de2ff30b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef6f732f4f297b6705d10ba215d64866e3d4f00ac8b433eb5873440cefeac768(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireCommonName],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ca0cb64ed4a460aa1a4a67a302ef3aba2e0c9fb2bbce06b6a310ef88635a8f3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9002f3dcb0046b36c72399571567e08943527c94656a5aa73785c1312ad981d8(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireDevicePosture],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c338d0347603026560a5191f1f7e0f522cec1cfd3ff3c93704cdeb95a442a5e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4a9e61c6f64ce92c274b8f5051fb0aa33890146987d94ed742113c4cf7fbdd2(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailDomain],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4104775d378a04af89c4d8d3d92e806494e24f80ccc7b29493bc6c2dc7372f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfd721b76c326f6427aa149ce3986dc97bf3bf229155a58bbb9224457f99e634(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmailListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8af5e83262e190fef823b3d3a31b6c935cd17977d907c7469a57c7aff463af78(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4e532305063b129021d6c4a92fc5614a59ad5502c753a718ee296d6c4e4c6c5(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6de6e3a190ba05f50637609d2ca31ac3d0b9bd52470a9c083383bd953141561e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2202e58f65d29b8b122b11f4ca8ed8ddee81c140a15906591c0db641d1af1c1c(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireEveryone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4655c0d90002cf9010e963e483da8a2636be7cc38a0a3490370d074608a420af(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e49d499113a521cc6be65c1c8d3337995339b002d14fef944006e40fb62723e3(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireExternalEvaluation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c2839415fafda10b065eabafd5c885f372cd3f9c20a2bbbee8af8e172ee4b2f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a63b7a078595bd6652cd62078be768acac4ae00729da0dde0e897be62f357ba(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGeo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f8b3962a8c313287b1dd50418749898aa8f6e9bf2e80e9e9e27a9e1d9d50d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c5ea4c1ee51876d4df650a21687c29c1da00e012ae3d9122c54892aeb0bc190(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGithubOrganization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d1ed9c3366a0ba60117ff7e1a215f8d003d8f0934e47ea211b02f630b24015a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a1f1d63652352bb0e20cf2fc96a2a50699a1a83a58eaef40a7bf0366a96cbc(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cc6037b549a8bb146e62f68670a224c0b864480beff22b1c22bc376b3e3aac0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6f67f8310cfd7b0c31b797ce6e7725b1f03a14e57c37c269006fd7f7e71fa0e(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireGsuite],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93b28c75bb326ce917af3fbefde051b56b280c37e72f9d4d653e0caa5cb72c20(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3e8a8f724e64b32b9cdd55e799c4df51ec707ec98256097e2ce10dc9e6266b6(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIpListStruct],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec690e5bf8397d831a6166957b016649e27876ca0b9228a418c6a8f654d21fd4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__280103c8bdd561e7e872470021d28ed1b2cf69d15cb7412ebf18f0a57907e0da(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f76e1e049daa30f851bf27eb0c2314909fd42696a79b477cdf0da023e46d2b7b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a09e564a9e6ce2fa52e242e3b49cd6cb507211a92a39a86d89017ebb32dcbe1(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLinkedAppToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee9ea661f40be4f69b0d583bdab2580d354589010f19b9b7d531d1dc2502b58d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b00a64b65abc1025ea458c4bf478d449b38f34350133f21402caaf808d0338e6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b81de931e18f4d070906dddbf886dbd967631fe959688bd410672d2a8a8772a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ae3995301b7222e20ba1b7e2865068450f3407abccb73d2950309af1690bc1b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb3f4b3c7692faaeea705b2efb18c45768d79400189568ebe1e7809fe51119c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ff73796a0f695792c26c728b3697c5811aa1622610d59aa8d9695b3bcf57edb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1589791c6ad7e83a8a5754f74f05e957dc29f8a3c57f78d18ca216b5a1234e8e(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireLoginMethod],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bb862a0b8243346b10aeb11097af6847c849409154ff22f91e56023d5710709(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efe98e85192fb36386d5d0003256a402b6bc97b8a58985882876dc7de53faa52(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOidc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2fd1009f641dcfc400ce27993d6f6e90cc59beff73024ab18254c07584d7876(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9a9af6652daef5fe01bdd059987ed888db48295dcbd89f68351dadc16bc8c1a(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireOkta],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0a0bc5e6af38852ca5c827085221cb7fb0e6f837d343ea54ce90e1e75cef48c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab70962124035863ab02a2b04a35a58bc51ab384a8409a6410a09c8c95dcc550(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequire],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f79c3853b4cf4f1065ac4c38c2b83d4a23d935aaae37878e0232e3ca4e9488e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23a0c111532e8d6f25bbf232632d370a2f0b822fbadda4a20a71d6ddec436829(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__568e404b67fc0360cfdb9845b6bf87e46c8b6fa56da7b0e449e7c41162481601(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__276dc1407e2d88cc3bfd0b2f95bf890e468397cb304b340b7689cf83e14022b7(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultPoliciesRequireServiceToken],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__807d9bdaa02cce5ae59227b6a0b1ec896d80d0b5ab3b28beb394b7f3d948e4d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5114ae473ef8b137d1b0131faedd4205ce43dfb4a248b7cb389c63e14905637(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef39406e45904101c11f491d2294bf47c426feb990fb292e264597417f5f25da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fd1afdf1679d7f39b3d5b1ff370142495f55781f764fe36a2714d3900282168(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b3e712e5dc3d240b6614c17e0b20dee1a43f0a34dff542ab793ba5979907f77(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1e33c7b46db93493a83eb9414b6e985637a7a281b0f01a9d13b9e5cce04996e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b16c8b60f1fea2c40d55047dfa0bee343d9ee5a557a24ecc17dba73af11b919(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1156edec229fb2d2787152988e447853722491a849e0a7e476a47c1798cc3411(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06568c2951246aa364eb5699eaa978730edeaf424530b4a7eb113c1430a5a19f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13f53c8dbf1e2626ebe81f77620fd874da92488fff29958229f11763b57d302d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0702318c874c63a996ce3619139f701e58c36a588ffa7280ccc9ce5d1bab768(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef3e9ad9577effedee637528fded47014c3d9f622b6a8ef4fdc0bfda3715283f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32fff38aab2eb013e95f74a8fd77546be577ff88025aa6a10591e74b01618fd0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f8923b2585cb33e0011b014002a6c0dc3beb61f43ad688b43dbf108ef0cafcd(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSourceNameByIdp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38a5ffac086a28d584f5cc0dbed0799b7341335af6e508d3c2c4654ea4e9b329(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeb7a75f01e0afc3768988e8654993a31a5c7fbea4b11c2d52d1167557cf5c53(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomAttributesSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9df3e56575922e663faed5764965933eb41254caa748d4297f3ddd9161b668a7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af79f8e0f30ca80daad00a9fc9ea1b3876225283ca262f4f015d0d62ae1478db(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef07d41bfa7b7297f85ce5d8c0e015237a61e2c7fd1ec5d6c188c7f4c01d85f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f52596e335e64bc3f55994ccd08eee27d4f5f4b8cf94f653e55ea906892d7b0f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98914de7bb9dce06d02213f09cb777acf25608df9d49f4a1bab8367dfe428b91(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bee0686a740e5f19ef3c2f34083feb67619ac9fcb9fb650590b82675b19366a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73242db2c3295cced3feedaf2aec9b12cb6dfd1053d5ef425684aa2f725aa505(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaims],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ffcca649fd4679b055e6b97eda64009519c97278275bcfb8915c3e18aee9434(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d3604caee533652048bfe28535027d2b80f10f00b1d137dcc877fc2d75a22d8(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppCustomClaimsSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23154d9f37cff1f0f478ce028c579b339e5163f57a10160c6fb2904fbe312304(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21df8fad1cc1951f921b1cfcac29b0ecc280bdcd4f68faa1e80dade5bafe15a1(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppHybridAndImplicitOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a61cff3de6083b460942547d10cba8d3d96aa09c046b9b85d5945a6b77f5f41(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4028b4c6452ae47c7008bcc2c0d8f8cf1af0ed1b68f48666e0cced0455d7f314(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasApp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93c0d3de69badce57902f281b9461478e43385fbcfcab3354281dc49dde38361(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65ae99c088489aa3781913da9b3ee1a0fd09bba69e97e2de51a401443d4af125(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultSaasAppRefreshTokenOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1daeb49ded03dd43703ce50dca43aebcd41f072b2a1a37cbd77e50177062e590(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cca9afdc14eafc7f636c838fc13f511d133a10838b5d4b8a712c02dc1919aa2(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigAuthentication],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c612836c9e99760d5eefa3becf8a0a1966718a98c3dbf829ad2e52372c7ac33(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83713bbeb2a858fedf9df76e9977e21ac5cce8bddcb2e4c090fcdecf06e2c789(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d72729fc140aa4f2bbbca47188b61020fbbd06d5bf09e090bc5413b198f045d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f13b061e1e325a5502aefda122143a2e278a1368e4cb7d0103779ee830b29225(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55dda19b1daa1bea360efe736210d12ed8bfb31b7763ef7d2b781f9855ef6d07(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__116e77d5027b08b04e48975f905b923c60a622baf422916a4674a5698b5e7ece(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56c0945c0c1c3ca081ffbe7b2303f71a41e807acc68a8843f4876818e3b4c8d8(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappingsOperations],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3060261a3e799fd08f1d7dbee5adacdd6cbccedcc28af80a223689d1cb75f1d8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5d6072af19bd039dbe781ad85ad585ec9cdc26ee1634ea96cfd80b2a9bb06d6(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfigMappings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4840045f4b5d6f9dbf0fbccc0f7c00c842b14aa8873eeeb76403406cd25b08c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e7f5434800821c849d17500de5c8fadd66bf3c3bc2951e65879e2ac945f2057(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultScimConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0815e1151a15cb3ce203d0d9607011017bf0d33e35f52f6c9d6a050c8faac6d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51bfa95bd21469d0ff0e03d3908c0bd17041e31bd0c8563aa6a24605251c3061(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d420519d8bb5c3dd2b90c6812551d98b2e6351d456332e4227b4400327494b99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46dc83761e862a97c7396c69bd9f03b563a49326e78f360969abd97115c031dd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02f354d2f16bb9512ae2d39d7a6671330b51ff38b1ca7d813de6e935b790f81d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__454096038234836a76b7fdfb06a4a40983c29ade5c1a3fa1afee7a2a0c11589f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d56aeff4609af5a0a08113b3caa41fb3c7cc582e93da42239b25e126ed685d0(
    value: typing.Optional[DataCloudflareZeroTrustAccessApplicationsResultTargetCriteria],
) -> None:
    """Type checking stubs"""
    pass
