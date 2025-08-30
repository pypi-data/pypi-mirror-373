r'''
# `cloudflare_zero_trust_gateway_settings`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_gateway_settings`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings).
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


class ZeroTrustGatewaySettings(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettings",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings cloudflare_zero_trust_gateway_settings}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        settings: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings cloudflare_zero_trust_gateway_settings} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#account_id ZeroTrustGatewaySettings#account_id}.
        :param settings: Account settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#settings ZeroTrustGatewaySettings#settings}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e835aa6c5393b3bccb9f3757aa1cc8e34cee2d7a93e870dce8110f777030091f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustGatewaySettingsConfig(
            account_id=account_id,
            settings=settings,
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
        '''Generates CDKTF code for importing a ZeroTrustGatewaySettings resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustGatewaySettings to import.
        :param import_from_id: The id of the existing ZeroTrustGatewaySettings that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustGatewaySettings to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6a9c540ee48d79bc94bf225d2e7f3d25e0fad690ba5931d93c9793a03c42dc5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putSettings")
    def put_settings(
        self,
        *,
        activity_log: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsActivityLog", typing.Dict[builtins.str, typing.Any]]] = None,
        antivirus: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsAntivirus", typing.Dict[builtins.str, typing.Any]]] = None,
        block_page: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsBlockPage", typing.Dict[builtins.str, typing.Any]]] = None,
        body_scanning: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsBodyScanning", typing.Dict[builtins.str, typing.Any]]] = None,
        browser_isolation: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsBrowserIsolation", typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_certificate: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsCustomCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        extended_email_matching: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsExtendedEmailMatching", typing.Dict[builtins.str, typing.Any]]] = None,
        fips: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsFips", typing.Dict[builtins.str, typing.Any]]] = None,
        host_selector: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsHostSelector", typing.Dict[builtins.str, typing.Any]]] = None,
        inspection: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsInspection", typing.Dict[builtins.str, typing.Any]]] = None,
        protocol_detection: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsProtocolDetection", typing.Dict[builtins.str, typing.Any]]] = None,
        sandbox: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsSandbox", typing.Dict[builtins.str, typing.Any]]] = None,
        tls_decrypt: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsTlsDecrypt", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param activity_log: Activity log settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#activity_log ZeroTrustGatewaySettings#activity_log}
        :param antivirus: Anti-virus settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#antivirus ZeroTrustGatewaySettings#antivirus}
        :param block_page: Block page layout settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#block_page ZeroTrustGatewaySettings#block_page}
        :param body_scanning: DLP body scanning settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#body_scanning ZeroTrustGatewaySettings#body_scanning}
        :param browser_isolation: Browser isolation settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#browser_isolation ZeroTrustGatewaySettings#browser_isolation}
        :param certificate: Certificate settings for Gateway TLS interception. If not specified, the Cloudflare Root CA will be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#certificate ZeroTrustGatewaySettings#certificate}
        :param custom_certificate: Custom certificate settings for BYO-PKI. (deprecated and replaced by ``certificate``). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#custom_certificate ZeroTrustGatewaySettings#custom_certificate}
        :param extended_email_matching: Extended e-mail matching settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#extended_email_matching ZeroTrustGatewaySettings#extended_email_matching}
        :param fips: FIPS settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#fips ZeroTrustGatewaySettings#fips}
        :param host_selector: Setting to enable host selector in egress policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#host_selector ZeroTrustGatewaySettings#host_selector}
        :param inspection: Setting to define inspection settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#inspection ZeroTrustGatewaySettings#inspection}
        :param protocol_detection: Protocol Detection settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#protocol_detection ZeroTrustGatewaySettings#protocol_detection}
        :param sandbox: Sandbox settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#sandbox ZeroTrustGatewaySettings#sandbox}
        :param tls_decrypt: TLS interception settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#tls_decrypt ZeroTrustGatewaySettings#tls_decrypt}
        '''
        value = ZeroTrustGatewaySettingsSettings(
            activity_log=activity_log,
            antivirus=antivirus,
            block_page=block_page,
            body_scanning=body_scanning,
            browser_isolation=browser_isolation,
            certificate=certificate,
            custom_certificate=custom_certificate,
            extended_email_matching=extended_email_matching,
            fips=fips,
            host_selector=host_selector,
            inspection=inspection,
            protocol_detection=protocol_detection,
            sandbox=sandbox,
            tls_decrypt=tls_decrypt,
        )

        return typing.cast(None, jsii.invoke(self, "putSettings", [value]))

    @jsii.member(jsii_name="resetSettings")
    def reset_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSettings", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="settings")
    def settings(self) -> "ZeroTrustGatewaySettingsSettingsOutputReference":
        return typing.cast("ZeroTrustGatewaySettingsSettingsOutputReference", jsii.get(self, "settings"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="settingsInput")
    def settings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewaySettingsSettings"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewaySettingsSettings"]], jsii.get(self, "settingsInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5f323899588c0d92313196544d971a5ad585faf1ae29ee162ace9408ebbf9a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsConfig",
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
        "settings": "settings",
    },
)
class ZeroTrustGatewaySettingsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        settings: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettings", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#account_id ZeroTrustGatewaySettings#account_id}.
        :param settings: Account settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#settings ZeroTrustGatewaySettings#settings}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(settings, dict):
            settings = ZeroTrustGatewaySettingsSettings(**settings)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__322ff5308daf0c47711318ff672028d3699332013934aecc39310a2adc383991)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument settings", value=settings, expected_type=type_hints["settings"])
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
        if settings is not None:
            self._values["settings"] = settings

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#account_id ZeroTrustGatewaySettings#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def settings(self) -> typing.Optional["ZeroTrustGatewaySettingsSettings"]:
        '''Account settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#settings ZeroTrustGatewaySettings#settings}
        '''
        result = self._values.get("settings")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettings"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettings",
    jsii_struct_bases=[],
    name_mapping={
        "activity_log": "activityLog",
        "antivirus": "antivirus",
        "block_page": "blockPage",
        "body_scanning": "bodyScanning",
        "browser_isolation": "browserIsolation",
        "certificate": "certificate",
        "custom_certificate": "customCertificate",
        "extended_email_matching": "extendedEmailMatching",
        "fips": "fips",
        "host_selector": "hostSelector",
        "inspection": "inspection",
        "protocol_detection": "protocolDetection",
        "sandbox": "sandbox",
        "tls_decrypt": "tlsDecrypt",
    },
)
class ZeroTrustGatewaySettingsSettings:
    def __init__(
        self,
        *,
        activity_log: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsActivityLog", typing.Dict[builtins.str, typing.Any]]] = None,
        antivirus: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsAntivirus", typing.Dict[builtins.str, typing.Any]]] = None,
        block_page: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsBlockPage", typing.Dict[builtins.str, typing.Any]]] = None,
        body_scanning: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsBodyScanning", typing.Dict[builtins.str, typing.Any]]] = None,
        browser_isolation: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsBrowserIsolation", typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_certificate: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsCustomCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        extended_email_matching: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsExtendedEmailMatching", typing.Dict[builtins.str, typing.Any]]] = None,
        fips: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsFips", typing.Dict[builtins.str, typing.Any]]] = None,
        host_selector: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsHostSelector", typing.Dict[builtins.str, typing.Any]]] = None,
        inspection: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsInspection", typing.Dict[builtins.str, typing.Any]]] = None,
        protocol_detection: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsProtocolDetection", typing.Dict[builtins.str, typing.Any]]] = None,
        sandbox: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsSandbox", typing.Dict[builtins.str, typing.Any]]] = None,
        tls_decrypt: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsTlsDecrypt", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param activity_log: Activity log settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#activity_log ZeroTrustGatewaySettings#activity_log}
        :param antivirus: Anti-virus settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#antivirus ZeroTrustGatewaySettings#antivirus}
        :param block_page: Block page layout settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#block_page ZeroTrustGatewaySettings#block_page}
        :param body_scanning: DLP body scanning settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#body_scanning ZeroTrustGatewaySettings#body_scanning}
        :param browser_isolation: Browser isolation settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#browser_isolation ZeroTrustGatewaySettings#browser_isolation}
        :param certificate: Certificate settings for Gateway TLS interception. If not specified, the Cloudflare Root CA will be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#certificate ZeroTrustGatewaySettings#certificate}
        :param custom_certificate: Custom certificate settings for BYO-PKI. (deprecated and replaced by ``certificate``). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#custom_certificate ZeroTrustGatewaySettings#custom_certificate}
        :param extended_email_matching: Extended e-mail matching settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#extended_email_matching ZeroTrustGatewaySettings#extended_email_matching}
        :param fips: FIPS settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#fips ZeroTrustGatewaySettings#fips}
        :param host_selector: Setting to enable host selector in egress policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#host_selector ZeroTrustGatewaySettings#host_selector}
        :param inspection: Setting to define inspection settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#inspection ZeroTrustGatewaySettings#inspection}
        :param protocol_detection: Protocol Detection settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#protocol_detection ZeroTrustGatewaySettings#protocol_detection}
        :param sandbox: Sandbox settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#sandbox ZeroTrustGatewaySettings#sandbox}
        :param tls_decrypt: TLS interception settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#tls_decrypt ZeroTrustGatewaySettings#tls_decrypt}
        '''
        if isinstance(activity_log, dict):
            activity_log = ZeroTrustGatewaySettingsSettingsActivityLog(**activity_log)
        if isinstance(antivirus, dict):
            antivirus = ZeroTrustGatewaySettingsSettingsAntivirus(**antivirus)
        if isinstance(block_page, dict):
            block_page = ZeroTrustGatewaySettingsSettingsBlockPage(**block_page)
        if isinstance(body_scanning, dict):
            body_scanning = ZeroTrustGatewaySettingsSettingsBodyScanning(**body_scanning)
        if isinstance(browser_isolation, dict):
            browser_isolation = ZeroTrustGatewaySettingsSettingsBrowserIsolation(**browser_isolation)
        if isinstance(certificate, dict):
            certificate = ZeroTrustGatewaySettingsSettingsCertificate(**certificate)
        if isinstance(custom_certificate, dict):
            custom_certificate = ZeroTrustGatewaySettingsSettingsCustomCertificate(**custom_certificate)
        if isinstance(extended_email_matching, dict):
            extended_email_matching = ZeroTrustGatewaySettingsSettingsExtendedEmailMatching(**extended_email_matching)
        if isinstance(fips, dict):
            fips = ZeroTrustGatewaySettingsSettingsFips(**fips)
        if isinstance(host_selector, dict):
            host_selector = ZeroTrustGatewaySettingsSettingsHostSelector(**host_selector)
        if isinstance(inspection, dict):
            inspection = ZeroTrustGatewaySettingsSettingsInspection(**inspection)
        if isinstance(protocol_detection, dict):
            protocol_detection = ZeroTrustGatewaySettingsSettingsProtocolDetection(**protocol_detection)
        if isinstance(sandbox, dict):
            sandbox = ZeroTrustGatewaySettingsSettingsSandbox(**sandbox)
        if isinstance(tls_decrypt, dict):
            tls_decrypt = ZeroTrustGatewaySettingsSettingsTlsDecrypt(**tls_decrypt)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f715ae0595e07919931305acd2a07ddefb2bfc0489ff466af13f6bd6f96bd7af)
            check_type(argname="argument activity_log", value=activity_log, expected_type=type_hints["activity_log"])
            check_type(argname="argument antivirus", value=antivirus, expected_type=type_hints["antivirus"])
            check_type(argname="argument block_page", value=block_page, expected_type=type_hints["block_page"])
            check_type(argname="argument body_scanning", value=body_scanning, expected_type=type_hints["body_scanning"])
            check_type(argname="argument browser_isolation", value=browser_isolation, expected_type=type_hints["browser_isolation"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument custom_certificate", value=custom_certificate, expected_type=type_hints["custom_certificate"])
            check_type(argname="argument extended_email_matching", value=extended_email_matching, expected_type=type_hints["extended_email_matching"])
            check_type(argname="argument fips", value=fips, expected_type=type_hints["fips"])
            check_type(argname="argument host_selector", value=host_selector, expected_type=type_hints["host_selector"])
            check_type(argname="argument inspection", value=inspection, expected_type=type_hints["inspection"])
            check_type(argname="argument protocol_detection", value=protocol_detection, expected_type=type_hints["protocol_detection"])
            check_type(argname="argument sandbox", value=sandbox, expected_type=type_hints["sandbox"])
            check_type(argname="argument tls_decrypt", value=tls_decrypt, expected_type=type_hints["tls_decrypt"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if activity_log is not None:
            self._values["activity_log"] = activity_log
        if antivirus is not None:
            self._values["antivirus"] = antivirus
        if block_page is not None:
            self._values["block_page"] = block_page
        if body_scanning is not None:
            self._values["body_scanning"] = body_scanning
        if browser_isolation is not None:
            self._values["browser_isolation"] = browser_isolation
        if certificate is not None:
            self._values["certificate"] = certificate
        if custom_certificate is not None:
            self._values["custom_certificate"] = custom_certificate
        if extended_email_matching is not None:
            self._values["extended_email_matching"] = extended_email_matching
        if fips is not None:
            self._values["fips"] = fips
        if host_selector is not None:
            self._values["host_selector"] = host_selector
        if inspection is not None:
            self._values["inspection"] = inspection
        if protocol_detection is not None:
            self._values["protocol_detection"] = protocol_detection
        if sandbox is not None:
            self._values["sandbox"] = sandbox
        if tls_decrypt is not None:
            self._values["tls_decrypt"] = tls_decrypt

    @builtins.property
    def activity_log(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsActivityLog"]:
        '''Activity log settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#activity_log ZeroTrustGatewaySettings#activity_log}
        '''
        result = self._values.get("activity_log")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsActivityLog"], result)

    @builtins.property
    def antivirus(self) -> typing.Optional["ZeroTrustGatewaySettingsSettingsAntivirus"]:
        '''Anti-virus settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#antivirus ZeroTrustGatewaySettings#antivirus}
        '''
        result = self._values.get("antivirus")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsAntivirus"], result)

    @builtins.property
    def block_page(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsBlockPage"]:
        '''Block page layout settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#block_page ZeroTrustGatewaySettings#block_page}
        '''
        result = self._values.get("block_page")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsBlockPage"], result)

    @builtins.property
    def body_scanning(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsBodyScanning"]:
        '''DLP body scanning settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#body_scanning ZeroTrustGatewaySettings#body_scanning}
        '''
        result = self._values.get("body_scanning")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsBodyScanning"], result)

    @builtins.property
    def browser_isolation(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsBrowserIsolation"]:
        '''Browser isolation settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#browser_isolation ZeroTrustGatewaySettings#browser_isolation}
        '''
        result = self._values.get("browser_isolation")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsBrowserIsolation"], result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsCertificate"]:
        '''Certificate settings for Gateway TLS interception. If not specified, the Cloudflare Root CA will be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#certificate ZeroTrustGatewaySettings#certificate}
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsCertificate"], result)

    @builtins.property
    def custom_certificate(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsCustomCertificate"]:
        '''Custom certificate settings for BYO-PKI. (deprecated and replaced by ``certificate``).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#custom_certificate ZeroTrustGatewaySettings#custom_certificate}
        '''
        result = self._values.get("custom_certificate")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsCustomCertificate"], result)

    @builtins.property
    def extended_email_matching(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsExtendedEmailMatching"]:
        '''Extended e-mail matching settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#extended_email_matching ZeroTrustGatewaySettings#extended_email_matching}
        '''
        result = self._values.get("extended_email_matching")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsExtendedEmailMatching"], result)

    @builtins.property
    def fips(self) -> typing.Optional["ZeroTrustGatewaySettingsSettingsFips"]:
        '''FIPS settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#fips ZeroTrustGatewaySettings#fips}
        '''
        result = self._values.get("fips")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsFips"], result)

    @builtins.property
    def host_selector(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsHostSelector"]:
        '''Setting to enable host selector in egress policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#host_selector ZeroTrustGatewaySettings#host_selector}
        '''
        result = self._values.get("host_selector")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsHostSelector"], result)

    @builtins.property
    def inspection(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsInspection"]:
        '''Setting to define inspection settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#inspection ZeroTrustGatewaySettings#inspection}
        '''
        result = self._values.get("inspection")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsInspection"], result)

    @builtins.property
    def protocol_detection(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsProtocolDetection"]:
        '''Protocol Detection settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#protocol_detection ZeroTrustGatewaySettings#protocol_detection}
        '''
        result = self._values.get("protocol_detection")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsProtocolDetection"], result)

    @builtins.property
    def sandbox(self) -> typing.Optional["ZeroTrustGatewaySettingsSettingsSandbox"]:
        '''Sandbox settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#sandbox ZeroTrustGatewaySettings#sandbox}
        '''
        result = self._values.get("sandbox")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsSandbox"], result)

    @builtins.property
    def tls_decrypt(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsTlsDecrypt"]:
        '''TLS interception settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#tls_decrypt ZeroTrustGatewaySettings#tls_decrypt}
        '''
        result = self._values.get("tls_decrypt")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsTlsDecrypt"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsActivityLog",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ZeroTrustGatewaySettingsSettingsActivityLog:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Enable activity logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__449048db3b5d9cc23c492ddb4c651230efd72fc1a90d3e16fe1686f4d2c60098)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable activity logging.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsActivityLog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsActivityLogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsActivityLogOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4fa3909832a7ff672424f0ab4081c71f48a94f81bbc2778053a5b0aabbccf9e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c837e5d867e238d3da2c463839e71e18382f9d88473d25a65d8e683b1c329a30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsActivityLog]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsActivityLog]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsActivityLog]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__935721b3effc640937a977b286ddd90734f69f3b7234da1c7a56463e36856978)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsAntivirus",
    jsii_struct_bases=[],
    name_mapping={
        "enabled_download_phase": "enabledDownloadPhase",
        "enabled_upload_phase": "enabledUploadPhase",
        "fail_closed": "failClosed",
        "notification_settings": "notificationSettings",
    },
)
class ZeroTrustGatewaySettingsSettingsAntivirus:
    def __init__(
        self,
        *,
        enabled_download_phase: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled_upload_phase: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fail_closed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notification_settings: typing.Optional[typing.Union["ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param enabled_download_phase: Enable anti-virus scanning on downloads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled_download_phase ZeroTrustGatewaySettings#enabled_download_phase}
        :param enabled_upload_phase: Enable anti-virus scanning on uploads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled_upload_phase ZeroTrustGatewaySettings#enabled_upload_phase}
        :param fail_closed: Block requests for files that cannot be scanned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#fail_closed ZeroTrustGatewaySettings#fail_closed}
        :param notification_settings: Configure a message to display on the user's device when an antivirus search is performed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#notification_settings ZeroTrustGatewaySettings#notification_settings}
        '''
        if isinstance(notification_settings, dict):
            notification_settings = ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings(**notification_settings)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__debc1555f7ea4284a087279cc6d87e0a641cb02e6717b65ead0d58b0d5b3c50f)
            check_type(argname="argument enabled_download_phase", value=enabled_download_phase, expected_type=type_hints["enabled_download_phase"])
            check_type(argname="argument enabled_upload_phase", value=enabled_upload_phase, expected_type=type_hints["enabled_upload_phase"])
            check_type(argname="argument fail_closed", value=fail_closed, expected_type=type_hints["fail_closed"])
            check_type(argname="argument notification_settings", value=notification_settings, expected_type=type_hints["notification_settings"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled_download_phase is not None:
            self._values["enabled_download_phase"] = enabled_download_phase
        if enabled_upload_phase is not None:
            self._values["enabled_upload_phase"] = enabled_upload_phase
        if fail_closed is not None:
            self._values["fail_closed"] = fail_closed
        if notification_settings is not None:
            self._values["notification_settings"] = notification_settings

    @builtins.property
    def enabled_download_phase(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable anti-virus scanning on downloads.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled_download_phase ZeroTrustGatewaySettings#enabled_download_phase}
        '''
        result = self._values.get("enabled_download_phase")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled_upload_phase(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable anti-virus scanning on uploads.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled_upload_phase ZeroTrustGatewaySettings#enabled_upload_phase}
        '''
        result = self._values.get("enabled_upload_phase")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def fail_closed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Block requests for files that cannot be scanned.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#fail_closed ZeroTrustGatewaySettings#fail_closed}
        '''
        result = self._values.get("fail_closed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def notification_settings(
        self,
    ) -> typing.Optional["ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings"]:
        '''Configure a message to display on the user's device when an antivirus search is performed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#notification_settings ZeroTrustGatewaySettings#notification_settings}
        '''
        result = self._values.get("notification_settings")
        return typing.cast(typing.Optional["ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsAntivirus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "include_context": "includeContext",
        "msg": "msg",
        "support_url": "supportUrl",
    },
)
class ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        msg: typing.Optional[builtins.str] = None,
        support_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Set notification on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param include_context: If true, context information will be passed as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#include_context ZeroTrustGatewaySettings#include_context}
        :param msg: Customize the message shown in the notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#msg ZeroTrustGatewaySettings#msg}
        :param support_url: Optional URL to direct users to additional information. If not set, the notification will open a block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#support_url ZeroTrustGatewaySettings#support_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e7391ec28d597088189b0d496dfa49feafde4f72eaf7ba2e5c731ab5a78bae0)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument include_context", value=include_context, expected_type=type_hints["include_context"])
            check_type(argname="argument msg", value=msg, expected_type=type_hints["msg"])
            check_type(argname="argument support_url", value=support_url, expected_type=type_hints["support_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if include_context is not None:
            self._values["include_context"] = include_context
        if msg is not None:
            self._values["msg"] = msg
        if support_url is not None:
            self._values["support_url"] = support_url

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set notification on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def include_context(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, context information will be passed as query parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#include_context ZeroTrustGatewaySettings#include_context}
        '''
        result = self._values.get("include_context")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def msg(self) -> typing.Optional[builtins.str]:
        '''Customize the message shown in the notification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#msg ZeroTrustGatewaySettings#msg}
        '''
        result = self._values.get("msg")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def support_url(self) -> typing.Optional[builtins.str]:
        '''Optional URL to direct users to additional information. If not set, the notification will open a block page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#support_url ZeroTrustGatewaySettings#support_url}
        '''
        result = self._values.get("support_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c62aa0dd553fa1dd819abb33ebe667327874d2f7ded9d4a6f464be9077e94bd6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetIncludeContext")
    def reset_include_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeContext", []))

    @jsii.member(jsii_name="resetMsg")
    def reset_msg(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMsg", []))

    @jsii.member(jsii_name="resetSupportUrl")
    def reset_support_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportUrl", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="includeContextInput")
    def include_context_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "includeContextInput"))

    @builtins.property
    @jsii.member(jsii_name="msgInput")
    def msg_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "msgInput"))

    @builtins.property
    @jsii.member(jsii_name="supportUrlInput")
    def support_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "supportUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6283e752b2738ce11e2554316725fbbe44bf1ca2d1645845dad34d25be3025d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeContext")
    def include_context(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "includeContext"))

    @include_context.setter
    def include_context(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e8e93a5a41f42da1d2564ee33149e7d39d9f7cc916492d1950495702769a585)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeContext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="msg")
    def msg(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "msg"))

    @msg.setter
    def msg(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab77cb20c4ce9d5c1afd25979f2d7714c38c3f4c196910ee18fbdf59834f7e99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "msg", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="supportUrl")
    def support_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "supportUrl"))

    @support_url.setter
    def support_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddac3c62e77742256b5ed57a9cd76f5eea902c77d2a8907c226096c232f4bec5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "supportUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a3fc0ade33c685c1763796088c60b714da417a8f19105e431a19a91aa756034)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustGatewaySettingsSettingsAntivirusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsAntivirusOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f3aba34ab57cc12f9785afda930f06c47ac3f1663b9a4fd1425ac992171197b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNotificationSettings")
    def put_notification_settings(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        msg: typing.Optional[builtins.str] = None,
        support_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Set notification on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param include_context: If true, context information will be passed as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#include_context ZeroTrustGatewaySettings#include_context}
        :param msg: Customize the message shown in the notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#msg ZeroTrustGatewaySettings#msg}
        :param support_url: Optional URL to direct users to additional information. If not set, the notification will open a block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#support_url ZeroTrustGatewaySettings#support_url}
        '''
        value = ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings(
            enabled=enabled,
            include_context=include_context,
            msg=msg,
            support_url=support_url,
        )

        return typing.cast(None, jsii.invoke(self, "putNotificationSettings", [value]))

    @jsii.member(jsii_name="resetEnabledDownloadPhase")
    def reset_enabled_download_phase(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabledDownloadPhase", []))

    @jsii.member(jsii_name="resetEnabledUploadPhase")
    def reset_enabled_upload_phase(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabledUploadPhase", []))

    @jsii.member(jsii_name="resetFailClosed")
    def reset_fail_closed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailClosed", []))

    @jsii.member(jsii_name="resetNotificationSettings")
    def reset_notification_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotificationSettings", []))

    @builtins.property
    @jsii.member(jsii_name="notificationSettings")
    def notification_settings(
        self,
    ) -> ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettingsOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettingsOutputReference, jsii.get(self, "notificationSettings"))

    @builtins.property
    @jsii.member(jsii_name="enabledDownloadPhaseInput")
    def enabled_download_phase_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledDownloadPhaseInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledUploadPhaseInput")
    def enabled_upload_phase_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledUploadPhaseInput"))

    @builtins.property
    @jsii.member(jsii_name="failClosedInput")
    def fail_closed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "failClosedInput"))

    @builtins.property
    @jsii.member(jsii_name="notificationSettingsInput")
    def notification_settings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings]], jsii.get(self, "notificationSettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledDownloadPhase")
    def enabled_download_phase(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabledDownloadPhase"))

    @enabled_download_phase.setter
    def enabled_download_phase(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72daabf3c9eed1a5c18fc388ff6171bb09c25f9464d64296d10f150226541c08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabledDownloadPhase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabledUploadPhase")
    def enabled_upload_phase(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabledUploadPhase"))

    @enabled_upload_phase.setter
    def enabled_upload_phase(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80cc72128944aa13676730862080d5f7190e2082f5a6475ae04c1eee6f18ab95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabledUploadPhase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="failClosed")
    def fail_closed(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "failClosed"))

    @fail_closed.setter
    def fail_closed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21a77565f7f9d89fb015331f3370a3fa4dbf7108125ea7d04d6a52a975c49536)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failClosed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f03bddab5ab625ecc1c98d597818ad48bb8080624bffc4524093599d22fca6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsBlockPage",
    jsii_struct_bases=[],
    name_mapping={
        "background_color": "backgroundColor",
        "enabled": "enabled",
        "footer_text": "footerText",
        "header_text": "headerText",
        "include_context": "includeContext",
        "logo_path": "logoPath",
        "mailto_address": "mailtoAddress",
        "mailto_subject": "mailtoSubject",
        "mode": "mode",
        "name": "name",
        "read_only": "readOnly",
        "source_account": "sourceAccount",
        "suppress_footer": "suppressFooter",
        "target_uri": "targetUri",
        "version": "version",
    },
)
class ZeroTrustGatewaySettingsSettingsBlockPage:
    def __init__(
        self,
        *,
        background_color: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        footer_text: typing.Optional[builtins.str] = None,
        header_text: typing.Optional[builtins.str] = None,
        include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        logo_path: typing.Optional[builtins.str] = None,
        mailto_address: typing.Optional[builtins.str] = None,
        mailto_subject: typing.Optional[builtins.str] = None,
        mode: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        source_account: typing.Optional[builtins.str] = None,
        suppress_footer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        target_uri: typing.Optional[builtins.str] = None,
        version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param background_color: If mode is customized_block_page: block page background color in #rrggbb format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#background_color ZeroTrustGatewaySettings#background_color}
        :param enabled: Enable only cipher suites and TLS versions compliant with FIPS. 140-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param footer_text: If mode is customized_block_page: block page footer text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#footer_text ZeroTrustGatewaySettings#footer_text}
        :param header_text: If mode is customized_block_page: block page header text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#header_text ZeroTrustGatewaySettings#header_text}
        :param include_context: If mode is redirect_uri: when enabled, context will be appended to target_uri as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#include_context ZeroTrustGatewaySettings#include_context}
        :param logo_path: If mode is customized_block_page: full URL to the logo file. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#logo_path ZeroTrustGatewaySettings#logo_path}
        :param mailto_address: If mode is customized_block_page: admin email for users to contact. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mailto_address ZeroTrustGatewaySettings#mailto_address}
        :param mailto_subject: If mode is customized_block_page: subject line for emails created from block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mailto_subject ZeroTrustGatewaySettings#mailto_subject}
        :param mode: Controls whether the user is redirected to a Cloudflare-hosted block page or to a customer-provided URI. Available values: "", "customized_block_page", "redirect_uri". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mode ZeroTrustGatewaySettings#mode}
        :param name: If mode is customized_block_page: block page title. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#name ZeroTrustGatewaySettings#name}
        :param read_only: This setting was shared via the Orgs API and cannot be edited by the current account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#read_only ZeroTrustGatewaySettings#read_only}
        :param source_account: Account tag of account that shared this setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#source_account ZeroTrustGatewaySettings#source_account}
        :param suppress_footer: If mode is customized_block_page: suppress detailed info at the bottom of the block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#suppress_footer ZeroTrustGatewaySettings#suppress_footer}
        :param target_uri: If mode is redirect_uri: URI to which the user should be redirected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#target_uri ZeroTrustGatewaySettings#target_uri}
        :param version: Version number of the setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#version ZeroTrustGatewaySettings#version}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6e87cdd5d37df790937259a5800085b17678f0d78a36aae00df49e610ee491a)
            check_type(argname="argument background_color", value=background_color, expected_type=type_hints["background_color"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument footer_text", value=footer_text, expected_type=type_hints["footer_text"])
            check_type(argname="argument header_text", value=header_text, expected_type=type_hints["header_text"])
            check_type(argname="argument include_context", value=include_context, expected_type=type_hints["include_context"])
            check_type(argname="argument logo_path", value=logo_path, expected_type=type_hints["logo_path"])
            check_type(argname="argument mailto_address", value=mailto_address, expected_type=type_hints["mailto_address"])
            check_type(argname="argument mailto_subject", value=mailto_subject, expected_type=type_hints["mailto_subject"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument read_only", value=read_only, expected_type=type_hints["read_only"])
            check_type(argname="argument source_account", value=source_account, expected_type=type_hints["source_account"])
            check_type(argname="argument suppress_footer", value=suppress_footer, expected_type=type_hints["suppress_footer"])
            check_type(argname="argument target_uri", value=target_uri, expected_type=type_hints["target_uri"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if background_color is not None:
            self._values["background_color"] = background_color
        if enabled is not None:
            self._values["enabled"] = enabled
        if footer_text is not None:
            self._values["footer_text"] = footer_text
        if header_text is not None:
            self._values["header_text"] = header_text
        if include_context is not None:
            self._values["include_context"] = include_context
        if logo_path is not None:
            self._values["logo_path"] = logo_path
        if mailto_address is not None:
            self._values["mailto_address"] = mailto_address
        if mailto_subject is not None:
            self._values["mailto_subject"] = mailto_subject
        if mode is not None:
            self._values["mode"] = mode
        if name is not None:
            self._values["name"] = name
        if read_only is not None:
            self._values["read_only"] = read_only
        if source_account is not None:
            self._values["source_account"] = source_account
        if suppress_footer is not None:
            self._values["suppress_footer"] = suppress_footer
        if target_uri is not None:
            self._values["target_uri"] = target_uri
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def background_color(self) -> typing.Optional[builtins.str]:
        '''If mode is customized_block_page: block page background color in #rrggbb format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#background_color ZeroTrustGatewaySettings#background_color}
        '''
        result = self._values.get("background_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable only cipher suites and TLS versions compliant with FIPS. 140-2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def footer_text(self) -> typing.Optional[builtins.str]:
        '''If mode is customized_block_page: block page footer text.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#footer_text ZeroTrustGatewaySettings#footer_text}
        '''
        result = self._values.get("footer_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def header_text(self) -> typing.Optional[builtins.str]:
        '''If mode is customized_block_page: block page header text.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#header_text ZeroTrustGatewaySettings#header_text}
        '''
        result = self._values.get("header_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_context(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If mode is redirect_uri: when enabled, context will be appended to target_uri as query parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#include_context ZeroTrustGatewaySettings#include_context}
        '''
        result = self._values.get("include_context")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def logo_path(self) -> typing.Optional[builtins.str]:
        '''If mode is customized_block_page: full URL to the logo file.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#logo_path ZeroTrustGatewaySettings#logo_path}
        '''
        result = self._values.get("logo_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mailto_address(self) -> typing.Optional[builtins.str]:
        '''If mode is customized_block_page: admin email for users to contact.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mailto_address ZeroTrustGatewaySettings#mailto_address}
        '''
        result = self._values.get("mailto_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mailto_subject(self) -> typing.Optional[builtins.str]:
        '''If mode is customized_block_page: subject line for emails created from block page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mailto_subject ZeroTrustGatewaySettings#mailto_subject}
        '''
        result = self._values.get("mailto_subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Controls whether the user is redirected to a Cloudflare-hosted block page or to a customer-provided URI.

        Available values: "", "customized_block_page", "redirect_uri".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mode ZeroTrustGatewaySettings#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''If mode is customized_block_page: block page title.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#name ZeroTrustGatewaySettings#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''This setting was shared via the Orgs API and cannot be edited by the current account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#read_only ZeroTrustGatewaySettings#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def source_account(self) -> typing.Optional[builtins.str]:
        '''Account tag of account that shared this setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#source_account ZeroTrustGatewaySettings#source_account}
        '''
        result = self._values.get("source_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_footer(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If mode is customized_block_page: suppress detailed info at the bottom of the block page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#suppress_footer ZeroTrustGatewaySettings#suppress_footer}
        '''
        result = self._values.get("suppress_footer")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def target_uri(self) -> typing.Optional[builtins.str]:
        '''If mode is redirect_uri: URI to which the user should be redirected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#target_uri ZeroTrustGatewaySettings#target_uri}
        '''
        result = self._values.get("target_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[jsii.Number]:
        '''Version number of the setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#version ZeroTrustGatewaySettings#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsBlockPage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsBlockPageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsBlockPageOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaaae33322b392eb56bb40c10206640556b9e9f13fd29ce17c72f729541384c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBackgroundColor")
    def reset_background_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackgroundColor", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetFooterText")
    def reset_footer_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFooterText", []))

    @jsii.member(jsii_name="resetHeaderText")
    def reset_header_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaderText", []))

    @jsii.member(jsii_name="resetIncludeContext")
    def reset_include_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeContext", []))

    @jsii.member(jsii_name="resetLogoPath")
    def reset_logo_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogoPath", []))

    @jsii.member(jsii_name="resetMailtoAddress")
    def reset_mailto_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMailtoAddress", []))

    @jsii.member(jsii_name="resetMailtoSubject")
    def reset_mailto_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMailtoSubject", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetSourceAccount")
    def reset_source_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceAccount", []))

    @jsii.member(jsii_name="resetSuppressFooter")
    def reset_suppress_footer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuppressFooter", []))

    @jsii.member(jsii_name="resetTargetUri")
    def reset_target_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetUri", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property
    @jsii.member(jsii_name="backgroundColorInput")
    def background_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backgroundColorInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="footerTextInput")
    def footer_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "footerTextInput"))

    @builtins.property
    @jsii.member(jsii_name="headerTextInput")
    def header_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerTextInput"))

    @builtins.property
    @jsii.member(jsii_name="includeContextInput")
    def include_context_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "includeContextInput"))

    @builtins.property
    @jsii.member(jsii_name="logoPathInput")
    def logo_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logoPathInput"))

    @builtins.property
    @jsii.member(jsii_name="mailtoAddressInput")
    def mailto_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mailtoAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="mailtoSubjectInput")
    def mailto_subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mailtoSubjectInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceAccountInput")
    def source_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="suppressFooterInput")
    def suppress_footer_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "suppressFooterInput"))

    @builtins.property
    @jsii.member(jsii_name="targetUriInput")
    def target_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetUriInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="backgroundColor")
    def background_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backgroundColor"))

    @background_color.setter
    def background_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7ef1784c3fa794018174c38ac92bcc0693826ac0658859324983669f5a461cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backgroundColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccff18927fb243b4d7a1e7662e44574facb1c036291780184f099de618ae4d68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="footerText")
    def footer_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "footerText"))

    @footer_text.setter
    def footer_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b428c5b1ff05690d92b5944ca295191de65e1740e2189f7e3114a8013f8bb114)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "footerText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headerText")
    def header_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerText"))

    @header_text.setter
    def header_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__151657b4e992cf771213b989606bcb5421a6618c697cf8b151c7ea6742454538)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headerText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeContext")
    def include_context(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "includeContext"))

    @include_context.setter
    def include_context(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2a40c133514a334f322411a5a4a94c2127d9701c7bd2370ba5a2f9c5a80fa10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeContext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logoPath")
    def logo_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logoPath"))

    @logo_path.setter
    def logo_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbc821a62689b9ed9fe43a3127ac8b0973aa0830b12166008d3998b72bb70c73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logoPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mailtoAddress")
    def mailto_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mailtoAddress"))

    @mailto_address.setter
    def mailto_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8adc75b927f097ca1707ba6596b8f37691ad5f24d25ad89d85a3d303217fb897)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mailtoAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mailtoSubject")
    def mailto_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mailtoSubject"))

    @mailto_subject.setter
    def mailto_subject(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__584a7dd956fa650ec15a800d8f4823dc147a2605051918328755dd1ae2795718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mailtoSubject", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2df23eb095f408c22af3f5e7ff229a4a86923c9b74684f59d5dafd5c663e14b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f67b12449ae4601985cdd82440d5695c4ad216a11c63c76a4734da9a31c3fbfe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47f6955a1756a0fa58dba4fb03b16daa8412e8c847e4309a0f4c6a128886e136)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceAccount")
    def source_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceAccount"))

    @source_account.setter
    def source_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00dc919dacfbfbe5c1d961f27133b1f05a9a1e3dc71440d5e57229d2f398bccf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="suppressFooter")
    def suppress_footer(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "suppressFooter"))

    @suppress_footer.setter
    def suppress_footer(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__170a63e578b422a42c0031bad6e3cd0d9773224888b0c3f47b58bd10ece621a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suppressFooter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetUri")
    def target_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetUri"))

    @target_uri.setter
    def target_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab01167783c6e0bfc0c07ecc1955478c026814afe7ac0bef0685374a72eed854)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetUri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @version.setter
    def version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1747d6586d9310a91a2b262eb788e609ed05fa5f8c4cbad9524c3e6d22f561b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBlockPage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBlockPage]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBlockPage]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__804c5935b681b27181cf8352eeaf1d18b4c7058f7370518ca1fc18f41391427a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsBodyScanning",
    jsii_struct_bases=[],
    name_mapping={"inspection_mode": "inspectionMode"},
)
class ZeroTrustGatewaySettingsSettingsBodyScanning:
    def __init__(
        self,
        *,
        inspection_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param inspection_mode: Set the inspection mode to either ``deep`` or ``shallow``. Available values: "deep", "shallow". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#inspection_mode ZeroTrustGatewaySettings#inspection_mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__973ad4d19e5aae6235b568364c5781b621151f19f39ddfa064da743b0b6dd9b3)
            check_type(argname="argument inspection_mode", value=inspection_mode, expected_type=type_hints["inspection_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if inspection_mode is not None:
            self._values["inspection_mode"] = inspection_mode

    @builtins.property
    def inspection_mode(self) -> typing.Optional[builtins.str]:
        '''Set the inspection mode to either ``deep`` or ``shallow``. Available values: "deep", "shallow".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#inspection_mode ZeroTrustGatewaySettings#inspection_mode}
        '''
        result = self._values.get("inspection_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsBodyScanning(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsBodyScanningOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsBodyScanningOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3928af4182102fd1a91b4a8cb4296b80087237f7d298409eab06dca4e412b182)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetInspectionMode")
    def reset_inspection_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInspectionMode", []))

    @builtins.property
    @jsii.member(jsii_name="inspectionModeInput")
    def inspection_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inspectionModeInput"))

    @builtins.property
    @jsii.member(jsii_name="inspectionMode")
    def inspection_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inspectionMode"))

    @inspection_mode.setter
    def inspection_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c13622f7f1e03389c9eb968eb77ab826ca1bb826e94206f1c9636c490e82e86f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inspectionMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBodyScanning]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBodyScanning]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBodyScanning]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c44470f741fe91ebe3a71cb44674eda3a76cbd302368a9b9741b335557eb1ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsBrowserIsolation",
    jsii_struct_bases=[],
    name_mapping={
        "non_identity_enabled": "nonIdentityEnabled",
        "url_browser_isolation_enabled": "urlBrowserIsolationEnabled",
    },
)
class ZeroTrustGatewaySettingsSettingsBrowserIsolation:
    def __init__(
        self,
        *,
        non_identity_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url_browser_isolation_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param non_identity_enabled: Enable non-identity onramp support for Browser Isolation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#non_identity_enabled ZeroTrustGatewaySettings#non_identity_enabled}
        :param url_browser_isolation_enabled: Enable Clientless Browser Isolation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#url_browser_isolation_enabled ZeroTrustGatewaySettings#url_browser_isolation_enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23ac38400d65f804c8df06e5d0c3b1b0d41dfed5be2fe704efac4498101cc026)
            check_type(argname="argument non_identity_enabled", value=non_identity_enabled, expected_type=type_hints["non_identity_enabled"])
            check_type(argname="argument url_browser_isolation_enabled", value=url_browser_isolation_enabled, expected_type=type_hints["url_browser_isolation_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if non_identity_enabled is not None:
            self._values["non_identity_enabled"] = non_identity_enabled
        if url_browser_isolation_enabled is not None:
            self._values["url_browser_isolation_enabled"] = url_browser_isolation_enabled

    @builtins.property
    def non_identity_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable non-identity onramp support for Browser Isolation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#non_identity_enabled ZeroTrustGatewaySettings#non_identity_enabled}
        '''
        result = self._values.get("non_identity_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def url_browser_isolation_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Clientless Browser Isolation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#url_browser_isolation_enabled ZeroTrustGatewaySettings#url_browser_isolation_enabled}
        '''
        result = self._values.get("url_browser_isolation_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsBrowserIsolation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsBrowserIsolationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsBrowserIsolationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27e0add587729700dbef6d2bef091ba44c7d2d051876bb0bee45d42dac5fa00f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetNonIdentityEnabled")
    def reset_non_identity_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNonIdentityEnabled", []))

    @jsii.member(jsii_name="resetUrlBrowserIsolationEnabled")
    def reset_url_browser_isolation_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrlBrowserIsolationEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="nonIdentityEnabledInput")
    def non_identity_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "nonIdentityEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="urlBrowserIsolationEnabledInput")
    def url_browser_isolation_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "urlBrowserIsolationEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="nonIdentityEnabled")
    def non_identity_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "nonIdentityEnabled"))

    @non_identity_enabled.setter
    def non_identity_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53b6de3707fad24ea3db01301e5111d38fb3ad949f0200f5379efcee0e404990)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nonIdentityEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlBrowserIsolationEnabled")
    def url_browser_isolation_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "urlBrowserIsolationEnabled"))

    @url_browser_isolation_enabled.setter
    def url_browser_isolation_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6e69bf66acd5a67fd915140ab425e9b535d1d4fa8a6696814e952ae289b5ec2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlBrowserIsolationEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBrowserIsolation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBrowserIsolation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBrowserIsolation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20b915eaa751dd035e0a2f9c55af9fe61d6ef1e09b52127c70416c89d1ef7ec8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsCertificate",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustGatewaySettingsSettingsCertificate:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: UUID of certificate to be used for interception. Certificate must be available (previously called 'active') on the edge. A nil UUID will indicate the Cloudflare Root CA should be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#id ZeroTrustGatewaySettings#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acd1c1b7d41a1878bc2fb86e48dc25d1747cc9ba00a53185e6f4044af1d7b966)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''UUID of certificate to be used for interception.

        Certificate must be available (previously called 'active') on the edge. A nil UUID will indicate the Cloudflare Root CA should be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#id ZeroTrustGatewaySettings#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsCertificateOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ac7ba0d482a07ca8c2c4b6448aa63327fd14ff0d36087dc645f212f5300bdd8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05d413708c953104b7f1abc33eb05fa218102e5f6590a3b7e0836188a487525a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCertificate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCertificate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d40cc7eedd8c13292651312c4f220052df63b3f3c19f3c0911daab02fae12022)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsCustomCertificate",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "binding_status": "bindingStatus",
        "id": "id",
        "updated_at": "updatedAt",
    },
)
class ZeroTrustGatewaySettingsSettingsCustomCertificate:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        binding_status: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable use of custom certificate authority for signing Gateway. traffic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param binding_status: Certificate status (internal). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#binding_status ZeroTrustGatewaySettings#binding_status}
        :param id: UUID of certificate (ID from MTLS certificate store). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#id ZeroTrustGatewaySettings#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#updated_at ZeroTrustGatewaySettings#updated_at}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07e4bf8521ecb98720f42862693ea97f0be075228e6bf59f3a6c1e0c8a9f27f5)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument binding_status", value=binding_status, expected_type=type_hints["binding_status"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enabled": enabled,
        }
        if binding_status is not None:
            self._values["binding_status"] = binding_status
        if id is not None:
            self._values["id"] = id
        if updated_at is not None:
            self._values["updated_at"] = updated_at

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable use of custom certificate authority for signing Gateway. traffic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def binding_status(self) -> typing.Optional[builtins.str]:
        '''Certificate status (internal).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#binding_status ZeroTrustGatewaySettings#binding_status}
        '''
        result = self._values.get("binding_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''UUID of certificate (ID from MTLS certificate store).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#id ZeroTrustGatewaySettings#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_at(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#updated_at ZeroTrustGatewaySettings#updated_at}.'''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsCustomCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsCustomCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsCustomCertificateOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52e65a55b71741e1237ed07a3557c30b451119c06b7bf2bf4734ab9e07ee6e76)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBindingStatus")
    def reset_binding_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBindingStatus", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetUpdatedAt")
    def reset_updated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedAt", []))

    @builtins.property
    @jsii.member(jsii_name="bindingStatusInput")
    def binding_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bindingStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedAtInput")
    def updated_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="bindingStatus")
    def binding_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bindingStatus"))

    @binding_status.setter
    def binding_status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3849e370b812e6447e390fc67ea9bc6041015bd073c713c772b53178254a16d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bindingStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a999e277bd2e41e8059dea75ace31f9e40e74fd2b55d1c81fe0bf4a4e3e522f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da91c39005c5db206fd2ad3706fe203292a04187ca8695dd01412d5db679056f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54d91b9c4cae66ef4043799fa42c859159e70a5ff3ee9e19a371ea08d451bcf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCustomCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCustomCertificate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCustomCertificate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a83269bee907fc41f45e81d8e10ee1370b725a3bc65fa1b7927aa4c86d97ff4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsExtendedEmailMatching",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "read_only": "readOnly",
        "source_account": "sourceAccount",
        "version": "version",
    },
)
class ZeroTrustGatewaySettingsSettingsExtendedEmailMatching:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        source_account: typing.Optional[builtins.str] = None,
        version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Enable matching all variants of user emails (with + or . modifiers) used as criteria in Firewall policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param read_only: This setting was shared via the Orgs API and cannot be edited by the current account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#read_only ZeroTrustGatewaySettings#read_only}
        :param source_account: Account tag of account that shared this setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#source_account ZeroTrustGatewaySettings#source_account}
        :param version: Version number of the setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#version ZeroTrustGatewaySettings#version}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60fc447be0ddd4b0584db955ef229645d061fcac94befe700eaa7a3325b78ec6)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument read_only", value=read_only, expected_type=type_hints["read_only"])
            check_type(argname="argument source_account", value=source_account, expected_type=type_hints["source_account"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if read_only is not None:
            self._values["read_only"] = read_only
        if source_account is not None:
            self._values["source_account"] = source_account
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable matching all variants of user emails (with + or . modifiers) used as criteria in Firewall policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''This setting was shared via the Orgs API and cannot be edited by the current account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#read_only ZeroTrustGatewaySettings#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def source_account(self) -> typing.Optional[builtins.str]:
        '''Account tag of account that shared this setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#source_account ZeroTrustGatewaySettings#source_account}
        '''
        result = self._values.get("source_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[jsii.Number]:
        '''Version number of the setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#version ZeroTrustGatewaySettings#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsExtendedEmailMatching(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsExtendedEmailMatchingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsExtendedEmailMatchingOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13a5e25560d64fa0ab87b5253c47c68b17989c540ffc69a5b9d022b608e6a2df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetSourceAccount")
    def reset_source_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceAccount", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceAccountInput")
    def source_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__747d784829ec35ae1444f341cf38930a9f731f4424954fd5a8b0eb96f8ced12c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1700fe273f491be575a8790e033f491a60b0eb0f7b770134c65cf03ae3f41df8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceAccount")
    def source_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceAccount"))

    @source_account.setter
    def source_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2e6c971bda96295661e96aa142f81f7f7afad83105bb6f370606068609e6999)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @version.setter
    def version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cf03622941a305a79f2ed40dcd8947bfb8b69cc932e5fe4a23c62af6e45b75c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsExtendedEmailMatching]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsExtendedEmailMatching]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsExtendedEmailMatching]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4989154c08c2599532f65d2860e87ddf8c4b60bf1c8046ec674ed9c5dbc5a6a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsFips",
    jsii_struct_bases=[],
    name_mapping={"tls": "tls"},
)
class ZeroTrustGatewaySettingsSettingsFips:
    def __init__(
        self,
        *,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param tls: Enable only cipher suites and TLS versions compliant with FIPS. 140-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#tls ZeroTrustGatewaySettings#tls}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a80f7f1916c83178f0a7cc209122a5d6cce2fbc4458ac460ca9eda36f4df711)
            check_type(argname="argument tls", value=tls, expected_type=type_hints["tls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if tls is not None:
            self._values["tls"] = tls

    @builtins.property
    def tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable only cipher suites and TLS versions compliant with FIPS. 140-2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#tls ZeroTrustGatewaySettings#tls}
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsFips(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsFipsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsFipsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__290eee58dd090a54751b58670a660ea57ab4efcba3b81efa24840bb26408b93b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetTls")
    def reset_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTls", []))

    @builtins.property
    @jsii.member(jsii_name="tlsInput")
    def tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsInput"))

    @builtins.property
    @jsii.member(jsii_name="tls")
    def tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tls"))

    @tls.setter
    def tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e894ada4735d6b96fe10e3e967e16e647ab4eeed07887fe63af09fa73db2591)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsFips]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsFips]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsFips]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd11d6fff29851eda47ca45a202abc5f0fa01c14caf282b3ed41df8a50a3e99f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsHostSelector",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ZeroTrustGatewaySettingsSettingsHostSelector:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Enable filtering via hosts for egress policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f06e24935b71e689908e73b5ede262bd75b4ed2e9b33003d537112efb75aec)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable filtering via hosts for egress policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsHostSelector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsHostSelectorOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsHostSelectorOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70faefaa614c3101c801fe59a585003bdd6a382b22bc0618f1277ac1f31c4e8b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9ffdd1de5473ada98800b8201f648ca111228f84af9146b50f2e88ac57dd331)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsHostSelector]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsHostSelector]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsHostSelector]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78a940c106541741b4c9db5048b113396483a07bee00dd4ff3928f98d209b1f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsInspection",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode"},
)
class ZeroTrustGatewaySettingsSettingsInspection:
    def __init__(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Defines the mode of inspection the proxy will use. - static: Gateway will use static inspection to inspect HTTP on TCP(80). If TLS decryption is on, Gateway will inspect HTTPS traffic on TCP(443) & UDP(443). - dynamic: Gateway will use protocol detection to dynamically inspect HTTP and HTTPS traffic on any port. TLS decryption must be on to inspect HTTPS traffic. Available values: "static", "dynamic". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mode ZeroTrustGatewaySettings#mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ed21a93616261f51830ff4df77cd96334ef745849efc6250f96fe67ae5a8cbe)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Defines the mode of inspection the proxy will use.

        - static: Gateway will use static inspection to inspect HTTP on TCP(80). If TLS decryption is on, Gateway will inspect HTTPS traffic on TCP(443) & UDP(443).
        - dynamic: Gateway will use protocol detection to dynamically inspect HTTP and HTTPS traffic on any port. TLS decryption must be on to inspect HTTPS traffic.
          Available values: "static", "dynamic".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mode ZeroTrustGatewaySettings#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsInspection(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsInspectionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsInspectionOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d17b7b51064ec1171a0b95412ce914d7936a80e29c0aa8d703956e41f2563b5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13ad9a2445874df91af853f6f01def069dc443f4a5f2cac54f509812b18c9089)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsInspection]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsInspection]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsInspection]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__904bbf4bd20573e4afca0c6d1b3e505b4f65c71b3dbcb7fdf07918ab523fa883)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustGatewaySettingsSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__357d4e585509b33d8043922ef652f4b0822b041eec63f3f2e8e1ac2361babd37)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putActivityLog")
    def put_activity_log(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Enable activity logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        value = ZeroTrustGatewaySettingsSettingsActivityLog(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putActivityLog", [value]))

    @jsii.member(jsii_name="putAntivirus")
    def put_antivirus(
        self,
        *,
        enabled_download_phase: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled_upload_phase: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fail_closed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notification_settings: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param enabled_download_phase: Enable anti-virus scanning on downloads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled_download_phase ZeroTrustGatewaySettings#enabled_download_phase}
        :param enabled_upload_phase: Enable anti-virus scanning on uploads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled_upload_phase ZeroTrustGatewaySettings#enabled_upload_phase}
        :param fail_closed: Block requests for files that cannot be scanned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#fail_closed ZeroTrustGatewaySettings#fail_closed}
        :param notification_settings: Configure a message to display on the user's device when an antivirus search is performed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#notification_settings ZeroTrustGatewaySettings#notification_settings}
        '''
        value = ZeroTrustGatewaySettingsSettingsAntivirus(
            enabled_download_phase=enabled_download_phase,
            enabled_upload_phase=enabled_upload_phase,
            fail_closed=fail_closed,
            notification_settings=notification_settings,
        )

        return typing.cast(None, jsii.invoke(self, "putAntivirus", [value]))

    @jsii.member(jsii_name="putBlockPage")
    def put_block_page(
        self,
        *,
        background_color: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        footer_text: typing.Optional[builtins.str] = None,
        header_text: typing.Optional[builtins.str] = None,
        include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        logo_path: typing.Optional[builtins.str] = None,
        mailto_address: typing.Optional[builtins.str] = None,
        mailto_subject: typing.Optional[builtins.str] = None,
        mode: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        source_account: typing.Optional[builtins.str] = None,
        suppress_footer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        target_uri: typing.Optional[builtins.str] = None,
        version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param background_color: If mode is customized_block_page: block page background color in #rrggbb format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#background_color ZeroTrustGatewaySettings#background_color}
        :param enabled: Enable only cipher suites and TLS versions compliant with FIPS. 140-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param footer_text: If mode is customized_block_page: block page footer text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#footer_text ZeroTrustGatewaySettings#footer_text}
        :param header_text: If mode is customized_block_page: block page header text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#header_text ZeroTrustGatewaySettings#header_text}
        :param include_context: If mode is redirect_uri: when enabled, context will be appended to target_uri as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#include_context ZeroTrustGatewaySettings#include_context}
        :param logo_path: If mode is customized_block_page: full URL to the logo file. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#logo_path ZeroTrustGatewaySettings#logo_path}
        :param mailto_address: If mode is customized_block_page: admin email for users to contact. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mailto_address ZeroTrustGatewaySettings#mailto_address}
        :param mailto_subject: If mode is customized_block_page: subject line for emails created from block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mailto_subject ZeroTrustGatewaySettings#mailto_subject}
        :param mode: Controls whether the user is redirected to a Cloudflare-hosted block page or to a customer-provided URI. Available values: "", "customized_block_page", "redirect_uri". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mode ZeroTrustGatewaySettings#mode}
        :param name: If mode is customized_block_page: block page title. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#name ZeroTrustGatewaySettings#name}
        :param read_only: This setting was shared via the Orgs API and cannot be edited by the current account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#read_only ZeroTrustGatewaySettings#read_only}
        :param source_account: Account tag of account that shared this setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#source_account ZeroTrustGatewaySettings#source_account}
        :param suppress_footer: If mode is customized_block_page: suppress detailed info at the bottom of the block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#suppress_footer ZeroTrustGatewaySettings#suppress_footer}
        :param target_uri: If mode is redirect_uri: URI to which the user should be redirected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#target_uri ZeroTrustGatewaySettings#target_uri}
        :param version: Version number of the setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#version ZeroTrustGatewaySettings#version}
        '''
        value = ZeroTrustGatewaySettingsSettingsBlockPage(
            background_color=background_color,
            enabled=enabled,
            footer_text=footer_text,
            header_text=header_text,
            include_context=include_context,
            logo_path=logo_path,
            mailto_address=mailto_address,
            mailto_subject=mailto_subject,
            mode=mode,
            name=name,
            read_only=read_only,
            source_account=source_account,
            suppress_footer=suppress_footer,
            target_uri=target_uri,
            version=version,
        )

        return typing.cast(None, jsii.invoke(self, "putBlockPage", [value]))

    @jsii.member(jsii_name="putBodyScanning")
    def put_body_scanning(
        self,
        *,
        inspection_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param inspection_mode: Set the inspection mode to either ``deep`` or ``shallow``. Available values: "deep", "shallow". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#inspection_mode ZeroTrustGatewaySettings#inspection_mode}
        '''
        value = ZeroTrustGatewaySettingsSettingsBodyScanning(
            inspection_mode=inspection_mode
        )

        return typing.cast(None, jsii.invoke(self, "putBodyScanning", [value]))

    @jsii.member(jsii_name="putBrowserIsolation")
    def put_browser_isolation(
        self,
        *,
        non_identity_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url_browser_isolation_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param non_identity_enabled: Enable non-identity onramp support for Browser Isolation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#non_identity_enabled ZeroTrustGatewaySettings#non_identity_enabled}
        :param url_browser_isolation_enabled: Enable Clientless Browser Isolation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#url_browser_isolation_enabled ZeroTrustGatewaySettings#url_browser_isolation_enabled}
        '''
        value = ZeroTrustGatewaySettingsSettingsBrowserIsolation(
            non_identity_enabled=non_identity_enabled,
            url_browser_isolation_enabled=url_browser_isolation_enabled,
        )

        return typing.cast(None, jsii.invoke(self, "putBrowserIsolation", [value]))

    @jsii.member(jsii_name="putCertificate")
    def put_certificate(self, *, id: builtins.str) -> None:
        '''
        :param id: UUID of certificate to be used for interception. Certificate must be available (previously called 'active') on the edge. A nil UUID will indicate the Cloudflare Root CA should be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#id ZeroTrustGatewaySettings#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustGatewaySettingsSettingsCertificate(id=id)

        return typing.cast(None, jsii.invoke(self, "putCertificate", [value]))

    @jsii.member(jsii_name="putCustomCertificate")
    def put_custom_certificate(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        binding_status: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable use of custom certificate authority for signing Gateway. traffic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param binding_status: Certificate status (internal). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#binding_status ZeroTrustGatewaySettings#binding_status}
        :param id: UUID of certificate (ID from MTLS certificate store). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#id ZeroTrustGatewaySettings#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#updated_at ZeroTrustGatewaySettings#updated_at}.
        '''
        value = ZeroTrustGatewaySettingsSettingsCustomCertificate(
            enabled=enabled,
            binding_status=binding_status,
            id=id,
            updated_at=updated_at,
        )

        return typing.cast(None, jsii.invoke(self, "putCustomCertificate", [value]))

    @jsii.member(jsii_name="putExtendedEmailMatching")
    def put_extended_email_matching(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        source_account: typing.Optional[builtins.str] = None,
        version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Enable matching all variants of user emails (with + or . modifiers) used as criteria in Firewall policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param read_only: This setting was shared via the Orgs API and cannot be edited by the current account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#read_only ZeroTrustGatewaySettings#read_only}
        :param source_account: Account tag of account that shared this setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#source_account ZeroTrustGatewaySettings#source_account}
        :param version: Version number of the setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#version ZeroTrustGatewaySettings#version}
        '''
        value = ZeroTrustGatewaySettingsSettingsExtendedEmailMatching(
            enabled=enabled,
            read_only=read_only,
            source_account=source_account,
            version=version,
        )

        return typing.cast(None, jsii.invoke(self, "putExtendedEmailMatching", [value]))

    @jsii.member(jsii_name="putFips")
    def put_fips(
        self,
        *,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param tls: Enable only cipher suites and TLS versions compliant with FIPS. 140-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#tls ZeroTrustGatewaySettings#tls}
        '''
        value = ZeroTrustGatewaySettingsSettingsFips(tls=tls)

        return typing.cast(None, jsii.invoke(self, "putFips", [value]))

    @jsii.member(jsii_name="putHostSelector")
    def put_host_selector(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Enable filtering via hosts for egress policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        value = ZeroTrustGatewaySettingsSettingsHostSelector(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putHostSelector", [value]))

    @jsii.member(jsii_name="putInspection")
    def put_inspection(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Defines the mode of inspection the proxy will use. - static: Gateway will use static inspection to inspect HTTP on TCP(80). If TLS decryption is on, Gateway will inspect HTTPS traffic on TCP(443) & UDP(443). - dynamic: Gateway will use protocol detection to dynamically inspect HTTP and HTTPS traffic on any port. TLS decryption must be on to inspect HTTPS traffic. Available values: "static", "dynamic". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#mode ZeroTrustGatewaySettings#mode}
        '''
        value = ZeroTrustGatewaySettingsSettingsInspection(mode=mode)

        return typing.cast(None, jsii.invoke(self, "putInspection", [value]))

    @jsii.member(jsii_name="putProtocolDetection")
    def put_protocol_detection(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Enable detecting protocol on initial bytes of client traffic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        value = ZeroTrustGatewaySettingsSettingsProtocolDetection(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putProtocolDetection", [value]))

    @jsii.member(jsii_name="putSandbox")
    def put_sandbox(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fallback_action: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable sandbox. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param fallback_action: Action to take when the file cannot be scanned. Available values: "allow", "block". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#fallback_action ZeroTrustGatewaySettings#fallback_action}
        '''
        value = ZeroTrustGatewaySettingsSettingsSandbox(
            enabled=enabled, fallback_action=fallback_action
        )

        return typing.cast(None, jsii.invoke(self, "putSandbox", [value]))

    @jsii.member(jsii_name="putTlsDecrypt")
    def put_tls_decrypt(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Enable inspecting encrypted HTTP traffic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        value = ZeroTrustGatewaySettingsSettingsTlsDecrypt(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putTlsDecrypt", [value]))

    @jsii.member(jsii_name="resetActivityLog")
    def reset_activity_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActivityLog", []))

    @jsii.member(jsii_name="resetAntivirus")
    def reset_antivirus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAntivirus", []))

    @jsii.member(jsii_name="resetBlockPage")
    def reset_block_page(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPage", []))

    @jsii.member(jsii_name="resetBodyScanning")
    def reset_body_scanning(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBodyScanning", []))

    @jsii.member(jsii_name="resetBrowserIsolation")
    def reset_browser_isolation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBrowserIsolation", []))

    @jsii.member(jsii_name="resetCertificate")
    def reset_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificate", []))

    @jsii.member(jsii_name="resetCustomCertificate")
    def reset_custom_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomCertificate", []))

    @jsii.member(jsii_name="resetExtendedEmailMatching")
    def reset_extended_email_matching(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtendedEmailMatching", []))

    @jsii.member(jsii_name="resetFips")
    def reset_fips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFips", []))

    @jsii.member(jsii_name="resetHostSelector")
    def reset_host_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostSelector", []))

    @jsii.member(jsii_name="resetInspection")
    def reset_inspection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInspection", []))

    @jsii.member(jsii_name="resetProtocolDetection")
    def reset_protocol_detection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocolDetection", []))

    @jsii.member(jsii_name="resetSandbox")
    def reset_sandbox(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSandbox", []))

    @jsii.member(jsii_name="resetTlsDecrypt")
    def reset_tls_decrypt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsDecrypt", []))

    @builtins.property
    @jsii.member(jsii_name="activityLog")
    def activity_log(
        self,
    ) -> ZeroTrustGatewaySettingsSettingsActivityLogOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsActivityLogOutputReference, jsii.get(self, "activityLog"))

    @builtins.property
    @jsii.member(jsii_name="antivirus")
    def antivirus(self) -> ZeroTrustGatewaySettingsSettingsAntivirusOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsAntivirusOutputReference, jsii.get(self, "antivirus"))

    @builtins.property
    @jsii.member(jsii_name="blockPage")
    def block_page(self) -> ZeroTrustGatewaySettingsSettingsBlockPageOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsBlockPageOutputReference, jsii.get(self, "blockPage"))

    @builtins.property
    @jsii.member(jsii_name="bodyScanning")
    def body_scanning(
        self,
    ) -> ZeroTrustGatewaySettingsSettingsBodyScanningOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsBodyScanningOutputReference, jsii.get(self, "bodyScanning"))

    @builtins.property
    @jsii.member(jsii_name="browserIsolation")
    def browser_isolation(
        self,
    ) -> ZeroTrustGatewaySettingsSettingsBrowserIsolationOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsBrowserIsolationOutputReference, jsii.get(self, "browserIsolation"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> ZeroTrustGatewaySettingsSettingsCertificateOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="customCertificate")
    def custom_certificate(
        self,
    ) -> ZeroTrustGatewaySettingsSettingsCustomCertificateOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsCustomCertificateOutputReference, jsii.get(self, "customCertificate"))

    @builtins.property
    @jsii.member(jsii_name="extendedEmailMatching")
    def extended_email_matching(
        self,
    ) -> ZeroTrustGatewaySettingsSettingsExtendedEmailMatchingOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsExtendedEmailMatchingOutputReference, jsii.get(self, "extendedEmailMatching"))

    @builtins.property
    @jsii.member(jsii_name="fips")
    def fips(self) -> ZeroTrustGatewaySettingsSettingsFipsOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsFipsOutputReference, jsii.get(self, "fips"))

    @builtins.property
    @jsii.member(jsii_name="hostSelector")
    def host_selector(
        self,
    ) -> ZeroTrustGatewaySettingsSettingsHostSelectorOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsHostSelectorOutputReference, jsii.get(self, "hostSelector"))

    @builtins.property
    @jsii.member(jsii_name="inspection")
    def inspection(self) -> ZeroTrustGatewaySettingsSettingsInspectionOutputReference:
        return typing.cast(ZeroTrustGatewaySettingsSettingsInspectionOutputReference, jsii.get(self, "inspection"))

    @builtins.property
    @jsii.member(jsii_name="protocolDetection")
    def protocol_detection(
        self,
    ) -> "ZeroTrustGatewaySettingsSettingsProtocolDetectionOutputReference":
        return typing.cast("ZeroTrustGatewaySettingsSettingsProtocolDetectionOutputReference", jsii.get(self, "protocolDetection"))

    @builtins.property
    @jsii.member(jsii_name="sandbox")
    def sandbox(self) -> "ZeroTrustGatewaySettingsSettingsSandboxOutputReference":
        return typing.cast("ZeroTrustGatewaySettingsSettingsSandboxOutputReference", jsii.get(self, "sandbox"))

    @builtins.property
    @jsii.member(jsii_name="tlsDecrypt")
    def tls_decrypt(
        self,
    ) -> "ZeroTrustGatewaySettingsSettingsTlsDecryptOutputReference":
        return typing.cast("ZeroTrustGatewaySettingsSettingsTlsDecryptOutputReference", jsii.get(self, "tlsDecrypt"))

    @builtins.property
    @jsii.member(jsii_name="activityLogInput")
    def activity_log_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsActivityLog]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsActivityLog]], jsii.get(self, "activityLogInput"))

    @builtins.property
    @jsii.member(jsii_name="antivirusInput")
    def antivirus_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirus]], jsii.get(self, "antivirusInput"))

    @builtins.property
    @jsii.member(jsii_name="blockPageInput")
    def block_page_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBlockPage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBlockPage]], jsii.get(self, "blockPageInput"))

    @builtins.property
    @jsii.member(jsii_name="bodyScanningInput")
    def body_scanning_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBodyScanning]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBodyScanning]], jsii.get(self, "bodyScanningInput"))

    @builtins.property
    @jsii.member(jsii_name="browserIsolationInput")
    def browser_isolation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBrowserIsolation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBrowserIsolation]], jsii.get(self, "browserIsolationInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCertificate]], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="customCertificateInput")
    def custom_certificate_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCustomCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCustomCertificate]], jsii.get(self, "customCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="extendedEmailMatchingInput")
    def extended_email_matching_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsExtendedEmailMatching]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsExtendedEmailMatching]], jsii.get(self, "extendedEmailMatchingInput"))

    @builtins.property
    @jsii.member(jsii_name="fipsInput")
    def fips_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsFips]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsFips]], jsii.get(self, "fipsInput"))

    @builtins.property
    @jsii.member(jsii_name="hostSelectorInput")
    def host_selector_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsHostSelector]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsHostSelector]], jsii.get(self, "hostSelectorInput"))

    @builtins.property
    @jsii.member(jsii_name="inspectionInput")
    def inspection_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsInspection]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsInspection]], jsii.get(self, "inspectionInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolDetectionInput")
    def protocol_detection_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewaySettingsSettingsProtocolDetection"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewaySettingsSettingsProtocolDetection"]], jsii.get(self, "protocolDetectionInput"))

    @builtins.property
    @jsii.member(jsii_name="sandboxInput")
    def sandbox_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewaySettingsSettingsSandbox"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewaySettingsSettingsSandbox"]], jsii.get(self, "sandboxInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsDecryptInput")
    def tls_decrypt_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewaySettingsSettingsTlsDecrypt"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewaySettingsSettingsTlsDecrypt"]], jsii.get(self, "tlsDecryptInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d670afca7a68c4afca27df5926576a27524a1f40cab48ebbd56b3b23f747999)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsProtocolDetection",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ZeroTrustGatewaySettingsSettingsProtocolDetection:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Enable detecting protocol on initial bytes of client traffic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e27be30e14e695ab9387efba4c92bd5079bb72de23b36b1d5af2c4c7b4c23831)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable detecting protocol on initial bytes of client traffic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsProtocolDetection(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsProtocolDetectionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsProtocolDetectionOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f756f87390bdad5210eb936633fc2c2f490ef227411f2f1eb557545533c7844)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73398daa91929734caf2321daef7a3ccc4a94ecf469a29d4135d5187777b767a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsProtocolDetection]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsProtocolDetection]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsProtocolDetection]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d6fa9da02bd87b924b5bc16f439170c768e932ca874bafefd6dec24c1f241ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsSandbox",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "fallback_action": "fallbackAction"},
)
class ZeroTrustGatewaySettingsSettingsSandbox:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fallback_action: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable sandbox. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        :param fallback_action: Action to take when the file cannot be scanned. Available values: "allow", "block". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#fallback_action ZeroTrustGatewaySettings#fallback_action}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c8730e250f82babab254ec9c5b36e9306c8ecf322af086fd1bcd8a77dd8e7e3)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument fallback_action", value=fallback_action, expected_type=type_hints["fallback_action"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if fallback_action is not None:
            self._values["fallback_action"] = fallback_action

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable sandbox.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def fallback_action(self) -> typing.Optional[builtins.str]:
        '''Action to take when the file cannot be scanned. Available values: "allow", "block".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#fallback_action ZeroTrustGatewaySettings#fallback_action}
        '''
        result = self._values.get("fallback_action")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsSandbox(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsSandboxOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsSandboxOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89df01de4a0cbe5f721c951233a89c84c91bf3331804defe589c4a4aa282c4b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetFallbackAction")
    def reset_fallback_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFallbackAction", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="fallbackActionInput")
    def fallback_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fallbackActionInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__320254c450391504011dffab9ad3d0e5b8e5f4305f1673f30f0bfc9ed6c980f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fallbackAction")
    def fallback_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fallbackAction"))

    @fallback_action.setter
    def fallback_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e88197e4b31fca0aae0b449ae760ab31278075d06a0b59f61bd584e97fd9cb50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallbackAction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsSandbox]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsSandbox]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsSandbox]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b821cac8c081051fa4d1c605828dc3d45d49c0e3d82daf51df52b69358347df3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsTlsDecrypt",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ZeroTrustGatewaySettingsSettingsTlsDecrypt:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Enable inspecting encrypted HTTP traffic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a61d4145042bc59b82e785c6e2d017a1e67c1b4b2599a2798b1d1c170adc11e)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable inspecting encrypted HTTP traffic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_settings#enabled ZeroTrustGatewaySettings#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewaySettingsSettingsTlsDecrypt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewaySettingsSettingsTlsDecryptOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewaySettings.ZeroTrustGatewaySettingsSettingsTlsDecryptOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__065e338bb7e867ac047624afd3b387faa96161898d4d74c3ae94d53dad7d567b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c510d4ea9c782ba3bb23d6f0005e85bec9aef3feb87af1c46037e4fe5d4e8b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsTlsDecrypt]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsTlsDecrypt]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsTlsDecrypt]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c73c4422679b5aa2644a648655471fca36a3a97207dd80d38256668385618feb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustGatewaySettings",
    "ZeroTrustGatewaySettingsConfig",
    "ZeroTrustGatewaySettingsSettings",
    "ZeroTrustGatewaySettingsSettingsActivityLog",
    "ZeroTrustGatewaySettingsSettingsActivityLogOutputReference",
    "ZeroTrustGatewaySettingsSettingsAntivirus",
    "ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings",
    "ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettingsOutputReference",
    "ZeroTrustGatewaySettingsSettingsAntivirusOutputReference",
    "ZeroTrustGatewaySettingsSettingsBlockPage",
    "ZeroTrustGatewaySettingsSettingsBlockPageOutputReference",
    "ZeroTrustGatewaySettingsSettingsBodyScanning",
    "ZeroTrustGatewaySettingsSettingsBodyScanningOutputReference",
    "ZeroTrustGatewaySettingsSettingsBrowserIsolation",
    "ZeroTrustGatewaySettingsSettingsBrowserIsolationOutputReference",
    "ZeroTrustGatewaySettingsSettingsCertificate",
    "ZeroTrustGatewaySettingsSettingsCertificateOutputReference",
    "ZeroTrustGatewaySettingsSettingsCustomCertificate",
    "ZeroTrustGatewaySettingsSettingsCustomCertificateOutputReference",
    "ZeroTrustGatewaySettingsSettingsExtendedEmailMatching",
    "ZeroTrustGatewaySettingsSettingsExtendedEmailMatchingOutputReference",
    "ZeroTrustGatewaySettingsSettingsFips",
    "ZeroTrustGatewaySettingsSettingsFipsOutputReference",
    "ZeroTrustGatewaySettingsSettingsHostSelector",
    "ZeroTrustGatewaySettingsSettingsHostSelectorOutputReference",
    "ZeroTrustGatewaySettingsSettingsInspection",
    "ZeroTrustGatewaySettingsSettingsInspectionOutputReference",
    "ZeroTrustGatewaySettingsSettingsOutputReference",
    "ZeroTrustGatewaySettingsSettingsProtocolDetection",
    "ZeroTrustGatewaySettingsSettingsProtocolDetectionOutputReference",
    "ZeroTrustGatewaySettingsSettingsSandbox",
    "ZeroTrustGatewaySettingsSettingsSandboxOutputReference",
    "ZeroTrustGatewaySettingsSettingsTlsDecrypt",
    "ZeroTrustGatewaySettingsSettingsTlsDecryptOutputReference",
]

publication.publish()

def _typecheckingstub__e835aa6c5393b3bccb9f3757aa1cc8e34cee2d7a93e870dce8110f777030091f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    settings: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettings, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__b6a9c540ee48d79bc94bf225d2e7f3d25e0fad690ba5931d93c9793a03c42dc5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5f323899588c0d92313196544d971a5ad585faf1ae29ee162ace9408ebbf9a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__322ff5308daf0c47711318ff672028d3699332013934aecc39310a2adc383991(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    settings: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f715ae0595e07919931305acd2a07ddefb2bfc0489ff466af13f6bd6f96bd7af(
    *,
    activity_log: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsActivityLog, typing.Dict[builtins.str, typing.Any]]] = None,
    antivirus: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsAntivirus, typing.Dict[builtins.str, typing.Any]]] = None,
    block_page: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsBlockPage, typing.Dict[builtins.str, typing.Any]]] = None,
    body_scanning: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsBodyScanning, typing.Dict[builtins.str, typing.Any]]] = None,
    browser_isolation: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsBrowserIsolation, typing.Dict[builtins.str, typing.Any]]] = None,
    certificate: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_certificate: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsCustomCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    extended_email_matching: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsExtendedEmailMatching, typing.Dict[builtins.str, typing.Any]]] = None,
    fips: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsFips, typing.Dict[builtins.str, typing.Any]]] = None,
    host_selector: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsHostSelector, typing.Dict[builtins.str, typing.Any]]] = None,
    inspection: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsInspection, typing.Dict[builtins.str, typing.Any]]] = None,
    protocol_detection: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsProtocolDetection, typing.Dict[builtins.str, typing.Any]]] = None,
    sandbox: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsSandbox, typing.Dict[builtins.str, typing.Any]]] = None,
    tls_decrypt: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsTlsDecrypt, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__449048db3b5d9cc23c492ddb4c651230efd72fc1a90d3e16fe1686f4d2c60098(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4fa3909832a7ff672424f0ab4081c71f48a94f81bbc2778053a5b0aabbccf9e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c837e5d867e238d3da2c463839e71e18382f9d88473d25a65d8e683b1c329a30(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__935721b3effc640937a977b286ddd90734f69f3b7234da1c7a56463e36856978(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsActivityLog]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__debc1555f7ea4284a087279cc6d87e0a641cb02e6717b65ead0d58b0d5b3c50f(
    *,
    enabled_download_phase: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled_upload_phase: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fail_closed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    notification_settings: typing.Optional[typing.Union[ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e7391ec28d597088189b0d496dfa49feafde4f72eaf7ba2e5c731ab5a78bae0(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    msg: typing.Optional[builtins.str] = None,
    support_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c62aa0dd553fa1dd819abb33ebe667327874d2f7ded9d4a6f464be9077e94bd6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6283e752b2738ce11e2554316725fbbe44bf1ca2d1645845dad34d25be3025d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e8e93a5a41f42da1d2564ee33149e7d39d9f7cc916492d1950495702769a585(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab77cb20c4ce9d5c1afd25979f2d7714c38c3f4c196910ee18fbdf59834f7e99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddac3c62e77742256b5ed57a9cd76f5eea902c77d2a8907c226096c232f4bec5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a3fc0ade33c685c1763796088c60b714da417a8f19105e431a19a91aa756034(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirusNotificationSettings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f3aba34ab57cc12f9785afda930f06c47ac3f1663b9a4fd1425ac992171197b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72daabf3c9eed1a5c18fc388ff6171bb09c25f9464d64296d10f150226541c08(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80cc72128944aa13676730862080d5f7190e2082f5a6475ae04c1eee6f18ab95(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21a77565f7f9d89fb015331f3370a3fa4dbf7108125ea7d04d6a52a975c49536(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f03bddab5ab625ecc1c98d597818ad48bb8080624bffc4524093599d22fca6e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsAntivirus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6e87cdd5d37df790937259a5800085b17678f0d78a36aae00df49e610ee491a(
    *,
    background_color: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    footer_text: typing.Optional[builtins.str] = None,
    header_text: typing.Optional[builtins.str] = None,
    include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    logo_path: typing.Optional[builtins.str] = None,
    mailto_address: typing.Optional[builtins.str] = None,
    mailto_subject: typing.Optional[builtins.str] = None,
    mode: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    source_account: typing.Optional[builtins.str] = None,
    suppress_footer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    target_uri: typing.Optional[builtins.str] = None,
    version: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaaae33322b392eb56bb40c10206640556b9e9f13fd29ce17c72f729541384c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7ef1784c3fa794018174c38ac92bcc0693826ac0658859324983669f5a461cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccff18927fb243b4d7a1e7662e44574facb1c036291780184f099de618ae4d68(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b428c5b1ff05690d92b5944ca295191de65e1740e2189f7e3114a8013f8bb114(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__151657b4e992cf771213b989606bcb5421a6618c697cf8b151c7ea6742454538(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2a40c133514a334f322411a5a4a94c2127d9701c7bd2370ba5a2f9c5a80fa10(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbc821a62689b9ed9fe43a3127ac8b0973aa0830b12166008d3998b72bb70c73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8adc75b927f097ca1707ba6596b8f37691ad5f24d25ad89d85a3d303217fb897(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__584a7dd956fa650ec15a800d8f4823dc147a2605051918328755dd1ae2795718(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2df23eb095f408c22af3f5e7ff229a4a86923c9b74684f59d5dafd5c663e14b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f67b12449ae4601985cdd82440d5695c4ad216a11c63c76a4734da9a31c3fbfe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47f6955a1756a0fa58dba4fb03b16daa8412e8c847e4309a0f4c6a128886e136(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00dc919dacfbfbe5c1d961f27133b1f05a9a1e3dc71440d5e57229d2f398bccf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__170a63e578b422a42c0031bad6e3cd0d9773224888b0c3f47b58bd10ece621a0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab01167783c6e0bfc0c07ecc1955478c026814afe7ac0bef0685374a72eed854(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1747d6586d9310a91a2b262eb788e609ed05fa5f8c4cbad9524c3e6d22f561b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__804c5935b681b27181cf8352eeaf1d18b4c7058f7370518ca1fc18f41391427a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBlockPage]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__973ad4d19e5aae6235b568364c5781b621151f19f39ddfa064da743b0b6dd9b3(
    *,
    inspection_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3928af4182102fd1a91b4a8cb4296b80087237f7d298409eab06dca4e412b182(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c13622f7f1e03389c9eb968eb77ab826ca1bb826e94206f1c9636c490e82e86f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c44470f741fe91ebe3a71cb44674eda3a76cbd302368a9b9741b335557eb1ef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBodyScanning]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23ac38400d65f804c8df06e5d0c3b1b0d41dfed5be2fe704efac4498101cc026(
    *,
    non_identity_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    url_browser_isolation_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27e0add587729700dbef6d2bef091ba44c7d2d051876bb0bee45d42dac5fa00f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53b6de3707fad24ea3db01301e5111d38fb3ad949f0200f5379efcee0e404990(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6e69bf66acd5a67fd915140ab425e9b535d1d4fa8a6696814e952ae289b5ec2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20b915eaa751dd035e0a2f9c55af9fe61d6ef1e09b52127c70416c89d1ef7ec8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsBrowserIsolation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acd1c1b7d41a1878bc2fb86e48dc25d1747cc9ba00a53185e6f4044af1d7b966(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ac7ba0d482a07ca8c2c4b6448aa63327fd14ff0d36087dc645f212f5300bdd8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05d413708c953104b7f1abc33eb05fa218102e5f6590a3b7e0836188a487525a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d40cc7eedd8c13292651312c4f220052df63b3f3c19f3c0911daab02fae12022(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCertificate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07e4bf8521ecb98720f42862693ea97f0be075228e6bf59f3a6c1e0c8a9f27f5(
    *,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    binding_status: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    updated_at: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52e65a55b71741e1237ed07a3557c30b451119c06b7bf2bf4734ab9e07ee6e76(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3849e370b812e6447e390fc67ea9bc6041015bd073c713c772b53178254a16d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a999e277bd2e41e8059dea75ace31f9e40e74fd2b55d1c81fe0bf4a4e3e522f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da91c39005c5db206fd2ad3706fe203292a04187ca8695dd01412d5db679056f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54d91b9c4cae66ef4043799fa42c859159e70a5ff3ee9e19a371ea08d451bcf8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a83269bee907fc41f45e81d8e10ee1370b725a3bc65fa1b7927aa4c86d97ff4e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsCustomCertificate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60fc447be0ddd4b0584db955ef229645d061fcac94befe700eaa7a3325b78ec6(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    source_account: typing.Optional[builtins.str] = None,
    version: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13a5e25560d64fa0ab87b5253c47c68b17989c540ffc69a5b9d022b608e6a2df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__747d784829ec35ae1444f341cf38930a9f731f4424954fd5a8b0eb96f8ced12c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1700fe273f491be575a8790e033f491a60b0eb0f7b770134c65cf03ae3f41df8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2e6c971bda96295661e96aa142f81f7f7afad83105bb6f370606068609e6999(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cf03622941a305a79f2ed40dcd8947bfb8b69cc932e5fe4a23c62af6e45b75c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4989154c08c2599532f65d2860e87ddf8c4b60bf1c8046ec674ed9c5dbc5a6a4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsExtendedEmailMatching]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a80f7f1916c83178f0a7cc209122a5d6cce2fbc4458ac460ca9eda36f4df711(
    *,
    tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__290eee58dd090a54751b58670a660ea57ab4efcba3b81efa24840bb26408b93b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e894ada4735d6b96fe10e3e967e16e647ab4eeed07887fe63af09fa73db2591(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd11d6fff29851eda47ca45a202abc5f0fa01c14caf282b3ed41df8a50a3e99f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsFips]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f06e24935b71e689908e73b5ede262bd75b4ed2e9b33003d537112efb75aec(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70faefaa614c3101c801fe59a585003bdd6a382b22bc0618f1277ac1f31c4e8b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9ffdd1de5473ada98800b8201f648ca111228f84af9146b50f2e88ac57dd331(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78a940c106541741b4c9db5048b113396483a07bee00dd4ff3928f98d209b1f7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsHostSelector]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ed21a93616261f51830ff4df77cd96334ef745849efc6250f96fe67ae5a8cbe(
    *,
    mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d17b7b51064ec1171a0b95412ce914d7936a80e29c0aa8d703956e41f2563b5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13ad9a2445874df91af853f6f01def069dc443f4a5f2cac54f509812b18c9089(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__904bbf4bd20573e4afca0c6d1b3e505b4f65c71b3dbcb7fdf07918ab523fa883(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsInspection]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__357d4e585509b33d8043922ef652f4b0822b041eec63f3f2e8e1ac2361babd37(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d670afca7a68c4afca27df5926576a27524a1f40cab48ebbd56b3b23f747999(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e27be30e14e695ab9387efba4c92bd5079bb72de23b36b1d5af2c4c7b4c23831(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f756f87390bdad5210eb936633fc2c2f490ef227411f2f1eb557545533c7844(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73398daa91929734caf2321daef7a3ccc4a94ecf469a29d4135d5187777b767a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d6fa9da02bd87b924b5bc16f439170c768e932ca874bafefd6dec24c1f241ef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsProtocolDetection]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c8730e250f82babab254ec9c5b36e9306c8ecf322af086fd1bcd8a77dd8e7e3(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fallback_action: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89df01de4a0cbe5f721c951233a89c84c91bf3331804defe589c4a4aa282c4b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__320254c450391504011dffab9ad3d0e5b8e5f4305f1673f30f0bfc9ed6c980f1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e88197e4b31fca0aae0b449ae760ab31278075d06a0b59f61bd584e97fd9cb50(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b821cac8c081051fa4d1c605828dc3d45d49c0e3d82daf51df52b69358347df3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsSandbox]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a61d4145042bc59b82e785c6e2d017a1e67c1b4b2599a2798b1d1c170adc11e(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__065e338bb7e867ac047624afd3b387faa96161898d4d74c3ae94d53dad7d567b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c510d4ea9c782ba3bb23d6f0005e85bec9aef3feb87af1c46037e4fe5d4e8b4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c73c4422679b5aa2644a648655471fca36a3a97207dd80d38256668385618feb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewaySettingsSettingsTlsDecrypt]],
) -> None:
    """Type checking stubs"""
    pass
