r'''
# `data_cloudflare_dns_record`

Refer to the Terraform Registry for docs: [`data_cloudflare_dns_record`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record).
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


class DataCloudflareDnsRecord(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecord",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record cloudflare_dns_record}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        zone_id: builtins.str,
        dns_record_id: typing.Optional[builtins.str] = None,
        filter: typing.Optional[typing.Union["DataCloudflareDnsRecordFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record cloudflare_dns_record} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#zone_id DataCloudflareDnsRecord#zone_id}
        :param dns_record_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#dns_record_id DataCloudflareDnsRecord#dns_record_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#filter DataCloudflareDnsRecord#filter}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__387548323ea3b6e610ed8ea26faca611caeb2040da76898ab7252522f69d329a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareDnsRecordConfig(
            zone_id=zone_id,
            dns_record_id=dns_record_id,
            filter=filter,
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
        '''Generates CDKTF code for importing a DataCloudflareDnsRecord resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareDnsRecord to import.
        :param import_from_id: The id of the existing DataCloudflareDnsRecord that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareDnsRecord to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6329cc847c2621c38d7ce3e8c918faaae8c180e9f38534a9b85372b26f6991a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        comment: typing.Optional[typing.Union["DataCloudflareDnsRecordFilterComment", typing.Dict[builtins.str, typing.Any]]] = None,
        content: typing.Optional[typing.Union["DataCloudflareDnsRecordFilterContent", typing.Dict[builtins.str, typing.Any]]] = None,
        direction: typing.Optional[builtins.str] = None,
        match: typing.Optional[builtins.str] = None,
        name: typing.Optional[typing.Union["DataCloudflareDnsRecordFilterName", typing.Dict[builtins.str, typing.Any]]] = None,
        order: typing.Optional[builtins.str] = None,
        proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        search: typing.Optional[builtins.str] = None,
        tag: typing.Optional[typing.Union["DataCloudflareDnsRecordFilterTag", typing.Dict[builtins.str, typing.Any]]] = None,
        tag_match: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#comment DataCloudflareDnsRecord#comment}.
        :param content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#content DataCloudflareDnsRecord#content}.
        :param direction: Direction to order DNS records in. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#direction DataCloudflareDnsRecord#direction}
        :param match: Whether to match all search requirements or at least one (any). If set to ``all``, acts like a logical AND between filters. If set to ``any``, acts like a logical OR instead. Note that the interaction between tag filters is controlled by the ``tag-match`` parameter instead. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#match DataCloudflareDnsRecord#match}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#name DataCloudflareDnsRecord#name}.
        :param order: Field to order DNS records by. Available values: "type", "name", "content", "ttl", "proxied". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#order DataCloudflareDnsRecord#order}
        :param proxied: Whether the record is receiving the performance and security benefits of Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#proxied DataCloudflareDnsRecord#proxied}
        :param search: Allows searching in multiple properties of a DNS record simultaneously. This parameter is intended for human users, not automation. Its exact behavior is intentionally left unspecified and is subject to change in the future. This parameter works independently of the ``match`` setting. For automated searches, please use the other available parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#search DataCloudflareDnsRecord#search}
        :param tag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#tag DataCloudflareDnsRecord#tag}.
        :param tag_match: Whether to match all tag search requirements or at least one (any). If set to ``all``, acts like a logical AND between tag filters. If set to ``any``, acts like a logical OR instead. Note that the regular ``match`` parameter is still used to combine the resulting condition with other filters that aren't related to tags. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#tag_match DataCloudflareDnsRecord#tag_match}
        :param type: Record type. Available values: "A", "AAAA", "CAA", "CERT", "CNAME", "DNSKEY", "DS", "HTTPS", "LOC", "MX", "NAPTR", "NS", "OPENPGPKEY", "PTR", "SMIMEA", "SRV", "SSHFP", "SVCB", "TLSA", "TXT", "URI". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#type DataCloudflareDnsRecord#type}
        '''
        value = DataCloudflareDnsRecordFilter(
            comment=comment,
            content=content,
            direction=direction,
            match=match,
            name=name,
            order=order,
            proxied=proxied,
            search=search,
            tag=tag,
            tag_match=tag_match,
            type=type,
        )

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetDnsRecordId")
    def reset_dns_record_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsRecordId", []))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

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
    def data(self) -> "DataCloudflareDnsRecordDataOutputReference":
        return typing.cast("DataCloudflareDnsRecordDataOutputReference", jsii.get(self, "data"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataCloudflareDnsRecordFilterOutputReference":
        return typing.cast("DataCloudflareDnsRecordFilterOutputReference", jsii.get(self, "filter"))

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
    def settings(self) -> "DataCloudflareDnsRecordSettingsOutputReference":
        return typing.cast("DataCloudflareDnsRecordSettingsOutputReference", jsii.get(self, "settings"))

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
    @jsii.member(jsii_name="dnsRecordIdInput")
    def dns_record_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dnsRecordIdInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordFilter"]], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsRecordId")
    def dns_record_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsRecordId"))

    @dns_record_id.setter
    def dns_record_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__847174128d6ff0507780c36756c05f8dac624cbb659e751b2d8467ae09218670)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsRecordId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e27bac5fa7d9c3107117e946519f5ce660389898565b165786fe505f07646f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordConfig",
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
        "dns_record_id": "dnsRecordId",
        "filter": "filter",
    },
)
class DataCloudflareDnsRecordConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        dns_record_id: typing.Optional[builtins.str] = None,
        filter: typing.Optional[typing.Union["DataCloudflareDnsRecordFilter", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#zone_id DataCloudflareDnsRecord#zone_id}
        :param dns_record_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#dns_record_id DataCloudflareDnsRecord#dns_record_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#filter DataCloudflareDnsRecord#filter}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = DataCloudflareDnsRecordFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8374f270c60c013a1ea9ae5bb5e64630aef01dc9046e06f1360794568bc14c69)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument dns_record_id", value=dns_record_id, expected_type=type_hints["dns_record_id"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
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
        if dns_record_id is not None:
            self._values["dns_record_id"] = dns_record_id
        if filter is not None:
            self._values["filter"] = filter

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#zone_id DataCloudflareDnsRecord#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dns_record_id(self) -> typing.Optional[builtins.str]:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#dns_record_id DataCloudflareDnsRecord#dns_record_id}
        '''
        result = self._values.get("dns_record_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filter(self) -> typing.Optional["DataCloudflareDnsRecordFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#filter DataCloudflareDnsRecord#filter}.'''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["DataCloudflareDnsRecordFilter"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordData",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareDnsRecordData:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordDataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordDataOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25d3cdf66d73aff0fa7d35afd7fbfc881efda08ca6a634d66086a8fd40dd9ec2)
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
    def internal_value(self) -> typing.Optional[DataCloudflareDnsRecordData]:
        return typing.cast(typing.Optional[DataCloudflareDnsRecordData], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareDnsRecordData],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9d4626a43fa46ab5de0d89f819718cc9387ae191c3a419f298495fed0c2267a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilter",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "content": "content",
        "direction": "direction",
        "match": "match",
        "name": "name",
        "order": "order",
        "proxied": "proxied",
        "search": "search",
        "tag": "tag",
        "tag_match": "tagMatch",
        "type": "type",
    },
)
class DataCloudflareDnsRecordFilter:
    def __init__(
        self,
        *,
        comment: typing.Optional[typing.Union["DataCloudflareDnsRecordFilterComment", typing.Dict[builtins.str, typing.Any]]] = None,
        content: typing.Optional[typing.Union["DataCloudflareDnsRecordFilterContent", typing.Dict[builtins.str, typing.Any]]] = None,
        direction: typing.Optional[builtins.str] = None,
        match: typing.Optional[builtins.str] = None,
        name: typing.Optional[typing.Union["DataCloudflareDnsRecordFilterName", typing.Dict[builtins.str, typing.Any]]] = None,
        order: typing.Optional[builtins.str] = None,
        proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        search: typing.Optional[builtins.str] = None,
        tag: typing.Optional[typing.Union["DataCloudflareDnsRecordFilterTag", typing.Dict[builtins.str, typing.Any]]] = None,
        tag_match: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#comment DataCloudflareDnsRecord#comment}.
        :param content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#content DataCloudflareDnsRecord#content}.
        :param direction: Direction to order DNS records in. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#direction DataCloudflareDnsRecord#direction}
        :param match: Whether to match all search requirements or at least one (any). If set to ``all``, acts like a logical AND between filters. If set to ``any``, acts like a logical OR instead. Note that the interaction between tag filters is controlled by the ``tag-match`` parameter instead. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#match DataCloudflareDnsRecord#match}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#name DataCloudflareDnsRecord#name}.
        :param order: Field to order DNS records by. Available values: "type", "name", "content", "ttl", "proxied". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#order DataCloudflareDnsRecord#order}
        :param proxied: Whether the record is receiving the performance and security benefits of Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#proxied DataCloudflareDnsRecord#proxied}
        :param search: Allows searching in multiple properties of a DNS record simultaneously. This parameter is intended for human users, not automation. Its exact behavior is intentionally left unspecified and is subject to change in the future. This parameter works independently of the ``match`` setting. For automated searches, please use the other available parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#search DataCloudflareDnsRecord#search}
        :param tag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#tag DataCloudflareDnsRecord#tag}.
        :param tag_match: Whether to match all tag search requirements or at least one (any). If set to ``all``, acts like a logical AND between tag filters. If set to ``any``, acts like a logical OR instead. Note that the regular ``match`` parameter is still used to combine the resulting condition with other filters that aren't related to tags. Available values: "any", "all". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#tag_match DataCloudflareDnsRecord#tag_match}
        :param type: Record type. Available values: "A", "AAAA", "CAA", "CERT", "CNAME", "DNSKEY", "DS", "HTTPS", "LOC", "MX", "NAPTR", "NS", "OPENPGPKEY", "PTR", "SMIMEA", "SRV", "SSHFP", "SVCB", "TLSA", "TXT", "URI". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#type DataCloudflareDnsRecord#type}
        '''
        if isinstance(comment, dict):
            comment = DataCloudflareDnsRecordFilterComment(**comment)
        if isinstance(content, dict):
            content = DataCloudflareDnsRecordFilterContent(**content)
        if isinstance(name, dict):
            name = DataCloudflareDnsRecordFilterName(**name)
        if isinstance(tag, dict):
            tag = DataCloudflareDnsRecordFilterTag(**tag)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__312487ab26d446b7c6bbbaea9147713934fdc1b79ba18a557e869a5811802982)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument match", value=match, expected_type=type_hints["match"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument order", value=order, expected_type=type_hints["order"])
            check_type(argname="argument proxied", value=proxied, expected_type=type_hints["proxied"])
            check_type(argname="argument search", value=search, expected_type=type_hints["search"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument tag_match", value=tag_match, expected_type=type_hints["tag_match"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if content is not None:
            self._values["content"] = content
        if direction is not None:
            self._values["direction"] = direction
        if match is not None:
            self._values["match"] = match
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
    def comment(self) -> typing.Optional["DataCloudflareDnsRecordFilterComment"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#comment DataCloudflareDnsRecord#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional["DataCloudflareDnsRecordFilterComment"], result)

    @builtins.property
    def content(self) -> typing.Optional["DataCloudflareDnsRecordFilterContent"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#content DataCloudflareDnsRecord#content}.'''
        result = self._values.get("content")
        return typing.cast(typing.Optional["DataCloudflareDnsRecordFilterContent"], result)

    @builtins.property
    def direction(self) -> typing.Optional[builtins.str]:
        '''Direction to order DNS records in. Available values: "asc", "desc".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#direction DataCloudflareDnsRecord#direction}
        '''
        result = self._values.get("direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def match(self) -> typing.Optional[builtins.str]:
        '''Whether to match all search requirements or at least one (any).

        If set to ``all``, acts like a logical AND between filters. If set to ``any``, acts like a logical OR instead. Note that the interaction between tag filters is controlled by the ``tag-match`` parameter instead.
        Available values: "any", "all".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#match DataCloudflareDnsRecord#match}
        '''
        result = self._values.get("match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional["DataCloudflareDnsRecordFilterName"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#name DataCloudflareDnsRecord#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional["DataCloudflareDnsRecordFilterName"], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''Field to order DNS records by. Available values: "type", "name", "content", "ttl", "proxied".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#order DataCloudflareDnsRecord#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxied(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether the record is receiving the performance and security benefits of Cloudflare.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#proxied DataCloudflareDnsRecord#proxied}
        '''
        result = self._values.get("proxied")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def search(self) -> typing.Optional[builtins.str]:
        '''Allows searching in multiple properties of a DNS record simultaneously.

        This parameter is intended for human users, not automation. Its exact behavior is intentionally left unspecified and is subject to change in the future. This parameter works independently of the ``match`` setting. For automated searches, please use the other available parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#search DataCloudflareDnsRecord#search}
        '''
        result = self._values.get("search")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag(self) -> typing.Optional["DataCloudflareDnsRecordFilterTag"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#tag DataCloudflareDnsRecord#tag}.'''
        result = self._values.get("tag")
        return typing.cast(typing.Optional["DataCloudflareDnsRecordFilterTag"], result)

    @builtins.property
    def tag_match(self) -> typing.Optional[builtins.str]:
        '''Whether to match all tag search requirements or at least one (any).

        If set to ``all``, acts like a logical AND between tag filters. If set to ``any``, acts like a logical OR instead. Note that the regular ``match`` parameter is still used to combine the resulting condition with other filters that aren't related to tags.
        Available values: "any", "all".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#tag_match DataCloudflareDnsRecord#tag_match}
        '''
        result = self._values.get("tag_match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Record type.

        Available values: "A", "AAAA", "CAA", "CERT", "CNAME", "DNSKEY", "DS", "HTTPS", "LOC", "MX", "NAPTR", "NS", "OPENPGPKEY", "PTR", "SMIMEA", "SRV", "SSHFP", "SVCB", "TLSA", "TXT", "URI".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#type DataCloudflareDnsRecord#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilterComment",
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
class DataCloudflareDnsRecordFilterComment:
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
        :param absent: If this parameter is present, only records *without* a comment are returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#absent DataCloudflareDnsRecord#absent}
        :param contains: Substring of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        :param endswith: Suffix of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        :param exact: Exact value of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        :param present: If this parameter is present, only records *with* a comment are returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#present DataCloudflareDnsRecord#present}
        :param startswith: Prefix of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58e9e0c7a0252b10cc13aeb6cae5a44d8aad1abbd8f1ec4926f581fcae6a627c)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#absent DataCloudflareDnsRecord#absent}
        '''
        result = self._values.get("absent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contains(self) -> typing.Optional[builtins.str]:
        '''Substring of the DNS record comment. Comment filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        '''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endswith(self) -> typing.Optional[builtins.str]:
        '''Suffix of the DNS record comment. Comment filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        '''
        result = self._values.get("endswith")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Exact value of the DNS record comment. Comment filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def present(self) -> typing.Optional[builtins.str]:
        '''If this parameter is present, only records *with* a comment are returned.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#present DataCloudflareDnsRecord#present}
        '''
        result = self._values.get("present")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startswith(self) -> typing.Optional[builtins.str]:
        '''Prefix of the DNS record comment. Comment filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        result = self._values.get("startswith")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordFilterComment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordFilterCommentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilterCommentOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1a29068fa1c39d48e7249f80f03bea90ffd8711665de5fb14f8f191c079933b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce1794c8a6d6d02ce518b253747eb642a43e16007c5ce9e201dcaefe9c91e44c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "absent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contains")
    def contains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contains"))

    @contains.setter
    def contains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f8014dca56a6dd681d49a9e09bf78f7c4bfb4817b0d9aa0159ba2447dd2c558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endswith")
    def endswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endswith"))

    @endswith.setter
    def endswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__236a54e323a7059e541bb14e2a2d15ea914bfebe17a4f7af8d5e09a8d601ffb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dea16e88645acef901dfa436dabb607afd1b6c67556966132fdfd2ae0a213ae8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="present")
    def present(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "present"))

    @present.setter
    def present(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f8d05355a9aace53f3fd3446c7d0452bd82096b32a4ce73070bccbeb86252a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "present", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startswith")
    def startswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startswith"))

    @startswith.setter
    def startswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7fb0e08df7b9efef343e4bdf5d533c73a44cfceee3403d36edc0252a9d3e5ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterComment]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterComment]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterComment]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4f0c603c2c17d57d4a6ac71a59132f31792f26f4545ec34812a12ba184f03ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilterContent",
    jsii_struct_bases=[],
    name_mapping={
        "contains": "contains",
        "endswith": "endswith",
        "exact": "exact",
        "startswith": "startswith",
    },
)
class DataCloudflareDnsRecordFilterContent:
    def __init__(
        self,
        *,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param contains: Substring of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        :param endswith: Suffix of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        :param exact: Exact value of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        :param startswith: Prefix of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bee5031d463c15eba2a5adfaca4b65951f6cf7a1b3e6c0df6244d9c18b311e99)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        '''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endswith(self) -> typing.Optional[builtins.str]:
        '''Suffix of the DNS record content. Content filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        '''
        result = self._values.get("endswith")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Exact value of the DNS record content. Content filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startswith(self) -> typing.Optional[builtins.str]:
        '''Prefix of the DNS record content. Content filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        result = self._values.get("startswith")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordFilterContent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordFilterContentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilterContentOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6240ca89e25f99691edc352314c3dec0b6b5db4eb92a7b9d1d97d056ea517f98)
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
            type_hints = typing.get_type_hints(_typecheckingstub__983e4d53cdc78201ae667523c61c886426575e4722234524cdd732ce696ded8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endswith")
    def endswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endswith"))

    @endswith.setter
    def endswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__302c9b5521c0564729e84346755526384315ec3af20ba425f4355ae52725c33b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b17410fe11e5ffae930e494a010faf8528f5e1e4ee0522f0a1bf07e68a97f51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startswith")
    def startswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startswith"))

    @startswith.setter
    def startswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51ec3ccec1df35b4b9afe827f31f2ba8ce593fdb1ef5f0794249ebf8a0fe3bcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterContent]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterContent]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterContent]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dd1f57dff7464b81b0d1d87382ca188e7f2dbfcf29318a5cffc13f2766c5cf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilterName",
    jsii_struct_bases=[],
    name_mapping={
        "contains": "contains",
        "endswith": "endswith",
        "exact": "exact",
        "startswith": "startswith",
    },
)
class DataCloudflareDnsRecordFilterName:
    def __init__(
        self,
        *,
        contains: typing.Optional[builtins.str] = None,
        endswith: typing.Optional[builtins.str] = None,
        exact: typing.Optional[builtins.str] = None,
        startswith: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param contains: Substring of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        :param endswith: Suffix of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        :param exact: Exact value of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        :param startswith: Prefix of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c365fbadb52c94d99e9a56b07dee06a496853b40b1d43bf3c87c87f3471c861e)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        '''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endswith(self) -> typing.Optional[builtins.str]:
        '''Suffix of the DNS record name. Name filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        '''
        result = self._values.get("endswith")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Exact value of the DNS record name. Name filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startswith(self) -> typing.Optional[builtins.str]:
        '''Prefix of the DNS record name. Name filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        result = self._values.get("startswith")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordFilterName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordFilterNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilterNameOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcef2f93b3ac5ac6815c9a7440ad91ee07406c21a1d36fb8771bd37d3caf4d8a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__394ec2147afc030889ed73c2484b4682f933cd15ebf4aa8a2044cd8773ca25ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endswith")
    def endswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endswith"))

    @endswith.setter
    def endswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee4b50331f299e73ad7acf6d76bc496c86e178e14009c0190e71b8a43b047998)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac7dc8f08ab96c5e1ee84615b042e1d925d12b5bbdfa931f06005047d07c41ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startswith")
    def startswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startswith"))

    @startswith.setter
    def startswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d893c6bd86c9696cd6416872c2b80b788335fcfcf63ad4cbafcf2fa72e5423a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterName]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterName]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dfa20e45747b2ace4c506eef2a3e95284e4aeb4eb01ab3cebbbe8245df8f1ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareDnsRecordFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilterOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ca2e6c966014cc285ad87fb7090d6f4fbe75a7b276407270266882dc75aa67a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
        :param absent: If this parameter is present, only records *without* a comment are returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#absent DataCloudflareDnsRecord#absent}
        :param contains: Substring of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        :param endswith: Suffix of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        :param exact: Exact value of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        :param present: If this parameter is present, only records *with* a comment are returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#present DataCloudflareDnsRecord#present}
        :param startswith: Prefix of the DNS record comment. Comment filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        value = DataCloudflareDnsRecordFilterComment(
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
        :param contains: Substring of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        :param endswith: Suffix of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        :param exact: Exact value of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        :param startswith: Prefix of the DNS record content. Content filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        value = DataCloudflareDnsRecordFilterContent(
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
        :param contains: Substring of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        :param endswith: Suffix of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        :param exact: Exact value of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        :param startswith: Prefix of the DNS record name. Name filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        value = DataCloudflareDnsRecordFilterName(
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
        :param absent: Name of a tag which must *not* be present on the DNS record. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#absent DataCloudflareDnsRecord#absent}
        :param contains: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value contains ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        :param endswith: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value ends with ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        :param exact: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value is ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        :param present: Name of a tag which must be present on the DNS record. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#present DataCloudflareDnsRecord#present}
        :param startswith: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value starts with ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        value = DataCloudflareDnsRecordFilterTag(
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

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> DataCloudflareDnsRecordFilterCommentOutputReference:
        return typing.cast(DataCloudflareDnsRecordFilterCommentOutputReference, jsii.get(self, "comment"))

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> DataCloudflareDnsRecordFilterContentOutputReference:
        return typing.cast(DataCloudflareDnsRecordFilterContentOutputReference, jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> DataCloudflareDnsRecordFilterNameOutputReference:
        return typing.cast(DataCloudflareDnsRecordFilterNameOutputReference, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> "DataCloudflareDnsRecordFilterTagOutputReference":
        return typing.cast("DataCloudflareDnsRecordFilterTagOutputReference", jsii.get(self, "tag"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterComment]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterComment]], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="contentInput")
    def content_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterContent]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterContent]], jsii.get(self, "contentInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterName]], jsii.get(self, "nameInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordFilterTag"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareDnsRecordFilterTag"]], jsii.get(self, "tagInput"))

    @builtins.property
    @jsii.member(jsii_name="tagMatchInput")
    def tag_match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagMatchInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3676a5fd46dab2c16d6ca8e3c7fc3c2fa8fc0f96bb7ca603593158787a64daf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="match")
    def match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "match"))

    @match.setter
    def match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f8a9705c31404163a5bc2f68ab0232c89faea9e961f953020d142a1b384d4f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "match", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="order")
    def order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "order"))

    @order.setter
    def order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dc76a70686234b0fd2e0b8ba32d113a1c44aa1bf24f52aae67e46345ccd6987)
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
            type_hints = typing.get_type_hints(_typecheckingstub__09258df9f85e14017bbd3a815a77f1a697cc8ab50db199e1c8339dcf3a838799)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxied", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="search")
    def search(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "search"))

    @search.setter
    def search(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__069bb1a2a1ee1f543cf5d3bc4697a6761e2afa52163cc6b78420ea16ae25390e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "search", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tagMatch")
    def tag_match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagMatch"))

    @tag_match.setter
    def tag_match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f55eeb017c8b008bfd13bdd1186c27ffa18cba9f70ee2fc079606d5f60b40660)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagMatch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4751e2a797d39e004348e8037a5b686b9f2f8bbc5ad9fefa2ff6eab42ec29ee4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cda89474ab5222d68eddcf17c11c0945edcba318ff42434814ec3ac1b76f576)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilterTag",
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
class DataCloudflareDnsRecordFilterTag:
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
        :param absent: Name of a tag which must *not* be present on the DNS record. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#absent DataCloudflareDnsRecord#absent}
        :param contains: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value contains ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        :param endswith: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value ends with ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        :param exact: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value is ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        :param present: Name of a tag which must be present on the DNS record. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#present DataCloudflareDnsRecord#present}
        :param startswith: A tag and value, of the form ``<tag-name>:<tag-value>``. The API will only return DNS records that have a tag named ``<tag-name>`` whose value starts with ``<tag-value>``. Tag filters are case-insensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b41da255f58cec28255b9cc0a9454d0bc9d5d31d0302562e0371f4a6a816681e)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#absent DataCloudflareDnsRecord#absent}
        '''
        result = self._values.get("absent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contains(self) -> typing.Optional[builtins.str]:
        '''A tag and value, of the form ``<tag-name>:<tag-value>``.

        The API will only return DNS records that have a tag named ``<tag-name>`` whose value contains ``<tag-value>``. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#contains DataCloudflareDnsRecord#contains}
        '''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endswith(self) -> typing.Optional[builtins.str]:
        '''A tag and value, of the form ``<tag-name>:<tag-value>``.

        The API will only return DNS records that have a tag named ``<tag-name>`` whose value ends with ``<tag-value>``. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#endswith DataCloudflareDnsRecord#endswith}
        '''
        result = self._values.get("endswith")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''A tag and value, of the form ``<tag-name>:<tag-value>``.

        The API will only return DNS records that have a tag named ``<tag-name>`` whose value is ``<tag-value>``. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#exact DataCloudflareDnsRecord#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def present(self) -> typing.Optional[builtins.str]:
        '''Name of a tag which must be present on the DNS record. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#present DataCloudflareDnsRecord#present}
        '''
        result = self._values.get("present")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startswith(self) -> typing.Optional[builtins.str]:
        '''A tag and value, of the form ``<tag-name>:<tag-value>``.

        The API will only return DNS records that have a tag named ``<tag-name>`` whose value starts with ``<tag-value>``. Tag filters are case-insensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/dns_record#startswith DataCloudflareDnsRecord#startswith}
        '''
        result = self._values.get("startswith")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordFilterTag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordFilterTagOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordFilterTagOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b0de75bb5b0027907dd33aa4f3d6e94aa522c864eca356b8822f1abb8ec27e5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b49ef9dcd28811fa90ed327a55b109bc21d65303c93ddb8a970233a8857b22ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "absent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contains")
    def contains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contains"))

    @contains.setter
    def contains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2140f0ff4a27a0beaf4912a3f467aa02ccd79a94b4548da7ae8b76c8fdf5c360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endswith")
    def endswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endswith"))

    @endswith.setter
    def endswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__431770685e5a93b51fafe3f02685c6c42949b7f30b3b355bd96c4ad4b07f7797)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__869ca073280057d3556e4f28efa2542504b305246466b13ae4f5368c2bb141c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="present")
    def present(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "present"))

    @present.setter
    def present(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f935112258a1a503232b78dbf3541ed964430b83766051fb9dacc21d56896cc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "present", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startswith")
    def startswith(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startswith"))

    @startswith.setter
    def startswith(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7426ec2cc93922e34577ad832a306d9a49f38ec577516dfe5a7cd200466d94d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startswith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterTag]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterTag]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterTag]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cca306fcfda5048f0a46eb27517d71f32a2f9b18af8c74b4b70750708c6fbe7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordSettings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareDnsRecordSettings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareDnsRecordSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareDnsRecordSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareDnsRecord.DataCloudflareDnsRecordSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be0aa913c378f3e6ccf2d272fae776359e5fc5281f974ae3aba62ddf0d0b0152)
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
    def internal_value(self) -> typing.Optional[DataCloudflareDnsRecordSettings]:
        return typing.cast(typing.Optional[DataCloudflareDnsRecordSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareDnsRecordSettings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f86efc7b2c34a9fead43ff9e7403b9b1ec3b214cd07a4d2974de3ae55f4a60e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareDnsRecord",
    "DataCloudflareDnsRecordConfig",
    "DataCloudflareDnsRecordData",
    "DataCloudflareDnsRecordDataOutputReference",
    "DataCloudflareDnsRecordFilter",
    "DataCloudflareDnsRecordFilterComment",
    "DataCloudflareDnsRecordFilterCommentOutputReference",
    "DataCloudflareDnsRecordFilterContent",
    "DataCloudflareDnsRecordFilterContentOutputReference",
    "DataCloudflareDnsRecordFilterName",
    "DataCloudflareDnsRecordFilterNameOutputReference",
    "DataCloudflareDnsRecordFilterOutputReference",
    "DataCloudflareDnsRecordFilterTag",
    "DataCloudflareDnsRecordFilterTagOutputReference",
    "DataCloudflareDnsRecordSettings",
    "DataCloudflareDnsRecordSettingsOutputReference",
]

publication.publish()

def _typecheckingstub__387548323ea3b6e610ed8ea26faca611caeb2040da76898ab7252522f69d329a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    zone_id: builtins.str,
    dns_record_id: typing.Optional[builtins.str] = None,
    filter: typing.Optional[typing.Union[DataCloudflareDnsRecordFilter, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__a6329cc847c2621c38d7ce3e8c918faaae8c180e9f38534a9b85372b26f6991a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__847174128d6ff0507780c36756c05f8dac624cbb659e751b2d8467ae09218670(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e27bac5fa7d9c3107117e946519f5ce660389898565b165786fe505f07646f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8374f270c60c013a1ea9ae5bb5e64630aef01dc9046e06f1360794568bc14c69(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: builtins.str,
    dns_record_id: typing.Optional[builtins.str] = None,
    filter: typing.Optional[typing.Union[DataCloudflareDnsRecordFilter, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25d3cdf66d73aff0fa7d35afd7fbfc881efda08ca6a634d66086a8fd40dd9ec2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9d4626a43fa46ab5de0d89f819718cc9387ae191c3a419f298495fed0c2267a(
    value: typing.Optional[DataCloudflareDnsRecordData],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__312487ab26d446b7c6bbbaea9147713934fdc1b79ba18a557e869a5811802982(
    *,
    comment: typing.Optional[typing.Union[DataCloudflareDnsRecordFilterComment, typing.Dict[builtins.str, typing.Any]]] = None,
    content: typing.Optional[typing.Union[DataCloudflareDnsRecordFilterContent, typing.Dict[builtins.str, typing.Any]]] = None,
    direction: typing.Optional[builtins.str] = None,
    match: typing.Optional[builtins.str] = None,
    name: typing.Optional[typing.Union[DataCloudflareDnsRecordFilterName, typing.Dict[builtins.str, typing.Any]]] = None,
    order: typing.Optional[builtins.str] = None,
    proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    search: typing.Optional[builtins.str] = None,
    tag: typing.Optional[typing.Union[DataCloudflareDnsRecordFilterTag, typing.Dict[builtins.str, typing.Any]]] = None,
    tag_match: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e9e0c7a0252b10cc13aeb6cae5a44d8aad1abbd8f1ec4926f581fcae6a627c(
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

def _typecheckingstub__d1a29068fa1c39d48e7249f80f03bea90ffd8711665de5fb14f8f191c079933b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce1794c8a6d6d02ce518b253747eb642a43e16007c5ce9e201dcaefe9c91e44c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f8014dca56a6dd681d49a9e09bf78f7c4bfb4817b0d9aa0159ba2447dd2c558(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__236a54e323a7059e541bb14e2a2d15ea914bfebe17a4f7af8d5e09a8d601ffb3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dea16e88645acef901dfa436dabb607afd1b6c67556966132fdfd2ae0a213ae8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f8d05355a9aace53f3fd3446c7d0452bd82096b32a4ce73070bccbeb86252a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7fb0e08df7b9efef343e4bdf5d533c73a44cfceee3403d36edc0252a9d3e5ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4f0c603c2c17d57d4a6ac71a59132f31792f26f4545ec34812a12ba184f03ea(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterComment]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bee5031d463c15eba2a5adfaca4b65951f6cf7a1b3e6c0df6244d9c18b311e99(
    *,
    contains: typing.Optional[builtins.str] = None,
    endswith: typing.Optional[builtins.str] = None,
    exact: typing.Optional[builtins.str] = None,
    startswith: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6240ca89e25f99691edc352314c3dec0b6b5db4eb92a7b9d1d97d056ea517f98(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__983e4d53cdc78201ae667523c61c886426575e4722234524cdd732ce696ded8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__302c9b5521c0564729e84346755526384315ec3af20ba425f4355ae52725c33b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b17410fe11e5ffae930e494a010faf8528f5e1e4ee0522f0a1bf07e68a97f51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51ec3ccec1df35b4b9afe827f31f2ba8ce593fdb1ef5f0794249ebf8a0fe3bcd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dd1f57dff7464b81b0d1d87382ca188e7f2dbfcf29318a5cffc13f2766c5cf2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterContent]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c365fbadb52c94d99e9a56b07dee06a496853b40b1d43bf3c87c87f3471c861e(
    *,
    contains: typing.Optional[builtins.str] = None,
    endswith: typing.Optional[builtins.str] = None,
    exact: typing.Optional[builtins.str] = None,
    startswith: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcef2f93b3ac5ac6815c9a7440ad91ee07406c21a1d36fb8771bd37d3caf4d8a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__394ec2147afc030889ed73c2484b4682f933cd15ebf4aa8a2044cd8773ca25ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee4b50331f299e73ad7acf6d76bc496c86e178e14009c0190e71b8a43b047998(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac7dc8f08ab96c5e1ee84615b042e1d925d12b5bbdfa931f06005047d07c41ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d893c6bd86c9696cd6416872c2b80b788335fcfcf63ad4cbafcf2fa72e5423a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dfa20e45747b2ace4c506eef2a3e95284e4aeb4eb01ab3cebbbe8245df8f1ab(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterName]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ca2e6c966014cc285ad87fb7090d6f4fbe75a7b276407270266882dc75aa67a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3676a5fd46dab2c16d6ca8e3c7fc3c2fa8fc0f96bb7ca603593158787a64daf2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f8a9705c31404163a5bc2f68ab0232c89faea9e961f953020d142a1b384d4f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dc76a70686234b0fd2e0b8ba32d113a1c44aa1bf24f52aae67e46345ccd6987(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09258df9f85e14017bbd3a815a77f1a697cc8ab50db199e1c8339dcf3a838799(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__069bb1a2a1ee1f543cf5d3bc4697a6761e2afa52163cc6b78420ea16ae25390e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f55eeb017c8b008bfd13bdd1186c27ffa18cba9f70ee2fc079606d5f60b40660(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4751e2a797d39e004348e8037a5b686b9f2f8bbc5ad9fefa2ff6eab42ec29ee4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cda89474ab5222d68eddcf17c11c0945edcba318ff42434814ec3ac1b76f576(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b41da255f58cec28255b9cc0a9454d0bc9d5d31d0302562e0371f4a6a816681e(
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

def _typecheckingstub__3b0de75bb5b0027907dd33aa4f3d6e94aa522c864eca356b8822f1abb8ec27e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b49ef9dcd28811fa90ed327a55b109bc21d65303c93ddb8a970233a8857b22ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2140f0ff4a27a0beaf4912a3f467aa02ccd79a94b4548da7ae8b76c8fdf5c360(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__431770685e5a93b51fafe3f02685c6c42949b7f30b3b355bd96c4ad4b07f7797(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__869ca073280057d3556e4f28efa2542504b305246466b13ae4f5368c2bb141c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f935112258a1a503232b78dbf3541ed964430b83766051fb9dacc21d56896cc6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7426ec2cc93922e34577ad832a306d9a49f38ec577516dfe5a7cd200466d94d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cca306fcfda5048f0a46eb27517d71f32a2f9b18af8c74b4b70750708c6fbe7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareDnsRecordFilterTag]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be0aa913c378f3e6ccf2d272fae776359e5fc5281f974ae3aba62ddf0d0b0152(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f86efc7b2c34a9fead43ff9e7403b9b1ec3b214cd07a4d2974de3ae55f4a60e0(
    value: typing.Optional[DataCloudflareDnsRecordSettings],
) -> None:
    """Type checking stubs"""
    pass
