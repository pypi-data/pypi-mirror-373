r'''
# `cloudflare_account_dns_settings`

Refer to the Terraform Registry for docs: [`cloudflare_account_dns_settings`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings).
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


class AccountDnsSettings(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettings",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings cloudflare_account_dns_settings}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        zone_defaults: typing.Optional[typing.Union["AccountDnsSettingsZoneDefaults", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings cloudflare_account_dns_settings} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#account_id AccountDnsSettings#account_id}
        :param zone_defaults: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#zone_defaults AccountDnsSettings#zone_defaults}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef6b91dd0eb503f71575e903bc4b087fd1a973d998c2d73eee5930dfcd00e957)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = AccountDnsSettingsConfig(
            account_id=account_id,
            zone_defaults=zone_defaults,
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
        '''Generates CDKTF code for importing a AccountDnsSettings resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AccountDnsSettings to import.
        :param import_from_id: The id of the existing AccountDnsSettings that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AccountDnsSettings to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48504cec189cac40d1397698c4e7289f92e727ab1e7660b6d4be6be9a2183763)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putZoneDefaults")
    def put_zone_defaults(
        self,
        *,
        flatten_all_cnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        foundation_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        internal_dns: typing.Optional[typing.Union["AccountDnsSettingsZoneDefaultsInternalDns", typing.Dict[builtins.str, typing.Any]]] = None,
        multi_provider: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        nameservers: typing.Optional[typing.Union["AccountDnsSettingsZoneDefaultsNameservers", typing.Dict[builtins.str, typing.Any]]] = None,
        ns_ttl: typing.Optional[jsii.Number] = None,
        secondary_overrides: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        soa: typing.Optional[typing.Union["AccountDnsSettingsZoneDefaultsSoa", typing.Dict[builtins.str, typing.Any]]] = None,
        zone_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param flatten_all_cnames: Whether to flatten all CNAME records in the zone. Note that, due to DNS limitations, a CNAME record at the zone apex will always be flattened. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#flatten_all_cnames AccountDnsSettings#flatten_all_cnames}
        :param foundation_dns: Whether to enable Foundation DNS Advanced Nameservers on the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#foundation_dns AccountDnsSettings#foundation_dns}
        :param internal_dns: Settings for this internal zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#internal_dns AccountDnsSettings#internal_dns}
        :param multi_provider: Whether to enable multi-provider DNS, which causes Cloudflare to activate the zone even when non-Cloudflare NS records exist, and to respect NS records at the zone apex during outbound zone transfers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#multi_provider AccountDnsSettings#multi_provider}
        :param nameservers: Settings determining the nameservers through which the zone should be available. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#nameservers AccountDnsSettings#nameservers}
        :param ns_ttl: The time to live (TTL) of the zone's nameserver (NS) records. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#ns_ttl AccountDnsSettings#ns_ttl}
        :param secondary_overrides: Allows a Secondary DNS zone to use (proxied) override records and CNAME flattening at the zone apex. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#secondary_overrides AccountDnsSettings#secondary_overrides}
        :param soa: Components of the zone's SOA record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#soa AccountDnsSettings#soa}
        :param zone_mode: Whether the zone mode is a regular or CDN/DNS only zone. Available values: "standard", "cdn_only", "dns_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#zone_mode AccountDnsSettings#zone_mode}
        '''
        value = AccountDnsSettingsZoneDefaults(
            flatten_all_cnames=flatten_all_cnames,
            foundation_dns=foundation_dns,
            internal_dns=internal_dns,
            multi_provider=multi_provider,
            nameservers=nameservers,
            ns_ttl=ns_ttl,
            secondary_overrides=secondary_overrides,
            soa=soa,
            zone_mode=zone_mode,
        )

        return typing.cast(None, jsii.invoke(self, "putZoneDefaults", [value]))

    @jsii.member(jsii_name="resetZoneDefaults")
    def reset_zone_defaults(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneDefaults", []))

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
    @jsii.member(jsii_name="zoneDefaults")
    def zone_defaults(self) -> "AccountDnsSettingsZoneDefaultsOutputReference":
        return typing.cast("AccountDnsSettingsZoneDefaultsOutputReference", jsii.get(self, "zoneDefaults"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneDefaultsInput")
    def zone_defaults_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountDnsSettingsZoneDefaults"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountDnsSettingsZoneDefaults"]], jsii.get(self, "zoneDefaultsInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bb2cec70a5d8006002e4a0f3ad86b96e288784abaae9bf00e0b3edd552fe910)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettingsConfig",
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
        "zone_defaults": "zoneDefaults",
    },
)
class AccountDnsSettingsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        zone_defaults: typing.Optional[typing.Union["AccountDnsSettingsZoneDefaults", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#account_id AccountDnsSettings#account_id}
        :param zone_defaults: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#zone_defaults AccountDnsSettings#zone_defaults}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(zone_defaults, dict):
            zone_defaults = AccountDnsSettingsZoneDefaults(**zone_defaults)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cd98b184f51c0a28ea0af67bd0d759c7dcea5793757601f2bfb6f21336ae43b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument zone_defaults", value=zone_defaults, expected_type=type_hints["zone_defaults"])
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
        if zone_defaults is not None:
            self._values["zone_defaults"] = zone_defaults

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#account_id AccountDnsSettings#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone_defaults(self) -> typing.Optional["AccountDnsSettingsZoneDefaults"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#zone_defaults AccountDnsSettings#zone_defaults}.'''
        result = self._values.get("zone_defaults")
        return typing.cast(typing.Optional["AccountDnsSettingsZoneDefaults"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountDnsSettingsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettingsZoneDefaults",
    jsii_struct_bases=[],
    name_mapping={
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
class AccountDnsSettingsZoneDefaults:
    def __init__(
        self,
        *,
        flatten_all_cnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        foundation_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        internal_dns: typing.Optional[typing.Union["AccountDnsSettingsZoneDefaultsInternalDns", typing.Dict[builtins.str, typing.Any]]] = None,
        multi_provider: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        nameservers: typing.Optional[typing.Union["AccountDnsSettingsZoneDefaultsNameservers", typing.Dict[builtins.str, typing.Any]]] = None,
        ns_ttl: typing.Optional[jsii.Number] = None,
        secondary_overrides: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        soa: typing.Optional[typing.Union["AccountDnsSettingsZoneDefaultsSoa", typing.Dict[builtins.str, typing.Any]]] = None,
        zone_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param flatten_all_cnames: Whether to flatten all CNAME records in the zone. Note that, due to DNS limitations, a CNAME record at the zone apex will always be flattened. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#flatten_all_cnames AccountDnsSettings#flatten_all_cnames}
        :param foundation_dns: Whether to enable Foundation DNS Advanced Nameservers on the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#foundation_dns AccountDnsSettings#foundation_dns}
        :param internal_dns: Settings for this internal zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#internal_dns AccountDnsSettings#internal_dns}
        :param multi_provider: Whether to enable multi-provider DNS, which causes Cloudflare to activate the zone even when non-Cloudflare NS records exist, and to respect NS records at the zone apex during outbound zone transfers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#multi_provider AccountDnsSettings#multi_provider}
        :param nameservers: Settings determining the nameservers through which the zone should be available. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#nameservers AccountDnsSettings#nameservers}
        :param ns_ttl: The time to live (TTL) of the zone's nameserver (NS) records. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#ns_ttl AccountDnsSettings#ns_ttl}
        :param secondary_overrides: Allows a Secondary DNS zone to use (proxied) override records and CNAME flattening at the zone apex. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#secondary_overrides AccountDnsSettings#secondary_overrides}
        :param soa: Components of the zone's SOA record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#soa AccountDnsSettings#soa}
        :param zone_mode: Whether the zone mode is a regular or CDN/DNS only zone. Available values: "standard", "cdn_only", "dns_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#zone_mode AccountDnsSettings#zone_mode}
        '''
        if isinstance(internal_dns, dict):
            internal_dns = AccountDnsSettingsZoneDefaultsInternalDns(**internal_dns)
        if isinstance(nameservers, dict):
            nameservers = AccountDnsSettingsZoneDefaultsNameservers(**nameservers)
        if isinstance(soa, dict):
            soa = AccountDnsSettingsZoneDefaultsSoa(**soa)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c0cf6942b77d65bb4dfd5641093280e8d2655bd225940995e0a3164db21290c)
            check_type(argname="argument flatten_all_cnames", value=flatten_all_cnames, expected_type=type_hints["flatten_all_cnames"])
            check_type(argname="argument foundation_dns", value=foundation_dns, expected_type=type_hints["foundation_dns"])
            check_type(argname="argument internal_dns", value=internal_dns, expected_type=type_hints["internal_dns"])
            check_type(argname="argument multi_provider", value=multi_provider, expected_type=type_hints["multi_provider"])
            check_type(argname="argument nameservers", value=nameservers, expected_type=type_hints["nameservers"])
            check_type(argname="argument ns_ttl", value=ns_ttl, expected_type=type_hints["ns_ttl"])
            check_type(argname="argument secondary_overrides", value=secondary_overrides, expected_type=type_hints["secondary_overrides"])
            check_type(argname="argument soa", value=soa, expected_type=type_hints["soa"])
            check_type(argname="argument zone_mode", value=zone_mode, expected_type=type_hints["zone_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
    def flatten_all_cnames(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to flatten all CNAME records in the zone.

        Note that, due to DNS limitations, a CNAME record at the zone apex will always be flattened.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#flatten_all_cnames AccountDnsSettings#flatten_all_cnames}
        '''
        result = self._values.get("flatten_all_cnames")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def foundation_dns(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to enable Foundation DNS Advanced Nameservers on the zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#foundation_dns AccountDnsSettings#foundation_dns}
        '''
        result = self._values.get("foundation_dns")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def internal_dns(
        self,
    ) -> typing.Optional["AccountDnsSettingsZoneDefaultsInternalDns"]:
        '''Settings for this internal zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#internal_dns AccountDnsSettings#internal_dns}
        '''
        result = self._values.get("internal_dns")
        return typing.cast(typing.Optional["AccountDnsSettingsZoneDefaultsInternalDns"], result)

    @builtins.property
    def multi_provider(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to enable multi-provider DNS, which causes Cloudflare to activate the zone even when non-Cloudflare NS records exist, and to respect NS records at the zone apex during outbound zone transfers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#multi_provider AccountDnsSettings#multi_provider}
        '''
        result = self._values.get("multi_provider")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def nameservers(
        self,
    ) -> typing.Optional["AccountDnsSettingsZoneDefaultsNameservers"]:
        '''Settings determining the nameservers through which the zone should be available.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#nameservers AccountDnsSettings#nameservers}
        '''
        result = self._values.get("nameservers")
        return typing.cast(typing.Optional["AccountDnsSettingsZoneDefaultsNameservers"], result)

    @builtins.property
    def ns_ttl(self) -> typing.Optional[jsii.Number]:
        '''The time to live (TTL) of the zone's nameserver (NS) records.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#ns_ttl AccountDnsSettings#ns_ttl}
        '''
        result = self._values.get("ns_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def secondary_overrides(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allows a Secondary DNS zone to use (proxied) override records and CNAME flattening at the zone apex.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#secondary_overrides AccountDnsSettings#secondary_overrides}
        '''
        result = self._values.get("secondary_overrides")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def soa(self) -> typing.Optional["AccountDnsSettingsZoneDefaultsSoa"]:
        '''Components of the zone's SOA record.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#soa AccountDnsSettings#soa}
        '''
        result = self._values.get("soa")
        return typing.cast(typing.Optional["AccountDnsSettingsZoneDefaultsSoa"], result)

    @builtins.property
    def zone_mode(self) -> typing.Optional[builtins.str]:
        '''Whether the zone mode is a regular or CDN/DNS only zone. Available values: "standard", "cdn_only", "dns_only".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#zone_mode AccountDnsSettings#zone_mode}
        '''
        result = self._values.get("zone_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountDnsSettingsZoneDefaults(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettingsZoneDefaultsInternalDns",
    jsii_struct_bases=[],
    name_mapping={"reference_zone_id": "referenceZoneId"},
)
class AccountDnsSettingsZoneDefaultsInternalDns:
    def __init__(
        self,
        *,
        reference_zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param reference_zone_id: The ID of the zone to fallback to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#reference_zone_id AccountDnsSettings#reference_zone_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3e5eff9e1eef40e12777e0d33f3b15289d22beb48b53221269102923da47e47)
            check_type(argname="argument reference_zone_id", value=reference_zone_id, expected_type=type_hints["reference_zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if reference_zone_id is not None:
            self._values["reference_zone_id"] = reference_zone_id

    @builtins.property
    def reference_zone_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the zone to fallback to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#reference_zone_id AccountDnsSettings#reference_zone_id}
        '''
        result = self._values.get("reference_zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountDnsSettingsZoneDefaultsInternalDns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountDnsSettingsZoneDefaultsInternalDnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettingsZoneDefaultsInternalDnsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c10c284aeae98d65b7f2550614c73cad9203229577997cfd581c1c947b7f6185)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e91845cba8e31a03273179c0dac385badd0b45a7ec27e1014cb78b01955ba500)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "referenceZoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsInternalDns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsInternalDns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsInternalDns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19d4518ed7a08746ca2847acac2729bffb1131c3538a2a610345544188f42489)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettingsZoneDefaultsNameservers",
    jsii_struct_bases=[],
    name_mapping={"type": "type"},
)
class AccountDnsSettingsZoneDefaultsNameservers:
    def __init__(self, *, type: builtins.str) -> None:
        '''
        :param type: Nameserver type Available values: "cloudflare.standard", "cloudflare.standard.random", "custom.account", "custom.tenant". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#type AccountDnsSettings#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__833623b7293bc2869378661f37761288607e12e081298a5c9539a321ff1c765e)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }

    @builtins.property
    def type(self) -> builtins.str:
        '''Nameserver type Available values: "cloudflare.standard", "cloudflare.standard.random", "custom.account", "custom.tenant".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#type AccountDnsSettings#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountDnsSettingsZoneDefaultsNameservers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountDnsSettingsZoneDefaultsNameserversOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettingsZoneDefaultsNameserversOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b852340e72d57e991bf9d63b182820b08b8aed264e9703c7d11394f664b971a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c65fc24e8cddfb274b61109f919d842a5dabd189628102f92171369064f484d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsNameservers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsNameservers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsNameservers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08533a427982d3d70de943832e4934948a3b67563360e2d7314d4dc895062d03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AccountDnsSettingsZoneDefaultsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettingsZoneDefaultsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f37f8069d51f2fc0168c3c04fd8a0667694a0d9211abc3deef3a70e58565c05)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putInternalDns")
    def put_internal_dns(
        self,
        *,
        reference_zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param reference_zone_id: The ID of the zone to fallback to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#reference_zone_id AccountDnsSettings#reference_zone_id}
        '''
        value = AccountDnsSettingsZoneDefaultsInternalDns(
            reference_zone_id=reference_zone_id
        )

        return typing.cast(None, jsii.invoke(self, "putInternalDns", [value]))

    @jsii.member(jsii_name="putNameservers")
    def put_nameservers(self, *, type: builtins.str) -> None:
        '''
        :param type: Nameserver type Available values: "cloudflare.standard", "cloudflare.standard.random", "custom.account", "custom.tenant". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#type AccountDnsSettings#type}
        '''
        value = AccountDnsSettingsZoneDefaultsNameservers(type=type)

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
        :param expire: Time in seconds of being unable to query the primary server after which secondary servers should stop serving the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#expire AccountDnsSettings#expire}
        :param min_ttl: The time to live (TTL) for negative caching of records within the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#min_ttl AccountDnsSettings#min_ttl}
        :param mname: The primary nameserver, which may be used for outbound zone transfers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#mname AccountDnsSettings#mname}
        :param refresh: Time in seconds after which secondary servers should re-check the SOA record to see if the zone has been updated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#refresh AccountDnsSettings#refresh}
        :param retry: Time in seconds after which secondary servers should retry queries after the primary server was unresponsive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#retry AccountDnsSettings#retry}
        :param rname: The email address of the zone administrator, with the first label representing the local part of the email address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#rname AccountDnsSettings#rname}
        :param ttl: The time to live (TTL) of the SOA record itself. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#ttl AccountDnsSettings#ttl}
        '''
        value = AccountDnsSettingsZoneDefaultsSoa(
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

    @builtins.property
    @jsii.member(jsii_name="internalDns")
    def internal_dns(self) -> AccountDnsSettingsZoneDefaultsInternalDnsOutputReference:
        return typing.cast(AccountDnsSettingsZoneDefaultsInternalDnsOutputReference, jsii.get(self, "internalDns"))

    @builtins.property
    @jsii.member(jsii_name="nameservers")
    def nameservers(self) -> AccountDnsSettingsZoneDefaultsNameserversOutputReference:
        return typing.cast(AccountDnsSettingsZoneDefaultsNameserversOutputReference, jsii.get(self, "nameservers"))

    @builtins.property
    @jsii.member(jsii_name="soa")
    def soa(self) -> "AccountDnsSettingsZoneDefaultsSoaOutputReference":
        return typing.cast("AccountDnsSettingsZoneDefaultsSoaOutputReference", jsii.get(self, "soa"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsInternalDns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsInternalDns]], jsii.get(self, "internalDnsInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsNameservers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsNameservers]], jsii.get(self, "nameserversInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountDnsSettingsZoneDefaultsSoa"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountDnsSettingsZoneDefaultsSoa"]], jsii.get(self, "soaInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__2185b3fa8b838a477749a2cd10ea54f642e97d1e26fc295faeda51779d9e5a8a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b9672f776de6a80c30b71cb68b3a94998052eb29849e43ff8f9c80f08444da51)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3051487dad3595a9f94813c9118279289334ac429be5bf0ccda1ddf2194f6a90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "multiProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nsTtl")
    def ns_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nsTtl"))

    @ns_ttl.setter
    def ns_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83795418f6c31eaa1c3ce1eada21f19dd561d3baf18b3b6b96c0ec766b39cb99)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5173733380beb261a261926a40379cff5ef4ad846b4aebc54a6fe49f71345bd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryOverrides", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneMode")
    def zone_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneMode"))

    @zone_mode.setter
    def zone_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2fe00ed193bb60de2048e7a961599302a730f516f38768af870a0b3ad45d81e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaults]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaults]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaults]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63436c247c3479c3288c4b0205364bb00a2f810e95b52ad6ee292a26d100d795)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettingsZoneDefaultsSoa",
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
class AccountDnsSettingsZoneDefaultsSoa:
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
        :param expire: Time in seconds of being unable to query the primary server after which secondary servers should stop serving the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#expire AccountDnsSettings#expire}
        :param min_ttl: The time to live (TTL) for negative caching of records within the zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#min_ttl AccountDnsSettings#min_ttl}
        :param mname: The primary nameserver, which may be used for outbound zone transfers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#mname AccountDnsSettings#mname}
        :param refresh: Time in seconds after which secondary servers should re-check the SOA record to see if the zone has been updated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#refresh AccountDnsSettings#refresh}
        :param retry: Time in seconds after which secondary servers should retry queries after the primary server was unresponsive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#retry AccountDnsSettings#retry}
        :param rname: The email address of the zone administrator, with the first label representing the local part of the email address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#rname AccountDnsSettings#rname}
        :param ttl: The time to live (TTL) of the SOA record itself. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#ttl AccountDnsSettings#ttl}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__645afd69f9c9d1d58afbaefea63878c278d57557f2bd3df126e36ca928ba601e)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#expire AccountDnsSettings#expire}
        '''
        result = self._values.get("expire")
        assert result is not None, "Required property 'expire' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_ttl(self) -> jsii.Number:
        '''The time to live (TTL) for negative caching of records within the zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#min_ttl AccountDnsSettings#min_ttl}
        '''
        result = self._values.get("min_ttl")
        assert result is not None, "Required property 'min_ttl' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def mname(self) -> builtins.str:
        '''The primary nameserver, which may be used for outbound zone transfers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#mname AccountDnsSettings#mname}
        '''
        result = self._values.get("mname")
        assert result is not None, "Required property 'mname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def refresh(self) -> jsii.Number:
        '''Time in seconds after which secondary servers should re-check the SOA record to see if the zone has been updated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#refresh AccountDnsSettings#refresh}
        '''
        result = self._values.get("refresh")
        assert result is not None, "Required property 'refresh' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retry(self) -> jsii.Number:
        '''Time in seconds after which secondary servers should retry queries after the primary server was unresponsive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#retry AccountDnsSettings#retry}
        '''
        result = self._values.get("retry")
        assert result is not None, "Required property 'retry' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def rname(self) -> builtins.str:
        '''The email address of the zone administrator, with the first label representing the local part of the email address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#rname AccountDnsSettings#rname}
        '''
        result = self._values.get("rname")
        assert result is not None, "Required property 'rname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ttl(self) -> jsii.Number:
        '''The time to live (TTL) of the SOA record itself.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/account_dns_settings#ttl AccountDnsSettings#ttl}
        '''
        result = self._values.get("ttl")
        assert result is not None, "Required property 'ttl' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountDnsSettingsZoneDefaultsSoa(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountDnsSettingsZoneDefaultsSoaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accountDnsSettings.AccountDnsSettingsZoneDefaultsSoaOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9f37906c0f95483fb0c57d0aedcd4c3eaa699c7ceb0bfeea01308bece98493c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7dc6b156a29326f2cd4def404550b4629ec3cf6fe0562e99bef66596e88b3b2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expire", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minTtl")
    def min_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minTtl"))

    @min_ttl.setter
    def min_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4530e4b5a8f5b4539f259dd9fb6ab3463f4434f4f48b561a902d40fc6ff68fc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mname")
    def mname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mname"))

    @mname.setter
    def mname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3d6e96240fb656c6c3e235ec6deb9d13bb4e5dd724a021a0c0516c3437c2f59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="refresh")
    def refresh(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refresh"))

    @refresh.setter
    def refresh(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98962826a5a2e8b20962a3356ac0b96da70101fefbc345765511f8985f93b66f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refresh", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retry")
    def retry(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retry"))

    @retry.setter
    def retry(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68cf7edddbfc9da4ba6c2e77fe0a07cf210946325e54f19dbf2b6ef2da2a6cc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retry", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rname")
    def rname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rname"))

    @rname.setter
    def rname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b076231a2f8e3f82f6941fffac2f6da58cced891047355aa65253a1c12b4cdea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__231dc9f0703886f93a81eae5c2091711b922fc5da96c9c2999bd6478b086a5e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsSoa]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsSoa]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsSoa]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b6fa72719649aa70b38951dfac3d79a111eb8af281f712c91318ad5fa80c99b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AccountDnsSettings",
    "AccountDnsSettingsConfig",
    "AccountDnsSettingsZoneDefaults",
    "AccountDnsSettingsZoneDefaultsInternalDns",
    "AccountDnsSettingsZoneDefaultsInternalDnsOutputReference",
    "AccountDnsSettingsZoneDefaultsNameservers",
    "AccountDnsSettingsZoneDefaultsNameserversOutputReference",
    "AccountDnsSettingsZoneDefaultsOutputReference",
    "AccountDnsSettingsZoneDefaultsSoa",
    "AccountDnsSettingsZoneDefaultsSoaOutputReference",
]

publication.publish()

def _typecheckingstub__ef6b91dd0eb503f71575e903bc4b087fd1a973d998c2d73eee5930dfcd00e957(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    zone_defaults: typing.Optional[typing.Union[AccountDnsSettingsZoneDefaults, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__48504cec189cac40d1397698c4e7289f92e727ab1e7660b6d4be6be9a2183763(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bb2cec70a5d8006002e4a0f3ad86b96e288784abaae9bf00e0b3edd552fe910(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cd98b184f51c0a28ea0af67bd0d759c7dcea5793757601f2bfb6f21336ae43b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    zone_defaults: typing.Optional[typing.Union[AccountDnsSettingsZoneDefaults, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c0cf6942b77d65bb4dfd5641093280e8d2655bd225940995e0a3164db21290c(
    *,
    flatten_all_cnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    foundation_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    internal_dns: typing.Optional[typing.Union[AccountDnsSettingsZoneDefaultsInternalDns, typing.Dict[builtins.str, typing.Any]]] = None,
    multi_provider: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    nameservers: typing.Optional[typing.Union[AccountDnsSettingsZoneDefaultsNameservers, typing.Dict[builtins.str, typing.Any]]] = None,
    ns_ttl: typing.Optional[jsii.Number] = None,
    secondary_overrides: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    soa: typing.Optional[typing.Union[AccountDnsSettingsZoneDefaultsSoa, typing.Dict[builtins.str, typing.Any]]] = None,
    zone_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3e5eff9e1eef40e12777e0d33f3b15289d22beb48b53221269102923da47e47(
    *,
    reference_zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c10c284aeae98d65b7f2550614c73cad9203229577997cfd581c1c947b7f6185(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e91845cba8e31a03273179c0dac385badd0b45a7ec27e1014cb78b01955ba500(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19d4518ed7a08746ca2847acac2729bffb1131c3538a2a610345544188f42489(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsInternalDns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__833623b7293bc2869378661f37761288607e12e081298a5c9539a321ff1c765e(
    *,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b852340e72d57e991bf9d63b182820b08b8aed264e9703c7d11394f664b971a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c65fc24e8cddfb274b61109f919d842a5dabd189628102f92171369064f484d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08533a427982d3d70de943832e4934948a3b67563360e2d7314d4dc895062d03(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsNameservers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f37f8069d51f2fc0168c3c04fd8a0667694a0d9211abc3deef3a70e58565c05(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2185b3fa8b838a477749a2cd10ea54f642e97d1e26fc295faeda51779d9e5a8a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9672f776de6a80c30b71cb68b3a94998052eb29849e43ff8f9c80f08444da51(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3051487dad3595a9f94813c9118279289334ac429be5bf0ccda1ddf2194f6a90(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83795418f6c31eaa1c3ce1eada21f19dd561d3baf18b3b6b96c0ec766b39cb99(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5173733380beb261a261926a40379cff5ef4ad846b4aebc54a6fe49f71345bd2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2fe00ed193bb60de2048e7a961599302a730f516f38768af870a0b3ad45d81e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63436c247c3479c3288c4b0205364bb00a2f810e95b52ad6ee292a26d100d795(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaults]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__645afd69f9c9d1d58afbaefea63878c278d57557f2bd3df126e36ca928ba601e(
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

def _typecheckingstub__d9f37906c0f95483fb0c57d0aedcd4c3eaa699c7ceb0bfeea01308bece98493c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dc6b156a29326f2cd4def404550b4629ec3cf6fe0562e99bef66596e88b3b2e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4530e4b5a8f5b4539f259dd9fb6ab3463f4434f4f48b561a902d40fc6ff68fc7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3d6e96240fb656c6c3e235ec6deb9d13bb4e5dd724a021a0c0516c3437c2f59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98962826a5a2e8b20962a3356ac0b96da70101fefbc345765511f8985f93b66f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68cf7edddbfc9da4ba6c2e77fe0a07cf210946325e54f19dbf2b6ef2da2a6cc4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b076231a2f8e3f82f6941fffac2f6da58cced891047355aa65253a1c12b4cdea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__231dc9f0703886f93a81eae5c2091711b922fc5da96c9c2999bd6478b086a5e6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b6fa72719649aa70b38951dfac3d79a111eb8af281f712c91318ad5fa80c99b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountDnsSettingsZoneDefaultsSoa]],
) -> None:
    """Type checking stubs"""
    pass
