r'''
# `cloudflare_zone_dns_settings`

Refer to the Terraform Registry for docs: [`cloudflare_zone_dns_settings`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings).
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


class ZoneDnsSettings(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zoneDnsSettings.ZoneDnsSettings",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings cloudflare_zone_dns_settings}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        zone_id: builtins.str,
        flatten_all_cnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        foundation_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        internal_dns: typing.Optional[typing.Union["ZoneDnsSettingsInternalDns", typing.Dict[builtins.str, typing.Any]]] = None,
        multi_provider: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        nameservers: typing.Optional[typing.Union["ZoneDnsSettingsNameservers", typing.Dict[builtins.str, typing.Any]]] = None,
        ns_ttl: typing.Optional[jsii.Number] = None,
        secondary_overrides: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        soa: typing.Optional[typing.Union["ZoneDnsSettingsSoa", typing.Dict[builtins.str, typing.Any]]] = None,
        zone_mode: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings cloudflare_zone_dns_settings} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#zone_id ZoneDnsSettings#zone_id}
        :param flatten_all_cnames: Whether to flatten all CNAME records in the zone. Note that, due to DNS limitations, a CNAME record at the zone apex will always be flattened. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#flatten_all_cnames ZoneDnsSettings#flatten_all_cnames}
        :param foundation_dns: Whether to enable Foundation DNS Advanced Nameservers on the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#foundation_dns ZoneDnsSettings#foundation_dns}
        :param internal_dns: Settings for this internal zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#internal_dns ZoneDnsSettings#internal_dns}
        :param multi_provider: Whether to enable multi-provider DNS, which causes Cloudflare to activate the zone even when non-Cloudflare NS records exist, and to respect NS records at the zone apex during outbound zone transfers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#multi_provider ZoneDnsSettings#multi_provider}
        :param nameservers: Settings determining the nameservers through which the zone should be available. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#nameservers ZoneDnsSettings#nameservers}
        :param ns_ttl: The time to live (TTL) of the zone's nameserver (NS) records. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#ns_ttl ZoneDnsSettings#ns_ttl}
        :param secondary_overrides: Allows a Secondary DNS zone to use (proxied) override records and CNAME flattening at the zone apex. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#secondary_overrides ZoneDnsSettings#secondary_overrides}
        :param soa: Components of the zone's SOA record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#soa ZoneDnsSettings#soa}
        :param zone_mode: Whether the zone mode is a regular or CDN/DNS only zone. Available values: "standard", "cdn_only", "dns_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#zone_mode ZoneDnsSettings#zone_mode}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72a7a45a39f58c58d3d0837cf0a7bcd2c149cfa6b12a96d07d6261ddb1167597)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZoneDnsSettingsConfig(
            zone_id=zone_id,
            flatten_all_cnames=flatten_all_cnames,
            foundation_dns=foundation_dns,
            internal_dns=internal_dns,
            multi_provider=multi_provider,
            nameservers=nameservers,
            ns_ttl=ns_ttl,
            secondary_overrides=secondary_overrides,
            soa=soa,
            zone_mode=zone_mode,
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
        '''Generates CDKTF code for importing a ZoneDnsSettings resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZoneDnsSettings to import.
        :param import_from_id: The id of the existing ZoneDnsSettings that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZoneDnsSettings to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b66a99a55215df0712c09fb32f8cc497504c1c2d537a7e6b1b0a35dfa046f8f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putInternalDns")
    def put_internal_dns(
        self,
        *,
        reference_zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param reference_zone_id: The ID of the zone to fallback to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#reference_zone_id ZoneDnsSettings#reference_zone_id}
        '''
        value = ZoneDnsSettingsInternalDns(reference_zone_id=reference_zone_id)

        return typing.cast(None, jsii.invoke(self, "putInternalDns", [value]))

    @jsii.member(jsii_name="putNameservers")
    def put_nameservers(
        self,
        *,
        type: builtins.str,
        ns_set: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Nameserver type Available values: "cloudflare.standard", "custom.account", "custom.tenant", "custom.zone". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#type ZoneDnsSettings#type}
        :param ns_set: Configured nameserver set to be used for this zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#ns_set ZoneDnsSettings#ns_set}
        '''
        value = ZoneDnsSettingsNameservers(type=type, ns_set=ns_set)

        return typing.cast(None, jsii.invoke(self, "putNameservers", [value]))

    @jsii.member(jsii_name="putSoa")
    def put_soa(
        self,
        *,
        expire: jsii.Number,
        min_ttl: jsii.Number,
        mname: builtins.str,
        refresh: jsii.Number,
        retry: jsii.Number,
        rname: builtins.str,
        ttl: jsii.Number,
    ) -> None:
        '''
        :param expire: Time in seconds of being unable to query the primary server after which secondary servers should stop serving the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#expire ZoneDnsSettings#expire}
        :param min_ttl: The time to live (TTL) for negative caching of records within the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#min_ttl ZoneDnsSettings#min_ttl}
        :param mname: The primary nameserver, which may be used for outbound zone transfers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#mname ZoneDnsSettings#mname}
        :param refresh: Time in seconds after which secondary servers should re-check the SOA record to see if the zone has been updated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#refresh ZoneDnsSettings#refresh}
        :param retry: Time in seconds after which secondary servers should retry queries after the primary server was unresponsive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#retry ZoneDnsSettings#retry}
        :param rname: The email address of the zone administrator, with the first label representing the local part of the email address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#rname ZoneDnsSettings#rname}
        :param ttl: The time to live (TTL) of the SOA record itself. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#ttl ZoneDnsSettings#ttl}
        '''
        value = ZoneDnsSettingsSoa(
            expire=expire,
            min_ttl=min_ttl,
            mname=mname,
            refresh=refresh,
            retry=retry,
            rname=rname,
            ttl=ttl,
        )

        return typing.cast(None, jsii.invoke(self, "putSoa", [value]))

    @jsii.member(jsii_name="resetFlattenAllCnames")
    def reset_flatten_all_cnames(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFlattenAllCnames", []))

    @jsii.member(jsii_name="resetFoundationDns")
    def reset_foundation_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFoundationDns", []))

    @jsii.member(jsii_name="resetInternalDns")
    def reset_internal_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternalDns", []))

    @jsii.member(jsii_name="resetMultiProvider")
    def reset_multi_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultiProvider", []))

    @jsii.member(jsii_name="resetNameservers")
    def reset_nameservers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNameservers", []))

    @jsii.member(jsii_name="resetNsTtl")
    def reset_ns_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNsTtl", []))

    @jsii.member(jsii_name="resetSecondaryOverrides")
    def reset_secondary_overrides(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryOverrides", []))

    @jsii.member(jsii_name="resetSoa")
    def reset_soa(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSoa", []))

    @jsii.member(jsii_name="resetZoneMode")
    def reset_zone_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneMode", []))

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
    @jsii.member(jsii_name="internalDns")
    def internal_dns(self) -> "ZoneDnsSettingsInternalDnsOutputReference":
        return typing.cast("ZoneDnsSettingsInternalDnsOutputReference", jsii.get(self, "internalDns"))

    @builtins.property
    @jsii.member(jsii_name="nameservers")
    def nameservers(self) -> "ZoneDnsSettingsNameserversOutputReference":
        return typing.cast("ZoneDnsSettingsNameserversOutputReference", jsii.get(self, "nameservers"))

    @builtins.property
    @jsii.member(jsii_name="soa")
    def soa(self) -> "ZoneDnsSettingsSoaOutputReference":
        return typing.cast("ZoneDnsSettingsSoaOutputReference", jsii.get(self, "soa"))

    @builtins.property
    @jsii.member(jsii_name="flattenAllCnamesInput")
    def flatten_all_cnames_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "flattenAllCnamesInput"))

    @builtins.property
    @jsii.member(jsii_name="foundationDnsInput")
    def foundation_dns_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "foundationDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalDnsInput")
    def internal_dns_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZoneDnsSettingsInternalDns"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZoneDnsSettingsInternalDns"]], jsii.get(self, "internalDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="multiProviderInput")
    def multi_provider_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "multiProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="nameserversInput")
    def nameservers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZoneDnsSettingsNameservers"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZoneDnsSettingsNameservers"]], jsii.get(self, "nameserversInput"))

    @builtins.property
    @jsii.member(jsii_name="nsTtlInput")
    def ns_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nsTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="secondaryOverridesInput")
    def secondary_overrides_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secondaryOverridesInput"))

    @builtins.property
    @jsii.member(jsii_name="soaInput")
    def soa_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZoneDnsSettingsSoa"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZoneDnsSettingsSoa"]], jsii.get(self, "soaInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneModeInput")
    def zone_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneModeInput"))

    @builtins.property
    @jsii.member(jsii_name="flattenAllCnames")
    def flatten_all_cnames(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "flattenAllCnames"))

    @flatten_all_cnames.setter
    def flatten_all_cnames(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f03ef6c9efac768f3b1301a4671659158774a61e44fd9a136899122f6c9da5fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "flattenAllCnames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="foundationDns")
    def foundation_dns(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "foundationDns"))

    @foundation_dns.setter
    def foundation_dns(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06d0aa118d26f6e6356ed42398d964940a771fe3889a2d5592f1120fdbcad8b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "foundationDns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="multiProvider")
    def multi_provider(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "multiProvider"))

    @multi_provider.setter
    def multi_provider(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac4ba0ceff9467ffbe8b34bfc462e9c2322e1f0c2c244bac734649b72362f85d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "multiProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nsTtl")
    def ns_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nsTtl"))

    @ns_ttl.setter
    def ns_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09e5aeddf8b5e604ddd98f0304a8f67b5dced04206c7ec1a3c2a36d0be36c5ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nsTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secondaryOverrides")
    def secondary_overrides(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secondaryOverrides"))

    @secondary_overrides.setter
    def secondary_overrides(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36c161bf11d611dac5e398d3aa9af12203d7647ac4a386333e494fbdcd202aba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryOverrides", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c28337c383567a613e847d0d12ce5fe982bb6d38dffeb07cdaee9e4c66cb79fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneMode")
    def zone_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneMode"))

    @zone_mode.setter
    def zone_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eec87ccd3e8d9870f4d94e317e56eaa7a6cf3386160fc0960d5db8c2da29b2b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneMode", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zoneDnsSettings.ZoneDnsSettingsConfig",
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
        "flatten_all_cnames": "flattenAllCnames",
        "foundation_dns": "foundationDns",
        "internal_dns": "internalDns",
        "multi_provider": "multiProvider",
        "nameservers": "nameservers",
        "ns_ttl": "nsTtl",
        "secondary_overrides": "secondaryOverrides",
        "soa": "soa",
        "zone_mode": "zoneMode",
    },
)
class ZoneDnsSettingsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        flatten_all_cnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        foundation_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        internal_dns: typing.Optional[typing.Union["ZoneDnsSettingsInternalDns", typing.Dict[builtins.str, typing.Any]]] = None,
        multi_provider: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        nameservers: typing.Optional[typing.Union["ZoneDnsSettingsNameservers", typing.Dict[builtins.str, typing.Any]]] = None,
        ns_ttl: typing.Optional[jsii.Number] = None,
        secondary_overrides: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        soa: typing.Optional[typing.Union["ZoneDnsSettingsSoa", typing.Dict[builtins.str, typing.Any]]] = None,
        zone_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#zone_id ZoneDnsSettings#zone_id}
        :param flatten_all_cnames: Whether to flatten all CNAME records in the zone. Note that, due to DNS limitations, a CNAME record at the zone apex will always be flattened. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#flatten_all_cnames ZoneDnsSettings#flatten_all_cnames}
        :param foundation_dns: Whether to enable Foundation DNS Advanced Nameservers on the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#foundation_dns ZoneDnsSettings#foundation_dns}
        :param internal_dns: Settings for this internal zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#internal_dns ZoneDnsSettings#internal_dns}
        :param multi_provider: Whether to enable multi-provider DNS, which causes Cloudflare to activate the zone even when non-Cloudflare NS records exist, and to respect NS records at the zone apex during outbound zone transfers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#multi_provider ZoneDnsSettings#multi_provider}
        :param nameservers: Settings determining the nameservers through which the zone should be available. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#nameservers ZoneDnsSettings#nameservers}
        :param ns_ttl: The time to live (TTL) of the zone's nameserver (NS) records. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#ns_ttl ZoneDnsSettings#ns_ttl}
        :param secondary_overrides: Allows a Secondary DNS zone to use (proxied) override records and CNAME flattening at the zone apex. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#secondary_overrides ZoneDnsSettings#secondary_overrides}
        :param soa: Components of the zone's SOA record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#soa ZoneDnsSettings#soa}
        :param zone_mode: Whether the zone mode is a regular or CDN/DNS only zone. Available values: "standard", "cdn_only", "dns_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#zone_mode ZoneDnsSettings#zone_mode}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(internal_dns, dict):
            internal_dns = ZoneDnsSettingsInternalDns(**internal_dns)
        if isinstance(nameservers, dict):
            nameservers = ZoneDnsSettingsNameservers(**nameservers)
        if isinstance(soa, dict):
            soa = ZoneDnsSettingsSoa(**soa)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__424068064902f5580baacd61a8713f8c7ccf6acac68330eeadef57a98733d726)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument flatten_all_cnames", value=flatten_all_cnames, expected_type=type_hints["flatten_all_cnames"])
            check_type(argname="argument foundation_dns", value=foundation_dns, expected_type=type_hints["foundation_dns"])
            check_type(argname="argument internal_dns", value=internal_dns, expected_type=type_hints["internal_dns"])
            check_type(argname="argument multi_provider", value=multi_provider, expected_type=type_hints["multi_provider"])
            check_type(argname="argument nameservers", value=nameservers, expected_type=type_hints["nameservers"])
            check_type(argname="argument ns_ttl", value=ns_ttl, expected_type=type_hints["ns_ttl"])
            check_type(argname="argument secondary_overrides", value=secondary_overrides, expected_type=type_hints["secondary_overrides"])
            check_type(argname="argument soa", value=soa, expected_type=type_hints["soa"])
            check_type(argname="argument zone_mode", value=zone_mode, expected_type=type_hints["zone_mode"])
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
        if flatten_all_cnames is not None:
            self._values["flatten_all_cnames"] = flatten_all_cnames
        if foundation_dns is not None:
            self._values["foundation_dns"] = foundation_dns
        if internal_dns is not None:
            self._values["internal_dns"] = internal_dns
        if multi_provider is not None:
            self._values["multi_provider"] = multi_provider
        if nameservers is not None:
            self._values["nameservers"] = nameservers
        if ns_ttl is not None:
            self._values["ns_ttl"] = ns_ttl
        if secondary_overrides is not None:
            self._values["secondary_overrides"] = secondary_overrides
        if soa is not None:
            self._values["soa"] = soa
        if zone_mode is not None:
            self._values["zone_mode"] = zone_mode

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#zone_id ZoneDnsSettings#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def flatten_all_cnames(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to flatten all CNAME records in the zone.

        Note that, due to DNS limitations, a CNAME record at the zone apex will always be flattened.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#flatten_all_cnames ZoneDnsSettings#flatten_all_cnames}
        '''
        result = self._values.get("flatten_all_cnames")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def foundation_dns(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to enable Foundation DNS Advanced Nameservers on the zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#foundation_dns ZoneDnsSettings#foundation_dns}
        '''
        result = self._values.get("foundation_dns")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def internal_dns(self) -> typing.Optional["ZoneDnsSettingsInternalDns"]:
        '''Settings for this internal zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#internal_dns ZoneDnsSettings#internal_dns}
        '''
        result = self._values.get("internal_dns")
        return typing.cast(typing.Optional["ZoneDnsSettingsInternalDns"], result)

    @builtins.property
    def multi_provider(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to enable multi-provider DNS, which causes Cloudflare to activate the zone even when non-Cloudflare NS records exist, and to respect NS records at the zone apex during outbound zone transfers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#multi_provider ZoneDnsSettings#multi_provider}
        '''
        result = self._values.get("multi_provider")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def nameservers(self) -> typing.Optional["ZoneDnsSettingsNameservers"]:
        '''Settings determining the nameservers through which the zone should be available.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#nameservers ZoneDnsSettings#nameservers}
        '''
        result = self._values.get("nameservers")
        return typing.cast(typing.Optional["ZoneDnsSettingsNameservers"], result)

    @builtins.property
    def ns_ttl(self) -> typing.Optional[jsii.Number]:
        '''The time to live (TTL) of the zone's nameserver (NS) records.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#ns_ttl ZoneDnsSettings#ns_ttl}
        '''
        result = self._values.get("ns_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def secondary_overrides(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allows a Secondary DNS zone to use (proxied) override records and CNAME flattening at the zone apex.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#secondary_overrides ZoneDnsSettings#secondary_overrides}
        '''
        result = self._values.get("secondary_overrides")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def soa(self) -> typing.Optional["ZoneDnsSettingsSoa"]:
        '''Components of the zone's SOA record.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#soa ZoneDnsSettings#soa}
        '''
        result = self._values.get("soa")
        return typing.cast(typing.Optional["ZoneDnsSettingsSoa"], result)

    @builtins.property
    def zone_mode(self) -> typing.Optional[builtins.str]:
        '''Whether the zone mode is a regular or CDN/DNS only zone. Available values: "standard", "cdn_only", "dns_only".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#zone_mode ZoneDnsSettings#zone_mode}
        '''
        result = self._values.get("zone_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneDnsSettingsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zoneDnsSettings.ZoneDnsSettingsInternalDns",
    jsii_struct_bases=[],
    name_mapping={"reference_zone_id": "referenceZoneId"},
)
class ZoneDnsSettingsInternalDns:
    def __init__(
        self,
        *,
        reference_zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param reference_zone_id: The ID of the zone to fallback to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#reference_zone_id ZoneDnsSettings#reference_zone_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4023034533d6d44b4edc6cc43c083b0b519e8cfb4fd4befb36ca12d37f1a8dcd)
            check_type(argname="argument reference_zone_id", value=reference_zone_id, expected_type=type_hints["reference_zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if reference_zone_id is not None:
            self._values["reference_zone_id"] = reference_zone_id

    @builtins.property
    def reference_zone_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the zone to fallback to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#reference_zone_id ZoneDnsSettings#reference_zone_id}
        '''
        result = self._values.get("reference_zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneDnsSettingsInternalDns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZoneDnsSettingsInternalDnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zoneDnsSettings.ZoneDnsSettingsInternalDnsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f62085d386d21b3c01d118102122ce231b728a69e6cc71ce9214f74bca4c7cdb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetReferenceZoneId")
    def reset_reference_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReferenceZoneId", []))

    @builtins.property
    @jsii.member(jsii_name="referenceZoneIdInput")
    def reference_zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "referenceZoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="referenceZoneId")
    def reference_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "referenceZoneId"))

    @reference_zone_id.setter
    def reference_zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85d3af0c1bfbd4d9c5e6df1541ab35d6e2fbc0680c5efd841015df9d99d34e18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "referenceZoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsInternalDns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsInternalDns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsInternalDns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__213a5c9234d4b93477b1cd728b90f5c6374164099569bcfa291c9333c37958a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zoneDnsSettings.ZoneDnsSettingsNameservers",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "ns_set": "nsSet"},
)
class ZoneDnsSettingsNameservers:
    def __init__(
        self,
        *,
        type: builtins.str,
        ns_set: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Nameserver type Available values: "cloudflare.standard", "custom.account", "custom.tenant", "custom.zone". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#type ZoneDnsSettings#type}
        :param ns_set: Configured nameserver set to be used for this zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#ns_set ZoneDnsSettings#ns_set}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fb750f788063a0a62700801b56b46f91514200834f26d6a8e8f209afacae010)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument ns_set", value=ns_set, expected_type=type_hints["ns_set"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if ns_set is not None:
            self._values["ns_set"] = ns_set

    @builtins.property
    def type(self) -> builtins.str:
        '''Nameserver type Available values: "cloudflare.standard", "custom.account", "custom.tenant", "custom.zone".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#type ZoneDnsSettings#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ns_set(self) -> typing.Optional[jsii.Number]:
        '''Configured nameserver set to be used for this zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#ns_set ZoneDnsSettings#ns_set}
        '''
        result = self._values.get("ns_set")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneDnsSettingsNameservers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZoneDnsSettingsNameserversOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zoneDnsSettings.ZoneDnsSettingsNameserversOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a1ac9785507195ba6c6d007cad68b58bc31662fe7f5d71d66f38616af07b1a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetNsSet")
    def reset_ns_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNsSet", []))

    @builtins.property
    @jsii.member(jsii_name="nsSetInput")
    def ns_set_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nsSetInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="nsSet")
    def ns_set(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nsSet"))

    @ns_set.setter
    def ns_set(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22a190277d724da7e8333af48ead01a437a9cf0fb0807d8b402c408b5a633d4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6c86fc5648589929693b57b3ce2d2df43981a999522248fdaf7f2671f41e24a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsNameservers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsNameservers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsNameservers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de4cce3dabba9d052b3f6db12a3ee637fac7394d64ffef529f171f27445dec62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zoneDnsSettings.ZoneDnsSettingsSoa",
    jsii_struct_bases=[],
    name_mapping={
        "expire": "expire",
        "min_ttl": "minTtl",
        "mname": "mname",
        "refresh": "refresh",
        "retry": "retry",
        "rname": "rname",
        "ttl": "ttl",
    },
)
class ZoneDnsSettingsSoa:
    def __init__(
        self,
        *,
        expire: jsii.Number,
        min_ttl: jsii.Number,
        mname: builtins.str,
        refresh: jsii.Number,
        retry: jsii.Number,
        rname: builtins.str,
        ttl: jsii.Number,
    ) -> None:
        '''
        :param expire: Time in seconds of being unable to query the primary server after which secondary servers should stop serving the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#expire ZoneDnsSettings#expire}
        :param min_ttl: The time to live (TTL) for negative caching of records within the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#min_ttl ZoneDnsSettings#min_ttl}
        :param mname: The primary nameserver, which may be used for outbound zone transfers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#mname ZoneDnsSettings#mname}
        :param refresh: Time in seconds after which secondary servers should re-check the SOA record to see if the zone has been updated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#refresh ZoneDnsSettings#refresh}
        :param retry: Time in seconds after which secondary servers should retry queries after the primary server was unresponsive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#retry ZoneDnsSettings#retry}
        :param rname: The email address of the zone administrator, with the first label representing the local part of the email address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#rname ZoneDnsSettings#rname}
        :param ttl: The time to live (TTL) of the SOA record itself. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#ttl ZoneDnsSettings#ttl}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__227bd8c1eb420c3e6fcba79b5c2358219f1301cc6f520f59d52e793a83ef489c)
            check_type(argname="argument expire", value=expire, expected_type=type_hints["expire"])
            check_type(argname="argument min_ttl", value=min_ttl, expected_type=type_hints["min_ttl"])
            check_type(argname="argument mname", value=mname, expected_type=type_hints["mname"])
            check_type(argname="argument refresh", value=refresh, expected_type=type_hints["refresh"])
            check_type(argname="argument retry", value=retry, expected_type=type_hints["retry"])
            check_type(argname="argument rname", value=rname, expected_type=type_hints["rname"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "expire": expire,
            "min_ttl": min_ttl,
            "mname": mname,
            "refresh": refresh,
            "retry": retry,
            "rname": rname,
            "ttl": ttl,
        }

    @builtins.property
    def expire(self) -> jsii.Number:
        '''Time in seconds of being unable to query the primary server after which secondary servers should stop serving the zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#expire ZoneDnsSettings#expire}
        '''
        result = self._values.get("expire")
        assert result is not None, "Required property 'expire' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_ttl(self) -> jsii.Number:
        '''The time to live (TTL) for negative caching of records within the zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#min_ttl ZoneDnsSettings#min_ttl}
        '''
        result = self._values.get("min_ttl")
        assert result is not None, "Required property 'min_ttl' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def mname(self) -> builtins.str:
        '''The primary nameserver, which may be used for outbound zone transfers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#mname ZoneDnsSettings#mname}
        '''
        result = self._values.get("mname")
        assert result is not None, "Required property 'mname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def refresh(self) -> jsii.Number:
        '''Time in seconds after which secondary servers should re-check the SOA record to see if the zone has been updated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#refresh ZoneDnsSettings#refresh}
        '''
        result = self._values.get("refresh")
        assert result is not None, "Required property 'refresh' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retry(self) -> jsii.Number:
        '''Time in seconds after which secondary servers should retry queries after the primary server was unresponsive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#retry ZoneDnsSettings#retry}
        '''
        result = self._values.get("retry")
        assert result is not None, "Required property 'retry' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def rname(self) -> builtins.str:
        '''The email address of the zone administrator, with the first label representing the local part of the email address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#rname ZoneDnsSettings#rname}
        '''
        result = self._values.get("rname")
        assert result is not None, "Required property 'rname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ttl(self) -> jsii.Number:
        '''The time to live (TTL) of the SOA record itself.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_dns_settings#ttl ZoneDnsSettings#ttl}
        '''
        result = self._values.get("ttl")
        assert result is not None, "Required property 'ttl' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneDnsSettingsSoa(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZoneDnsSettingsSoaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zoneDnsSettings.ZoneDnsSettingsSoaOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30ff8bb066076f66a8f8392e8d7ec7301d8d762df1d118c9ff20c033000fc295)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="expireInput")
    def expire_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "expireInput"))

    @builtins.property
    @jsii.member(jsii_name="minTtlInput")
    def min_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="mnameInput")
    def mname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mnameInput"))

    @builtins.property
    @jsii.member(jsii_name="refreshInput")
    def refresh_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "refreshInput"))

    @builtins.property
    @jsii.member(jsii_name="retryInput")
    def retry_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryInput"))

    @builtins.property
    @jsii.member(jsii_name="rnameInput")
    def rname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rnameInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="expire")
    def expire(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expire"))

    @expire.setter
    def expire(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4c7e4d9d99fd551813307ec3d13a6f5710b38a1ba316c9fb47c24b352812801)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expire", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minTtl")
    def min_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minTtl"))

    @min_ttl.setter
    def min_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94e83fd40039c232f61b3c2a3c95fe44cb2409febf51dfbb049ef39ff7d6c312)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mname")
    def mname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mname"))

    @mname.setter
    def mname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a69e12c280640ef46ec1d8e2d8abac46165329f26a6a538996cbc8dfa884c1f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="refresh")
    def refresh(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refresh"))

    @refresh.setter
    def refresh(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6066381d4a91575a7dd298713d97601cb1c13f237612ff8d8bde6afc8c17d403)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refresh", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retry")
    def retry(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retry"))

    @retry.setter
    def retry(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d495487848d137f98554dddc7637b0816eab7a179303c9a062f8560582b31c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retry", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rname")
    def rname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rname"))

    @rname.setter
    def rname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa92bf97e9c78b70c3284fff021299f720526b4e1fa8391a9769b43e86137146)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ce94f7691b94419bbc9ffe4313298283270bc866997de2cf2fa521540b8c759)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsSoa]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsSoa]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsSoa]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfa12c352485e8a27590acd5953ecea295ec1f2304216fc873ea1b91a984b6b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZoneDnsSettings",
    "ZoneDnsSettingsConfig",
    "ZoneDnsSettingsInternalDns",
    "ZoneDnsSettingsInternalDnsOutputReference",
    "ZoneDnsSettingsNameservers",
    "ZoneDnsSettingsNameserversOutputReference",
    "ZoneDnsSettingsSoa",
    "ZoneDnsSettingsSoaOutputReference",
]

publication.publish()

def _typecheckingstub__72a7a45a39f58c58d3d0837cf0a7bcd2c149cfa6b12a96d07d6261ddb1167597(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    zone_id: builtins.str,
    flatten_all_cnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    foundation_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    internal_dns: typing.Optional[typing.Union[ZoneDnsSettingsInternalDns, typing.Dict[builtins.str, typing.Any]]] = None,
    multi_provider: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    nameservers: typing.Optional[typing.Union[ZoneDnsSettingsNameservers, typing.Dict[builtins.str, typing.Any]]] = None,
    ns_ttl: typing.Optional[jsii.Number] = None,
    secondary_overrides: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    soa: typing.Optional[typing.Union[ZoneDnsSettingsSoa, typing.Dict[builtins.str, typing.Any]]] = None,
    zone_mode: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__1b66a99a55215df0712c09fb32f8cc497504c1c2d537a7e6b1b0a35dfa046f8f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f03ef6c9efac768f3b1301a4671659158774a61e44fd9a136899122f6c9da5fd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06d0aa118d26f6e6356ed42398d964940a771fe3889a2d5592f1120fdbcad8b0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac4ba0ceff9467ffbe8b34bfc462e9c2322e1f0c2c244bac734649b72362f85d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09e5aeddf8b5e604ddd98f0304a8f67b5dced04206c7ec1a3c2a36d0be36c5ef(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36c161bf11d611dac5e398d3aa9af12203d7647ac4a386333e494fbdcd202aba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c28337c383567a613e847d0d12ce5fe982bb6d38dffeb07cdaee9e4c66cb79fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eec87ccd3e8d9870f4d94e317e56eaa7a6cf3386160fc0960d5db8c2da29b2b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__424068064902f5580baacd61a8713f8c7ccf6acac68330eeadef57a98733d726(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: builtins.str,
    flatten_all_cnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    foundation_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    internal_dns: typing.Optional[typing.Union[ZoneDnsSettingsInternalDns, typing.Dict[builtins.str, typing.Any]]] = None,
    multi_provider: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    nameservers: typing.Optional[typing.Union[ZoneDnsSettingsNameservers, typing.Dict[builtins.str, typing.Any]]] = None,
    ns_ttl: typing.Optional[jsii.Number] = None,
    secondary_overrides: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    soa: typing.Optional[typing.Union[ZoneDnsSettingsSoa, typing.Dict[builtins.str, typing.Any]]] = None,
    zone_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4023034533d6d44b4edc6cc43c083b0b519e8cfb4fd4befb36ca12d37f1a8dcd(
    *,
    reference_zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f62085d386d21b3c01d118102122ce231b728a69e6cc71ce9214f74bca4c7cdb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85d3af0c1bfbd4d9c5e6df1541ab35d6e2fbc0680c5efd841015df9d99d34e18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__213a5c9234d4b93477b1cd728b90f5c6374164099569bcfa291c9333c37958a7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsInternalDns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fb750f788063a0a62700801b56b46f91514200834f26d6a8e8f209afacae010(
    *,
    type: builtins.str,
    ns_set: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a1ac9785507195ba6c6d007cad68b58bc31662fe7f5d71d66f38616af07b1a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22a190277d724da7e8333af48ead01a437a9cf0fb0807d8b402c408b5a633d4a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6c86fc5648589929693b57b3ce2d2df43981a999522248fdaf7f2671f41e24a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de4cce3dabba9d052b3f6db12a3ee637fac7394d64ffef529f171f27445dec62(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsNameservers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__227bd8c1eb420c3e6fcba79b5c2358219f1301cc6f520f59d52e793a83ef489c(
    *,
    expire: jsii.Number,
    min_ttl: jsii.Number,
    mname: builtins.str,
    refresh: jsii.Number,
    retry: jsii.Number,
    rname: builtins.str,
    ttl: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30ff8bb066076f66a8f8392e8d7ec7301d8d762df1d118c9ff20c033000fc295(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4c7e4d9d99fd551813307ec3d13a6f5710b38a1ba316c9fb47c24b352812801(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94e83fd40039c232f61b3c2a3c95fe44cb2409febf51dfbb049ef39ff7d6c312(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a69e12c280640ef46ec1d8e2d8abac46165329f26a6a538996cbc8dfa884c1f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6066381d4a91575a7dd298713d97601cb1c13f237612ff8d8bde6afc8c17d403(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d495487848d137f98554dddc7637b0816eab7a179303c9a062f8560582b31c1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa92bf97e9c78b70c3284fff021299f720526b4e1fa8391a9769b43e86137146(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ce94f7691b94419bbc9ffe4313298283270bc866997de2cf2fa521540b8c759(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfa12c352485e8a27590acd5953ecea295ec1f2304216fc873ea1b91a984b6b8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneDnsSettingsSoa]],
) -> None:
    """Type checking stubs"""
    pass
