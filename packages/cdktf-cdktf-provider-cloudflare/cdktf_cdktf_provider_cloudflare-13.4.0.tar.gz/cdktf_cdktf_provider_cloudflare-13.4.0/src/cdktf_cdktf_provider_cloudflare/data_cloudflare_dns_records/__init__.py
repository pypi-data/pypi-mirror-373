r'''
# `data_cloudflare_dns_records`

Refer to the Terraform Registry for docs: [`data_cloudflare_dns_records`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records).
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


class DataCloudflareDnsRecords(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecords",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records cloudflare_dns_records}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        zone_id: builtins.str,
        comment: typing.Optional[typing.Union["DataCloudflareDnsRecordsComment", typing.Dict[builtins.str, typing.Any]]] = None,
        content: typing.Optional[typing.Union["DataCloudflareDnsRecordsContent", typing.Dict[builtins.str, typing.Any]]] = None,
        direction: typing.Optional[builtins.str] = None,
        match: typing.Optional[builtins.str] = None,
        max_items: typing.Optional[jsii.Number] = None,
        name: typing.Optional[typing.Union["DataCloudflareDnsRecordsName", typing.Dict[builtins.str, typing.Any]]] = None,
        order: typing.Optional[builtins.str] = None,
        proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        search: typing.Optional[builtins.str] = None,
        tag: typing.Optional[typing.Union["DataCloudflareDnsRecordsTag", typing.Dict[builtins.str, typing.Any]]] = None,
        tag_match: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records cloudflare_dns_records} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#zone_id DataCloudflareDnsRecords#zone_id}
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#comment DataCloudflareDnsRecords#comment}.
        :param content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#content DataCloudflareDnsRecords#content}.
        :param direction: Direction to order DNS records in. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#direction DataCloudflareDnsRecords#direction}
        :param match: Whether to match all search requirements or at least one (any). If set to ``all``, acts like a logical AND between filters. If set to ``any``, acts like a logical OR instead. Note that the interaction between tag filters is controlled by the ``tag-match`` parameter instead. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#match DataCloudflareDnsRecords#match}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#max_items DataCloudflareDnsRecords#max_items}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#name DataCloudflareDnsRecords#name}.
        :param order: Field to order DNS records by. Available values: "type", "name", "content", "ttl", "proxied". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#order DataCloudflareDnsRecords#order}
        :param proxied: Whether the record is receiving the performance and security benefits of Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#proxied DataCloudflareDnsRecords#proxied}
        :param search: Allows searching in multiple properties of a DNS record simultaneously. This parameter is intended for human users, not automation. Its exact behavior is intentionally left unspecified and is subject to change in the future. This parameter works independently of the ``match`` setting. For automated searches, please use the other available parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#search DataCloudflareDnsRecords#search}
        :param tag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#tag DataCloudflareDnsRecords#tag}.
        :param tag_match: Whether to match all tag search requirements or at least one (any). If set to ``all``, acts like a logical AND between tag filters. If set to ``any``, acts like a logical OR instead. Note that the regular ``match`` parameter is still used to combine the resulting condition with other filters that aren't related to tags. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#tag_match DataCloudflareDnsRecords#tag_match}
        :param type: Record type. Available values: "A", "AAAA", "CAA", "CERT", "CNAME", "DNSKEY", "DS", "HTTPS", "LOC", "MX", "NAPTR", "NS", "OPENPGPKEY", "PTR", "SMIMEA", "SRV", "SSHFP", "SVCB", "TLSA", "TXT", "URI". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#type DataCloudflareDnsRecords#type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d64fe25b447e9b86a416fb1fc0efa8ca67ba86b1f2b1fe66823eb909202ebb21)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareDnsRecordsConfig(
            zone_id=zone_id,
            comment=comment,
            content=content,
            direction=direction,
            match=match,
            max_items=max_items,
            name=name,
            order=order,
            proxied=proxied,
            search=search,
            tag=tag,
            tag_match=tag_match,
            type=type,
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
        '''Generates CDKTF code for importing a DataCloudflareDnsRecords resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareDnsRecords to import.
        :param import_from_id: The id of the existing DataCloudflareDnsRecords that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareDnsRecords to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1be17faa4ddc92c4f1c1bed26babfe97a80ba4607d1fd6106daadc95f784970)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putComment")
    def put_comment(
        self,
        *,
        absent: typing.Optional[builtins.str] = None,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        present: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param absent: If this parameter is present, only records *without* a comment are returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#absent DataCloudflareDnsRecords#absent}
        :param contains: Substring of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        :param endswith: Suffix of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        :param exact: Exact value of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        :param present: If this parameter is present, only records *with* a comment are returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#present DataCloudflareDnsRecords#present}
        :param startswith: Prefix of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        value = DataCloudflareDnsRecordsComment(
            absent=absent,
            contains=contains,
            endswith=endswith,
            exact=exact,
            present=present,
            startswith=startswith,
        )

        return typing.cast(None, jsii.invoke(self, "putComment", [value]))

    @jsii.member(jsii_name="putContent")
    def put_content(
        self,
        *,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param contains: Substring of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        :param endswith: Suffix of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        :param exact: Exact value of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        :param startswith: Prefix of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        value = DataCloudflareDnsRecordsContent(
            contains=contains, endswith=endswith, exact=exact, startswith=startswith
        )

        return typing.cast(None, jsii.invoke(self, "putContent", [value]))

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
        :param contains: Substring of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        :param endswith: Suffix of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        :param exact: Exact value of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        :param startswith: Prefix of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        value = DataCloudflareDnsRecordsName(
            contains=contains, endswith=endswith, exact=exact, startswith=startswith
        )

        return typing.cast(None, jsii.invoke(self, "putName", [value]))

    @jsii.member(jsii_name="putTag")
    def put_tag(
        self,
        *,
        absent: typing.Optional[builtins.str] = None,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        present: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param absent: Name of a tag which must *not* be present on the DNS record. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#absent DataCloudflareDnsRecords#absent}
        :param contains: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value contains ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        :param endswith: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value ends with ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        :param exact: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value is ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        :param present: Name of a tag which must be present on the DNS record. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#present DataCloudflareDnsRecords#present}
        :param startswith: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value starts with ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        value = DataCloudflareDnsRecordsTag(
            absent=absent,
            contains=contains,
            endswith=endswith,
            exact=exact,
            present=present,
            startswith=startswith,
        )

        return typing.cast(None, jsii.invoke(self, "putTag", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetContent")
    def reset_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContent", []))

    @jsii.member(jsii_name="resetDirection")
    def reset_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirection", []))

    @jsii.member(jsii_name="resetMatch")
    def reset_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatch", []))

    @jsii.member(jsii_name="resetMaxItems")
    def reset_max_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxItems", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOrder")
    def reset_order(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrder", []))

    @jsii.member(jsii_name="resetProxied")
    def reset_proxied(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProxied", []))

    @jsii.member(jsii_name="resetSearch")
    def reset_search(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearch", []))

    @jsii.member(jsii_name="resetTag")
    def reset_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTag", []))

    @jsii.member(jsii_name="resetTagMatch")
    def reset_tag_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagMatch", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
    @jsii.member(jsii_name="comment")
    def comment(self) -> "DataCloudflareDnsRecordsCommentOutputReference":
        return typing.cast("DataCloudflareDnsRecordsCommentOutputReference", jsii.get(self, "comment"))

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> "DataCloudflareDnsRecordsContentOutputReference":
        return typing.cast("DataCloudflareDnsRecordsContentOutputReference", jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> "DataCloudflareDnsRecordsNameOutputReference":
        return typing.cast("DataCloudflareDnsRecordsNameOutputReference", jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="result")
    def result(self) -> "DataCloudflareDnsRecordsResultList":
        return typing.cast("DataCloudflareDnsRecordsResultList", jsii.get(self, "result"))

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> "DataCloudflareDnsRecordsTagOutputReference":
        return typing.cast("DataCloudflareDnsRecordsTagOutputReference", jsii.get(self, "tag"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordsComment"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordsComment"]], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="contentInput")
    def content_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordsContent"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordsContent"]], jsii.get(self, "contentInput"))

    @builtins.property
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property
    @jsii.member(jsii_name="matchInput")
    def match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "matchInput"))

    @builtins.property
    @jsii.member(jsii_name="maxItemsInput")
    def max_items_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxItemsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordsName"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordsName"]], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="orderInput")
    def order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orderInput"))

    @builtins.property
    @jsii.member(jsii_name="proxiedInput")
    def proxied_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "proxiedInput"))

    @builtins.property
    @jsii.member(jsii_name="searchInput")
    def search_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "searchInput"))

    @builtins.property
    @jsii.member(jsii_name="tagInput")
    def tag_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordsTag"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordsTag"]], jsii.get(self, "tagInput"))

    @builtins.property
    @jsii.member(jsii_name="tagMatchInput")
    def tag_match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagMatchInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__2d3ef638cfb114abb955a3ae04d283a238fce70c54743b1687fa86c19760c87e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="match")
    def match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "match"))

    @match.setter
    def match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed6b8865831d5726939aae302f53303e40c503d6bc5e55d9b047efa5c1d03d2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "match", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxItems")
    def max_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxItems"))

    @max_items.setter
    def max_items(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fad74243d6b06e2e0d3dacf54eb7cd2663836ee442fee935de5020a1621b1fe5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxItems", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="order")
    def order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "order"))

    @order.setter
    def order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c72dfac254378b931ef8e3044ffd64846fcbe5672f27454f29748d16dafc650)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "order", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proxied")
    def proxied(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "proxied"))

    @proxied.setter
    def proxied(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0effa05a870bcc1f43eddd6c1d2be62b81a6004bada50e924ee1a4b2fb57083)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxied", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="search")
    def search(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "search"))

    @search.setter
    def search(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47b3ecc2dcadb653a11e11c1632f6e5983f04cd732d1971488e7d16d4434458b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "search", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tagMatch")
    def tag_match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagMatch"))

    @tag_match.setter
    def tag_match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60edadf1e5b494d65bd90c83fca6aa17cd933ed5f8b9b46907d31f155e00478f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagMatch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d35d70f2b563c5b32c4b7919994452ce5947ab613ac97d94ed2d20637722ece3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8dcf7b6042a5a3a53b277af0bdee6b82a2c39aef69b2990b9429359a4da096e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsComment",
    jsii_struct_bases=[],
    name_mapping={
        "absent": "absent",
        "contains": "contains",
        "endswith": "endswith",
        "exact": "exact",
        "present": "present",
        "startswith": "startswith",
    },
)
class DataCloudflareDnsRecordsComment:
    def __init__(
        self,
        *,
        absent: typing.Optional[builtins.str] = None,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        present: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param absent: If this parameter is present, only records *without* a comment are returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#absent DataCloudflareDnsRecords#absent}
        :param contains: Substring of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        :param endswith: Suffix of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        :param exact: Exact value of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        :param present: If this parameter is present, only records *with* a comment are returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#present DataCloudflareDnsRecords#present}
        :param startswith: Prefix of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c665fd4e35519b124d2603726477075e971fd8cc6bcf8ed4a3c45f24541428a0)
            check_type(argname="argument absent", value=absent, expected_type=type_hints["absent"])
            check_type(argname="argument contains", value=contains, expected_type=type_hints["contains"])
            check_type(argname="argument endswith", value=endswith, expected_type=type_hints["endswith"])
            check_type(argname="argument exact", value=exact, expected_type=type_hints["exact"])
            check_type(argname="argument present", value=present, expected_type=type_hints["present"])
            check_type(argname="argument startswith", value=startswith, expected_type=type_hints["startswith"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if absent is not None:
            self._values["absent"] = absent
        if contains is not None:
            self._values["contains"] = contains
        if endswith is not None:
            self._values["endswith"] = endswith
        if exact is not None:
            self._values["exact"] = exact
        if present is not None:
            self._values["present"] = present
        if startswith is not None:
            self._values["startswith"] = startswith

    @builtins.property
    def absent(self) -> typing.Optional[builtins.str]:
        '''If this parameter is present, only records *without* a comment are returned.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#absent DataCloudflareDnsRecords#absent}
        '''
        result = self._values.get("absent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contains(self) -> typing.Optional[builtins.str]:
        '''Substring of the DNS record comment. Comment filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        '''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endswith(self) -> typing.Optional[builtins.str]:
        '''Suffix of the DNS record comment. Comment filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        '''
        result = self._values.get("endswith")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Exact value of the DNS record comment. Comment filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def present(self) -> typing.Optional[builtins.str]:
        '''If this parameter is present, only records *with* a comment are returned.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#present DataCloudflareDnsRecords#present}
        '''
        result = self._values.get("present")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startswith(self) -> typing.Optional[builtins.str]:
        '''Prefix of the DNS record comment. Comment filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        result = self._values.get("startswith")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordsComment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordsCommentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsCommentOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72a178f7c5ecb22bd79dcd6586aa980225e8b6d86966591c74e8d3f9a5a6be8c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAbsent")
    def reset_absent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAbsent", []))

    @jsii.member(jsii_name="resetContains")
    def reset_contains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContains", []))

    @jsii.member(jsii_name="resetEndswith")
    def reset_endswith(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndswith", []))

    @jsii.member(jsii_name="resetExact")
    def reset_exact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExact", []))

    @jsii.member(jsii_name="resetPresent")
    def reset_present(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPresent", []))

    @jsii.member(jsii_name="resetStartswith")
    def reset_startswith(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartswith", []))

    @builtins.property
    @jsii.member(jsii_name="absentInput")
    def absent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "absentInput"))

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
    @jsii.member(jsii_name="presentInput")
    def present_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "presentInput"))

    @builtins.property
    @jsii.member(jsii_name="startswithInput")
    def startswith_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startswithInput"))

    @builtins.property
    @jsii.member(jsii_name="absent")
    def absent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "absent"))

    @absent.setter
    def absent(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4cad05b23cd0983814e09200cf2d5de5fe32b6befcb6782e3e8bede21ca797e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "absent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contains")
    def contains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contains"))

    @contains.setter
    def contains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b5ca2c4248489551faaeceaeaa3483c1644a5d8aac6193dc2aa95e7eb379d38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endswith")
    def endswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endswith"))

    @endswith.setter
    def endswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5a6ecac1989467d45d8b827dae6f1bd64ab42eab8851bacdd23d24c31444433)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65d86b6865a808600db5031bbdae7e02794eb3b57e63de45aaebe7530833c566)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="present")
    def present(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "present"))

    @present.setter
    def present(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b5e5a07943cc48119d4b35ca77bed99485506d5204d44ca0b25f23257886124)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "present", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startswith")
    def startswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startswith"))

    @startswith.setter
    def startswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42dbcff2cac2ccbe748ee371023f7b1b82e3a6c6d435ee562a0ba74be73e22db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsComment]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsComment]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsComment]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ebcd200e9cf20d1b525e07ab19e9797cc8862aa869bc403386d5a45a6552e73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsConfig",
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
        "comment": "comment",
        "content": "content",
        "direction": "direction",
        "match": "match",
        "max_items": "maxItems",
        "name": "name",
        "order": "order",
        "proxied": "proxied",
        "search": "search",
        "tag": "tag",
        "tag_match": "tagMatch",
        "type": "type",
    },
)
class DataCloudflareDnsRecordsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        comment: typing.Optional[typing.Union[DataCloudflareDnsRecordsComment, typing.Dict[builtins.str, typing.Any]]] = None,
        content: typing.Optional[typing.Union["DataCloudflareDnsRecordsContent", typing.Dict[builtins.str, typing.Any]]] = None,
        direction: typing.Optional[builtins.str] = None,
        match: typing.Optional[builtins.str] = None,
        max_items: typing.Optional[jsii.Number] = None,
        name: typing.Optional[typing.Union["DataCloudflareDnsRecordsName", typing.Dict[builtins.str, typing.Any]]] = None,
        order: typing.Optional[builtins.str] = None,
        proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        search: typing.Optional[builtins.str] = None,
        tag: typing.Optional[typing.Union["DataCloudflareDnsRecordsTag", typing.Dict[builtins.str, typing.Any]]] = None,
        tag_match: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#zone_id DataCloudflareDnsRecords#zone_id}
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#comment DataCloudflareDnsRecords#comment}.
        :param content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#content DataCloudflareDnsRecords#content}.
        :param direction: Direction to order DNS records in. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#direction DataCloudflareDnsRecords#direction}
        :param match: Whether to match all search requirements or at least one (any). If set to ``all``, acts like a logical AND between filters. If set to ``any``, acts like a logical OR instead. Note that the interaction between tag filters is controlled by the ``tag-match`` parameter instead. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#match DataCloudflareDnsRecords#match}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#max_items DataCloudflareDnsRecords#max_items}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#name DataCloudflareDnsRecords#name}.
        :param order: Field to order DNS records by. Available values: "type", "name", "content", "ttl", "proxied". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#order DataCloudflareDnsRecords#order}
        :param proxied: Whether the record is receiving the performance and security benefits of Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#proxied DataCloudflareDnsRecords#proxied}
        :param search: Allows searching in multiple properties of a DNS record simultaneously. This parameter is intended for human users, not automation. Its exact behavior is intentionally left unspecified and is subject to change in the future. This parameter works independently of the ``match`` setting. For automated searches, please use the other available parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#search DataCloudflareDnsRecords#search}
        :param tag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#tag DataCloudflareDnsRecords#tag}.
        :param tag_match: Whether to match all tag search requirements or at least one (any). If set to ``all``, acts like a logical AND between tag filters. If set to ``any``, acts like a logical OR instead. Note that the regular ``match`` parameter is still used to combine the resulting condition with other filters that aren't related to tags. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#tag_match DataCloudflareDnsRecords#tag_match}
        :param type: Record type. Available values: "A", "AAAA", "CAA", "CERT", "CNAME", "DNSKEY", "DS", "HTTPS", "LOC", "MX", "NAPTR", "NS", "OPENPGPKEY", "PTR", "SMIMEA", "SRV", "SSHFP", "SVCB", "TLSA", "TXT", "URI". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#type DataCloudflareDnsRecords#type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(comment, dict):
            comment = DataCloudflareDnsRecordsComment(**comment)
        if isinstance(content, dict):
            content = DataCloudflareDnsRecordsContent(**content)
        if isinstance(name, dict):
            name = DataCloudflareDnsRecordsName(**name)
        if isinstance(tag, dict):
            tag = DataCloudflareDnsRecordsTag(**tag)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0087e859b23b53faaa34de94be72335889d3507f820469c05f07e40e4dd955a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument match", value=match, expected_type=type_hints["match"])
            check_type(argname="argument max_items", value=max_items, expected_type=type_hints["max_items"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument order", value=order, expected_type=type_hints["order"])
            check_type(argname="argument proxied", value=proxied, expected_type=type_hints["proxied"])
            check_type(argname="argument search", value=search, expected_type=type_hints["search"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument tag_match", value=tag_match, expected_type=type_hints["tag_match"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
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
        if comment is not None:
            self._values["comment"] = comment
        if content is not None:
            self._values["content"] = content
        if direction is not None:
            self._values["direction"] = direction
        if match is not None:
            self._values["match"] = match
        if max_items is not None:
            self._values["max_items"] = max_items
        if name is not None:
            self._values["name"] = name
        if order is not None:
            self._values["order"] = order
        if proxied is not None:
            self._values["proxied"] = proxied
        if search is not None:
            self._values["search"] = search
        if tag is not None:
            self._values["tag"] = tag
        if tag_match is not None:
            self._values["tag_match"] = tag_match
        if type is not None:
            self._values["type"] = type

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#zone_id DataCloudflareDnsRecords#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[DataCloudflareDnsRecordsComment]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#comment DataCloudflareDnsRecords#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[DataCloudflareDnsRecordsComment], result)

    @builtins.property
    def content(self) -> typing.Optional["DataCloudflareDnsRecordsContent"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#content DataCloudflareDnsRecords#content}.'''
        result = self._values.get("content")
        return typing.cast(typing.Optional["DataCloudflareDnsRecordsContent"], result)

    @builtins.property
    def direction(self) -> typing.Optional[builtins.str]:
        '''Direction to order DNS records in. Available values: "asc", "desc".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#direction DataCloudflareDnsRecords#direction}
        '''
        result = self._values.get("direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def match(self) -> typing.Optional[builtins.str]:
        '''Whether to match all search requirements or at least one (any).

        If set to ``all``, acts like a logical AND between filters. If set to ``any``, acts like a logical OR instead. Note that the interaction between tag filters is controlled by the ``tag-match`` parameter instead.
        Available values: "any", "all".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#match DataCloudflareDnsRecords#match}
        '''
        result = self._values.get("match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_items(self) -> typing.Optional[jsii.Number]:
        '''Max items to fetch, default: 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#max_items DataCloudflareDnsRecords#max_items}
        '''
        result = self._values.get("max_items")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional["DataCloudflareDnsRecordsName"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#name DataCloudflareDnsRecords#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional["DataCloudflareDnsRecordsName"], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''Field to order DNS records by. Available values: "type", "name", "content", "ttl", "proxied".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#order DataCloudflareDnsRecords#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxied(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether the record is receiving the performance and security benefits of Cloudflare.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#proxied DataCloudflareDnsRecords#proxied}
        '''
        result = self._values.get("proxied")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def search(self) -> typing.Optional[builtins.str]:
        '''Allows searching in multiple properties of a DNS record simultaneously.

        This parameter is intended for human users, not automation. Its exact behavior is intentionally left unspecified and is subject to change in the future. This parameter works independently of the ``match`` setting. For automated searches, please use the other available parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#search DataCloudflareDnsRecords#search}
        '''
        result = self._values.get("search")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag(self) -> typing.Optional["DataCloudflareDnsRecordsTag"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#tag DataCloudflareDnsRecords#tag}.'''
        result = self._values.get("tag")
        return typing.cast(typing.Optional["DataCloudflareDnsRecordsTag"], result)

    @builtins.property
    def tag_match(self) -> typing.Optional[builtins.str]:
        '''Whether to match all tag search requirements or at least one (any).

        If set to ``all``, acts like a logical AND between tag filters. If set to ``any``, acts like a logical OR instead. Note that the regular ``match`` parameter is still used to combine the resulting condition with other filters that aren't related to tags.
        Available values: "any", "all".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#tag_match DataCloudflareDnsRecords#tag_match}
        '''
        result = self._values.get("tag_match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Record type.

        Available values: "A", "AAAA", "CAA", "CERT", "CNAME", "DNSKEY", "DS", "HTTPS", "LOC", "MX", "NAPTR", "NS", "OPENPGPKEY", "PTR", "SMIMEA", "SRV", "SSHFP", "SVCB", "TLSA", "TXT", "URI".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#type DataCloudflareDnsRecords#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsContent",
    jsii_struct_bases=[],
    name_mapping={
        "contains": "contains",
        "endswith": "endswith",
        "exact": "exact",
        "startswith": "startswith",
    },
)
class DataCloudflareDnsRecordsContent:
    def __init__(
        self,
        *,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param contains: Substring of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        :param endswith: Suffix of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        :param exact: Exact value of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        :param startswith: Prefix of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98b2397e58d8b9a553484adfbd8080242c002aa19f445509e0e5bdaff9e8bfad)
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
        '''Substring of the DNS record content. Content filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        '''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endswith(self) -> typing.Optional[builtins.str]:
        '''Suffix of the DNS record content. Content filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        '''
        result = self._values.get("endswith")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Exact value of the DNS record content. Content filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startswith(self) -> typing.Optional[builtins.str]:
        '''Prefix of the DNS record content. Content filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        result = self._values.get("startswith")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordsContent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordsContentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsContentOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__032a14bb84cc6d7ab959e16863142c6c61e22a47bd8d258b1d7d4d733e0e764c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__232f7d0252f8f5d2ca5f950fd034b674970a713e7a68451447f5c810a47f7852)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endswith")
    def endswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endswith"))

    @endswith.setter
    def endswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c03aa6e3df9e3ee30344e40ad77cbdcb2634aa679a61e767d8adc42d7308a42c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d89ad6dfc06fe181add3adc997a261bd93feb17224fcff63438f329b47afdf76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startswith")
    def startswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startswith"))

    @startswith.setter
    def startswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__402e883eac96f41bacc46e6b86a993e03a1a00706e1354037eae26e5de8d2e7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsContent]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsContent]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsContent]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27036bc10f7cac9d7bdddc76fb7495383b2dbe4878d1650c0c76c9f12f0fa224)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsName",
    jsii_struct_bases=[],
    name_mapping={
        "contains": "contains",
        "endswith": "endswith",
        "exact": "exact",
        "startswith": "startswith",
    },
)
class DataCloudflareDnsRecordsName:
    def __init__(
        self,
        *,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param contains: Substring of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        :param endswith: Suffix of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        :param exact: Exact value of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        :param startswith: Prefix of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52acab876a135a31cb51c375ea66e8cd5272374b01c674fa5a57ede6236db877)
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
        '''Substring of the DNS record name. Name filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        '''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endswith(self) -> typing.Optional[builtins.str]:
        '''Suffix of the DNS record name. Name filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        '''
        result = self._values.get("endswith")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Exact value of the DNS record name. Name filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startswith(self) -> typing.Optional[builtins.str]:
        '''Prefix of the DNS record name. Name filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        result = self._values.get("startswith")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordsName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordsNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsNameOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c94e49b2de5adba5f1f02dd74e876d549f06e7c9bab55c374fa0cce024b572b9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28390f792738f53189523faef7fcdaf8c598a307a8ba79c97daba71cb474c63a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endswith")
    def endswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endswith"))

    @endswith.setter
    def endswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a01a58a030af65672c24925333deaaf2fee403383e51b6310f1feaab715c90d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e74ecdeaf6074ca797c84fdd0301916ca46c5f4cac962492f9a53e064dbcb522)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startswith")
    def startswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startswith"))

    @startswith.setter
    def startswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3baabcb144983e61b93834b84daeeff1365bb651b07930b9f2172bc510210c89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsName]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsName]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7371dcf8efdfb1d3d0d68ddcfc36ba7fa1fe8d5dfe26d0b9d1a0db6683ec95d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareDnsRecordsResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordsResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsResultData",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareDnsRecordsResultData:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordsResultData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordsResultDataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsResultDataOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cde00a040f2333f8e4cd9e593c954f9029c9c3f004abc6cfbcb28cfc96f9a03)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "algorithm"))

    @builtins.property
    @jsii.member(jsii_name="altitude")
    def altitude(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "altitude"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="digest")
    def digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "digest"))

    @builtins.property
    @jsii.member(jsii_name="digestType")
    def digest_type(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "digestType"))

    @builtins.property
    @jsii.member(jsii_name="fingerprint")
    def fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fingerprint"))

    @builtins.property
    @jsii.member(jsii_name="flags")
    def flags(self) -> _cdktf_9a9027ec.AnyMap:
        return typing.cast(_cdktf_9a9027ec.AnyMap, jsii.get(self, "flags"))

    @builtins.property
    @jsii.member(jsii_name="keyTag")
    def key_tag(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keyTag"))

    @builtins.property
    @jsii.member(jsii_name="latDegrees")
    def lat_degrees(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latDegrees"))

    @builtins.property
    @jsii.member(jsii_name="latDirection")
    def lat_direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latDirection"))

    @builtins.property
    @jsii.member(jsii_name="latMinutes")
    def lat_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latMinutes"))

    @builtins.property
    @jsii.member(jsii_name="latSeconds")
    def lat_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latSeconds"))

    @builtins.property
    @jsii.member(jsii_name="longDegrees")
    def long_degrees(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longDegrees"))

    @builtins.property
    @jsii.member(jsii_name="longDirection")
    def long_direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "longDirection"))

    @builtins.property
    @jsii.member(jsii_name="longMinutes")
    def long_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longMinutes"))

    @builtins.property
    @jsii.member(jsii_name="longSeconds")
    def long_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longSeconds"))

    @builtins.property
    @jsii.member(jsii_name="matchingType")
    def matching_type(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "matchingType"))

    @builtins.property
    @jsii.member(jsii_name="order")
    def order(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "order"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="precisionHorz")
    def precision_horz(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precisionHorz"))

    @builtins.property
    @jsii.member(jsii_name="precisionVert")
    def precision_vert(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precisionVert"))

    @builtins.property
    @jsii.member(jsii_name="preference")
    def preference(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "preference"))

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "protocol"))

    @builtins.property
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @builtins.property
    @jsii.member(jsii_name="replacement")
    def replacement(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replacement"))

    @builtins.property
    @jsii.member(jsii_name="selector")
    def selector(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "selector"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tag"))

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="usage")
    def usage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "usage"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="weight")
    def weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weight"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataCloudflareDnsRecordsResultData]:
        return typing.cast(typing.Optional[DataCloudflareDnsRecordsResultData], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareDnsRecordsResultData],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be48b320a85629eb7635188d47adf2498849621f2e57bab85fd8838885cb319b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareDnsRecordsResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__12113aa8804c4c470c9598add6632f78ef0189a9927ac8559ce006561ec617eb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareDnsRecordsResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c318b40d66f739036c5a3e361ab79b1eb14bfcc00915d4377847ae59dc5470d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareDnsRecordsResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aec184bdca4f57ac179ab14db6dc861e60b9972acc0e1f08293c6372f38ba4bd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e6c6cf10fecccd497950ae3260ebf31a52aa49e15e73287535475bec9a185314)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4199c7b505494211c29bb1ab5ff5b8d879d0cc867e56d9c70d1cd1ca3fba5aae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareDnsRecordsResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b8594e309e683cb10a7c4ad812f51741ff616d3f9ee2be62774d84e6086e6edf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @builtins.property
    @jsii.member(jsii_name="commentModifiedOn")
    def comment_modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commentModifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> DataCloudflareDnsRecordsResultDataOutputReference:
        return typing.cast(DataCloudflareDnsRecordsResultDataOutputReference, jsii.get(self, "data"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="meta")
    def meta(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "meta"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @builtins.property
    @jsii.member(jsii_name="proxiable")
    def proxiable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "proxiable"))

    @builtins.property
    @jsii.member(jsii_name="proxied")
    def proxied(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "proxied"))

    @builtins.property
    @jsii.member(jsii_name="settings")
    def settings(self) -> "DataCloudflareDnsRecordsResultSettingsOutputReference":
        return typing.cast("DataCloudflareDnsRecordsResultSettingsOutputReference", jsii.get(self, "settings"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="tagsModifiedOn")
    def tags_modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagsModifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataCloudflareDnsRecordsResult]:
        return typing.cast(typing.Optional[DataCloudflareDnsRecordsResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareDnsRecordsResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5a9b809028a3d10b1afc93edc7e8449f51d3c7659e660e916b6ad565b7e2b53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsResultSettings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareDnsRecordsResultSettings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordsResultSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordsResultSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsResultSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d48c7d010807a6c1f750e2a2a7c60adb0218f44bdf480ba760b645faedfdd3c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="flattenCname")
    def flatten_cname(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "flattenCname"))

    @builtins.property
    @jsii.member(jsii_name="ipv4Only")
    def ipv4_only(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ipv4Only"))

    @builtins.property
    @jsii.member(jsii_name="ipv6Only")
    def ipv6_only(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ipv6Only"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataCloudflareDnsRecordsResultSettings]:
        return typing.cast(typing.Optional[DataCloudflareDnsRecordsResultSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareDnsRecordsResultSettings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a11d973a1ce681594731f930fe2fb6fa88ddda572c940de347f777040b7a88c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsTag",
    jsii_struct_bases=[],
    name_mapping={
        "absent": "absent",
        "contains": "contains",
        "endswith": "endswith",
        "exact": "exact",
        "present": "present",
        "startswith": "startswith",
    },
)
class DataCloudflareDnsRecordsTag:
    def __init__(
        self,
        *,
        absent: typing.Optional[builtins.str] = None,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        present: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param absent: Name of a tag which must *not* be present on the DNS record. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#absent DataCloudflareDnsRecords#absent}
        :param contains: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value contains ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        :param endswith: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value ends with ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        :param exact: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value is ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        :param present: Name of a tag which must be present on the DNS record. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#present DataCloudflareDnsRecords#present}
        :param startswith: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value starts with ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2083115598dbf751cd0b7532848abfaa23ffb232a89f84fdaacbf50880080709)
            check_type(argname="argument absent", value=absent, expected_type=type_hints["absent"])
            check_type(argname="argument contains", value=contains, expected_type=type_hints["contains"])
            check_type(argname="argument endswith", value=endswith, expected_type=type_hints["endswith"])
            check_type(argname="argument exact", value=exact, expected_type=type_hints["exact"])
            check_type(argname="argument present", value=present, expected_type=type_hints["present"])
            check_type(argname="argument startswith", value=startswith, expected_type=type_hints["startswith"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if absent is not None:
            self._values["absent"] = absent
        if contains is not None:
            self._values["contains"] = contains
        if endswith is not None:
            self._values["endswith"] = endswith
        if exact is not None:
            self._values["exact"] = exact
        if present is not None:
            self._values["present"] = present
        if startswith is not None:
            self._values["startswith"] = startswith

    @builtins.property
    def absent(self) -> typing.Optional[builtins.str]:
        '''Name of a tag which must *not* be present on the DNS record. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#absent DataCloudflareDnsRecords#absent}
        '''
        result = self._values.get("absent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contains(self) -> typing.Optional[builtins.str]:
        '''A tag and value, of the form ``<tag-name>:<tag-value>``.

        The API will only return DNS records that have a tag named ``<tag-name>`` whose value contains ``<tag-value>``. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#contains DataCloudflareDnsRecords#contains}
        '''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endswith(self) -> typing.Optional[builtins.str]:
        '''A tag and value, of the form ``<tag-name>:<tag-value>``.

        The API will only return DNS records that have a tag named ``<tag-name>`` whose value ends with ``<tag-value>``. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#endswith DataCloudflareDnsRecords#endswith}
        '''
        result = self._values.get("endswith")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''A tag and value, of the form ``<tag-name>:<tag-value>``.

        The API will only return DNS records that have a tag named ``<tag-name>`` whose value is ``<tag-value>``. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#exact DataCloudflareDnsRecords#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def present(self) -> typing.Optional[builtins.str]:
        '''Name of a tag which must be present on the DNS record. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#present DataCloudflareDnsRecords#present}
        '''
        result = self._values.get("present")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startswith(self) -> typing.Optional[builtins.str]:
        '''A tag and value, of the form ``<tag-name>:<tag-value>``.

        The API will only return DNS records that have a tag named ``<tag-name>`` whose value starts with ``<tag-value>``. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_records#startswith DataCloudflareDnsRecords#startswith}
        '''
        result = self._values.get("startswith")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordsTag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordsTagOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecords.DataCloudflareDnsRecordsTagOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__250ea2fa23836200c9af8ca7a7abb5bcd5d2f260a40370bdc4d56d6a4f9ac61e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAbsent")
    def reset_absent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAbsent", []))

    @jsii.member(jsii_name="resetContains")
    def reset_contains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContains", []))

    @jsii.member(jsii_name="resetEndswith")
    def reset_endswith(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndswith", []))

    @jsii.member(jsii_name="resetExact")
    def reset_exact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExact", []))

    @jsii.member(jsii_name="resetPresent")
    def reset_present(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPresent", []))

    @jsii.member(jsii_name="resetStartswith")
    def reset_startswith(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartswith", []))

    @builtins.property
    @jsii.member(jsii_name="absentInput")
    def absent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "absentInput"))

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
    @jsii.member(jsii_name="presentInput")
    def present_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "presentInput"))

    @builtins.property
    @jsii.member(jsii_name="startswithInput")
    def startswith_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startswithInput"))

    @builtins.property
    @jsii.member(jsii_name="absent")
    def absent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "absent"))

    @absent.setter
    def absent(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bacddee44e0539838e240f302b319ef96f7f792c29d8c662ab173caa11baf962)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "absent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contains")
    def contains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contains"))

    @contains.setter
    def contains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4409321ef799a0378af26acb68949bb42990f3ac9c46c07b8087ba81021ea5a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endswith")
    def endswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endswith"))

    @endswith.setter
    def endswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6098c49869e29368bd805f63464bbd348fae31914ead9ea876a4fa6d9f1d2f1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed990b4c9c179e995a96df6d3772acc54ed3614f75ee3a5d3c9647630afc3a3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="present")
    def present(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "present"))

    @present.setter
    def present(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e458eaded4ef911782d3be46f2cb4db71986697a0f78310b1891c33cc4ae3f13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "present", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startswith")
    def startswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startswith"))

    @startswith.setter
    def startswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8569f27550d8015e8ac3c2f1c45b1fbb32566900542287aee6829559aeb20368)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsTag]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsTag]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsTag]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a40d07b0b1e44807c094f509812bc454c0dcc4ea3e527359433e40312c5e107f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareDnsRecords",
    "DataCloudflareDnsRecordsComment",
    "DataCloudflareDnsRecordsCommentOutputReference",
    "DataCloudflareDnsRecordsConfig",
    "DataCloudflareDnsRecordsContent",
    "DataCloudflareDnsRecordsContentOutputReference",
    "DataCloudflareDnsRecordsName",
    "DataCloudflareDnsRecordsNameOutputReference",
    "DataCloudflareDnsRecordsResult",
    "DataCloudflareDnsRecordsResultData",
    "DataCloudflareDnsRecordsResultDataOutputReference",
    "DataCloudflareDnsRecordsResultList",
    "DataCloudflareDnsRecordsResultOutputReference",
    "DataCloudflareDnsRecordsResultSettings",
    "DataCloudflareDnsRecordsResultSettingsOutputReference",
    "DataCloudflareDnsRecordsTag",
    "DataCloudflareDnsRecordsTagOutputReference",
]

publication.publish()

def _typecheckingstub__d64fe25b447e9b86a416fb1fc0efa8ca67ba86b1f2b1fe66823eb909202ebb21(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    zone_id: builtins.str,
    comment: typing.Optional[typing.Union[DataCloudflareDnsRecordsComment, typing.Dict[builtins.str, typing.Any]]] = None,
    content: typing.Optional[typing.Union[DataCloudflareDnsRecordsContent, typing.Dict[builtins.str, typing.Any]]] = None,
    direction: typing.Optional[builtins.str] = None,
    match: typing.Optional[builtins.str] = None,
    max_items: typing.Optional[jsii.Number] = None,
    name: typing.Optional[typing.Union[DataCloudflareDnsRecordsName, typing.Dict[builtins.str, typing.Any]]] = None,
    order: typing.Optional[builtins.str] = None,
    proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    search: typing.Optional[builtins.str] = None,
    tag: typing.Optional[typing.Union[DataCloudflareDnsRecordsTag, typing.Dict[builtins.str, typing.Any]]] = None,
    tag_match: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a1be17faa4ddc92c4f1c1bed26babfe97a80ba4607d1fd6106daadc95f784970(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d3ef638cfb114abb955a3ae04d283a238fce70c54743b1687fa86c19760c87e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed6b8865831d5726939aae302f53303e40c503d6bc5e55d9b047efa5c1d03d2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fad74243d6b06e2e0d3dacf54eb7cd2663836ee442fee935de5020a1621b1fe5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c72dfac254378b931ef8e3044ffd64846fcbe5672f27454f29748d16dafc650(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0effa05a870bcc1f43eddd6c1d2be62b81a6004bada50e924ee1a4b2fb57083(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47b3ecc2dcadb653a11e11c1632f6e5983f04cd732d1971488e7d16d4434458b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60edadf1e5b494d65bd90c83fca6aa17cd933ed5f8b9b46907d31f155e00478f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d35d70f2b563c5b32c4b7919994452ce5947ab613ac97d94ed2d20637722ece3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8dcf7b6042a5a3a53b277af0bdee6b82a2c39aef69b2990b9429359a4da096e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c665fd4e35519b124d2603726477075e971fd8cc6bcf8ed4a3c45f24541428a0(
    *,
    absent: typing.Optional[builtins.str] = None,
    contains: typing.Optional[builtins.str] = None,
    endswith: typing.Optional[builtins.str] = None,
    exact: typing.Optional[builtins.str] = None,
    present: typing.Optional[builtins.str] = None,
    startswith: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72a178f7c5ecb22bd79dcd6586aa980225e8b6d86966591c74e8d3f9a5a6be8c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4cad05b23cd0983814e09200cf2d5de5fe32b6befcb6782e3e8bede21ca797e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b5ca2c4248489551faaeceaeaa3483c1644a5d8aac6193dc2aa95e7eb379d38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5a6ecac1989467d45d8b827dae6f1bd64ab42eab8851bacdd23d24c31444433(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65d86b6865a808600db5031bbdae7e02794eb3b57e63de45aaebe7530833c566(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b5e5a07943cc48119d4b35ca77bed99485506d5204d44ca0b25f23257886124(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42dbcff2cac2ccbe748ee371023f7b1b82e3a6c6d435ee562a0ba74be73e22db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ebcd200e9cf20d1b525e07ab19e9797cc8862aa869bc403386d5a45a6552e73(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsComment]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0087e859b23b53faaa34de94be72335889d3507f820469c05f07e40e4dd955a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: builtins.str,
    comment: typing.Optional[typing.Union[DataCloudflareDnsRecordsComment, typing.Dict[builtins.str, typing.Any]]] = None,
    content: typing.Optional[typing.Union[DataCloudflareDnsRecordsContent, typing.Dict[builtins.str, typing.Any]]] = None,
    direction: typing.Optional[builtins.str] = None,
    match: typing.Optional[builtins.str] = None,
    max_items: typing.Optional[jsii.Number] = None,
    name: typing.Optional[typing.Union[DataCloudflareDnsRecordsName, typing.Dict[builtins.str, typing.Any]]] = None,
    order: typing.Optional[builtins.str] = None,
    proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    search: typing.Optional[builtins.str] = None,
    tag: typing.Optional[typing.Union[DataCloudflareDnsRecordsTag, typing.Dict[builtins.str, typing.Any]]] = None,
    tag_match: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98b2397e58d8b9a553484adfbd8080242c002aa19f445509e0e5bdaff9e8bfad(
    *,
    contains: typing.Optional[builtins.str] = None,
    endswith: typing.Optional[builtins.str] = None,
    exact: typing.Optional[builtins.str] = None,
    startswith: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__032a14bb84cc6d7ab959e16863142c6c61e22a47bd8d258b1d7d4d733e0e764c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__232f7d0252f8f5d2ca5f950fd034b674970a713e7a68451447f5c810a47f7852(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c03aa6e3df9e3ee30344e40ad77cbdcb2634aa679a61e767d8adc42d7308a42c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d89ad6dfc06fe181add3adc997a261bd93feb17224fcff63438f329b47afdf76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__402e883eac96f41bacc46e6b86a993e03a1a00706e1354037eae26e5de8d2e7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27036bc10f7cac9d7bdddc76fb7495383b2dbe4878d1650c0c76c9f12f0fa224(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsContent]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52acab876a135a31cb51c375ea66e8cd5272374b01c674fa5a57ede6236db877(
    *,
    contains: typing.Optional[builtins.str] = None,
    endswith: typing.Optional[builtins.str] = None,
    exact: typing.Optional[builtins.str] = None,
    startswith: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c94e49b2de5adba5f1f02dd74e876d549f06e7c9bab55c374fa0cce024b572b9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28390f792738f53189523faef7fcdaf8c598a307a8ba79c97daba71cb474c63a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a01a58a030af65672c24925333deaaf2fee403383e51b6310f1feaab715c90d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e74ecdeaf6074ca797c84fdd0301916ca46c5f4cac962492f9a53e064dbcb522(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3baabcb144983e61b93834b84daeeff1365bb651b07930b9f2172bc510210c89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7371dcf8efdfb1d3d0d68ddcfc36ba7fa1fe8d5dfe26d0b9d1a0db6683ec95d3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsName]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cde00a040f2333f8e4cd9e593c954f9029c9c3f004abc6cfbcb28cfc96f9a03(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be48b320a85629eb7635188d47adf2498849621f2e57bab85fd8838885cb319b(
    value: typing.Optional[DataCloudflareDnsRecordsResultData],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12113aa8804c4c470c9598add6632f78ef0189a9927ac8559ce006561ec617eb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c318b40d66f739036c5a3e361ab79b1eb14bfcc00915d4377847ae59dc5470d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aec184bdca4f57ac179ab14db6dc861e60b9972acc0e1f08293c6372f38ba4bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6c6cf10fecccd497950ae3260ebf31a52aa49e15e73287535475bec9a185314(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4199c7b505494211c29bb1ab5ff5b8d879d0cc867e56d9c70d1cd1ca3fba5aae(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8594e309e683cb10a7c4ad812f51741ff616d3f9ee2be62774d84e6086e6edf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5a9b809028a3d10b1afc93edc7e8449f51d3c7659e660e916b6ad565b7e2b53(
    value: typing.Optional[DataCloudflareDnsRecordsResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d48c7d010807a6c1f750e2a2a7c60adb0218f44bdf480ba760b645faedfdd3c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a11d973a1ce681594731f930fe2fb6fa88ddda572c940de347f777040b7a88c(
    value: typing.Optional[DataCloudflareDnsRecordsResultSettings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2083115598dbf751cd0b7532848abfaa23ffb232a89f84fdaacbf50880080709(
    *,
    absent: typing.Optional[builtins.str] = None,
    contains: typing.Optional[builtins.str] = None,
    endswith: typing.Optional[builtins.str] = None,
    exact: typing.Optional[builtins.str] = None,
    present: typing.Optional[builtins.str] = None,
    startswith: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__250ea2fa23836200c9af8ca7a7abb5bcd5d2f260a40370bdc4d56d6a4f9ac61e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bacddee44e0539838e240f302b319ef96f7f792c29d8c662ab173caa11baf962(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4409321ef799a0378af26acb68949bb42990f3ac9c46c07b8087ba81021ea5a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6098c49869e29368bd805f63464bbd348fae31914ead9ea876a4fa6d9f1d2f1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed990b4c9c179e995a96df6d3772acc54ed3614f75ee3a5d3c9647630afc3a3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e458eaded4ef911782d3be46f2cb4db71986697a0f78310b1891c33cc4ae3f13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8569f27550d8015e8ac3c2f1c45b1fbb32566900542287aee6829559aeb20368(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a40d07b0b1e44807c094f509812bc454c0dcc4ea3e527359433e40312c5e107f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordsTag]],
) -> None:
    """Type checking stubs"""
    pass
