r'''
# `provider`

Refer to the Terraform Registry for docs: [`cloudflare`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs).
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


class CloudflareProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.provider.CloudflareProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs cloudflare}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        api_key: typing.Optional[builtins.str] = None,
        api_token: typing.Optional[builtins.str] = None,
        api_user_service_key: typing.Optional[builtins.str] = None,
        base_url: typing.Optional[builtins.str] = None,
        email: typing.Optional[builtins.str] = None,
        user_agent_operator_suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs cloudflare} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#alias CloudflareProvider#alias}
        :param api_key: The API key for operations. Alternatively, can be configured using the ``CLOUDFLARE_API_KEY`` environment variable. API keys are `now considered legacy by Cloudflare <https://developers.cloudflare.com/fundamentals/api/get-started/keys/#limitations>`_, API tokens should be used instead. Must provide only one of ``api_key``, ``api_token``, ``api_user_service_key``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#api_key CloudflareProvider#api_key}
        :param api_token: The API Token for operations. Alternatively, can be configured using the ``CLOUDFLARE_API_TOKEN`` environment variable. Must provide only one of ``api_key``, ``api_token``, ``api_user_service_key``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#api_token CloudflareProvider#api_token}
        :param api_user_service_key: A special Cloudflare API key good for a restricted set of endpoints. Alternatively, can be configured using the ``CLOUDFLARE_API_USER_SERVICE_KEY`` environment variable. Must provide only one of ``api_key``, ``api_token``, ``api_user_service_key``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#api_user_service_key CloudflareProvider#api_user_service_key}
        :param base_url: Value to override the default HTTP client base URL. Alternatively, can be configured using the ``base_url`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#base_url CloudflareProvider#base_url}
        :param email: A registered Cloudflare email address. Alternatively, can be configured using the ``CLOUDFLARE_EMAIL`` environment variable. Required when using ``api_key``. Conflicts with ``api_token``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#email CloudflareProvider#email}
        :param user_agent_operator_suffix: A value to append to the HTTP User Agent for all API calls. This value is not something most users need to modify however, if you are using a non-standard provider or operator configuration, this is recommended to assist in uniquely identifying your traffic. **Setting this value will remove the Terraform version from the HTTP User Agent string and may have unintended consequences**. Alternatively, can be configured using the ``CLOUDFLARE_USER_AGENT_OPERATOR_SUFFIX`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#user_agent_operator_suffix CloudflareProvider#user_agent_operator_suffix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6c8ed5006d3e3fa5a2c23fad8b013482f81a5f8eb784f19b3759f2301dfe852)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = CloudflareProviderConfig(
            alias=alias,
            api_key=api_key,
            api_token=api_token,
            api_user_service_key=api_user_service_key,
            base_url=base_url,
            email=email,
            user_agent_operator_suffix=user_agent_operator_suffix,
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
        '''Generates CDKTF code for importing a CloudflareProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CloudflareProvider to import.
        :param import_from_id: The id of the existing CloudflareProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CloudflareProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d3d75b6652fb7c29104bc3370eada3fb496826950c55f9632e9bb68cf445f9c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @jsii.member(jsii_name="resetApiToken")
    def reset_api_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiToken", []))

    @jsii.member(jsii_name="resetApiUserServiceKey")
    def reset_api_user_service_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiUserServiceKey", []))

    @jsii.member(jsii_name="resetBaseUrl")
    def reset_base_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseUrl", []))

    @jsii.member(jsii_name="resetEmail")
    def reset_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmail", []))

    @jsii.member(jsii_name="resetUserAgentOperatorSuffix")
    def reset_user_agent_operator_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserAgentOperatorSuffix", []))

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
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="apiTokenInput")
    def api_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="apiUserServiceKeyInput")
    def api_user_service_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiUserServiceKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="baseUrlInput")
    def base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="userAgentOperatorSuffixInput")
    def user_agent_operator_suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userAgentOperatorSuffixInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c930854d6ea7147c8ed15c32af3e48deafd93fb8f753d8178b8b2404d9b1316)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dcacca017c51d23cee3b3d542660b1a4889ec7e22f721fbccb9c95ae9aa0db5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiToken")
    def api_token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiToken"))

    @api_token.setter
    def api_token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64356e8c2024559d318fd9a82d7a6699d2313b75587320a5a36f4dbc9d3854ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiUserServiceKey")
    def api_user_service_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiUserServiceKey"))

    @api_user_service_key.setter
    def api_user_service_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1d647dffa5e61b66c498aa264eb4a7f4a10e26bd61db9ae56567d4ad0ba322f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiUserServiceKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrl"))

    @base_url.setter
    def base_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afe4ad021c65f2a616e70db90b42903af09fb20c79c0c60c792d5bfe6f378097)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "email"))

    @email.setter
    def email(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8d25273a46ef4056e832d8bd4e26168c3442fb9b316190a8404e6a4d5efdd33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userAgentOperatorSuffix")
    def user_agent_operator_suffix(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userAgentOperatorSuffix"))

    @user_agent_operator_suffix.setter
    def user_agent_operator_suffix(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03dbeb5898bad7db445f44a34b30a3ddbe87bdf6addeb6a73105fcfefbcb8f2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userAgentOperatorSuffix", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.provider.CloudflareProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alias": "alias",
        "api_key": "apiKey",
        "api_token": "apiToken",
        "api_user_service_key": "apiUserServiceKey",
        "base_url": "baseUrl",
        "email": "email",
        "user_agent_operator_suffix": "userAgentOperatorSuffix",
    },
)
class CloudflareProviderConfig:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        api_key: typing.Optional[builtins.str] = None,
        api_token: typing.Optional[builtins.str] = None,
        api_user_service_key: typing.Optional[builtins.str] = None,
        base_url: typing.Optional[builtins.str] = None,
        email: typing.Optional[builtins.str] = None,
        user_agent_operator_suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#alias CloudflareProvider#alias}
        :param api_key: The API key for operations. Alternatively, can be configured using the ``CLOUDFLARE_API_KEY`` environment variable. API keys are `now considered legacy by Cloudflare <https://developers.cloudflare.com/fundamentals/api/get-started/keys/#limitations>`_, API tokens should be used instead. Must provide only one of ``api_key``, ``api_token``, ``api_user_service_key``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#api_key CloudflareProvider#api_key}
        :param api_token: The API Token for operations. Alternatively, can be configured using the ``CLOUDFLARE_API_TOKEN`` environment variable. Must provide only one of ``api_key``, ``api_token``, ``api_user_service_key``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#api_token CloudflareProvider#api_token}
        :param api_user_service_key: A special Cloudflare API key good for a restricted set of endpoints. Alternatively, can be configured using the ``CLOUDFLARE_API_USER_SERVICE_KEY`` environment variable. Must provide only one of ``api_key``, ``api_token``, ``api_user_service_key``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#api_user_service_key CloudflareProvider#api_user_service_key}
        :param base_url: Value to override the default HTTP client base URL. Alternatively, can be configured using the ``base_url`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#base_url CloudflareProvider#base_url}
        :param email: A registered Cloudflare email address. Alternatively, can be configured using the ``CLOUDFLARE_EMAIL`` environment variable. Required when using ``api_key``. Conflicts with ``api_token``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#email CloudflareProvider#email}
        :param user_agent_operator_suffix: A value to append to the HTTP User Agent for all API calls. This value is not something most users need to modify however, if you are using a non-standard provider or operator configuration, this is recommended to assist in uniquely identifying your traffic. **Setting this value will remove the Terraform version from the HTTP User Agent string and may have unintended consequences**. Alternatively, can be configured using the ``CLOUDFLARE_USER_AGENT_OPERATOR_SUFFIX`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#user_agent_operator_suffix CloudflareProvider#user_agent_operator_suffix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be8b5a991fa153b7d55c84e6205ae7cb1dbfa2bb0998c1fc9f399200956addc4)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument api_token", value=api_token, expected_type=type_hints["api_token"])
            check_type(argname="argument api_user_service_key", value=api_user_service_key, expected_type=type_hints["api_user_service_key"])
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument user_agent_operator_suffix", value=user_agent_operator_suffix, expected_type=type_hints["user_agent_operator_suffix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if api_key is not None:
            self._values["api_key"] = api_key
        if api_token is not None:
            self._values["api_token"] = api_token
        if api_user_service_key is not None:
            self._values["api_user_service_key"] = api_user_service_key
        if base_url is not None:
            self._values["base_url"] = base_url
        if email is not None:
            self._values["email"] = email
        if user_agent_operator_suffix is not None:
            self._values["user_agent_operator_suffix"] = user_agent_operator_suffix

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#alias CloudflareProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''The API key for operations.

        Alternatively, can be configured using the ``CLOUDFLARE_API_KEY`` environment variable. API keys are `now considered legacy by Cloudflare <https://developers.cloudflare.com/fundamentals/api/get-started/keys/#limitations>`_, API tokens should be used instead. Must provide only one of ``api_key``, ``api_token``, ``api_user_service_key``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#api_key CloudflareProvider#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_token(self) -> typing.Optional[builtins.str]:
        '''The API Token for operations.

        Alternatively, can be configured using the ``CLOUDFLARE_API_TOKEN`` environment variable. Must provide only one of ``api_key``, ``api_token``, ``api_user_service_key``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#api_token CloudflareProvider#api_token}
        '''
        result = self._values.get("api_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_user_service_key(self) -> typing.Optional[builtins.str]:
        '''A special Cloudflare API key good for a restricted set of endpoints.

        Alternatively, can be configured using the ``CLOUDFLARE_API_USER_SERVICE_KEY`` environment variable. Must provide only one of ``api_key``, ``api_token``, ``api_user_service_key``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#api_user_service_key CloudflareProvider#api_user_service_key}
        '''
        result = self._values.get("api_user_service_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def base_url(self) -> typing.Optional[builtins.str]:
        '''Value to override the default HTTP client base URL. Alternatively, can be configured using the ``base_url`` environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#base_url CloudflareProvider#base_url}
        '''
        result = self._values.get("base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''A registered Cloudflare email address.

        Alternatively, can be configured using the ``CLOUDFLARE_EMAIL`` environment variable. Required when using ``api_key``. Conflicts with ``api_token``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#email CloudflareProvider#email}
        '''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_agent_operator_suffix(self) -> typing.Optional[builtins.str]:
        '''A value to append to the HTTP User Agent for all API calls.

        This value is not something most users need to modify however, if you are using a non-standard provider or operator configuration, this is recommended to assist in uniquely identifying your traffic. **Setting this value will remove the Terraform version from the HTTP User Agent string and may have unintended consequences**. Alternatively, can be configured using the ``CLOUDFLARE_USER_AGENT_OPERATOR_SUFFIX`` environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs#user_agent_operator_suffix CloudflareProvider#user_agent_operator_suffix}
        '''
        result = self._values.get("user_agent_operator_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudflareProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CloudflareProvider",
    "CloudflareProviderConfig",
]

publication.publish()

def _typecheckingstub__e6c8ed5006d3e3fa5a2c23fad8b013482f81a5f8eb784f19b3759f2301dfe852(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alias: typing.Optional[builtins.str] = None,
    api_key: typing.Optional[builtins.str] = None,
    api_token: typing.Optional[builtins.str] = None,
    api_user_service_key: typing.Optional[builtins.str] = None,
    base_url: typing.Optional[builtins.str] = None,
    email: typing.Optional[builtins.str] = None,
    user_agent_operator_suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d3d75b6652fb7c29104bc3370eada3fb496826950c55f9632e9bb68cf445f9c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c930854d6ea7147c8ed15c32af3e48deafd93fb8f753d8178b8b2404d9b1316(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dcacca017c51d23cee3b3d542660b1a4889ec7e22f721fbccb9c95ae9aa0db5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64356e8c2024559d318fd9a82d7a6699d2313b75587320a5a36f4dbc9d3854ec(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1d647dffa5e61b66c498aa264eb4a7f4a10e26bd61db9ae56567d4ad0ba322f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afe4ad021c65f2a616e70db90b42903af09fb20c79c0c60c792d5bfe6f378097(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d25273a46ef4056e832d8bd4e26168c3442fb9b316190a8404e6a4d5efdd33(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03dbeb5898bad7db445f44a34b30a3ddbe87bdf6addeb6a73105fcfefbcb8f2e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be8b5a991fa153b7d55c84e6205ae7cb1dbfa2bb0998c1fc9f399200956addc4(
    *,
    alias: typing.Optional[builtins.str] = None,
    api_key: typing.Optional[builtins.str] = None,
    api_token: typing.Optional[builtins.str] = None,
    api_user_service_key: typing.Optional[builtins.str] = None,
    base_url: typing.Optional[builtins.str] = None,
    email: typing.Optional[builtins.str] = None,
    user_agent_operator_suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
