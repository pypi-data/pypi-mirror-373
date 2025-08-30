r'''
# `cloudflare_zero_trust_access_identity_provider`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_access_identity_provider`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider).
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


class ZeroTrustAccessIdentityProvider(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessIdentityProvider.ZeroTrustAccessIdentityProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider cloudflare_zero_trust_access_identity_provider}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        config: typing.Union["ZeroTrustAccessIdentityProviderConfigA", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        type: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        scim_config: typing.Optional[typing.Union["ZeroTrustAccessIdentityProviderScimConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        zone_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider cloudflare_zero_trust_access_identity_provider} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param config: The configuration parameters for the identity provider. To view the required parameters for a specific provider, refer to our `developer documentation <https://developers.cloudflare.com/cloudflare-one/identity/idp-integration/>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#config ZeroTrustAccessIdentityProvider#config}
        :param name: The name of the identity provider, shown to users on the login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#name ZeroTrustAccessIdentityProvider#name}
        :param type: The type of identity provider. To determine the value for a specific provider, refer to our `developer documentation <https://developers.cloudflare.com/cloudflare-one/identity/idp-integration/>`_. Available values: "onetimepin", "azureAD", "saml", "centrify", "facebook", "github", "google-apps", "google", "linkedin", "oidc", "okta", "onelogin", "pingone", "yandex". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#type ZeroTrustAccessIdentityProvider#type}
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#account_id ZeroTrustAccessIdentityProvider#account_id}
        :param scim_config: The configuration settings for enabling a System for Cross-Domain Identity Management (SCIM) with the identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#scim_config ZeroTrustAccessIdentityProvider#scim_config}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#zone_id ZeroTrustAccessIdentityProvider#zone_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b6fd0822ba9fc801cfa64394eaa38aa130771cae55579d4b55196ecfa4c927)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config_ = ZeroTrustAccessIdentityProviderConfig(
            config=config,
            name=name,
            type=type,
            account_id=account_id,
            scim_config=scim_config,
            zone_id=zone_id,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ZeroTrustAccessIdentityProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustAccessIdentityProvider to import.
        :param import_from_id: The id of the existing ZeroTrustAccessIdentityProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustAccessIdentityProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95a93e9f5e6406dad638d4ce84e07b5cd4331bd3e68c409ac14c0c119b1265e7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        apps_domain: typing.Optional[builtins.str] = None,
        attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorization_server_id: typing.Optional[builtins.str] = None,
        auth_url: typing.Optional[builtins.str] = None,
        centrify_account: typing.Optional[builtins.str] = None,
        centrify_app_id: typing.Optional[builtins.str] = None,
        certs_url: typing.Optional[builtins.str] = None,
        claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        conditional_access_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        directory_id: typing.Optional[builtins.str] = None,
        email_attribute_name: typing.Optional[builtins.str] = None,
        email_claim_name: typing.Optional[builtins.str] = None,
        header_attributes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessIdentityProviderConfigHeaderAttributes", typing.Dict[builtins.str, typing.Any]]]]] = None,
        idp_public_certs: typing.Optional[typing.Sequence[builtins.str]] = None,
        issuer_url: typing.Optional[builtins.str] = None,
        okta_account: typing.Optional[builtins.str] = None,
        onelogin_account: typing.Optional[builtins.str] = None,
        ping_env_id: typing.Optional[builtins.str] = None,
        pkce_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        prompt: typing.Optional[builtins.str] = None,
        scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        sign_request: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sso_target_url: typing.Optional[builtins.str] = None,
        support_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param apps_domain: Your companies TLD. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#apps_domain ZeroTrustAccessIdentityProvider#apps_domain}
        :param attributes: A list of SAML attribute names that will be added to your signed JWT token and can be used in SAML policy rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#attributes ZeroTrustAccessIdentityProvider#attributes}
        :param authorization_server_id: Your okta authorization server id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#authorization_server_id ZeroTrustAccessIdentityProvider#authorization_server_id}
        :param auth_url: The authorization_endpoint URL of your IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#auth_url ZeroTrustAccessIdentityProvider#auth_url}
        :param centrify_account: Your centrify account url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#centrify_account ZeroTrustAccessIdentityProvider#centrify_account}
        :param centrify_app_id: Your centrify app id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#centrify_app_id ZeroTrustAccessIdentityProvider#centrify_app_id}
        :param certs_url: The jwks_uri endpoint of your IdP to allow the IdP keys to sign the tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#certs_url ZeroTrustAccessIdentityProvider#certs_url}
        :param claims: Custom claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#claims ZeroTrustAccessIdentityProvider#claims}
        :param client_id: Your OAuth Client ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#client_id ZeroTrustAccessIdentityProvider#client_id}
        :param client_secret: Your OAuth Client Secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#client_secret ZeroTrustAccessIdentityProvider#client_secret}
        :param conditional_access_enabled: Should Cloudflare try to load authentication contexts from your account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#conditional_access_enabled ZeroTrustAccessIdentityProvider#conditional_access_enabled}
        :param directory_id: Your Azure directory uuid. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#directory_id ZeroTrustAccessIdentityProvider#directory_id}
        :param email_attribute_name: The attribute name for email in the SAML response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#email_attribute_name ZeroTrustAccessIdentityProvider#email_attribute_name}
        :param email_claim_name: The claim name for email in the id_token response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#email_claim_name ZeroTrustAccessIdentityProvider#email_claim_name}
        :param header_attributes: Add a list of attribute names that will be returned in the response header from the Access callback. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#header_attributes ZeroTrustAccessIdentityProvider#header_attributes}
        :param idp_public_certs: X509 certificate to verify the signature in the SAML authentication response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#idp_public_certs ZeroTrustAccessIdentityProvider#idp_public_certs}
        :param issuer_url: IdP Entity ID or Issuer URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#issuer_url ZeroTrustAccessIdentityProvider#issuer_url}
        :param okta_account: Your okta account url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#okta_account ZeroTrustAccessIdentityProvider#okta_account}
        :param onelogin_account: Your OneLogin account url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#onelogin_account ZeroTrustAccessIdentityProvider#onelogin_account}
        :param ping_env_id: Your PingOne environment identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#ping_env_id ZeroTrustAccessIdentityProvider#ping_env_id}
        :param pkce_enabled: Enable Proof Key for Code Exchange (PKCE). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#pkce_enabled ZeroTrustAccessIdentityProvider#pkce_enabled}
        :param prompt: Indicates the type of user interaction that is required. prompt=login forces the user to enter their credentials on that request, negating single-sign on. prompt=none is the opposite. It ensures that the user isn't presented with any interactive prompt. If the request can't be completed silently by using single-sign on, the Microsoft identity platform returns an interaction_required error. prompt=select_account interrupts single sign-on providing account selection experience listing all the accounts either in session or any remembered account or an option to choose to use a different account altogether. Available values: "login", "select_account", "none". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#prompt ZeroTrustAccessIdentityProvider#prompt}
        :param scopes: OAuth scopes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#scopes ZeroTrustAccessIdentityProvider#scopes}
        :param sign_request: Sign the SAML authentication request with Access credentials. To verify the signature, use the public key from the Access certs endpoints. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#sign_request ZeroTrustAccessIdentityProvider#sign_request}
        :param sso_target_url: URL to send the SAML authentication requests to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#sso_target_url ZeroTrustAccessIdentityProvider#sso_target_url}
        :param support_groups: Should Cloudflare try to load groups from your account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#support_groups ZeroTrustAccessIdentityProvider#support_groups}
        :param token_url: The token_endpoint URL of your IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#token_url ZeroTrustAccessIdentityProvider#token_url}
        '''
        value = ZeroTrustAccessIdentityProviderConfigA(
            apps_domain=apps_domain,
            attributes=attributes,
            authorization_server_id=authorization_server_id,
            auth_url=auth_url,
            centrify_account=centrify_account,
            centrify_app_id=centrify_app_id,
            certs_url=certs_url,
            claims=claims,
            client_id=client_id,
            client_secret=client_secret,
            conditional_access_enabled=conditional_access_enabled,
            directory_id=directory_id,
            email_attribute_name=email_attribute_name,
            email_claim_name=email_claim_name,
            header_attributes=header_attributes,
            idp_public_certs=idp_public_certs,
            issuer_url=issuer_url,
            okta_account=okta_account,
            onelogin_account=onelogin_account,
            ping_env_id=ping_env_id,
            pkce_enabled=pkce_enabled,
            prompt=prompt,
            scopes=scopes,
            sign_request=sign_request,
            sso_target_url=sso_target_url,
            support_groups=support_groups,
            token_url=token_url,
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="putScimConfig")
    def put_scim_config(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        identity_update_behavior: typing.Optional[builtins.str] = None,
        seat_deprovision: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        user_deprovision: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: A flag to enable or disable SCIM for the identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#enabled ZeroTrustAccessIdentityProvider#enabled}
        :param identity_update_behavior: Indicates how a SCIM event updates a user identity used for policy evaluation. Use "automatic" to automatically update a user's identity and augment it with fields from the SCIM user resource. Use "reauth" to force re-authentication on group membership updates, user identity update will only occur after successful re-authentication. With "reauth" identities will not contain fields from the SCIM user resource. With "no_action" identities will not be changed by SCIM updates in any way and users will not be prompted to reauthenticate. Available values: "automatic", "reauth", "no_action". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#identity_update_behavior ZeroTrustAccessIdentityProvider#identity_update_behavior}
        :param seat_deprovision: A flag to remove a user's seat in Zero Trust when they have been deprovisioned in the Identity Provider. This cannot be enabled unless user_deprovision is also enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#seat_deprovision ZeroTrustAccessIdentityProvider#seat_deprovision}
        :param user_deprovision: A flag to enable revoking a user's session in Access and Gateway when they have been deprovisioned in the Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#user_deprovision ZeroTrustAccessIdentityProvider#user_deprovision}
        '''
        value = ZeroTrustAccessIdentityProviderScimConfig(
            enabled=enabled,
            identity_update_behavior=identity_update_behavior,
            seat_deprovision=seat_deprovision,
            user_deprovision=user_deprovision,
        )

        return typing.cast(None, jsii.invoke(self, "putScimConfig", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetScimConfig")
    def reset_scim_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScimConfig", []))

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
    @jsii.member(jsii_name="config")
    def config(self) -> "ZeroTrustAccessIdentityProviderConfigAOutputReference":
        return typing.cast("ZeroTrustAccessIdentityProviderConfigAOutputReference", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="scimConfig")
    def scim_config(self) -> "ZeroTrustAccessIdentityProviderScimConfigOutputReference":
        return typing.cast("ZeroTrustAccessIdentityProviderScimConfigOutputReference", jsii.get(self, "scimConfig"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessIdentityProviderConfigA"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessIdentityProviderConfigA"]], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="scimConfigInput")
    def scim_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessIdentityProviderScimConfig"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessIdentityProviderScimConfig"]], jsii.get(self, "scimConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__b3c13fe9846cbbb98e08c4d361a3e58e7aecaa13810a65adae682d16604effa0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f32fb4ae5420a2de675d0b6a4cc781df7b5bd54905ace0b7220f101e2cd0c12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9196e2522fb2c9aa41e54b74894604180266fc797af81dd47610a2f86906b376)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12d8ec068925129c4ecd3a4ae93b3aa4fb14dd04e13b0e4e5f633a3a82910f12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessIdentityProvider.ZeroTrustAccessIdentityProviderConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "config": "config",
        "name": "name",
        "type": "type",
        "account_id": "accountId",
        "scim_config": "scimConfig",
        "zone_id": "zoneId",
    },
)
class ZeroTrustAccessIdentityProviderConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        config: typing.Union["ZeroTrustAccessIdentityProviderConfigA", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        type: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        scim_config: typing.Optional[typing.Union["ZeroTrustAccessIdentityProviderScimConfig", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param config: The configuration parameters for the identity provider. To view the required parameters for a specific provider, refer to our `developer documentation <https://developers.cloudflare.com/cloudflare-one/identity/idp-integration/>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#config ZeroTrustAccessIdentityProvider#config}
        :param name: The name of the identity provider, shown to users on the login page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#name ZeroTrustAccessIdentityProvider#name}
        :param type: The type of identity provider. To determine the value for a specific provider, refer to our `developer documentation <https://developers.cloudflare.com/cloudflare-one/identity/idp-integration/>`_. Available values: "onetimepin", "azureAD", "saml", "centrify", "facebook", "github", "google-apps", "google", "linkedin", "oidc", "okta", "onelogin", "pingone", "yandex". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#type ZeroTrustAccessIdentityProvider#type}
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#account_id ZeroTrustAccessIdentityProvider#account_id}
        :param scim_config: The configuration settings for enabling a System for Cross-Domain Identity Management (SCIM) with the identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#scim_config ZeroTrustAccessIdentityProvider#scim_config}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#zone_id ZeroTrustAccessIdentityProvider#zone_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(config, dict):
            config = ZeroTrustAccessIdentityProviderConfigA(**config)
        if isinstance(scim_config, dict):
            scim_config = ZeroTrustAccessIdentityProviderScimConfig(**scim_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c533353ecd98e1c6ca56d019306578d8a618a4ecc1e8db45e4bdf738e18ce696)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument scim_config", value=scim_config, expected_type=type_hints["scim_config"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "config": config,
            "name": name,
            "type": type,
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if scim_config is not None:
            self._values["scim_config"] = scim_config
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
    def config(self) -> "ZeroTrustAccessIdentityProviderConfigA":
        '''The configuration parameters for the identity provider.

        To view the required parameters for a specific provider, refer to our `developer documentation <https://developers.cloudflare.com/cloudflare-one/identity/idp-integration/>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#config ZeroTrustAccessIdentityProvider#config}
        '''
        result = self._values.get("config")
        assert result is not None, "Required property 'config' is missing"
        return typing.cast("ZeroTrustAccessIdentityProviderConfigA", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the identity provider, shown to users on the login page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#name ZeroTrustAccessIdentityProvider#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of identity provider.

        To determine the value for a specific provider, refer to our `developer documentation <https://developers.cloudflare.com/cloudflare-one/identity/idp-integration/>`_.
        Available values: "onetimepin", "azureAD", "saml", "centrify", "facebook", "github", "google-apps", "google", "linkedin", "oidc", "okta", "onelogin", "pingone", "yandex".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#type ZeroTrustAccessIdentityProvider#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''The Account ID to use for this endpoint. Mutually exclusive with the Zone ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#account_id ZeroTrustAccessIdentityProvider#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scim_config(
        self,
    ) -> typing.Optional["ZeroTrustAccessIdentityProviderScimConfig"]:
        '''The configuration settings for enabling a System for Cross-Domain Identity Management (SCIM) with the identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#scim_config ZeroTrustAccessIdentityProvider#scim_config}
        '''
        result = self._values.get("scim_config")
        return typing.cast(typing.Optional["ZeroTrustAccessIdentityProviderScimConfig"], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''The Zone ID to use for this endpoint. Mutually exclusive with the Account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#zone_id ZeroTrustAccessIdentityProvider#zone_id}
        '''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessIdentityProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessIdentityProvider.ZeroTrustAccessIdentityProviderConfigA",
    jsii_struct_bases=[],
    name_mapping={
        "apps_domain": "appsDomain",
        "attributes": "attributes",
        "authorization_server_id": "authorizationServerId",
        "auth_url": "authUrl",
        "centrify_account": "centrifyAccount",
        "centrify_app_id": "centrifyAppId",
        "certs_url": "certsUrl",
        "claims": "claims",
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "conditional_access_enabled": "conditionalAccessEnabled",
        "directory_id": "directoryId",
        "email_attribute_name": "emailAttributeName",
        "email_claim_name": "emailClaimName",
        "header_attributes": "headerAttributes",
        "idp_public_certs": "idpPublicCerts",
        "issuer_url": "issuerUrl",
        "okta_account": "oktaAccount",
        "onelogin_account": "oneloginAccount",
        "ping_env_id": "pingEnvId",
        "pkce_enabled": "pkceEnabled",
        "prompt": "prompt",
        "scopes": "scopes",
        "sign_request": "signRequest",
        "sso_target_url": "ssoTargetUrl",
        "support_groups": "supportGroups",
        "token_url": "tokenUrl",
    },
)
class ZeroTrustAccessIdentityProviderConfigA:
    def __init__(
        self,
        *,
        apps_domain: typing.Optional[builtins.str] = None,
        attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorization_server_id: typing.Optional[builtins.str] = None,
        auth_url: typing.Optional[builtins.str] = None,
        centrify_account: typing.Optional[builtins.str] = None,
        centrify_app_id: typing.Optional[builtins.str] = None,
        certs_url: typing.Optional[builtins.str] = None,
        claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        conditional_access_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        directory_id: typing.Optional[builtins.str] = None,
        email_attribute_name: typing.Optional[builtins.str] = None,
        email_claim_name: typing.Optional[builtins.str] = None,
        header_attributes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessIdentityProviderConfigHeaderAttributes", typing.Dict[builtins.str, typing.Any]]]]] = None,
        idp_public_certs: typing.Optional[typing.Sequence[builtins.str]] = None,
        issuer_url: typing.Optional[builtins.str] = None,
        okta_account: typing.Optional[builtins.str] = None,
        onelogin_account: typing.Optional[builtins.str] = None,
        ping_env_id: typing.Optional[builtins.str] = None,
        pkce_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        prompt: typing.Optional[builtins.str] = None,
        scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        sign_request: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sso_target_url: typing.Optional[builtins.str] = None,
        support_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param apps_domain: Your companies TLD. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#apps_domain ZeroTrustAccessIdentityProvider#apps_domain}
        :param attributes: A list of SAML attribute names that will be added to your signed JWT token and can be used in SAML policy rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#attributes ZeroTrustAccessIdentityProvider#attributes}
        :param authorization_server_id: Your okta authorization server id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#authorization_server_id ZeroTrustAccessIdentityProvider#authorization_server_id}
        :param auth_url: The authorization_endpoint URL of your IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#auth_url ZeroTrustAccessIdentityProvider#auth_url}
        :param centrify_account: Your centrify account url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#centrify_account ZeroTrustAccessIdentityProvider#centrify_account}
        :param centrify_app_id: Your centrify app id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#centrify_app_id ZeroTrustAccessIdentityProvider#centrify_app_id}
        :param certs_url: The jwks_uri endpoint of your IdP to allow the IdP keys to sign the tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#certs_url ZeroTrustAccessIdentityProvider#certs_url}
        :param claims: Custom claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#claims ZeroTrustAccessIdentityProvider#claims}
        :param client_id: Your OAuth Client ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#client_id ZeroTrustAccessIdentityProvider#client_id}
        :param client_secret: Your OAuth Client Secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#client_secret ZeroTrustAccessIdentityProvider#client_secret}
        :param conditional_access_enabled: Should Cloudflare try to load authentication contexts from your account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#conditional_access_enabled ZeroTrustAccessIdentityProvider#conditional_access_enabled}
        :param directory_id: Your Azure directory uuid. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#directory_id ZeroTrustAccessIdentityProvider#directory_id}
        :param email_attribute_name: The attribute name for email in the SAML response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#email_attribute_name ZeroTrustAccessIdentityProvider#email_attribute_name}
        :param email_claim_name: The claim name for email in the id_token response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#email_claim_name ZeroTrustAccessIdentityProvider#email_claim_name}
        :param header_attributes: Add a list of attribute names that will be returned in the response header from the Access callback. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#header_attributes ZeroTrustAccessIdentityProvider#header_attributes}
        :param idp_public_certs: X509 certificate to verify the signature in the SAML authentication response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#idp_public_certs ZeroTrustAccessIdentityProvider#idp_public_certs}
        :param issuer_url: IdP Entity ID or Issuer URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#issuer_url ZeroTrustAccessIdentityProvider#issuer_url}
        :param okta_account: Your okta account url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#okta_account ZeroTrustAccessIdentityProvider#okta_account}
        :param onelogin_account: Your OneLogin account url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#onelogin_account ZeroTrustAccessIdentityProvider#onelogin_account}
        :param ping_env_id: Your PingOne environment identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#ping_env_id ZeroTrustAccessIdentityProvider#ping_env_id}
        :param pkce_enabled: Enable Proof Key for Code Exchange (PKCE). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#pkce_enabled ZeroTrustAccessIdentityProvider#pkce_enabled}
        :param prompt: Indicates the type of user interaction that is required. prompt=login forces the user to enter their credentials on that request, negating single-sign on. prompt=none is the opposite. It ensures that the user isn't presented with any interactive prompt. If the request can't be completed silently by using single-sign on, the Microsoft identity platform returns an interaction_required error. prompt=select_account interrupts single sign-on providing account selection experience listing all the accounts either in session or any remembered account or an option to choose to use a different account altogether. Available values: "login", "select_account", "none". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#prompt ZeroTrustAccessIdentityProvider#prompt}
        :param scopes: OAuth scopes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#scopes ZeroTrustAccessIdentityProvider#scopes}
        :param sign_request: Sign the SAML authentication request with Access credentials. To verify the signature, use the public key from the Access certs endpoints. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#sign_request ZeroTrustAccessIdentityProvider#sign_request}
        :param sso_target_url: URL to send the SAML authentication requests to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#sso_target_url ZeroTrustAccessIdentityProvider#sso_target_url}
        :param support_groups: Should Cloudflare try to load groups from your account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#support_groups ZeroTrustAccessIdentityProvider#support_groups}
        :param token_url: The token_endpoint URL of your IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#token_url ZeroTrustAccessIdentityProvider#token_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__609d3fe69049e1bce9a36b6e1bfb26c263c5578150b448210874f773c494717c)
            check_type(argname="argument apps_domain", value=apps_domain, expected_type=type_hints["apps_domain"])
            check_type(argname="argument attributes", value=attributes, expected_type=type_hints["attributes"])
            check_type(argname="argument authorization_server_id", value=authorization_server_id, expected_type=type_hints["authorization_server_id"])
            check_type(argname="argument auth_url", value=auth_url, expected_type=type_hints["auth_url"])
            check_type(argname="argument centrify_account", value=centrify_account, expected_type=type_hints["centrify_account"])
            check_type(argname="argument centrify_app_id", value=centrify_app_id, expected_type=type_hints["centrify_app_id"])
            check_type(argname="argument certs_url", value=certs_url, expected_type=type_hints["certs_url"])
            check_type(argname="argument claims", value=claims, expected_type=type_hints["claims"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument conditional_access_enabled", value=conditional_access_enabled, expected_type=type_hints["conditional_access_enabled"])
            check_type(argname="argument directory_id", value=directory_id, expected_type=type_hints["directory_id"])
            check_type(argname="argument email_attribute_name", value=email_attribute_name, expected_type=type_hints["email_attribute_name"])
            check_type(argname="argument email_claim_name", value=email_claim_name, expected_type=type_hints["email_claim_name"])
            check_type(argname="argument header_attributes", value=header_attributes, expected_type=type_hints["header_attributes"])
            check_type(argname="argument idp_public_certs", value=idp_public_certs, expected_type=type_hints["idp_public_certs"])
            check_type(argname="argument issuer_url", value=issuer_url, expected_type=type_hints["issuer_url"])
            check_type(argname="argument okta_account", value=okta_account, expected_type=type_hints["okta_account"])
            check_type(argname="argument onelogin_account", value=onelogin_account, expected_type=type_hints["onelogin_account"])
            check_type(argname="argument ping_env_id", value=ping_env_id, expected_type=type_hints["ping_env_id"])
            check_type(argname="argument pkce_enabled", value=pkce_enabled, expected_type=type_hints["pkce_enabled"])
            check_type(argname="argument prompt", value=prompt, expected_type=type_hints["prompt"])
            check_type(argname="argument scopes", value=scopes, expected_type=type_hints["scopes"])
            check_type(argname="argument sign_request", value=sign_request, expected_type=type_hints["sign_request"])
            check_type(argname="argument sso_target_url", value=sso_target_url, expected_type=type_hints["sso_target_url"])
            check_type(argname="argument support_groups", value=support_groups, expected_type=type_hints["support_groups"])
            check_type(argname="argument token_url", value=token_url, expected_type=type_hints["token_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if apps_domain is not None:
            self._values["apps_domain"] = apps_domain
        if attributes is not None:
            self._values["attributes"] = attributes
        if authorization_server_id is not None:
            self._values["authorization_server_id"] = authorization_server_id
        if auth_url is not None:
            self._values["auth_url"] = auth_url
        if centrify_account is not None:
            self._values["centrify_account"] = centrify_account
        if centrify_app_id is not None:
            self._values["centrify_app_id"] = centrify_app_id
        if certs_url is not None:
            self._values["certs_url"] = certs_url
        if claims is not None:
            self._values["claims"] = claims
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if conditional_access_enabled is not None:
            self._values["conditional_access_enabled"] = conditional_access_enabled
        if directory_id is not None:
            self._values["directory_id"] = directory_id
        if email_attribute_name is not None:
            self._values["email_attribute_name"] = email_attribute_name
        if email_claim_name is not None:
            self._values["email_claim_name"] = email_claim_name
        if header_attributes is not None:
            self._values["header_attributes"] = header_attributes
        if idp_public_certs is not None:
            self._values["idp_public_certs"] = idp_public_certs
        if issuer_url is not None:
            self._values["issuer_url"] = issuer_url
        if okta_account is not None:
            self._values["okta_account"] = okta_account
        if onelogin_account is not None:
            self._values["onelogin_account"] = onelogin_account
        if ping_env_id is not None:
            self._values["ping_env_id"] = ping_env_id
        if pkce_enabled is not None:
            self._values["pkce_enabled"] = pkce_enabled
        if prompt is not None:
            self._values["prompt"] = prompt
        if scopes is not None:
            self._values["scopes"] = scopes
        if sign_request is not None:
            self._values["sign_request"] = sign_request
        if sso_target_url is not None:
            self._values["sso_target_url"] = sso_target_url
        if support_groups is not None:
            self._values["support_groups"] = support_groups
        if token_url is not None:
            self._values["token_url"] = token_url

    @builtins.property
    def apps_domain(self) -> typing.Optional[builtins.str]:
        '''Your companies TLD.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#apps_domain ZeroTrustAccessIdentityProvider#apps_domain}
        '''
        result = self._values.get("apps_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of SAML attribute names that will be added to your signed JWT token and can be used in SAML policy rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#attributes ZeroTrustAccessIdentityProvider#attributes}
        '''
        result = self._values.get("attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def authorization_server_id(self) -> typing.Optional[builtins.str]:
        '''Your okta authorization server id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#authorization_server_id ZeroTrustAccessIdentityProvider#authorization_server_id}
        '''
        result = self._values.get("authorization_server_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_url(self) -> typing.Optional[builtins.str]:
        '''The authorization_endpoint URL of your IdP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#auth_url ZeroTrustAccessIdentityProvider#auth_url}
        '''
        result = self._values.get("auth_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def centrify_account(self) -> typing.Optional[builtins.str]:
        '''Your centrify account url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#centrify_account ZeroTrustAccessIdentityProvider#centrify_account}
        '''
        result = self._values.get("centrify_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def centrify_app_id(self) -> typing.Optional[builtins.str]:
        '''Your centrify app id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#centrify_app_id ZeroTrustAccessIdentityProvider#centrify_app_id}
        '''
        result = self._values.get("centrify_app_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certs_url(self) -> typing.Optional[builtins.str]:
        '''The jwks_uri endpoint of your IdP to allow the IdP keys to sign the tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#certs_url ZeroTrustAccessIdentityProvider#certs_url}
        '''
        result = self._values.get("certs_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def claims(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Custom claims.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#claims ZeroTrustAccessIdentityProvider#claims}
        '''
        result = self._values.get("claims")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Your OAuth Client ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#client_id ZeroTrustAccessIdentityProvider#client_id}
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[builtins.str]:
        '''Your OAuth Client Secret.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#client_secret ZeroTrustAccessIdentityProvider#client_secret}
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def conditional_access_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Should Cloudflare try to load authentication contexts from your account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#conditional_access_enabled ZeroTrustAccessIdentityProvider#conditional_access_enabled}
        '''
        result = self._values.get("conditional_access_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def directory_id(self) -> typing.Optional[builtins.str]:
        '''Your Azure directory uuid.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#directory_id ZeroTrustAccessIdentityProvider#directory_id}
        '''
        result = self._values.get("directory_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_attribute_name(self) -> typing.Optional[builtins.str]:
        '''The attribute name for email in the SAML response.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#email_attribute_name ZeroTrustAccessIdentityProvider#email_attribute_name}
        '''
        result = self._values.get("email_attribute_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_claim_name(self) -> typing.Optional[builtins.str]:
        '''The claim name for email in the id_token response.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#email_claim_name ZeroTrustAccessIdentityProvider#email_claim_name}
        '''
        result = self._values.get("email_claim_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def header_attributes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessIdentityProviderConfigHeaderAttributes"]]]:
        '''Add a list of attribute names that will be returned in the response header from the Access callback.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#header_attributes ZeroTrustAccessIdentityProvider#header_attributes}
        '''
        result = self._values.get("header_attributes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessIdentityProviderConfigHeaderAttributes"]]], result)

    @builtins.property
    def idp_public_certs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''X509 certificate to verify the signature in the SAML authentication response.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#idp_public_certs ZeroTrustAccessIdentityProvider#idp_public_certs}
        '''
        result = self._values.get("idp_public_certs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def issuer_url(self) -> typing.Optional[builtins.str]:
        '''IdP Entity ID or Issuer URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#issuer_url ZeroTrustAccessIdentityProvider#issuer_url}
        '''
        result = self._values.get("issuer_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def okta_account(self) -> typing.Optional[builtins.str]:
        '''Your okta account url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#okta_account ZeroTrustAccessIdentityProvider#okta_account}
        '''
        result = self._values.get("okta_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def onelogin_account(self) -> typing.Optional[builtins.str]:
        '''Your OneLogin account url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#onelogin_account ZeroTrustAccessIdentityProvider#onelogin_account}
        '''
        result = self._values.get("onelogin_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ping_env_id(self) -> typing.Optional[builtins.str]:
        '''Your PingOne environment identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#ping_env_id ZeroTrustAccessIdentityProvider#ping_env_id}
        '''
        result = self._values.get("ping_env_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pkce_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Proof Key for Code Exchange (PKCE).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#pkce_enabled ZeroTrustAccessIdentityProvider#pkce_enabled}
        '''
        result = self._values.get("pkce_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def prompt(self) -> typing.Optional[builtins.str]:
        '''Indicates the type of user interaction that is required.

        prompt=login forces the user to enter their credentials on that request, negating single-sign on. prompt=none is the opposite. It ensures that the user isn't presented with any interactive prompt. If the request can't be completed silently by using single-sign on, the Microsoft identity platform returns an interaction_required error. prompt=select_account interrupts single sign-on providing account selection experience listing all the accounts either in session or any remembered account or an option to choose to use a different account altogether.
        Available values: "login", "select_account", "none".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#prompt ZeroTrustAccessIdentityProvider#prompt}
        '''
        result = self._values.get("prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''OAuth scopes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#scopes ZeroTrustAccessIdentityProvider#scopes}
        '''
        result = self._values.get("scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sign_request(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Sign the SAML authentication request with Access credentials.

        To verify the signature, use the public key from the Access certs endpoints.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#sign_request ZeroTrustAccessIdentityProvider#sign_request}
        '''
        result = self._values.get("sign_request")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sso_target_url(self) -> typing.Optional[builtins.str]:
        '''URL to send the SAML authentication requests to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#sso_target_url ZeroTrustAccessIdentityProvider#sso_target_url}
        '''
        result = self._values.get("sso_target_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def support_groups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Should Cloudflare try to load groups from your account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#support_groups ZeroTrustAccessIdentityProvider#support_groups}
        '''
        result = self._values.get("support_groups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token_url(self) -> typing.Optional[builtins.str]:
        '''The token_endpoint URL of your IdP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#token_url ZeroTrustAccessIdentityProvider#token_url}
        '''
        result = self._values.get("token_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessIdentityProviderConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessIdentityProviderConfigAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessIdentityProvider.ZeroTrustAccessIdentityProviderConfigAOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e5966aa51aeb98bd290ef6c3c2b9868251e8f1f9610f417c6340b1352eb3fb3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putHeaderAttributes")
    def put_header_attributes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessIdentityProviderConfigHeaderAttributes", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__238fc1db827d2fd0e8fa39616c5ec2d2d7edc7d9ae4d8a30c52f94a4505628dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHeaderAttributes", [value]))

    @jsii.member(jsii_name="resetAppsDomain")
    def reset_apps_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppsDomain", []))

    @jsii.member(jsii_name="resetAttributes")
    def reset_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttributes", []))

    @jsii.member(jsii_name="resetAuthorizationServerId")
    def reset_authorization_server_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorizationServerId", []))

    @jsii.member(jsii_name="resetAuthUrl")
    def reset_auth_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthUrl", []))

    @jsii.member(jsii_name="resetCentrifyAccount")
    def reset_centrify_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCentrifyAccount", []))

    @jsii.member(jsii_name="resetCentrifyAppId")
    def reset_centrify_app_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCentrifyAppId", []))

    @jsii.member(jsii_name="resetCertsUrl")
    def reset_certs_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertsUrl", []))

    @jsii.member(jsii_name="resetClaims")
    def reset_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClaims", []))

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetClientSecret")
    def reset_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientSecret", []))

    @jsii.member(jsii_name="resetConditionalAccessEnabled")
    def reset_conditional_access_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConditionalAccessEnabled", []))

    @jsii.member(jsii_name="resetDirectoryId")
    def reset_directory_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectoryId", []))

    @jsii.member(jsii_name="resetEmailAttributeName")
    def reset_email_attribute_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailAttributeName", []))

    @jsii.member(jsii_name="resetEmailClaimName")
    def reset_email_claim_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailClaimName", []))

    @jsii.member(jsii_name="resetHeaderAttributes")
    def reset_header_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaderAttributes", []))

    @jsii.member(jsii_name="resetIdpPublicCerts")
    def reset_idp_public_certs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpPublicCerts", []))

    @jsii.member(jsii_name="resetIssuerUrl")
    def reset_issuer_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuerUrl", []))

    @jsii.member(jsii_name="resetOktaAccount")
    def reset_okta_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOktaAccount", []))

    @jsii.member(jsii_name="resetOneloginAccount")
    def reset_onelogin_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOneloginAccount", []))

    @jsii.member(jsii_name="resetPingEnvId")
    def reset_ping_env_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPingEnvId", []))

    @jsii.member(jsii_name="resetPkceEnabled")
    def reset_pkce_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPkceEnabled", []))

    @jsii.member(jsii_name="resetPrompt")
    def reset_prompt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrompt", []))

    @jsii.member(jsii_name="resetScopes")
    def reset_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScopes", []))

    @jsii.member(jsii_name="resetSignRequest")
    def reset_sign_request(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignRequest", []))

    @jsii.member(jsii_name="resetSsoTargetUrl")
    def reset_sso_target_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsoTargetUrl", []))

    @jsii.member(jsii_name="resetSupportGroups")
    def reset_support_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportGroups", []))

    @jsii.member(jsii_name="resetTokenUrl")
    def reset_token_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenUrl", []))

    @builtins.property
    @jsii.member(jsii_name="headerAttributes")
    def header_attributes(
        self,
    ) -> "ZeroTrustAccessIdentityProviderConfigHeaderAttributesList":
        return typing.cast("ZeroTrustAccessIdentityProviderConfigHeaderAttributesList", jsii.get(self, "headerAttributes"))

    @builtins.property
    @jsii.member(jsii_name="redirectUrl")
    def redirect_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redirectUrl"))

    @builtins.property
    @jsii.member(jsii_name="appsDomainInput")
    def apps_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appsDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="attributesInput")
    def attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "attributesInput"))

    @builtins.property
    @jsii.member(jsii_name="authorizationServerIdInput")
    def authorization_server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizationServerIdInput"))

    @builtins.property
    @jsii.member(jsii_name="authUrlInput")
    def auth_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="centrifyAccountInput")
    def centrify_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "centrifyAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="centrifyAppIdInput")
    def centrify_app_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "centrifyAppIdInput"))

    @builtins.property
    @jsii.member(jsii_name="certsUrlInput")
    def certs_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certsUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="claimsInput")
    def claims_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "claimsInput"))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="conditionalAccessEnabledInput")
    def conditional_access_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "conditionalAccessEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="emailAttributeNameInput")
    def email_attribute_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailAttributeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="emailClaimNameInput")
    def email_claim_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailClaimNameInput"))

    @builtins.property
    @jsii.member(jsii_name="headerAttributesInput")
    def header_attributes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessIdentityProviderConfigHeaderAttributes"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessIdentityProviderConfigHeaderAttributes"]]], jsii.get(self, "headerAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="idpPublicCertsInput")
    def idp_public_certs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "idpPublicCertsInput"))

    @builtins.property
    @jsii.member(jsii_name="issuerUrlInput")
    def issuer_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="oktaAccountInput")
    def okta_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oktaAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="oneloginAccountInput")
    def onelogin_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oneloginAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="pingEnvIdInput")
    def ping_env_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pingEnvIdInput"))

    @builtins.property
    @jsii.member(jsii_name="pkceEnabledInput")
    def pkce_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pkceEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="promptInput")
    def prompt_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "promptInput"))

    @builtins.property
    @jsii.member(jsii_name="scopesInput")
    def scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "scopesInput"))

    @builtins.property
    @jsii.member(jsii_name="signRequestInput")
    def sign_request_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "signRequestInput"))

    @builtins.property
    @jsii.member(jsii_name="ssoTargetUrlInput")
    def sso_target_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ssoTargetUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="supportGroupsInput")
    def support_groups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "supportGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenUrlInput")
    def token_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="appsDomain")
    def apps_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appsDomain"))

    @apps_domain.setter
    def apps_domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6c03150f5ffb5c4020e9e534ae5c5fe5b970e40dc24fb9b6884f582ef3ad9e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appsDomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributes")
    def attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "attributes"))

    @attributes.setter
    def attributes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb4c18a2b189d0092c9a9a99e66eb388c5df538fc9e200de22489b73a2b0a7c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authorizationServerId")
    def authorization_server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizationServerId"))

    @authorization_server_id.setter
    def authorization_server_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7be857c579a0b37d64e43dc61b25d36bf84a5ca8b7b4b125fb1db39d5e6a241b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorizationServerId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authUrl")
    def auth_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authUrl"))

    @auth_url.setter
    def auth_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfd45a2429dcfab191ec3ff753a5a36d2397759e146c42d2edd6442b3dea4dd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="centrifyAccount")
    def centrify_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "centrifyAccount"))

    @centrify_account.setter
    def centrify_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50d0bcf282e4ac43cd1401c44c5a549710d4615880bbb9bfbfe91fbbb5ade95b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "centrifyAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="centrifyAppId")
    def centrify_app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "centrifyAppId"))

    @centrify_app_id.setter
    def centrify_app_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__479d6fc639ac09e890ac565a88e0eb63f73213b16f9677d9e0c2ab0e1c83493a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "centrifyAppId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certsUrl")
    def certs_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certsUrl"))

    @certs_url.setter
    def certs_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0fd62bde4f06fd80256ec6ccb92110f24fe8f7896f29358a25c1f316d1da155)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certsUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="claims")
    def claims(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "claims"))

    @claims.setter
    def claims(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a41abe04424655aed67f48dbe0f5af2da66cbad15c852d13fe3a5fdd2d4461c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claims", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c0e241659384cf094cadb136fed96070496281c053a7a3853e1c5853e4ee967)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ebbe2d0ff3cefc2941f3a739f0d96e31ba83d634f06f9668a5fdef2a5834147)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="conditionalAccessEnabled")
    def conditional_access_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "conditionalAccessEnabled"))

    @conditional_access_enabled.setter
    def conditional_access_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e641a3d64345ca742dcf91460887e905de941b31158480927ad619b0ae6620f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "conditionalAccessEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53223a90ee2eb3db8ec9bd96fb414e142f4761577bc87af6b1e44efcd3fe0c17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directoryId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailAttributeName")
    def email_attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailAttributeName"))

    @email_attribute_name.setter
    def email_attribute_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87087a241d801a594e81b850e0e90634729d94691801b45bf6a3b1524740af78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailAttributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailClaimName")
    def email_claim_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailClaimName"))

    @email_claim_name.setter
    def email_claim_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc96f4aba15474cc406a83336f55f57a206d2515d9a8b5c7fc2528965cbf355d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailClaimName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idpPublicCerts")
    def idp_public_certs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "idpPublicCerts"))

    @idp_public_certs.setter
    def idp_public_certs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8ec30134e7c23494a45c4f2602650f08cda028e94185bf47b6616c2de912824)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpPublicCerts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuerUrl")
    def issuer_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerUrl"))

    @issuer_url.setter
    def issuer_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4798d175fea9ccbf8c54f3fc912310bcb3efcf50d3e667d3fdd02810c5bee45b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuerUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oktaAccount")
    def okta_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oktaAccount"))

    @okta_account.setter
    def okta_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02fa2487fb86a6746cd6fee62819b45949128c27fe784efe7172389dde4887bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oktaAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oneloginAccount")
    def onelogin_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oneloginAccount"))

    @onelogin_account.setter
    def onelogin_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__005243f52217d7d4cb96fc49ed67d2dfdbbaf38c755a51f13d4fb6323eb8f693)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oneloginAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pingEnvId")
    def ping_env_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pingEnvId"))

    @ping_env_id.setter
    def ping_env_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca7ad5a2d8784d357a87d2243f4b49f188e7d7fa48253d0ac222e2cc1a3f52c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pingEnvId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pkceEnabled")
    def pkce_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pkceEnabled"))

    @pkce_enabled.setter
    def pkce_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8da8c825bde980d13964c2158148ce9b965a08a9b150a3138826a8e7c9d87d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pkceEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prompt")
    def prompt(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prompt"))

    @prompt.setter
    def prompt(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86840a10a5b4dcbb60c46766b9f89e45e339ad395261e42531d3a85913f0d612)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prompt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scopes")
    def scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "scopes"))

    @scopes.setter
    def scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c46c4456408c5cf3165373c8c99b6343f7e18b68f0849bfb9f7e7c38fb8e1d45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scopes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signRequest")
    def sign_request(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "signRequest"))

    @sign_request.setter
    def sign_request(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3b832fbcee09d87ae40d41f77089dbf6baf07432798f5454be6ffc575b9fbd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signRequest", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ssoTargetUrl")
    def sso_target_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ssoTargetUrl"))

    @sso_target_url.setter
    def sso_target_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d02e9a2d938304c94e3f89099a3659f10763a3d84e0077bf6b2a7821452de4d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssoTargetUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="supportGroups")
    def support_groups(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "supportGroups"))

    @support_groups.setter
    def support_groups(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__451d1af36cf398ebe8bd7589fe06173f758af2ba198babc5a385a87c8189bcbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "supportGroups", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenUrl")
    def token_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenUrl"))

    @token_url.setter
    def token_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79cd09b7447641181512dc28face7546f4f6dd2676f44a2d873039eff70e7478)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderConfigA]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderConfigA]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderConfigA]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4edc920de5761d47d8ff22df9248c4e24bc25c1f1a3eb9aec059d3fcee9d2372)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessIdentityProvider.ZeroTrustAccessIdentityProviderConfigHeaderAttributes",
    jsii_struct_bases=[],
    name_mapping={"attribute_name": "attributeName", "header_name": "headerName"},
)
class ZeroTrustAccessIdentityProviderConfigHeaderAttributes:
    def __init__(
        self,
        *,
        attribute_name: typing.Optional[builtins.str] = None,
        header_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param attribute_name: attribute name from the IDP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#attribute_name ZeroTrustAccessIdentityProvider#attribute_name}
        :param header_name: header that will be added on the request to the origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#header_name ZeroTrustAccessIdentityProvider#header_name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74501f4627a1a5b0e12008583a239cc2e22370694ca1ac2bb51454a64fa31677)
            check_type(argname="argument attribute_name", value=attribute_name, expected_type=type_hints["attribute_name"])
            check_type(argname="argument header_name", value=header_name, expected_type=type_hints["header_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if attribute_name is not None:
            self._values["attribute_name"] = attribute_name
        if header_name is not None:
            self._values["header_name"] = header_name

    @builtins.property
    def attribute_name(self) -> typing.Optional[builtins.str]:
        '''attribute name from the IDP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#attribute_name ZeroTrustAccessIdentityProvider#attribute_name}
        '''
        result = self._values.get("attribute_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def header_name(self) -> typing.Optional[builtins.str]:
        '''header that will be added on the request to the origin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#header_name ZeroTrustAccessIdentityProvider#header_name}
        '''
        result = self._values.get("header_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessIdentityProviderConfigHeaderAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessIdentityProviderConfigHeaderAttributesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessIdentityProvider.ZeroTrustAccessIdentityProviderConfigHeaderAttributesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__80cd0b6632dd5509a58935c540df923a014a06d50c95fee6000fd4851f8368d4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustAccessIdentityProviderConfigHeaderAttributesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d6c41463f8fbd073c8e984627ad6e3c45a9ef5d572e942f846d330f84d72ffc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustAccessIdentityProviderConfigHeaderAttributesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__289f4679f1c185a0de93cf47bdc03450b5df1f9d8440b0d346a5828c3e7608a4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b50f6713b9fe7c66f597aeacb36edcb73129f02c49f81c817a4299b9c2214ca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__de1f68cc21516a2600e918c3514b60d27f53e978470061dbe516e6f6b743377b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessIdentityProviderConfigHeaderAttributes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessIdentityProviderConfigHeaderAttributes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessIdentityProviderConfigHeaderAttributes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8af1cdb724450a3c489374e0e56878c3a05e14eefc4e60b121c057473988f2c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessIdentityProviderConfigHeaderAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessIdentityProvider.ZeroTrustAccessIdentityProviderConfigHeaderAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba4e444af13bf9d300dfb22618bcc5de01da8bdde34edd890a6e40f61f41d349)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAttributeName")
    def reset_attribute_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttributeName", []))

    @jsii.member(jsii_name="resetHeaderName")
    def reset_header_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaderName", []))

    @builtins.property
    @jsii.member(jsii_name="attributeNameInput")
    def attribute_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="headerNameInput")
    def header_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeName"))

    @attribute_name.setter
    def attribute_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__817de4be8975195fb799db15799000b662cef401dc155f1abdd7e9cdddd3a1e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headerName")
    def header_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerName"))

    @header_name.setter
    def header_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec939f2159ea5483de8ea0390b16d0b9dd5b4c18499e1b013532c56b3e603307)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderConfigHeaderAttributes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderConfigHeaderAttributes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderConfigHeaderAttributes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e65b61cdb25676765cfcfd2a19bcd11af82f2685ee0ce549cabbca2161b82995)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessIdentityProvider.ZeroTrustAccessIdentityProviderScimConfig",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "identity_update_behavior": "identityUpdateBehavior",
        "seat_deprovision": "seatDeprovision",
        "user_deprovision": "userDeprovision",
    },
)
class ZeroTrustAccessIdentityProviderScimConfig:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        identity_update_behavior: typing.Optional[builtins.str] = None,
        seat_deprovision: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        user_deprovision: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: A flag to enable or disable SCIM for the identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#enabled ZeroTrustAccessIdentityProvider#enabled}
        :param identity_update_behavior: Indicates how a SCIM event updates a user identity used for policy evaluation. Use "automatic" to automatically update a user's identity and augment it with fields from the SCIM user resource. Use "reauth" to force re-authentication on group membership updates, user identity update will only occur after successful re-authentication. With "reauth" identities will not contain fields from the SCIM user resource. With "no_action" identities will not be changed by SCIM updates in any way and users will not be prompted to reauthenticate. Available values: "automatic", "reauth", "no_action". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#identity_update_behavior ZeroTrustAccessIdentityProvider#identity_update_behavior}
        :param seat_deprovision: A flag to remove a user's seat in Zero Trust when they have been deprovisioned in the Identity Provider. This cannot be enabled unless user_deprovision is also enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#seat_deprovision ZeroTrustAccessIdentityProvider#seat_deprovision}
        :param user_deprovision: A flag to enable revoking a user's session in Access and Gateway when they have been deprovisioned in the Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#user_deprovision ZeroTrustAccessIdentityProvider#user_deprovision}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc4316578d7806e1d279e9f7c005ca5251b4458218747db56e20bf809fb6625f)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument identity_update_behavior", value=identity_update_behavior, expected_type=type_hints["identity_update_behavior"])
            check_type(argname="argument seat_deprovision", value=seat_deprovision, expected_type=type_hints["seat_deprovision"])
            check_type(argname="argument user_deprovision", value=user_deprovision, expected_type=type_hints["user_deprovision"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if identity_update_behavior is not None:
            self._values["identity_update_behavior"] = identity_update_behavior
        if seat_deprovision is not None:
            self._values["seat_deprovision"] = seat_deprovision
        if user_deprovision is not None:
            self._values["user_deprovision"] = user_deprovision

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''A flag to enable or disable SCIM for the identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#enabled ZeroTrustAccessIdentityProvider#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def identity_update_behavior(self) -> typing.Optional[builtins.str]:
        '''Indicates how a SCIM event updates a user identity used for policy evaluation.

        Use "automatic" to automatically update a user's identity and augment it with fields from the SCIM user resource. Use "reauth" to force re-authentication on group membership updates, user identity update will only occur after successful re-authentication. With "reauth" identities will not contain fields from the SCIM user resource. With "no_action" identities will not be changed by SCIM updates in any way and users will not be prompted to reauthenticate.
        Available values: "automatic", "reauth", "no_action".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#identity_update_behavior ZeroTrustAccessIdentityProvider#identity_update_behavior}
        '''
        result = self._values.get("identity_update_behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def seat_deprovision(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''A flag to remove a user's seat in Zero Trust when they have been deprovisioned in the Identity Provider.

        This cannot be enabled unless user_deprovision is also enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#seat_deprovision ZeroTrustAccessIdentityProvider#seat_deprovision}
        '''
        result = self._values.get("seat_deprovision")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def user_deprovision(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''A flag to enable revoking a user's session in Access and Gateway when they have been deprovisioned in the Identity Provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_identity_provider#user_deprovision ZeroTrustAccessIdentityProvider#user_deprovision}
        '''
        result = self._values.get("user_deprovision")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessIdentityProviderScimConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessIdentityProviderScimConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessIdentityProvider.ZeroTrustAccessIdentityProviderScimConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__318707c37619d0f587a691cb248413b6dd4ff6a0c930d478bd096aa58d91fc09)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetIdentityUpdateBehavior")
    def reset_identity_update_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityUpdateBehavior", []))

    @jsii.member(jsii_name="resetSeatDeprovision")
    def reset_seat_deprovision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeatDeprovision", []))

    @jsii.member(jsii_name="resetUserDeprovision")
    def reset_user_deprovision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserDeprovision", []))

    @builtins.property
    @jsii.member(jsii_name="scimBaseUrl")
    def scim_base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scimBaseUrl"))

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secret"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="identityUpdateBehaviorInput")
    def identity_update_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityUpdateBehaviorInput"))

    @builtins.property
    @jsii.member(jsii_name="seatDeprovisionInput")
    def seat_deprovision_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "seatDeprovisionInput"))

    @builtins.property
    @jsii.member(jsii_name="userDeprovisionInput")
    def user_deprovision_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "userDeprovisionInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__c1fa50579658d1d3363758b2cc54ea3f4489a94dbdd2d909d515a56234d25a3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityUpdateBehavior")
    def identity_update_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityUpdateBehavior"))

    @identity_update_behavior.setter
    def identity_update_behavior(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b476bcebfb5ac3259617742a8600347d65741c0f0fae9b6a69721d6fea921de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityUpdateBehavior", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="seatDeprovision")
    def seat_deprovision(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "seatDeprovision"))

    @seat_deprovision.setter
    def seat_deprovision(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6387757982a8c33ac9abe19a51938065f97075803ce2ef7578ab94be7915925c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "seatDeprovision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userDeprovision")
    def user_deprovision(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "userDeprovision"))

    @user_deprovision.setter
    def user_deprovision(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fed12a6477c46a4ace1e3bdcbbd3daed48f7e7d384aaea665d9ad53807b8fcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userDeprovision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderScimConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderScimConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderScimConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c95de4605d0427a4cc4714be74da8d1d963a3b2772a5e3658a92d1e081697b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustAccessIdentityProvider",
    "ZeroTrustAccessIdentityProviderConfig",
    "ZeroTrustAccessIdentityProviderConfigA",
    "ZeroTrustAccessIdentityProviderConfigAOutputReference",
    "ZeroTrustAccessIdentityProviderConfigHeaderAttributes",
    "ZeroTrustAccessIdentityProviderConfigHeaderAttributesList",
    "ZeroTrustAccessIdentityProviderConfigHeaderAttributesOutputReference",
    "ZeroTrustAccessIdentityProviderScimConfig",
    "ZeroTrustAccessIdentityProviderScimConfigOutputReference",
]

publication.publish()

def _typecheckingstub__e9b6fd0822ba9fc801cfa64394eaa38aa130771cae55579d4b55196ecfa4c927(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    config: typing.Union[ZeroTrustAccessIdentityProviderConfigA, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    type: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    scim_config: typing.Optional[typing.Union[ZeroTrustAccessIdentityProviderScimConfig, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__95a93e9f5e6406dad638d4ce84e07b5cd4331bd3e68c409ac14c0c119b1265e7(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3c13fe9846cbbb98e08c4d361a3e58e7aecaa13810a65adae682d16604effa0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f32fb4ae5420a2de675d0b6a4cc781df7b5bd54905ace0b7220f101e2cd0c12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9196e2522fb2c9aa41e54b74894604180266fc797af81dd47610a2f86906b376(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12d8ec068925129c4ecd3a4ae93b3aa4fb14dd04e13b0e4e5f633a3a82910f12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c533353ecd98e1c6ca56d019306578d8a618a4ecc1e8db45e4bdf738e18ce696(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    config: typing.Union[ZeroTrustAccessIdentityProviderConfigA, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    type: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    scim_config: typing.Optional[typing.Union[ZeroTrustAccessIdentityProviderScimConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__609d3fe69049e1bce9a36b6e1bfb26c263c5578150b448210874f773c494717c(
    *,
    apps_domain: typing.Optional[builtins.str] = None,
    attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
    authorization_server_id: typing.Optional[builtins.str] = None,
    auth_url: typing.Optional[builtins.str] = None,
    centrify_account: typing.Optional[builtins.str] = None,
    centrify_app_id: typing.Optional[builtins.str] = None,
    certs_url: typing.Optional[builtins.str] = None,
    claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    client_id: typing.Optional[builtins.str] = None,
    client_secret: typing.Optional[builtins.str] = None,
    conditional_access_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    directory_id: typing.Optional[builtins.str] = None,
    email_attribute_name: typing.Optional[builtins.str] = None,
    email_claim_name: typing.Optional[builtins.str] = None,
    header_attributes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessIdentityProviderConfigHeaderAttributes, typing.Dict[builtins.str, typing.Any]]]]] = None,
    idp_public_certs: typing.Optional[typing.Sequence[builtins.str]] = None,
    issuer_url: typing.Optional[builtins.str] = None,
    okta_account: typing.Optional[builtins.str] = None,
    onelogin_account: typing.Optional[builtins.str] = None,
    ping_env_id: typing.Optional[builtins.str] = None,
    pkce_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    prompt: typing.Optional[builtins.str] = None,
    scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    sign_request: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sso_target_url: typing.Optional[builtins.str] = None,
    support_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e5966aa51aeb98bd290ef6c3c2b9868251e8f1f9610f417c6340b1352eb3fb3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__238fc1db827d2fd0e8fa39616c5ec2d2d7edc7d9ae4d8a30c52f94a4505628dc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessIdentityProviderConfigHeaderAttributes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6c03150f5ffb5c4020e9e534ae5c5fe5b970e40dc24fb9b6884f582ef3ad9e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb4c18a2b189d0092c9a9a99e66eb388c5df538fc9e200de22489b73a2b0a7c6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7be857c579a0b37d64e43dc61b25d36bf84a5ca8b7b4b125fb1db39d5e6a241b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfd45a2429dcfab191ec3ff753a5a36d2397759e146c42d2edd6442b3dea4dd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50d0bcf282e4ac43cd1401c44c5a549710d4615880bbb9bfbfe91fbbb5ade95b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__479d6fc639ac09e890ac565a88e0eb63f73213b16f9677d9e0c2ab0e1c83493a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0fd62bde4f06fd80256ec6ccb92110f24fe8f7896f29358a25c1f316d1da155(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a41abe04424655aed67f48dbe0f5af2da66cbad15c852d13fe3a5fdd2d4461c5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c0e241659384cf094cadb136fed96070496281c053a7a3853e1c5853e4ee967(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ebbe2d0ff3cefc2941f3a739f0d96e31ba83d634f06f9668a5fdef2a5834147(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e641a3d64345ca742dcf91460887e905de941b31158480927ad619b0ae6620f4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53223a90ee2eb3db8ec9bd96fb414e142f4761577bc87af6b1e44efcd3fe0c17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87087a241d801a594e81b850e0e90634729d94691801b45bf6a3b1524740af78(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc96f4aba15474cc406a83336f55f57a206d2515d9a8b5c7fc2528965cbf355d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8ec30134e7c23494a45c4f2602650f08cda028e94185bf47b6616c2de912824(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4798d175fea9ccbf8c54f3fc912310bcb3efcf50d3e667d3fdd02810c5bee45b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02fa2487fb86a6746cd6fee62819b45949128c27fe784efe7172389dde4887bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__005243f52217d7d4cb96fc49ed67d2dfdbbaf38c755a51f13d4fb6323eb8f693(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca7ad5a2d8784d357a87d2243f4b49f188e7d7fa48253d0ac222e2cc1a3f52c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8da8c825bde980d13964c2158148ce9b965a08a9b150a3138826a8e7c9d87d2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86840a10a5b4dcbb60c46766b9f89e45e339ad395261e42531d3a85913f0d612(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c46c4456408c5cf3165373c8c99b6343f7e18b68f0849bfb9f7e7c38fb8e1d45(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3b832fbcee09d87ae40d41f77089dbf6baf07432798f5454be6ffc575b9fbd2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d02e9a2d938304c94e3f89099a3659f10763a3d84e0077bf6b2a7821452de4d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__451d1af36cf398ebe8bd7589fe06173f758af2ba198babc5a385a87c8189bcbc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79cd09b7447641181512dc28face7546f4f6dd2676f44a2d873039eff70e7478(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4edc920de5761d47d8ff22df9248c4e24bc25c1f1a3eb9aec059d3fcee9d2372(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderConfigA]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74501f4627a1a5b0e12008583a239cc2e22370694ca1ac2bb51454a64fa31677(
    *,
    attribute_name: typing.Optional[builtins.str] = None,
    header_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80cd0b6632dd5509a58935c540df923a014a06d50c95fee6000fd4851f8368d4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d6c41463f8fbd073c8e984627ad6e3c45a9ef5d572e942f846d330f84d72ffc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__289f4679f1c185a0de93cf47bdc03450b5df1f9d8440b0d346a5828c3e7608a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b50f6713b9fe7c66f597aeacb36edcb73129f02c49f81c817a4299b9c2214ca(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de1f68cc21516a2600e918c3514b60d27f53e978470061dbe516e6f6b743377b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8af1cdb724450a3c489374e0e56878c3a05e14eefc4e60b121c057473988f2c6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessIdentityProviderConfigHeaderAttributes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba4e444af13bf9d300dfb22618bcc5de01da8bdde34edd890a6e40f61f41d349(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__817de4be8975195fb799db15799000b662cef401dc155f1abdd7e9cdddd3a1e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec939f2159ea5483de8ea0390b16d0b9dd5b4c18499e1b013532c56b3e603307(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e65b61cdb25676765cfcfd2a19bcd11af82f2685ee0ce549cabbca2161b82995(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderConfigHeaderAttributes]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc4316578d7806e1d279e9f7c005ca5251b4458218747db56e20bf809fb6625f(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    identity_update_behavior: typing.Optional[builtins.str] = None,
    seat_deprovision: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    user_deprovision: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__318707c37619d0f587a691cb248413b6dd4ff6a0c930d478bd096aa58d91fc09(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1fa50579658d1d3363758b2cc54ea3f4489a94dbdd2d909d515a56234d25a3f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b476bcebfb5ac3259617742a8600347d65741c0f0fae9b6a69721d6fea921de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6387757982a8c33ac9abe19a51938065f97075803ce2ef7578ab94be7915925c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fed12a6477c46a4ace1e3bdcbbd3daed48f7e7d384aaea665d9ad53807b8fcb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c95de4605d0427a4cc4714be74da8d1d963a3b2772a5e3658a92d1e081697b5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessIdentityProviderScimConfig]],
) -> None:
    """Type checking stubs"""
    pass
