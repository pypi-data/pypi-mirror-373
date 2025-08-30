r'''
# `cloudflare_zero_trust_device_custom_profile`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_device_custom_profile`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile).
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


class ZeroTrustDeviceCustomProfile(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfile",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile cloudflare_zero_trust_device_custom_profile}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        match: builtins.str,
        name: builtins.str,
        precedence: jsii.Number,
        allowed_to_leave: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mode_switch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_updates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_connect: typing.Optional[jsii.Number] = None,
        captive_portal: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        disable_auto_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceCustomProfileExclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        exclude_office_ips: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceCustomProfileInclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        lan_allow_minutes: typing.Optional[jsii.Number] = None,
        lan_allow_subnet_size: typing.Optional[jsii.Number] = None,
        register_interface_ip_with_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sccm_vpn_boundary_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_mode_v2: typing.Optional[typing.Union["ZeroTrustDeviceCustomProfileServiceModeV2", typing.Dict[builtins.str, typing.Any]]] = None,
        support_url: typing.Optional[builtins.str] = None,
        switch_locked: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tunnel_protocol: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile cloudflare_zero_trust_device_custom_profile} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#account_id ZeroTrustDeviceCustomProfile#account_id}.
        :param match: The wirefilter expression to match devices. Available values: "identity.email", "identity.groups.id", "identity.groups.name", "identity.groups.email", "identity.service_token_uuid", "identity.saml_attributes", "network", "os.name", "os.version". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#match ZeroTrustDeviceCustomProfile#match}
        :param name: The name of the device settings profile. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#name ZeroTrustDeviceCustomProfile#name}
        :param precedence: The precedence of the policy. Lower values indicate higher precedence. Policies will be evaluated in ascending order of this field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#precedence ZeroTrustDeviceCustomProfile#precedence}
        :param allowed_to_leave: Whether to allow devices to leave the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#allowed_to_leave ZeroTrustDeviceCustomProfile#allowed_to_leave}
        :param allow_mode_switch: Whether to allow the user to switch WARP between modes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#allow_mode_switch ZeroTrustDeviceCustomProfile#allow_mode_switch}
        :param allow_updates: Whether to receive update notifications when a new version of the client is available. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#allow_updates ZeroTrustDeviceCustomProfile#allow_updates}
        :param auto_connect: The amount of time in seconds to reconnect after having been disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#auto_connect ZeroTrustDeviceCustomProfile#auto_connect}
        :param captive_portal: Turn on the captive portal after the specified amount of time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#captive_portal ZeroTrustDeviceCustomProfile#captive_portal}
        :param description: A description of the policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#description ZeroTrustDeviceCustomProfile#description}
        :param disable_auto_fallback: If the ``dns_server`` field of a fallback domain is not present, the client will fall back to a best guess of the default/system DNS resolvers unless this policy option is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#disable_auto_fallback ZeroTrustDeviceCustomProfile#disable_auto_fallback}
        :param enabled: Whether the policy will be applied to matching devices. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#enabled ZeroTrustDeviceCustomProfile#enabled}
        :param exclude: List of routes excluded in the WARP client's tunnel. Both 'exclude' and 'include' cannot be set in the same request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#exclude ZeroTrustDeviceCustomProfile#exclude}
        :param exclude_office_ips: Whether to add Microsoft IPs to Split Tunnel exclusions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#exclude_office_ips ZeroTrustDeviceCustomProfile#exclude_office_ips}
        :param include: List of routes included in the WARP client's tunnel. Both 'exclude' and 'include' cannot be set in the same request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#include ZeroTrustDeviceCustomProfile#include}
        :param lan_allow_minutes: The amount of time in minutes a user is allowed access to their LAN. A value of 0 will allow LAN access until the next WARP reconnection, such as a reboot or a laptop waking from sleep. Note that this field is omitted from the response if null or unset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#lan_allow_minutes ZeroTrustDeviceCustomProfile#lan_allow_minutes}
        :param lan_allow_subnet_size: The size of the subnet for the local access network. Note that this field is omitted from the response if null or unset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#lan_allow_subnet_size ZeroTrustDeviceCustomProfile#lan_allow_subnet_size}
        :param register_interface_ip_with_dns: Determines if the operating system will register WARP's local interface IP with your on-premises DNS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#register_interface_ip_with_dns ZeroTrustDeviceCustomProfile#register_interface_ip_with_dns}
        :param sccm_vpn_boundary_support: Determines whether the WARP client indicates to SCCM that it is inside a VPN boundary. (Windows only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#sccm_vpn_boundary_support ZeroTrustDeviceCustomProfile#sccm_vpn_boundary_support}
        :param service_mode_v2: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#service_mode_v2 ZeroTrustDeviceCustomProfile#service_mode_v2}.
        :param support_url: The URL to launch when the Send Feedback button is clicked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#support_url ZeroTrustDeviceCustomProfile#support_url}
        :param switch_locked: Whether to allow the user to turn off the WARP switch and disconnect the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#switch_locked ZeroTrustDeviceCustomProfile#switch_locked}
        :param tunnel_protocol: Determines which tunnel protocol to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#tunnel_protocol ZeroTrustDeviceCustomProfile#tunnel_protocol}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__892750ee6d327436d674cc96685cdf3198c07378abd461534011e7b6013d7951)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustDeviceCustomProfileConfig(
            account_id=account_id,
            match=match,
            name=name,
            precedence=precedence,
            allowed_to_leave=allowed_to_leave,
            allow_mode_switch=allow_mode_switch,
            allow_updates=allow_updates,
            auto_connect=auto_connect,
            captive_portal=captive_portal,
            description=description,
            disable_auto_fallback=disable_auto_fallback,
            enabled=enabled,
            exclude=exclude,
            exclude_office_ips=exclude_office_ips,
            include=include,
            lan_allow_minutes=lan_allow_minutes,
            lan_allow_subnet_size=lan_allow_subnet_size,
            register_interface_ip_with_dns=register_interface_ip_with_dns,
            sccm_vpn_boundary_support=sccm_vpn_boundary_support,
            service_mode_v2=service_mode_v2,
            support_url=support_url,
            switch_locked=switch_locked,
            tunnel_protocol=tunnel_protocol,
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
        '''Generates CDKTF code for importing a ZeroTrustDeviceCustomProfile resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustDeviceCustomProfile to import.
        :param import_from_id: The id of the existing ZeroTrustDeviceCustomProfile that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustDeviceCustomProfile to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1289fc35564713d5332d8089635fad7ecd71e893dcf66ee937731d05e570d29)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putExclude")
    def put_exclude(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceCustomProfileExclude", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a8b645f5ba47e750d5e657534f404d9392a36f339819125f1137ed1bbc7f9cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExclude", [value]))

    @jsii.member(jsii_name="putInclude")
    def put_include(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceCustomProfileInclude", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42c3c0bef0a3caa7223598740369d2d5a6000156ad1f53067508afcdabc9e219)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInclude", [value]))

    @jsii.member(jsii_name="putServiceModeV2")
    def put_service_mode_v2(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mode: The mode to run the WARP client under. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#mode ZeroTrustDeviceCustomProfile#mode}
        :param port: The port number when used with proxy mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#port ZeroTrustDeviceCustomProfile#port}
        '''
        value = ZeroTrustDeviceCustomProfileServiceModeV2(mode=mode, port=port)

        return typing.cast(None, jsii.invoke(self, "putServiceModeV2", [value]))

    @jsii.member(jsii_name="resetAllowedToLeave")
    def reset_allowed_to_leave(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedToLeave", []))

    @jsii.member(jsii_name="resetAllowModeSwitch")
    def reset_allow_mode_switch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowModeSwitch", []))

    @jsii.member(jsii_name="resetAllowUpdates")
    def reset_allow_updates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowUpdates", []))

    @jsii.member(jsii_name="resetAutoConnect")
    def reset_auto_connect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoConnect", []))

    @jsii.member(jsii_name="resetCaptivePortal")
    def reset_captive_portal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaptivePortal", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisableAutoFallback")
    def reset_disable_auto_fallback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableAutoFallback", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetExclude")
    def reset_exclude(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExclude", []))

    @jsii.member(jsii_name="resetExcludeOfficeIps")
    def reset_exclude_office_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeOfficeIps", []))

    @jsii.member(jsii_name="resetInclude")
    def reset_include(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInclude", []))

    @jsii.member(jsii_name="resetLanAllowMinutes")
    def reset_lan_allow_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLanAllowMinutes", []))

    @jsii.member(jsii_name="resetLanAllowSubnetSize")
    def reset_lan_allow_subnet_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLanAllowSubnetSize", []))

    @jsii.member(jsii_name="resetRegisterInterfaceIpWithDns")
    def reset_register_interface_ip_with_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegisterInterfaceIpWithDns", []))

    @jsii.member(jsii_name="resetSccmVpnBoundarySupport")
    def reset_sccm_vpn_boundary_support(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSccmVpnBoundarySupport", []))

    @jsii.member(jsii_name="resetServiceModeV2")
    def reset_service_mode_v2(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceModeV2", []))

    @jsii.member(jsii_name="resetSupportUrl")
    def reset_support_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportUrl", []))

    @jsii.member(jsii_name="resetSwitchLocked")
    def reset_switch_locked(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSwitchLocked", []))

    @jsii.member(jsii_name="resetTunnelProtocol")
    def reset_tunnel_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTunnelProtocol", []))

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
    @jsii.member(jsii_name="default")
    def default(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "default"))

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> "ZeroTrustDeviceCustomProfileExcludeList":
        return typing.cast("ZeroTrustDeviceCustomProfileExcludeList", jsii.get(self, "exclude"))

    @builtins.property
    @jsii.member(jsii_name="fallbackDomains")
    def fallback_domains(self) -> "ZeroTrustDeviceCustomProfileFallbackDomainsList":
        return typing.cast("ZeroTrustDeviceCustomProfileFallbackDomainsList", jsii.get(self, "fallbackDomains"))

    @builtins.property
    @jsii.member(jsii_name="gatewayUniqueId")
    def gateway_unique_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayUniqueId"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> "ZeroTrustDeviceCustomProfileIncludeList":
        return typing.cast("ZeroTrustDeviceCustomProfileIncludeList", jsii.get(self, "include"))

    @builtins.property
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @builtins.property
    @jsii.member(jsii_name="serviceModeV2")
    def service_mode_v2(
        self,
    ) -> "ZeroTrustDeviceCustomProfileServiceModeV2OutputReference":
        return typing.cast("ZeroTrustDeviceCustomProfileServiceModeV2OutputReference", jsii.get(self, "serviceModeV2"))

    @builtins.property
    @jsii.member(jsii_name="targetTests")
    def target_tests(self) -> "ZeroTrustDeviceCustomProfileTargetTestsList":
        return typing.cast("ZeroTrustDeviceCustomProfileTargetTestsList", jsii.get(self, "targetTests"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedToLeaveInput")
    def allowed_to_leave_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowedToLeaveInput"))

    @builtins.property
    @jsii.member(jsii_name="allowModeSwitchInput")
    def allow_mode_switch_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowModeSwitchInput"))

    @builtins.property
    @jsii.member(jsii_name="allowUpdatesInput")
    def allow_updates_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowUpdatesInput"))

    @builtins.property
    @jsii.member(jsii_name="autoConnectInput")
    def auto_connect_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autoConnectInput"))

    @builtins.property
    @jsii.member(jsii_name="captivePortalInput")
    def captive_portal_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "captivePortalInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="disableAutoFallbackInput")
    def disable_auto_fallback_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableAutoFallbackInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeInput")
    def exclude_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceCustomProfileExclude"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceCustomProfileExclude"]]], jsii.get(self, "excludeInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeOfficeIpsInput")
    def exclude_office_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "excludeOfficeIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="includeInput")
    def include_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceCustomProfileInclude"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceCustomProfileInclude"]]], jsii.get(self, "includeInput"))

    @builtins.property
    @jsii.member(jsii_name="lanAllowMinutesInput")
    def lan_allow_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lanAllowMinutesInput"))

    @builtins.property
    @jsii.member(jsii_name="lanAllowSubnetSizeInput")
    def lan_allow_subnet_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lanAllowSubnetSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="matchInput")
    def match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "matchInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="precedenceInput")
    def precedence_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "precedenceInput"))

    @builtins.property
    @jsii.member(jsii_name="registerInterfaceIpWithDnsInput")
    def register_interface_ip_with_dns_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "registerInterfaceIpWithDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="sccmVpnBoundarySupportInput")
    def sccm_vpn_boundary_support_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sccmVpnBoundarySupportInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceModeV2Input")
    def service_mode_v2_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustDeviceCustomProfileServiceModeV2"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustDeviceCustomProfileServiceModeV2"]], jsii.get(self, "serviceModeV2Input"))

    @builtins.property
    @jsii.member(jsii_name="supportUrlInput")
    def support_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "supportUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="switchLockedInput")
    def switch_locked_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "switchLockedInput"))

    @builtins.property
    @jsii.member(jsii_name="tunnelProtocolInput")
    def tunnel_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tunnelProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49eb9703ac6f2199ee23f0961c889dc829a32a84c5bded92bebc959c6e40c465)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedToLeave")
    def allowed_to_leave(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowedToLeave"))

    @allowed_to_leave.setter
    def allowed_to_leave(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24348761c54c8edd0078b37492c5d715c61434f940d1e6bed0b85b7c46da1fe9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedToLeave", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowModeSwitch")
    def allow_mode_switch(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowModeSwitch"))

    @allow_mode_switch.setter
    def allow_mode_switch(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f8a35af70bb4320482ce9784f94cf9f556c1e0955efe2cd0c7fa7fbbcc6212a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowModeSwitch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowUpdates")
    def allow_updates(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowUpdates"))

    @allow_updates.setter
    def allow_updates(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e57f0d7340907ed153b523259e68cc75bb7e5e78f300db4a619db40fe308cc13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowUpdates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoConnect")
    def auto_connect(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoConnect"))

    @auto_connect.setter
    def auto_connect(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7971b0feee9ad5e743b92fe16bbc7d79498acd11f6369ea84650a42804794351)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoConnect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="captivePortal")
    def captive_portal(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "captivePortal"))

    @captive_portal.setter
    def captive_portal(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdaaca05bd413a28892ef111f9b833e1b38fb7b89f0125270a2ee6936c4734e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "captivePortal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e1069bf3fa8aa5adea5c7e988c0966fd26932f06364491f0c347e38d82e9deb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableAutoFallback")
    def disable_auto_fallback(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableAutoFallback"))

    @disable_auto_fallback.setter
    def disable_auto_fallback(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc9c17712ef6b9b997d5320dddf93d92e00380c305aebf5079b0f754bb153f06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableAutoFallback", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__83aa891f845b877d1eea049d8b221578a0fb3785a28440edd2e990198057c8cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludeOfficeIps")
    def exclude_office_ips(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "excludeOfficeIps"))

    @exclude_office_ips.setter
    def exclude_office_ips(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53b7ce9590f70881caba538b136a0dd93e319072deb7aadb21bf607627dc6d7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeOfficeIps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lanAllowMinutes")
    def lan_allow_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lanAllowMinutes"))

    @lan_allow_minutes.setter
    def lan_allow_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e0be2eac7d36ee9aeb73e79f03384017ab9b27ee6efe14b0036c1ee379655af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanAllowMinutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lanAllowSubnetSize")
    def lan_allow_subnet_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lanAllowSubnetSize"))

    @lan_allow_subnet_size.setter
    def lan_allow_subnet_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2da28304784b1279913a4ea747aa0f0bd3fe76645206b76ff5172ee087afa03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanAllowSubnetSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="match")
    def match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "match"))

    @match.setter
    def match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a259a8fcbefb0f4ee27c74217093ea63dbc30d64718829e31fae177f9c5f4a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "match", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3abda7e726a69b65d7cfc0d3faf0be5e33afecc5dc215c733b505f3fcb178c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="precedence")
    def precedence(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precedence"))

    @precedence.setter
    def precedence(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3d793f208f985aa13fbe7c6cb7e21f22bf51c75eea65d9cd721769af4cf5e21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "precedence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="registerInterfaceIpWithDns")
    def register_interface_ip_with_dns(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "registerInterfaceIpWithDns"))

    @register_interface_ip_with_dns.setter
    def register_interface_ip_with_dns(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53e4528eabcdd4d6d8b923061e976cb5f97809b79cfa6d0f2c2c7abfab76f4b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "registerInterfaceIpWithDns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sccmVpnBoundarySupport")
    def sccm_vpn_boundary_support(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "sccmVpnBoundarySupport"))

    @sccm_vpn_boundary_support.setter
    def sccm_vpn_boundary_support(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd7539b82e137348881321ce471643ebaf5a64b5ce6e7d5df5ec2e81776f3a39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sccmVpnBoundarySupport", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="supportUrl")
    def support_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "supportUrl"))

    @support_url.setter
    def support_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a888107e12522d9cda66cd89f363486ff39ac56540ca229a2be85c517bdb460)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "supportUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="switchLocked")
    def switch_locked(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "switchLocked"))

    @switch_locked.setter
    def switch_locked(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__895f7ffa0b0d79621dba88174350516d65ad2799e6328f22c3611e8a595135cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "switchLocked", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tunnelProtocol")
    def tunnel_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tunnelProtocol"))

    @tunnel_protocol.setter
    def tunnel_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb60a72db627a6b0fee55af2d5fb5b8d5f28359bc8d7101dfbe5e24627a32b34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tunnelProtocol", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileConfig",
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
        "match": "match",
        "name": "name",
        "precedence": "precedence",
        "allowed_to_leave": "allowedToLeave",
        "allow_mode_switch": "allowModeSwitch",
        "allow_updates": "allowUpdates",
        "auto_connect": "autoConnect",
        "captive_portal": "captivePortal",
        "description": "description",
        "disable_auto_fallback": "disableAutoFallback",
        "enabled": "enabled",
        "exclude": "exclude",
        "exclude_office_ips": "excludeOfficeIps",
        "include": "include",
        "lan_allow_minutes": "lanAllowMinutes",
        "lan_allow_subnet_size": "lanAllowSubnetSize",
        "register_interface_ip_with_dns": "registerInterfaceIpWithDns",
        "sccm_vpn_boundary_support": "sccmVpnBoundarySupport",
        "service_mode_v2": "serviceModeV2",
        "support_url": "supportUrl",
        "switch_locked": "switchLocked",
        "tunnel_protocol": "tunnelProtocol",
    },
)
class ZeroTrustDeviceCustomProfileConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        match: builtins.str,
        name: builtins.str,
        precedence: jsii.Number,
        allowed_to_leave: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mode_switch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_updates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_connect: typing.Optional[jsii.Number] = None,
        captive_portal: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        disable_auto_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceCustomProfileExclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        exclude_office_ips: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceCustomProfileInclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        lan_allow_minutes: typing.Optional[jsii.Number] = None,
        lan_allow_subnet_size: typing.Optional[jsii.Number] = None,
        register_interface_ip_with_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sccm_vpn_boundary_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_mode_v2: typing.Optional[typing.Union["ZeroTrustDeviceCustomProfileServiceModeV2", typing.Dict[builtins.str, typing.Any]]] = None,
        support_url: typing.Optional[builtins.str] = None,
        switch_locked: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tunnel_protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#account_id ZeroTrustDeviceCustomProfile#account_id}.
        :param match: The wirefilter expression to match devices. Available values: "identity.email", "identity.groups.id", "identity.groups.name", "identity.groups.email", "identity.service_token_uuid", "identity.saml_attributes", "network", "os.name", "os.version". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#match ZeroTrustDeviceCustomProfile#match}
        :param name: The name of the device settings profile. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#name ZeroTrustDeviceCustomProfile#name}
        :param precedence: The precedence of the policy. Lower values indicate higher precedence. Policies will be evaluated in ascending order of this field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#precedence ZeroTrustDeviceCustomProfile#precedence}
        :param allowed_to_leave: Whether to allow devices to leave the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#allowed_to_leave ZeroTrustDeviceCustomProfile#allowed_to_leave}
        :param allow_mode_switch: Whether to allow the user to switch WARP between modes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#allow_mode_switch ZeroTrustDeviceCustomProfile#allow_mode_switch}
        :param allow_updates: Whether to receive update notifications when a new version of the client is available. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#allow_updates ZeroTrustDeviceCustomProfile#allow_updates}
        :param auto_connect: The amount of time in seconds to reconnect after having been disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#auto_connect ZeroTrustDeviceCustomProfile#auto_connect}
        :param captive_portal: Turn on the captive portal after the specified amount of time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#captive_portal ZeroTrustDeviceCustomProfile#captive_portal}
        :param description: A description of the policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#description ZeroTrustDeviceCustomProfile#description}
        :param disable_auto_fallback: If the ``dns_server`` field of a fallback domain is not present, the client will fall back to a best guess of the default/system DNS resolvers unless this policy option is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#disable_auto_fallback ZeroTrustDeviceCustomProfile#disable_auto_fallback}
        :param enabled: Whether the policy will be applied to matching devices. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#enabled ZeroTrustDeviceCustomProfile#enabled}
        :param exclude: List of routes excluded in the WARP client's tunnel. Both 'exclude' and 'include' cannot be set in the same request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#exclude ZeroTrustDeviceCustomProfile#exclude}
        :param exclude_office_ips: Whether to add Microsoft IPs to Split Tunnel exclusions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#exclude_office_ips ZeroTrustDeviceCustomProfile#exclude_office_ips}
        :param include: List of routes included in the WARP client's tunnel. Both 'exclude' and 'include' cannot be set in the same request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#include ZeroTrustDeviceCustomProfile#include}
        :param lan_allow_minutes: The amount of time in minutes a user is allowed access to their LAN. A value of 0 will allow LAN access until the next WARP reconnection, such as a reboot or a laptop waking from sleep. Note that this field is omitted from the response if null or unset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#lan_allow_minutes ZeroTrustDeviceCustomProfile#lan_allow_minutes}
        :param lan_allow_subnet_size: The size of the subnet for the local access network. Note that this field is omitted from the response if null or unset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#lan_allow_subnet_size ZeroTrustDeviceCustomProfile#lan_allow_subnet_size}
        :param register_interface_ip_with_dns: Determines if the operating system will register WARP's local interface IP with your on-premises DNS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#register_interface_ip_with_dns ZeroTrustDeviceCustomProfile#register_interface_ip_with_dns}
        :param sccm_vpn_boundary_support: Determines whether the WARP client indicates to SCCM that it is inside a VPN boundary. (Windows only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#sccm_vpn_boundary_support ZeroTrustDeviceCustomProfile#sccm_vpn_boundary_support}
        :param service_mode_v2: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#service_mode_v2 ZeroTrustDeviceCustomProfile#service_mode_v2}.
        :param support_url: The URL to launch when the Send Feedback button is clicked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#support_url ZeroTrustDeviceCustomProfile#support_url}
        :param switch_locked: Whether to allow the user to turn off the WARP switch and disconnect the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#switch_locked ZeroTrustDeviceCustomProfile#switch_locked}
        :param tunnel_protocol: Determines which tunnel protocol to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#tunnel_protocol ZeroTrustDeviceCustomProfile#tunnel_protocol}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(service_mode_v2, dict):
            service_mode_v2 = ZeroTrustDeviceCustomProfileServiceModeV2(**service_mode_v2)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea0f55d3803e8f6356ff4fe9f3e7e0c7184e0ebea654174d32c165f89859384d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument match", value=match, expected_type=type_hints["match"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument precedence", value=precedence, expected_type=type_hints["precedence"])
            check_type(argname="argument allowed_to_leave", value=allowed_to_leave, expected_type=type_hints["allowed_to_leave"])
            check_type(argname="argument allow_mode_switch", value=allow_mode_switch, expected_type=type_hints["allow_mode_switch"])
            check_type(argname="argument allow_updates", value=allow_updates, expected_type=type_hints["allow_updates"])
            check_type(argname="argument auto_connect", value=auto_connect, expected_type=type_hints["auto_connect"])
            check_type(argname="argument captive_portal", value=captive_portal, expected_type=type_hints["captive_portal"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_auto_fallback", value=disable_auto_fallback, expected_type=type_hints["disable_auto_fallback"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument exclude", value=exclude, expected_type=type_hints["exclude"])
            check_type(argname="argument exclude_office_ips", value=exclude_office_ips, expected_type=type_hints["exclude_office_ips"])
            check_type(argname="argument include", value=include, expected_type=type_hints["include"])
            check_type(argname="argument lan_allow_minutes", value=lan_allow_minutes, expected_type=type_hints["lan_allow_minutes"])
            check_type(argname="argument lan_allow_subnet_size", value=lan_allow_subnet_size, expected_type=type_hints["lan_allow_subnet_size"])
            check_type(argname="argument register_interface_ip_with_dns", value=register_interface_ip_with_dns, expected_type=type_hints["register_interface_ip_with_dns"])
            check_type(argname="argument sccm_vpn_boundary_support", value=sccm_vpn_boundary_support, expected_type=type_hints["sccm_vpn_boundary_support"])
            check_type(argname="argument service_mode_v2", value=service_mode_v2, expected_type=type_hints["service_mode_v2"])
            check_type(argname="argument support_url", value=support_url, expected_type=type_hints["support_url"])
            check_type(argname="argument switch_locked", value=switch_locked, expected_type=type_hints["switch_locked"])
            check_type(argname="argument tunnel_protocol", value=tunnel_protocol, expected_type=type_hints["tunnel_protocol"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "match": match,
            "name": name,
            "precedence": precedence,
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
        if allowed_to_leave is not None:
            self._values["allowed_to_leave"] = allowed_to_leave
        if allow_mode_switch is not None:
            self._values["allow_mode_switch"] = allow_mode_switch
        if allow_updates is not None:
            self._values["allow_updates"] = allow_updates
        if auto_connect is not None:
            self._values["auto_connect"] = auto_connect
        if captive_portal is not None:
            self._values["captive_portal"] = captive_portal
        if description is not None:
            self._values["description"] = description
        if disable_auto_fallback is not None:
            self._values["disable_auto_fallback"] = disable_auto_fallback
        if enabled is not None:
            self._values["enabled"] = enabled
        if exclude is not None:
            self._values["exclude"] = exclude
        if exclude_office_ips is not None:
            self._values["exclude_office_ips"] = exclude_office_ips
        if include is not None:
            self._values["include"] = include
        if lan_allow_minutes is not None:
            self._values["lan_allow_minutes"] = lan_allow_minutes
        if lan_allow_subnet_size is not None:
            self._values["lan_allow_subnet_size"] = lan_allow_subnet_size
        if register_interface_ip_with_dns is not None:
            self._values["register_interface_ip_with_dns"] = register_interface_ip_with_dns
        if sccm_vpn_boundary_support is not None:
            self._values["sccm_vpn_boundary_support"] = sccm_vpn_boundary_support
        if service_mode_v2 is not None:
            self._values["service_mode_v2"] = service_mode_v2
        if support_url is not None:
            self._values["support_url"] = support_url
        if switch_locked is not None:
            self._values["switch_locked"] = switch_locked
        if tunnel_protocol is not None:
            self._values["tunnel_protocol"] = tunnel_protocol

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#account_id ZeroTrustDeviceCustomProfile#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def match(self) -> builtins.str:
        '''The wirefilter expression to match devices. Available values: "identity.email", "identity.groups.id", "identity.groups.name", "identity.groups.email", "identity.service_token_uuid", "identity.saml_attributes", "network", "os.name", "os.version".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#match ZeroTrustDeviceCustomProfile#match}
        '''
        result = self._values.get("match")
        assert result is not None, "Required property 'match' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the device settings profile.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#name ZeroTrustDeviceCustomProfile#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def precedence(self) -> jsii.Number:
        '''The precedence of the policy.

        Lower values indicate higher precedence. Policies will be evaluated in ascending order of this field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#precedence ZeroTrustDeviceCustomProfile#precedence}
        '''
        result = self._values.get("precedence")
        assert result is not None, "Required property 'precedence' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def allowed_to_leave(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to allow devices to leave the organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#allowed_to_leave ZeroTrustDeviceCustomProfile#allowed_to_leave}
        '''
        result = self._values.get("allowed_to_leave")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_mode_switch(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to allow the user to switch WARP between modes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#allow_mode_switch ZeroTrustDeviceCustomProfile#allow_mode_switch}
        '''
        result = self._values.get("allow_mode_switch")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_updates(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to receive update notifications when a new version of the client is available.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#allow_updates ZeroTrustDeviceCustomProfile#allow_updates}
        '''
        result = self._values.get("allow_updates")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_connect(self) -> typing.Optional[jsii.Number]:
        '''The amount of time in seconds to reconnect after having been disabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#auto_connect ZeroTrustDeviceCustomProfile#auto_connect}
        '''
        result = self._values.get("auto_connect")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def captive_portal(self) -> typing.Optional[jsii.Number]:
        '''Turn on the captive portal after the specified amount of time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#captive_portal ZeroTrustDeviceCustomProfile#captive_portal}
        '''
        result = self._values.get("captive_portal")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#description ZeroTrustDeviceCustomProfile#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_auto_fallback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If the ``dns_server`` field of a fallback domain is not present, the client will fall back to a best guess of the default/system DNS resolvers unless this policy option is set to ``true``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#disable_auto_fallback ZeroTrustDeviceCustomProfile#disable_auto_fallback}
        '''
        result = self._values.get("disable_auto_fallback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether the policy will be applied to matching devices.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#enabled ZeroTrustDeviceCustomProfile#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def exclude(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceCustomProfileExclude"]]]:
        '''List of routes excluded in the WARP client's tunnel.

        Both 'exclude' and 'include' cannot be set in the same request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#exclude ZeroTrustDeviceCustomProfile#exclude}
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceCustomProfileExclude"]]], result)

    @builtins.property
    def exclude_office_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to add Microsoft IPs to Split Tunnel exclusions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#exclude_office_ips ZeroTrustDeviceCustomProfile#exclude_office_ips}
        '''
        result = self._values.get("exclude_office_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def include(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceCustomProfileInclude"]]]:
        '''List of routes included in the WARP client's tunnel.

        Both 'exclude' and 'include' cannot be set in the same request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#include ZeroTrustDeviceCustomProfile#include}
        '''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceCustomProfileInclude"]]], result)

    @builtins.property
    def lan_allow_minutes(self) -> typing.Optional[jsii.Number]:
        '''The amount of time in minutes a user is allowed access to their LAN.

        A value of 0 will allow LAN access until the next WARP reconnection, such as a reboot or a laptop waking from sleep. Note that this field is omitted from the response if null or unset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#lan_allow_minutes ZeroTrustDeviceCustomProfile#lan_allow_minutes}
        '''
        result = self._values.get("lan_allow_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lan_allow_subnet_size(self) -> typing.Optional[jsii.Number]:
        '''The size of the subnet for the local access network.

        Note that this field is omitted from the response if null or unset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#lan_allow_subnet_size ZeroTrustDeviceCustomProfile#lan_allow_subnet_size}
        '''
        result = self._values.get("lan_allow_subnet_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def register_interface_ip_with_dns(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines if the operating system will register WARP's local interface IP with your on-premises DNS server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#register_interface_ip_with_dns ZeroTrustDeviceCustomProfile#register_interface_ip_with_dns}
        '''
        result = self._values.get("register_interface_ip_with_dns")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sccm_vpn_boundary_support(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines whether the WARP client indicates to SCCM that it is inside a VPN boundary. (Windows only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#sccm_vpn_boundary_support ZeroTrustDeviceCustomProfile#sccm_vpn_boundary_support}
        '''
        result = self._values.get("sccm_vpn_boundary_support")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def service_mode_v2(
        self,
    ) -> typing.Optional["ZeroTrustDeviceCustomProfileServiceModeV2"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#service_mode_v2 ZeroTrustDeviceCustomProfile#service_mode_v2}.'''
        result = self._values.get("service_mode_v2")
        return typing.cast(typing.Optional["ZeroTrustDeviceCustomProfileServiceModeV2"], result)

    @builtins.property
    def support_url(self) -> typing.Optional[builtins.str]:
        '''The URL to launch when the Send Feedback button is clicked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#support_url ZeroTrustDeviceCustomProfile#support_url}
        '''
        result = self._values.get("support_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def switch_locked(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to allow the user to turn off the WARP switch and disconnect the client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#switch_locked ZeroTrustDeviceCustomProfile#switch_locked}
        '''
        result = self._values.get("switch_locked")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tunnel_protocol(self) -> typing.Optional[builtins.str]:
        '''Determines which tunnel protocol to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#tunnel_protocol ZeroTrustDeviceCustomProfile#tunnel_protocol}
        '''
        result = self._values.get("tunnel_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceCustomProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileExclude",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "description": "description", "host": "host"},
)
class ZeroTrustDeviceCustomProfileExclude:
    def __init__(
        self,
        *,
        address: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: The address in CIDR format to exclude from the tunnel. If ``address`` is present, ``host`` must not be present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#address ZeroTrustDeviceCustomProfile#address}
        :param description: A description of the Split Tunnel item, displayed in the client UI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#description ZeroTrustDeviceCustomProfile#description}
        :param host: The domain name to exclude from the tunnel. If ``host`` is present, ``address`` must not be present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#host ZeroTrustDeviceCustomProfile#host}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a267719377348af68fec55bea78a5bfa8723c74aea8d66dc6e76d9634e3f8a11)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if address is not None:
            self._values["address"] = address
        if description is not None:
            self._values["description"] = description
        if host is not None:
            self._values["host"] = host

    @builtins.property
    def address(self) -> typing.Optional[builtins.str]:
        '''The address in CIDR format to exclude from the tunnel. If ``address`` is present, ``host`` must not be present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#address ZeroTrustDeviceCustomProfile#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the Split Tunnel item, displayed in the client UI.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#description ZeroTrustDeviceCustomProfile#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''The domain name to exclude from the tunnel. If ``host`` is present, ``address`` must not be present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#host ZeroTrustDeviceCustomProfile#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceCustomProfileExclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDeviceCustomProfileExcludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileExcludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d1693cef3cd9b2657acc266ceb65c6def84b9f0e756baf36fb79f660eaec18d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDeviceCustomProfileExcludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd0d36f83fb2d6860508a79aaa34fc239a4aaf3a6e3ce4be197148a2682502fc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDeviceCustomProfileExcludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90d4ea1117b7d09e01d0cd7aa4404079e6930f444765a2102a0a583b51720284)
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
            type_hints = typing.get_type_hints(_typecheckingstub__561becef6d7d4c03aad17e471e75f6920186fa0114e08a6a0a3fbb8b64666e9b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2ef5ac8aa6265ad539f44ed422a3100109a23ffdb02a806db8844ac06a171e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceCustomProfileExclude]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceCustomProfileExclude]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceCustomProfileExclude]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e99108a4f35b9687a0f5df3e0f97bd86ea660abd214c748dd4a83ecc1efb68de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDeviceCustomProfileExcludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileExcludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61916b733032b55214b93b0ca8098dac614fe2269478cb4e91e0abd9288ab8f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAddress")
    def reset_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddress", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fac0eae1895bcf05bf7903fc50d15a2a860439b7b9e490047a06cf2afa57a0ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4d2b21f57e52456bdf582f08756983e029423f0a944085f9139f667f74fee81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1160c1a1c3c6b97a712eb55b0002f6d0972052fe8cfb831ec7658c26e0fb0dfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileExclude]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileExclude]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileExclude]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0c3d7540d4ee5c563c110d730a0325cc8d7b56957b6fea57dc380d7514b0925)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileFallbackDomains",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustDeviceCustomProfileFallbackDomains:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceCustomProfileFallbackDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDeviceCustomProfileFallbackDomainsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileFallbackDomainsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__655dc878ad1e827269d02b1b7d2bcece3db17a37219b22b9fd9f8dc24205ffc5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDeviceCustomProfileFallbackDomainsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__278638e44154c573cecc2112d06de2962f68c6c5668682b8c8509c1c9ee90611)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDeviceCustomProfileFallbackDomainsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de2086e7fa639c591ce2da8322b53d8fe089a8ac8faad00a241eb6687da66fc2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__733c4a3a375a05ff5387779f918f2508ec45da2ed39dac09b8fd1c6b083dcd89)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db9cc7f4a12412413ea429b48b6a480dca747b8acffb85585b6be45fef66b81a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDeviceCustomProfileFallbackDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileFallbackDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d895a0933d7f13c5f4be1ba315a243e865349fe01d6b495eb95bc9b4179885b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="dnsServer")
    def dns_server(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsServer"))

    @builtins.property
    @jsii.member(jsii_name="suffix")
    def suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "suffix"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ZeroTrustDeviceCustomProfileFallbackDomains]:
        return typing.cast(typing.Optional[ZeroTrustDeviceCustomProfileFallbackDomains], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ZeroTrustDeviceCustomProfileFallbackDomains],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0cfcaa22a14d763dd8874fb916e77a5f1e59991ba953be27e34b3dec0d48ccc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileInclude",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "description": "description", "host": "host"},
)
class ZeroTrustDeviceCustomProfileInclude:
    def __init__(
        self,
        *,
        address: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: The address in CIDR format to include in the tunnel. If ``address`` is present, ``host`` must not be present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#address ZeroTrustDeviceCustomProfile#address}
        :param description: A description of the Split Tunnel item, displayed in the client UI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#description ZeroTrustDeviceCustomProfile#description}
        :param host: The domain name to include in the tunnel. If ``host`` is present, ``address`` must not be present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#host ZeroTrustDeviceCustomProfile#host}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7762e0024186e24f5cc6c3fd86ec646e7f006224ede671abe54120dfc05d901)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if address is not None:
            self._values["address"] = address
        if description is not None:
            self._values["description"] = description
        if host is not None:
            self._values["host"] = host

    @builtins.property
    def address(self) -> typing.Optional[builtins.str]:
        '''The address in CIDR format to include in the tunnel. If ``address`` is present, ``host`` must not be present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#address ZeroTrustDeviceCustomProfile#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the Split Tunnel item, displayed in the client UI.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#description ZeroTrustDeviceCustomProfile#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''The domain name to include in the tunnel. If ``host`` is present, ``address`` must not be present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#host ZeroTrustDeviceCustomProfile#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceCustomProfileInclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDeviceCustomProfileIncludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileIncludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__069ec6aa5503de13b0a10076cfcf4e6fd390da231e198f59f878ae90f7dce1d7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDeviceCustomProfileIncludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0923ae4ff4d6aa62cfc9ff21e2b520b2e7fcce2eeb4bc627b26ea356cbe183a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDeviceCustomProfileIncludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee90eff7c1f0cb40de9d21424ec1c5546d9feec6e2776240a836d7a64a5eb789)
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
            type_hints = typing.get_type_hints(_typecheckingstub__872ce452c47f87f4affc93834c3359a53728d32aa1bd3f44d1403dbbdeeb44e5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__75996b7133e89ad138c1559aabf891f0c69db9cb5e5e129f431ddd90e7de6e80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceCustomProfileInclude]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceCustomProfileInclude]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceCustomProfileInclude]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__499bf9d4c33d772a77fee43d62a4855bb8220b5fbe1bb0a702f3cf150034d5dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDeviceCustomProfileIncludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileIncludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e58b7ff0271c2ddd3791c272c44c29d9f9130b39c100b07c992d64a662f97f87)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAddress")
    def reset_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddress", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c5eaf6c45b1f65d58e56c753159b3c598fb825987eb78a9d29700214353179a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0801067b496cc0e6e587c84045ade4e45897836fca478eda7d10d9ce2c8d1e99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70c5c4c197a5b93111ce5c13f8af78b50c19b18ffe6734571ef75c43beecd3cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileInclude]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileInclude]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileInclude]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9b63dfd0c6f6fddd0b785ef44a0a3e918a0768c5d3da5f3850a50ea367d4b4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileServiceModeV2",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "port": "port"},
)
class ZeroTrustDeviceCustomProfileServiceModeV2:
    def __init__(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mode: The mode to run the WARP client under. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#mode ZeroTrustDeviceCustomProfile#mode}
        :param port: The port number when used with proxy mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#port ZeroTrustDeviceCustomProfile#port}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c81b66010c41f792dfeff871fa5e295299dda156a3acb8c7b22827a2e58952cf)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''The mode to run the WARP client under.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#mode ZeroTrustDeviceCustomProfile#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The port number when used with proxy mode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_custom_profile#port ZeroTrustDeviceCustomProfile#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceCustomProfileServiceModeV2(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDeviceCustomProfileServiceModeV2OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileServiceModeV2OutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__177e401035e536cbffecd6267f3c8304cf79ca84e5751827a745b0b224d16544)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5da9369f53af57c2d8efbe159399ae21e25dfc8bec5c960f8c9db54071cb5f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5243e8f7133b405a962e9677de178f7247945e4cda8908d4e041efb70a0a5dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileServiceModeV2]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileServiceModeV2]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileServiceModeV2]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8936ea091b1268257e1ca904a9c2ecceb01ddbed6cdc82686d55e9cc9a7ae86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileTargetTests",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustDeviceCustomProfileTargetTests:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceCustomProfileTargetTests(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDeviceCustomProfileTargetTestsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileTargetTestsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4543e84bb96b6a8e7770d66fc38b21b670c9226765381dfdef29745e536e3ed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDeviceCustomProfileTargetTestsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__630c0000ac417636a30dc84855cc3a185c6bd298ad9be6f7b6b333e2248af56c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDeviceCustomProfileTargetTestsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a25cd3e12a45ed550e1dec5d37c97c83cd8f4d47ca63d65a6624e6cac14fb7ca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ab78b4eb49a3080d98c1f68135d3bb320976529c6a59ecaacc42402ce53c23d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb24d8cf5b5c107d559968dce0eeaaf34ccc7ebb32b87bc4d85babfc078f646f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDeviceCustomProfileTargetTestsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceCustomProfile.ZeroTrustDeviceCustomProfileTargetTestsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__755dd6c96c8842f349cb4381533c72d206f5e4348f5f536b5fb5e18eb8231c7b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ZeroTrustDeviceCustomProfileTargetTests]:
        return typing.cast(typing.Optional[ZeroTrustDeviceCustomProfileTargetTests], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ZeroTrustDeviceCustomProfileTargetTests],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__297f8a537a9c9c67014b0ae07323a98b98e4a60187af3ac95f53816a9bec3af0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustDeviceCustomProfile",
    "ZeroTrustDeviceCustomProfileConfig",
    "ZeroTrustDeviceCustomProfileExclude",
    "ZeroTrustDeviceCustomProfileExcludeList",
    "ZeroTrustDeviceCustomProfileExcludeOutputReference",
    "ZeroTrustDeviceCustomProfileFallbackDomains",
    "ZeroTrustDeviceCustomProfileFallbackDomainsList",
    "ZeroTrustDeviceCustomProfileFallbackDomainsOutputReference",
    "ZeroTrustDeviceCustomProfileInclude",
    "ZeroTrustDeviceCustomProfileIncludeList",
    "ZeroTrustDeviceCustomProfileIncludeOutputReference",
    "ZeroTrustDeviceCustomProfileServiceModeV2",
    "ZeroTrustDeviceCustomProfileServiceModeV2OutputReference",
    "ZeroTrustDeviceCustomProfileTargetTests",
    "ZeroTrustDeviceCustomProfileTargetTestsList",
    "ZeroTrustDeviceCustomProfileTargetTestsOutputReference",
]

publication.publish()

def _typecheckingstub__892750ee6d327436d674cc96685cdf3198c07378abd461534011e7b6013d7951(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    match: builtins.str,
    name: builtins.str,
    precedence: jsii.Number,
    allowed_to_leave: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mode_switch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_updates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_connect: typing.Optional[jsii.Number] = None,
    captive_portal: typing.Optional[jsii.Number] = None,
    description: typing.Optional[builtins.str] = None,
    disable_auto_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceCustomProfileExclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    exclude_office_ips: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceCustomProfileInclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    lan_allow_minutes: typing.Optional[jsii.Number] = None,
    lan_allow_subnet_size: typing.Optional[jsii.Number] = None,
    register_interface_ip_with_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sccm_vpn_boundary_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_mode_v2: typing.Optional[typing.Union[ZeroTrustDeviceCustomProfileServiceModeV2, typing.Dict[builtins.str, typing.Any]]] = None,
    support_url: typing.Optional[builtins.str] = None,
    switch_locked: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tunnel_protocol: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__c1289fc35564713d5332d8089635fad7ecd71e893dcf66ee937731d05e570d29(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a8b645f5ba47e750d5e657534f404d9392a36f339819125f1137ed1bbc7f9cf(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceCustomProfileExclude, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42c3c0bef0a3caa7223598740369d2d5a6000156ad1f53067508afcdabc9e219(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceCustomProfileInclude, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49eb9703ac6f2199ee23f0961c889dc829a32a84c5bded92bebc959c6e40c465(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24348761c54c8edd0078b37492c5d715c61434f940d1e6bed0b85b7c46da1fe9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f8a35af70bb4320482ce9784f94cf9f556c1e0955efe2cd0c7fa7fbbcc6212a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e57f0d7340907ed153b523259e68cc75bb7e5e78f300db4a619db40fe308cc13(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7971b0feee9ad5e743b92fe16bbc7d79498acd11f6369ea84650a42804794351(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdaaca05bd413a28892ef111f9b833e1b38fb7b89f0125270a2ee6936c4734e9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e1069bf3fa8aa5adea5c7e988c0966fd26932f06364491f0c347e38d82e9deb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc9c17712ef6b9b997d5320dddf93d92e00380c305aebf5079b0f754bb153f06(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83aa891f845b877d1eea049d8b221578a0fb3785a28440edd2e990198057c8cc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53b7ce9590f70881caba538b136a0dd93e319072deb7aadb21bf607627dc6d7f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e0be2eac7d36ee9aeb73e79f03384017ab9b27ee6efe14b0036c1ee379655af(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2da28304784b1279913a4ea747aa0f0bd3fe76645206b76ff5172ee087afa03(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a259a8fcbefb0f4ee27c74217093ea63dbc30d64718829e31fae177f9c5f4a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3abda7e726a69b65d7cfc0d3faf0be5e33afecc5dc215c733b505f3fcb178c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3d793f208f985aa13fbe7c6cb7e21f22bf51c75eea65d9cd721769af4cf5e21(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53e4528eabcdd4d6d8b923061e976cb5f97809b79cfa6d0f2c2c7abfab76f4b2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd7539b82e137348881321ce471643ebaf5a64b5ce6e7d5df5ec2e81776f3a39(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a888107e12522d9cda66cd89f363486ff39ac56540ca229a2be85c517bdb460(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__895f7ffa0b0d79621dba88174350516d65ad2799e6328f22c3611e8a595135cf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb60a72db627a6b0fee55af2d5fb5b8d5f28359bc8d7101dfbe5e24627a32b34(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea0f55d3803e8f6356ff4fe9f3e7e0c7184e0ebea654174d32c165f89859384d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    match: builtins.str,
    name: builtins.str,
    precedence: jsii.Number,
    allowed_to_leave: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mode_switch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_updates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_connect: typing.Optional[jsii.Number] = None,
    captive_portal: typing.Optional[jsii.Number] = None,
    description: typing.Optional[builtins.str] = None,
    disable_auto_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceCustomProfileExclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    exclude_office_ips: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceCustomProfileInclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    lan_allow_minutes: typing.Optional[jsii.Number] = None,
    lan_allow_subnet_size: typing.Optional[jsii.Number] = None,
    register_interface_ip_with_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sccm_vpn_boundary_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_mode_v2: typing.Optional[typing.Union[ZeroTrustDeviceCustomProfileServiceModeV2, typing.Dict[builtins.str, typing.Any]]] = None,
    support_url: typing.Optional[builtins.str] = None,
    switch_locked: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tunnel_protocol: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a267719377348af68fec55bea78a5bfa8723c74aea8d66dc6e76d9634e3f8a11(
    *,
    address: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d1693cef3cd9b2657acc266ceb65c6def84b9f0e756baf36fb79f660eaec18d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd0d36f83fb2d6860508a79aaa34fc239a4aaf3a6e3ce4be197148a2682502fc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90d4ea1117b7d09e01d0cd7aa4404079e6930f444765a2102a0a583b51720284(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__561becef6d7d4c03aad17e471e75f6920186fa0114e08a6a0a3fbb8b64666e9b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2ef5ac8aa6265ad539f44ed422a3100109a23ffdb02a806db8844ac06a171e9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e99108a4f35b9687a0f5df3e0f97bd86ea660abd214c748dd4a83ecc1efb68de(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceCustomProfileExclude]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61916b733032b55214b93b0ca8098dac614fe2269478cb4e91e0abd9288ab8f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fac0eae1895bcf05bf7903fc50d15a2a860439b7b9e490047a06cf2afa57a0ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4d2b21f57e52456bdf582f08756983e029423f0a944085f9139f667f74fee81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1160c1a1c3c6b97a712eb55b0002f6d0972052fe8cfb831ec7658c26e0fb0dfa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0c3d7540d4ee5c563c110d730a0325cc8d7b56957b6fea57dc380d7514b0925(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileExclude]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__655dc878ad1e827269d02b1b7d2bcece3db17a37219b22b9fd9f8dc24205ffc5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__278638e44154c573cecc2112d06de2962f68c6c5668682b8c8509c1c9ee90611(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de2086e7fa639c591ce2da8322b53d8fe089a8ac8faad00a241eb6687da66fc2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__733c4a3a375a05ff5387779f918f2508ec45da2ed39dac09b8fd1c6b083dcd89(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db9cc7f4a12412413ea429b48b6a480dca747b8acffb85585b6be45fef66b81a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d895a0933d7f13c5f4be1ba315a243e865349fe01d6b495eb95bc9b4179885b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0cfcaa22a14d763dd8874fb916e77a5f1e59991ba953be27e34b3dec0d48ccc(
    value: typing.Optional[ZeroTrustDeviceCustomProfileFallbackDomains],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7762e0024186e24f5cc6c3fd86ec646e7f006224ede671abe54120dfc05d901(
    *,
    address: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__069ec6aa5503de13b0a10076cfcf4e6fd390da231e198f59f878ae90f7dce1d7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0923ae4ff4d6aa62cfc9ff21e2b520b2e7fcce2eeb4bc627b26ea356cbe183a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee90eff7c1f0cb40de9d21424ec1c5546d9feec6e2776240a836d7a64a5eb789(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__872ce452c47f87f4affc93834c3359a53728d32aa1bd3f44d1403dbbdeeb44e5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75996b7133e89ad138c1559aabf891f0c69db9cb5e5e129f431ddd90e7de6e80(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__499bf9d4c33d772a77fee43d62a4855bb8220b5fbe1bb0a702f3cf150034d5dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceCustomProfileInclude]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e58b7ff0271c2ddd3791c272c44c29d9f9130b39c100b07c992d64a662f97f87(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c5eaf6c45b1f65d58e56c753159b3c598fb825987eb78a9d29700214353179a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0801067b496cc0e6e587c84045ade4e45897836fca478eda7d10d9ce2c8d1e99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70c5c4c197a5b93111ce5c13f8af78b50c19b18ffe6734571ef75c43beecd3cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9b63dfd0c6f6fddd0b785ef44a0a3e918a0768c5d3da5f3850a50ea367d4b4f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileInclude]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c81b66010c41f792dfeff871fa5e295299dda156a3acb8c7b22827a2e58952cf(
    *,
    mode: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__177e401035e536cbffecd6267f3c8304cf79ca84e5751827a745b0b224d16544(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5da9369f53af57c2d8efbe159399ae21e25dfc8bec5c960f8c9db54071cb5f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5243e8f7133b405a962e9677de178f7247945e4cda8908d4e041efb70a0a5dc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8936ea091b1268257e1ca904a9c2ecceb01ddbed6cdc82686d55e9cc9a7ae86(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceCustomProfileServiceModeV2]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4543e84bb96b6a8e7770d66fc38b21b670c9226765381dfdef29745e536e3ed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__630c0000ac417636a30dc84855cc3a185c6bd298ad9be6f7b6b333e2248af56c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a25cd3e12a45ed550e1dec5d37c97c83cd8f4d47ca63d65a6624e6cac14fb7ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ab78b4eb49a3080d98c1f68135d3bb320976529c6a59ecaacc42402ce53c23d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb24d8cf5b5c107d559968dce0eeaaf34ccc7ebb32b87bc4d85babfc078f646f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__755dd6c96c8842f349cb4381533c72d206f5e4348f5f536b5fb5e18eb8231c7b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__297f8a537a9c9c67014b0ae07323a98b98e4a60187af3ac95f53816a9bec3af0(
    value: typing.Optional[ZeroTrustDeviceCustomProfileTargetTests],
) -> None:
    """Type checking stubs"""
    pass
