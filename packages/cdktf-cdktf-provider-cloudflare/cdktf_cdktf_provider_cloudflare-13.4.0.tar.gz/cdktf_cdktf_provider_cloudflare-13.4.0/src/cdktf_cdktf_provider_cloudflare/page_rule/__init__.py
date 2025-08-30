r'''
# `cloudflare_page_rule`

Refer to the Terraform Registry for docs: [`cloudflare_page_rule`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule).
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


class PageRule(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRule",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule cloudflare_page_rule}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        actions: typing.Union["PageRuleActions", typing.Dict[builtins.str, typing.Any]],
        target: builtins.str,
        zone_id: builtins.str,
        priority: typing.Optional[jsii.Number] = None,
        status: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule cloudflare_page_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param actions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#actions PageRule#actions}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#target PageRule#target}.
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#zone_id PageRule#zone_id}
        :param priority: The priority of the rule, used to define which Page Rule is processed over another. A higher number indicates a higher priority. For example, if you have a catch-all Page Rule (rule A: ``/images/*``) but want a more specific Page Rule to take precedence (rule B: ``/images/special/*``), specify a higher priority for rule B so it overrides rule A. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#priority PageRule#priority}
        :param status: The status of the Page Rule. Available values: "active", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#status PageRule#status}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__236eb22c254552fb3cf23c2853d4eb6d53d7d86e79695fe42050b09cbe48162d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = PageRuleConfig(
            actions=actions,
            target=target,
            zone_id=zone_id,
            priority=priority,
            status=status,
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
        '''Generates CDKTF code for importing a PageRule resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PageRule to import.
        :param import_from_id: The id of the existing PageRule that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PageRule to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d3e17519810100113ddebfef1d2a49f6ee3e5ac94d7cc629edf773b39799092)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putActions")
    def put_actions(
        self,
        *,
        always_use_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        automatic_https_rewrites: typing.Optional[builtins.str] = None,
        browser_cache_ttl: typing.Optional[jsii.Number] = None,
        browser_check: typing.Optional[builtins.str] = None,
        bypass_cache_on_cookie: typing.Optional[builtins.str] = None,
        cache_by_device_type: typing.Optional[builtins.str] = None,
        cache_deception_armor: typing.Optional[builtins.str] = None,
        cache_key_fields: typing.Optional[typing.Union["PageRuleActionsCacheKeyFields", typing.Dict[builtins.str, typing.Any]]] = None,
        cache_level: typing.Optional[builtins.str] = None,
        cache_on_cookie: typing.Optional[builtins.str] = None,
        cache_ttl_by_status: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        disable_apps: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_performance: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_security: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_zaraz: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        edge_cache_ttl: typing.Optional[jsii.Number] = None,
        email_obfuscation: typing.Optional[builtins.str] = None,
        explicit_cache_control: typing.Optional[builtins.str] = None,
        forwarding_url: typing.Optional[typing.Union["PageRuleActionsForwardingUrl", typing.Dict[builtins.str, typing.Any]]] = None,
        host_header_override: typing.Optional[builtins.str] = None,
        ip_geolocation: typing.Optional[builtins.str] = None,
        mirage: typing.Optional[builtins.str] = None,
        opportunistic_encryption: typing.Optional[builtins.str] = None,
        origin_error_page_pass_thru: typing.Optional[builtins.str] = None,
        polish: typing.Optional[builtins.str] = None,
        resolve_override: typing.Optional[builtins.str] = None,
        respect_strong_etag: typing.Optional[builtins.str] = None,
        response_buffering: typing.Optional[builtins.str] = None,
        rocket_loader: typing.Optional[builtins.str] = None,
        security_level: typing.Optional[builtins.str] = None,
        sort_query_string_for_cache: typing.Optional[builtins.str] = None,
        ssl: typing.Optional[builtins.str] = None,
        true_client_ip_header: typing.Optional[builtins.str] = None,
        waf: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param always_use_https: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#always_use_https PageRule#always_use_https}.
        :param automatic_https_rewrites: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#automatic_https_rewrites PageRule#automatic_https_rewrites}.
        :param browser_cache_ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#browser_cache_ttl PageRule#browser_cache_ttl}.
        :param browser_check: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#browser_check PageRule#browser_check}.
        :param bypass_cache_on_cookie: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#bypass_cache_on_cookie PageRule#bypass_cache_on_cookie}.
        :param cache_by_device_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_by_device_type PageRule#cache_by_device_type}.
        :param cache_deception_armor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_deception_armor PageRule#cache_deception_armor}.
        :param cache_key_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_key_fields PageRule#cache_key_fields}.
        :param cache_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_level PageRule#cache_level}.
        :param cache_on_cookie: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_on_cookie PageRule#cache_on_cookie}.
        :param cache_ttl_by_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_ttl_by_status PageRule#cache_ttl_by_status}.
        :param disable_apps: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_apps PageRule#disable_apps}.
        :param disable_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_performance PageRule#disable_performance}.
        :param disable_security: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_security PageRule#disable_security}.
        :param disable_zaraz: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_zaraz PageRule#disable_zaraz}.
        :param edge_cache_ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#edge_cache_ttl PageRule#edge_cache_ttl}.
        :param email_obfuscation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#email_obfuscation PageRule#email_obfuscation}.
        :param explicit_cache_control: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#explicit_cache_control PageRule#explicit_cache_control}.
        :param forwarding_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#forwarding_url PageRule#forwarding_url}.
        :param host_header_override: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#host_header_override PageRule#host_header_override}.
        :param ip_geolocation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#ip_geolocation PageRule#ip_geolocation}.
        :param mirage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#mirage PageRule#mirage}.
        :param opportunistic_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#opportunistic_encryption PageRule#opportunistic_encryption}.
        :param origin_error_page_pass_thru: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#origin_error_page_pass_thru PageRule#origin_error_page_pass_thru}.
        :param polish: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#polish PageRule#polish}.
        :param resolve_override: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#resolve_override PageRule#resolve_override}.
        :param respect_strong_etag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#respect_strong_etag PageRule#respect_strong_etag}.
        :param response_buffering: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#response_buffering PageRule#response_buffering}.
        :param rocket_loader: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#rocket_loader PageRule#rocket_loader}.
        :param security_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#security_level PageRule#security_level}.
        :param sort_query_string_for_cache: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#sort_query_string_for_cache PageRule#sort_query_string_for_cache}.
        :param ssl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#ssl PageRule#ssl}.
        :param true_client_ip_header: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#true_client_ip_header PageRule#true_client_ip_header}.
        :param waf: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#waf PageRule#waf}.
        '''
        value = PageRuleActions(
            always_use_https=always_use_https,
            automatic_https_rewrites=automatic_https_rewrites,
            browser_cache_ttl=browser_cache_ttl,
            browser_check=browser_check,
            bypass_cache_on_cookie=bypass_cache_on_cookie,
            cache_by_device_type=cache_by_device_type,
            cache_deception_armor=cache_deception_armor,
            cache_key_fields=cache_key_fields,
            cache_level=cache_level,
            cache_on_cookie=cache_on_cookie,
            cache_ttl_by_status=cache_ttl_by_status,
            disable_apps=disable_apps,
            disable_performance=disable_performance,
            disable_security=disable_security,
            disable_zaraz=disable_zaraz,
            edge_cache_ttl=edge_cache_ttl,
            email_obfuscation=email_obfuscation,
            explicit_cache_control=explicit_cache_control,
            forwarding_url=forwarding_url,
            host_header_override=host_header_override,
            ip_geolocation=ip_geolocation,
            mirage=mirage,
            opportunistic_encryption=opportunistic_encryption,
            origin_error_page_pass_thru=origin_error_page_pass_thru,
            polish=polish,
            resolve_override=resolve_override,
            respect_strong_etag=respect_strong_etag,
            response_buffering=response_buffering,
            rocket_loader=rocket_loader,
            security_level=security_level,
            sort_query_string_for_cache=sort_query_string_for_cache,
            ssl=ssl,
            true_client_ip_header=true_client_ip_header,
            waf=waf,
        )

        return typing.cast(None, jsii.invoke(self, "putActions", [value]))

    @jsii.member(jsii_name="resetPriority")
    def reset_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPriority", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

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
    @jsii.member(jsii_name="actions")
    def actions(self) -> "PageRuleActionsOutputReference":
        return typing.cast("PageRuleActionsOutputReference", jsii.get(self, "actions"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="actionsInput")
    def actions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PageRuleActions"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PageRuleActions"]], jsii.get(self, "actionsInput"))

    @builtins.property
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78425583a59687d7d3b90d46a1d2c7d785c671efe36f9e03f9806f786af0a72c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaba95fc3909ae63549960f5fff0ef615946f26afe55d2be892ac944f9459363)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__823ee4bd39a3fae9f80cd2f5ee7fabda4d0c2c54dd654c2ce6cbf8804f03ac2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__723448f003c4960eed4dd173610dd894938391dc9d4dbba736099a60da5caf89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActions",
    jsii_struct_bases=[],
    name_mapping={
        "always_use_https": "alwaysUseHttps",
        "automatic_https_rewrites": "automaticHttpsRewrites",
        "browser_cache_ttl": "browserCacheTtl",
        "browser_check": "browserCheck",
        "bypass_cache_on_cookie": "bypassCacheOnCookie",
        "cache_by_device_type": "cacheByDeviceType",
        "cache_deception_armor": "cacheDeceptionArmor",
        "cache_key_fields": "cacheKeyFields",
        "cache_level": "cacheLevel",
        "cache_on_cookie": "cacheOnCookie",
        "cache_ttl_by_status": "cacheTtlByStatus",
        "disable_apps": "disableApps",
        "disable_performance": "disablePerformance",
        "disable_security": "disableSecurity",
        "disable_zaraz": "disableZaraz",
        "edge_cache_ttl": "edgeCacheTtl",
        "email_obfuscation": "emailObfuscation",
        "explicit_cache_control": "explicitCacheControl",
        "forwarding_url": "forwardingUrl",
        "host_header_override": "hostHeaderOverride",
        "ip_geolocation": "ipGeolocation",
        "mirage": "mirage",
        "opportunistic_encryption": "opportunisticEncryption",
        "origin_error_page_pass_thru": "originErrorPagePassThru",
        "polish": "polish",
        "resolve_override": "resolveOverride",
        "respect_strong_etag": "respectStrongEtag",
        "response_buffering": "responseBuffering",
        "rocket_loader": "rocketLoader",
        "security_level": "securityLevel",
        "sort_query_string_for_cache": "sortQueryStringForCache",
        "ssl": "ssl",
        "true_client_ip_header": "trueClientIpHeader",
        "waf": "waf",
    },
)
class PageRuleActions:
    def __init__(
        self,
        *,
        always_use_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        automatic_https_rewrites: typing.Optional[builtins.str] = None,
        browser_cache_ttl: typing.Optional[jsii.Number] = None,
        browser_check: typing.Optional[builtins.str] = None,
        bypass_cache_on_cookie: typing.Optional[builtins.str] = None,
        cache_by_device_type: typing.Optional[builtins.str] = None,
        cache_deception_armor: typing.Optional[builtins.str] = None,
        cache_key_fields: typing.Optional[typing.Union["PageRuleActionsCacheKeyFields", typing.Dict[builtins.str, typing.Any]]] = None,
        cache_level: typing.Optional[builtins.str] = None,
        cache_on_cookie: typing.Optional[builtins.str] = None,
        cache_ttl_by_status: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        disable_apps: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_performance: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_security: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_zaraz: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        edge_cache_ttl: typing.Optional[jsii.Number] = None,
        email_obfuscation: typing.Optional[builtins.str] = None,
        explicit_cache_control: typing.Optional[builtins.str] = None,
        forwarding_url: typing.Optional[typing.Union["PageRuleActionsForwardingUrl", typing.Dict[builtins.str, typing.Any]]] = None,
        host_header_override: typing.Optional[builtins.str] = None,
        ip_geolocation: typing.Optional[builtins.str] = None,
        mirage: typing.Optional[builtins.str] = None,
        opportunistic_encryption: typing.Optional[builtins.str] = None,
        origin_error_page_pass_thru: typing.Optional[builtins.str] = None,
        polish: typing.Optional[builtins.str] = None,
        resolve_override: typing.Optional[builtins.str] = None,
        respect_strong_etag: typing.Optional[builtins.str] = None,
        response_buffering: typing.Optional[builtins.str] = None,
        rocket_loader: typing.Optional[builtins.str] = None,
        security_level: typing.Optional[builtins.str] = None,
        sort_query_string_for_cache: typing.Optional[builtins.str] = None,
        ssl: typing.Optional[builtins.str] = None,
        true_client_ip_header: typing.Optional[builtins.str] = None,
        waf: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param always_use_https: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#always_use_https PageRule#always_use_https}.
        :param automatic_https_rewrites: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#automatic_https_rewrites PageRule#automatic_https_rewrites}.
        :param browser_cache_ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#browser_cache_ttl PageRule#browser_cache_ttl}.
        :param browser_check: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#browser_check PageRule#browser_check}.
        :param bypass_cache_on_cookie: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#bypass_cache_on_cookie PageRule#bypass_cache_on_cookie}.
        :param cache_by_device_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_by_device_type PageRule#cache_by_device_type}.
        :param cache_deception_armor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_deception_armor PageRule#cache_deception_armor}.
        :param cache_key_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_key_fields PageRule#cache_key_fields}.
        :param cache_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_level PageRule#cache_level}.
        :param cache_on_cookie: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_on_cookie PageRule#cache_on_cookie}.
        :param cache_ttl_by_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_ttl_by_status PageRule#cache_ttl_by_status}.
        :param disable_apps: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_apps PageRule#disable_apps}.
        :param disable_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_performance PageRule#disable_performance}.
        :param disable_security: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_security PageRule#disable_security}.
        :param disable_zaraz: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_zaraz PageRule#disable_zaraz}.
        :param edge_cache_ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#edge_cache_ttl PageRule#edge_cache_ttl}.
        :param email_obfuscation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#email_obfuscation PageRule#email_obfuscation}.
        :param explicit_cache_control: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#explicit_cache_control PageRule#explicit_cache_control}.
        :param forwarding_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#forwarding_url PageRule#forwarding_url}.
        :param host_header_override: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#host_header_override PageRule#host_header_override}.
        :param ip_geolocation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#ip_geolocation PageRule#ip_geolocation}.
        :param mirage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#mirage PageRule#mirage}.
        :param opportunistic_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#opportunistic_encryption PageRule#opportunistic_encryption}.
        :param origin_error_page_pass_thru: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#origin_error_page_pass_thru PageRule#origin_error_page_pass_thru}.
        :param polish: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#polish PageRule#polish}.
        :param resolve_override: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#resolve_override PageRule#resolve_override}.
        :param respect_strong_etag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#respect_strong_etag PageRule#respect_strong_etag}.
        :param response_buffering: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#response_buffering PageRule#response_buffering}.
        :param rocket_loader: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#rocket_loader PageRule#rocket_loader}.
        :param security_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#security_level PageRule#security_level}.
        :param sort_query_string_for_cache: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#sort_query_string_for_cache PageRule#sort_query_string_for_cache}.
        :param ssl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#ssl PageRule#ssl}.
        :param true_client_ip_header: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#true_client_ip_header PageRule#true_client_ip_header}.
        :param waf: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#waf PageRule#waf}.
        '''
        if isinstance(cache_key_fields, dict):
            cache_key_fields = PageRuleActionsCacheKeyFields(**cache_key_fields)
        if isinstance(forwarding_url, dict):
            forwarding_url = PageRuleActionsForwardingUrl(**forwarding_url)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf4ebb980142101ae1ac0d7a8c83b27fb567a416ac971a10f6a3e9b6a75197dc)
            check_type(argname="argument always_use_https", value=always_use_https, expected_type=type_hints["always_use_https"])
            check_type(argname="argument automatic_https_rewrites", value=automatic_https_rewrites, expected_type=type_hints["automatic_https_rewrites"])
            check_type(argname="argument browser_cache_ttl", value=browser_cache_ttl, expected_type=type_hints["browser_cache_ttl"])
            check_type(argname="argument browser_check", value=browser_check, expected_type=type_hints["browser_check"])
            check_type(argname="argument bypass_cache_on_cookie", value=bypass_cache_on_cookie, expected_type=type_hints["bypass_cache_on_cookie"])
            check_type(argname="argument cache_by_device_type", value=cache_by_device_type, expected_type=type_hints["cache_by_device_type"])
            check_type(argname="argument cache_deception_armor", value=cache_deception_armor, expected_type=type_hints["cache_deception_armor"])
            check_type(argname="argument cache_key_fields", value=cache_key_fields, expected_type=type_hints["cache_key_fields"])
            check_type(argname="argument cache_level", value=cache_level, expected_type=type_hints["cache_level"])
            check_type(argname="argument cache_on_cookie", value=cache_on_cookie, expected_type=type_hints["cache_on_cookie"])
            check_type(argname="argument cache_ttl_by_status", value=cache_ttl_by_status, expected_type=type_hints["cache_ttl_by_status"])
            check_type(argname="argument disable_apps", value=disable_apps, expected_type=type_hints["disable_apps"])
            check_type(argname="argument disable_performance", value=disable_performance, expected_type=type_hints["disable_performance"])
            check_type(argname="argument disable_security", value=disable_security, expected_type=type_hints["disable_security"])
            check_type(argname="argument disable_zaraz", value=disable_zaraz, expected_type=type_hints["disable_zaraz"])
            check_type(argname="argument edge_cache_ttl", value=edge_cache_ttl, expected_type=type_hints["edge_cache_ttl"])
            check_type(argname="argument email_obfuscation", value=email_obfuscation, expected_type=type_hints["email_obfuscation"])
            check_type(argname="argument explicit_cache_control", value=explicit_cache_control, expected_type=type_hints["explicit_cache_control"])
            check_type(argname="argument forwarding_url", value=forwarding_url, expected_type=type_hints["forwarding_url"])
            check_type(argname="argument host_header_override", value=host_header_override, expected_type=type_hints["host_header_override"])
            check_type(argname="argument ip_geolocation", value=ip_geolocation, expected_type=type_hints["ip_geolocation"])
            check_type(argname="argument mirage", value=mirage, expected_type=type_hints["mirage"])
            check_type(argname="argument opportunistic_encryption", value=opportunistic_encryption, expected_type=type_hints["opportunistic_encryption"])
            check_type(argname="argument origin_error_page_pass_thru", value=origin_error_page_pass_thru, expected_type=type_hints["origin_error_page_pass_thru"])
            check_type(argname="argument polish", value=polish, expected_type=type_hints["polish"])
            check_type(argname="argument resolve_override", value=resolve_override, expected_type=type_hints["resolve_override"])
            check_type(argname="argument respect_strong_etag", value=respect_strong_etag, expected_type=type_hints["respect_strong_etag"])
            check_type(argname="argument response_buffering", value=response_buffering, expected_type=type_hints["response_buffering"])
            check_type(argname="argument rocket_loader", value=rocket_loader, expected_type=type_hints["rocket_loader"])
            check_type(argname="argument security_level", value=security_level, expected_type=type_hints["security_level"])
            check_type(argname="argument sort_query_string_for_cache", value=sort_query_string_for_cache, expected_type=type_hints["sort_query_string_for_cache"])
            check_type(argname="argument ssl", value=ssl, expected_type=type_hints["ssl"])
            check_type(argname="argument true_client_ip_header", value=true_client_ip_header, expected_type=type_hints["true_client_ip_header"])
            check_type(argname="argument waf", value=waf, expected_type=type_hints["waf"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if always_use_https is not None:
            self._values["always_use_https"] = always_use_https
        if automatic_https_rewrites is not None:
            self._values["automatic_https_rewrites"] = automatic_https_rewrites
        if browser_cache_ttl is not None:
            self._values["browser_cache_ttl"] = browser_cache_ttl
        if browser_check is not None:
            self._values["browser_check"] = browser_check
        if bypass_cache_on_cookie is not None:
            self._values["bypass_cache_on_cookie"] = bypass_cache_on_cookie
        if cache_by_device_type is not None:
            self._values["cache_by_device_type"] = cache_by_device_type
        if cache_deception_armor is not None:
            self._values["cache_deception_armor"] = cache_deception_armor
        if cache_key_fields is not None:
            self._values["cache_key_fields"] = cache_key_fields
        if cache_level is not None:
            self._values["cache_level"] = cache_level
        if cache_on_cookie is not None:
            self._values["cache_on_cookie"] = cache_on_cookie
        if cache_ttl_by_status is not None:
            self._values["cache_ttl_by_status"] = cache_ttl_by_status
        if disable_apps is not None:
            self._values["disable_apps"] = disable_apps
        if disable_performance is not None:
            self._values["disable_performance"] = disable_performance
        if disable_security is not None:
            self._values["disable_security"] = disable_security
        if disable_zaraz is not None:
            self._values["disable_zaraz"] = disable_zaraz
        if edge_cache_ttl is not None:
            self._values["edge_cache_ttl"] = edge_cache_ttl
        if email_obfuscation is not None:
            self._values["email_obfuscation"] = email_obfuscation
        if explicit_cache_control is not None:
            self._values["explicit_cache_control"] = explicit_cache_control
        if forwarding_url is not None:
            self._values["forwarding_url"] = forwarding_url
        if host_header_override is not None:
            self._values["host_header_override"] = host_header_override
        if ip_geolocation is not None:
            self._values["ip_geolocation"] = ip_geolocation
        if mirage is not None:
            self._values["mirage"] = mirage
        if opportunistic_encryption is not None:
            self._values["opportunistic_encryption"] = opportunistic_encryption
        if origin_error_page_pass_thru is not None:
            self._values["origin_error_page_pass_thru"] = origin_error_page_pass_thru
        if polish is not None:
            self._values["polish"] = polish
        if resolve_override is not None:
            self._values["resolve_override"] = resolve_override
        if respect_strong_etag is not None:
            self._values["respect_strong_etag"] = respect_strong_etag
        if response_buffering is not None:
            self._values["response_buffering"] = response_buffering
        if rocket_loader is not None:
            self._values["rocket_loader"] = rocket_loader
        if security_level is not None:
            self._values["security_level"] = security_level
        if sort_query_string_for_cache is not None:
            self._values["sort_query_string_for_cache"] = sort_query_string_for_cache
        if ssl is not None:
            self._values["ssl"] = ssl
        if true_client_ip_header is not None:
            self._values["true_client_ip_header"] = true_client_ip_header
        if waf is not None:
            self._values["waf"] = waf

    @builtins.property
    def always_use_https(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#always_use_https PageRule#always_use_https}.'''
        result = self._values.get("always_use_https")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def automatic_https_rewrites(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#automatic_https_rewrites PageRule#automatic_https_rewrites}.'''
        result = self._values.get("automatic_https_rewrites")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def browser_cache_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#browser_cache_ttl PageRule#browser_cache_ttl}.'''
        result = self._values.get("browser_cache_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def browser_check(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#browser_check PageRule#browser_check}.'''
        result = self._values.get("browser_check")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bypass_cache_on_cookie(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#bypass_cache_on_cookie PageRule#bypass_cache_on_cookie}.'''
        result = self._values.get("bypass_cache_on_cookie")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_by_device_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_by_device_type PageRule#cache_by_device_type}.'''
        result = self._values.get("cache_by_device_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_deception_armor(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_deception_armor PageRule#cache_deception_armor}.'''
        result = self._values.get("cache_deception_armor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_key_fields(self) -> typing.Optional["PageRuleActionsCacheKeyFields"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_key_fields PageRule#cache_key_fields}.'''
        result = self._values.get("cache_key_fields")
        return typing.cast(typing.Optional["PageRuleActionsCacheKeyFields"], result)

    @builtins.property
    def cache_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_level PageRule#cache_level}.'''
        result = self._values.get("cache_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_on_cookie(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_on_cookie PageRule#cache_on_cookie}.'''
        result = self._values.get("cache_on_cookie")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_ttl_by_status(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cache_ttl_by_status PageRule#cache_ttl_by_status}.'''
        result = self._values.get("cache_ttl_by_status")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def disable_apps(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_apps PageRule#disable_apps}.'''
        result = self._values.get("disable_apps")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def disable_performance(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_performance PageRule#disable_performance}.'''
        result = self._values.get("disable_performance")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def disable_security(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_security PageRule#disable_security}.'''
        result = self._values.get("disable_security")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def disable_zaraz(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#disable_zaraz PageRule#disable_zaraz}.'''
        result = self._values.get("disable_zaraz")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def edge_cache_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#edge_cache_ttl PageRule#edge_cache_ttl}.'''
        result = self._values.get("edge_cache_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def email_obfuscation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#email_obfuscation PageRule#email_obfuscation}.'''
        result = self._values.get("email_obfuscation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def explicit_cache_control(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#explicit_cache_control PageRule#explicit_cache_control}.'''
        result = self._values.get("explicit_cache_control")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forwarding_url(self) -> typing.Optional["PageRuleActionsForwardingUrl"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#forwarding_url PageRule#forwarding_url}.'''
        result = self._values.get("forwarding_url")
        return typing.cast(typing.Optional["PageRuleActionsForwardingUrl"], result)

    @builtins.property
    def host_header_override(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#host_header_override PageRule#host_header_override}.'''
        result = self._values.get("host_header_override")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_geolocation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#ip_geolocation PageRule#ip_geolocation}.'''
        result = self._values.get("ip_geolocation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mirage(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#mirage PageRule#mirage}.'''
        result = self._values.get("mirage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def opportunistic_encryption(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#opportunistic_encryption PageRule#opportunistic_encryption}.'''
        result = self._values.get("opportunistic_encryption")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_error_page_pass_thru(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#origin_error_page_pass_thru PageRule#origin_error_page_pass_thru}.'''
        result = self._values.get("origin_error_page_pass_thru")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def polish(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#polish PageRule#polish}.'''
        result = self._values.get("polish")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resolve_override(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#resolve_override PageRule#resolve_override}.'''
        result = self._values.get("resolve_override")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def respect_strong_etag(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#respect_strong_etag PageRule#respect_strong_etag}.'''
        result = self._values.get("respect_strong_etag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_buffering(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#response_buffering PageRule#response_buffering}.'''
        result = self._values.get("response_buffering")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rocket_loader(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#rocket_loader PageRule#rocket_loader}.'''
        result = self._values.get("rocket_loader")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#security_level PageRule#security_level}.'''
        result = self._values.get("security_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sort_query_string_for_cache(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#sort_query_string_for_cache PageRule#sort_query_string_for_cache}.'''
        result = self._values.get("sort_query_string_for_cache")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#ssl PageRule#ssl}.'''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def true_client_ip_header(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#true_client_ip_header PageRule#true_client_ip_header}.'''
        result = self._values.get("true_client_ip_header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def waf(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#waf PageRule#waf}.'''
        result = self._values.get("waf")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageRuleActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFields",
    jsii_struct_bases=[],
    name_mapping={
        "cookie": "cookie",
        "header": "header",
        "host": "host",
        "query_string": "queryString",
        "user": "user",
    },
)
class PageRuleActionsCacheKeyFields:
    def __init__(
        self,
        *,
        cookie: typing.Optional[typing.Union["PageRuleActionsCacheKeyFieldsCookie", typing.Dict[builtins.str, typing.Any]]] = None,
        header: typing.Optional[typing.Union["PageRuleActionsCacheKeyFieldsHeader", typing.Dict[builtins.str, typing.Any]]] = None,
        host: typing.Optional[typing.Union["PageRuleActionsCacheKeyFieldsHost", typing.Dict[builtins.str, typing.Any]]] = None,
        query_string: typing.Optional[typing.Union["PageRuleActionsCacheKeyFieldsQueryString", typing.Dict[builtins.str, typing.Any]]] = None,
        user: typing.Optional[typing.Union["PageRuleActionsCacheKeyFieldsUser", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cookie: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cookie PageRule#cookie}.
        :param header: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#header PageRule#header}.
        :param host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#host PageRule#host}.
        :param query_string: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#query_string PageRule#query_string}.
        :param user: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#user PageRule#user}.
        '''
        if isinstance(cookie, dict):
            cookie = PageRuleActionsCacheKeyFieldsCookie(**cookie)
        if isinstance(header, dict):
            header = PageRuleActionsCacheKeyFieldsHeader(**header)
        if isinstance(host, dict):
            host = PageRuleActionsCacheKeyFieldsHost(**host)
        if isinstance(query_string, dict):
            query_string = PageRuleActionsCacheKeyFieldsQueryString(**query_string)
        if isinstance(user, dict):
            user = PageRuleActionsCacheKeyFieldsUser(**user)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e77ecaa90d7cf91d05a56c53c802f1f33cb188776c377a0f4b961a3ac4cca4f0)
            check_type(argname="argument cookie", value=cookie, expected_type=type_hints["cookie"])
            check_type(argname="argument header", value=header, expected_type=type_hints["header"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument query_string", value=query_string, expected_type=type_hints["query_string"])
            check_type(argname="argument user", value=user, expected_type=type_hints["user"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cookie is not None:
            self._values["cookie"] = cookie
        if header is not None:
            self._values["header"] = header
        if host is not None:
            self._values["host"] = host
        if query_string is not None:
            self._values["query_string"] = query_string
        if user is not None:
            self._values["user"] = user

    @builtins.property
    def cookie(self) -> typing.Optional["PageRuleActionsCacheKeyFieldsCookie"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cookie PageRule#cookie}.'''
        result = self._values.get("cookie")
        return typing.cast(typing.Optional["PageRuleActionsCacheKeyFieldsCookie"], result)

    @builtins.property
    def header(self) -> typing.Optional["PageRuleActionsCacheKeyFieldsHeader"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#header PageRule#header}.'''
        result = self._values.get("header")
        return typing.cast(typing.Optional["PageRuleActionsCacheKeyFieldsHeader"], result)

    @builtins.property
    def host(self) -> typing.Optional["PageRuleActionsCacheKeyFieldsHost"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#host PageRule#host}.'''
        result = self._values.get("host")
        return typing.cast(typing.Optional["PageRuleActionsCacheKeyFieldsHost"], result)

    @builtins.property
    def query_string(
        self,
    ) -> typing.Optional["PageRuleActionsCacheKeyFieldsQueryString"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#query_string PageRule#query_string}.'''
        result = self._values.get("query_string")
        return typing.cast(typing.Optional["PageRuleActionsCacheKeyFieldsQueryString"], result)

    @builtins.property
    def user(self) -> typing.Optional["PageRuleActionsCacheKeyFieldsUser"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#user PageRule#user}.'''
        result = self._values.get("user")
        return typing.cast(typing.Optional["PageRuleActionsCacheKeyFieldsUser"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageRuleActionsCacheKeyFields(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsCookie",
    jsii_struct_bases=[],
    name_mapping={"check_presence": "checkPresence", "include": "include"},
)
class PageRuleActionsCacheKeyFieldsCookie:
    def __init__(
        self,
        *,
        check_presence: typing.Optional[typing.Sequence[builtins.str]] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param check_presence: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#check_presence PageRule#check_presence}.
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#include PageRule#include}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69b925ed2f73a79d279954a9d6dc7815e94940803028915abd7a7da3b22d2045)
            check_type(argname="argument check_presence", value=check_presence, expected_type=type_hints["check_presence"])
            check_type(argname="argument include", value=include, expected_type=type_hints["include"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if check_presence is not None:
            self._values["check_presence"] = check_presence
        if include is not None:
            self._values["include"] = include

    @builtins.property
    def check_presence(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#check_presence PageRule#check_presence}.'''
        result = self._values.get("check_presence")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#include PageRule#include}.'''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageRuleActionsCacheKeyFieldsCookie(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PageRuleActionsCacheKeyFieldsCookieOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsCookieOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5de40c342556b0de77dbb043a296fc1aac66adbf2652f767aa3ae230fc57da34)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCheckPresence")
    def reset_check_presence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckPresence", []))

    @jsii.member(jsii_name="resetInclude")
    def reset_include(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInclude", []))

    @builtins.property
    @jsii.member(jsii_name="checkPresenceInput")
    def check_presence_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "checkPresenceInput"))

    @builtins.property
    @jsii.member(jsii_name="includeInput")
    def include_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeInput"))

    @builtins.property
    @jsii.member(jsii_name="checkPresence")
    def check_presence(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "checkPresence"))

    @check_presence.setter
    def check_presence(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ae34aafd2bcc8e40e8ee525f0b5c598ee095a668b92b12e69278b84f5b6730e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checkPresence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d11df9afc298b273b7995665a8faf624bc60b7379e7ac5c774ed1cb4f1341b38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsCookie]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsCookie]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsCookie]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98009a8b817ba4e31040ff1018f5c9d71387bc29f9d9afdcaf7b5c751e864dd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsHeader",
    jsii_struct_bases=[],
    name_mapping={
        "check_presence": "checkPresence",
        "exclude": "exclude",
        "include": "include",
    },
)
class PageRuleActionsCacheKeyFieldsHeader:
    def __init__(
        self,
        *,
        check_presence: typing.Optional[typing.Sequence[builtins.str]] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param check_presence: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#check_presence PageRule#check_presence}.
        :param exclude: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#exclude PageRule#exclude}.
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#include PageRule#include}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa871e3b27cc7b93abd244efe24bae80be7c6d769adf131620998dc7049daed3)
            check_type(argname="argument check_presence", value=check_presence, expected_type=type_hints["check_presence"])
            check_type(argname="argument exclude", value=exclude, expected_type=type_hints["exclude"])
            check_type(argname="argument include", value=include, expected_type=type_hints["include"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if check_presence is not None:
            self._values["check_presence"] = check_presence
        if exclude is not None:
            self._values["exclude"] = exclude
        if include is not None:
            self._values["include"] = include

    @builtins.property
    def check_presence(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#check_presence PageRule#check_presence}.'''
        result = self._values.get("check_presence")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#exclude PageRule#exclude}.'''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#include PageRule#include}.'''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageRuleActionsCacheKeyFieldsHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PageRuleActionsCacheKeyFieldsHeaderOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsHeaderOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f519b073aaa02997052f28351119ee0073df500f5d6fd6687828459d367d568c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCheckPresence")
    def reset_check_presence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckPresence", []))

    @jsii.member(jsii_name="resetExclude")
    def reset_exclude(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExclude", []))

    @jsii.member(jsii_name="resetInclude")
    def reset_include(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInclude", []))

    @builtins.property
    @jsii.member(jsii_name="checkPresenceInput")
    def check_presence_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "checkPresenceInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeInput")
    def exclude_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeInput"))

    @builtins.property
    @jsii.member(jsii_name="includeInput")
    def include_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeInput"))

    @builtins.property
    @jsii.member(jsii_name="checkPresence")
    def check_presence(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "checkPresence"))

    @check_presence.setter
    def check_presence(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8270f65aa831186d8efe7eff4c5650deae0a6ec5a42c78efaae44187f1d48172)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checkPresence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exclude"))

    @exclude.setter
    def exclude(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f286f84e95156b0cf53498798a02986397c3e7d23d8848c6c37460c488e0eb8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bd6e3e3ebb840a9f12d9677f232af1b44670539efe7eed0aa7244a632cfc743)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHeader]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHeader]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHeader]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7f18a69debbec8530d11f49dba273db2d380ec8e63dc2388780f49c652b901b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsHost",
    jsii_struct_bases=[],
    name_mapping={"resolved": "resolved"},
)
class PageRuleActionsCacheKeyFieldsHost:
    def __init__(
        self,
        *,
        resolved: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param resolved: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#resolved PageRule#resolved}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8da67a019aae9cdd3cad78632d11626f52cb742bc98bd8c2b857ba356ccd74e7)
            check_type(argname="argument resolved", value=resolved, expected_type=type_hints["resolved"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if resolved is not None:
            self._values["resolved"] = resolved

    @builtins.property
    def resolved(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#resolved PageRule#resolved}.'''
        result = self._values.get("resolved")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageRuleActionsCacheKeyFieldsHost(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PageRuleActionsCacheKeyFieldsHostOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsHostOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3b7835f7da100efd954cd9bbe34160ff872c2ed6010827a288f6d98f4e0841e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetResolved")
    def reset_resolved(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResolved", []))

    @builtins.property
    @jsii.member(jsii_name="resolvedInput")
    def resolved_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "resolvedInput"))

    @builtins.property
    @jsii.member(jsii_name="resolved")
    def resolved(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "resolved"))

    @resolved.setter
    def resolved(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a31e43e3cb9964345bf25caf1eea420ecf2f0b068779f0b30d0e18e8cee3140)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resolved", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHost]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHost]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHost]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5ffedf1b31b99bedda959fa4cd9f3ebd9f0cd3f47653990e3923efe4a4c3b2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PageRuleActionsCacheKeyFieldsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39ddfd907b1dccb5b231e96e19240c83f4868493c3491af56417f7352d7c5703)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCookie")
    def put_cookie(
        self,
        *,
        check_presence: typing.Optional[typing.Sequence[builtins.str]] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param check_presence: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#check_presence PageRule#check_presence}.
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#include PageRule#include}.
        '''
        value = PageRuleActionsCacheKeyFieldsCookie(
            check_presence=check_presence, include=include
        )

        return typing.cast(None, jsii.invoke(self, "putCookie", [value]))

    @jsii.member(jsii_name="putHeader")
    def put_header(
        self,
        *,
        check_presence: typing.Optional[typing.Sequence[builtins.str]] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param check_presence: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#check_presence PageRule#check_presence}.
        :param exclude: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#exclude PageRule#exclude}.
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#include PageRule#include}.
        '''
        value = PageRuleActionsCacheKeyFieldsHeader(
            check_presence=check_presence, exclude=exclude, include=include
        )

        return typing.cast(None, jsii.invoke(self, "putHeader", [value]))

    @jsii.member(jsii_name="putHost")
    def put_host(
        self,
        *,
        resolved: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param resolved: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#resolved PageRule#resolved}.
        '''
        value = PageRuleActionsCacheKeyFieldsHost(resolved=resolved)

        return typing.cast(None, jsii.invoke(self, "putHost", [value]))

    @jsii.member(jsii_name="putQueryString")
    def put_query_string(
        self,
        *,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#exclude PageRule#exclude}.
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#include PageRule#include}.
        '''
        value = PageRuleActionsCacheKeyFieldsQueryString(
            exclude=exclude, include=include
        )

        return typing.cast(None, jsii.invoke(self, "putQueryString", [value]))

    @jsii.member(jsii_name="putUser")
    def put_user(
        self,
        *,
        device_type: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        geo: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        lang: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param device_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#device_type PageRule#device_type}.
        :param geo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#geo PageRule#geo}.
        :param lang: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#lang PageRule#lang}.
        '''
        value = PageRuleActionsCacheKeyFieldsUser(
            device_type=device_type, geo=geo, lang=lang
        )

        return typing.cast(None, jsii.invoke(self, "putUser", [value]))

    @jsii.member(jsii_name="resetCookie")
    def reset_cookie(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCookie", []))

    @jsii.member(jsii_name="resetHeader")
    def reset_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeader", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetQueryString")
    def reset_query_string(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryString", []))

    @jsii.member(jsii_name="resetUser")
    def reset_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUser", []))

    @builtins.property
    @jsii.member(jsii_name="cookie")
    def cookie(self) -> PageRuleActionsCacheKeyFieldsCookieOutputReference:
        return typing.cast(PageRuleActionsCacheKeyFieldsCookieOutputReference, jsii.get(self, "cookie"))

    @builtins.property
    @jsii.member(jsii_name="header")
    def header(self) -> PageRuleActionsCacheKeyFieldsHeaderOutputReference:
        return typing.cast(PageRuleActionsCacheKeyFieldsHeaderOutputReference, jsii.get(self, "header"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> PageRuleActionsCacheKeyFieldsHostOutputReference:
        return typing.cast(PageRuleActionsCacheKeyFieldsHostOutputReference, jsii.get(self, "host"))

    @builtins.property
    @jsii.member(jsii_name="queryString")
    def query_string(self) -> "PageRuleActionsCacheKeyFieldsQueryStringOutputReference":
        return typing.cast("PageRuleActionsCacheKeyFieldsQueryStringOutputReference", jsii.get(self, "queryString"))

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> "PageRuleActionsCacheKeyFieldsUserOutputReference":
        return typing.cast("PageRuleActionsCacheKeyFieldsUserOutputReference", jsii.get(self, "user"))

    @builtins.property
    @jsii.member(jsii_name="cookieInput")
    def cookie_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsCookie]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsCookie]], jsii.get(self, "cookieInput"))

    @builtins.property
    @jsii.member(jsii_name="headerInput")
    def header_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHeader]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHeader]], jsii.get(self, "headerInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHost]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHost]], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="queryStringInput")
    def query_string_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PageRuleActionsCacheKeyFieldsQueryString"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PageRuleActionsCacheKeyFieldsQueryString"]], jsii.get(self, "queryStringInput"))

    @builtins.property
    @jsii.member(jsii_name="userInput")
    def user_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PageRuleActionsCacheKeyFieldsUser"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PageRuleActionsCacheKeyFieldsUser"]], jsii.get(self, "userInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFields]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFields]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFields]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2aeb52ba3dc622bb0efe2c743f7bb027f9c741c20f0ff231e7b8cc7ef79c716)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsQueryString",
    jsii_struct_bases=[],
    name_mapping={"exclude": "exclude", "include": "include"},
)
class PageRuleActionsCacheKeyFieldsQueryString:
    def __init__(
        self,
        *,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#exclude PageRule#exclude}.
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#include PageRule#include}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d3892605efe4261a3a8158137fcdd61b75e3b02ea948c88c099e67a6a79b7ad)
            check_type(argname="argument exclude", value=exclude, expected_type=type_hints["exclude"])
            check_type(argname="argument include", value=include, expected_type=type_hints["include"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude is not None:
            self._values["exclude"] = exclude
        if include is not None:
            self._values["include"] = include

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#exclude PageRule#exclude}.'''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#include PageRule#include}.'''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageRuleActionsCacheKeyFieldsQueryString(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PageRuleActionsCacheKeyFieldsQueryStringOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsQueryStringOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__19a006cd5b9d97bdc416d777fd5bdfd61c53c1458ff554e8710dad183df85482)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExclude")
    def reset_exclude(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExclude", []))

    @jsii.member(jsii_name="resetInclude")
    def reset_include(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInclude", []))

    @builtins.property
    @jsii.member(jsii_name="excludeInput")
    def exclude_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeInput"))

    @builtins.property
    @jsii.member(jsii_name="includeInput")
    def include_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeInput"))

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exclude"))

    @exclude.setter
    def exclude(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8be8e5cc44508e7a10a584f9f538034f991603863465cc90d46f53daebf6c541)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__338c89594ec8121e1a6ba1703d55035be7c0fe9fb9c00889e79aedf0c938eb0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsQueryString]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsQueryString]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsQueryString]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a16b93bd314b7e238cc25ba82bf31994b00608fa09b7b45a66bce2a174d4aa4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsUser",
    jsii_struct_bases=[],
    name_mapping={"device_type": "deviceType", "geo": "geo", "lang": "lang"},
)
class PageRuleActionsCacheKeyFieldsUser:
    def __init__(
        self,
        *,
        device_type: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        geo: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        lang: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param device_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#device_type PageRule#device_type}.
        :param geo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#geo PageRule#geo}.
        :param lang: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#lang PageRule#lang}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1185938b5c4f7f4f9285fd7af7bf0dbb6a589490350d3e3820ca4b10bc7d15df)
            check_type(argname="argument device_type", value=device_type, expected_type=type_hints["device_type"])
            check_type(argname="argument geo", value=geo, expected_type=type_hints["geo"])
            check_type(argname="argument lang", value=lang, expected_type=type_hints["lang"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if device_type is not None:
            self._values["device_type"] = device_type
        if geo is not None:
            self._values["geo"] = geo
        if lang is not None:
            self._values["lang"] = lang

    @builtins.property
    def device_type(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#device_type PageRule#device_type}.'''
        result = self._values.get("device_type")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def geo(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#geo PageRule#geo}.'''
        result = self._values.get("geo")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def lang(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#lang PageRule#lang}.'''
        result = self._values.get("lang")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageRuleActionsCacheKeyFieldsUser(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PageRuleActionsCacheKeyFieldsUserOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsCacheKeyFieldsUserOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__927837ae2acac3ae0a0dbec6ce412b91949d6d1f2aecae87f75485b4b966e704)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDeviceType")
    def reset_device_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceType", []))

    @jsii.member(jsii_name="resetGeo")
    def reset_geo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGeo", []))

    @jsii.member(jsii_name="resetLang")
    def reset_lang(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLang", []))

    @builtins.property
    @jsii.member(jsii_name="deviceTypeInput")
    def device_type_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deviceTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="geoInput")
    def geo_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "geoInput"))

    @builtins.property
    @jsii.member(jsii_name="langInput")
    def lang_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "langInput"))

    @builtins.property
    @jsii.member(jsii_name="deviceType")
    def device_type(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deviceType"))

    @device_type.setter
    def device_type(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4089762c09af996c952fa8e3cb89a1ca411afe0236fa279683afb9830c7d70ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deviceType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "geo"))

    @geo.setter
    def geo(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d81f3c65572bcd63826dd4b330de3f7d07f5f0312703ebe65f4a2097a31e1f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "geo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lang")
    def lang(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "lang"))

    @lang.setter
    def lang(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b7c6b6162ce9bded3d292b6cebe26a3d8997d789f34d9d725babe63dba00e71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lang", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsUser]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsUser]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsUser]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72eaab090760a082f59f5ff3d57d08a70228ddec3574d008fc15e68fb3fce31e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsForwardingUrl",
    jsii_struct_bases=[],
    name_mapping={"status_code": "statusCode", "url": "url"},
)
class PageRuleActionsForwardingUrl:
    def __init__(self, *, status_code: jsii.Number, url: builtins.str) -> None:
        '''
        :param status_code: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#status_code PageRule#status_code}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#url PageRule#url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9e99c1ff8f3cb4b3f06788808b96b4ea89eb8f89233903750cb4d8abf04d3e0)
            check_type(argname="argument status_code", value=status_code, expected_type=type_hints["status_code"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status_code": status_code,
            "url": url,
        }

    @builtins.property
    def status_code(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#status_code PageRule#status_code}.'''
        result = self._values.get("status_code")
        assert result is not None, "Required property 'status_code' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#url PageRule#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageRuleActionsForwardingUrl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PageRuleActionsForwardingUrlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsForwardingUrlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__48980f4c7f151c0f1a4ffb3faf3fd07a25f7d5fb5fd2fa7499f2112afab5a5e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="statusCodeInput")
    def status_code_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "statusCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe0dad18b903852b1d426fb003d04ca5fec93bdf1a44b6f6c62fd4430a1643cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statusCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be674708d7801433a2a4bbb8720b9827dc53f5b93325c1c1b52d478835a2e0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsForwardingUrl]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsForwardingUrl]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsForwardingUrl]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b874ee01474f325ad80ee20c9b32de747a2dd9f3b47c573a9dfa26ee79bcc02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PageRuleActionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleActionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d19600dc22c94fd29ed9d377c5efa561ca62915318b70dafe97e39ac56dc142c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCacheKeyFields")
    def put_cache_key_fields(
        self,
        *,
        cookie: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsCookie, typing.Dict[builtins.str, typing.Any]]] = None,
        header: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsHeader, typing.Dict[builtins.str, typing.Any]]] = None,
        host: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsHost, typing.Dict[builtins.str, typing.Any]]] = None,
        query_string: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsQueryString, typing.Dict[builtins.str, typing.Any]]] = None,
        user: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsUser, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cookie: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#cookie PageRule#cookie}.
        :param header: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#header PageRule#header}.
        :param host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#host PageRule#host}.
        :param query_string: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#query_string PageRule#query_string}.
        :param user: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#user PageRule#user}.
        '''
        value = PageRuleActionsCacheKeyFields(
            cookie=cookie,
            header=header,
            host=host,
            query_string=query_string,
            user=user,
        )

        return typing.cast(None, jsii.invoke(self, "putCacheKeyFields", [value]))

    @jsii.member(jsii_name="putForwardingUrl")
    def put_forwarding_url(
        self,
        *,
        status_code: jsii.Number,
        url: builtins.str,
    ) -> None:
        '''
        :param status_code: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#status_code PageRule#status_code}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#url PageRule#url}.
        '''
        value = PageRuleActionsForwardingUrl(status_code=status_code, url=url)

        return typing.cast(None, jsii.invoke(self, "putForwardingUrl", [value]))

    @jsii.member(jsii_name="resetAlwaysUseHttps")
    def reset_always_use_https(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlwaysUseHttps", []))

    @jsii.member(jsii_name="resetAutomaticHttpsRewrites")
    def reset_automatic_https_rewrites(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticHttpsRewrites", []))

    @jsii.member(jsii_name="resetBrowserCacheTtl")
    def reset_browser_cache_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBrowserCacheTtl", []))

    @jsii.member(jsii_name="resetBrowserCheck")
    def reset_browser_check(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBrowserCheck", []))

    @jsii.member(jsii_name="resetBypassCacheOnCookie")
    def reset_bypass_cache_on_cookie(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBypassCacheOnCookie", []))

    @jsii.member(jsii_name="resetCacheByDeviceType")
    def reset_cache_by_device_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheByDeviceType", []))

    @jsii.member(jsii_name="resetCacheDeceptionArmor")
    def reset_cache_deception_armor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheDeceptionArmor", []))

    @jsii.member(jsii_name="resetCacheKeyFields")
    def reset_cache_key_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheKeyFields", []))

    @jsii.member(jsii_name="resetCacheLevel")
    def reset_cache_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheLevel", []))

    @jsii.member(jsii_name="resetCacheOnCookie")
    def reset_cache_on_cookie(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheOnCookie", []))

    @jsii.member(jsii_name="resetCacheTtlByStatus")
    def reset_cache_ttl_by_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheTtlByStatus", []))

    @jsii.member(jsii_name="resetDisableApps")
    def reset_disable_apps(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableApps", []))

    @jsii.member(jsii_name="resetDisablePerformance")
    def reset_disable_performance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisablePerformance", []))

    @jsii.member(jsii_name="resetDisableSecurity")
    def reset_disable_security(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableSecurity", []))

    @jsii.member(jsii_name="resetDisableZaraz")
    def reset_disable_zaraz(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableZaraz", []))

    @jsii.member(jsii_name="resetEdgeCacheTtl")
    def reset_edge_cache_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEdgeCacheTtl", []))

    @jsii.member(jsii_name="resetEmailObfuscation")
    def reset_email_obfuscation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailObfuscation", []))

    @jsii.member(jsii_name="resetExplicitCacheControl")
    def reset_explicit_cache_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExplicitCacheControl", []))

    @jsii.member(jsii_name="resetForwardingUrl")
    def reset_forwarding_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForwardingUrl", []))

    @jsii.member(jsii_name="resetHostHeaderOverride")
    def reset_host_header_override(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostHeaderOverride", []))

    @jsii.member(jsii_name="resetIpGeolocation")
    def reset_ip_geolocation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpGeolocation", []))

    @jsii.member(jsii_name="resetMirage")
    def reset_mirage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMirage", []))

    @jsii.member(jsii_name="resetOpportunisticEncryption")
    def reset_opportunistic_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpportunisticEncryption", []))

    @jsii.member(jsii_name="resetOriginErrorPagePassThru")
    def reset_origin_error_page_pass_thru(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginErrorPagePassThru", []))

    @jsii.member(jsii_name="resetPolish")
    def reset_polish(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolish", []))

    @jsii.member(jsii_name="resetResolveOverride")
    def reset_resolve_override(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResolveOverride", []))

    @jsii.member(jsii_name="resetRespectStrongEtag")
    def reset_respect_strong_etag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespectStrongEtag", []))

    @jsii.member(jsii_name="resetResponseBuffering")
    def reset_response_buffering(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseBuffering", []))

    @jsii.member(jsii_name="resetRocketLoader")
    def reset_rocket_loader(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRocketLoader", []))

    @jsii.member(jsii_name="resetSecurityLevel")
    def reset_security_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityLevel", []))

    @jsii.member(jsii_name="resetSortQueryStringForCache")
    def reset_sort_query_string_for_cache(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSortQueryStringForCache", []))

    @jsii.member(jsii_name="resetSsl")
    def reset_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsl", []))

    @jsii.member(jsii_name="resetTrueClientIpHeader")
    def reset_true_client_ip_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrueClientIpHeader", []))

    @jsii.member(jsii_name="resetWaf")
    def reset_waf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaf", []))

    @builtins.property
    @jsii.member(jsii_name="cacheKeyFields")
    def cache_key_fields(self) -> PageRuleActionsCacheKeyFieldsOutputReference:
        return typing.cast(PageRuleActionsCacheKeyFieldsOutputReference, jsii.get(self, "cacheKeyFields"))

    @builtins.property
    @jsii.member(jsii_name="forwardingUrl")
    def forwarding_url(self) -> PageRuleActionsForwardingUrlOutputReference:
        return typing.cast(PageRuleActionsForwardingUrlOutputReference, jsii.get(self, "forwardingUrl"))

    @builtins.property
    @jsii.member(jsii_name="alwaysUseHttpsInput")
    def always_use_https_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "alwaysUseHttpsInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticHttpsRewritesInput")
    def automatic_https_rewrites_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "automaticHttpsRewritesInput"))

    @builtins.property
    @jsii.member(jsii_name="browserCacheTtlInput")
    def browser_cache_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "browserCacheTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="browserCheckInput")
    def browser_check_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "browserCheckInput"))

    @builtins.property
    @jsii.member(jsii_name="bypassCacheOnCookieInput")
    def bypass_cache_on_cookie_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bypassCacheOnCookieInput"))

    @builtins.property
    @jsii.member(jsii_name="cacheByDeviceTypeInput")
    def cache_by_device_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheByDeviceTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cacheDeceptionArmorInput")
    def cache_deception_armor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheDeceptionArmorInput"))

    @builtins.property
    @jsii.member(jsii_name="cacheKeyFieldsInput")
    def cache_key_fields_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFields]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFields]], jsii.get(self, "cacheKeyFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="cacheLevelInput")
    def cache_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="cacheOnCookieInput")
    def cache_on_cookie_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheOnCookieInput"))

    @builtins.property
    @jsii.member(jsii_name="cacheTtlByStatusInput")
    def cache_ttl_by_status_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "cacheTtlByStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="disableAppsInput")
    def disable_apps_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableAppsInput"))

    @builtins.property
    @jsii.member(jsii_name="disablePerformanceInput")
    def disable_performance_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disablePerformanceInput"))

    @builtins.property
    @jsii.member(jsii_name="disableSecurityInput")
    def disable_security_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableSecurityInput"))

    @builtins.property
    @jsii.member(jsii_name="disableZarazInput")
    def disable_zaraz_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableZarazInput"))

    @builtins.property
    @jsii.member(jsii_name="edgeCacheTtlInput")
    def edge_cache_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "edgeCacheTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="emailObfuscationInput")
    def email_obfuscation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailObfuscationInput"))

    @builtins.property
    @jsii.member(jsii_name="explicitCacheControlInput")
    def explicit_cache_control_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "explicitCacheControlInput"))

    @builtins.property
    @jsii.member(jsii_name="forwardingUrlInput")
    def forwarding_url_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsForwardingUrl]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsForwardingUrl]], jsii.get(self, "forwardingUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="hostHeaderOverrideInput")
    def host_header_override_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostHeaderOverrideInput"))

    @builtins.property
    @jsii.member(jsii_name="ipGeolocationInput")
    def ip_geolocation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipGeolocationInput"))

    @builtins.property
    @jsii.member(jsii_name="mirageInput")
    def mirage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mirageInput"))

    @builtins.property
    @jsii.member(jsii_name="opportunisticEncryptionInput")
    def opportunistic_encryption_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "opportunisticEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="originErrorPagePassThruInput")
    def origin_error_page_pass_thru_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "originErrorPagePassThruInput"))

    @builtins.property
    @jsii.member(jsii_name="polishInput")
    def polish_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "polishInput"))

    @builtins.property
    @jsii.member(jsii_name="resolveOverrideInput")
    def resolve_override_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resolveOverrideInput"))

    @builtins.property
    @jsii.member(jsii_name="respectStrongEtagInput")
    def respect_strong_etag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "respectStrongEtagInput"))

    @builtins.property
    @jsii.member(jsii_name="responseBufferingInput")
    def response_buffering_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseBufferingInput"))

    @builtins.property
    @jsii.member(jsii_name="rocketLoaderInput")
    def rocket_loader_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rocketLoaderInput"))

    @builtins.property
    @jsii.member(jsii_name="securityLevelInput")
    def security_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="sortQueryStringForCacheInput")
    def sort_query_string_for_cache_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sortQueryStringForCacheInput"))

    @builtins.property
    @jsii.member(jsii_name="sslInput")
    def ssl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslInput"))

    @builtins.property
    @jsii.member(jsii_name="trueClientIpHeaderInput")
    def true_client_ip_header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trueClientIpHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="wafInput")
    def waf_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wafInput"))

    @builtins.property
    @jsii.member(jsii_name="alwaysUseHttps")
    def always_use_https(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "alwaysUseHttps"))

    @always_use_https.setter
    def always_use_https(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60908d0ab548b0732c4b80fc71a6c74de53c70169bace4fe411dc209341eb331)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysUseHttps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="automaticHttpsRewrites")
    def automatic_https_rewrites(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "automaticHttpsRewrites"))

    @automatic_https_rewrites.setter
    def automatic_https_rewrites(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40e1cea0bfa90561698ad92bf2906ccef346b0ded4420d5a3967d2e21feb57bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automaticHttpsRewrites", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="browserCacheTtl")
    def browser_cache_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "browserCacheTtl"))

    @browser_cache_ttl.setter
    def browser_cache_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__845a01ed128525409c548d272c4261591ecf918e01ba4f4e65caf2dbe74e4d2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "browserCacheTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="browserCheck")
    def browser_check(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "browserCheck"))

    @browser_check.setter
    def browser_check(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1996a65c306e72a1e0be7f0f89271ca64710a17624a6b22307c5215b7375019b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "browserCheck", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bypassCacheOnCookie")
    def bypass_cache_on_cookie(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bypassCacheOnCookie"))

    @bypass_cache_on_cookie.setter
    def bypass_cache_on_cookie(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa53e0df29183732e1629516acd8e446a047616d009667623e4dca77e8cc9766)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bypassCacheOnCookie", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cacheByDeviceType")
    def cache_by_device_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheByDeviceType"))

    @cache_by_device_type.setter
    def cache_by_device_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e51f1d7b72cac73879aa1f0ebb57f1c98940bb69b3c5eee200309d7591d3c8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cacheByDeviceType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cacheDeceptionArmor")
    def cache_deception_armor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheDeceptionArmor"))

    @cache_deception_armor.setter
    def cache_deception_armor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82272024ac6529b6842a7c3910f447603511077e0cce7411ade507b20e1fe9eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cacheDeceptionArmor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cacheLevel")
    def cache_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheLevel"))

    @cache_level.setter
    def cache_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06a630ad6bd8f7916e8e151513d9d48785c86a65567b87ccfd675421017f7d41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cacheLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cacheOnCookie")
    def cache_on_cookie(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheOnCookie"))

    @cache_on_cookie.setter
    def cache_on_cookie(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c5089e29fbb13d0259361b2cdb46dc84dea4bfe744277b05f8d34280fc63889)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cacheOnCookie", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cacheTtlByStatus")
    def cache_ttl_by_status(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "cacheTtlByStatus"))

    @cache_ttl_by_status.setter
    def cache_ttl_by_status(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6a09031b84489b841beec9d11c0a853f3d44cc838308924ccd83af4634f1649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cacheTtlByStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableApps")
    def disable_apps(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableApps"))

    @disable_apps.setter
    def disable_apps(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6972573d717a4dcdc0a41d0ea769e9f880675d2fc46a00703d064b2a01f6f69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableApps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disablePerformance")
    def disable_performance(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disablePerformance"))

    @disable_performance.setter
    def disable_performance(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aecfe815b36717daffade85b69862a3786cfb2d23708d24e97e9866c255b83a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disablePerformance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableSecurity")
    def disable_security(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableSecurity"))

    @disable_security.setter
    def disable_security(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e66798335e7e046e5b36d7b93495f1b4554d9173c48c4d9454418df8483692ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableSecurity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableZaraz")
    def disable_zaraz(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableZaraz"))

    @disable_zaraz.setter
    def disable_zaraz(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2276f49a16792e01a16594a68dd4867c08b06de4ce7877417c603e9eeeee80c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableZaraz", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="edgeCacheTtl")
    def edge_cache_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "edgeCacheTtl"))

    @edge_cache_ttl.setter
    def edge_cache_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0de92e81a5dbdbc421236bf8b4c7521e9f9c5e2a453db76d699968d85e090d98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "edgeCacheTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailObfuscation")
    def email_obfuscation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailObfuscation"))

    @email_obfuscation.setter
    def email_obfuscation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceed7f4358cc9af9859c48b993f644cdc0e8e21d5bfa87e088a320daa3afadb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailObfuscation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="explicitCacheControl")
    def explicit_cache_control(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "explicitCacheControl"))

    @explicit_cache_control.setter
    def explicit_cache_control(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7412a3b457c8bf7bdc7a558c8af8e4440195ffbc942aea24a7800829f9e7a14d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "explicitCacheControl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostHeaderOverride")
    def host_header_override(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostHeaderOverride"))

    @host_header_override.setter
    def host_header_override(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8b40e021b4efb6a17d00090ba3303ca7fb180278f56a2ff21a14ff176abdf59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostHeaderOverride", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipGeolocation")
    def ip_geolocation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipGeolocation"))

    @ip_geolocation.setter
    def ip_geolocation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdde553f4d0bbda06a5991798a1f783218bc3899ba92d1bd077faee2b6ecb0e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipGeolocation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mirage")
    def mirage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mirage"))

    @mirage.setter
    def mirage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e58984630b094e94e096d2cffc4c0689a718e4cb98ed1d614c82d26195572802)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mirage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="opportunisticEncryption")
    def opportunistic_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "opportunisticEncryption"))

    @opportunistic_encryption.setter
    def opportunistic_encryption(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6e19b59361cae031a934932f90ef691d38fbd4cebbbdaaa8752f3875c1bf2af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "opportunisticEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="originErrorPagePassThru")
    def origin_error_page_pass_thru(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originErrorPagePassThru"))

    @origin_error_page_pass_thru.setter
    def origin_error_page_pass_thru(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a65ec0cce373ffd1905cb6a1eee7a67db4ba47b70948628c182084373ad6742b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "originErrorPagePassThru", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="polish")
    def polish(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "polish"))

    @polish.setter
    def polish(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e62defac004ddf3b2040f5d0d9d2551c279db604d5ae9d2422edf8d9422632f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "polish", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resolveOverride")
    def resolve_override(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resolveOverride"))

    @resolve_override.setter
    def resolve_override(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf70d126eec4394a54e833a16d4545f7dc69dfdca96adb95f4783a9644abda4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resolveOverride", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="respectStrongEtag")
    def respect_strong_etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "respectStrongEtag"))

    @respect_strong_etag.setter
    def respect_strong_etag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28710606d936986b5fbe894995daec055d237f6d173161f82b129865d065e4cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectStrongEtag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="responseBuffering")
    def response_buffering(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseBuffering"))

    @response_buffering.setter
    def response_buffering(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f2bad0de3b2cdf5c73fc29a18bf1fe0cfdca8063a56b7cf619d84eacb98fb8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseBuffering", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rocketLoader")
    def rocket_loader(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rocketLoader"))

    @rocket_loader.setter
    def rocket_loader(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0014d56c32525dbd8e13eb3826d014ae387cf0efc43711b6250fb0b0f936e91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rocketLoader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityLevel")
    def security_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityLevel"))

    @security_level.setter
    def security_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9093ef519ff2814142f6da569904cd7efc7b557835fa3853e48965d3eb74c24e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sortQueryStringForCache")
    def sort_query_string_for_cache(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sortQueryStringForCache"))

    @sort_query_string_for_cache.setter
    def sort_query_string_for_cache(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__315136d4eb2025708647b95379e01dde04f839750cb68acf04ccfd3de5cf4e08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sortQueryStringForCache", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ssl")
    def ssl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ssl"))

    @ssl.setter
    def ssl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ac756b45e6bb420f9d904a6d5da9ae193c117721f4d82ea498f8f25a5f512f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trueClientIpHeader")
    def true_client_ip_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trueClientIpHeader"))

    @true_client_ip_header.setter
    def true_client_ip_header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ff2478b4ff86f4cd2b8b680e017057046fe1d85456bc0d257eede443cf4d7b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trueClientIpHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="waf")
    def waf(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "waf"))

    @waf.setter
    def waf(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ce41ec709ecb9ae4c0ef776cccb96b7763e0825fc00c0798f6362d1be347995)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waf", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cc4b49f3983e2ff4fe75585819bf2a7c9c94718af8a77eef7dfb9870e445790)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pageRule.PageRuleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "actions": "actions",
        "target": "target",
        "zone_id": "zoneId",
        "priority": "priority",
        "status": "status",
    },
)
class PageRuleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        actions: typing.Union[PageRuleActions, typing.Dict[builtins.str, typing.Any]],
        target: builtins.str,
        zone_id: builtins.str,
        priority: typing.Optional[jsii.Number] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param actions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#actions PageRule#actions}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#target PageRule#target}.
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#zone_id PageRule#zone_id}
        :param priority: The priority of the rule, used to define which Page Rule is processed over another. A higher number indicates a higher priority. For example, if you have a catch-all Page Rule (rule A: ``/images/*``) but want a more specific Page Rule to take precedence (rule B: ``/images/special/*``), specify a higher priority for rule B so it overrides rule A. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#priority PageRule#priority}
        :param status: The status of the Page Rule. Available values: "active", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#status PageRule#status}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(actions, dict):
            actions = PageRuleActions(**actions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b728f4e60aefa01f724a31b2719dbe00ed190b52a24b1c2a32ecdf267f8b2d7)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "actions": actions,
            "target": target,
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
        if priority is not None:
            self._values["priority"] = priority
        if status is not None:
            self._values["status"] = status

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
    def actions(self) -> PageRuleActions:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#actions PageRule#actions}.'''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(PageRuleActions, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#target PageRule#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#zone_id PageRule#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''The priority of the rule, used to define which Page Rule is processed over another.

        A higher number indicates a higher priority. For example,
        if you have a catch-all Page Rule (rule A: ``/images/*``) but want a more
        specific Page Rule to take precedence (rule B: ``/images/special/*``),
        specify a higher priority for rule B so it overrides rule A.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#priority PageRule#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''The status of the Page Rule. Available values: "active", "disabled".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/page_rule#status PageRule#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PageRule",
    "PageRuleActions",
    "PageRuleActionsCacheKeyFields",
    "PageRuleActionsCacheKeyFieldsCookie",
    "PageRuleActionsCacheKeyFieldsCookieOutputReference",
    "PageRuleActionsCacheKeyFieldsHeader",
    "PageRuleActionsCacheKeyFieldsHeaderOutputReference",
    "PageRuleActionsCacheKeyFieldsHost",
    "PageRuleActionsCacheKeyFieldsHostOutputReference",
    "PageRuleActionsCacheKeyFieldsOutputReference",
    "PageRuleActionsCacheKeyFieldsQueryString",
    "PageRuleActionsCacheKeyFieldsQueryStringOutputReference",
    "PageRuleActionsCacheKeyFieldsUser",
    "PageRuleActionsCacheKeyFieldsUserOutputReference",
    "PageRuleActionsForwardingUrl",
    "PageRuleActionsForwardingUrlOutputReference",
    "PageRuleActionsOutputReference",
    "PageRuleConfig",
]

publication.publish()

def _typecheckingstub__236eb22c254552fb3cf23c2853d4eb6d53d7d86e79695fe42050b09cbe48162d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    actions: typing.Union[PageRuleActions, typing.Dict[builtins.str, typing.Any]],
    target: builtins.str,
    zone_id: builtins.str,
    priority: typing.Optional[jsii.Number] = None,
    status: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__3d3e17519810100113ddebfef1d2a49f6ee3e5ac94d7cc629edf773b39799092(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78425583a59687d7d3b90d46a1d2c7d785c671efe36f9e03f9806f786af0a72c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaba95fc3909ae63549960f5fff0ef615946f26afe55d2be892ac944f9459363(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__823ee4bd39a3fae9f80cd2f5ee7fabda4d0c2c54dd654c2ce6cbf8804f03ac2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__723448f003c4960eed4dd173610dd894938391dc9d4dbba736099a60da5caf89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf4ebb980142101ae1ac0d7a8c83b27fb567a416ac971a10f6a3e9b6a75197dc(
    *,
    always_use_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    automatic_https_rewrites: typing.Optional[builtins.str] = None,
    browser_cache_ttl: typing.Optional[jsii.Number] = None,
    browser_check: typing.Optional[builtins.str] = None,
    bypass_cache_on_cookie: typing.Optional[builtins.str] = None,
    cache_by_device_type: typing.Optional[builtins.str] = None,
    cache_deception_armor: typing.Optional[builtins.str] = None,
    cache_key_fields: typing.Optional[typing.Union[PageRuleActionsCacheKeyFields, typing.Dict[builtins.str, typing.Any]]] = None,
    cache_level: typing.Optional[builtins.str] = None,
    cache_on_cookie: typing.Optional[builtins.str] = None,
    cache_ttl_by_status: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    disable_apps: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_performance: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_security: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_zaraz: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    edge_cache_ttl: typing.Optional[jsii.Number] = None,
    email_obfuscation: typing.Optional[builtins.str] = None,
    explicit_cache_control: typing.Optional[builtins.str] = None,
    forwarding_url: typing.Optional[typing.Union[PageRuleActionsForwardingUrl, typing.Dict[builtins.str, typing.Any]]] = None,
    host_header_override: typing.Optional[builtins.str] = None,
    ip_geolocation: typing.Optional[builtins.str] = None,
    mirage: typing.Optional[builtins.str] = None,
    opportunistic_encryption: typing.Optional[builtins.str] = None,
    origin_error_page_pass_thru: typing.Optional[builtins.str] = None,
    polish: typing.Optional[builtins.str] = None,
    resolve_override: typing.Optional[builtins.str] = None,
    respect_strong_etag: typing.Optional[builtins.str] = None,
    response_buffering: typing.Optional[builtins.str] = None,
    rocket_loader: typing.Optional[builtins.str] = None,
    security_level: typing.Optional[builtins.str] = None,
    sort_query_string_for_cache: typing.Optional[builtins.str] = None,
    ssl: typing.Optional[builtins.str] = None,
    true_client_ip_header: typing.Optional[builtins.str] = None,
    waf: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e77ecaa90d7cf91d05a56c53c802f1f33cb188776c377a0f4b961a3ac4cca4f0(
    *,
    cookie: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsCookie, typing.Dict[builtins.str, typing.Any]]] = None,
    header: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsHeader, typing.Dict[builtins.str, typing.Any]]] = None,
    host: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsHost, typing.Dict[builtins.str, typing.Any]]] = None,
    query_string: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsQueryString, typing.Dict[builtins.str, typing.Any]]] = None,
    user: typing.Optional[typing.Union[PageRuleActionsCacheKeyFieldsUser, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69b925ed2f73a79d279954a9d6dc7815e94940803028915abd7a7da3b22d2045(
    *,
    check_presence: typing.Optional[typing.Sequence[builtins.str]] = None,
    include: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5de40c342556b0de77dbb043a296fc1aac66adbf2652f767aa3ae230fc57da34(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ae34aafd2bcc8e40e8ee525f0b5c598ee095a668b92b12e69278b84f5b6730e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d11df9afc298b273b7995665a8faf624bc60b7379e7ac5c774ed1cb4f1341b38(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98009a8b817ba4e31040ff1018f5c9d71387bc29f9d9afdcaf7b5c751e864dd6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsCookie]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa871e3b27cc7b93abd244efe24bae80be7c6d769adf131620998dc7049daed3(
    *,
    check_presence: typing.Optional[typing.Sequence[builtins.str]] = None,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    include: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f519b073aaa02997052f28351119ee0073df500f5d6fd6687828459d367d568c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8270f65aa831186d8efe7eff4c5650deae0a6ec5a42c78efaae44187f1d48172(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f286f84e95156b0cf53498798a02986397c3e7d23d8848c6c37460c488e0eb8c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bd6e3e3ebb840a9f12d9677f232af1b44670539efe7eed0aa7244a632cfc743(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7f18a69debbec8530d11f49dba273db2d380ec8e63dc2388780f49c652b901b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHeader]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8da67a019aae9cdd3cad78632d11626f52cb742bc98bd8c2b857ba356ccd74e7(
    *,
    resolved: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3b7835f7da100efd954cd9bbe34160ff872c2ed6010827a288f6d98f4e0841e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a31e43e3cb9964345bf25caf1eea420ecf2f0b068779f0b30d0e18e8cee3140(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5ffedf1b31b99bedda959fa4cd9f3ebd9f0cd3f47653990e3923efe4a4c3b2f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsHost]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39ddfd907b1dccb5b231e96e19240c83f4868493c3491af56417f7352d7c5703(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2aeb52ba3dc622bb0efe2c743f7bb027f9c741c20f0ff231e7b8cc7ef79c716(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFields]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d3892605efe4261a3a8158137fcdd61b75e3b02ea948c88c099e67a6a79b7ad(
    *,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    include: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19a006cd5b9d97bdc416d777fd5bdfd61c53c1458ff554e8710dad183df85482(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8be8e5cc44508e7a10a584f9f538034f991603863465cc90d46f53daebf6c541(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__338c89594ec8121e1a6ba1703d55035be7c0fe9fb9c00889e79aedf0c938eb0e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a16b93bd314b7e238cc25ba82bf31994b00608fa09b7b45a66bce2a174d4aa4c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsQueryString]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1185938b5c4f7f4f9285fd7af7bf0dbb6a589490350d3e3820ca4b10bc7d15df(
    *,
    device_type: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    geo: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    lang: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__927837ae2acac3ae0a0dbec6ce412b91949d6d1f2aecae87f75485b4b966e704(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4089762c09af996c952fa8e3cb89a1ca411afe0236fa279683afb9830c7d70ff(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d81f3c65572bcd63826dd4b330de3f7d07f5f0312703ebe65f4a2097a31e1f5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b7c6b6162ce9bded3d292b6cebe26a3d8997d789f34d9d725babe63dba00e71(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72eaab090760a082f59f5ff3d57d08a70228ddec3574d008fc15e68fb3fce31e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsCacheKeyFieldsUser]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9e99c1ff8f3cb4b3f06788808b96b4ea89eb8f89233903750cb4d8abf04d3e0(
    *,
    status_code: jsii.Number,
    url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48980f4c7f151c0f1a4ffb3faf3fd07a25f7d5fb5fd2fa7499f2112afab5a5e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe0dad18b903852b1d426fb003d04ca5fec93bdf1a44b6f6c62fd4430a1643cb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6be674708d7801433a2a4bbb8720b9827dc53f5b93325c1c1b52d478835a2e0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b874ee01474f325ad80ee20c9b32de747a2dd9f3b47c573a9dfa26ee79bcc02(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActionsForwardingUrl]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d19600dc22c94fd29ed9d377c5efa561ca62915318b70dafe97e39ac56dc142c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60908d0ab548b0732c4b80fc71a6c74de53c70169bace4fe411dc209341eb331(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40e1cea0bfa90561698ad92bf2906ccef346b0ded4420d5a3967d2e21feb57bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__845a01ed128525409c548d272c4261591ecf918e01ba4f4e65caf2dbe74e4d2b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1996a65c306e72a1e0be7f0f89271ca64710a17624a6b22307c5215b7375019b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa53e0df29183732e1629516acd8e446a047616d009667623e4dca77e8cc9766(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e51f1d7b72cac73879aa1f0ebb57f1c98940bb69b3c5eee200309d7591d3c8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82272024ac6529b6842a7c3910f447603511077e0cce7411ade507b20e1fe9eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06a630ad6bd8f7916e8e151513d9d48785c86a65567b87ccfd675421017f7d41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c5089e29fbb13d0259361b2cdb46dc84dea4bfe744277b05f8d34280fc63889(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a09031b84489b841beec9d11c0a853f3d44cc838308924ccd83af4634f1649(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6972573d717a4dcdc0a41d0ea769e9f880675d2fc46a00703d064b2a01f6f69(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aecfe815b36717daffade85b69862a3786cfb2d23708d24e97e9866c255b83a6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e66798335e7e046e5b36d7b93495f1b4554d9173c48c4d9454418df8483692ed(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2276f49a16792e01a16594a68dd4867c08b06de4ce7877417c603e9eeeee80c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0de92e81a5dbdbc421236bf8b4c7521e9f9c5e2a453db76d699968d85e090d98(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceed7f4358cc9af9859c48b993f644cdc0e8e21d5bfa87e088a320daa3afadb9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7412a3b457c8bf7bdc7a558c8af8e4440195ffbc942aea24a7800829f9e7a14d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8b40e021b4efb6a17d00090ba3303ca7fb180278f56a2ff21a14ff176abdf59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdde553f4d0bbda06a5991798a1f783218bc3899ba92d1bd077faee2b6ecb0e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e58984630b094e94e096d2cffc4c0689a718e4cb98ed1d614c82d26195572802(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6e19b59361cae031a934932f90ef691d38fbd4cebbbdaaa8752f3875c1bf2af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a65ec0cce373ffd1905cb6a1eee7a67db4ba47b70948628c182084373ad6742b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e62defac004ddf3b2040f5d0d9d2551c279db604d5ae9d2422edf8d9422632f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf70d126eec4394a54e833a16d4545f7dc69dfdca96adb95f4783a9644abda4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28710606d936986b5fbe894995daec055d237f6d173161f82b129865d065e4cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f2bad0de3b2cdf5c73fc29a18bf1fe0cfdca8063a56b7cf619d84eacb98fb8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0014d56c32525dbd8e13eb3826d014ae387cf0efc43711b6250fb0b0f936e91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9093ef519ff2814142f6da569904cd7efc7b557835fa3853e48965d3eb74c24e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__315136d4eb2025708647b95379e01dde04f839750cb68acf04ccfd3de5cf4e08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ac756b45e6bb420f9d904a6d5da9ae193c117721f4d82ea498f8f25a5f512f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ff2478b4ff86f4cd2b8b680e017057046fe1d85456bc0d257eede443cf4d7b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ce41ec709ecb9ae4c0ef776cccb96b7763e0825fc00c0798f6362d1be347995(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cc4b49f3983e2ff4fe75585819bf2a7c9c94718af8a77eef7dfb9870e445790(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PageRuleActions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b728f4e60aefa01f724a31b2719dbe00ed190b52a24b1c2a32ecdf267f8b2d7(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    actions: typing.Union[PageRuleActions, typing.Dict[builtins.str, typing.Any]],
    target: builtins.str,
    zone_id: builtins.str,
    priority: typing.Optional[jsii.Number] = None,
    status: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
