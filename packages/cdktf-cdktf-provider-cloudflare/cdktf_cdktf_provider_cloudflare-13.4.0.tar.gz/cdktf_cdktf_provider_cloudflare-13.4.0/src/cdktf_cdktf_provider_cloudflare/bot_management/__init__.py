r'''
# `cloudflare_bot_management`

Refer to the Terraform Registry for docs: [`cloudflare_bot_management`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management).
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


class BotManagement(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.botManagement.BotManagement",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management cloudflare_bot_management}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        zone_id: builtins.str,
        ai_bots_protection: typing.Optional[builtins.str] = None,
        auto_update_model: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        bm_cookie_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        crawler_protection: typing.Optional[builtins.str] = None,
        enable_js: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fight_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_robots_txt_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        optimize_wordpress: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sbfm_definitely_automated: typing.Optional[builtins.str] = None,
        sbfm_likely_automated: typing.Optional[builtins.str] = None,
        sbfm_static_resource_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sbfm_verified_bots: typing.Optional[builtins.str] = None,
        suppress_session_score: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management cloudflare_bot_management} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#zone_id BotManagement#zone_id}
        :param ai_bots_protection: Enable rule to block AI Scrapers and Crawlers. Please note the value ``only_on_ad_pages`` is currently not available for Enterprise customers. Available values: "block", "disabled", "only_on_ad_pages". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#ai_bots_protection BotManagement#ai_bots_protection}
        :param auto_update_model: Automatically update to the newest bot detection models created by Cloudflare as they are released. `Learn more. <https://developers.cloudflare.com/bots/reference/machine-learning-models#model-versions-and-release-notes>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#auto_update_model BotManagement#auto_update_model}
        :param bm_cookie_enabled: Indicates that the bot management cookie can be placed on end user devices accessing the site. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#bm_cookie_enabled BotManagement#bm_cookie_enabled}
        :param crawler_protection: Enable rule to punish AI Scrapers and Crawlers via a link maze. Available values: "enabled", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#crawler_protection BotManagement#crawler_protection}
        :param enable_js: Use lightweight, invisible JavaScript detections to improve Bot Management. `Learn more about JavaScript Detections <https://developers.cloudflare.com/bots/reference/javascript-detections/>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#enable_js BotManagement#enable_js}
        :param fight_mode: Whether to enable Bot Fight Mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#fight_mode BotManagement#fight_mode}
        :param is_robots_txt_managed: Enable cloudflare managed robots.txt. If an existing robots.txt is detected, then managed robots.txt will be prepended to the existing robots.txt. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#is_robots_txt_managed BotManagement#is_robots_txt_managed}
        :param optimize_wordpress: Whether to optimize Super Bot Fight Mode protections for Wordpress. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#optimize_wordpress BotManagement#optimize_wordpress}
        :param sbfm_definitely_automated: Super Bot Fight Mode (SBFM) action to take on definitely automated requests. Available values: "allow", "block", "managed_challenge". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_definitely_automated BotManagement#sbfm_definitely_automated}
        :param sbfm_likely_automated: Super Bot Fight Mode (SBFM) action to take on likely automated requests. Available values: "allow", "block", "managed_challenge". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_likely_automated BotManagement#sbfm_likely_automated}
        :param sbfm_static_resource_protection: Super Bot Fight Mode (SBFM) to enable static resource protection. Enable if static resources on your application need bot protection. Note: Static resource protection can also result in legitimate traffic being blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_static_resource_protection BotManagement#sbfm_static_resource_protection}
        :param sbfm_verified_bots: Super Bot Fight Mode (SBFM) action to take on verified bots requests. Available values: "allow", "block". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_verified_bots BotManagement#sbfm_verified_bots}
        :param suppress_session_score: Whether to disable tracking the highest bot score for a session in the Bot Management cookie. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#suppress_session_score BotManagement#suppress_session_score}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__835e9cd225f36521bfacdb79a5efebf9df0246f752c7e1119e4df005eff6907f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = BotManagementConfig(
            zone_id=zone_id,
            ai_bots_protection=ai_bots_protection,
            auto_update_model=auto_update_model,
            bm_cookie_enabled=bm_cookie_enabled,
            crawler_protection=crawler_protection,
            enable_js=enable_js,
            fight_mode=fight_mode,
            is_robots_txt_managed=is_robots_txt_managed,
            optimize_wordpress=optimize_wordpress,
            sbfm_definitely_automated=sbfm_definitely_automated,
            sbfm_likely_automated=sbfm_likely_automated,
            sbfm_static_resource_protection=sbfm_static_resource_protection,
            sbfm_verified_bots=sbfm_verified_bots,
            suppress_session_score=suppress_session_score,
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
        '''Generates CDKTF code for importing a BotManagement resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the BotManagement to import.
        :param import_from_id: The id of the existing BotManagement that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the BotManagement to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15ac1f6dc4ff03a5f31ec5146e65620530ca9fd5cdb79724e67ebc7f7ffbe322)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAiBotsProtection")
    def reset_ai_bots_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAiBotsProtection", []))

    @jsii.member(jsii_name="resetAutoUpdateModel")
    def reset_auto_update_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoUpdateModel", []))

    @jsii.member(jsii_name="resetBmCookieEnabled")
    def reset_bm_cookie_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBmCookieEnabled", []))

    @jsii.member(jsii_name="resetCrawlerProtection")
    def reset_crawler_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCrawlerProtection", []))

    @jsii.member(jsii_name="resetEnableJs")
    def reset_enable_js(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableJs", []))

    @jsii.member(jsii_name="resetFightMode")
    def reset_fight_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFightMode", []))

    @jsii.member(jsii_name="resetIsRobotsTxtManaged")
    def reset_is_robots_txt_managed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsRobotsTxtManaged", []))

    @jsii.member(jsii_name="resetOptimizeWordpress")
    def reset_optimize_wordpress(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptimizeWordpress", []))

    @jsii.member(jsii_name="resetSbfmDefinitelyAutomated")
    def reset_sbfm_definitely_automated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSbfmDefinitelyAutomated", []))

    @jsii.member(jsii_name="resetSbfmLikelyAutomated")
    def reset_sbfm_likely_automated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSbfmLikelyAutomated", []))

    @jsii.member(jsii_name="resetSbfmStaticResourceProtection")
    def reset_sbfm_static_resource_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSbfmStaticResourceProtection", []))

    @jsii.member(jsii_name="resetSbfmVerifiedBots")
    def reset_sbfm_verified_bots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSbfmVerifiedBots", []))

    @jsii.member(jsii_name="resetSuppressSessionScore")
    def reset_suppress_session_score(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuppressSessionScore", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="staleZoneConfiguration")
    def stale_zone_configuration(
        self,
    ) -> "BotManagementStaleZoneConfigurationOutputReference":
        return typing.cast("BotManagementStaleZoneConfigurationOutputReference", jsii.get(self, "staleZoneConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="usingLatestModel")
    def using_latest_model(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "usingLatestModel"))

    @builtins.property
    @jsii.member(jsii_name="aiBotsProtectionInput")
    def ai_bots_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aiBotsProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="autoUpdateModelInput")
    def auto_update_model_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoUpdateModelInput"))

    @builtins.property
    @jsii.member(jsii_name="bmCookieEnabledInput")
    def bm_cookie_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "bmCookieEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="crawlerProtectionInput")
    def crawler_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "crawlerProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="enableJsInput")
    def enable_js_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableJsInput"))

    @builtins.property
    @jsii.member(jsii_name="fightModeInput")
    def fight_mode_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "fightModeInput"))

    @builtins.property
    @jsii.member(jsii_name="isRobotsTxtManagedInput")
    def is_robots_txt_managed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isRobotsTxtManagedInput"))

    @builtins.property
    @jsii.member(jsii_name="optimizeWordpressInput")
    def optimize_wordpress_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "optimizeWordpressInput"))

    @builtins.property
    @jsii.member(jsii_name="sbfmDefinitelyAutomatedInput")
    def sbfm_definitely_automated_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sbfmDefinitelyAutomatedInput"))

    @builtins.property
    @jsii.member(jsii_name="sbfmLikelyAutomatedInput")
    def sbfm_likely_automated_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sbfmLikelyAutomatedInput"))

    @builtins.property
    @jsii.member(jsii_name="sbfmStaticResourceProtectionInput")
    def sbfm_static_resource_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sbfmStaticResourceProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="sbfmVerifiedBotsInput")
    def sbfm_verified_bots_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sbfmVerifiedBotsInput"))

    @builtins.property
    @jsii.member(jsii_name="suppressSessionScoreInput")
    def suppress_session_score_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "suppressSessionScoreInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="aiBotsProtection")
    def ai_bots_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aiBotsProtection"))

    @ai_bots_protection.setter
    def ai_bots_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__477a4820500c756b727f02e46042c5ac483938129dc042e17171462f65456dc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aiBotsProtection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoUpdateModel")
    def auto_update_model(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoUpdateModel"))

    @auto_update_model.setter
    def auto_update_model(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98d0f34d9ebf8e345d24278be7202c4281e28c5f893928a6941c32a0b7f1a2c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoUpdateModel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bmCookieEnabled")
    def bm_cookie_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "bmCookieEnabled"))

    @bm_cookie_enabled.setter
    def bm_cookie_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b56cd21c61d34c195175d01cb1f20d29aeb283a8db1fba1edd6620220dab5b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bmCookieEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="crawlerProtection")
    def crawler_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "crawlerProtection"))

    @crawler_protection.setter
    def crawler_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1772d6a5f0ec8bdc9aa438f693817a0476fc9b5037a9eae34a4a9686aa4c0754)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crawlerProtection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableJs")
    def enable_js(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableJs"))

    @enable_js.setter
    def enable_js(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8335d3dc411549438d9df6e31e1790f126fc13f23a0d5f55fe8d2d36ff7d771)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableJs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fightMode")
    def fight_mode(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "fightMode"))

    @fight_mode.setter
    def fight_mode(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91d7241e3b6316002a49c1109ba63f39ef9e6a2e8ecf1ca79c657697d248a8ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fightMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isRobotsTxtManaged")
    def is_robots_txt_managed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isRobotsTxtManaged"))

    @is_robots_txt_managed.setter
    def is_robots_txt_managed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2377327bfd325d15929b2f0a1466b7c96d7f3a6130ac1832c8593006685127a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isRobotsTxtManaged", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="optimizeWordpress")
    def optimize_wordpress(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "optimizeWordpress"))

    @optimize_wordpress.setter
    def optimize_wordpress(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70d22312d2eadff0db80819005ff554d683174c4df667137c49ce4304661f2c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "optimizeWordpress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sbfmDefinitelyAutomated")
    def sbfm_definitely_automated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sbfmDefinitelyAutomated"))

    @sbfm_definitely_automated.setter
    def sbfm_definitely_automated(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9a9e65cdeb34c6147ed24305f616cf13b9391e59a0f651a33b7878fc9f8d123)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sbfmDefinitelyAutomated", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sbfmLikelyAutomated")
    def sbfm_likely_automated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sbfmLikelyAutomated"))

    @sbfm_likely_automated.setter
    def sbfm_likely_automated(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bf875d965e5ada558c7f52327669b3118de4768a53c97bfbb390bd3bb952531)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sbfmLikelyAutomated", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sbfmStaticResourceProtection")
    def sbfm_static_resource_protection(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "sbfmStaticResourceProtection"))

    @sbfm_static_resource_protection.setter
    def sbfm_static_resource_protection(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a5fedbd661a4a4e1966513ffa3a349929ba544cad2b9c5d526fc87a233c0655)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sbfmStaticResourceProtection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sbfmVerifiedBots")
    def sbfm_verified_bots(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sbfmVerifiedBots"))

    @sbfm_verified_bots.setter
    def sbfm_verified_bots(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bddfb4fc5703a9f1be7a738a3a2ee2f516fb75ebdfc39485a5a0a83809d7de1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sbfmVerifiedBots", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="suppressSessionScore")
    def suppress_session_score(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "suppressSessionScore"))

    @suppress_session_score.setter
    def suppress_session_score(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__495ee6a893808fb81c9eb6e86cfab1999189a2026448553bb159a3c9d41b98c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suppressSessionScore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbef026fa53028e4e8082cdc0393f5f0682b89190f1151166138e33c2d2253c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.botManagement.BotManagementConfig",
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
        "ai_bots_protection": "aiBotsProtection",
        "auto_update_model": "autoUpdateModel",
        "bm_cookie_enabled": "bmCookieEnabled",
        "crawler_protection": "crawlerProtection",
        "enable_js": "enableJs",
        "fight_mode": "fightMode",
        "is_robots_txt_managed": "isRobotsTxtManaged",
        "optimize_wordpress": "optimizeWordpress",
        "sbfm_definitely_automated": "sbfmDefinitelyAutomated",
        "sbfm_likely_automated": "sbfmLikelyAutomated",
        "sbfm_static_resource_protection": "sbfmStaticResourceProtection",
        "sbfm_verified_bots": "sbfmVerifiedBots",
        "suppress_session_score": "suppressSessionScore",
    },
)
class BotManagementConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        ai_bots_protection: typing.Optional[builtins.str] = None,
        auto_update_model: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        bm_cookie_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        crawler_protection: typing.Optional[builtins.str] = None,
        enable_js: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fight_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_robots_txt_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        optimize_wordpress: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sbfm_definitely_automated: typing.Optional[builtins.str] = None,
        sbfm_likely_automated: typing.Optional[builtins.str] = None,
        sbfm_static_resource_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sbfm_verified_bots: typing.Optional[builtins.str] = None,
        suppress_session_score: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#zone_id BotManagement#zone_id}
        :param ai_bots_protection: Enable rule to block AI Scrapers and Crawlers. Please note the value ``only_on_ad_pages`` is currently not available for Enterprise customers. Available values: "block", "disabled", "only_on_ad_pages". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#ai_bots_protection BotManagement#ai_bots_protection}
        :param auto_update_model: Automatically update to the newest bot detection models created by Cloudflare as they are released. `Learn more. <https://developers.cloudflare.com/bots/reference/machine-learning-models#model-versions-and-release-notes>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#auto_update_model BotManagement#auto_update_model}
        :param bm_cookie_enabled: Indicates that the bot management cookie can be placed on end user devices accessing the site. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#bm_cookie_enabled BotManagement#bm_cookie_enabled}
        :param crawler_protection: Enable rule to punish AI Scrapers and Crawlers via a link maze. Available values: "enabled", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#crawler_protection BotManagement#crawler_protection}
        :param enable_js: Use lightweight, invisible JavaScript detections to improve Bot Management. `Learn more about JavaScript Detections <https://developers.cloudflare.com/bots/reference/javascript-detections/>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#enable_js BotManagement#enable_js}
        :param fight_mode: Whether to enable Bot Fight Mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#fight_mode BotManagement#fight_mode}
        :param is_robots_txt_managed: Enable cloudflare managed robots.txt. If an existing robots.txt is detected, then managed robots.txt will be prepended to the existing robots.txt. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#is_robots_txt_managed BotManagement#is_robots_txt_managed}
        :param optimize_wordpress: Whether to optimize Super Bot Fight Mode protections for Wordpress. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#optimize_wordpress BotManagement#optimize_wordpress}
        :param sbfm_definitely_automated: Super Bot Fight Mode (SBFM) action to take on definitely automated requests. Available values: "allow", "block", "managed_challenge". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_definitely_automated BotManagement#sbfm_definitely_automated}
        :param sbfm_likely_automated: Super Bot Fight Mode (SBFM) action to take on likely automated requests. Available values: "allow", "block", "managed_challenge". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_likely_automated BotManagement#sbfm_likely_automated}
        :param sbfm_static_resource_protection: Super Bot Fight Mode (SBFM) to enable static resource protection. Enable if static resources on your application need bot protection. Note: Static resource protection can also result in legitimate traffic being blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_static_resource_protection BotManagement#sbfm_static_resource_protection}
        :param sbfm_verified_bots: Super Bot Fight Mode (SBFM) action to take on verified bots requests. Available values: "allow", "block". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_verified_bots BotManagement#sbfm_verified_bots}
        :param suppress_session_score: Whether to disable tracking the highest bot score for a session in the Bot Management cookie. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#suppress_session_score BotManagement#suppress_session_score}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf0fb1213d736e869bd1a1a79c3a6f923d7b272cdd96e5e9ad62fc87faef40b9)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument ai_bots_protection", value=ai_bots_protection, expected_type=type_hints["ai_bots_protection"])
            check_type(argname="argument auto_update_model", value=auto_update_model, expected_type=type_hints["auto_update_model"])
            check_type(argname="argument bm_cookie_enabled", value=bm_cookie_enabled, expected_type=type_hints["bm_cookie_enabled"])
            check_type(argname="argument crawler_protection", value=crawler_protection, expected_type=type_hints["crawler_protection"])
            check_type(argname="argument enable_js", value=enable_js, expected_type=type_hints["enable_js"])
            check_type(argname="argument fight_mode", value=fight_mode, expected_type=type_hints["fight_mode"])
            check_type(argname="argument is_robots_txt_managed", value=is_robots_txt_managed, expected_type=type_hints["is_robots_txt_managed"])
            check_type(argname="argument optimize_wordpress", value=optimize_wordpress, expected_type=type_hints["optimize_wordpress"])
            check_type(argname="argument sbfm_definitely_automated", value=sbfm_definitely_automated, expected_type=type_hints["sbfm_definitely_automated"])
            check_type(argname="argument sbfm_likely_automated", value=sbfm_likely_automated, expected_type=type_hints["sbfm_likely_automated"])
            check_type(argname="argument sbfm_static_resource_protection", value=sbfm_static_resource_protection, expected_type=type_hints["sbfm_static_resource_protection"])
            check_type(argname="argument sbfm_verified_bots", value=sbfm_verified_bots, expected_type=type_hints["sbfm_verified_bots"])
            check_type(argname="argument suppress_session_score", value=suppress_session_score, expected_type=type_hints["suppress_session_score"])
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
        if ai_bots_protection is not None:
            self._values["ai_bots_protection"] = ai_bots_protection
        if auto_update_model is not None:
            self._values["auto_update_model"] = auto_update_model
        if bm_cookie_enabled is not None:
            self._values["bm_cookie_enabled"] = bm_cookie_enabled
        if crawler_protection is not None:
            self._values["crawler_protection"] = crawler_protection
        if enable_js is not None:
            self._values["enable_js"] = enable_js
        if fight_mode is not None:
            self._values["fight_mode"] = fight_mode
        if is_robots_txt_managed is not None:
            self._values["is_robots_txt_managed"] = is_robots_txt_managed
        if optimize_wordpress is not None:
            self._values["optimize_wordpress"] = optimize_wordpress
        if sbfm_definitely_automated is not None:
            self._values["sbfm_definitely_automated"] = sbfm_definitely_automated
        if sbfm_likely_automated is not None:
            self._values["sbfm_likely_automated"] = sbfm_likely_automated
        if sbfm_static_resource_protection is not None:
            self._values["sbfm_static_resource_protection"] = sbfm_static_resource_protection
        if sbfm_verified_bots is not None:
            self._values["sbfm_verified_bots"] = sbfm_verified_bots
        if suppress_session_score is not None:
            self._values["suppress_session_score"] = suppress_session_score

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#zone_id BotManagement#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ai_bots_protection(self) -> typing.Optional[builtins.str]:
        '''Enable rule to block AI Scrapers and Crawlers.

        Please note the value ``only_on_ad_pages`` is currently not available for Enterprise customers.
        Available values: "block", "disabled", "only_on_ad_pages".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#ai_bots_protection BotManagement#ai_bots_protection}
        '''
        result = self._values.get("ai_bots_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_update_model(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Automatically update to the newest bot detection models created by Cloudflare as they are released. `Learn more. <https://developers.cloudflare.com/bots/reference/machine-learning-models#model-versions-and-release-notes>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#auto_update_model BotManagement#auto_update_model}
        '''
        result = self._values.get("auto_update_model")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def bm_cookie_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates that the bot management cookie can be placed on end user devices accessing the site. Defaults to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#bm_cookie_enabled BotManagement#bm_cookie_enabled}
        '''
        result = self._values.get("bm_cookie_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def crawler_protection(self) -> typing.Optional[builtins.str]:
        '''Enable rule to punish AI Scrapers and Crawlers via a link maze. Available values: "enabled", "disabled".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#crawler_protection BotManagement#crawler_protection}
        '''
        result = self._values.get("crawler_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_js(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use lightweight, invisible JavaScript detections to improve Bot Management. `Learn more about JavaScript Detections <https://developers.cloudflare.com/bots/reference/javascript-detections/>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#enable_js BotManagement#enable_js}
        '''
        result = self._values.get("enable_js")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def fight_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to enable Bot Fight Mode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#fight_mode BotManagement#fight_mode}
        '''
        result = self._values.get("fight_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_robots_txt_managed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable cloudflare managed robots.txt. If an existing robots.txt is detected, then managed robots.txt will be prepended to the existing robots.txt.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#is_robots_txt_managed BotManagement#is_robots_txt_managed}
        '''
        result = self._values.get("is_robots_txt_managed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def optimize_wordpress(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to optimize Super Bot Fight Mode protections for Wordpress.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#optimize_wordpress BotManagement#optimize_wordpress}
        '''
        result = self._values.get("optimize_wordpress")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sbfm_definitely_automated(self) -> typing.Optional[builtins.str]:
        '''Super Bot Fight Mode (SBFM) action to take on definitely automated requests. Available values: "allow", "block", "managed_challenge".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_definitely_automated BotManagement#sbfm_definitely_automated}
        '''
        result = self._values.get("sbfm_definitely_automated")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sbfm_likely_automated(self) -> typing.Optional[builtins.str]:
        '''Super Bot Fight Mode (SBFM) action to take on likely automated requests. Available values: "allow", "block", "managed_challenge".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_likely_automated BotManagement#sbfm_likely_automated}
        '''
        result = self._values.get("sbfm_likely_automated")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sbfm_static_resource_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Super Bot Fight Mode (SBFM) to enable static resource protection.

        Enable if static resources on your application need bot protection.
        Note: Static resource protection can also result in legitimate traffic being blocked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_static_resource_protection BotManagement#sbfm_static_resource_protection}
        '''
        result = self._values.get("sbfm_static_resource_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sbfm_verified_bots(self) -> typing.Optional[builtins.str]:
        '''Super Bot Fight Mode (SBFM) action to take on verified bots requests. Available values: "allow", "block".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#sbfm_verified_bots BotManagement#sbfm_verified_bots}
        '''
        result = self._values.get("sbfm_verified_bots")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_session_score(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to disable tracking the highest bot score for a session in the Bot Management cookie.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/bot_management#suppress_session_score BotManagement#suppress_session_score}
        '''
        result = self._values.get("suppress_session_score")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BotManagementConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.botManagement.BotManagementStaleZoneConfiguration",
    jsii_struct_bases=[],
    name_mapping={},
)
class BotManagementStaleZoneConfiguration:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BotManagementStaleZoneConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BotManagementStaleZoneConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.botManagement.BotManagementStaleZoneConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a61a921194d56fd46a0488c66433419185ab67c9edafbc316253006de24c37df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="fightMode")
    def fight_mode(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "fightMode"))

    @builtins.property
    @jsii.member(jsii_name="optimizeWordpress")
    def optimize_wordpress(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "optimizeWordpress"))

    @builtins.property
    @jsii.member(jsii_name="sbfmDefinitelyAutomated")
    def sbfm_definitely_automated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sbfmDefinitelyAutomated"))

    @builtins.property
    @jsii.member(jsii_name="sbfmLikelyAutomated")
    def sbfm_likely_automated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sbfmLikelyAutomated"))

    @builtins.property
    @jsii.member(jsii_name="sbfmStaticResourceProtection")
    def sbfm_static_resource_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sbfmStaticResourceProtection"))

    @builtins.property
    @jsii.member(jsii_name="sbfmVerifiedBots")
    def sbfm_verified_bots(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sbfmVerifiedBots"))

    @builtins.property
    @jsii.member(jsii_name="suppressSessionScore")
    def suppress_session_score(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "suppressSessionScore"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BotManagementStaleZoneConfiguration]:
        return typing.cast(typing.Optional[BotManagementStaleZoneConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BotManagementStaleZoneConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20b9786aced8324c7c6f0108592dd4954ec25129a5d85e29a8685b8fdd6e0e00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "BotManagement",
    "BotManagementConfig",
    "BotManagementStaleZoneConfiguration",
    "BotManagementStaleZoneConfigurationOutputReference",
]

publication.publish()

def _typecheckingstub__835e9cd225f36521bfacdb79a5efebf9df0246f752c7e1119e4df005eff6907f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    zone_id: builtins.str,
    ai_bots_protection: typing.Optional[builtins.str] = None,
    auto_update_model: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    bm_cookie_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    crawler_protection: typing.Optional[builtins.str] = None,
    enable_js: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fight_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_robots_txt_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    optimize_wordpress: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sbfm_definitely_automated: typing.Optional[builtins.str] = None,
    sbfm_likely_automated: typing.Optional[builtins.str] = None,
    sbfm_static_resource_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sbfm_verified_bots: typing.Optional[builtins.str] = None,
    suppress_session_score: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__15ac1f6dc4ff03a5f31ec5146e65620530ca9fd5cdb79724e67ebc7f7ffbe322(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__477a4820500c756b727f02e46042c5ac483938129dc042e17171462f65456dc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98d0f34d9ebf8e345d24278be7202c4281e28c5f893928a6941c32a0b7f1a2c3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b56cd21c61d34c195175d01cb1f20d29aeb283a8db1fba1edd6620220dab5b3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1772d6a5f0ec8bdc9aa438f693817a0476fc9b5037a9eae34a4a9686aa4c0754(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8335d3dc411549438d9df6e31e1790f126fc13f23a0d5f55fe8d2d36ff7d771(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91d7241e3b6316002a49c1109ba63f39ef9e6a2e8ecf1ca79c657697d248a8ae(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2377327bfd325d15929b2f0a1466b7c96d7f3a6130ac1832c8593006685127a0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70d22312d2eadff0db80819005ff554d683174c4df667137c49ce4304661f2c1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9a9e65cdeb34c6147ed24305f616cf13b9391e59a0f651a33b7878fc9f8d123(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bf875d965e5ada558c7f52327669b3118de4768a53c97bfbb390bd3bb952531(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a5fedbd661a4a4e1966513ffa3a349929ba544cad2b9c5d526fc87a233c0655(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bddfb4fc5703a9f1be7a738a3a2ee2f516fb75ebdfc39485a5a0a83809d7de1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__495ee6a893808fb81c9eb6e86cfab1999189a2026448553bb159a3c9d41b98c5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbef026fa53028e4e8082cdc0393f5f0682b89190f1151166138e33c2d2253c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf0fb1213d736e869bd1a1a79c3a6f923d7b272cdd96e5e9ad62fc87faef40b9(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: builtins.str,
    ai_bots_protection: typing.Optional[builtins.str] = None,
    auto_update_model: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    bm_cookie_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    crawler_protection: typing.Optional[builtins.str] = None,
    enable_js: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fight_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_robots_txt_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    optimize_wordpress: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sbfm_definitely_automated: typing.Optional[builtins.str] = None,
    sbfm_likely_automated: typing.Optional[builtins.str] = None,
    sbfm_static_resource_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sbfm_verified_bots: typing.Optional[builtins.str] = None,
    suppress_session_score: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a61a921194d56fd46a0488c66433419185ab67c9edafbc316253006de24c37df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20b9786aced8324c7c6f0108592dd4954ec25129a5d85e29a8685b8fdd6e0e00(
    value: typing.Optional[BotManagementStaleZoneConfiguration],
) -> None:
    """Type checking stubs"""
    pass
