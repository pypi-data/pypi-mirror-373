r'''
# `cloudflare_zero_trust_device_default_profile`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_device_default_profile`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile).
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


class ZeroTrustDeviceDefaultProfile(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfile",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile cloudflare_zero_trust_device_default_profile}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        allowed_to_leave: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mode_switch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_updates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_connect: typing.Optional[jsii.Number] = None,
        captive_portal: typing.Optional[jsii.Number] = None,
        disable_auto_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceDefaultProfileExclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        exclude_office_ips: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceDefaultProfileInclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        lan_allow_minutes: typing.Optional[jsii.Number] = None,
        lan_allow_subnet_size: typing.Optional[jsii.Number] = None,
        register_interface_ip_with_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sccm_vpn_boundary_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_mode_v2: typing.Optional[typing.Union["ZeroTrustDeviceDefaultProfileServiceModeV2", typing.Dict[builtins.str, typing.Any]]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile cloudflare_zero_trust_device_default_profile} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#account_id ZeroTrustDeviceDefaultProfile#account_id}.
        :param allowed_to_leave: Whether to allow devices to leave the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#allowed_to_leave ZeroTrustDeviceDefaultProfile#allowed_to_leave}
        :param allow_mode_switch: Whether to allow the user to switch WARP between modes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#allow_mode_switch ZeroTrustDeviceDefaultProfile#allow_mode_switch}
        :param allow_updates: Whether to receive update notifications when a new version of the client is available. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#allow_updates ZeroTrustDeviceDefaultProfile#allow_updates}
        :param auto_connect: The amount of time in seconds to reconnect after having been disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#auto_connect ZeroTrustDeviceDefaultProfile#auto_connect}
        :param captive_portal: Turn on the captive portal after the specified amount of time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#captive_portal ZeroTrustDeviceDefaultProfile#captive_portal}
        :param disable_auto_fallback: If the ``dns_server`` field of a fallback domain is not present, the client will fall back to a best guess of the default/system DNS resolvers unless this policy option is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#disable_auto_fallback ZeroTrustDeviceDefaultProfile#disable_auto_fallback}
        :param exclude: List of routes excluded in the WARP client's tunnel. Both 'exclude' and 'include' cannot be set in the same request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#exclude ZeroTrustDeviceDefaultProfile#exclude}
        :param exclude_office_ips: Whether to add Microsoft IPs to Split Tunnel exclusions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#exclude_office_ips ZeroTrustDeviceDefaultProfile#exclude_office_ips}
        :param include: List of routes included in the WARP client's tunnel. Both 'exclude' and 'include' cannot be set in the same request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#include ZeroTrustDeviceDefaultProfile#include}
        :param lan_allow_minutes: The amount of time in minutes a user is allowed access to their LAN. A value of 0 will allow LAN access until the next WARP reconnection, such as a reboot or a laptop waking from sleep. Note that this field is omitted from the response if null or unset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#lan_allow_minutes ZeroTrustDeviceDefaultProfile#lan_allow_minutes}
        :param lan_allow_subnet_size: The size of the subnet for the local access network. Note that this field is omitted from the response if null or unset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#lan_allow_subnet_size ZeroTrustDeviceDefaultProfile#lan_allow_subnet_size}
        :param register_interface_ip_with_dns: Determines if the operating system will register WARP's local interface IP with your on-premises DNS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#register_interface_ip_with_dns ZeroTrustDeviceDefaultProfile#register_interface_ip_with_dns}
        :param sccm_vpn_boundary_support: Determines whether the WARP client indicates to SCCM that it is inside a VPN boundary. (Windows only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#sccm_vpn_boundary_support ZeroTrustDeviceDefaultProfile#sccm_vpn_boundary_support}
        :param service_mode_v2: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#service_mode_v2 ZeroTrustDeviceDefaultProfile#service_mode_v2}.
        :param support_url: The URL to launch when the Send Feedback button is clicked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#support_url ZeroTrustDeviceDefaultProfile#support_url}
        :param switch_locked: Whether to allow the user to turn off the WARP switch and disconnect the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#switch_locked ZeroTrustDeviceDefaultProfile#switch_locked}
        :param tunnel_protocol: Determines which tunnel protocol to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#tunnel_protocol ZeroTrustDeviceDefaultProfile#tunnel_protocol}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd1e430c3de79ec44c4da667c1fcb7f80da06d10396e1d66ad3373963efaec46)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustDeviceDefaultProfileConfig(
            account_id=account_id,
            allowed_to_leave=allowed_to_leave,
            allow_mode_switch=allow_mode_switch,
            allow_updates=allow_updates,
            auto_connect=auto_connect,
            captive_portal=captive_portal,
            disable_auto_fallback=disable_auto_fallback,
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
        '''Generates CDKTF code for importing a ZeroTrustDeviceDefaultProfile resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustDeviceDefaultProfile to import.
        :param import_from_id: The id of the existing ZeroTrustDeviceDefaultProfile that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustDeviceDefaultProfile to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9261cfb32fea9fa03f7dc7ac72f693db10f62e9c72f4b9e585c06ebe13067b87)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putExclude")
    def put_exclude(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceDefaultProfileExclude", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__901ff592eee6d1686f429219a70fd8727070163ace349a5d6b02e8cefcaa142d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExclude", [value]))

    @jsii.member(jsii_name="putInclude")
    def put_include(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceDefaultProfileInclude", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f18d732244584b4fde20753fb4c7ad664547c6869d18eb36a509fdf43d1ec776)
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
        :param mode: The mode to run the WARP client under. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#mode ZeroTrustDeviceDefaultProfile#mode}
        :param port: The port number when used with proxy mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#port ZeroTrustDeviceDefaultProfile#port}
        '''
        value = ZeroTrustDeviceDefaultProfileServiceModeV2(mode=mode, port=port)

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

    @jsii.member(jsii_name="resetDisableAutoFallback")
    def reset_disable_auto_fallback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableAutoFallback", []))

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
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> "ZeroTrustDeviceDefaultProfileExcludeList":
        return typing.cast("ZeroTrustDeviceDefaultProfileExcludeList", jsii.get(self, "exclude"))

    @builtins.property
    @jsii.member(jsii_name="fallbackDomains")
    def fallback_domains(self) -> "ZeroTrustDeviceDefaultProfileFallbackDomainsList":
        return typing.cast("ZeroTrustDeviceDefaultProfileFallbackDomainsList", jsii.get(self, "fallbackDomains"))

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
    def include(self) -> "ZeroTrustDeviceDefaultProfileIncludeList":
        return typing.cast("ZeroTrustDeviceDefaultProfileIncludeList", jsii.get(self, "include"))

    @builtins.property
    @jsii.member(jsii_name="serviceModeV2")
    def service_mode_v2(
        self,
    ) -> "ZeroTrustDeviceDefaultProfileServiceModeV2OutputReference":
        return typing.cast("ZeroTrustDeviceDefaultProfileServiceModeV2OutputReference", jsii.get(self, "serviceModeV2"))

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
    @jsii.member(jsii_name="disableAutoFallbackInput")
    def disable_auto_fallback_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableAutoFallbackInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeInput")
    def exclude_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceDefaultProfileExclude"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceDefaultProfileExclude"]]], jsii.get(self, "excludeInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceDefaultProfileInclude"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceDefaultProfileInclude"]]], jsii.get(self, "includeInput"))

    @builtins.property
    @jsii.member(jsii_name="lanAllowMinutesInput")
    def lan_allow_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lanAllowMinutesInput"))

    @builtins.property
    @jsii.member(jsii_name="lanAllowSubnetSizeInput")
    def lan_allow_subnet_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lanAllowSubnetSizeInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustDeviceDefaultProfileServiceModeV2"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustDeviceDefaultProfileServiceModeV2"]], jsii.get(self, "serviceModeV2Input"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__fcb6a32ff112b1cb57da98a928efaa2eb0102e7aad9822563330c85bce3cc55f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3461806c5a73af9d0765c43c26e0bcf8fe976843413d4d217ded79b78f6d2dec)
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
            type_hints = typing.get_type_hints(_typecheckingstub__251c6d266bf6cea09079fb204b78062fb685abacce9aafe74dfb6b217e5537af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a28f19147ca55ddab0de7c1ad435621b8688ef3aaf23fd7f48bb105e46a7b98e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowUpdates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoConnect")
    def auto_connect(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoConnect"))

    @auto_connect.setter
    def auto_connect(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__177e8cf89521b4f78e6ec9ef78813b853c5671e0809d4ca0cc036fa0c6f78168)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoConnect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="captivePortal")
    def captive_portal(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "captivePortal"))

    @captive_portal.setter
    def captive_portal(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6071bfc30b56743c9e85583ec5f171efc5d7c0d029c6cae6a4a0fceceb602d6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "captivePortal", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__cd7fc9707782004d90aa4345a4bdc9991250094b8003bbec0e923e604851be4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableAutoFallback", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__adeb88d43f173118d01ca3445c64084a7341909ac889838245cfcdb749acd284)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeOfficeIps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lanAllowMinutes")
    def lan_allow_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lanAllowMinutes"))

    @lan_allow_minutes.setter
    def lan_allow_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e96e291351d2965a69c8766e667d4f40f10bbf052f0588fff325a05d963d828)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanAllowMinutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lanAllowSubnetSize")
    def lan_allow_subnet_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lanAllowSubnetSize"))

    @lan_allow_subnet_size.setter
    def lan_allow_subnet_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec2a803958f21b38b2541cd3e5c0c16bf21f501a668d438f7662220b3bb249ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanAllowSubnetSize", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__d721f62beb08b20a285a1533d3fd70160064e295ce4083e9e637ce8819885876)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e107993ba8ec1124c06a0aa66c072aac06e589f1d95c71573aa5fca8457a1f91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sccmVpnBoundarySupport", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="supportUrl")
    def support_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "supportUrl"))

    @support_url.setter
    def support_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e45b08871bdef2a140ed7b0c170334f89a79371f8142e479de0eed15a722582a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f652ca737e537985a538ec80e5804fee1bc6ec068e2b0622b280a9505d75e63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "switchLocked", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tunnelProtocol")
    def tunnel_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tunnelProtocol"))

    @tunnel_protocol.setter
    def tunnel_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__377e7a4dd2b27d01d8047c05730e5ffed6718794068ba3acc26c4ed7debc2781)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tunnelProtocol", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileConfig",
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
        "allowed_to_leave": "allowedToLeave",
        "allow_mode_switch": "allowModeSwitch",
        "allow_updates": "allowUpdates",
        "auto_connect": "autoConnect",
        "captive_portal": "captivePortal",
        "disable_auto_fallback": "disableAutoFallback",
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
class ZeroTrustDeviceDefaultProfileConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allowed_to_leave: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mode_switch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_updates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_connect: typing.Optional[jsii.Number] = None,
        captive_portal: typing.Optional[jsii.Number] = None,
        disable_auto_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceDefaultProfileExclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        exclude_office_ips: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDeviceDefaultProfileInclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        lan_allow_minutes: typing.Optional[jsii.Number] = None,
        lan_allow_subnet_size: typing.Optional[jsii.Number] = None,
        register_interface_ip_with_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sccm_vpn_boundary_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_mode_v2: typing.Optional[typing.Union["ZeroTrustDeviceDefaultProfileServiceModeV2", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#account_id ZeroTrustDeviceDefaultProfile#account_id}.
        :param allowed_to_leave: Whether to allow devices to leave the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#allowed_to_leave ZeroTrustDeviceDefaultProfile#allowed_to_leave}
        :param allow_mode_switch: Whether to allow the user to switch WARP between modes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#allow_mode_switch ZeroTrustDeviceDefaultProfile#allow_mode_switch}
        :param allow_updates: Whether to receive update notifications when a new version of the client is available. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#allow_updates ZeroTrustDeviceDefaultProfile#allow_updates}
        :param auto_connect: The amount of time in seconds to reconnect after having been disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#auto_connect ZeroTrustDeviceDefaultProfile#auto_connect}
        :param captive_portal: Turn on the captive portal after the specified amount of time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#captive_portal ZeroTrustDeviceDefaultProfile#captive_portal}
        :param disable_auto_fallback: If the ``dns_server`` field of a fallback domain is not present, the client will fall back to a best guess of the default/system DNS resolvers unless this policy option is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#disable_auto_fallback ZeroTrustDeviceDefaultProfile#disable_auto_fallback}
        :param exclude: List of routes excluded in the WARP client's tunnel. Both 'exclude' and 'include' cannot be set in the same request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#exclude ZeroTrustDeviceDefaultProfile#exclude}
        :param exclude_office_ips: Whether to add Microsoft IPs to Split Tunnel exclusions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#exclude_office_ips ZeroTrustDeviceDefaultProfile#exclude_office_ips}
        :param include: List of routes included in the WARP client's tunnel. Both 'exclude' and 'include' cannot be set in the same request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#include ZeroTrustDeviceDefaultProfile#include}
        :param lan_allow_minutes: The amount of time in minutes a user is allowed access to their LAN. A value of 0 will allow LAN access until the next WARP reconnection, such as a reboot or a laptop waking from sleep. Note that this field is omitted from the response if null or unset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#lan_allow_minutes ZeroTrustDeviceDefaultProfile#lan_allow_minutes}
        :param lan_allow_subnet_size: The size of the subnet for the local access network. Note that this field is omitted from the response if null or unset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#lan_allow_subnet_size ZeroTrustDeviceDefaultProfile#lan_allow_subnet_size}
        :param register_interface_ip_with_dns: Determines if the operating system will register WARP's local interface IP with your on-premises DNS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#register_interface_ip_with_dns ZeroTrustDeviceDefaultProfile#register_interface_ip_with_dns}
        :param sccm_vpn_boundary_support: Determines whether the WARP client indicates to SCCM that it is inside a VPN boundary. (Windows only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#sccm_vpn_boundary_support ZeroTrustDeviceDefaultProfile#sccm_vpn_boundary_support}
        :param service_mode_v2: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#service_mode_v2 ZeroTrustDeviceDefaultProfile#service_mode_v2}.
        :param support_url: The URL to launch when the Send Feedback button is clicked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#support_url ZeroTrustDeviceDefaultProfile#support_url}
        :param switch_locked: Whether to allow the user to turn off the WARP switch and disconnect the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#switch_locked ZeroTrustDeviceDefaultProfile#switch_locked}
        :param tunnel_protocol: Determines which tunnel protocol to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#tunnel_protocol ZeroTrustDeviceDefaultProfile#tunnel_protocol}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(service_mode_v2, dict):
            service_mode_v2 = ZeroTrustDeviceDefaultProfileServiceModeV2(**service_mode_v2)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48e88582cb4f1e703c95a00fe007638b47068debac3bcfc28805621bb512ce8b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument allowed_to_leave", value=allowed_to_leave, expected_type=type_hints["allowed_to_leave"])
            check_type(argname="argument allow_mode_switch", value=allow_mode_switch, expected_type=type_hints["allow_mode_switch"])
            check_type(argname="argument allow_updates", value=allow_updates, expected_type=type_hints["allow_updates"])
            check_type(argname="argument auto_connect", value=auto_connect, expected_type=type_hints["auto_connect"])
            check_type(argname="argument captive_portal", value=captive_portal, expected_type=type_hints["captive_portal"])
            check_type(argname="argument disable_auto_fallback", value=disable_auto_fallback, expected_type=type_hints["disable_auto_fallback"])
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
        if disable_auto_fallback is not None:
            self._values["disable_auto_fallback"] = disable_auto_fallback
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#account_id ZeroTrustDeviceDefaultProfile#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_to_leave(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to allow devices to leave the organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#allowed_to_leave ZeroTrustDeviceDefaultProfile#allowed_to_leave}
        '''
        result = self._values.get("allowed_to_leave")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_mode_switch(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to allow the user to switch WARP between modes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#allow_mode_switch ZeroTrustDeviceDefaultProfile#allow_mode_switch}
        '''
        result = self._values.get("allow_mode_switch")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_updates(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to receive update notifications when a new version of the client is available.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#allow_updates ZeroTrustDeviceDefaultProfile#allow_updates}
        '''
        result = self._values.get("allow_updates")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_connect(self) -> typing.Optional[jsii.Number]:
        '''The amount of time in seconds to reconnect after having been disabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#auto_connect ZeroTrustDeviceDefaultProfile#auto_connect}
        '''
        result = self._values.get("auto_connect")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def captive_portal(self) -> typing.Optional[jsii.Number]:
        '''Turn on the captive portal after the specified amount of time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#captive_portal ZeroTrustDeviceDefaultProfile#captive_portal}
        '''
        result = self._values.get("captive_portal")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disable_auto_fallback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If the ``dns_server`` field of a fallback domain is not present, the client will fall back to a best guess of the default/system DNS resolvers unless this policy option is set to ``true``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#disable_auto_fallback ZeroTrustDeviceDefaultProfile#disable_auto_fallback}
        '''
        result = self._values.get("disable_auto_fallback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def exclude(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceDefaultProfileExclude"]]]:
        '''List of routes excluded in the WARP client's tunnel.

        Both 'exclude' and 'include' cannot be set in the same request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#exclude ZeroTrustDeviceDefaultProfile#exclude}
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceDefaultProfileExclude"]]], result)

    @builtins.property
    def exclude_office_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to add Microsoft IPs to Split Tunnel exclusions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#exclude_office_ips ZeroTrustDeviceDefaultProfile#exclude_office_ips}
        '''
        result = self._values.get("exclude_office_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def include(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceDefaultProfileInclude"]]]:
        '''List of routes included in the WARP client's tunnel.

        Both 'exclude' and 'include' cannot be set in the same request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#include ZeroTrustDeviceDefaultProfile#include}
        '''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDeviceDefaultProfileInclude"]]], result)

    @builtins.property
    def lan_allow_minutes(self) -> typing.Optional[jsii.Number]:
        '''The amount of time in minutes a user is allowed access to their LAN.

        A value of 0 will allow LAN access until the next WARP reconnection, such as a reboot or a laptop waking from sleep. Note that this field is omitted from the response if null or unset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#lan_allow_minutes ZeroTrustDeviceDefaultProfile#lan_allow_minutes}
        '''
        result = self._values.get("lan_allow_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lan_allow_subnet_size(self) -> typing.Optional[jsii.Number]:
        '''The size of the subnet for the local access network.

        Note that this field is omitted from the response if null or unset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#lan_allow_subnet_size ZeroTrustDeviceDefaultProfile#lan_allow_subnet_size}
        '''
        result = self._values.get("lan_allow_subnet_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def register_interface_ip_with_dns(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines if the operating system will register WARP's local interface IP with your on-premises DNS server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#register_interface_ip_with_dns ZeroTrustDeviceDefaultProfile#register_interface_ip_with_dns}
        '''
        result = self._values.get("register_interface_ip_with_dns")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sccm_vpn_boundary_support(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines whether the WARP client indicates to SCCM that it is inside a VPN boundary. (Windows only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#sccm_vpn_boundary_support ZeroTrustDeviceDefaultProfile#sccm_vpn_boundary_support}
        '''
        result = self._values.get("sccm_vpn_boundary_support")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def service_mode_v2(
        self,
    ) -> typing.Optional["ZeroTrustDeviceDefaultProfileServiceModeV2"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#service_mode_v2 ZeroTrustDeviceDefaultProfile#service_mode_v2}.'''
        result = self._values.get("service_mode_v2")
        return typing.cast(typing.Optional["ZeroTrustDeviceDefaultProfileServiceModeV2"], result)

    @builtins.property
    def support_url(self) -> typing.Optional[builtins.str]:
        '''The URL to launch when the Send Feedback button is clicked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#support_url ZeroTrustDeviceDefaultProfile#support_url}
        '''
        result = self._values.get("support_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def switch_locked(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to allow the user to turn off the WARP switch and disconnect the client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#switch_locked ZeroTrustDeviceDefaultProfile#switch_locked}
        '''
        result = self._values.get("switch_locked")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tunnel_protocol(self) -> typing.Optional[builtins.str]:
        '''Determines which tunnel protocol to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#tunnel_protocol ZeroTrustDeviceDefaultProfile#tunnel_protocol}
        '''
        result = self._values.get("tunnel_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceDefaultProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileExclude",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "description": "description", "host": "host"},
)
class ZeroTrustDeviceDefaultProfileExclude:
    def __init__(
        self,
        *,
        address: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: The address in CIDR format to exclude from the tunnel. If ``address`` is present, ``host`` must not be present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#address ZeroTrustDeviceDefaultProfile#address}
        :param description: A description of the Split Tunnel item, displayed in the client UI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#description ZeroTrustDeviceDefaultProfile#description}
        :param host: The domain name to exclude from the tunnel. If ``host`` is present, ``address`` must not be present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#host ZeroTrustDeviceDefaultProfile#host}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b50c01b2bdad8e0316cab5f2f94822d565336e6ebe57e3f81d4bc7477c6debd1)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#address ZeroTrustDeviceDefaultProfile#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the Split Tunnel item, displayed in the client UI.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#description ZeroTrustDeviceDefaultProfile#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''The domain name to exclude from the tunnel. If ``host`` is present, ``address`` must not be present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#host ZeroTrustDeviceDefaultProfile#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceDefaultProfileExclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDeviceDefaultProfileExcludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileExcludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2b93480d8fc316ece67b0eb3417354de69172e797d4b59354f05bde524d29ef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDeviceDefaultProfileExcludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6947245af01b302e8e54669fed92506bcf49a6f3684ff1f5b0ef131785e10f63)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDeviceDefaultProfileExcludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6dbdd9bfb4f93556c69932d583ba7d99efcf6087fd614ee6bf7b5d00f0d08e5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcf2ec19ae3e8c3f7ffa490dcd4a9362faa0810169ca2475ee366d3524bb8c1e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__553a65de8e65a385a9fcc638280129ef910b35e0ec7994ffbae5363f16f37cd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceDefaultProfileExclude]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceDefaultProfileExclude]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceDefaultProfileExclude]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a61acae9b561590ca4e33220230f8677578d22f9edd686048e9883f7874c2aa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDeviceDefaultProfileExcludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileExcludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba41689cdd042bffe4e50e981ce75ccd3ee224019813c0d45d4fb5f7978b7b8c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd92447f0e2dc569ebd7965049613348d4c27e87b3fdc008ea6fe1a20d3dc3e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fc45b8efb00cb19542c42a982ca6b79dd453544a2ccb3b1ce6e6523578a19f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba89d4552ee9ceb4b16b9f7ec79dd4b2e907c46ae8dc9291d0946cf5b6697988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileExclude]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileExclude]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileExclude]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43c19915d2c753257ad8c8eddf247b2adc8b3ed0fbabc4b75802944d5118a576)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileFallbackDomains",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustDeviceDefaultProfileFallbackDomains:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceDefaultProfileFallbackDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDeviceDefaultProfileFallbackDomainsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileFallbackDomainsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0cdadf6c44116b8e1c4d9b17592f1b952caea2e7abaa8aabcc233c710165b29e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDeviceDefaultProfileFallbackDomainsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5ac50ee216878211829f24a6df328609348adaee7700fa464d283124ff09f7c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDeviceDefaultProfileFallbackDomainsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9409ce7a6dfbb92b730b20c4c13eb5960bd10d30dfcdbbb382c62ce798b3baa4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e9d78b1f155892152d56f5b045192038fdbb12e9d375e46dde91f42135abc72)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5307bc57b82358cb60ddf21a62987cbac4b6512d4694514702d326addd1d2ad4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDeviceDefaultProfileFallbackDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileFallbackDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__afe3f3576de39bc3ab342958344832d3e1a38e2f4d13d4e5c64490db41ff4daa)
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
    ) -> typing.Optional[ZeroTrustDeviceDefaultProfileFallbackDomains]:
        return typing.cast(typing.Optional[ZeroTrustDeviceDefaultProfileFallbackDomains], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ZeroTrustDeviceDefaultProfileFallbackDomains],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f45bcae0a96c4b146d92f4d13992a5fc6bdebf3232aafe5a3b6ee4da093bb576)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileInclude",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "description": "description", "host": "host"},
)
class ZeroTrustDeviceDefaultProfileInclude:
    def __init__(
        self,
        *,
        address: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: The address in CIDR format to include in the tunnel. If ``address`` is present, ``host`` must not be present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#address ZeroTrustDeviceDefaultProfile#address}
        :param description: A description of the Split Tunnel item, displayed in the client UI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#description ZeroTrustDeviceDefaultProfile#description}
        :param host: The domain name to include in the tunnel. If ``host`` is present, ``address`` must not be present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#host ZeroTrustDeviceDefaultProfile#host}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c8a8e1a34374aacb525226e9cf2ebf7542230d327854eba4dcfcb19b03510f6)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#address ZeroTrustDeviceDefaultProfile#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the Split Tunnel item, displayed in the client UI.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#description ZeroTrustDeviceDefaultProfile#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''The domain name to include in the tunnel. If ``host`` is present, ``address`` must not be present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#host ZeroTrustDeviceDefaultProfile#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceDefaultProfileInclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDeviceDefaultProfileIncludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileIncludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81de3e5149ff2ec63d638e14ea5492959087636f2154f2c22335e5bf71bf8052)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDeviceDefaultProfileIncludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dcd69bdafcc4e67e326b3e3da4632604b5e8dd2f2452ece032600e168b04449)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDeviceDefaultProfileIncludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c6bfc2ba89fa2d96e72886be0eed3471e5f355e8e06d68430afc10edcf530ef)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ee0a0fd26432587907970c9d135b27a6956c15e4fb3756d7460fbd9bddfd0bc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e1bb54c87101469c7ebba46a9c725fcdb9d6fd861e4017fc69f5f3cdbc93634d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceDefaultProfileInclude]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceDefaultProfileInclude]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceDefaultProfileInclude]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e926d5bd4f5483fb8abe04cf6252ee42a81f17b93a2d6790776816394ba841f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDeviceDefaultProfileIncludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileIncludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__57610792d7dfd01d093be5021ec212886fa224914e7a9facfffc8f6a499fa00d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d8e81f58dbcd7504d66f97979ca3d71a7f809e398c19c7c73c24d58ae6ff91f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19016b94088565c4b8c3d1421018acde67af283371c7455ba1aa13da6f5a6685)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b874d2a7fbdc56dbd2089ae767697bbba054da8ecb5bf85430f1488405f1edd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileInclude]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileInclude]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileInclude]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2789a66742e52518aab0d44d7cc75ff987bd8fceb55893026c29f50ca711c7d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileServiceModeV2",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "port": "port"},
)
class ZeroTrustDeviceDefaultProfileServiceModeV2:
    def __init__(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mode: The mode to run the WARP client under. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#mode ZeroTrustDeviceDefaultProfile#mode}
        :param port: The port number when used with proxy mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#port ZeroTrustDeviceDefaultProfile#port}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c12940fda3ba6384a6d2a5fd4c3c555153e1c537337d1e7ff504f9b365ab705f)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#mode ZeroTrustDeviceDefaultProfile#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The port number when used with proxy mode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_default_profile#port ZeroTrustDeviceDefaultProfile#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDeviceDefaultProfileServiceModeV2(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDeviceDefaultProfileServiceModeV2OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDeviceDefaultProfile.ZeroTrustDeviceDefaultProfileServiceModeV2OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c0dd8707edd6a03ea8f3cec8d95d581bebb28a981de41f74c1fd7965e37f8a8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__479ff16bd0a2fad5f20525f5ca2e94b9a0bc73a3132b62ee4e3a87e07c97a234)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0acccbdd33cb5413065716730b1e29dd7c4850ef02293601f50dd908858883f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileServiceModeV2]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileServiceModeV2]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileServiceModeV2]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e74704dc1c63950ee0421a304e823480ec6d553d1dd4fa94d4fae9b7905bcfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustDeviceDefaultProfile",
    "ZeroTrustDeviceDefaultProfileConfig",
    "ZeroTrustDeviceDefaultProfileExclude",
    "ZeroTrustDeviceDefaultProfileExcludeList",
    "ZeroTrustDeviceDefaultProfileExcludeOutputReference",
    "ZeroTrustDeviceDefaultProfileFallbackDomains",
    "ZeroTrustDeviceDefaultProfileFallbackDomainsList",
    "ZeroTrustDeviceDefaultProfileFallbackDomainsOutputReference",
    "ZeroTrustDeviceDefaultProfileInclude",
    "ZeroTrustDeviceDefaultProfileIncludeList",
    "ZeroTrustDeviceDefaultProfileIncludeOutputReference",
    "ZeroTrustDeviceDefaultProfileServiceModeV2",
    "ZeroTrustDeviceDefaultProfileServiceModeV2OutputReference",
]

publication.publish()

def _typecheckingstub__fd1e430c3de79ec44c4da667c1fcb7f80da06d10396e1d66ad3373963efaec46(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    allowed_to_leave: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mode_switch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_updates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_connect: typing.Optional[jsii.Number] = None,
    captive_portal: typing.Optional[jsii.Number] = None,
    disable_auto_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceDefaultProfileExclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    exclude_office_ips: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceDefaultProfileInclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    lan_allow_minutes: typing.Optional[jsii.Number] = None,
    lan_allow_subnet_size: typing.Optional[jsii.Number] = None,
    register_interface_ip_with_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sccm_vpn_boundary_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_mode_v2: typing.Optional[typing.Union[ZeroTrustDeviceDefaultProfileServiceModeV2, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__9261cfb32fea9fa03f7dc7ac72f693db10f62e9c72f4b9e585c06ebe13067b87(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__901ff592eee6d1686f429219a70fd8727070163ace349a5d6b02e8cefcaa142d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceDefaultProfileExclude, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f18d732244584b4fde20753fb4c7ad664547c6869d18eb36a509fdf43d1ec776(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceDefaultProfileInclude, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcb6a32ff112b1cb57da98a928efaa2eb0102e7aad9822563330c85bce3cc55f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3461806c5a73af9d0765c43c26e0bcf8fe976843413d4d217ded79b78f6d2dec(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__251c6d266bf6cea09079fb204b78062fb685abacce9aafe74dfb6b217e5537af(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a28f19147ca55ddab0de7c1ad435621b8688ef3aaf23fd7f48bb105e46a7b98e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__177e8cf89521b4f78e6ec9ef78813b853c5671e0809d4ca0cc036fa0c6f78168(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6071bfc30b56743c9e85583ec5f171efc5d7c0d029c6cae6a4a0fceceb602d6d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd7fc9707782004d90aa4345a4bdc9991250094b8003bbec0e923e604851be4f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adeb88d43f173118d01ca3445c64084a7341909ac889838245cfcdb749acd284(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e96e291351d2965a69c8766e667d4f40f10bbf052f0588fff325a05d963d828(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec2a803958f21b38b2541cd3e5c0c16bf21f501a668d438f7662220b3bb249ce(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d721f62beb08b20a285a1533d3fd70160064e295ce4083e9e637ce8819885876(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e107993ba8ec1124c06a0aa66c072aac06e589f1d95c71573aa5fca8457a1f91(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e45b08871bdef2a140ed7b0c170334f89a79371f8142e479de0eed15a722582a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f652ca737e537985a538ec80e5804fee1bc6ec068e2b0622b280a9505d75e63(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__377e7a4dd2b27d01d8047c05730e5ffed6718794068ba3acc26c4ed7debc2781(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48e88582cb4f1e703c95a00fe007638b47068debac3bcfc28805621bb512ce8b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    allowed_to_leave: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mode_switch: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_updates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_connect: typing.Optional[jsii.Number] = None,
    captive_portal: typing.Optional[jsii.Number] = None,
    disable_auto_fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceDefaultProfileExclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    exclude_office_ips: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDeviceDefaultProfileInclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    lan_allow_minutes: typing.Optional[jsii.Number] = None,
    lan_allow_subnet_size: typing.Optional[jsii.Number] = None,
    register_interface_ip_with_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sccm_vpn_boundary_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_mode_v2: typing.Optional[typing.Union[ZeroTrustDeviceDefaultProfileServiceModeV2, typing.Dict[builtins.str, typing.Any]]] = None,
    support_url: typing.Optional[builtins.str] = None,
    switch_locked: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tunnel_protocol: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b50c01b2bdad8e0316cab5f2f94822d565336e6ebe57e3f81d4bc7477c6debd1(
    *,
    address: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2b93480d8fc316ece67b0eb3417354de69172e797d4b59354f05bde524d29ef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6947245af01b302e8e54669fed92506bcf49a6f3684ff1f5b0ef131785e10f63(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6dbdd9bfb4f93556c69932d583ba7d99efcf6087fd614ee6bf7b5d00f0d08e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcf2ec19ae3e8c3f7ffa490dcd4a9362faa0810169ca2475ee366d3524bb8c1e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__553a65de8e65a385a9fcc638280129ef910b35e0ec7994ffbae5363f16f37cd1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a61acae9b561590ca4e33220230f8677578d22f9edd686048e9883f7874c2aa9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceDefaultProfileExclude]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba41689cdd042bffe4e50e981ce75ccd3ee224019813c0d45d4fb5f7978b7b8c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd92447f0e2dc569ebd7965049613348d4c27e87b3fdc008ea6fe1a20d3dc3e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fc45b8efb00cb19542c42a982ca6b79dd453544a2ccb3b1ce6e6523578a19f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba89d4552ee9ceb4b16b9f7ec79dd4b2e907c46ae8dc9291d0946cf5b6697988(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43c19915d2c753257ad8c8eddf247b2adc8b3ed0fbabc4b75802944d5118a576(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileExclude]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cdadf6c44116b8e1c4d9b17592f1b952caea2e7abaa8aabcc233c710165b29e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5ac50ee216878211829f24a6df328609348adaee7700fa464d283124ff09f7c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9409ce7a6dfbb92b730b20c4c13eb5960bd10d30dfcdbbb382c62ce798b3baa4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e9d78b1f155892152d56f5b045192038fdbb12e9d375e46dde91f42135abc72(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5307bc57b82358cb60ddf21a62987cbac4b6512d4694514702d326addd1d2ad4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afe3f3576de39bc3ab342958344832d3e1a38e2f4d13d4e5c64490db41ff4daa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f45bcae0a96c4b146d92f4d13992a5fc6bdebf3232aafe5a3b6ee4da093bb576(
    value: typing.Optional[ZeroTrustDeviceDefaultProfileFallbackDomains],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c8a8e1a34374aacb525226e9cf2ebf7542230d327854eba4dcfcb19b03510f6(
    *,
    address: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81de3e5149ff2ec63d638e14ea5492959087636f2154f2c22335e5bf71bf8052(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dcd69bdafcc4e67e326b3e3da4632604b5e8dd2f2452ece032600e168b04449(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c6bfc2ba89fa2d96e72886be0eed3471e5f355e8e06d68430afc10edcf530ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ee0a0fd26432587907970c9d135b27a6956c15e4fb3756d7460fbd9bddfd0bc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1bb54c87101469c7ebba46a9c725fcdb9d6fd861e4017fc69f5f3cdbc93634d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e926d5bd4f5483fb8abe04cf6252ee42a81f17b93a2d6790776816394ba841f9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDeviceDefaultProfileInclude]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57610792d7dfd01d093be5021ec212886fa224914e7a9facfffc8f6a499fa00d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d8e81f58dbcd7504d66f97979ca3d71a7f809e398c19c7c73c24d58ae6ff91f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19016b94088565c4b8c3d1421018acde67af283371c7455ba1aa13da6f5a6685(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b874d2a7fbdc56dbd2089ae767697bbba054da8ecb5bf85430f1488405f1edd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2789a66742e52518aab0d44d7cc75ff987bd8fceb55893026c29f50ca711c7d5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileInclude]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c12940fda3ba6384a6d2a5fd4c3c555153e1c537337d1e7ff504f9b365ab705f(
    *,
    mode: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c0dd8707edd6a03ea8f3cec8d95d581bebb28a981de41f74c1fd7965e37f8a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__479ff16bd0a2fad5f20525f5ca2e94b9a0bc73a3132b62ee4e3a87e07c97a234(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0acccbdd33cb5413065716730b1e29dd7c4850ef02293601f50dd908858883f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e74704dc1c63950ee0421a304e823480ec6d553d1dd4fa94d4fae9b7905bcfd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDeviceDefaultProfileServiceModeV2]],
) -> None:
    """Type checking stubs"""
    pass
