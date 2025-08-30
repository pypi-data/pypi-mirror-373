r'''
# `data_cloudflare_page_shield_connections_list`

Refer to the Terraform Registry for docs: [`data_cloudflare_page_shield_connections_list`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list).
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


class DataCloudflarePageShieldConnectionsList(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePageShieldConnectionsList.DataCloudflarePageShieldConnectionsList",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list cloudflare_page_shield_connections_list}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        zone_id: builtins.str,
        direction: typing.Optional[builtins.str] = None,
        exclude_cdn_cgi: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exclude_urls: typing.Optional[builtins.str] = None,
        export: typing.Optional[builtins.str] = None,
        hosts: typing.Optional[builtins.str] = None,
        max_items: typing.Optional[jsii.Number] = None,
        order_by: typing.Optional[builtins.str] = None,
        page: typing.Optional[builtins.str] = None,
        page_url: typing.Optional[builtins.str] = None,
        per_page: typing.Optional[jsii.Number] = None,
        prioritize_malicious: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        status: typing.Optional[builtins.str] = None,
        urls: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list cloudflare_page_shield_connections_list} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#zone_id DataCloudflarePageShieldConnectionsList#zone_id}
        :param direction: The direction used to sort returned connections. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#direction DataCloudflarePageShieldConnectionsList#direction}
        :param exclude_cdn_cgi: When true, excludes connections seen in a ``/cdn-cgi`` path from the returned connections. The default value is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#exclude_cdn_cgi DataCloudflarePageShieldConnectionsList#exclude_cdn_cgi}
        :param exclude_urls: Excludes connections whose URL contains one of the URL-encoded URLs separated by commas. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#exclude_urls DataCloudflarePageShieldConnectionsList#exclude_urls}
        :param export: Export the list of connections as a file. Available values: "csv". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#export DataCloudflarePageShieldConnectionsList#export}
        :param hosts: Includes connections that match one or more URL-encoded hostnames separated by commas. Wildcards are supported at the start and end of each hostname to support starts with, ends with and contains. If no wildcards are used, results will be filtered by exact match Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#hosts DataCloudflarePageShieldConnectionsList#hosts}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#max_items DataCloudflarePageShieldConnectionsList#max_items}
        :param order_by: The field used to sort returned connections. Available values: "first_seen_at", "last_seen_at". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#order_by DataCloudflarePageShieldConnectionsList#order_by}
        :param page: The current page number of the paginated results. We additionally support a special value "all". When "all" is used, the API will return all the connections with the applied filters in a single page. This feature is best-effort and it may only work for zones with a low number of connections Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#page DataCloudflarePageShieldConnectionsList#page}
        :param page_url: Includes connections that match one or more page URLs (separated by commas) where they were last seen. Wildcards are supported at the start and end of each page URL to support starts with, ends with and contains. If no wildcards are used, results will be filtered by exact match Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#page_url DataCloudflarePageShieldConnectionsList#page_url}
        :param per_page: The number of results per page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#per_page DataCloudflarePageShieldConnectionsList#per_page}
        :param prioritize_malicious: When true, malicious connections appear first in the returned connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#prioritize_malicious DataCloudflarePageShieldConnectionsList#prioritize_malicious}
        :param status: Filters the returned connections using a comma-separated list of connection statuses. Accepted values: ``active``, ``infrequent``, and ``inactive``. The default value is ``active``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#status DataCloudflarePageShieldConnectionsList#status}
        :param urls: Includes connections whose URL contain one or more URL-encoded URLs separated by commas. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#urls DataCloudflarePageShieldConnectionsList#urls}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a797c2e002ad86d260aa35ec8050736e86b5319a014eab70741f4d8a24eb0c97)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflarePageShieldConnectionsListConfig(
            zone_id=zone_id,
            direction=direction,
            exclude_cdn_cgi=exclude_cdn_cgi,
            exclude_urls=exclude_urls,
            export=export,
            hosts=hosts,
            max_items=max_items,
            order_by=order_by,
            page=page,
            page_url=page_url,
            per_page=per_page,
            prioritize_malicious=prioritize_malicious,
            status=status,
            urls=urls,
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
        '''Generates CDKTF code for importing a DataCloudflarePageShieldConnectionsList resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflarePageShieldConnectionsList to import.
        :param import_from_id: The id of the existing DataCloudflarePageShieldConnectionsList that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflarePageShieldConnectionsList to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a07333733b7ad59792b3e089afd9a373db280c1313ba415b8e16c12453cd4ca9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDirection")
    def reset_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirection", []))

    @jsii.member(jsii_name="resetExcludeCdnCgi")
    def reset_exclude_cdn_cgi(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeCdnCgi", []))

    @jsii.member(jsii_name="resetExcludeUrls")
    def reset_exclude_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeUrls", []))

    @jsii.member(jsii_name="resetExport")
    def reset_export(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExport", []))

    @jsii.member(jsii_name="resetHosts")
    def reset_hosts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHosts", []))

    @jsii.member(jsii_name="resetMaxItems")
    def reset_max_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxItems", []))

    @jsii.member(jsii_name="resetOrderBy")
    def reset_order_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrderBy", []))

    @jsii.member(jsii_name="resetPage")
    def reset_page(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPage", []))

    @jsii.member(jsii_name="resetPageUrl")
    def reset_page_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPageUrl", []))

    @jsii.member(jsii_name="resetPerPage")
    def reset_per_page(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerPage", []))

    @jsii.member(jsii_name="resetPrioritizeMalicious")
    def reset_prioritize_malicious(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrioritizeMalicious", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetUrls")
    def reset_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrls", []))

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
    def result(self) -> "DataCloudflarePageShieldConnectionsListResultList":
        return typing.cast("DataCloudflarePageShieldConnectionsListResultList", jsii.get(self, "result"))

    @builtins.property
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeCdnCgiInput")
    def exclude_cdn_cgi_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "excludeCdnCgiInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeUrlsInput")
    def exclude_urls_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "excludeUrlsInput"))

    @builtins.property
    @jsii.member(jsii_name="exportInput")
    def export_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "exportInput"))

    @builtins.property
    @jsii.member(jsii_name="hostsInput")
    def hosts_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxItemsInput")
    def max_items_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxItemsInput"))

    @builtins.property
    @jsii.member(jsii_name="orderByInput")
    def order_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orderByInput"))

    @builtins.property
    @jsii.member(jsii_name="pageInput")
    def page_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pageInput"))

    @builtins.property
    @jsii.member(jsii_name="pageUrlInput")
    def page_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pageUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="perPageInput")
    def per_page_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "perPageInput"))

    @builtins.property
    @jsii.member(jsii_name="prioritizeMaliciousInput")
    def prioritize_malicious_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "prioritizeMaliciousInput"))

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="urlsInput")
    def urls_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlsInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b110686458e0cc74eed26f69e9461fbd482fe16314f1e840cf44903679a5a7b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludeCdnCgi")
    def exclude_cdn_cgi(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "excludeCdnCgi"))

    @exclude_cdn_cgi.setter
    def exclude_cdn_cgi(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91e684acd41c1b644049ae8f9884f769fc3c859b6a87d50430b380b16322f49d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeCdnCgi", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludeUrls")
    def exclude_urls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "excludeUrls"))

    @exclude_urls.setter
    def exclude_urls(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e90c9e7bfff741a77d84434520b2de38fcc7a71335964e38e82c22520a31543)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeUrls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="export")
    def export(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "export"))

    @export.setter
    def export(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b48de5dc762bf657ad493511bd19806bdd3658eddad7ebc3743d81e2852eeb40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "export", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hosts")
    def hosts(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hosts"))

    @hosts.setter
    def hosts(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__682c87eb443c1b714707c123823159eb36e99c165575dccbe2eb38555cfc7835)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hosts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxItems")
    def max_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxItems"))

    @max_items.setter
    def max_items(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__808f41bafe8c5a03c9711396f3be21e738e246be15833e3674fcfd4e28811d7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxItems", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="orderBy")
    def order_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "orderBy"))

    @order_by.setter
    def order_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c86b3f1f5caa08fe0e608a67ca7867af96ec6d6464cfcda53d02e4432abfa7b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "orderBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="page")
    def page(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "page"))

    @page.setter
    def page(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37b564286784b71b69ea44449b983477ce78458840ae4db89d192431cf03e9fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "page", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pageUrl")
    def page_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pageUrl"))

    @page_url.setter
    def page_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9eaef4b6c64f303ec92c1ec2d8a18053f92021c4d888922405d7b0953ecf53c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pageUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="perPage")
    def per_page(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "perPage"))

    @per_page.setter
    def per_page(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8aff4d5420339c9d5d8f87e060a4a5bf95a752c638e10248be02e06b39c8caec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "perPage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prioritizeMalicious")
    def prioritize_malicious(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "prioritizeMalicious"))

    @prioritize_malicious.setter
    def prioritize_malicious(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b33a97a12e7fddf86706ec43bd271e7e1132133c844ed783880b08d2e602e7fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prioritizeMalicious", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21be6b402e889b91c69905a075ab065a55332e8b0765cbf12463c9ea47e9a33f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urls")
    def urls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "urls"))

    @urls.setter
    def urls(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59c27bd77bdff10520b3faa3478eb1969406f84b7ae0db71322bc3e9f1164c55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d17379a7cf84c751bcc6622e291be41e0520c02cc305aa12026bd9863d36e57f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePageShieldConnectionsList.DataCloudflarePageShieldConnectionsListConfig",
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
        "direction": "direction",
        "exclude_cdn_cgi": "excludeCdnCgi",
        "exclude_urls": "excludeUrls",
        "export": "export",
        "hosts": "hosts",
        "max_items": "maxItems",
        "order_by": "orderBy",
        "page": "page",
        "page_url": "pageUrl",
        "per_page": "perPage",
        "prioritize_malicious": "prioritizeMalicious",
        "status": "status",
        "urls": "urls",
    },
)
class DataCloudflarePageShieldConnectionsListConfig(
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
        zone_id: builtins.str,
        direction: typing.Optional[builtins.str] = None,
        exclude_cdn_cgi: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exclude_urls: typing.Optional[builtins.str] = None,
        export: typing.Optional[builtins.str] = None,
        hosts: typing.Optional[builtins.str] = None,
        max_items: typing.Optional[jsii.Number] = None,
        order_by: typing.Optional[builtins.str] = None,
        page: typing.Optional[builtins.str] = None,
        page_url: typing.Optional[builtins.str] = None,
        per_page: typing.Optional[jsii.Number] = None,
        prioritize_malicious: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        status: typing.Optional[builtins.str] = None,
        urls: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#zone_id DataCloudflarePageShieldConnectionsList#zone_id}
        :param direction: The direction used to sort returned connections. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#direction DataCloudflarePageShieldConnectionsList#direction}
        :param exclude_cdn_cgi: When true, excludes connections seen in a ``/cdn-cgi`` path from the returned connections. The default value is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#exclude_cdn_cgi DataCloudflarePageShieldConnectionsList#exclude_cdn_cgi}
        :param exclude_urls: Excludes connections whose URL contains one of the URL-encoded URLs separated by commas. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#exclude_urls DataCloudflarePageShieldConnectionsList#exclude_urls}
        :param export: Export the list of connections as a file. Available values: "csv". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#export DataCloudflarePageShieldConnectionsList#export}
        :param hosts: Includes connections that match one or more URL-encoded hostnames separated by commas. Wildcards are supported at the start and end of each hostname to support starts with, ends with and contains. If no wildcards are used, results will be filtered by exact match Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#hosts DataCloudflarePageShieldConnectionsList#hosts}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#max_items DataCloudflarePageShieldConnectionsList#max_items}
        :param order_by: The field used to sort returned connections. Available values: "first_seen_at", "last_seen_at". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#order_by DataCloudflarePageShieldConnectionsList#order_by}
        :param page: The current page number of the paginated results. We additionally support a special value "all". When "all" is used, the API will return all the connections with the applied filters in a single page. This feature is best-effort and it may only work for zones with a low number of connections Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#page DataCloudflarePageShieldConnectionsList#page}
        :param page_url: Includes connections that match one or more page URLs (separated by commas) where they were last seen. Wildcards are supported at the start and end of each page URL to support starts with, ends with and contains. If no wildcards are used, results will be filtered by exact match Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#page_url DataCloudflarePageShieldConnectionsList#page_url}
        :param per_page: The number of results per page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#per_page DataCloudflarePageShieldConnectionsList#per_page}
        :param prioritize_malicious: When true, malicious connections appear first in the returned connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#prioritize_malicious DataCloudflarePageShieldConnectionsList#prioritize_malicious}
        :param status: Filters the returned connections using a comma-separated list of connection statuses. Accepted values: ``active``, ``infrequent``, and ``inactive``. The default value is ``active``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#status DataCloudflarePageShieldConnectionsList#status}
        :param urls: Includes connections whose URL contain one or more URL-encoded URLs separated by commas. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#urls DataCloudflarePageShieldConnectionsList#urls}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44cb008638b750e3489f34e1cad53d4cd35476267ced179c05697a9c8377555f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument exclude_cdn_cgi", value=exclude_cdn_cgi, expected_type=type_hints["exclude_cdn_cgi"])
            check_type(argname="argument exclude_urls", value=exclude_urls, expected_type=type_hints["exclude_urls"])
            check_type(argname="argument export", value=export, expected_type=type_hints["export"])
            check_type(argname="argument hosts", value=hosts, expected_type=type_hints["hosts"])
            check_type(argname="argument max_items", value=max_items, expected_type=type_hints["max_items"])
            check_type(argname="argument order_by", value=order_by, expected_type=type_hints["order_by"])
            check_type(argname="argument page", value=page, expected_type=type_hints["page"])
            check_type(argname="argument page_url", value=page_url, expected_type=type_hints["page_url"])
            check_type(argname="argument per_page", value=per_page, expected_type=type_hints["per_page"])
            check_type(argname="argument prioritize_malicious", value=prioritize_malicious, expected_type=type_hints["prioritize_malicious"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument urls", value=urls, expected_type=type_hints["urls"])
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
        if direction is not None:
            self._values["direction"] = direction
        if exclude_cdn_cgi is not None:
            self._values["exclude_cdn_cgi"] = exclude_cdn_cgi
        if exclude_urls is not None:
            self._values["exclude_urls"] = exclude_urls
        if export is not None:
            self._values["export"] = export
        if hosts is not None:
            self._values["hosts"] = hosts
        if max_items is not None:
            self._values["max_items"] = max_items
        if order_by is not None:
            self._values["order_by"] = order_by
        if page is not None:
            self._values["page"] = page
        if page_url is not None:
            self._values["page_url"] = page_url
        if per_page is not None:
            self._values["per_page"] = per_page
        if prioritize_malicious is not None:
            self._values["prioritize_malicious"] = prioritize_malicious
        if status is not None:
            self._values["status"] = status
        if urls is not None:
            self._values["urls"] = urls

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#zone_id DataCloudflarePageShieldConnectionsList#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def direction(self) -> typing.Optional[builtins.str]:
        '''The direction used to sort returned connections. Available values: "asc", "desc".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#direction DataCloudflarePageShieldConnectionsList#direction}
        '''
        result = self._values.get("direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude_cdn_cgi(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When true, excludes connections seen in a ``/cdn-cgi`` path from the returned connections. The default value is true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#exclude_cdn_cgi DataCloudflarePageShieldConnectionsList#exclude_cdn_cgi}
        '''
        result = self._values.get("exclude_cdn_cgi")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def exclude_urls(self) -> typing.Optional[builtins.str]:
        '''Excludes connections whose URL contains one of the URL-encoded URLs separated by commas.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#exclude_urls DataCloudflarePageShieldConnectionsList#exclude_urls}
        '''
        result = self._values.get("exclude_urls")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def export(self) -> typing.Optional[builtins.str]:
        '''Export the list of connections as a file. Available values: "csv".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#export DataCloudflarePageShieldConnectionsList#export}
        '''
        result = self._values.get("export")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hosts(self) -> typing.Optional[builtins.str]:
        '''Includes connections that match one or more URL-encoded hostnames separated by commas.

        Wildcards are supported at the start and end of each hostname to support starts with, ends with
        and contains. If no wildcards are used, results will be filtered by exact match

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#hosts DataCloudflarePageShieldConnectionsList#hosts}
        '''
        result = self._values.get("hosts")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_items(self) -> typing.Optional[jsii.Number]:
        '''Max items to fetch, default: 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#max_items DataCloudflarePageShieldConnectionsList#max_items}
        '''
        result = self._values.get("max_items")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def order_by(self) -> typing.Optional[builtins.str]:
        '''The field used to sort returned connections. Available values: "first_seen_at", "last_seen_at".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#order_by DataCloudflarePageShieldConnectionsList#order_by}
        '''
        result = self._values.get("order_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def page(self) -> typing.Optional[builtins.str]:
        '''The current page number of the paginated results.

        We additionally support a special value "all". When "all" is used, the API will return all the connections
        with the applied filters in a single page. This feature is best-effort and it may only work for zones with
        a low number of connections

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#page DataCloudflarePageShieldConnectionsList#page}
        '''
        result = self._values.get("page")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def page_url(self) -> typing.Optional[builtins.str]:
        '''Includes connections that match one or more page URLs (separated by commas) where they were last seen.

        Wildcards are supported at the start and end of each page URL to support starts with, ends with
        and contains. If no wildcards are used, results will be filtered by exact match

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#page_url DataCloudflarePageShieldConnectionsList#page_url}
        '''
        result = self._values.get("page_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def per_page(self) -> typing.Optional[jsii.Number]:
        '''The number of results per page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#per_page DataCloudflarePageShieldConnectionsList#per_page}
        '''
        result = self._values.get("per_page")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def prioritize_malicious(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When true, malicious connections appear first in the returned connections.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#prioritize_malicious DataCloudflarePageShieldConnectionsList#prioritize_malicious}
        '''
        result = self._values.get("prioritize_malicious")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Filters the returned connections using a comma-separated list of connection statuses.

        Accepted values: ``active``, ``infrequent``, and ``inactive``. The default value is ``active``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#status DataCloudflarePageShieldConnectionsList#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def urls(self) -> typing.Optional[builtins.str]:
        '''Includes connections whose URL contain one or more URL-encoded URLs separated by commas.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/page_shield_connections_list#urls DataCloudflarePageShieldConnectionsList#urls}
        '''
        result = self._values.get("urls")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePageShieldConnectionsListConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePageShieldConnectionsList.DataCloudflarePageShieldConnectionsListResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePageShieldConnectionsListResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePageShieldConnectionsListResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePageShieldConnectionsListResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePageShieldConnectionsList.DataCloudflarePageShieldConnectionsListResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d65708d155b67b112a1c384347eacb97a1fb16b290e108cb05045c47520fd7dd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflarePageShieldConnectionsListResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a24b32ccd7c9d12ad371b42a257074ba4c156dccd981cd33262dd294c78c3799)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflarePageShieldConnectionsListResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8026cf72a6184bedf3194f058376c498ac31466dbfe77e0924f206750ba9ca15)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ae22d88b391d2ff104c8bf38bb66347013106608f411b36b1da668728be77a5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e1b3458bb80eb9e0023c4e82de3cc837164395f3c94d56280078755aa931a0b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePageShieldConnectionsListResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePageShieldConnectionsList.DataCloudflarePageShieldConnectionsListResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ac70fe4032ab8cca505ca5021b2e4e707ed03055d4a57dd882fb7bec9c22d90)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="addedAt")
    def added_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "addedAt"))

    @builtins.property
    @jsii.member(jsii_name="domainReportedMalicious")
    def domain_reported_malicious(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "domainReportedMalicious"))

    @builtins.property
    @jsii.member(jsii_name="firstPageUrl")
    def first_page_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firstPageUrl"))

    @builtins.property
    @jsii.member(jsii_name="firstSeenAt")
    def first_seen_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firstSeenAt"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="lastSeenAt")
    def last_seen_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastSeenAt"))

    @builtins.property
    @jsii.member(jsii_name="maliciousDomainCategories")
    def malicious_domain_categories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "maliciousDomainCategories"))

    @builtins.property
    @jsii.member(jsii_name="maliciousUrlCategories")
    def malicious_url_categories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "maliciousUrlCategories"))

    @builtins.property
    @jsii.member(jsii_name="pageUrls")
    def page_urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pageUrls"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="urlContainsCdnCgiPath")
    def url_contains_cdn_cgi_path(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "urlContainsCdnCgiPath"))

    @builtins.property
    @jsii.member(jsii_name="urlReportedMalicious")
    def url_reported_malicious(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "urlReportedMalicious"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePageShieldConnectionsListResult]:
        return typing.cast(typing.Optional[DataCloudflarePageShieldConnectionsListResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePageShieldConnectionsListResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3217f552c4fbb7ace878cd9098bff07a3467970844cbebed9182f4555689ccca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflarePageShieldConnectionsList",
    "DataCloudflarePageShieldConnectionsListConfig",
    "DataCloudflarePageShieldConnectionsListResult",
    "DataCloudflarePageShieldConnectionsListResultList",
    "DataCloudflarePageShieldConnectionsListResultOutputReference",
]

publication.publish()

def _typecheckingstub__a797c2e002ad86d260aa35ec8050736e86b5319a014eab70741f4d8a24eb0c97(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    zone_id: builtins.str,
    direction: typing.Optional[builtins.str] = None,
    exclude_cdn_cgi: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exclude_urls: typing.Optional[builtins.str] = None,
    export: typing.Optional[builtins.str] = None,
    hosts: typing.Optional[builtins.str] = None,
    max_items: typing.Optional[jsii.Number] = None,
    order_by: typing.Optional[builtins.str] = None,
    page: typing.Optional[builtins.str] = None,
    page_url: typing.Optional[builtins.str] = None,
    per_page: typing.Optional[jsii.Number] = None,
    prioritize_malicious: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    status: typing.Optional[builtins.str] = None,
    urls: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a07333733b7ad59792b3e089afd9a373db280c1313ba415b8e16c12453cd4ca9(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b110686458e0cc74eed26f69e9461fbd482fe16314f1e840cf44903679a5a7b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91e684acd41c1b644049ae8f9884f769fc3c859b6a87d50430b380b16322f49d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e90c9e7bfff741a77d84434520b2de38fcc7a71335964e38e82c22520a31543(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b48de5dc762bf657ad493511bd19806bdd3658eddad7ebc3743d81e2852eeb40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__682c87eb443c1b714707c123823159eb36e99c165575dccbe2eb38555cfc7835(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__808f41bafe8c5a03c9711396f3be21e738e246be15833e3674fcfd4e28811d7d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c86b3f1f5caa08fe0e608a67ca7867af96ec6d6464cfcda53d02e4432abfa7b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37b564286784b71b69ea44449b983477ce78458840ae4db89d192431cf03e9fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eaef4b6c64f303ec92c1ec2d8a18053f92021c4d888922405d7b0953ecf53c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8aff4d5420339c9d5d8f87e060a4a5bf95a752c638e10248be02e06b39c8caec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b33a97a12e7fddf86706ec43bd271e7e1132133c844ed783880b08d2e602e7fc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21be6b402e889b91c69905a075ab065a55332e8b0765cbf12463c9ea47e9a33f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59c27bd77bdff10520b3faa3478eb1969406f84b7ae0db71322bc3e9f1164c55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d17379a7cf84c751bcc6622e291be41e0520c02cc305aa12026bd9863d36e57f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44cb008638b750e3489f34e1cad53d4cd35476267ced179c05697a9c8377555f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: builtins.str,
    direction: typing.Optional[builtins.str] = None,
    exclude_cdn_cgi: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exclude_urls: typing.Optional[builtins.str] = None,
    export: typing.Optional[builtins.str] = None,
    hosts: typing.Optional[builtins.str] = None,
    max_items: typing.Optional[jsii.Number] = None,
    order_by: typing.Optional[builtins.str] = None,
    page: typing.Optional[builtins.str] = None,
    page_url: typing.Optional[builtins.str] = None,
    per_page: typing.Optional[jsii.Number] = None,
    prioritize_malicious: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    status: typing.Optional[builtins.str] = None,
    urls: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d65708d155b67b112a1c384347eacb97a1fb16b290e108cb05045c47520fd7dd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a24b32ccd7c9d12ad371b42a257074ba4c156dccd981cd33262dd294c78c3799(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8026cf72a6184bedf3194f058376c498ac31466dbfe77e0924f206750ba9ca15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ae22d88b391d2ff104c8bf38bb66347013106608f411b36b1da668728be77a5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1b3458bb80eb9e0023c4e82de3cc837164395f3c94d56280078755aa931a0b5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ac70fe4032ab8cca505ca5021b2e4e707ed03055d4a57dd882fb7bec9c22d90(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3217f552c4fbb7ace878cd9098bff07a3467970844cbebed9182f4555689ccca(
    value: typing.Optional[DataCloudflarePageShieldConnectionsListResult],
) -> None:
    """Type checking stubs"""
    pass
