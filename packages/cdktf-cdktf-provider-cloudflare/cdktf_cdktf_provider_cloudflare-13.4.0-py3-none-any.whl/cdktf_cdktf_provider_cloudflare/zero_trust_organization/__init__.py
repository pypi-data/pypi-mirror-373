r'''
# `cloudflare_zero_trust_organization`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_organization`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization).
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


class ZeroTrustOrganization(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustOrganization.ZeroTrustOrganization",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization cloudflare_zero_trust_organization}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        allow_authenticate_via_warp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auth_domain: typing.Optional[builtins.str] = None,
        auto_redirect_to_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_pages: typing.Optional[typing.Union["ZeroTrustOrganizationCustomPages", typing.Dict[builtins.str, typing.Any]]] = None,
        is_ui_read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        login_design: typing.Optional[typing.Union["ZeroTrustOrganizationLoginDesign", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        session_duration: typing.Optional[builtins.str] = None,
        ui_read_only_toggle_reason: typing.Optional[builtins.str] = None,
        user_seat_expiration_inactive_time: typing.Optional[builtins.str] = None,
        warp_auth_session_duration: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization cloudflare_zero_trust_organization} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#account_id ZeroTrustOrganization#account_id}
        :param allow_authenticate_via_warp: When set to true, users can authenticate via WARP for any application in your organization. Application settings will take precedence over this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#allow_authenticate_via_warp ZeroTrustOrganization#allow_authenticate_via_warp}
        :param auth_domain: The unique subdomain assigned to your Zero Trust organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#auth_domain ZeroTrustOrganization#auth_domain}
        :param auto_redirect_to_identity: When set to ``true``, users skip the identity provider selection step during login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#auto_redirect_to_identity ZeroTrustOrganization#auto_redirect_to_identity}
        :param custom_pages: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#custom_pages ZeroTrustOrganization#custom_pages}.
        :param is_ui_read_only: Lock all settings as Read-Only in the Dashboard, regardless of user permission. Updates may only be made via the API or Terraform for this account when enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#is_ui_read_only ZeroTrustOrganization#is_ui_read_only}
        :param login_design: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#login_design ZeroTrustOrganization#login_design}.
        :param name: The name of your Zero Trust organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#name ZeroTrustOrganization#name}
        :param session_duration: The amount of time that tokens issued for applications will be valid. Must be in the format ``300ms`` or ``2h45m``. Valid time units are: ns, us (or µs), ms, s, m, h. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#session_duration ZeroTrustOrganization#session_duration}
        :param ui_read_only_toggle_reason: A description of the reason why the UI read only field is being toggled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#ui_read_only_toggle_reason ZeroTrustOrganization#ui_read_only_toggle_reason}
        :param user_seat_expiration_inactive_time: The amount of time a user seat is inactive before it expires. When the user seat exceeds the set time of inactivity, the user is removed as an active seat and no longer counts against your Teams seat count. Minimum value for this setting is 1 month (730h). Must be in the format ``300ms`` or ``2h45m``. Valid time units are: ``ns``, ``us`` (or ``µs``), ``ms``, ``s``, ``m``, ``h``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#user_seat_expiration_inactive_time ZeroTrustOrganization#user_seat_expiration_inactive_time}
        :param warp_auth_session_duration: The amount of time that tokens issued for applications will be valid. Must be in the format ``30m`` or ``2h45m``. Valid time units are: m, h. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#warp_auth_session_duration ZeroTrustOrganization#warp_auth_session_duration}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#zone_id ZeroTrustOrganization#zone_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62ab4e1142a20a9f21f585ad4cfc7f20e1ca01e0e702fd44c7a7f85ea4a8c9d4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustOrganizationConfig(
            account_id=account_id,
            allow_authenticate_via_warp=allow_authenticate_via_warp,
            auth_domain=auth_domain,
            auto_redirect_to_identity=auto_redirect_to_identity,
            custom_pages=custom_pages,
            is_ui_read_only=is_ui_read_only,
            login_design=login_design,
            name=name,
            session_duration=session_duration,
            ui_read_only_toggle_reason=ui_read_only_toggle_reason,
            user_seat_expiration_inactive_time=user_seat_expiration_inactive_time,
            warp_auth_session_duration=warp_auth_session_duration,
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
        '''Generates CDKTF code for importing a ZeroTrustOrganization resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustOrganization to import.
        :param import_from_id: The id of the existing ZeroTrustOrganization that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustOrganization to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfa90d8c8f3599369011f562047f6f7ec2556eeede2d757e75f1b781142271aa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCustomPages")
    def put_custom_pages(
        self,
        *,
        forbidden: typing.Optional[builtins.str] = None,
        identity_denied: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param forbidden: The uid of the custom page to use when a user is denied access after failing a non-identity rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#forbidden ZeroTrustOrganization#forbidden}
        :param identity_denied: The uid of the custom page to use when a user is denied access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#identity_denied ZeroTrustOrganization#identity_denied}
        '''
        value = ZeroTrustOrganizationCustomPages(
            forbidden=forbidden, identity_denied=identity_denied
        )

        return typing.cast(None, jsii.invoke(self, "putCustomPages", [value]))

    @jsii.member(jsii_name="putLoginDesign")
    def put_login_design(
        self,
        *,
        background_color: typing.Optional[builtins.str] = None,
        footer_text: typing.Optional[builtins.str] = None,
        header_text: typing.Optional[builtins.str] = None,
        logo_path: typing.Optional[builtins.str] = None,
        text_color: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param background_color: The background color on your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#background_color ZeroTrustOrganization#background_color}
        :param footer_text: The text at the bottom of your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#footer_text ZeroTrustOrganization#footer_text}
        :param header_text: The text at the top of your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#header_text ZeroTrustOrganization#header_text}
        :param logo_path: The URL of the logo on your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#logo_path ZeroTrustOrganization#logo_path}
        :param text_color: The text color on your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#text_color ZeroTrustOrganization#text_color}
        '''
        value = ZeroTrustOrganizationLoginDesign(
            background_color=background_color,
            footer_text=footer_text,
            header_text=header_text,
            logo_path=logo_path,
            text_color=text_color,
        )

        return typing.cast(None, jsii.invoke(self, "putLoginDesign", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetAllowAuthenticateViaWarp")
    def reset_allow_authenticate_via_warp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowAuthenticateViaWarp", []))

    @jsii.member(jsii_name="resetAuthDomain")
    def reset_auth_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthDomain", []))

    @jsii.member(jsii_name="resetAutoRedirectToIdentity")
    def reset_auto_redirect_to_identity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRedirectToIdentity", []))

    @jsii.member(jsii_name="resetCustomPages")
    def reset_custom_pages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomPages", []))

    @jsii.member(jsii_name="resetIsUiReadOnly")
    def reset_is_ui_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsUiReadOnly", []))

    @jsii.member(jsii_name="resetLoginDesign")
    def reset_login_design(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoginDesign", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSessionDuration")
    def reset_session_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionDuration", []))

    @jsii.member(jsii_name="resetUiReadOnlyToggleReason")
    def reset_ui_read_only_toggle_reason(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUiReadOnlyToggleReason", []))

    @jsii.member(jsii_name="resetUserSeatExpirationInactiveTime")
    def reset_user_seat_expiration_inactive_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserSeatExpirationInactiveTime", []))

    @jsii.member(jsii_name="resetWarpAuthSessionDuration")
    def reset_warp_auth_session_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWarpAuthSessionDuration", []))

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
    @jsii.member(jsii_name="customPages")
    def custom_pages(self) -> "ZeroTrustOrganizationCustomPagesOutputReference":
        return typing.cast("ZeroTrustOrganizationCustomPagesOutputReference", jsii.get(self, "customPages"))

    @builtins.property
    @jsii.member(jsii_name="loginDesign")
    def login_design(self) -> "ZeroTrustOrganizationLoginDesignOutputReference":
        return typing.cast("ZeroTrustOrganizationLoginDesignOutputReference", jsii.get(self, "loginDesign"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="allowAuthenticateViaWarpInput")
    def allow_authenticate_via_warp_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowAuthenticateViaWarpInput"))

    @builtins.property
    @jsii.member(jsii_name="authDomainInput")
    def auth_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRedirectToIdentityInput")
    def auto_redirect_to_identity_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoRedirectToIdentityInput"))

    @builtins.property
    @jsii.member(jsii_name="customPagesInput")
    def custom_pages_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustOrganizationCustomPages"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustOrganizationCustomPages"]], jsii.get(self, "customPagesInput"))

    @builtins.property
    @jsii.member(jsii_name="isUiReadOnlyInput")
    def is_ui_read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isUiReadOnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="loginDesignInput")
    def login_design_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustOrganizationLoginDesign"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustOrganizationLoginDesign"]], jsii.get(self, "loginDesignInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionDurationInput")
    def session_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="uiReadOnlyToggleReasonInput")
    def ui_read_only_toggle_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uiReadOnlyToggleReasonInput"))

    @builtins.property
    @jsii.member(jsii_name="userSeatExpirationInactiveTimeInput")
    def user_seat_expiration_inactive_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userSeatExpirationInactiveTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="warpAuthSessionDurationInput")
    def warp_auth_session_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warpAuthSessionDurationInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__711257f822d827038112fb06a9473ae9a74677c64e4749c529e53756eac25ebe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowAuthenticateViaWarp")
    def allow_authenticate_via_warp(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowAuthenticateViaWarp"))

    @allow_authenticate_via_warp.setter
    def allow_authenticate_via_warp(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__797a010c4ada501878457b002a5b6e39e83cd77485aefcd86a4322f598e028af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowAuthenticateViaWarp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authDomain")
    def auth_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authDomain"))

    @auth_domain.setter
    def auth_domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ac58ccd6090217fc966c1df0a70387cbd9a961668ac040de1e5abb78519037a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authDomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoRedirectToIdentity")
    def auto_redirect_to_identity(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoRedirectToIdentity"))

    @auto_redirect_to_identity.setter
    def auto_redirect_to_identity(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3ba5bbcbff620fab98e6ba1a0b081c59c7ad2317581eaf6b5fd78b41a89ccb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRedirectToIdentity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isUiReadOnly")
    def is_ui_read_only(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isUiReadOnly"))

    @is_ui_read_only.setter
    def is_ui_read_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b95dfc4ca55081d41c9179136095bdffd078ff00125a3170baed6853796ca0a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isUiReadOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e71933a90e1bc9d5cea399b5e769ef69ff6c9dc0e524f62db73843a76088f004)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionDuration")
    def session_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionDuration"))

    @session_duration.setter
    def session_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a47529c338def36dfab44ab7e369683e03d1d7f0e053a6dc9d212f3053d51cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uiReadOnlyToggleReason")
    def ui_read_only_toggle_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uiReadOnlyToggleReason"))

    @ui_read_only_toggle_reason.setter
    def ui_read_only_toggle_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1838b0bceddab4dcad3f5d8a593136d460ea4ba47f0ade081d180a88df641918)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uiReadOnlyToggleReason", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userSeatExpirationInactiveTime")
    def user_seat_expiration_inactive_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userSeatExpirationInactiveTime"))

    @user_seat_expiration_inactive_time.setter
    def user_seat_expiration_inactive_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37003259813cdb7306cc5157fe8d17adcdc65407431db97da22411caa487731f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userSeatExpirationInactiveTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warpAuthSessionDuration")
    def warp_auth_session_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warpAuthSessionDuration"))

    @warp_auth_session_duration.setter
    def warp_auth_session_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c44fad6476c147a2dd63171a805b00e26eb664ceb1854a742da2235c324223d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warpAuthSessionDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f47380aa2184084a89e156922612847934eb6476781ecf970e8269584f861a66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustOrganization.ZeroTrustOrganizationConfig",
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
        "allow_authenticate_via_warp": "allowAuthenticateViaWarp",
        "auth_domain": "authDomain",
        "auto_redirect_to_identity": "autoRedirectToIdentity",
        "custom_pages": "customPages",
        "is_ui_read_only": "isUiReadOnly",
        "login_design": "loginDesign",
        "name": "name",
        "session_duration": "sessionDuration",
        "ui_read_only_toggle_reason": "uiReadOnlyToggleReason",
        "user_seat_expiration_inactive_time": "userSeatExpirationInactiveTime",
        "warp_auth_session_duration": "warpAuthSessionDuration",
        "zone_id": "zoneId",
    },
)
class ZeroTrustOrganizationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allow_authenticate_via_warp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auth_domain: typing.Optional[builtins.str] = None,
        auto_redirect_to_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_pages: typing.Optional[typing.Union["ZeroTrustOrganizationCustomPages", typing.Dict[builtins.str, typing.Any]]] = None,
        is_ui_read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        login_design: typing.Optional[typing.Union["ZeroTrustOrganizationLoginDesign", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        session_duration: typing.Optional[builtins.str] = None,
        ui_read_only_toggle_reason: typing.Optional[builtins.str] = None,
        user_seat_expiration_inactive_time: typing.Optional[builtins.str] = None,
        warp_auth_session_duration: typing.Optional[builtins.str] = None,
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
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#account_id ZeroTrustOrganization#account_id}
        :param allow_authenticate_via_warp: When set to true, users can authenticate via WARP for any application in your organization. Application settings will take precedence over this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#allow_authenticate_via_warp ZeroTrustOrganization#allow_authenticate_via_warp}
        :param auth_domain: The unique subdomain assigned to your Zero Trust organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#auth_domain ZeroTrustOrganization#auth_domain}
        :param auto_redirect_to_identity: When set to ``true``, users skip the identity provider selection step during login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#auto_redirect_to_identity ZeroTrustOrganization#auto_redirect_to_identity}
        :param custom_pages: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#custom_pages ZeroTrustOrganization#custom_pages}.
        :param is_ui_read_only: Lock all settings as Read-Only in the Dashboard, regardless of user permission. Updates may only be made via the API or Terraform for this account when enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#is_ui_read_only ZeroTrustOrganization#is_ui_read_only}
        :param login_design: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#login_design ZeroTrustOrganization#login_design}.
        :param name: The name of your Zero Trust organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#name ZeroTrustOrganization#name}
        :param session_duration: The amount of time that tokens issued for applications will be valid. Must be in the format ``300ms`` or ``2h45m``. Valid time units are: ns, us (or µs), ms, s, m, h. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#session_duration ZeroTrustOrganization#session_duration}
        :param ui_read_only_toggle_reason: A description of the reason why the UI read only field is being toggled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#ui_read_only_toggle_reason ZeroTrustOrganization#ui_read_only_toggle_reason}
        :param user_seat_expiration_inactive_time: The amount of time a user seat is inactive before it expires. When the user seat exceeds the set time of inactivity, the user is removed as an active seat and no longer counts against your Teams seat count. Minimum value for this setting is 1 month (730h). Must be in the format ``300ms`` or ``2h45m``. Valid time units are: ``ns``, ``us`` (or ``µs``), ``ms``, ``s``, ``m``, ``h``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#user_seat_expiration_inactive_time ZeroTrustOrganization#user_seat_expiration_inactive_time}
        :param warp_auth_session_duration: The amount of time that tokens issued for applications will be valid. Must be in the format ``30m`` or ``2h45m``. Valid time units are: m, h. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#warp_auth_session_duration ZeroTrustOrganization#warp_auth_session_duration}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#zone_id ZeroTrustOrganization#zone_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(custom_pages, dict):
            custom_pages = ZeroTrustOrganizationCustomPages(**custom_pages)
        if isinstance(login_design, dict):
            login_design = ZeroTrustOrganizationLoginDesign(**login_design)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acdcba3ab6bae49adc45621bedf91cf6af174aa0629a4dfb59d8e664ace9ac99)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument allow_authenticate_via_warp", value=allow_authenticate_via_warp, expected_type=type_hints["allow_authenticate_via_warp"])
            check_type(argname="argument auth_domain", value=auth_domain, expected_type=type_hints["auth_domain"])
            check_type(argname="argument auto_redirect_to_identity", value=auto_redirect_to_identity, expected_type=type_hints["auto_redirect_to_identity"])
            check_type(argname="argument custom_pages", value=custom_pages, expected_type=type_hints["custom_pages"])
            check_type(argname="argument is_ui_read_only", value=is_ui_read_only, expected_type=type_hints["is_ui_read_only"])
            check_type(argname="argument login_design", value=login_design, expected_type=type_hints["login_design"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument session_duration", value=session_duration, expected_type=type_hints["session_duration"])
            check_type(argname="argument ui_read_only_toggle_reason", value=ui_read_only_toggle_reason, expected_type=type_hints["ui_read_only_toggle_reason"])
            check_type(argname="argument user_seat_expiration_inactive_time", value=user_seat_expiration_inactive_time, expected_type=type_hints["user_seat_expiration_inactive_time"])
            check_type(argname="argument warp_auth_session_duration", value=warp_auth_session_duration, expected_type=type_hints["warp_auth_session_duration"])
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
        if allow_authenticate_via_warp is not None:
            self._values["allow_authenticate_via_warp"] = allow_authenticate_via_warp
        if auth_domain is not None:
            self._values["auth_domain"] = auth_domain
        if auto_redirect_to_identity is not None:
            self._values["auto_redirect_to_identity"] = auto_redirect_to_identity
        if custom_pages is not None:
            self._values["custom_pages"] = custom_pages
        if is_ui_read_only is not None:
            self._values["is_ui_read_only"] = is_ui_read_only
        if login_design is not None:
            self._values["login_design"] = login_design
        if name is not None:
            self._values["name"] = name
        if session_duration is not None:
            self._values["session_duration"] = session_duration
        if ui_read_only_toggle_reason is not None:
            self._values["ui_read_only_toggle_reason"] = ui_read_only_toggle_reason
        if user_seat_expiration_inactive_time is not None:
            self._values["user_seat_expiration_inactive_time"] = user_seat_expiration_inactive_time
        if warp_auth_session_duration is not None:
            self._values["warp_auth_session_duration"] = warp_auth_session_duration
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#account_id ZeroTrustOrganization#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allow_authenticate_via_warp(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When set to true, users can authenticate via WARP for any application in your organization.

        Application settings will take precedence over this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#allow_authenticate_via_warp ZeroTrustOrganization#allow_authenticate_via_warp}
        '''
        result = self._values.get("allow_authenticate_via_warp")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auth_domain(self) -> typing.Optional[builtins.str]:
        '''The unique subdomain assigned to your Zero Trust organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#auth_domain ZeroTrustOrganization#auth_domain}
        '''
        result = self._values.get("auth_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_redirect_to_identity(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When set to ``true``, users skip the identity provider selection step during login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#auto_redirect_to_identity ZeroTrustOrganization#auto_redirect_to_identity}
        '''
        result = self._values.get("auto_redirect_to_identity")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def custom_pages(self) -> typing.Optional["ZeroTrustOrganizationCustomPages"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#custom_pages ZeroTrustOrganization#custom_pages}.'''
        result = self._values.get("custom_pages")
        return typing.cast(typing.Optional["ZeroTrustOrganizationCustomPages"], result)

    @builtins.property
    def is_ui_read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Lock all settings as Read-Only in the Dashboard, regardless of user permission.

        Updates may only be made via the API or Terraform for this account when enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#is_ui_read_only ZeroTrustOrganization#is_ui_read_only}
        '''
        result = self._values.get("is_ui_read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def login_design(self) -> typing.Optional["ZeroTrustOrganizationLoginDesign"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#login_design ZeroTrustOrganization#login_design}.'''
        result = self._values.get("login_design")
        return typing.cast(typing.Optional["ZeroTrustOrganizationLoginDesign"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of your Zero Trust organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#name ZeroTrustOrganization#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_duration(self) -> typing.Optional[builtins.str]:
        '''The amount of time that tokens issued for applications will be valid.

        Must be in the format ``300ms`` or ``2h45m``. Valid time units are: ns, us (or µs), ms, s, m, h.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#session_duration ZeroTrustOrganization#session_duration}
        '''
        result = self._values.get("session_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ui_read_only_toggle_reason(self) -> typing.Optional[builtins.str]:
        '''A description of the reason why the UI read only field is being toggled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#ui_read_only_toggle_reason ZeroTrustOrganization#ui_read_only_toggle_reason}
        '''
        result = self._values.get("ui_read_only_toggle_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_seat_expiration_inactive_time(self) -> typing.Optional[builtins.str]:
        '''The amount of time a user seat is inactive before it expires.

        When the user seat exceeds the set time of inactivity, the user is removed as an active seat and no longer counts against your Teams seat count.  Minimum value for this setting is 1 month (730h). Must be in the format ``300ms`` or ``2h45m``. Valid time units are: ``ns``, ``us`` (or ``µs``), ``ms``, ``s``, ``m``, ``h``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#user_seat_expiration_inactive_time ZeroTrustOrganization#user_seat_expiration_inactive_time}
        '''
        result = self._values.get("user_seat_expiration_inactive_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def warp_auth_session_duration(self) -> typing.Optional[builtins.str]:
        '''The amount of time that tokens issued for applications will be valid.

        Must be in the format ``30m`` or ``2h45m``. Valid time units are: m, h.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#warp_auth_session_duration ZeroTrustOrganization#warp_auth_session_duration}
        '''
        result = self._values.get("warp_auth_session_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''The Zone ID to use for this endpoint. Mutually exclusive with the Account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#zone_id ZeroTrustOrganization#zone_id}
        '''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustOrganizationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustOrganization.ZeroTrustOrganizationCustomPages",
    jsii_struct_bases=[],
    name_mapping={"forbidden": "forbidden", "identity_denied": "identityDenied"},
)
class ZeroTrustOrganizationCustomPages:
    def __init__(
        self,
        *,
        forbidden: typing.Optional[builtins.str] = None,
        identity_denied: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param forbidden: The uid of the custom page to use when a user is denied access after failing a non-identity rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#forbidden ZeroTrustOrganization#forbidden}
        :param identity_denied: The uid of the custom page to use when a user is denied access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#identity_denied ZeroTrustOrganization#identity_denied}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81cf167196b4fd1e42e66b76dc511a782cc6ef5eeac5b375e0196cf22dbdf9b3)
            check_type(argname="argument forbidden", value=forbidden, expected_type=type_hints["forbidden"])
            check_type(argname="argument identity_denied", value=identity_denied, expected_type=type_hints["identity_denied"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if forbidden is not None:
            self._values["forbidden"] = forbidden
        if identity_denied is not None:
            self._values["identity_denied"] = identity_denied

    @builtins.property
    def forbidden(self) -> typing.Optional[builtins.str]:
        '''The uid of the custom page to use when a user is denied access after failing a non-identity rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#forbidden ZeroTrustOrganization#forbidden}
        '''
        result = self._values.get("forbidden")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_denied(self) -> typing.Optional[builtins.str]:
        '''The uid of the custom page to use when a user is denied access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#identity_denied ZeroTrustOrganization#identity_denied}
        '''
        result = self._values.get("identity_denied")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustOrganizationCustomPages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustOrganizationCustomPagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustOrganization.ZeroTrustOrganizationCustomPagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c6327edbdadcd9e5ff7b5208ec4f84dd609e2e6676cb96a4ffe8fa7a5b0aec3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetForbidden")
    def reset_forbidden(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForbidden", []))

    @jsii.member(jsii_name="resetIdentityDenied")
    def reset_identity_denied(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityDenied", []))

    @builtins.property
    @jsii.member(jsii_name="forbiddenInput")
    def forbidden_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "forbiddenInput"))

    @builtins.property
    @jsii.member(jsii_name="identityDeniedInput")
    def identity_denied_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityDeniedInput"))

    @builtins.property
    @jsii.member(jsii_name="forbidden")
    def forbidden(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forbidden"))

    @forbidden.setter
    def forbidden(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80534ac07508ff100aa2588626ea73da8ca5c657d156fc10fb1c2763ec1b2d15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forbidden", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityDenied")
    def identity_denied(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityDenied"))

    @identity_denied.setter
    def identity_denied(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8738fff563f33786921c3a1027a7ff6f2b7126c15ef711c6449b215544f737f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityDenied", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustOrganizationCustomPages]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustOrganizationCustomPages]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustOrganizationCustomPages]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__961409026b50016306209cbf5a5c62b57094066a22317b17b65c583bcf1d222e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustOrganization.ZeroTrustOrganizationLoginDesign",
    jsii_struct_bases=[],
    name_mapping={
        "background_color": "backgroundColor",
        "footer_text": "footerText",
        "header_text": "headerText",
        "logo_path": "logoPath",
        "text_color": "textColor",
    },
)
class ZeroTrustOrganizationLoginDesign:
    def __init__(
        self,
        *,
        background_color: typing.Optional[builtins.str] = None,
        footer_text: typing.Optional[builtins.str] = None,
        header_text: typing.Optional[builtins.str] = None,
        logo_path: typing.Optional[builtins.str] = None,
        text_color: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param background_color: The background color on your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#background_color ZeroTrustOrganization#background_color}
        :param footer_text: The text at the bottom of your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#footer_text ZeroTrustOrganization#footer_text}
        :param header_text: The text at the top of your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#header_text ZeroTrustOrganization#header_text}
        :param logo_path: The URL of the logo on your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#logo_path ZeroTrustOrganization#logo_path}
        :param text_color: The text color on your login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#text_color ZeroTrustOrganization#text_color}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8c1b8954e3359b87b92195af9a5990f09d0b6a5629634f06cc59c186c31f9a3)
            check_type(argname="argument background_color", value=background_color, expected_type=type_hints["background_color"])
            check_type(argname="argument footer_text", value=footer_text, expected_type=type_hints["footer_text"])
            check_type(argname="argument header_text", value=header_text, expected_type=type_hints["header_text"])
            check_type(argname="argument logo_path", value=logo_path, expected_type=type_hints["logo_path"])
            check_type(argname="argument text_color", value=text_color, expected_type=type_hints["text_color"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if background_color is not None:
            self._values["background_color"] = background_color
        if footer_text is not None:
            self._values["footer_text"] = footer_text
        if header_text is not None:
            self._values["header_text"] = header_text
        if logo_path is not None:
            self._values["logo_path"] = logo_path
        if text_color is not None:
            self._values["text_color"] = text_color

    @builtins.property
    def background_color(self) -> typing.Optional[builtins.str]:
        '''The background color on your login page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#background_color ZeroTrustOrganization#background_color}
        '''
        result = self._values.get("background_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def footer_text(self) -> typing.Optional[builtins.str]:
        '''The text at the bottom of your login page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#footer_text ZeroTrustOrganization#footer_text}
        '''
        result = self._values.get("footer_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def header_text(self) -> typing.Optional[builtins.str]:
        '''The text at the top of your login page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#header_text ZeroTrustOrganization#header_text}
        '''
        result = self._values.get("header_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logo_path(self) -> typing.Optional[builtins.str]:
        '''The URL of the logo on your login page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#logo_path ZeroTrustOrganization#logo_path}
        '''
        result = self._values.get("logo_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def text_color(self) -> typing.Optional[builtins.str]:
        '''The text color on your login page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_organization#text_color ZeroTrustOrganization#text_color}
        '''
        result = self._values.get("text_color")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustOrganizationLoginDesign(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustOrganizationLoginDesignOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustOrganization.ZeroTrustOrganizationLoginDesignOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a65f34a8f2a77a8f70ace00f24c246383ee79421d62012c16ef253ad373de950)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBackgroundColor")
    def reset_background_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackgroundColor", []))

    @jsii.member(jsii_name="resetFooterText")
    def reset_footer_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFooterText", []))

    @jsii.member(jsii_name="resetHeaderText")
    def reset_header_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaderText", []))

    @jsii.member(jsii_name="resetLogoPath")
    def reset_logo_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogoPath", []))

    @jsii.member(jsii_name="resetTextColor")
    def reset_text_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTextColor", []))

    @builtins.property
    @jsii.member(jsii_name="backgroundColorInput")
    def background_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backgroundColorInput"))

    @builtins.property
    @jsii.member(jsii_name="footerTextInput")
    def footer_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "footerTextInput"))

    @builtins.property
    @jsii.member(jsii_name="headerTextInput")
    def header_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerTextInput"))

    @builtins.property
    @jsii.member(jsii_name="logoPathInput")
    def logo_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logoPathInput"))

    @builtins.property
    @jsii.member(jsii_name="textColorInput")
    def text_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "textColorInput"))

    @builtins.property
    @jsii.member(jsii_name="backgroundColor")
    def background_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backgroundColor"))

    @background_color.setter
    def background_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57950dd58efa10d8ac7996b8ec36210a108a3faf55acfc524318598e23adc949)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backgroundColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="footerText")
    def footer_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "footerText"))

    @footer_text.setter
    def footer_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0a3b6b4de969353a06a868a0404805d4227bc47cadbcf6f5e540afa26d9249e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "footerText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headerText")
    def header_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerText"))

    @header_text.setter
    def header_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__758707c4884d21ce910531885452534f935f541050faecb277aa720a91bfc718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headerText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logoPath")
    def logo_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logoPath"))

    @logo_path.setter
    def logo_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__718d0f018079e04a03eaf5ad324a2d7a71f1a8b5bb2e6d8faf4dffbd8a52b70c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logoPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="textColor")
    def text_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "textColor"))

    @text_color.setter
    def text_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__493170e0e886c4352f797468dd7c79ff91b3d497672c6e2fd6b04b1f13d0b5dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "textColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustOrganizationLoginDesign]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustOrganizationLoginDesign]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustOrganizationLoginDesign]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8c293a70d23abfa817de16dd21851acb664790d457b96fd7175bfa16f07a77d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustOrganization",
    "ZeroTrustOrganizationConfig",
    "ZeroTrustOrganizationCustomPages",
    "ZeroTrustOrganizationCustomPagesOutputReference",
    "ZeroTrustOrganizationLoginDesign",
    "ZeroTrustOrganizationLoginDesignOutputReference",
]

publication.publish()

def _typecheckingstub__62ab4e1142a20a9f21f585ad4cfc7f20e1ca01e0e702fd44c7a7f85ea4a8c9d4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    allow_authenticate_via_warp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auth_domain: typing.Optional[builtins.str] = None,
    auto_redirect_to_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_pages: typing.Optional[typing.Union[ZeroTrustOrganizationCustomPages, typing.Dict[builtins.str, typing.Any]]] = None,
    is_ui_read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    login_design: typing.Optional[typing.Union[ZeroTrustOrganizationLoginDesign, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    session_duration: typing.Optional[builtins.str] = None,
    ui_read_only_toggle_reason: typing.Optional[builtins.str] = None,
    user_seat_expiration_inactive_time: typing.Optional[builtins.str] = None,
    warp_auth_session_duration: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__cfa90d8c8f3599369011f562047f6f7ec2556eeede2d757e75f1b781142271aa(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__711257f822d827038112fb06a9473ae9a74677c64e4749c529e53756eac25ebe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__797a010c4ada501878457b002a5b6e39e83cd77485aefcd86a4322f598e028af(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ac58ccd6090217fc966c1df0a70387cbd9a961668ac040de1e5abb78519037a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3ba5bbcbff620fab98e6ba1a0b081c59c7ad2317581eaf6b5fd78b41a89ccb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b95dfc4ca55081d41c9179136095bdffd078ff00125a3170baed6853796ca0a1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e71933a90e1bc9d5cea399b5e769ef69ff6c9dc0e524f62db73843a76088f004(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a47529c338def36dfab44ab7e369683e03d1d7f0e053a6dc9d212f3053d51cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1838b0bceddab4dcad3f5d8a593136d460ea4ba47f0ade081d180a88df641918(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37003259813cdb7306cc5157fe8d17adcdc65407431db97da22411caa487731f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c44fad6476c147a2dd63171a805b00e26eb664ceb1854a742da2235c324223d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f47380aa2184084a89e156922612847934eb6476781ecf970e8269584f861a66(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acdcba3ab6bae49adc45621bedf91cf6af174aa0629a4dfb59d8e664ace9ac99(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: typing.Optional[builtins.str] = None,
    allow_authenticate_via_warp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auth_domain: typing.Optional[builtins.str] = None,
    auto_redirect_to_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_pages: typing.Optional[typing.Union[ZeroTrustOrganizationCustomPages, typing.Dict[builtins.str, typing.Any]]] = None,
    is_ui_read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    login_design: typing.Optional[typing.Union[ZeroTrustOrganizationLoginDesign, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    session_duration: typing.Optional[builtins.str] = None,
    ui_read_only_toggle_reason: typing.Optional[builtins.str] = None,
    user_seat_expiration_inactive_time: typing.Optional[builtins.str] = None,
    warp_auth_session_duration: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81cf167196b4fd1e42e66b76dc511a782cc6ef5eeac5b375e0196cf22dbdf9b3(
    *,
    forbidden: typing.Optional[builtins.str] = None,
    identity_denied: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c6327edbdadcd9e5ff7b5208ec4f84dd609e2e6676cb96a4ffe8fa7a5b0aec3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80534ac07508ff100aa2588626ea73da8ca5c657d156fc10fb1c2763ec1b2d15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8738fff563f33786921c3a1027a7ff6f2b7126c15ef711c6449b215544f737f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__961409026b50016306209cbf5a5c62b57094066a22317b17b65c583bcf1d222e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustOrganizationCustomPages]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8c1b8954e3359b87b92195af9a5990f09d0b6a5629634f06cc59c186c31f9a3(
    *,
    background_color: typing.Optional[builtins.str] = None,
    footer_text: typing.Optional[builtins.str] = None,
    header_text: typing.Optional[builtins.str] = None,
    logo_path: typing.Optional[builtins.str] = None,
    text_color: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a65f34a8f2a77a8f70ace00f24c246383ee79421d62012c16ef253ad373de950(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57950dd58efa10d8ac7996b8ec36210a108a3faf55acfc524318598e23adc949(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a3b6b4de969353a06a868a0404805d4227bc47cadbcf6f5e540afa26d9249e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__758707c4884d21ce910531885452534f935f541050faecb277aa720a91bfc718(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__718d0f018079e04a03eaf5ad324a2d7a71f1a8b5bb2e6d8faf4dffbd8a52b70c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__493170e0e886c4352f797468dd7c79ff91b3d497672c6e2fd6b04b1f13d0b5dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8c293a70d23abfa817de16dd21851acb664790d457b96fd7175bfa16f07a77d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustOrganizationLoginDesign]],
) -> None:
    """Type checking stubs"""
    pass
