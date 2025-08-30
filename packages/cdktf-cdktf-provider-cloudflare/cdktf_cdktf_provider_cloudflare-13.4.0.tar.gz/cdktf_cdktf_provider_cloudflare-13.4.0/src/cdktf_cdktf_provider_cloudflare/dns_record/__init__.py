r'''
# `cloudflare_dns_record`

Refer to the Terraform Registry for docs: [`cloudflare_dns_record`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record).
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


class DnsRecord(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dnsRecord.DnsRecord",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record cloudflare_dns_record}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        ttl: jsii.Number,
        type: builtins.str,
        zone_id: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        content: typing.Optional[builtins.str] = None,
        data: typing.Optional[typing.Union["DnsRecordData", typing.Dict[builtins.str, typing.Any]]] = None,
        priority: typing.Optional[jsii.Number] = None,
        proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        settings: typing.Optional[typing.Union["DnsRecordSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record cloudflare_dns_record} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: DNS record name (or @ for the zone apex) in Punycode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#name DnsRecord#name}
        :param ttl: Time To Live (TTL) of the DNS record in seconds. Setting to 1 means 'automatic'. Value must be between 60 and 86400, with the minimum reduced to 30 for Enterprise zones. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#ttl DnsRecord#ttl}
        :param type: Record type. Available values: "A", "AAAA", "CNAME", "MX", "NS", "OPENPGPKEY", "PTR", "TXT", "CAA", "CERT", "DNSKEY", "DS", "HTTPS", "LOC", "NAPTR", "SMIMEA", "SRV", "SSHFP", "SVCB", "TLSA", "URI". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#type DnsRecord#type}
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#zone_id DnsRecord#zone_id}
        :param comment: Comments or notes about the DNS record. This field has no effect on DNS responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#comment DnsRecord#comment}
        :param content: A valid IPv4 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#content DnsRecord#content}
        :param data: Components of a CAA record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#data DnsRecord#data}
        :param priority: Required for MX, SRV and URI records; unused by other record types. Records with lower priorities are preferred. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#priority DnsRecord#priority}
        :param proxied: Whether the record is receiving the performance and security benefits of Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#proxied DnsRecord#proxied}
        :param settings: Settings for the DNS record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#settings DnsRecord#settings}
        :param tags: Custom tags for the DNS record. This field has no effect on DNS responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#tags DnsRecord#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d1e4b33e059c7560d80448e275d13c08e147ebc16405b527ea368635ebdeb57)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DnsRecordConfig(
            name=name,
            ttl=ttl,
            type=type,
            zone_id=zone_id,
            comment=comment,
            content=content,
            data=data,
            priority=priority,
            proxied=proxied,
            settings=settings,
            tags=tags,
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
        '''Generates CDKTF code for importing a DnsRecord resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DnsRecord to import.
        :param import_from_id: The id of the existing DnsRecord that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DnsRecord to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff9592783ada9de699a70a313ace305cfe839f48bb79a392bb9b30ced66dbdb4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putData")
    def put_data(
        self,
        *,
        algorithm: typing.Optional[jsii.Number] = None,
        altitude: typing.Optional[jsii.Number] = None,
        certificate: typing.Optional[builtins.str] = None,
        digest: typing.Optional[builtins.str] = None,
        digest_type: typing.Optional[jsii.Number] = None,
        fingerprint: typing.Optional[builtins.str] = None,
        flags: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        key_tag: typing.Optional[jsii.Number] = None,
        lat_degrees: typing.Optional[jsii.Number] = None,
        lat_direction: typing.Optional[builtins.str] = None,
        lat_minutes: typing.Optional[jsii.Number] = None,
        lat_seconds: typing.Optional[jsii.Number] = None,
        long_degrees: typing.Optional[jsii.Number] = None,
        long_direction: typing.Optional[builtins.str] = None,
        long_minutes: typing.Optional[jsii.Number] = None,
        long_seconds: typing.Optional[jsii.Number] = None,
        matching_type: typing.Optional[jsii.Number] = None,
        order: typing.Optional[jsii.Number] = None,
        port: typing.Optional[jsii.Number] = None,
        precision_horz: typing.Optional[jsii.Number] = None,
        precision_vert: typing.Optional[jsii.Number] = None,
        preference: typing.Optional[jsii.Number] = None,
        priority: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[jsii.Number] = None,
        public_key: typing.Optional[builtins.str] = None,
        regex: typing.Optional[builtins.str] = None,
        replacement: typing.Optional[builtins.str] = None,
        selector: typing.Optional[jsii.Number] = None,
        service: typing.Optional[builtins.str] = None,
        size: typing.Optional[jsii.Number] = None,
        tag: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        type: typing.Optional[jsii.Number] = None,
        usage: typing.Optional[jsii.Number] = None,
        value: typing.Optional[builtins.str] = None,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param algorithm: Algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#algorithm DnsRecord#algorithm}
        :param altitude: Altitude of location in meters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#altitude DnsRecord#altitude}
        :param certificate: Certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#certificate DnsRecord#certificate}
        :param digest: Digest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#digest DnsRecord#digest}
        :param digest_type: Digest Type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#digest_type DnsRecord#digest_type}
        :param fingerprint: Fingerprint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#fingerprint DnsRecord#fingerprint}
        :param flags: Flags for the CAA record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#flags DnsRecord#flags}
        :param key_tag: Key Tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#key_tag DnsRecord#key_tag}
        :param lat_degrees: Degrees of latitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_degrees DnsRecord#lat_degrees}
        :param lat_direction: Latitude direction. Available values: "N", "S". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_direction DnsRecord#lat_direction}
        :param lat_minutes: Minutes of latitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_minutes DnsRecord#lat_minutes}
        :param lat_seconds: Seconds of latitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_seconds DnsRecord#lat_seconds}
        :param long_degrees: Degrees of longitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_degrees DnsRecord#long_degrees}
        :param long_direction: Longitude direction. Available values: "E", "W". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_direction DnsRecord#long_direction}
        :param long_minutes: Minutes of longitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_minutes DnsRecord#long_minutes}
        :param long_seconds: Seconds of longitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_seconds DnsRecord#long_seconds}
        :param matching_type: Matching Type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#matching_type DnsRecord#matching_type}
        :param order: Order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#order DnsRecord#order}
        :param port: The port of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#port DnsRecord#port}
        :param precision_horz: Horizontal precision of location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#precision_horz DnsRecord#precision_horz}
        :param precision_vert: Vertical precision of location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#precision_vert DnsRecord#precision_vert}
        :param preference: Preference. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#preference DnsRecord#preference}
        :param priority: Priority. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#priority DnsRecord#priority}
        :param protocol: Protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#protocol DnsRecord#protocol}
        :param public_key: Public Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#public_key DnsRecord#public_key}
        :param regex: Regex. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#regex DnsRecord#regex}
        :param replacement: Replacement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#replacement DnsRecord#replacement}
        :param selector: Selector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#selector DnsRecord#selector}
        :param service: Service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#service DnsRecord#service}
        :param size: Size of location in meters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#size DnsRecord#size}
        :param tag: Name of the property controlled by this record (e.g.: issue, issuewild, iodef). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#tag DnsRecord#tag}
        :param target: Target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#target DnsRecord#target}
        :param type: Type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#type DnsRecord#type}
        :param usage: Usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#usage DnsRecord#usage}
        :param value: Value of the record. This field's semantics depend on the chosen tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#value DnsRecord#value}
        :param weight: The record weight. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#weight DnsRecord#weight}
        '''
        value_ = DnsRecordData(
            algorithm=algorithm,
            altitude=altitude,
            certificate=certificate,
            digest=digest,
            digest_type=digest_type,
            fingerprint=fingerprint,
            flags=flags,
            key_tag=key_tag,
            lat_degrees=lat_degrees,
            lat_direction=lat_direction,
            lat_minutes=lat_minutes,
            lat_seconds=lat_seconds,
            long_degrees=long_degrees,
            long_direction=long_direction,
            long_minutes=long_minutes,
            long_seconds=long_seconds,
            matching_type=matching_type,
            order=order,
            port=port,
            precision_horz=precision_horz,
            precision_vert=precision_vert,
            preference=preference,
            priority=priority,
            protocol=protocol,
            public_key=public_key,
            regex=regex,
            replacement=replacement,
            selector=selector,
            service=service,
            size=size,
            tag=tag,
            target=target,
            type=type,
            usage=usage,
            value=value,
            weight=weight,
        )

        return typing.cast(None, jsii.invoke(self, "putData", [value_]))

    @jsii.member(jsii_name="putSettings")
    def put_settings(
        self,
        *,
        flatten_cname: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ipv4_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ipv6_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param flatten_cname: If enabled, causes the CNAME record to be resolved externally and the resulting address records (e.g., A and AAAA) to be returned instead of the CNAME record itself. This setting is unavailable for proxied records, since they are always flattened. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#flatten_cname DnsRecord#flatten_cname}
        :param ipv4_only: When enabled, only A records will be generated, and AAAA records will not be created. This setting is intended for exceptional cases. Note that this option only applies to proxied records and it has no effect on whether Cloudflare communicates with the origin using IPv4 or IPv6. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#ipv4_only DnsRecord#ipv4_only}
        :param ipv6_only: When enabled, only AAAA records will be generated, and A records will not be created. This setting is intended for exceptional cases. Note that this option only applies to proxied records and it has no effect on whether Cloudflare communicates with the origin using IPv4 or IPv6. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#ipv6_only DnsRecord#ipv6_only}
        '''
        value = DnsRecordSettings(
            flatten_cname=flatten_cname, ipv4_only=ipv4_only, ipv6_only=ipv6_only
        )

        return typing.cast(None, jsii.invoke(self, "putSettings", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetContent")
    def reset_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContent", []))

    @jsii.member(jsii_name="resetData")
    def reset_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetData", []))

    @jsii.member(jsii_name="resetPriority")
    def reset_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPriority", []))

    @jsii.member(jsii_name="resetProxied")
    def reset_proxied(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProxied", []))

    @jsii.member(jsii_name="resetSettings")
    def reset_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSettings", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="commentModifiedOn")
    def comment_modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commentModifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> "DnsRecordDataOutputReference":
        return typing.cast("DnsRecordDataOutputReference", jsii.get(self, "data"))

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
    @jsii.member(jsii_name="proxiable")
    def proxiable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "proxiable"))

    @builtins.property
    @jsii.member(jsii_name="settings")
    def settings(self) -> "DnsRecordSettingsOutputReference":
        return typing.cast("DnsRecordSettingsOutputReference", jsii.get(self, "settings"))

    @builtins.property
    @jsii.member(jsii_name="tagsModifiedOn")
    def tags_modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagsModifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="contentInput")
    def content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentInput"))

    @builtins.property
    @jsii.member(jsii_name="dataInput")
    def data_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DnsRecordData"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DnsRecordData"]], jsii.get(self, "dataInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property
    @jsii.member(jsii_name="proxiedInput")
    def proxied_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "proxiedInput"))

    @builtins.property
    @jsii.member(jsii_name="settingsInput")
    def settings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DnsRecordSettings"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DnsRecordSettings"]], jsii.get(self, "settingsInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c81ab12041781173b6b28ce7d3db582146789af8d62c8044f98a4d0780e7523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @content.setter
    def content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aa946175749029f209a4d96297218b6e52fa7c6a3b0b80d65fecd74cab4af2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "content", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__999b0cf80d39e26372232f0435a79065d6aeb48892b17e47a1c5fae8aafbf098)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c96caf2ec95cc43509afb161c12deb918c579e7409c3a1e09e91fd6612ebcf32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__48fc5ebcd34f90285a211308280c187dc34648cc29ffec7ede99a21cd64a84c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxied", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__818db78f6836eb9f50c4216f7503241e4314c2b2f11063cd9e2115898a1e0301)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__098ec4f8c354f02533f21123e634bf7b688482f06013fbeb11b6aeed5d9a5ccd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bae9be44da3bfa4c93ffde6e1f54c2c0f99d819aa8925fba47495724dbffd728)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2fa97840b392aaa6043b3f87171fc447290f02eba27814b39f3268a94ab7e0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dnsRecord.DnsRecordConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "ttl": "ttl",
        "type": "type",
        "zone_id": "zoneId",
        "comment": "comment",
        "content": "content",
        "data": "data",
        "priority": "priority",
        "proxied": "proxied",
        "settings": "settings",
        "tags": "tags",
    },
)
class DnsRecordConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        ttl: jsii.Number,
        type: builtins.str,
        zone_id: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        content: typing.Optional[builtins.str] = None,
        data: typing.Optional[typing.Union["DnsRecordData", typing.Dict[builtins.str, typing.Any]]] = None,
        priority: typing.Optional[jsii.Number] = None,
        proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        settings: typing.Optional[typing.Union["DnsRecordSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: DNS record name (or @ for the zone apex) in Punycode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#name DnsRecord#name}
        :param ttl: Time To Live (TTL) of the DNS record in seconds. Setting to 1 means 'automatic'. Value must be between 60 and 86400, with the minimum reduced to 30 for Enterprise zones. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#ttl DnsRecord#ttl}
        :param type: Record type. Available values: "A", "AAAA", "CNAME", "MX", "NS", "OPENPGPKEY", "PTR", "TXT", "CAA", "CERT", "DNSKEY", "DS", "HTTPS", "LOC", "NAPTR", "SMIMEA", "SRV", "SSHFP", "SVCB", "TLSA", "URI". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#type DnsRecord#type}
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#zone_id DnsRecord#zone_id}
        :param comment: Comments or notes about the DNS record. This field has no effect on DNS responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#comment DnsRecord#comment}
        :param content: A valid IPv4 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#content DnsRecord#content}
        :param data: Components of a CAA record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#data DnsRecord#data}
        :param priority: Required for MX, SRV and URI records; unused by other record types. Records with lower priorities are preferred. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#priority DnsRecord#priority}
        :param proxied: Whether the record is receiving the performance and security benefits of Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#proxied DnsRecord#proxied}
        :param settings: Settings for the DNS record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#settings DnsRecord#settings}
        :param tags: Custom tags for the DNS record. This field has no effect on DNS responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#tags DnsRecord#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(data, dict):
            data = DnsRecordData(**data)
        if isinstance(settings, dict):
            settings = DnsRecordSettings(**settings)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84483ca7f938b055e889e9f85be823a2219e9b0dfe6206f25c3b3076955c8bcf)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument data", value=data, expected_type=type_hints["data"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument proxied", value=proxied, expected_type=type_hints["proxied"])
            check_type(argname="argument settings", value=settings, expected_type=type_hints["settings"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "ttl": ttl,
            "type": type,
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
        if data is not None:
            self._values["data"] = data
        if priority is not None:
            self._values["priority"] = priority
        if proxied is not None:
            self._values["proxied"] = proxied
        if settings is not None:
            self._values["settings"] = settings
        if tags is not None:
            self._values["tags"] = tags

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
    def name(self) -> builtins.str:
        '''DNS record name (or @ for the zone apex) in Punycode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#name DnsRecord#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ttl(self) -> jsii.Number:
        '''Time To Live (TTL) of the DNS record in seconds.

        Setting to 1 means 'automatic'. Value must be between 60 and 86400, with the minimum reduced to 30 for Enterprise zones.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#ttl DnsRecord#ttl}
        '''
        result = self._values.get("ttl")
        assert result is not None, "Required property 'ttl' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Record type.

        Available values: "A", "AAAA", "CNAME", "MX", "NS", "OPENPGPKEY", "PTR", "TXT", "CAA", "CERT", "DNSKEY", "DS", "HTTPS", "LOC", "NAPTR", "SMIMEA", "SRV", "SSHFP", "SVCB", "TLSA", "URI".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#type DnsRecord#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#zone_id DnsRecord#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Comments or notes about the DNS record. This field has no effect on DNS responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#comment DnsRecord#comment}
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content(self) -> typing.Optional[builtins.str]:
        '''A valid IPv4 address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#content DnsRecord#content}
        '''
        result = self._values.get("content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data(self) -> typing.Optional["DnsRecordData"]:
        '''Components of a CAA record.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#data DnsRecord#data}
        '''
        result = self._values.get("data")
        return typing.cast(typing.Optional["DnsRecordData"], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Required for MX, SRV and URI records; unused by other record types. Records with lower priorities are preferred.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#priority DnsRecord#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def proxied(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether the record is receiving the performance and security benefits of Cloudflare.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#proxied DnsRecord#proxied}
        '''
        result = self._values.get("proxied")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def settings(self) -> typing.Optional["DnsRecordSettings"]:
        '''Settings for the DNS record.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#settings DnsRecord#settings}
        '''
        result = self._values.get("settings")
        return typing.cast(typing.Optional["DnsRecordSettings"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Custom tags for the DNS record. This field has no effect on DNS responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#tags DnsRecord#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DnsRecordConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dnsRecord.DnsRecordData",
    jsii_struct_bases=[],
    name_mapping={
        "algorithm": "algorithm",
        "altitude": "altitude",
        "certificate": "certificate",
        "digest": "digest",
        "digest_type": "digestType",
        "fingerprint": "fingerprint",
        "flags": "flags",
        "key_tag": "keyTag",
        "lat_degrees": "latDegrees",
        "lat_direction": "latDirection",
        "lat_minutes": "latMinutes",
        "lat_seconds": "latSeconds",
        "long_degrees": "longDegrees",
        "long_direction": "longDirection",
        "long_minutes": "longMinutes",
        "long_seconds": "longSeconds",
        "matching_type": "matchingType",
        "order": "order",
        "port": "port",
        "precision_horz": "precisionHorz",
        "precision_vert": "precisionVert",
        "preference": "preference",
        "priority": "priority",
        "protocol": "protocol",
        "public_key": "publicKey",
        "regex": "regex",
        "replacement": "replacement",
        "selector": "selector",
        "service": "service",
        "size": "size",
        "tag": "tag",
        "target": "target",
        "type": "type",
        "usage": "usage",
        "value": "value",
        "weight": "weight",
    },
)
class DnsRecordData:
    def __init__(
        self,
        *,
        algorithm: typing.Optional[jsii.Number] = None,
        altitude: typing.Optional[jsii.Number] = None,
        certificate: typing.Optional[builtins.str] = None,
        digest: typing.Optional[builtins.str] = None,
        digest_type: typing.Optional[jsii.Number] = None,
        fingerprint: typing.Optional[builtins.str] = None,
        flags: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        key_tag: typing.Optional[jsii.Number] = None,
        lat_degrees: typing.Optional[jsii.Number] = None,
        lat_direction: typing.Optional[builtins.str] = None,
        lat_minutes: typing.Optional[jsii.Number] = None,
        lat_seconds: typing.Optional[jsii.Number] = None,
        long_degrees: typing.Optional[jsii.Number] = None,
        long_direction: typing.Optional[builtins.str] = None,
        long_minutes: typing.Optional[jsii.Number] = None,
        long_seconds: typing.Optional[jsii.Number] = None,
        matching_type: typing.Optional[jsii.Number] = None,
        order: typing.Optional[jsii.Number] = None,
        port: typing.Optional[jsii.Number] = None,
        precision_horz: typing.Optional[jsii.Number] = None,
        precision_vert: typing.Optional[jsii.Number] = None,
        preference: typing.Optional[jsii.Number] = None,
        priority: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[jsii.Number] = None,
        public_key: typing.Optional[builtins.str] = None,
        regex: typing.Optional[builtins.str] = None,
        replacement: typing.Optional[builtins.str] = None,
        selector: typing.Optional[jsii.Number] = None,
        service: typing.Optional[builtins.str] = None,
        size: typing.Optional[jsii.Number] = None,
        tag: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        type: typing.Optional[jsii.Number] = None,
        usage: typing.Optional[jsii.Number] = None,
        value: typing.Optional[builtins.str] = None,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param algorithm: Algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#algorithm DnsRecord#algorithm}
        :param altitude: Altitude of location in meters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#altitude DnsRecord#altitude}
        :param certificate: Certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#certificate DnsRecord#certificate}
        :param digest: Digest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#digest DnsRecord#digest}
        :param digest_type: Digest Type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#digest_type DnsRecord#digest_type}
        :param fingerprint: Fingerprint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#fingerprint DnsRecord#fingerprint}
        :param flags: Flags for the CAA record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#flags DnsRecord#flags}
        :param key_tag: Key Tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#key_tag DnsRecord#key_tag}
        :param lat_degrees: Degrees of latitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_degrees DnsRecord#lat_degrees}
        :param lat_direction: Latitude direction. Available values: "N", "S". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_direction DnsRecord#lat_direction}
        :param lat_minutes: Minutes of latitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_minutes DnsRecord#lat_minutes}
        :param lat_seconds: Seconds of latitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_seconds DnsRecord#lat_seconds}
        :param long_degrees: Degrees of longitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_degrees DnsRecord#long_degrees}
        :param long_direction: Longitude direction. Available values: "E", "W". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_direction DnsRecord#long_direction}
        :param long_minutes: Minutes of longitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_minutes DnsRecord#long_minutes}
        :param long_seconds: Seconds of longitude. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_seconds DnsRecord#long_seconds}
        :param matching_type: Matching Type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#matching_type DnsRecord#matching_type}
        :param order: Order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#order DnsRecord#order}
        :param port: The port of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#port DnsRecord#port}
        :param precision_horz: Horizontal precision of location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#precision_horz DnsRecord#precision_horz}
        :param precision_vert: Vertical precision of location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#precision_vert DnsRecord#precision_vert}
        :param preference: Preference. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#preference DnsRecord#preference}
        :param priority: Priority. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#priority DnsRecord#priority}
        :param protocol: Protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#protocol DnsRecord#protocol}
        :param public_key: Public Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#public_key DnsRecord#public_key}
        :param regex: Regex. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#regex DnsRecord#regex}
        :param replacement: Replacement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#replacement DnsRecord#replacement}
        :param selector: Selector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#selector DnsRecord#selector}
        :param service: Service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#service DnsRecord#service}
        :param size: Size of location in meters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#size DnsRecord#size}
        :param tag: Name of the property controlled by this record (e.g.: issue, issuewild, iodef). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#tag DnsRecord#tag}
        :param target: Target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#target DnsRecord#target}
        :param type: Type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#type DnsRecord#type}
        :param usage: Usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#usage DnsRecord#usage}
        :param value: Value of the record. This field's semantics depend on the chosen tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#value DnsRecord#value}
        :param weight: The record weight. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#weight DnsRecord#weight}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c6a2b34fb8f5ecce8ddcb058ef76280f4a87c5101c68cb19706f16386ea7175)
            check_type(argname="argument algorithm", value=algorithm, expected_type=type_hints["algorithm"])
            check_type(argname="argument altitude", value=altitude, expected_type=type_hints["altitude"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument digest", value=digest, expected_type=type_hints["digest"])
            check_type(argname="argument digest_type", value=digest_type, expected_type=type_hints["digest_type"])
            check_type(argname="argument fingerprint", value=fingerprint, expected_type=type_hints["fingerprint"])
            check_type(argname="argument flags", value=flags, expected_type=type_hints["flags"])
            check_type(argname="argument key_tag", value=key_tag, expected_type=type_hints["key_tag"])
            check_type(argname="argument lat_degrees", value=lat_degrees, expected_type=type_hints["lat_degrees"])
            check_type(argname="argument lat_direction", value=lat_direction, expected_type=type_hints["lat_direction"])
            check_type(argname="argument lat_minutes", value=lat_minutes, expected_type=type_hints["lat_minutes"])
            check_type(argname="argument lat_seconds", value=lat_seconds, expected_type=type_hints["lat_seconds"])
            check_type(argname="argument long_degrees", value=long_degrees, expected_type=type_hints["long_degrees"])
            check_type(argname="argument long_direction", value=long_direction, expected_type=type_hints["long_direction"])
            check_type(argname="argument long_minutes", value=long_minutes, expected_type=type_hints["long_minutes"])
            check_type(argname="argument long_seconds", value=long_seconds, expected_type=type_hints["long_seconds"])
            check_type(argname="argument matching_type", value=matching_type, expected_type=type_hints["matching_type"])
            check_type(argname="argument order", value=order, expected_type=type_hints["order"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument precision_horz", value=precision_horz, expected_type=type_hints["precision_horz"])
            check_type(argname="argument precision_vert", value=precision_vert, expected_type=type_hints["precision_vert"])
            check_type(argname="argument preference", value=preference, expected_type=type_hints["preference"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument public_key", value=public_key, expected_type=type_hints["public_key"])
            check_type(argname="argument regex", value=regex, expected_type=type_hints["regex"])
            check_type(argname="argument replacement", value=replacement, expected_type=type_hints["replacement"])
            check_type(argname="argument selector", value=selector, expected_type=type_hints["selector"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument size", value=size, expected_type=type_hints["size"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument usage", value=usage, expected_type=type_hints["usage"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument weight", value=weight, expected_type=type_hints["weight"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if algorithm is not None:
            self._values["algorithm"] = algorithm
        if altitude is not None:
            self._values["altitude"] = altitude
        if certificate is not None:
            self._values["certificate"] = certificate
        if digest is not None:
            self._values["digest"] = digest
        if digest_type is not None:
            self._values["digest_type"] = digest_type
        if fingerprint is not None:
            self._values["fingerprint"] = fingerprint
        if flags is not None:
            self._values["flags"] = flags
        if key_tag is not None:
            self._values["key_tag"] = key_tag
        if lat_degrees is not None:
            self._values["lat_degrees"] = lat_degrees
        if lat_direction is not None:
            self._values["lat_direction"] = lat_direction
        if lat_minutes is not None:
            self._values["lat_minutes"] = lat_minutes
        if lat_seconds is not None:
            self._values["lat_seconds"] = lat_seconds
        if long_degrees is not None:
            self._values["long_degrees"] = long_degrees
        if long_direction is not None:
            self._values["long_direction"] = long_direction
        if long_minutes is not None:
            self._values["long_minutes"] = long_minutes
        if long_seconds is not None:
            self._values["long_seconds"] = long_seconds
        if matching_type is not None:
            self._values["matching_type"] = matching_type
        if order is not None:
            self._values["order"] = order
        if port is not None:
            self._values["port"] = port
        if precision_horz is not None:
            self._values["precision_horz"] = precision_horz
        if precision_vert is not None:
            self._values["precision_vert"] = precision_vert
        if preference is not None:
            self._values["preference"] = preference
        if priority is not None:
            self._values["priority"] = priority
        if protocol is not None:
            self._values["protocol"] = protocol
        if public_key is not None:
            self._values["public_key"] = public_key
        if regex is not None:
            self._values["regex"] = regex
        if replacement is not None:
            self._values["replacement"] = replacement
        if selector is not None:
            self._values["selector"] = selector
        if service is not None:
            self._values["service"] = service
        if size is not None:
            self._values["size"] = size
        if tag is not None:
            self._values["tag"] = tag
        if target is not None:
            self._values["target"] = target
        if type is not None:
            self._values["type"] = type
        if usage is not None:
            self._values["usage"] = usage
        if value is not None:
            self._values["value"] = value
        if weight is not None:
            self._values["weight"] = weight

    @builtins.property
    def algorithm(self) -> typing.Optional[jsii.Number]:
        '''Algorithm.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#algorithm DnsRecord#algorithm}
        '''
        result = self._values.get("algorithm")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def altitude(self) -> typing.Optional[jsii.Number]:
        '''Altitude of location in meters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#altitude DnsRecord#altitude}
        '''
        result = self._values.get("altitude")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def certificate(self) -> typing.Optional[builtins.str]:
        '''Certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#certificate DnsRecord#certificate}
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def digest(self) -> typing.Optional[builtins.str]:
        '''Digest.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#digest DnsRecord#digest}
        '''
        result = self._values.get("digest")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def digest_type(self) -> typing.Optional[jsii.Number]:
        '''Digest Type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#digest_type DnsRecord#digest_type}
        '''
        result = self._values.get("digest_type")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fingerprint(self) -> typing.Optional[builtins.str]:
        '''Fingerprint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#fingerprint DnsRecord#fingerprint}
        '''
        result = self._values.get("fingerprint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def flags(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Flags for the CAA record.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#flags DnsRecord#flags}
        '''
        result = self._values.get("flags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def key_tag(self) -> typing.Optional[jsii.Number]:
        '''Key Tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#key_tag DnsRecord#key_tag}
        '''
        result = self._values.get("key_tag")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lat_degrees(self) -> typing.Optional[jsii.Number]:
        '''Degrees of latitude.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_degrees DnsRecord#lat_degrees}
        '''
        result = self._values.get("lat_degrees")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lat_direction(self) -> typing.Optional[builtins.str]:
        '''Latitude direction. Available values: "N", "S".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_direction DnsRecord#lat_direction}
        '''
        result = self._values.get("lat_direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lat_minutes(self) -> typing.Optional[jsii.Number]:
        '''Minutes of latitude.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_minutes DnsRecord#lat_minutes}
        '''
        result = self._values.get("lat_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lat_seconds(self) -> typing.Optional[jsii.Number]:
        '''Seconds of latitude.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#lat_seconds DnsRecord#lat_seconds}
        '''
        result = self._values.get("lat_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def long_degrees(self) -> typing.Optional[jsii.Number]:
        '''Degrees of longitude.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_degrees DnsRecord#long_degrees}
        '''
        result = self._values.get("long_degrees")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def long_direction(self) -> typing.Optional[builtins.str]:
        '''Longitude direction. Available values: "E", "W".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_direction DnsRecord#long_direction}
        '''
        result = self._values.get("long_direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def long_minutes(self) -> typing.Optional[jsii.Number]:
        '''Minutes of longitude.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_minutes DnsRecord#long_minutes}
        '''
        result = self._values.get("long_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def long_seconds(self) -> typing.Optional[jsii.Number]:
        '''Seconds of longitude.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#long_seconds DnsRecord#long_seconds}
        '''
        result = self._values.get("long_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def matching_type(self) -> typing.Optional[jsii.Number]:
        '''Matching Type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#matching_type DnsRecord#matching_type}
        '''
        result = self._values.get("matching_type")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def order(self) -> typing.Optional[jsii.Number]:
        '''Order.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#order DnsRecord#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The port of the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#port DnsRecord#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def precision_horz(self) -> typing.Optional[jsii.Number]:
        '''Horizontal precision of location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#precision_horz DnsRecord#precision_horz}
        '''
        result = self._values.get("precision_horz")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def precision_vert(self) -> typing.Optional[jsii.Number]:
        '''Vertical precision of location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#precision_vert DnsRecord#precision_vert}
        '''
        result = self._values.get("precision_vert")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preference(self) -> typing.Optional[jsii.Number]:
        '''Preference.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#preference DnsRecord#preference}
        '''
        result = self._values.get("preference")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Priority.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#priority DnsRecord#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def protocol(self) -> typing.Optional[jsii.Number]:
        '''Protocol.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#protocol DnsRecord#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def public_key(self) -> typing.Optional[builtins.str]:
        '''Public Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#public_key DnsRecord#public_key}
        '''
        result = self._values.get("public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def regex(self) -> typing.Optional[builtins.str]:
        '''Regex.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#regex DnsRecord#regex}
        '''
        result = self._values.get("regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replacement(self) -> typing.Optional[builtins.str]:
        '''Replacement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#replacement DnsRecord#replacement}
        '''
        result = self._values.get("replacement")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def selector(self) -> typing.Optional[jsii.Number]:
        '''Selector.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#selector DnsRecord#selector}
        '''
        result = self._values.get("selector")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''Service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#service DnsRecord#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def size(self) -> typing.Optional[jsii.Number]:
        '''Size of location in meters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#size DnsRecord#size}
        '''
        result = self._values.get("size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''Name of the property controlled by this record (e.g.: issue, issuewild, iodef).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#tag DnsRecord#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#target DnsRecord#target}
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[jsii.Number]:
        '''Type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#type DnsRecord#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def usage(self) -> typing.Optional[jsii.Number]:
        '''Usage.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#usage DnsRecord#usage}
        '''
        result = self._values.get("usage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Value of the record. This field's semantics depend on the chosen tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#value DnsRecord#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def weight(self) -> typing.Optional[jsii.Number]:
        '''The record weight.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#weight DnsRecord#weight}
        '''
        result = self._values.get("weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DnsRecordData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DnsRecordDataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dnsRecord.DnsRecordDataOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffae8025dc1673480d2202a2c6770c954f71c34741b357d68417237f4a09bb5c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAlgorithm")
    def reset_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlgorithm", []))

    @jsii.member(jsii_name="resetAltitude")
    def reset_altitude(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAltitude", []))

    @jsii.member(jsii_name="resetCertificate")
    def reset_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificate", []))

    @jsii.member(jsii_name="resetDigest")
    def reset_digest(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDigest", []))

    @jsii.member(jsii_name="resetDigestType")
    def reset_digest_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDigestType", []))

    @jsii.member(jsii_name="resetFingerprint")
    def reset_fingerprint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFingerprint", []))

    @jsii.member(jsii_name="resetFlags")
    def reset_flags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFlags", []))

    @jsii.member(jsii_name="resetKeyTag")
    def reset_key_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyTag", []))

    @jsii.member(jsii_name="resetLatDegrees")
    def reset_lat_degrees(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatDegrees", []))

    @jsii.member(jsii_name="resetLatDirection")
    def reset_lat_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatDirection", []))

    @jsii.member(jsii_name="resetLatMinutes")
    def reset_lat_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatMinutes", []))

    @jsii.member(jsii_name="resetLatSeconds")
    def reset_lat_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatSeconds", []))

    @jsii.member(jsii_name="resetLongDegrees")
    def reset_long_degrees(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLongDegrees", []))

    @jsii.member(jsii_name="resetLongDirection")
    def reset_long_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLongDirection", []))

    @jsii.member(jsii_name="resetLongMinutes")
    def reset_long_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLongMinutes", []))

    @jsii.member(jsii_name="resetLongSeconds")
    def reset_long_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLongSeconds", []))

    @jsii.member(jsii_name="resetMatchingType")
    def reset_matching_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatchingType", []))

    @jsii.member(jsii_name="resetOrder")
    def reset_order(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrder", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetPrecisionHorz")
    def reset_precision_horz(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrecisionHorz", []))

    @jsii.member(jsii_name="resetPrecisionVert")
    def reset_precision_vert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrecisionVert", []))

    @jsii.member(jsii_name="resetPreference")
    def reset_preference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreference", []))

    @jsii.member(jsii_name="resetPriority")
    def reset_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPriority", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @jsii.member(jsii_name="resetPublicKey")
    def reset_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicKey", []))

    @jsii.member(jsii_name="resetRegex")
    def reset_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegex", []))

    @jsii.member(jsii_name="resetReplacement")
    def reset_replacement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplacement", []))

    @jsii.member(jsii_name="resetSelector")
    def reset_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelector", []))

    @jsii.member(jsii_name="resetService")
    def reset_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetService", []))

    @jsii.member(jsii_name="resetSize")
    def reset_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSize", []))

    @jsii.member(jsii_name="resetTag")
    def reset_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTag", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetUsage")
    def reset_usage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsage", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @jsii.member(jsii_name="resetWeight")
    def reset_weight(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeight", []))

    @builtins.property
    @jsii.member(jsii_name="algorithmInput")
    def algorithm_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "algorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="altitudeInput")
    def altitude_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "altitudeInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="digestInput")
    def digest_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "digestInput"))

    @builtins.property
    @jsii.member(jsii_name="digestTypeInput")
    def digest_type_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "digestTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="fingerprintInput")
    def fingerprint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fingerprintInput"))

    @builtins.property
    @jsii.member(jsii_name="flagsInput")
    def flags_input(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "flagsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyTagInput")
    def key_tag_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keyTagInput"))

    @builtins.property
    @jsii.member(jsii_name="latDegreesInput")
    def lat_degrees_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "latDegreesInput"))

    @builtins.property
    @jsii.member(jsii_name="latDirectionInput")
    def lat_direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "latDirectionInput"))

    @builtins.property
    @jsii.member(jsii_name="latMinutesInput")
    def lat_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "latMinutesInput"))

    @builtins.property
    @jsii.member(jsii_name="latSecondsInput")
    def lat_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "latSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="longDegreesInput")
    def long_degrees_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "longDegreesInput"))

    @builtins.property
    @jsii.member(jsii_name="longDirectionInput")
    def long_direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "longDirectionInput"))

    @builtins.property
    @jsii.member(jsii_name="longMinutesInput")
    def long_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "longMinutesInput"))

    @builtins.property
    @jsii.member(jsii_name="longSecondsInput")
    def long_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "longSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="matchingTypeInput")
    def matching_type_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "matchingTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="orderInput")
    def order_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "orderInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="precisionHorzInput")
    def precision_horz_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "precisionHorzInput"))

    @builtins.property
    @jsii.member(jsii_name="precisionVertInput")
    def precision_vert_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "precisionVertInput"))

    @builtins.property
    @jsii.member(jsii_name="preferenceInput")
    def preference_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "preferenceInput"))

    @builtins.property
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="publicKeyInput")
    def public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="regexInput")
    def regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regexInput"))

    @builtins.property
    @jsii.member(jsii_name="replacementInput")
    def replacement_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replacementInput"))

    @builtins.property
    @jsii.member(jsii_name="selectorInput")
    def selector_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "selectorInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInput")
    def size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInput"))

    @builtins.property
    @jsii.member(jsii_name="tagInput")
    def tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="usageInput")
    def usage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "usageInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="weightInput")
    def weight_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "weightInput"))

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89671d242e30a4ec60dd20fe009660fc8b72dd405adcefc4a219be491adc857f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="altitude")
    def altitude(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "altitude"))

    @altitude.setter
    def altitude(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9cc44cb55ae14c19cd2543210574abd7ec87d06383e6eef3d2eabc14887aa88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "altitude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__431a76d52ebf48a22455dd158f98edeb3f9846add28d68e7024b8a4add00ee00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="digest")
    def digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "digest"))

    @digest.setter
    def digest(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6da0a6527bcd0eaa153ede4f09631d26e1e08addfde9def402a56e33e3d4ec4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "digest", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="digestType")
    def digest_type(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "digestType"))

    @digest_type.setter
    def digest_type(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c396aa7e6b6f1ccd8db42902dfbf64277ea8bf2bab6f22c1a382c017edecd897)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "digestType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fingerprint")
    def fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fingerprint"))

    @fingerprint.setter
    def fingerprint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf27fe4c87a746bcb8daadc20a7aa823948c42f4b81783dccd2b5d0a9e77091f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fingerprint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="flags")
    def flags(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "flags"))

    @flags.setter
    def flags(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c91f4a136188c3e21c4e80f05e8ff2d41ba91691819ae9ba535f26662db26bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "flags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyTag")
    def key_tag(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keyTag"))

    @key_tag.setter
    def key_tag(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5750dec31e17b522ef8d7c2f9a273efdbeaaf4f318a7a53420297f8d6aead363)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latDegrees")
    def lat_degrees(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latDegrees"))

    @lat_degrees.setter
    def lat_degrees(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__184a25071dd5201888045b3396b4cf7fbc573f65e191b59aa249004720d3f0ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latDegrees", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latDirection")
    def lat_direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latDirection"))

    @lat_direction.setter
    def lat_direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc1bc80efc7cbd339a4cb95d10b11f4bc40ef65db507883f38c6a85f1577eda7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latDirection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latMinutes")
    def lat_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latMinutes"))

    @lat_minutes.setter
    def lat_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9afc3ab88c0e295a60a9ae4fe766c9a71cbcda068193a5d1bb177215accd456f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latMinutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latSeconds")
    def lat_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latSeconds"))

    @lat_seconds.setter
    def lat_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07935bfdb2d4416d1567d49501f261eb33c567cf3b6df95422d3c5712c2ab3aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="longDegrees")
    def long_degrees(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longDegrees"))

    @long_degrees.setter
    def long_degrees(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__184598042298efa921d9d8fbb4155c8583443649b2c129daf9f72d855c4caada)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "longDegrees", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="longDirection")
    def long_direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "longDirection"))

    @long_direction.setter
    def long_direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09c60ccd537e74115855bccebf00b31b79f38de0b2ea3e287471228158b3a80f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "longDirection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="longMinutes")
    def long_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longMinutes"))

    @long_minutes.setter
    def long_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed9a55cf1a99c3caae11ded431071578c4bb8bd3e362a6aaacde2f9d0bbdd872)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "longMinutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="longSeconds")
    def long_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longSeconds"))

    @long_seconds.setter
    def long_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed584241d94127f2e6c5845ebff2c7faec2508c4bde7845b12477ac413055532)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "longSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="matchingType")
    def matching_type(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "matchingType"))

    @matching_type.setter
    def matching_type(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fa7b220d635b5d8ce4371e273185ce536b1cfcefc3d26e08853f15f21d411d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "matchingType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="order")
    def order(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "order"))

    @order.setter
    def order(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c240aa8393e4b8664a4e089103998ec320a981b4f968ace481f17e876f75658)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "order", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f6d725ee38fcfab076e8fc564f69b6daf8e3657d853eddb07c4e76143154cd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="precisionHorz")
    def precision_horz(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precisionHorz"))

    @precision_horz.setter
    def precision_horz(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f4e7083ef3d52315d152d75158ee0be5ecef1c67572fd32c59f2b296c40dd00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "precisionHorz", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="precisionVert")
    def precision_vert(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precisionVert"))

    @precision_vert.setter
    def precision_vert(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e9c023e7221b688ceba6a4251cf037679b7f393672dfe33fcecde09ae71bbee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "precisionVert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preference")
    def preference(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "preference"))

    @preference.setter
    def preference(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f283899023c11abccf904470b28a25ae118d9966a9d2b96a51128799dca9d77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preference", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb007d8c091071a52e5ee840099e757f704a039d0245e2d1dd2eb85e78c9fb10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b054896928ef43f9fd5670a9a74577235a01e0085d6176c5dace90a1e273d669)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @public_key.setter
    def public_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__105e95013316a261dbcdb302f1c943862dd086e2c9dce3a201456cd78b2d28b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @regex.setter
    def regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__679925a7222bdb3ccd37378b8dfa441cad00bc5af00ac9f8a51f094c91c4584e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replacement")
    def replacement(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replacement"))

    @replacement.setter
    def replacement(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6504e8e9c2f70fa29021fddbbd1b3b7069de68314329d0d01a75fd3ac6c2a2a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replacement", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="selector")
    def selector(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "selector"))

    @selector.setter
    def selector(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__773bdded8d5ca409da1affc1f6442750a9da0c4a1a433f6c4cb8c2a884e8b3c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "selector", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08a84585783c5bf620864dcf262a50d42646c957b6549069f0a5e4fe6373ff10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @size.setter
    def size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10842657f686835164f6bcd62218d7a89fc1f323b6067b62683188cf4289a9c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "size", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d54f7be2e5ad897aae3260b4b1edca514f4b127222c31b5fc2b56d2fdbfc2bee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__078c126e6e470e7f4f8956dd78cbfcd3d760de2cdefcea92dd1a9cb29459d385)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "type"))

    @type.setter
    def type(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0868dcfa54f3d3f23d75ecdd6d5e40b23447667ab71ba0eba8297e4ce37781f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usage")
    def usage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "usage"))

    @usage.setter
    def usage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b479f37a6d75b5ee38f7dd9aaff354427d926ceb6f4fa4cb1e0ed9d3d841beae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89fcdf9758129a6c28d3ea17782ee909cd335a2ad9c667757d6cdfad2935e7db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="weight")
    def weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weight"))

    @weight.setter
    def weight(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c14b788689e1928c5e6d8d65dc94c60ec190535904f5590e942f7c1e82057da0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "weight", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsRecordData]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsRecordData]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsRecordData]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e15c884c265a68183b5fd24e39dbd5ddbb790cfae8ebe847bfb4589ad657916)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dnsRecord.DnsRecordSettings",
    jsii_struct_bases=[],
    name_mapping={
        "flatten_cname": "flattenCname",
        "ipv4_only": "ipv4Only",
        "ipv6_only": "ipv6Only",
    },
)
class DnsRecordSettings:
    def __init__(
        self,
        *,
        flatten_cname: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ipv4_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ipv6_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param flatten_cname: If enabled, causes the CNAME record to be resolved externally and the resulting address records (e.g., A and AAAA) to be returned instead of the CNAME record itself. This setting is unavailable for proxied records, since they are always flattened. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#flatten_cname DnsRecord#flatten_cname}
        :param ipv4_only: When enabled, only A records will be generated, and AAAA records will not be created. This setting is intended for exceptional cases. Note that this option only applies to proxied records and it has no effect on whether Cloudflare communicates with the origin using IPv4 or IPv6. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#ipv4_only DnsRecord#ipv4_only}
        :param ipv6_only: When enabled, only AAAA records will be generated, and A records will not be created. This setting is intended for exceptional cases. Note that this option only applies to proxied records and it has no effect on whether Cloudflare communicates with the origin using IPv4 or IPv6. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#ipv6_only DnsRecord#ipv6_only}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b7692dd47a5a245a72845d854858941e2f9d598bcfa128b375ebef4d7a5cdfd)
            check_type(argname="argument flatten_cname", value=flatten_cname, expected_type=type_hints["flatten_cname"])
            check_type(argname="argument ipv4_only", value=ipv4_only, expected_type=type_hints["ipv4_only"])
            check_type(argname="argument ipv6_only", value=ipv6_only, expected_type=type_hints["ipv6_only"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if flatten_cname is not None:
            self._values["flatten_cname"] = flatten_cname
        if ipv4_only is not None:
            self._values["ipv4_only"] = ipv4_only
        if ipv6_only is not None:
            self._values["ipv6_only"] = ipv6_only

    @builtins.property
    def flatten_cname(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If enabled, causes the CNAME record to be resolved externally and the resulting address records (e.g., A and AAAA) to be returned instead of the CNAME record itself. This setting is unavailable for proxied records, since they are always flattened.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#flatten_cname DnsRecord#flatten_cname}
        '''
        result = self._values.get("flatten_cname")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ipv4_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When enabled, only A records will be generated, and AAAA records will not be created.

        This setting is intended for exceptional cases. Note that this option only applies to proxied records and it has no effect on whether Cloudflare communicates with the origin using IPv4 or IPv6.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#ipv4_only DnsRecord#ipv4_only}
        '''
        result = self._values.get("ipv4_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ipv6_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When enabled, only AAAA records will be generated, and A records will not be created.

        This setting is intended for exceptional cases. Note that this option only applies to proxied records and it has no effect on whether Cloudflare communicates with the origin using IPv4 or IPv6.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/dns_record#ipv6_only DnsRecord#ipv6_only}
        '''
        result = self._values.get("ipv6_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DnsRecordSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DnsRecordSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dnsRecord.DnsRecordSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e124c4fac92168ca9cf507be1102d68b84f7cbb96ec07d007ca224c72e331731)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFlattenCname")
    def reset_flatten_cname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFlattenCname", []))

    @jsii.member(jsii_name="resetIpv4Only")
    def reset_ipv4_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4Only", []))

    @jsii.member(jsii_name="resetIpv6Only")
    def reset_ipv6_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6Only", []))

    @builtins.property
    @jsii.member(jsii_name="flattenCnameInput")
    def flatten_cname_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "flattenCnameInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv4OnlyInput")
    def ipv4_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ipv4OnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv6OnlyInput")
    def ipv6_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ipv6OnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="flattenCname")
    def flatten_cname(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "flattenCname"))

    @flatten_cname.setter
    def flatten_cname(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77be35f087ef4055f67b19b6cc23a76db00665e23a26583e849b97b665ac7d3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "flattenCname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Only")
    def ipv4_only(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ipv4Only"))

    @ipv4_only.setter
    def ipv4_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d5372157ef733b8f0ed81b743bb290c1cdd95237be828af74088a00af4e661a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Only", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Only")
    def ipv6_only(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ipv6Only"))

    @ipv6_only.setter
    def ipv6_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48cacf9d392cbe408a3ee7218d7cf8ebfb5e6fbfc9ca2cbbd4e6387f2ec24fb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Only", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsRecordSettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsRecordSettings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsRecordSettings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ada12ef71f8ab72a547ceb4c2944d51c51a8311d9f5afc2183a180ff007a5c59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DnsRecord",
    "DnsRecordConfig",
    "DnsRecordData",
    "DnsRecordDataOutputReference",
    "DnsRecordSettings",
    "DnsRecordSettingsOutputReference",
]

publication.publish()

def _typecheckingstub__1d1e4b33e059c7560d80448e275d13c08e147ebc16405b527ea368635ebdeb57(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    ttl: jsii.Number,
    type: builtins.str,
    zone_id: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    content: typing.Optional[builtins.str] = None,
    data: typing.Optional[typing.Union[DnsRecordData, typing.Dict[builtins.str, typing.Any]]] = None,
    priority: typing.Optional[jsii.Number] = None,
    proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    settings: typing.Optional[typing.Union[DnsRecordSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__ff9592783ada9de699a70a313ace305cfe839f48bb79a392bb9b30ced66dbdb4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c81ab12041781173b6b28ce7d3db582146789af8d62c8044f98a4d0780e7523(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aa946175749029f209a4d96297218b6e52fa7c6a3b0b80d65fecd74cab4af2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__999b0cf80d39e26372232f0435a79065d6aeb48892b17e47a1c5fae8aafbf098(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c96caf2ec95cc43509afb161c12deb918c579e7409c3a1e09e91fd6612ebcf32(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48fc5ebcd34f90285a211308280c187dc34648cc29ffec7ede99a21cd64a84c5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__818db78f6836eb9f50c4216f7503241e4314c2b2f11063cd9e2115898a1e0301(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__098ec4f8c354f02533f21123e634bf7b688482f06013fbeb11b6aeed5d9a5ccd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bae9be44da3bfa4c93ffde6e1f54c2c0f99d819aa8925fba47495724dbffd728(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2fa97840b392aaa6043b3f87171fc447290f02eba27814b39f3268a94ab7e0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84483ca7f938b055e889e9f85be823a2219e9b0dfe6206f25c3b3076955c8bcf(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    ttl: jsii.Number,
    type: builtins.str,
    zone_id: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    content: typing.Optional[builtins.str] = None,
    data: typing.Optional[typing.Union[DnsRecordData, typing.Dict[builtins.str, typing.Any]]] = None,
    priority: typing.Optional[jsii.Number] = None,
    proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    settings: typing.Optional[typing.Union[DnsRecordSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c6a2b34fb8f5ecce8ddcb058ef76280f4a87c5101c68cb19706f16386ea7175(
    *,
    algorithm: typing.Optional[jsii.Number] = None,
    altitude: typing.Optional[jsii.Number] = None,
    certificate: typing.Optional[builtins.str] = None,
    digest: typing.Optional[builtins.str] = None,
    digest_type: typing.Optional[jsii.Number] = None,
    fingerprint: typing.Optional[builtins.str] = None,
    flags: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    key_tag: typing.Optional[jsii.Number] = None,
    lat_degrees: typing.Optional[jsii.Number] = None,
    lat_direction: typing.Optional[builtins.str] = None,
    lat_minutes: typing.Optional[jsii.Number] = None,
    lat_seconds: typing.Optional[jsii.Number] = None,
    long_degrees: typing.Optional[jsii.Number] = None,
    long_direction: typing.Optional[builtins.str] = None,
    long_minutes: typing.Optional[jsii.Number] = None,
    long_seconds: typing.Optional[jsii.Number] = None,
    matching_type: typing.Optional[jsii.Number] = None,
    order: typing.Optional[jsii.Number] = None,
    port: typing.Optional[jsii.Number] = None,
    precision_horz: typing.Optional[jsii.Number] = None,
    precision_vert: typing.Optional[jsii.Number] = None,
    preference: typing.Optional[jsii.Number] = None,
    priority: typing.Optional[jsii.Number] = None,
    protocol: typing.Optional[jsii.Number] = None,
    public_key: typing.Optional[builtins.str] = None,
    regex: typing.Optional[builtins.str] = None,
    replacement: typing.Optional[builtins.str] = None,
    selector: typing.Optional[jsii.Number] = None,
    service: typing.Optional[builtins.str] = None,
    size: typing.Optional[jsii.Number] = None,
    tag: typing.Optional[builtins.str] = None,
    target: typing.Optional[builtins.str] = None,
    type: typing.Optional[jsii.Number] = None,
    usage: typing.Optional[jsii.Number] = None,
    value: typing.Optional[builtins.str] = None,
    weight: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffae8025dc1673480d2202a2c6770c954f71c34741b357d68417237f4a09bb5c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89671d242e30a4ec60dd20fe009660fc8b72dd405adcefc4a219be491adc857f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9cc44cb55ae14c19cd2543210574abd7ec87d06383e6eef3d2eabc14887aa88(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__431a76d52ebf48a22455dd158f98edeb3f9846add28d68e7024b8a4add00ee00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6da0a6527bcd0eaa153ede4f09631d26e1e08addfde9def402a56e33e3d4ec4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c396aa7e6b6f1ccd8db42902dfbf64277ea8bf2bab6f22c1a382c017edecd897(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf27fe4c87a746bcb8daadc20a7aa823948c42f4b81783dccd2b5d0a9e77091f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c91f4a136188c3e21c4e80f05e8ff2d41ba91691819ae9ba535f26662db26bd(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5750dec31e17b522ef8d7c2f9a273efdbeaaf4f318a7a53420297f8d6aead363(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__184a25071dd5201888045b3396b4cf7fbc573f65e191b59aa249004720d3f0ad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc1bc80efc7cbd339a4cb95d10b11f4bc40ef65db507883f38c6a85f1577eda7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9afc3ab88c0e295a60a9ae4fe766c9a71cbcda068193a5d1bb177215accd456f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07935bfdb2d4416d1567d49501f261eb33c567cf3b6df95422d3c5712c2ab3aa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__184598042298efa921d9d8fbb4155c8583443649b2c129daf9f72d855c4caada(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09c60ccd537e74115855bccebf00b31b79f38de0b2ea3e287471228158b3a80f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed9a55cf1a99c3caae11ded431071578c4bb8bd3e362a6aaacde2f9d0bbdd872(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed584241d94127f2e6c5845ebff2c7faec2508c4bde7845b12477ac413055532(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fa7b220d635b5d8ce4371e273185ce536b1cfcefc3d26e08853f15f21d411d4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c240aa8393e4b8664a4e089103998ec320a981b4f968ace481f17e876f75658(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f6d725ee38fcfab076e8fc564f69b6daf8e3657d853eddb07c4e76143154cd3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f4e7083ef3d52315d152d75158ee0be5ecef1c67572fd32c59f2b296c40dd00(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e9c023e7221b688ceba6a4251cf037679b7f393672dfe33fcecde09ae71bbee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f283899023c11abccf904470b28a25ae118d9966a9d2b96a51128799dca9d77(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb007d8c091071a52e5ee840099e757f704a039d0245e2d1dd2eb85e78c9fb10(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b054896928ef43f9fd5670a9a74577235a01e0085d6176c5dace90a1e273d669(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__105e95013316a261dbcdb302f1c943862dd086e2c9dce3a201456cd78b2d28b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__679925a7222bdb3ccd37378b8dfa441cad00bc5af00ac9f8a51f094c91c4584e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6504e8e9c2f70fa29021fddbbd1b3b7069de68314329d0d01a75fd3ac6c2a2a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__773bdded8d5ca409da1affc1f6442750a9da0c4a1a433f6c4cb8c2a884e8b3c0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08a84585783c5bf620864dcf262a50d42646c957b6549069f0a5e4fe6373ff10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10842657f686835164f6bcd62218d7a89fc1f323b6067b62683188cf4289a9c9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d54f7be2e5ad897aae3260b4b1edca514f4b127222c31b5fc2b56d2fdbfc2bee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__078c126e6e470e7f4f8956dd78cbfcd3d760de2cdefcea92dd1a9cb29459d385(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0868dcfa54f3d3f23d75ecdd6d5e40b23447667ab71ba0eba8297e4ce37781f4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b479f37a6d75b5ee38f7dd9aaff354427d926ceb6f4fa4cb1e0ed9d3d841beae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89fcdf9758129a6c28d3ea17782ee909cd335a2ad9c667757d6cdfad2935e7db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c14b788689e1928c5e6d8d65dc94c60ec190535904f5590e942f7c1e82057da0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e15c884c265a68183b5fd24e39dbd5ddbb790cfae8ebe847bfb4589ad657916(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsRecordData]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b7692dd47a5a245a72845d854858941e2f9d598bcfa128b375ebef4d7a5cdfd(
    *,
    flatten_cname: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ipv4_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ipv6_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e124c4fac92168ca9cf507be1102d68b84f7cbb96ec07d007ca224c72e331731(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77be35f087ef4055f67b19b6cc23a76db00665e23a26583e849b97b665ac7d3f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d5372157ef733b8f0ed81b743bb290c1cdd95237be828af74088a00af4e661a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48cacf9d392cbe408a3ee7218d7cf8ebfb5e6fbfc9ca2cbbd4e6387f2ec24fb2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ada12ef71f8ab72a547ceb4c2944d51c51a8311d9f5afc2183a180ff007a5c59(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DnsRecordSettings]],
) -> None:
    """Type checking stubs"""
    pass
