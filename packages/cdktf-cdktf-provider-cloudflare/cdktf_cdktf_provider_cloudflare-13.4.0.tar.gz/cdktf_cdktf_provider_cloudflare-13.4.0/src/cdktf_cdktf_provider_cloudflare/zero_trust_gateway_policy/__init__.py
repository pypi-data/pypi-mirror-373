r'''
# `cloudflare_zero_trust_gateway_policy`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_gateway_policy`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy).
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


class ZeroTrustGatewayPolicy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy cloudflare_zero_trust_gateway_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        action: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        device_posture: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        expiration: typing.Optional[typing.Union["ZeroTrustGatewayPolicyExpiration", typing.Dict[builtins.str, typing.Any]]] = None,
        filters: typing.Optional[typing.Sequence[builtins.str]] = None,
        identity: typing.Optional[builtins.str] = None,
        precedence: typing.Optional[jsii.Number] = None,
        rule_settings: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[typing.Union["ZeroTrustGatewayPolicySchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        traffic: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy cloudflare_zero_trust_gateway_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#account_id ZeroTrustGatewayPolicy#account_id}.
        :param action: The action to perform when the associated traffic, identity, and device posture expressions are either absent or evaluate to ``true``. Available values: "on", "off", "allow", "block", "scan", "noscan", "safesearch", "ytrestricted", "isolate", "noisolate", "override", "l4_override", "egress", "resolve", "quarantine", "redirect". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#action ZeroTrustGatewayPolicy#action}
        :param name: The name of the rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#name ZeroTrustGatewayPolicy#name}
        :param description: The description of the rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#description ZeroTrustGatewayPolicy#description}
        :param device_posture: The wirefilter expression used for device posture check matching. The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#device_posture ZeroTrustGatewayPolicy#device_posture}
        :param enabled: True if the rule is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enabled ZeroTrustGatewayPolicy#enabled}
        :param expiration: The expiration time stamp and default duration of a DNS policy. Takes precedence over the policy's ``schedule`` configuration, if any. This does not apply to HTTP or network policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#expiration ZeroTrustGatewayPolicy#expiration}
        :param filters: The protocol or layer to evaluate the traffic, identity, and device. posture expressions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#filters ZeroTrustGatewayPolicy#filters}
        :param identity: The wirefilter expression used for identity matching. The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#identity ZeroTrustGatewayPolicy#identity}
        :param precedence: Precedence sets the order of your rules. Lower values indicate higher precedence. At each processing phase, applicable rules are evaluated in ascending order of this value. Refer to `Order of enforcement <http://developers.cloudflare.com/learning-paths/secure-internet-traffic/understand-policies/order-of-enforcement/#manage-precedence-with-terraform>`_ docs on how to manage precedence via Terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#precedence ZeroTrustGatewayPolicy#precedence}
        :param rule_settings: Additional settings that modify the rule's action. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#rule_settings ZeroTrustGatewayPolicy#rule_settings}
        :param schedule: The schedule for activating DNS policies. This does not apply to HTTP or network policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#schedule ZeroTrustGatewayPolicy#schedule}
        :param traffic: The wirefilter expression used for traffic matching. The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#traffic ZeroTrustGatewayPolicy#traffic}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e786f3b51fdd9d9ed8a9ede6d413dce3bca2cd0cf1cb66429b00315285745858)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustGatewayPolicyConfig(
            account_id=account_id,
            action=action,
            name=name,
            description=description,
            device_posture=device_posture,
            enabled=enabled,
            expiration=expiration,
            filters=filters,
            identity=identity,
            precedence=precedence,
            rule_settings=rule_settings,
            schedule=schedule,
            traffic=traffic,
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
        '''Generates CDKTF code for importing a ZeroTrustGatewayPolicy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustGatewayPolicy to import.
        :param import_from_id: The id of the existing ZeroTrustGatewayPolicy that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustGatewayPolicy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08a82a394c6d2096b6cfe77d2cb2d7a0802d1cb0b8c4111b58a4499f87b9cb2b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putExpiration")
    def put_expiration(
        self,
        *,
        expires_at: builtins.str,
        duration: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param expires_at: The time stamp at which the policy will expire and cease to be applied. Must adhere to RFC 3339 and include a UTC offset. Non-zero offsets are accepted but will be converted to the equivalent value with offset zero (UTC+00:00) and will be returned as time stamps with offset zero denoted by a trailing 'Z'. Policies with an expiration do not consider the timezone of clients they are applied to, and expire "globally" at the point given by their ``expires_at`` value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#expires_at ZeroTrustGatewayPolicy#expires_at}
        :param duration: The default duration a policy will be active in minutes. Must be set in order to use the ``reset_expiration`` endpoint on this rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#duration ZeroTrustGatewayPolicy#duration}
        '''
        value = ZeroTrustGatewayPolicyExpiration(
            expires_at=expires_at, duration=duration
        )

        return typing.cast(None, jsii.invoke(self, "putExpiration", [value]))

    @jsii.member(jsii_name="putRuleSettings")
    def put_rule_settings(
        self,
        *,
        add_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        allow_child_bypass: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        audit_ssh: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsAuditSsh", typing.Dict[builtins.str, typing.Any]]] = None,
        biso_admin_controls: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls", typing.Dict[builtins.str, typing.Any]]] = None,
        block_page: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsBlockPage", typing.Dict[builtins.str, typing.Any]]] = None,
        block_page_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        block_reason: typing.Optional[builtins.str] = None,
        bypass_parent_rule: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        check_session: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsCheckSession", typing.Dict[builtins.str, typing.Any]]] = None,
        dns_resolvers: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsDnsResolvers", typing.Dict[builtins.str, typing.Any]]] = None,
        egress: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsEgress", typing.Dict[builtins.str, typing.Any]]] = None,
        ignore_cname_category_matches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        insecure_disable_dnssec_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_categories: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_indicator_feeds: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        l4_override: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsL4Override", typing.Dict[builtins.str, typing.Any]]] = None,
        notification_settings: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsNotificationSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        override_host: typing.Optional[builtins.str] = None,
        override_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        payload_log: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsPayloadLog", typing.Dict[builtins.str, typing.Any]]] = None,
        quarantine: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsQuarantine", typing.Dict[builtins.str, typing.Any]]] = None,
        redirect: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsRedirect", typing.Dict[builtins.str, typing.Any]]] = None,
        resolve_dns_internally: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally", typing.Dict[builtins.str, typing.Any]]] = None,
        resolve_dns_through_cloudflare: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        untrusted_cert: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsUntrustedCert", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param add_headers: Add custom headers to allowed requests, in the form of key-value pairs. Keys are header names, pointing to an array with its header value(s). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#add_headers ZeroTrustGatewayPolicy#add_headers}
        :param allow_child_bypass: Set by parent MSP accounts to enable their children to bypass this rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#allow_child_bypass ZeroTrustGatewayPolicy#allow_child_bypass}
        :param audit_ssh: Settings for the Audit SSH action. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#audit_ssh ZeroTrustGatewayPolicy#audit_ssh}
        :param biso_admin_controls: Configure how browser isolation behaves. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#biso_admin_controls ZeroTrustGatewayPolicy#biso_admin_controls}
        :param block_page: Custom block page settings. If missing/null, blocking will use the the account settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#block_page ZeroTrustGatewayPolicy#block_page}
        :param block_page_enabled: Enable the custom block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#block_page_enabled ZeroTrustGatewayPolicy#block_page_enabled}
        :param block_reason: The text describing why this block occurred, displayed on the custom block page (if enabled). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#block_reason ZeroTrustGatewayPolicy#block_reason}
        :param bypass_parent_rule: Set by children MSP accounts to bypass their parent's rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#bypass_parent_rule ZeroTrustGatewayPolicy#bypass_parent_rule}
        :param check_session: Configure how session check behaves. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#check_session ZeroTrustGatewayPolicy#check_session}
        :param dns_resolvers: Add your own custom resolvers to route queries that match the resolver policy. Cannot be used when 'resolve_dns_through_cloudflare' or 'resolve_dns_internally' are set. DNS queries will route to the address closest to their origin. Only valid when a rule's action is set to 'resolve'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dns_resolvers ZeroTrustGatewayPolicy#dns_resolvers}
        :param egress: Configure how Gateway Proxy traffic egresses. You can enable this setting for rules with Egress actions and filters, or omit it to indicate local egress via WARP IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#egress ZeroTrustGatewayPolicy#egress}
        :param ignore_cname_category_matches: Set to true, to ignore the category matches at CNAME domains in a response. If unchecked, the categories in this rule will be checked against all the CNAME domain categories in a response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ignore_cname_category_matches ZeroTrustGatewayPolicy#ignore_cname_category_matches}
        :param insecure_disable_dnssec_validation: INSECURE - disable DNSSEC validation (for Allow actions). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#insecure_disable_dnssec_validation ZeroTrustGatewayPolicy#insecure_disable_dnssec_validation}
        :param ip_categories: Set to true to enable IPs in DNS resolver category blocks. By default categories only block based on domain names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip_categories ZeroTrustGatewayPolicy#ip_categories}
        :param ip_indicator_feeds: Set to true to include IPs in DNS resolver indicator feed blocks. By default indicator feeds only block based on domain names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip_indicator_feeds ZeroTrustGatewayPolicy#ip_indicator_feeds}
        :param l4_override: Send matching traffic to the supplied destination IP address. and port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#l4override ZeroTrustGatewayPolicy#l4override}
        :param notification_settings: Configure a notification to display on the user's device when this rule is matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#notification_settings ZeroTrustGatewayPolicy#notification_settings}
        :param override_host: Override matching DNS queries with a hostname. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#override_host ZeroTrustGatewayPolicy#override_host}
        :param override_ips: Override matching DNS queries with an IP or set of IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#override_ips ZeroTrustGatewayPolicy#override_ips}
        :param payload_log: Configure DLP payload logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#payload_log ZeroTrustGatewayPolicy#payload_log}
        :param quarantine: Settings that apply to quarantine rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#quarantine ZeroTrustGatewayPolicy#quarantine}
        :param redirect: Settings that apply to redirect rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#redirect ZeroTrustGatewayPolicy#redirect}
        :param resolve_dns_internally: Configure to forward the query to the internal DNS service, passing the specified 'view_id' as input. Cannot be set when 'dns_resolvers' are specified or 'resolve_dns_through_cloudflare' is set. Only valid when a rule's action is set to 'resolve'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#resolve_dns_internally ZeroTrustGatewayPolicy#resolve_dns_internally}
        :param resolve_dns_through_cloudflare: Enable to send queries that match the policy to Cloudflare's default 1.1.1.1 DNS resolver. Cannot be set when 'dns_resolvers' are specified or 'resolve_dns_internally' is set. Only valid when a rule's action is set to 'resolve'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#resolve_dns_through_cloudflare ZeroTrustGatewayPolicy#resolve_dns_through_cloudflare}
        :param untrusted_cert: Configure behavior when an upstream cert is invalid or an SSL error occurs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#untrusted_cert ZeroTrustGatewayPolicy#untrusted_cert}
        '''
        value = ZeroTrustGatewayPolicyRuleSettings(
            add_headers=add_headers,
            allow_child_bypass=allow_child_bypass,
            audit_ssh=audit_ssh,
            biso_admin_controls=biso_admin_controls,
            block_page=block_page,
            block_page_enabled=block_page_enabled,
            block_reason=block_reason,
            bypass_parent_rule=bypass_parent_rule,
            check_session=check_session,
            dns_resolvers=dns_resolvers,
            egress=egress,
            ignore_cname_category_matches=ignore_cname_category_matches,
            insecure_disable_dnssec_validation=insecure_disable_dnssec_validation,
            ip_categories=ip_categories,
            ip_indicator_feeds=ip_indicator_feeds,
            l4_override=l4_override,
            notification_settings=notification_settings,
            override_host=override_host,
            override_ips=override_ips,
            payload_log=payload_log,
            quarantine=quarantine,
            redirect=redirect,
            resolve_dns_internally=resolve_dns_internally,
            resolve_dns_through_cloudflare=resolve_dns_through_cloudflare,
            untrusted_cert=untrusted_cert,
        )

        return typing.cast(None, jsii.invoke(self, "putRuleSettings", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(
        self,
        *,
        fri: typing.Optional[builtins.str] = None,
        mon: typing.Optional[builtins.str] = None,
        sat: typing.Optional[builtins.str] = None,
        sun: typing.Optional[builtins.str] = None,
        thu: typing.Optional[builtins.str] = None,
        time_zone: typing.Optional[builtins.str] = None,
        tue: typing.Optional[builtins.str] = None,
        wed: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fri: The time intervals when the rule will be active on Fridays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Fridays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#fri ZeroTrustGatewayPolicy#fri}
        :param mon: The time intervals when the rule will be active on Mondays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Mondays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#mon ZeroTrustGatewayPolicy#mon}
        :param sat: The time intervals when the rule will be active on Saturdays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Saturdays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#sat ZeroTrustGatewayPolicy#sat}
        :param sun: The time intervals when the rule will be active on Sundays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Sundays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#sun ZeroTrustGatewayPolicy#sun}
        :param thu: The time intervals when the rule will be active on Thursdays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Thursdays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#thu ZeroTrustGatewayPolicy#thu}
        :param time_zone: The time zone the rule will be evaluated against. If a `valid time zone city name <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List>`_ is provided, Gateway will always use the current time at that time zone. If this parameter is omitted, then Gateway will use the time zone inferred from the user's source IP to evaluate the rule. If Gateway cannot determine the time zone from the IP, we will fall back to the time zone of the user's connected data center. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#time_zone ZeroTrustGatewayPolicy#time_zone}
        :param tue: The time intervals when the rule will be active on Tuesdays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Tuesdays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#tue ZeroTrustGatewayPolicy#tue}
        :param wed: The time intervals when the rule will be active on Wednesdays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Wednesdays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#wed ZeroTrustGatewayPolicy#wed}
        '''
        value = ZeroTrustGatewayPolicySchedule(
            fri=fri,
            mon=mon,
            sat=sat,
            sun=sun,
            thu=thu,
            time_zone=time_zone,
            tue=tue,
            wed=wed,
        )

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDevicePosture")
    def reset_device_posture(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDevicePosture", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetExpiration")
    def reset_expiration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpiration", []))

    @jsii.member(jsii_name="resetFilters")
    def reset_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilters", []))

    @jsii.member(jsii_name="resetIdentity")
    def reset_identity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentity", []))

    @jsii.member(jsii_name="resetPrecedence")
    def reset_precedence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrecedence", []))

    @jsii.member(jsii_name="resetRuleSettings")
    def reset_rule_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuleSettings", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @jsii.member(jsii_name="resetTraffic")
    def reset_traffic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTraffic", []))

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
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="expiration")
    def expiration(self) -> "ZeroTrustGatewayPolicyExpirationOutputReference":
        return typing.cast("ZeroTrustGatewayPolicyExpirationOutputReference", jsii.get(self, "expiration"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="notSharable")
    def not_sharable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "notSharable"))

    @builtins.property
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "readOnly"))

    @builtins.property
    @jsii.member(jsii_name="ruleSettings")
    def rule_settings(self) -> "ZeroTrustGatewayPolicyRuleSettingsOutputReference":
        return typing.cast("ZeroTrustGatewayPolicyRuleSettingsOutputReference", jsii.get(self, "ruleSettings"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "ZeroTrustGatewayPolicyScheduleOutputReference":
        return typing.cast("ZeroTrustGatewayPolicyScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="sourceAccount")
    def source_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceAccount"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="warningStatus")
    def warning_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warningStatus"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="devicePostureInput")
    def device_posture_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "devicePostureInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationInput")
    def expiration_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyExpiration"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyExpiration"]], jsii.get(self, "expirationInput"))

    @builtins.property
    @jsii.member(jsii_name="filtersInput")
    def filters_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "filtersInput"))

    @builtins.property
    @jsii.member(jsii_name="identityInput")
    def identity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="precedenceInput")
    def precedence_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "precedenceInput"))

    @builtins.property
    @jsii.member(jsii_name="ruleSettingsInput")
    def rule_settings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettings"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettings"]], jsii.get(self, "ruleSettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicySchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicySchedule"]], jsii.get(self, "scheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficInput")
    def traffic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trafficInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0bb7ba5f48d9b8e2a3bb95f022537a9bfc450f3475c72a300c1cae1683f9ec2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7bbd14973f8b3f0a43994b287c91e533e76cb5b8c5e095101c90750c11d93b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83db28167eff420a547cf252dd8e7781e5796c1cace39c68df6c1a06b2da2d0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "devicePosture"))

    @device_posture.setter
    def device_posture(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee39d2975aef69e34e1a231b8e211addc371b9ad64dceb2f20e20d4ae852c237)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "devicePosture", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__45825779e8075f762c6a646e54a09f77631a4328dfb317cc06b661e8121e179b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="filters")
    def filters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "filters"))

    @filters.setter
    def filters(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f18e5f294f5711f739edce78df2d227cbee0051bd29aba76a875d970ca98100b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "filters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identity")
    def identity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identity"))

    @identity.setter
    def identity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fff43c71cbeb7eff49371043e13151751ba92b81c1e0493e6f2f3ebce50d929)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa62bd411e5957a4f46d586eb095eb3d653370b09ee649ce6849dd5a2d07624b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="precedence")
    def precedence(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precedence"))

    @precedence.setter
    def precedence(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5210b06d00643b59aad339b83d84162c64bdb7c26827fb9528babd7e3e61786c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "precedence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="traffic")
    def traffic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "traffic"))

    @traffic.setter
    def traffic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__872dd1a90e3d9f1a1ba75703168e5c9754c8cbf3777f03ea7b5294d225912329)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "traffic", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyConfig",
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
        "action": "action",
        "name": "name",
        "description": "description",
        "device_posture": "devicePosture",
        "enabled": "enabled",
        "expiration": "expiration",
        "filters": "filters",
        "identity": "identity",
        "precedence": "precedence",
        "rule_settings": "ruleSettings",
        "schedule": "schedule",
        "traffic": "traffic",
    },
)
class ZeroTrustGatewayPolicyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        action: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        device_posture: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        expiration: typing.Optional[typing.Union["ZeroTrustGatewayPolicyExpiration", typing.Dict[builtins.str, typing.Any]]] = None,
        filters: typing.Optional[typing.Sequence[builtins.str]] = None,
        identity: typing.Optional[builtins.str] = None,
        precedence: typing.Optional[jsii.Number] = None,
        rule_settings: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[typing.Union["ZeroTrustGatewayPolicySchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        traffic: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#account_id ZeroTrustGatewayPolicy#account_id}.
        :param action: The action to perform when the associated traffic, identity, and device posture expressions are either absent or evaluate to ``true``. Available values: "on", "off", "allow", "block", "scan", "noscan", "safesearch", "ytrestricted", "isolate", "noisolate", "override", "l4_override", "egress", "resolve", "quarantine", "redirect". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#action ZeroTrustGatewayPolicy#action}
        :param name: The name of the rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#name ZeroTrustGatewayPolicy#name}
        :param description: The description of the rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#description ZeroTrustGatewayPolicy#description}
        :param device_posture: The wirefilter expression used for device posture check matching. The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#device_posture ZeroTrustGatewayPolicy#device_posture}
        :param enabled: True if the rule is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enabled ZeroTrustGatewayPolicy#enabled}
        :param expiration: The expiration time stamp and default duration of a DNS policy. Takes precedence over the policy's ``schedule`` configuration, if any. This does not apply to HTTP or network policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#expiration ZeroTrustGatewayPolicy#expiration}
        :param filters: The protocol or layer to evaluate the traffic, identity, and device. posture expressions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#filters ZeroTrustGatewayPolicy#filters}
        :param identity: The wirefilter expression used for identity matching. The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#identity ZeroTrustGatewayPolicy#identity}
        :param precedence: Precedence sets the order of your rules. Lower values indicate higher precedence. At each processing phase, applicable rules are evaluated in ascending order of this value. Refer to `Order of enforcement <http://developers.cloudflare.com/learning-paths/secure-internet-traffic/understand-policies/order-of-enforcement/#manage-precedence-with-terraform>`_ docs on how to manage precedence via Terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#precedence ZeroTrustGatewayPolicy#precedence}
        :param rule_settings: Additional settings that modify the rule's action. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#rule_settings ZeroTrustGatewayPolicy#rule_settings}
        :param schedule: The schedule for activating DNS policies. This does not apply to HTTP or network policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#schedule ZeroTrustGatewayPolicy#schedule}
        :param traffic: The wirefilter expression used for traffic matching. The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#traffic ZeroTrustGatewayPolicy#traffic}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(expiration, dict):
            expiration = ZeroTrustGatewayPolicyExpiration(**expiration)
        if isinstance(rule_settings, dict):
            rule_settings = ZeroTrustGatewayPolicyRuleSettings(**rule_settings)
        if isinstance(schedule, dict):
            schedule = ZeroTrustGatewayPolicySchedule(**schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f3d5137255dbb7219c971b313cd804791e2a0ef37964d8a593b17f6a3718187)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument device_posture", value=device_posture, expected_type=type_hints["device_posture"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument expiration", value=expiration, expected_type=type_hints["expiration"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument precedence", value=precedence, expected_type=type_hints["precedence"])
            check_type(argname="argument rule_settings", value=rule_settings, expected_type=type_hints["rule_settings"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument traffic", value=traffic, expected_type=type_hints["traffic"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "action": action,
            "name": name,
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
        if description is not None:
            self._values["description"] = description
        if device_posture is not None:
            self._values["device_posture"] = device_posture
        if enabled is not None:
            self._values["enabled"] = enabled
        if expiration is not None:
            self._values["expiration"] = expiration
        if filters is not None:
            self._values["filters"] = filters
        if identity is not None:
            self._values["identity"] = identity
        if precedence is not None:
            self._values["precedence"] = precedence
        if rule_settings is not None:
            self._values["rule_settings"] = rule_settings
        if schedule is not None:
            self._values["schedule"] = schedule
        if traffic is not None:
            self._values["traffic"] = traffic

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#account_id ZeroTrustGatewayPolicy#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action(self) -> builtins.str:
        '''The action to perform when the associated traffic, identity, and device posture expressions are either absent or evaluate to ``true``.

        Available values: "on", "off", "allow", "block", "scan", "noscan", "safesearch", "ytrestricted", "isolate", "noisolate", "override", "l4_override", "egress", "resolve", "quarantine", "redirect".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#action ZeroTrustGatewayPolicy#action}
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#name ZeroTrustGatewayPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#description ZeroTrustGatewayPolicy#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_posture(self) -> typing.Optional[builtins.str]:
        '''The wirefilter expression used for device posture check matching.

        The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#device_posture ZeroTrustGatewayPolicy#device_posture}
        '''
        result = self._values.get("device_posture")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the rule is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enabled ZeroTrustGatewayPolicy#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def expiration(self) -> typing.Optional["ZeroTrustGatewayPolicyExpiration"]:
        '''The expiration time stamp and default duration of a DNS policy. Takes precedence over the policy's ``schedule`` configuration, if any.

        This does not apply to HTTP or network policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#expiration ZeroTrustGatewayPolicy#expiration}
        '''
        result = self._values.get("expiration")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyExpiration"], result)

    @builtins.property
    def filters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The protocol or layer to evaluate the traffic, identity, and device. posture expressions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#filters ZeroTrustGatewayPolicy#filters}
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def identity(self) -> typing.Optional[builtins.str]:
        '''The wirefilter expression used for identity matching.

        The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#identity ZeroTrustGatewayPolicy#identity}
        '''
        result = self._values.get("identity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def precedence(self) -> typing.Optional[jsii.Number]:
        '''Precedence sets the order of your rules.

        Lower values indicate higher precedence. At each processing phase, applicable rules are evaluated in ascending order of this value. Refer to `Order of enforcement <http://developers.cloudflare.com/learning-paths/secure-internet-traffic/understand-policies/order-of-enforcement/#manage-precedence-with-terraform>`_ docs on how to manage precedence via Terraform.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#precedence ZeroTrustGatewayPolicy#precedence}
        '''
        result = self._values.get("precedence")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rule_settings(self) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettings"]:
        '''Additional settings that modify the rule's action.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#rule_settings ZeroTrustGatewayPolicy#rule_settings}
        '''
        result = self._values.get("rule_settings")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettings"], result)

    @builtins.property
    def schedule(self) -> typing.Optional["ZeroTrustGatewayPolicySchedule"]:
        '''The schedule for activating DNS policies. This does not apply to HTTP or network policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#schedule ZeroTrustGatewayPolicy#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicySchedule"], result)

    @builtins.property
    def traffic(self) -> typing.Optional[builtins.str]:
        '''The wirefilter expression used for traffic matching.

        The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#traffic ZeroTrustGatewayPolicy#traffic}
        '''
        result = self._values.get("traffic")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyExpiration",
    jsii_struct_bases=[],
    name_mapping={"expires_at": "expiresAt", "duration": "duration"},
)
class ZeroTrustGatewayPolicyExpiration:
    def __init__(
        self,
        *,
        expires_at: builtins.str,
        duration: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param expires_at: The time stamp at which the policy will expire and cease to be applied. Must adhere to RFC 3339 and include a UTC offset. Non-zero offsets are accepted but will be converted to the equivalent value with offset zero (UTC+00:00) and will be returned as time stamps with offset zero denoted by a trailing 'Z'. Policies with an expiration do not consider the timezone of clients they are applied to, and expire "globally" at the point given by their ``expires_at`` value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#expires_at ZeroTrustGatewayPolicy#expires_at}
        :param duration: The default duration a policy will be active in minutes. Must be set in order to use the ``reset_expiration`` endpoint on this rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#duration ZeroTrustGatewayPolicy#duration}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a22e90656dbfb5affc5461cc88f420c65a62504626e8aaae73b67bd55f5d706d)
            check_type(argname="argument expires_at", value=expires_at, expected_type=type_hints["expires_at"])
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "expires_at": expires_at,
        }
        if duration is not None:
            self._values["duration"] = duration

    @builtins.property
    def expires_at(self) -> builtins.str:
        '''The time stamp at which the policy will expire and cease to be applied.

        Must adhere to RFC 3339 and include a UTC offset. Non-zero
        offsets are accepted but will be converted to the equivalent
        value with offset zero (UTC+00:00) and will be returned as time
        stamps with offset zero denoted by a trailing 'Z'.

        Policies with an expiration do not consider the timezone of
        clients they are applied to, and expire "globally" at the point
        given by their ``expires_at`` value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#expires_at ZeroTrustGatewayPolicy#expires_at}
        '''
        result = self._values.get("expires_at")
        assert result is not None, "Required property 'expires_at' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def duration(self) -> typing.Optional[jsii.Number]:
        '''The default duration a policy will be active in minutes.

        Must be set in order to use the ``reset_expiration`` endpoint on this rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#duration ZeroTrustGatewayPolicy#duration}
        '''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyExpiration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyExpirationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyExpirationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__acc4a601ddf89bd273cfff3a1f85944fc997bba30d3e4fc12a25695c453beb41)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDuration")
    def reset_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDuration", []))

    @builtins.property
    @jsii.member(jsii_name="expired")
    def expired(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "expired"))

    @builtins.property
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "durationInput"))

    @builtins.property
    @jsii.member(jsii_name="expiresAtInput")
    def expires_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expiresAtInput"))

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c3a7530d11d824f05eed7541a667e4d0fff1c0038bdc91d3b18985fb7f71289)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="expiresAt")
    def expires_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiresAt"))

    @expires_at.setter
    def expires_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbea57ced4427f47478d49c78359ac3e387fc37d5fc0784f9d2ddbdcfc935173)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expiresAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyExpiration]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyExpiration]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyExpiration]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffadd22ffcf5404d27322fc7899d4e3fd48372db2388a659b4f6afa1955f4cc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettings",
    jsii_struct_bases=[],
    name_mapping={
        "add_headers": "addHeaders",
        "allow_child_bypass": "allowChildBypass",
        "audit_ssh": "auditSsh",
        "biso_admin_controls": "bisoAdminControls",
        "block_page": "blockPage",
        "block_page_enabled": "blockPageEnabled",
        "block_reason": "blockReason",
        "bypass_parent_rule": "bypassParentRule",
        "check_session": "checkSession",
        "dns_resolvers": "dnsResolvers",
        "egress": "egress",
        "ignore_cname_category_matches": "ignoreCnameCategoryMatches",
        "insecure_disable_dnssec_validation": "insecureDisableDnssecValidation",
        "ip_categories": "ipCategories",
        "ip_indicator_feeds": "ipIndicatorFeeds",
        "l4_override": "l4Override",
        "notification_settings": "notificationSettings",
        "override_host": "overrideHost",
        "override_ips": "overrideIps",
        "payload_log": "payloadLog",
        "quarantine": "quarantine",
        "redirect": "redirect",
        "resolve_dns_internally": "resolveDnsInternally",
        "resolve_dns_through_cloudflare": "resolveDnsThroughCloudflare",
        "untrusted_cert": "untrustedCert",
    },
)
class ZeroTrustGatewayPolicyRuleSettings:
    def __init__(
        self,
        *,
        add_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        allow_child_bypass: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        audit_ssh: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsAuditSsh", typing.Dict[builtins.str, typing.Any]]] = None,
        biso_admin_controls: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls", typing.Dict[builtins.str, typing.Any]]] = None,
        block_page: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsBlockPage", typing.Dict[builtins.str, typing.Any]]] = None,
        block_page_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        block_reason: typing.Optional[builtins.str] = None,
        bypass_parent_rule: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        check_session: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsCheckSession", typing.Dict[builtins.str, typing.Any]]] = None,
        dns_resolvers: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsDnsResolvers", typing.Dict[builtins.str, typing.Any]]] = None,
        egress: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsEgress", typing.Dict[builtins.str, typing.Any]]] = None,
        ignore_cname_category_matches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        insecure_disable_dnssec_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_categories: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_indicator_feeds: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        l4_override: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsL4Override", typing.Dict[builtins.str, typing.Any]]] = None,
        notification_settings: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsNotificationSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        override_host: typing.Optional[builtins.str] = None,
        override_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        payload_log: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsPayloadLog", typing.Dict[builtins.str, typing.Any]]] = None,
        quarantine: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsQuarantine", typing.Dict[builtins.str, typing.Any]]] = None,
        redirect: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsRedirect", typing.Dict[builtins.str, typing.Any]]] = None,
        resolve_dns_internally: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally", typing.Dict[builtins.str, typing.Any]]] = None,
        resolve_dns_through_cloudflare: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        untrusted_cert: typing.Optional[typing.Union["ZeroTrustGatewayPolicyRuleSettingsUntrustedCert", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param add_headers: Add custom headers to allowed requests, in the form of key-value pairs. Keys are header names, pointing to an array with its header value(s). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#add_headers ZeroTrustGatewayPolicy#add_headers}
        :param allow_child_bypass: Set by parent MSP accounts to enable their children to bypass this rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#allow_child_bypass ZeroTrustGatewayPolicy#allow_child_bypass}
        :param audit_ssh: Settings for the Audit SSH action. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#audit_ssh ZeroTrustGatewayPolicy#audit_ssh}
        :param biso_admin_controls: Configure how browser isolation behaves. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#biso_admin_controls ZeroTrustGatewayPolicy#biso_admin_controls}
        :param block_page: Custom block page settings. If missing/null, blocking will use the the account settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#block_page ZeroTrustGatewayPolicy#block_page}
        :param block_page_enabled: Enable the custom block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#block_page_enabled ZeroTrustGatewayPolicy#block_page_enabled}
        :param block_reason: The text describing why this block occurred, displayed on the custom block page (if enabled). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#block_reason ZeroTrustGatewayPolicy#block_reason}
        :param bypass_parent_rule: Set by children MSP accounts to bypass their parent's rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#bypass_parent_rule ZeroTrustGatewayPolicy#bypass_parent_rule}
        :param check_session: Configure how session check behaves. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#check_session ZeroTrustGatewayPolicy#check_session}
        :param dns_resolvers: Add your own custom resolvers to route queries that match the resolver policy. Cannot be used when 'resolve_dns_through_cloudflare' or 'resolve_dns_internally' are set. DNS queries will route to the address closest to their origin. Only valid when a rule's action is set to 'resolve'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dns_resolvers ZeroTrustGatewayPolicy#dns_resolvers}
        :param egress: Configure how Gateway Proxy traffic egresses. You can enable this setting for rules with Egress actions and filters, or omit it to indicate local egress via WARP IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#egress ZeroTrustGatewayPolicy#egress}
        :param ignore_cname_category_matches: Set to true, to ignore the category matches at CNAME domains in a response. If unchecked, the categories in this rule will be checked against all the CNAME domain categories in a response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ignore_cname_category_matches ZeroTrustGatewayPolicy#ignore_cname_category_matches}
        :param insecure_disable_dnssec_validation: INSECURE - disable DNSSEC validation (for Allow actions). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#insecure_disable_dnssec_validation ZeroTrustGatewayPolicy#insecure_disable_dnssec_validation}
        :param ip_categories: Set to true to enable IPs in DNS resolver category blocks. By default categories only block based on domain names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip_categories ZeroTrustGatewayPolicy#ip_categories}
        :param ip_indicator_feeds: Set to true to include IPs in DNS resolver indicator feed blocks. By default indicator feeds only block based on domain names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip_indicator_feeds ZeroTrustGatewayPolicy#ip_indicator_feeds}
        :param l4_override: Send matching traffic to the supplied destination IP address. and port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#l4override ZeroTrustGatewayPolicy#l4override}
        :param notification_settings: Configure a notification to display on the user's device when this rule is matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#notification_settings ZeroTrustGatewayPolicy#notification_settings}
        :param override_host: Override matching DNS queries with a hostname. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#override_host ZeroTrustGatewayPolicy#override_host}
        :param override_ips: Override matching DNS queries with an IP or set of IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#override_ips ZeroTrustGatewayPolicy#override_ips}
        :param payload_log: Configure DLP payload logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#payload_log ZeroTrustGatewayPolicy#payload_log}
        :param quarantine: Settings that apply to quarantine rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#quarantine ZeroTrustGatewayPolicy#quarantine}
        :param redirect: Settings that apply to redirect rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#redirect ZeroTrustGatewayPolicy#redirect}
        :param resolve_dns_internally: Configure to forward the query to the internal DNS service, passing the specified 'view_id' as input. Cannot be set when 'dns_resolvers' are specified or 'resolve_dns_through_cloudflare' is set. Only valid when a rule's action is set to 'resolve'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#resolve_dns_internally ZeroTrustGatewayPolicy#resolve_dns_internally}
        :param resolve_dns_through_cloudflare: Enable to send queries that match the policy to Cloudflare's default 1.1.1.1 DNS resolver. Cannot be set when 'dns_resolvers' are specified or 'resolve_dns_internally' is set. Only valid when a rule's action is set to 'resolve'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#resolve_dns_through_cloudflare ZeroTrustGatewayPolicy#resolve_dns_through_cloudflare}
        :param untrusted_cert: Configure behavior when an upstream cert is invalid or an SSL error occurs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#untrusted_cert ZeroTrustGatewayPolicy#untrusted_cert}
        '''
        if isinstance(audit_ssh, dict):
            audit_ssh = ZeroTrustGatewayPolicyRuleSettingsAuditSsh(**audit_ssh)
        if isinstance(biso_admin_controls, dict):
            biso_admin_controls = ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls(**biso_admin_controls)
        if isinstance(block_page, dict):
            block_page = ZeroTrustGatewayPolicyRuleSettingsBlockPage(**block_page)
        if isinstance(check_session, dict):
            check_session = ZeroTrustGatewayPolicyRuleSettingsCheckSession(**check_session)
        if isinstance(dns_resolvers, dict):
            dns_resolvers = ZeroTrustGatewayPolicyRuleSettingsDnsResolvers(**dns_resolvers)
        if isinstance(egress, dict):
            egress = ZeroTrustGatewayPolicyRuleSettingsEgress(**egress)
        if isinstance(l4_override, dict):
            l4_override = ZeroTrustGatewayPolicyRuleSettingsL4Override(**l4_override)
        if isinstance(notification_settings, dict):
            notification_settings = ZeroTrustGatewayPolicyRuleSettingsNotificationSettings(**notification_settings)
        if isinstance(payload_log, dict):
            payload_log = ZeroTrustGatewayPolicyRuleSettingsPayloadLog(**payload_log)
        if isinstance(quarantine, dict):
            quarantine = ZeroTrustGatewayPolicyRuleSettingsQuarantine(**quarantine)
        if isinstance(redirect, dict):
            redirect = ZeroTrustGatewayPolicyRuleSettingsRedirect(**redirect)
        if isinstance(resolve_dns_internally, dict):
            resolve_dns_internally = ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally(**resolve_dns_internally)
        if isinstance(untrusted_cert, dict):
            untrusted_cert = ZeroTrustGatewayPolicyRuleSettingsUntrustedCert(**untrusted_cert)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea8f89e3048662a05610c3fc4775c975b8cbfc7190cf304482a2b63c0a5c20af)
            check_type(argname="argument add_headers", value=add_headers, expected_type=type_hints["add_headers"])
            check_type(argname="argument allow_child_bypass", value=allow_child_bypass, expected_type=type_hints["allow_child_bypass"])
            check_type(argname="argument audit_ssh", value=audit_ssh, expected_type=type_hints["audit_ssh"])
            check_type(argname="argument biso_admin_controls", value=biso_admin_controls, expected_type=type_hints["biso_admin_controls"])
            check_type(argname="argument block_page", value=block_page, expected_type=type_hints["block_page"])
            check_type(argname="argument block_page_enabled", value=block_page_enabled, expected_type=type_hints["block_page_enabled"])
            check_type(argname="argument block_reason", value=block_reason, expected_type=type_hints["block_reason"])
            check_type(argname="argument bypass_parent_rule", value=bypass_parent_rule, expected_type=type_hints["bypass_parent_rule"])
            check_type(argname="argument check_session", value=check_session, expected_type=type_hints["check_session"])
            check_type(argname="argument dns_resolvers", value=dns_resolvers, expected_type=type_hints["dns_resolvers"])
            check_type(argname="argument egress", value=egress, expected_type=type_hints["egress"])
            check_type(argname="argument ignore_cname_category_matches", value=ignore_cname_category_matches, expected_type=type_hints["ignore_cname_category_matches"])
            check_type(argname="argument insecure_disable_dnssec_validation", value=insecure_disable_dnssec_validation, expected_type=type_hints["insecure_disable_dnssec_validation"])
            check_type(argname="argument ip_categories", value=ip_categories, expected_type=type_hints["ip_categories"])
            check_type(argname="argument ip_indicator_feeds", value=ip_indicator_feeds, expected_type=type_hints["ip_indicator_feeds"])
            check_type(argname="argument l4_override", value=l4_override, expected_type=type_hints["l4_override"])
            check_type(argname="argument notification_settings", value=notification_settings, expected_type=type_hints["notification_settings"])
            check_type(argname="argument override_host", value=override_host, expected_type=type_hints["override_host"])
            check_type(argname="argument override_ips", value=override_ips, expected_type=type_hints["override_ips"])
            check_type(argname="argument payload_log", value=payload_log, expected_type=type_hints["payload_log"])
            check_type(argname="argument quarantine", value=quarantine, expected_type=type_hints["quarantine"])
            check_type(argname="argument redirect", value=redirect, expected_type=type_hints["redirect"])
            check_type(argname="argument resolve_dns_internally", value=resolve_dns_internally, expected_type=type_hints["resolve_dns_internally"])
            check_type(argname="argument resolve_dns_through_cloudflare", value=resolve_dns_through_cloudflare, expected_type=type_hints["resolve_dns_through_cloudflare"])
            check_type(argname="argument untrusted_cert", value=untrusted_cert, expected_type=type_hints["untrusted_cert"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if add_headers is not None:
            self._values["add_headers"] = add_headers
        if allow_child_bypass is not None:
            self._values["allow_child_bypass"] = allow_child_bypass
        if audit_ssh is not None:
            self._values["audit_ssh"] = audit_ssh
        if biso_admin_controls is not None:
            self._values["biso_admin_controls"] = biso_admin_controls
        if block_page is not None:
            self._values["block_page"] = block_page
        if block_page_enabled is not None:
            self._values["block_page_enabled"] = block_page_enabled
        if block_reason is not None:
            self._values["block_reason"] = block_reason
        if bypass_parent_rule is not None:
            self._values["bypass_parent_rule"] = bypass_parent_rule
        if check_session is not None:
            self._values["check_session"] = check_session
        if dns_resolvers is not None:
            self._values["dns_resolvers"] = dns_resolvers
        if egress is not None:
            self._values["egress"] = egress
        if ignore_cname_category_matches is not None:
            self._values["ignore_cname_category_matches"] = ignore_cname_category_matches
        if insecure_disable_dnssec_validation is not None:
            self._values["insecure_disable_dnssec_validation"] = insecure_disable_dnssec_validation
        if ip_categories is not None:
            self._values["ip_categories"] = ip_categories
        if ip_indicator_feeds is not None:
            self._values["ip_indicator_feeds"] = ip_indicator_feeds
        if l4_override is not None:
            self._values["l4_override"] = l4_override
        if notification_settings is not None:
            self._values["notification_settings"] = notification_settings
        if override_host is not None:
            self._values["override_host"] = override_host
        if override_ips is not None:
            self._values["override_ips"] = override_ips
        if payload_log is not None:
            self._values["payload_log"] = payload_log
        if quarantine is not None:
            self._values["quarantine"] = quarantine
        if redirect is not None:
            self._values["redirect"] = redirect
        if resolve_dns_internally is not None:
            self._values["resolve_dns_internally"] = resolve_dns_internally
        if resolve_dns_through_cloudflare is not None:
            self._values["resolve_dns_through_cloudflare"] = resolve_dns_through_cloudflare
        if untrusted_cert is not None:
            self._values["untrusted_cert"] = untrusted_cert

    @builtins.property
    def add_headers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''Add custom headers to allowed requests, in the form of key-value pairs.

        Keys are header names, pointing to an array with its header value(s).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#add_headers ZeroTrustGatewayPolicy#add_headers}
        '''
        result = self._values.get("add_headers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def allow_child_bypass(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set by parent MSP accounts to enable their children to bypass this rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#allow_child_bypass ZeroTrustGatewayPolicy#allow_child_bypass}
        '''
        result = self._values.get("allow_child_bypass")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def audit_ssh(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsAuditSsh"]:
        '''Settings for the Audit SSH action.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#audit_ssh ZeroTrustGatewayPolicy#audit_ssh}
        '''
        result = self._values.get("audit_ssh")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsAuditSsh"], result)

    @builtins.property
    def biso_admin_controls(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls"]:
        '''Configure how browser isolation behaves.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#biso_admin_controls ZeroTrustGatewayPolicy#biso_admin_controls}
        '''
        result = self._values.get("biso_admin_controls")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls"], result)

    @builtins.property
    def block_page(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsBlockPage"]:
        '''Custom block page settings. If missing/null, blocking will use the the account settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#block_page ZeroTrustGatewayPolicy#block_page}
        '''
        result = self._values.get("block_page")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsBlockPage"], result)

    @builtins.property
    def block_page_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the custom block page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#block_page_enabled ZeroTrustGatewayPolicy#block_page_enabled}
        '''
        result = self._values.get("block_page_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def block_reason(self) -> typing.Optional[builtins.str]:
        '''The text describing why this block occurred, displayed on the custom block page (if enabled).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#block_reason ZeroTrustGatewayPolicy#block_reason}
        '''
        result = self._values.get("block_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bypass_parent_rule(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set by children MSP accounts to bypass their parent's rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#bypass_parent_rule ZeroTrustGatewayPolicy#bypass_parent_rule}
        '''
        result = self._values.get("bypass_parent_rule")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def check_session(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsCheckSession"]:
        '''Configure how session check behaves.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#check_session ZeroTrustGatewayPolicy#check_session}
        '''
        result = self._values.get("check_session")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsCheckSession"], result)

    @builtins.property
    def dns_resolvers(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsDnsResolvers"]:
        '''Add your own custom resolvers to route queries that match the resolver policy.

        Cannot be used when 'resolve_dns_through_cloudflare' or 'resolve_dns_internally' are set. DNS queries will route to the address closest to their origin. Only valid when a rule's action is set to 'resolve'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dns_resolvers ZeroTrustGatewayPolicy#dns_resolvers}
        '''
        result = self._values.get("dns_resolvers")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsDnsResolvers"], result)

    @builtins.property
    def egress(self) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsEgress"]:
        '''Configure how Gateway Proxy traffic egresses.

        You can enable this setting for rules with Egress actions and filters, or omit it to indicate local egress via WARP IPs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#egress ZeroTrustGatewayPolicy#egress}
        '''
        result = self._values.get("egress")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsEgress"], result)

    @builtins.property
    def ignore_cname_category_matches(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true, to ignore the category matches at CNAME domains in a response.

        If unchecked, the categories in this rule will be checked against all the CNAME domain categories in a response.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ignore_cname_category_matches ZeroTrustGatewayPolicy#ignore_cname_category_matches}
        '''
        result = self._values.get("ignore_cname_category_matches")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def insecure_disable_dnssec_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''INSECURE - disable DNSSEC validation (for Allow actions).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#insecure_disable_dnssec_validation ZeroTrustGatewayPolicy#insecure_disable_dnssec_validation}
        '''
        result = self._values.get("insecure_disable_dnssec_validation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ip_categories(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to enable IPs in DNS resolver category blocks.

        By default categories only block based on domain names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip_categories ZeroTrustGatewayPolicy#ip_categories}
        '''
        result = self._values.get("ip_categories")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ip_indicator_feeds(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to include IPs in DNS resolver indicator feed blocks.

        By default indicator feeds only block based on domain names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip_indicator_feeds ZeroTrustGatewayPolicy#ip_indicator_feeds}
        '''
        result = self._values.get("ip_indicator_feeds")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def l4_override(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsL4Override"]:
        '''Send matching traffic to the supplied destination IP address. and port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#l4override ZeroTrustGatewayPolicy#l4override}
        '''
        result = self._values.get("l4_override")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsL4Override"], result)

    @builtins.property
    def notification_settings(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsNotificationSettings"]:
        '''Configure a notification to display on the user's device when this rule is matched.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#notification_settings ZeroTrustGatewayPolicy#notification_settings}
        '''
        result = self._values.get("notification_settings")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsNotificationSettings"], result)

    @builtins.property
    def override_host(self) -> typing.Optional[builtins.str]:
        '''Override matching DNS queries with a hostname.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#override_host ZeroTrustGatewayPolicy#override_host}
        '''
        result = self._values.get("override_host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def override_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Override matching DNS queries with an IP or set of IPs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#override_ips ZeroTrustGatewayPolicy#override_ips}
        '''
        result = self._values.get("override_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def payload_log(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsPayloadLog"]:
        '''Configure DLP payload logging.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#payload_log ZeroTrustGatewayPolicy#payload_log}
        '''
        result = self._values.get("payload_log")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsPayloadLog"], result)

    @builtins.property
    def quarantine(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsQuarantine"]:
        '''Settings that apply to quarantine rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#quarantine ZeroTrustGatewayPolicy#quarantine}
        '''
        result = self._values.get("quarantine")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsQuarantine"], result)

    @builtins.property
    def redirect(self) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsRedirect"]:
        '''Settings that apply to redirect rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#redirect ZeroTrustGatewayPolicy#redirect}
        '''
        result = self._values.get("redirect")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsRedirect"], result)

    @builtins.property
    def resolve_dns_internally(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally"]:
        '''Configure to forward the query to the internal DNS service, passing the specified 'view_id' as input.

        Cannot be set when 'dns_resolvers' are specified or 'resolve_dns_through_cloudflare' is set. Only valid when a rule's action is set to 'resolve'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#resolve_dns_internally ZeroTrustGatewayPolicy#resolve_dns_internally}
        '''
        result = self._values.get("resolve_dns_internally")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally"], result)

    @builtins.property
    def resolve_dns_through_cloudflare(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable to send queries that match the policy to Cloudflare's default 1.1.1.1 DNS resolver. Cannot be set when 'dns_resolvers' are specified or 'resolve_dns_internally' is set. Only valid when a rule's action is set to 'resolve'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#resolve_dns_through_cloudflare ZeroTrustGatewayPolicy#resolve_dns_through_cloudflare}
        '''
        result = self._values.get("resolve_dns_through_cloudflare")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def untrusted_cert(
        self,
    ) -> typing.Optional["ZeroTrustGatewayPolicyRuleSettingsUntrustedCert"]:
        '''Configure behavior when an upstream cert is invalid or an SSL error occurs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#untrusted_cert ZeroTrustGatewayPolicy#untrusted_cert}
        '''
        result = self._values.get("untrusted_cert")
        return typing.cast(typing.Optional["ZeroTrustGatewayPolicyRuleSettingsUntrustedCert"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsAuditSsh",
    jsii_struct_bases=[],
    name_mapping={"command_logging": "commandLogging"},
)
class ZeroTrustGatewayPolicyRuleSettingsAuditSsh:
    def __init__(
        self,
        *,
        command_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param command_logging: Enable to turn on SSH command logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#command_logging ZeroTrustGatewayPolicy#command_logging}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e13806ef402ec94ed21dd8e335b31ece45f371213e9bd91cd4f83a977b851a3)
            check_type(argname="argument command_logging", value=command_logging, expected_type=type_hints["command_logging"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if command_logging is not None:
            self._values["command_logging"] = command_logging

    @builtins.property
    def command_logging(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable to turn on SSH command logging.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#command_logging ZeroTrustGatewayPolicy#command_logging}
        '''
        result = self._values.get("command_logging")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsAuditSsh(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7cbe1aad2274aab866344e2e4178aa08f6f0894258b0a1d57502ac56a236f45)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCommandLogging")
    def reset_command_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommandLogging", []))

    @builtins.property
    @jsii.member(jsii_name="commandLoggingInput")
    def command_logging_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "commandLoggingInput"))

    @builtins.property
    @jsii.member(jsii_name="commandLogging")
    def command_logging(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "commandLogging"))

    @command_logging.setter
    def command_logging(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e9da99cbe034882dfcd29f81babcb2a2c1f9170d681b8bdcfdf43385b072238)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commandLogging", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsAuditSsh]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsAuditSsh]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsAuditSsh]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f5fc353cec0452da1882b51e0644b7d85e988ab68deb41c5016c972fb20c440)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls",
    jsii_struct_bases=[],
    name_mapping={
        "copy": "copy",
        "dcp": "dcp",
        "dd": "dd",
        "dk": "dk",
        "download": "download",
        "dp": "dp",
        "du": "du",
        "keyboard": "keyboard",
        "paste": "paste",
        "printing": "printing",
        "upload": "upload",
        "version": "version",
    },
)
class ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls:
    def __init__(
        self,
        *,
        copy: typing.Optional[builtins.str] = None,
        dcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dd: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[builtins.str] = None,
        dp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        du: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        keyboard: typing.Optional[builtins.str] = None,
        paste: typing.Optional[builtins.str] = None,
        printing: typing.Optional[builtins.str] = None,
        upload: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param copy: Configure whether copy is enabled or not. When set with "remote_only", copying isolated content from the remote browser to the user's local clipboard is disabled. When absent, copy is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled", "remote_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#copy ZeroTrustGatewayPolicy#copy}
        :param dcp: Set to false to enable copy-pasting. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dcp ZeroTrustGatewayPolicy#dcp}
        :param dd: Set to false to enable downloading. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dd ZeroTrustGatewayPolicy#dd}
        :param dk: Set to false to enable keyboard usage. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dk ZeroTrustGatewayPolicy#dk}
        :param download: Configure whether downloading enabled or not. When set with "remote_only", downloads are only available for viewing. Only applies when ``version == "v2"``. Available values: "enabled", "disabled", "remote_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#download ZeroTrustGatewayPolicy#download}
        :param dp: Set to false to enable printing. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dp ZeroTrustGatewayPolicy#dp}
        :param du: Set to false to enable uploading. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#du ZeroTrustGatewayPolicy#du}
        :param keyboard: Configure whether keyboard usage is enabled or not. When absent, keyboard usage is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#keyboard ZeroTrustGatewayPolicy#keyboard}
        :param paste: Configure whether pasting is enabled or not. When set with "remote_only", pasting content from the user's local clipboard into isolated pages is disabled. When absent, paste is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled", "remote_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#paste ZeroTrustGatewayPolicy#paste}
        :param printing: Configure whether printing is enabled or not. When absent, printing is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#printing ZeroTrustGatewayPolicy#printing}
        :param upload: Configure whether uploading is enabled or not. When absent, uploading is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#upload ZeroTrustGatewayPolicy#upload}
        :param version: Indicates which version of the browser isolation controls should apply. Available values: "v1", "v2". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#version ZeroTrustGatewayPolicy#version}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fd65a816aca7befaa772d1c5d0ecc9d1f288ab4e81f1ffdade3c911a0b13b14)
            check_type(argname="argument copy", value=copy, expected_type=type_hints["copy"])
            check_type(argname="argument dcp", value=dcp, expected_type=type_hints["dcp"])
            check_type(argname="argument dd", value=dd, expected_type=type_hints["dd"])
            check_type(argname="argument dk", value=dk, expected_type=type_hints["dk"])
            check_type(argname="argument download", value=download, expected_type=type_hints["download"])
            check_type(argname="argument dp", value=dp, expected_type=type_hints["dp"])
            check_type(argname="argument du", value=du, expected_type=type_hints["du"])
            check_type(argname="argument keyboard", value=keyboard, expected_type=type_hints["keyboard"])
            check_type(argname="argument paste", value=paste, expected_type=type_hints["paste"])
            check_type(argname="argument printing", value=printing, expected_type=type_hints["printing"])
            check_type(argname="argument upload", value=upload, expected_type=type_hints["upload"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if copy is not None:
            self._values["copy"] = copy
        if dcp is not None:
            self._values["dcp"] = dcp
        if dd is not None:
            self._values["dd"] = dd
        if dk is not None:
            self._values["dk"] = dk
        if download is not None:
            self._values["download"] = download
        if dp is not None:
            self._values["dp"] = dp
        if du is not None:
            self._values["du"] = du
        if keyboard is not None:
            self._values["keyboard"] = keyboard
        if paste is not None:
            self._values["paste"] = paste
        if printing is not None:
            self._values["printing"] = printing
        if upload is not None:
            self._values["upload"] = upload
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def copy(self) -> typing.Optional[builtins.str]:
        '''Configure whether copy is enabled or not.

        When set with "remote_only", copying isolated content from the remote browser to the user's local clipboard is disabled. When absent, copy is enabled. Only applies when ``version == "v2"``.
        Available values: "enabled", "disabled", "remote_only".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#copy ZeroTrustGatewayPolicy#copy}
        '''
        result = self._values.get("copy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dcp(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to false to enable copy-pasting. Only applies when ``version == "v1"``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dcp ZeroTrustGatewayPolicy#dcp}
        '''
        result = self._values.get("dcp")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dd(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to false to enable downloading. Only applies when ``version == "v1"``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dd ZeroTrustGatewayPolicy#dd}
        '''
        result = self._values.get("dd")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dk(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to false to enable keyboard usage. Only applies when ``version == "v1"``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dk ZeroTrustGatewayPolicy#dk}
        '''
        result = self._values.get("dk")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def download(self) -> typing.Optional[builtins.str]:
        '''Configure whether downloading enabled or not.

        When set with "remote_only", downloads are only available for viewing. Only applies when ``version == "v2"``.
        Available values: "enabled", "disabled", "remote_only".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#download ZeroTrustGatewayPolicy#download}
        '''
        result = self._values.get("download")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dp(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to false to enable printing. Only applies when ``version == "v1"``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dp ZeroTrustGatewayPolicy#dp}
        '''
        result = self._values.get("dp")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def du(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to false to enable uploading. Only applies when ``version == "v1"``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#du ZeroTrustGatewayPolicy#du}
        '''
        result = self._values.get("du")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def keyboard(self) -> typing.Optional[builtins.str]:
        '''Configure whether keyboard usage is enabled or not.

        When absent, keyboard usage is enabled. Only applies when ``version == "v2"``.
        Available values: "enabled", "disabled".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#keyboard ZeroTrustGatewayPolicy#keyboard}
        '''
        result = self._values.get("keyboard")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def paste(self) -> typing.Optional[builtins.str]:
        '''Configure whether pasting is enabled or not.

        When set with "remote_only", pasting content from the user's local clipboard into isolated pages is disabled. When absent, paste is enabled. Only applies when ``version == "v2"``.
        Available values: "enabled", "disabled", "remote_only".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#paste ZeroTrustGatewayPolicy#paste}
        '''
        result = self._values.get("paste")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def printing(self) -> typing.Optional[builtins.str]:
        '''Configure whether printing is enabled or not.

        When absent, printing is enabled. Only applies when ``version == "v2"``.
        Available values: "enabled", "disabled".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#printing ZeroTrustGatewayPolicy#printing}
        '''
        result = self._values.get("printing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def upload(self) -> typing.Optional[builtins.str]:
        '''Configure whether uploading is enabled or not.

        When absent, uploading is enabled. Only applies when ``version == "v2"``.
        Available values: "enabled", "disabled".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#upload ZeroTrustGatewayPolicy#upload}
        '''
        result = self._values.get("upload")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Indicates which version of the browser isolation controls should apply. Available values: "v1", "v2".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#version ZeroTrustGatewayPolicy#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e487688fb41ca3eaba6906db9cc86e97d2f8b3c4b56ad97fcb47b4ac4a290d93)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCopy")
    def reset_copy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopy", []))

    @jsii.member(jsii_name="resetDcp")
    def reset_dcp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDcp", []))

    @jsii.member(jsii_name="resetDd")
    def reset_dd(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDd", []))

    @jsii.member(jsii_name="resetDk")
    def reset_dk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDk", []))

    @jsii.member(jsii_name="resetDownload")
    def reset_download(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDownload", []))

    @jsii.member(jsii_name="resetDp")
    def reset_dp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDp", []))

    @jsii.member(jsii_name="resetDu")
    def reset_du(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDu", []))

    @jsii.member(jsii_name="resetKeyboard")
    def reset_keyboard(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyboard", []))

    @jsii.member(jsii_name="resetPaste")
    def reset_paste(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPaste", []))

    @jsii.member(jsii_name="resetPrinting")
    def reset_printing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrinting", []))

    @jsii.member(jsii_name="resetUpload")
    def reset_upload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpload", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property
    @jsii.member(jsii_name="copyInput")
    def copy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyInput"))

    @builtins.property
    @jsii.member(jsii_name="dcpInput")
    def dcp_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dcpInput"))

    @builtins.property
    @jsii.member(jsii_name="ddInput")
    def dd_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ddInput"))

    @builtins.property
    @jsii.member(jsii_name="dkInput")
    def dk_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dkInput"))

    @builtins.property
    @jsii.member(jsii_name="downloadInput")
    def download_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "downloadInput"))

    @builtins.property
    @jsii.member(jsii_name="dpInput")
    def dp_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dpInput"))

    @builtins.property
    @jsii.member(jsii_name="duInput")
    def du_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "duInput"))

    @builtins.property
    @jsii.member(jsii_name="keyboardInput")
    def keyboard_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyboardInput"))

    @builtins.property
    @jsii.member(jsii_name="pasteInput")
    def paste_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pasteInput"))

    @builtins.property
    @jsii.member(jsii_name="printingInput")
    def printing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "printingInput"))

    @builtins.property
    @jsii.member(jsii_name="uploadInput")
    def upload_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uploadInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="copy")
    def copy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copy"))

    @copy.setter
    def copy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__847e3266c339f242561bab36b9a127e98d78563625e6c532c3f51fd30069bdfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "copy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dcp")
    def dcp(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dcp"))

    @dcp.setter
    def dcp(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__264d6acc8cc77cb9a29bf5d3bca13e3646a9de80271af961d75c8520f3629f58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dcp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dd")
    def dd(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dd"))

    @dd.setter
    def dd(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ee0f17f2cd11bf1a250092ce145d5e79ab393299d65a8706ca616d56b920655)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dd", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dk")
    def dk(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dk"))

    @dk.setter
    def dk(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c5edf013cf0cfbe0cca5e429d20c3df97c1d2f794e73bd5d940a107b4d453dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "download"))

    @download.setter
    def download(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc80e10e9fa19e95eec091b3618e843ad611828178978d4763a289ac6426f4eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "download", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dp")
    def dp(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dp"))

    @dp.setter
    def dp(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d21870a1ccb9a308ffaef2e102f2faba77562fc15d375bee975eba9a246f7e00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="du")
    def du(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "du"))

    @du.setter
    def du(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89fee6ac0a0cc34d094468baeee53248b29bbc6b4dafdd2bf79e0f1900af59f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "du", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyboard")
    def keyboard(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyboard"))

    @keyboard.setter
    def keyboard(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6374e94307d57e43c0ac67c0858375ca82eae0e986e4cc92d4defe244a06ce3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyboard", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="paste")
    def paste(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "paste"))

    @paste.setter
    def paste(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffc1f7f453c402a0aa874558556f56aa275fbcd1783f012e03c5e95d9d702df5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "paste", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="printing")
    def printing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "printing"))

    @printing.setter
    def printing(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a93839565865f32a568de6c6e02c7a8a72c86935c4fc597a9a9e6a01fa83fecb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "printing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="upload")
    def upload(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "upload"))

    @upload.setter
    def upload(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92fc6cb26b207b7cf8331a3e49388a9560f205745c7cf1b20e05969d7f5fa793)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "upload", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4690a0a29a87ddf078dfd55099392f0d402bbb99e1b25b405bd45cd70cb5a144)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b16262088665bd23c4414f6ce9e1ef921a03111175eb5160228b5b8cbdb35cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsBlockPage",
    jsii_struct_bases=[],
    name_mapping={"target_uri": "targetUri", "include_context": "includeContext"},
)
class ZeroTrustGatewayPolicyRuleSettingsBlockPage:
    def __init__(
        self,
        *,
        target_uri: builtins.str,
        include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param target_uri: URI to which the user will be redirected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#target_uri ZeroTrustGatewayPolicy#target_uri}
        :param include_context: If true, context information will be passed as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#include_context ZeroTrustGatewayPolicy#include_context}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9fb9d94740379040849ad9c6520fb4dd017f7f54c36906c06fad8f870a2d98e)
            check_type(argname="argument target_uri", value=target_uri, expected_type=type_hints["target_uri"])
            check_type(argname="argument include_context", value=include_context, expected_type=type_hints["include_context"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target_uri": target_uri,
        }
        if include_context is not None:
            self._values["include_context"] = include_context

    @builtins.property
    def target_uri(self) -> builtins.str:
        '''URI to which the user will be redirected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#target_uri ZeroTrustGatewayPolicy#target_uri}
        '''
        result = self._values.get("target_uri")
        assert result is not None, "Required property 'target_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def include_context(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, context information will be passed as query parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#include_context ZeroTrustGatewayPolicy#include_context}
        '''
        result = self._values.get("include_context")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsBlockPage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__abf8985c3a0d36fee6d72818af6af8191daccacff470b7ce4c76b71c0abc2e60)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIncludeContext")
    def reset_include_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeContext", []))

    @builtins.property
    @jsii.member(jsii_name="includeContextInput")
    def include_context_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "includeContextInput"))

    @builtins.property
    @jsii.member(jsii_name="targetUriInput")
    def target_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetUriInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__643efd4d4715e0e44f722ba2a63c73c421fee488a6d3ca0ba8da7409708b7439)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeContext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetUri")
    def target_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetUri"))

    @target_uri.setter
    def target_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d81f95b03c49167f5c7f070994f82470c7aa380b01fd57029028d8ee2f08dfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetUri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBlockPage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBlockPage]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBlockPage]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0924b10f56d0b14df3284cf60625f495175ec98ac50f5abb71761de13d850b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsCheckSession",
    jsii_struct_bases=[],
    name_mapping={"duration": "duration", "enforce": "enforce"},
)
class ZeroTrustGatewayPolicyRuleSettingsCheckSession:
    def __init__(
        self,
        *,
        duration: typing.Optional[builtins.str] = None,
        enforce: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param duration: Configure how fresh the session needs to be to be considered valid. The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#duration ZeroTrustGatewayPolicy#duration}
        :param enforce: Set to true to enable session enforcement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enforce ZeroTrustGatewayPolicy#enforce}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56199ee2205a76f737af972538e10f89fe9b1ad3b1ae437325cab49c99f6877b)
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
            check_type(argname="argument enforce", value=enforce, expected_type=type_hints["enforce"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if duration is not None:
            self._values["duration"] = duration
        if enforce is not None:
            self._values["enforce"] = enforce

    @builtins.property
    def duration(self) -> typing.Optional[builtins.str]:
        '''Configure how fresh the session needs to be to be considered valid.

        The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#duration ZeroTrustGatewayPolicy#duration}
        '''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enforce(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to enable session enforcement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enforce ZeroTrustGatewayPolicy#enforce}
        '''
        result = self._values.get("enforce")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsCheckSession(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64e808649dd9d4901863979bb24d8623d67310b6fc114de70bc108fa8480a248)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDuration")
    def reset_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDuration", []))

    @jsii.member(jsii_name="resetEnforce")
    def reset_enforce(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforce", []))

    @builtins.property
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "durationInput"))

    @builtins.property
    @jsii.member(jsii_name="enforceInput")
    def enforce_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enforceInput"))

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33b8a53e3936669c3400cdac4a0dcaa9df95fde0f9b01f93cddf02a0f6de668b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enforce")
    def enforce(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enforce"))

    @enforce.setter
    def enforce(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__704639372dcc580a04c74d5c5fb881b8f14087b8aad093f31515ad4d3b70b1b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforce", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsCheckSession]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsCheckSession]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsCheckSession]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7cea6cb3a0aa5166676514ff8fe2f424ad1b786908f73d5bd1b9cc8d02add24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsDnsResolvers",
    jsii_struct_bases=[],
    name_mapping={"ipv4": "ipv4", "ipv6": "ipv6"},
)
class ZeroTrustGatewayPolicyRuleSettingsDnsResolvers:
    def __init__(
        self,
        *,
        ipv4: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4", typing.Dict[builtins.str, typing.Any]]]]] = None,
        ipv6: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param ipv4: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv4 ZeroTrustGatewayPolicy#ipv4}.
        :param ipv6: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv6 ZeroTrustGatewayPolicy#ipv6}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e61e86bdabb946d2d3a72397fbab37eed75de1962c303d02d391da06329eb2b1)
            check_type(argname="argument ipv4", value=ipv4, expected_type=type_hints["ipv4"])
            check_type(argname="argument ipv6", value=ipv6, expected_type=type_hints["ipv6"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ipv4 is not None:
            self._values["ipv4"] = ipv4
        if ipv6 is not None:
            self._values["ipv6"] = ipv6

    @builtins.property
    def ipv4(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv4 ZeroTrustGatewayPolicy#ipv4}.'''
        result = self._values.get("ipv4")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4"]]], result)

    @builtins.property
    def ipv6(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv6 ZeroTrustGatewayPolicy#ipv6}.'''
        result = self._values.get("ipv6")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsDnsResolvers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4",
    jsii_struct_bases=[],
    name_mapping={
        "ip": "ip",
        "port": "port",
        "route_through_private_network": "routeThroughPrivateNetwork",
        "vnet_id": "vnetId",
    },
)
class ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4:
    def __init__(
        self,
        *,
        ip: builtins.str,
        port: typing.Optional[jsii.Number] = None,
        route_through_private_network: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vnet_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ip: IPv4 address of upstream resolver. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip ZeroTrustGatewayPolicy#ip}
        :param port: A port number to use for upstream resolver. Defaults to 53 if unspecified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#port ZeroTrustGatewayPolicy#port}
        :param route_through_private_network: Whether to connect to this resolver over a private network. Must be set when vnet_id is set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#route_through_private_network ZeroTrustGatewayPolicy#route_through_private_network}
        :param vnet_id: Optionally specify a virtual network for this resolver. Uses default virtual network id if omitted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#vnet_id ZeroTrustGatewayPolicy#vnet_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c24719bdc3038d165f74ab720bef83026321ba3145104cfaa1c1b20d148cab8)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument route_through_private_network", value=route_through_private_network, expected_type=type_hints["route_through_private_network"])
            check_type(argname="argument vnet_id", value=vnet_id, expected_type=type_hints["vnet_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip": ip,
        }
        if port is not None:
            self._values["port"] = port
        if route_through_private_network is not None:
            self._values["route_through_private_network"] = route_through_private_network
        if vnet_id is not None:
            self._values["vnet_id"] = vnet_id

    @builtins.property
    def ip(self) -> builtins.str:
        '''IPv4 address of upstream resolver.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip ZeroTrustGatewayPolicy#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''A port number to use for upstream resolver. Defaults to 53 if unspecified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#port ZeroTrustGatewayPolicy#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def route_through_private_network(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to connect to this resolver over a private network. Must be set when vnet_id is set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#route_through_private_network ZeroTrustGatewayPolicy#route_through_private_network}
        '''
        result = self._values.get("route_through_private_network")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vnet_id(self) -> typing.Optional[builtins.str]:
        '''Optionally specify a virtual network for this resolver. Uses default virtual network id if omitted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#vnet_id ZeroTrustGatewayPolicy#vnet_id}
        '''
        result = self._values.get("vnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8325a1a409077918c933b460bfcc5f3a826ee186f245ca9839b836c70d772e06)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__533b1bf8395b943248c885e85812eb93b2a774de10422d63612cf28ac14cafaa)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6c2d41d484fcff6d4869072b8c656d8d1637c6d2ded398ea49a1d65dbaebbd2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__89dd7a58248308472bd5468feb92374998e6b7b5590ec736782c3a553637e060)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d71763ee18b7be04bf6a77a7792383688b0cfd8db3c6ed614cd32776113332c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe57289c5a429db420b6145e99ddaaf5ede4dc135885cf66ffa8e5fa4303b979)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__11b79a03168b1f67148b565cda58d26b288c914a1d512954035060c72b5e3d87)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetRouteThroughPrivateNetwork")
    def reset_route_through_private_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteThroughPrivateNetwork", []))

    @jsii.member(jsii_name="resetVnetId")
    def reset_vnet_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVnetId", []))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="routeThroughPrivateNetworkInput")
    def route_through_private_network_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "routeThroughPrivateNetworkInput"))

    @builtins.property
    @jsii.member(jsii_name="vnetIdInput")
    def vnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vnetIdInput"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1fd7414892d1597a66dac08101d741d4f8d59be453c0dea8a8d1338514cb5b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48f65de8183eaebfe0f9215db319b0e90ea52991fb28e72d46082a8ace1646ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeThroughPrivateNetwork")
    def route_through_private_network(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "routeThroughPrivateNetwork"))

    @route_through_private_network.setter
    def route_through_private_network(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4329b10738e673d9049a8ce03c03876d48454709cdddfc3de5497fc5492f8189)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeThroughPrivateNetwork", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vnetId")
    def vnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vnetId"))

    @vnet_id.setter
    def vnet_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4b0d19c27d6fd136e1e0d206878f3628b4675a45ec9fc28cefe607883cb7397)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vnetId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3fe51044e877d271f848c76ef15c1b3e10a340760aa9758e97ea688bc18e0a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6",
    jsii_struct_bases=[],
    name_mapping={
        "ip": "ip",
        "port": "port",
        "route_through_private_network": "routeThroughPrivateNetwork",
        "vnet_id": "vnetId",
    },
)
class ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6:
    def __init__(
        self,
        *,
        ip: builtins.str,
        port: typing.Optional[jsii.Number] = None,
        route_through_private_network: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vnet_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ip: IPv6 address of upstream resolver. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip ZeroTrustGatewayPolicy#ip}
        :param port: A port number to use for upstream resolver. Defaults to 53 if unspecified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#port ZeroTrustGatewayPolicy#port}
        :param route_through_private_network: Whether to connect to this resolver over a private network. Must be set when vnet_id is set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#route_through_private_network ZeroTrustGatewayPolicy#route_through_private_network}
        :param vnet_id: Optionally specify a virtual network for this resolver. Uses default virtual network id if omitted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#vnet_id ZeroTrustGatewayPolicy#vnet_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f85e4dfa7046f3af0deee7ff5a1e3a4b86af348b71fe1af87e2692b77712992)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument route_through_private_network", value=route_through_private_network, expected_type=type_hints["route_through_private_network"])
            check_type(argname="argument vnet_id", value=vnet_id, expected_type=type_hints["vnet_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip": ip,
        }
        if port is not None:
            self._values["port"] = port
        if route_through_private_network is not None:
            self._values["route_through_private_network"] = route_through_private_network
        if vnet_id is not None:
            self._values["vnet_id"] = vnet_id

    @builtins.property
    def ip(self) -> builtins.str:
        '''IPv6 address of upstream resolver.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip ZeroTrustGatewayPolicy#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''A port number to use for upstream resolver. Defaults to 53 if unspecified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#port ZeroTrustGatewayPolicy#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def route_through_private_network(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to connect to this resolver over a private network. Must be set when vnet_id is set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#route_through_private_network ZeroTrustGatewayPolicy#route_through_private_network}
        '''
        result = self._values.get("route_through_private_network")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vnet_id(self) -> typing.Optional[builtins.str]:
        '''Optionally specify a virtual network for this resolver. Uses default virtual network id if omitted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#vnet_id ZeroTrustGatewayPolicy#vnet_id}
        '''
        result = self._values.get("vnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e4bfb32196b3551481e8cca349977d12590376dd4642cc0bc2726152543abe8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc981020efa520611da174b7843290c261f1dc2e2a32ec583c026ee3b10931fb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8407ffb93365f1e2e11b27875a35c4dca52915c0e1f10356b9a1e7ef826cbc4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b6117090d75a8b51dc4d30205a60b06123d6019c3934be55e60967b5f4d56c1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f0a68cd7314b423e0e39a7e15fbd9a1108fa2272438d35e24cb18ade3535045)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a80c31a75c73774f61153c8df8e0968b4f59e3a499f73f0e7f101d5efe967bd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6aefc0967e7ec9bfc17da46922d77545c41748b7953a536aa596d76d466151ba)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetRouteThroughPrivateNetwork")
    def reset_route_through_private_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteThroughPrivateNetwork", []))

    @jsii.member(jsii_name="resetVnetId")
    def reset_vnet_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVnetId", []))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="routeThroughPrivateNetworkInput")
    def route_through_private_network_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "routeThroughPrivateNetworkInput"))

    @builtins.property
    @jsii.member(jsii_name="vnetIdInput")
    def vnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vnetIdInput"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9d1a1427283f10bb887bae9c8c09aa3473bb39bee635cb748cc7bec7288aff2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0988a9d00ba8ce08c0f3fe89efeabad47e3fd9a2817225d945e7d064436329d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeThroughPrivateNetwork")
    def route_through_private_network(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "routeThroughPrivateNetwork"))

    @route_through_private_network.setter
    def route_through_private_network(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8866e5fdf3ff5e525fe793fa1633c72c80b4ba2ef2047c9e8d0446894140b9ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeThroughPrivateNetwork", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vnetId")
    def vnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vnetId"))

    @vnet_id.setter
    def vnet_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f45582a25857306e9cd17c9127b3d076c4693372dd57adbbf473a7705fc42db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vnetId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7bb6c8dd0d7cf527e474f84d5a925a39708320a10e08bdafbc5a00915848a41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bfe77d83fd907f5544880a4f430e59c13a1392f63bd7abfafdef6f884393e209)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putIpv4")
    def put_ipv4(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b669ea23d8599a8644f7eeadecdb0f6bdc876d012383fbd95625edd251989a36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putIpv4", [value]))

    @jsii.member(jsii_name="putIpv6")
    def put_ipv6(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9dc0db711eacec9887cafb44e734357f3d89b9fb5f4d297e2f7ca1f2c366bd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putIpv6", [value]))

    @jsii.member(jsii_name="resetIpv4")
    def reset_ipv4(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4", []))

    @jsii.member(jsii_name="resetIpv6")
    def reset_ipv6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6", []))

    @builtins.property
    @jsii.member(jsii_name="ipv4")
    def ipv4(self) -> ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List, jsii.get(self, "ipv4"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List, jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="ipv4Input")
    def ipv4_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]]], jsii.get(self, "ipv4Input"))

    @builtins.property
    @jsii.member(jsii_name="ipv6Input")
    def ipv6_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]]], jsii.get(self, "ipv6Input"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolvers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolvers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolvers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__298b64663e24f0ea5c0535778501a4f36f10bbaead2fca81e35f69674e0c9d84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsEgress",
    jsii_struct_bases=[],
    name_mapping={"ipv4": "ipv4", "ipv4_fallback": "ipv4Fallback", "ipv6": "ipv6"},
)
class ZeroTrustGatewayPolicyRuleSettingsEgress:
    def __init__(
        self,
        *,
        ipv4: typing.Optional[builtins.str] = None,
        ipv4_fallback: typing.Optional[builtins.str] = None,
        ipv6: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ipv4: The IPv4 address to be used for egress. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv4 ZeroTrustGatewayPolicy#ipv4}
        :param ipv4_fallback: The fallback IPv4 address to be used for egress in the event of an error egressing with the primary IPv4. Can be '0.0.0.0' to indicate local egress via WARP IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv4_fallback ZeroTrustGatewayPolicy#ipv4_fallback}
        :param ipv6: The IPv6 range to be used for egress. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv6 ZeroTrustGatewayPolicy#ipv6}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54c20c20790982b1f4876312fe70df67926222adacb75525c029e94887d98091)
            check_type(argname="argument ipv4", value=ipv4, expected_type=type_hints["ipv4"])
            check_type(argname="argument ipv4_fallback", value=ipv4_fallback, expected_type=type_hints["ipv4_fallback"])
            check_type(argname="argument ipv6", value=ipv6, expected_type=type_hints["ipv6"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ipv4 is not None:
            self._values["ipv4"] = ipv4
        if ipv4_fallback is not None:
            self._values["ipv4_fallback"] = ipv4_fallback
        if ipv6 is not None:
            self._values["ipv6"] = ipv6

    @builtins.property
    def ipv4(self) -> typing.Optional[builtins.str]:
        '''The IPv4 address to be used for egress.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv4 ZeroTrustGatewayPolicy#ipv4}
        '''
        result = self._values.get("ipv4")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv4_fallback(self) -> typing.Optional[builtins.str]:
        '''The fallback IPv4 address to be used for egress in the event of an error egressing with the primary IPv4.

        Can be '0.0.0.0' to indicate local egress via WARP IPs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv4_fallback ZeroTrustGatewayPolicy#ipv4_fallback}
        '''
        result = self._values.get("ipv4_fallback")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6(self) -> typing.Optional[builtins.str]:
        '''The IPv6 range to be used for egress.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv6 ZeroTrustGatewayPolicy#ipv6}
        '''
        result = self._values.get("ipv6")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsEgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsEgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsEgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0796cb8575c970172d0ce9e0ad3d1e0860b3ab8d36b679e13b1f966c06bade9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIpv4")
    def reset_ipv4(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4", []))

    @jsii.member(jsii_name="resetIpv4Fallback")
    def reset_ipv4_fallback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4Fallback", []))

    @jsii.member(jsii_name="resetIpv6")
    def reset_ipv6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6", []))

    @builtins.property
    @jsii.member(jsii_name="ipv4FallbackInput")
    def ipv4_fallback_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv4FallbackInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv4Input")
    def ipv4_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv4Input"))

    @builtins.property
    @jsii.member(jsii_name="ipv6Input")
    def ipv6_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv6Input"))

    @builtins.property
    @jsii.member(jsii_name="ipv4")
    def ipv4(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4"))

    @ipv4.setter
    def ipv4(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__966af7cdf684fe3aa938943063e2d7977054accb6cead27577e182dd385c3c7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Fallback")
    def ipv4_fallback(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Fallback"))

    @ipv4_fallback.setter
    def ipv4_fallback(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd6e3514c0230e5012ef0492d45c9d1b43937198b0bd8b5bd65da9a5cc57ee88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Fallback", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6"))

    @ipv6.setter
    def ipv6(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a862b5eb8ce043e340f8e643740e87ed76e3bbe47211aecb9ed70ca4ad785c12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsEgress]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsEgress]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsEgress]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6833a6d490876a271d35b87f147a66acb5deb7685ab224819007c64d0e400263)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsL4Override",
    jsii_struct_bases=[],
    name_mapping={"ip": "ip", "port": "port"},
)
class ZeroTrustGatewayPolicyRuleSettingsL4Override:
    def __init__(
        self,
        *,
        ip: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param ip: IPv4 or IPv6 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip ZeroTrustGatewayPolicy#ip}
        :param port: A port number to use for TCP/UDP overrides. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#port ZeroTrustGatewayPolicy#port}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbef793f0f9dfeabe7b5485433aab6102e162df9a897abc8d4b8aa339fee92ea)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ip is not None:
            self._values["ip"] = ip
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def ip(self) -> typing.Optional[builtins.str]:
        '''IPv4 or IPv6 address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip ZeroTrustGatewayPolicy#ip}
        '''
        result = self._values.get("ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''A port number to use for TCP/UDP overrides.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#port ZeroTrustGatewayPolicy#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsL4Override(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6376ac5fce76140ef3b8fb4f6af9e78a84d144fa24bf3dea6601411840482eb6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIp")
    def reset_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIp", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a062656fb3774493c7ec44c60f40ddae4dcc2ab4ae76d3fac41cfca847cee672)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5059f6a84f9af734199f2419a73019521b0ef42cdde25d33f3848ffa428e0aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsL4Override]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsL4Override]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsL4Override]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6992764ef0e447a8c43336bc9eb62ac1a401718853c978e226e191973c17cb66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsNotificationSettings",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "include_context": "includeContext",
        "msg": "msg",
        "support_url": "supportUrl",
    },
)
class ZeroTrustGatewayPolicyRuleSettingsNotificationSettings:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        msg: typing.Optional[builtins.str] = None,
        support_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Set notification on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enabled ZeroTrustGatewayPolicy#enabled}
        :param include_context: If true, context information will be passed as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#include_context ZeroTrustGatewayPolicy#include_context}
        :param msg: Customize the message shown in the notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#msg ZeroTrustGatewayPolicy#msg}
        :param support_url: Optional URL to direct users to additional information. If not set, the notification will open a block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#support_url ZeroTrustGatewayPolicy#support_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8db5c5eeaf4ff44b629eb99747f03cd75818482acd82211db67f8e37ddf7fc2)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enabled ZeroTrustGatewayPolicy#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def include_context(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, context information will be passed as query parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#include_context ZeroTrustGatewayPolicy#include_context}
        '''
        result = self._values.get("include_context")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def msg(self) -> typing.Optional[builtins.str]:
        '''Customize the message shown in the notification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#msg ZeroTrustGatewayPolicy#msg}
        '''
        result = self._values.get("msg")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def support_url(self) -> typing.Optional[builtins.str]:
        '''Optional URL to direct users to additional information. If not set, the notification will open a block page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#support_url ZeroTrustGatewayPolicy#support_url}
        '''
        result = self._values.get("support_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsNotificationSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__727c90cf4d7e78e845de5b7b5c003c1d7edca7319b28566b450c0738e7d213fc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e07fe27be482df4e82f9d62e5ba477d03b5e5c742909acc39649a932218a327d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__97e07a261b5f0dae0a9dc4c071310288f889a2c94ade0a8e85f3acd49c625170)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeContext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="msg")
    def msg(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "msg"))

    @msg.setter
    def msg(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dc15ee2beaf4b1d8f0d0378d8e4545b004f7c996e8ae82f6b10748aefad695f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "msg", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="supportUrl")
    def support_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "supportUrl"))

    @support_url.setter
    def support_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99fef0f410d5c6360be8db0b53fa52f68d0a745a5d8ac7815daf6cddc788b82e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "supportUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsNotificationSettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsNotificationSettings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsNotificationSettings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6537fcfae534b3c752b2fbe6489d26533be9a49e9425c470c18a6d3d0f036ea7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustGatewayPolicyRuleSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0f1fbdcc6d5b96639588760d6d409fb65e4ee361bc0d52ea6c5e7f0dbd6ada66)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAuditSsh")
    def put_audit_ssh(
        self,
        *,
        command_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param command_logging: Enable to turn on SSH command logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#command_logging ZeroTrustGatewayPolicy#command_logging}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsAuditSsh(
            command_logging=command_logging
        )

        return typing.cast(None, jsii.invoke(self, "putAuditSsh", [value]))

    @jsii.member(jsii_name="putBisoAdminControls")
    def put_biso_admin_controls(
        self,
        *,
        copy: typing.Optional[builtins.str] = None,
        dcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dd: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[builtins.str] = None,
        dp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        du: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        keyboard: typing.Optional[builtins.str] = None,
        paste: typing.Optional[builtins.str] = None,
        printing: typing.Optional[builtins.str] = None,
        upload: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param copy: Configure whether copy is enabled or not. When set with "remote_only", copying isolated content from the remote browser to the user's local clipboard is disabled. When absent, copy is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled", "remote_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#copy ZeroTrustGatewayPolicy#copy}
        :param dcp: Set to false to enable copy-pasting. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dcp ZeroTrustGatewayPolicy#dcp}
        :param dd: Set to false to enable downloading. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dd ZeroTrustGatewayPolicy#dd}
        :param dk: Set to false to enable keyboard usage. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dk ZeroTrustGatewayPolicy#dk}
        :param download: Configure whether downloading enabled or not. When set with "remote_only", downloads are only available for viewing. Only applies when ``version == "v2"``. Available values: "enabled", "disabled", "remote_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#download ZeroTrustGatewayPolicy#download}
        :param dp: Set to false to enable printing. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#dp ZeroTrustGatewayPolicy#dp}
        :param du: Set to false to enable uploading. Only applies when ``version == "v1"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#du ZeroTrustGatewayPolicy#du}
        :param keyboard: Configure whether keyboard usage is enabled or not. When absent, keyboard usage is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#keyboard ZeroTrustGatewayPolicy#keyboard}
        :param paste: Configure whether pasting is enabled or not. When set with "remote_only", pasting content from the user's local clipboard into isolated pages is disabled. When absent, paste is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled", "remote_only". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#paste ZeroTrustGatewayPolicy#paste}
        :param printing: Configure whether printing is enabled or not. When absent, printing is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#printing ZeroTrustGatewayPolicy#printing}
        :param upload: Configure whether uploading is enabled or not. When absent, uploading is enabled. Only applies when ``version == "v2"``. Available values: "enabled", "disabled". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#upload ZeroTrustGatewayPolicy#upload}
        :param version: Indicates which version of the browser isolation controls should apply. Available values: "v1", "v2". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#version ZeroTrustGatewayPolicy#version}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls(
            copy=copy,
            dcp=dcp,
            dd=dd,
            dk=dk,
            download=download,
            dp=dp,
            du=du,
            keyboard=keyboard,
            paste=paste,
            printing=printing,
            upload=upload,
            version=version,
        )

        return typing.cast(None, jsii.invoke(self, "putBisoAdminControls", [value]))

    @jsii.member(jsii_name="putBlockPage")
    def put_block_page(
        self,
        *,
        target_uri: builtins.str,
        include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param target_uri: URI to which the user will be redirected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#target_uri ZeroTrustGatewayPolicy#target_uri}
        :param include_context: If true, context information will be passed as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#include_context ZeroTrustGatewayPolicy#include_context}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsBlockPage(
            target_uri=target_uri, include_context=include_context
        )

        return typing.cast(None, jsii.invoke(self, "putBlockPage", [value]))

    @jsii.member(jsii_name="putCheckSession")
    def put_check_session(
        self,
        *,
        duration: typing.Optional[builtins.str] = None,
        enforce: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param duration: Configure how fresh the session needs to be to be considered valid. The API automatically formats and sanitizes this expression. This returns a normalized version that may differ from your input and cause Terraform state drift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#duration ZeroTrustGatewayPolicy#duration}
        :param enforce: Set to true to enable session enforcement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enforce ZeroTrustGatewayPolicy#enforce}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsCheckSession(
            duration=duration, enforce=enforce
        )

        return typing.cast(None, jsii.invoke(self, "putCheckSession", [value]))

    @jsii.member(jsii_name="putDnsResolvers")
    def put_dns_resolvers(
        self,
        *,
        ipv4: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4, typing.Dict[builtins.str, typing.Any]]]]] = None,
        ipv6: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param ipv4: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv4 ZeroTrustGatewayPolicy#ipv4}.
        :param ipv6: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv6 ZeroTrustGatewayPolicy#ipv6}.
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsDnsResolvers(ipv4=ipv4, ipv6=ipv6)

        return typing.cast(None, jsii.invoke(self, "putDnsResolvers", [value]))

    @jsii.member(jsii_name="putEgress")
    def put_egress(
        self,
        *,
        ipv4: typing.Optional[builtins.str] = None,
        ipv4_fallback: typing.Optional[builtins.str] = None,
        ipv6: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ipv4: The IPv4 address to be used for egress. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv4 ZeroTrustGatewayPolicy#ipv4}
        :param ipv4_fallback: The fallback IPv4 address to be used for egress in the event of an error egressing with the primary IPv4. Can be '0.0.0.0' to indicate local egress via WARP IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv4_fallback ZeroTrustGatewayPolicy#ipv4_fallback}
        :param ipv6: The IPv6 range to be used for egress. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ipv6 ZeroTrustGatewayPolicy#ipv6}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsEgress(
            ipv4=ipv4, ipv4_fallback=ipv4_fallback, ipv6=ipv6
        )

        return typing.cast(None, jsii.invoke(self, "putEgress", [value]))

    @jsii.member(jsii_name="putL4Override")
    def put_l4_override(
        self,
        *,
        ip: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param ip: IPv4 or IPv6 address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#ip ZeroTrustGatewayPolicy#ip}
        :param port: A port number to use for TCP/UDP overrides. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#port ZeroTrustGatewayPolicy#port}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsL4Override(ip=ip, port=port)

        return typing.cast(None, jsii.invoke(self, "putL4Override", [value]))

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
        :param enabled: Set notification on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enabled ZeroTrustGatewayPolicy#enabled}
        :param include_context: If true, context information will be passed as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#include_context ZeroTrustGatewayPolicy#include_context}
        :param msg: Customize the message shown in the notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#msg ZeroTrustGatewayPolicy#msg}
        :param support_url: Optional URL to direct users to additional information. If not set, the notification will open a block page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#support_url ZeroTrustGatewayPolicy#support_url}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsNotificationSettings(
            enabled=enabled,
            include_context=include_context,
            msg=msg,
            support_url=support_url,
        )

        return typing.cast(None, jsii.invoke(self, "putNotificationSettings", [value]))

    @jsii.member(jsii_name="putPayloadLog")
    def put_payload_log(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Set to true to enable DLP payload logging for this rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enabled ZeroTrustGatewayPolicy#enabled}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsPayloadLog(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putPayloadLog", [value]))

    @jsii.member(jsii_name="putQuarantine")
    def put_quarantine(
        self,
        *,
        file_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param file_types: Types of files to sandbox. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#file_types ZeroTrustGatewayPolicy#file_types}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsQuarantine(file_types=file_types)

        return typing.cast(None, jsii.invoke(self, "putQuarantine", [value]))

    @jsii.member(jsii_name="putRedirect")
    def put_redirect(
        self,
        *,
        target_uri: builtins.str,
        include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        preserve_path_and_query: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param target_uri: URI to which the user will be redirected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#target_uri ZeroTrustGatewayPolicy#target_uri}
        :param include_context: If true, context information will be passed as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#include_context ZeroTrustGatewayPolicy#include_context}
        :param preserve_path_and_query: If true, the path and query parameters from the original request will be appended to target_uri. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#preserve_path_and_query ZeroTrustGatewayPolicy#preserve_path_and_query}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsRedirect(
            target_uri=target_uri,
            include_context=include_context,
            preserve_path_and_query=preserve_path_and_query,
        )

        return typing.cast(None, jsii.invoke(self, "putRedirect", [value]))

    @jsii.member(jsii_name="putResolveDnsInternally")
    def put_resolve_dns_internally(
        self,
        *,
        fallback: typing.Optional[builtins.str] = None,
        view_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fallback: The fallback behavior to apply when the internal DNS response code is different from 'NOERROR' or when the response data only contains CNAME records for 'A' or 'AAAA' queries. Available values: "none", "public_dns". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#fallback ZeroTrustGatewayPolicy#fallback}
        :param view_id: The internal DNS view identifier that's passed to the internal DNS service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#view_id ZeroTrustGatewayPolicy#view_id}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally(
            fallback=fallback, view_id=view_id
        )

        return typing.cast(None, jsii.invoke(self, "putResolveDnsInternally", [value]))

    @jsii.member(jsii_name="putUntrustedCert")
    def put_untrusted_cert(
        self,
        *,
        action: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action: The action performed when an untrusted certificate is seen. The default action is an error with HTTP code 526. Available values: "pass_through", "block", "error". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#action ZeroTrustGatewayPolicy#action}
        '''
        value = ZeroTrustGatewayPolicyRuleSettingsUntrustedCert(action=action)

        return typing.cast(None, jsii.invoke(self, "putUntrustedCert", [value]))

    @jsii.member(jsii_name="resetAddHeaders")
    def reset_add_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddHeaders", []))

    @jsii.member(jsii_name="resetAllowChildBypass")
    def reset_allow_child_bypass(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowChildBypass", []))

    @jsii.member(jsii_name="resetAuditSsh")
    def reset_audit_ssh(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditSsh", []))

    @jsii.member(jsii_name="resetBisoAdminControls")
    def reset_biso_admin_controls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBisoAdminControls", []))

    @jsii.member(jsii_name="resetBlockPage")
    def reset_block_page(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPage", []))

    @jsii.member(jsii_name="resetBlockPageEnabled")
    def reset_block_page_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPageEnabled", []))

    @jsii.member(jsii_name="resetBlockReason")
    def reset_block_reason(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockReason", []))

    @jsii.member(jsii_name="resetBypassParentRule")
    def reset_bypass_parent_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBypassParentRule", []))

    @jsii.member(jsii_name="resetCheckSession")
    def reset_check_session(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckSession", []))

    @jsii.member(jsii_name="resetDnsResolvers")
    def reset_dns_resolvers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsResolvers", []))

    @jsii.member(jsii_name="resetEgress")
    def reset_egress(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEgress", []))

    @jsii.member(jsii_name="resetIgnoreCnameCategoryMatches")
    def reset_ignore_cname_category_matches(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreCnameCategoryMatches", []))

    @jsii.member(jsii_name="resetInsecureDisableDnssecValidation")
    def reset_insecure_disable_dnssec_validation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureDisableDnssecValidation", []))

    @jsii.member(jsii_name="resetIpCategories")
    def reset_ip_categories(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpCategories", []))

    @jsii.member(jsii_name="resetIpIndicatorFeeds")
    def reset_ip_indicator_feeds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpIndicatorFeeds", []))

    @jsii.member(jsii_name="resetL4Override")
    def reset_l4_override(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetL4Override", []))

    @jsii.member(jsii_name="resetNotificationSettings")
    def reset_notification_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotificationSettings", []))

    @jsii.member(jsii_name="resetOverrideHost")
    def reset_override_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideHost", []))

    @jsii.member(jsii_name="resetOverrideIps")
    def reset_override_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideIps", []))

    @jsii.member(jsii_name="resetPayloadLog")
    def reset_payload_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPayloadLog", []))

    @jsii.member(jsii_name="resetQuarantine")
    def reset_quarantine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuarantine", []))

    @jsii.member(jsii_name="resetRedirect")
    def reset_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirect", []))

    @jsii.member(jsii_name="resetResolveDnsInternally")
    def reset_resolve_dns_internally(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResolveDnsInternally", []))

    @jsii.member(jsii_name="resetResolveDnsThroughCloudflare")
    def reset_resolve_dns_through_cloudflare(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResolveDnsThroughCloudflare", []))

    @jsii.member(jsii_name="resetUntrustedCert")
    def reset_untrusted_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUntrustedCert", []))

    @builtins.property
    @jsii.member(jsii_name="auditSsh")
    def audit_ssh(self) -> ZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference, jsii.get(self, "auditSsh"))

    @builtins.property
    @jsii.member(jsii_name="bisoAdminControls")
    def biso_admin_controls(
        self,
    ) -> ZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference, jsii.get(self, "bisoAdminControls"))

    @builtins.property
    @jsii.member(jsii_name="blockPage")
    def block_page(self) -> ZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference, jsii.get(self, "blockPage"))

    @builtins.property
    @jsii.member(jsii_name="checkSession")
    def check_session(
        self,
    ) -> ZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference, jsii.get(self, "checkSession"))

    @builtins.property
    @jsii.member(jsii_name="dnsResolvers")
    def dns_resolvers(
        self,
    ) -> ZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference, jsii.get(self, "dnsResolvers"))

    @builtins.property
    @jsii.member(jsii_name="egress")
    def egress(self) -> ZeroTrustGatewayPolicyRuleSettingsEgressOutputReference:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsEgressOutputReference, jsii.get(self, "egress"))

    @builtins.property
    @jsii.member(jsii_name="l4Override")
    def l4_override(
        self,
    ) -> ZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference, jsii.get(self, "l4Override"))

    @builtins.property
    @jsii.member(jsii_name="notificationSettings")
    def notification_settings(
        self,
    ) -> ZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference:
        return typing.cast(ZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference, jsii.get(self, "notificationSettings"))

    @builtins.property
    @jsii.member(jsii_name="payloadLog")
    def payload_log(
        self,
    ) -> "ZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference":
        return typing.cast("ZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference", jsii.get(self, "payloadLog"))

    @builtins.property
    @jsii.member(jsii_name="quarantine")
    def quarantine(
        self,
    ) -> "ZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference":
        return typing.cast("ZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference", jsii.get(self, "quarantine"))

    @builtins.property
    @jsii.member(jsii_name="redirect")
    def redirect(self) -> "ZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference":
        return typing.cast("ZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference", jsii.get(self, "redirect"))

    @builtins.property
    @jsii.member(jsii_name="resolveDnsInternally")
    def resolve_dns_internally(
        self,
    ) -> "ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference":
        return typing.cast("ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference", jsii.get(self, "resolveDnsInternally"))

    @builtins.property
    @jsii.member(jsii_name="untrustedCert")
    def untrusted_cert(
        self,
    ) -> "ZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference":
        return typing.cast("ZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference", jsii.get(self, "untrustedCert"))

    @builtins.property
    @jsii.member(jsii_name="addHeadersInput")
    def add_headers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "addHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="allowChildBypassInput")
    def allow_child_bypass_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowChildBypassInput"))

    @builtins.property
    @jsii.member(jsii_name="auditSshInput")
    def audit_ssh_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsAuditSsh]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsAuditSsh]], jsii.get(self, "auditSshInput"))

    @builtins.property
    @jsii.member(jsii_name="bisoAdminControlsInput")
    def biso_admin_controls_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls]], jsii.get(self, "bisoAdminControlsInput"))

    @builtins.property
    @jsii.member(jsii_name="blockPageEnabledInput")
    def block_page_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "blockPageEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="blockPageInput")
    def block_page_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBlockPage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBlockPage]], jsii.get(self, "blockPageInput"))

    @builtins.property
    @jsii.member(jsii_name="blockReasonInput")
    def block_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "blockReasonInput"))

    @builtins.property
    @jsii.member(jsii_name="bypassParentRuleInput")
    def bypass_parent_rule_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "bypassParentRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="checkSessionInput")
    def check_session_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsCheckSession]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsCheckSession]], jsii.get(self, "checkSessionInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsResolversInput")
    def dns_resolvers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolvers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolvers]], jsii.get(self, "dnsResolversInput"))

    @builtins.property
    @jsii.member(jsii_name="egressInput")
    def egress_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsEgress]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsEgress]], jsii.get(self, "egressInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreCnameCategoryMatchesInput")
    def ignore_cname_category_matches_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ignoreCnameCategoryMatchesInput"))

    @builtins.property
    @jsii.member(jsii_name="insecureDisableDnssecValidationInput")
    def insecure_disable_dnssec_validation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureDisableDnssecValidationInput"))

    @builtins.property
    @jsii.member(jsii_name="ipCategoriesInput")
    def ip_categories_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ipCategoriesInput"))

    @builtins.property
    @jsii.member(jsii_name="ipIndicatorFeedsInput")
    def ip_indicator_feeds_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ipIndicatorFeedsInput"))

    @builtins.property
    @jsii.member(jsii_name="l4OverrideInput")
    def l4_override_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsL4Override]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsL4Override]], jsii.get(self, "l4OverrideInput"))

    @builtins.property
    @jsii.member(jsii_name="notificationSettingsInput")
    def notification_settings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsNotificationSettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsNotificationSettings]], jsii.get(self, "notificationSettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="overrideHostInput")
    def override_host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "overrideHostInput"))

    @builtins.property
    @jsii.member(jsii_name="overrideIpsInput")
    def override_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "overrideIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="payloadLogInput")
    def payload_log_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsPayloadLog"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsPayloadLog"]], jsii.get(self, "payloadLogInput"))

    @builtins.property
    @jsii.member(jsii_name="quarantineInput")
    def quarantine_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsQuarantine"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsQuarantine"]], jsii.get(self, "quarantineInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectInput")
    def redirect_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsRedirect"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsRedirect"]], jsii.get(self, "redirectInput"))

    @builtins.property
    @jsii.member(jsii_name="resolveDnsInternallyInput")
    def resolve_dns_internally_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally"]], jsii.get(self, "resolveDnsInternallyInput"))

    @builtins.property
    @jsii.member(jsii_name="resolveDnsThroughCloudflareInput")
    def resolve_dns_through_cloudflare_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "resolveDnsThroughCloudflareInput"))

    @builtins.property
    @jsii.member(jsii_name="untrustedCertInput")
    def untrusted_cert_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsUntrustedCert"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustGatewayPolicyRuleSettingsUntrustedCert"]], jsii.get(self, "untrustedCertInput"))

    @builtins.property
    @jsii.member(jsii_name="addHeaders")
    def add_headers(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "addHeaders"))

    @add_headers.setter
    def add_headers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a1f1f59b388e3b04d2fdc50bcdbc60dff8c312c77394e51f79fc0d9b92f994a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowChildBypass")
    def allow_child_bypass(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowChildBypass"))

    @allow_child_bypass.setter
    def allow_child_bypass(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c1fc79c6b71da20148ca5347784263aad3f198663797834c88c471ac2f6931d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowChildBypass", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="blockPageEnabled")
    def block_page_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "blockPageEnabled"))

    @block_page_enabled.setter
    def block_page_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c07d9f8c9923508c1d3b62f502d6885231364fd4bb9b55025d663a8724fdbaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockPageEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="blockReason")
    def block_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "blockReason"))

    @block_reason.setter
    def block_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c43883e87bbc6a1c0a0d78726e1e14d93beaa05a21e98daff92bb783685128fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockReason", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bypassParentRule")
    def bypass_parent_rule(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "bypassParentRule"))

    @bypass_parent_rule.setter
    def bypass_parent_rule(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb65d78b3a1632140634e15585710dfceb0568352431b9f8446d8a5724d20f54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bypassParentRule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreCnameCategoryMatches")
    def ignore_cname_category_matches(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ignoreCnameCategoryMatches"))

    @ignore_cname_category_matches.setter
    def ignore_cname_category_matches(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4927b6567e05d6e5b2db1c5b2bda5bf1451af31383f529e592384aa9be803593)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreCnameCategoryMatches", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insecureDisableDnssecValidation")
    def insecure_disable_dnssec_validation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "insecureDisableDnssecValidation"))

    @insecure_disable_dnssec_validation.setter
    def insecure_disable_dnssec_validation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9bcb95e227278b99caf156a3ac3c9bc6a4fa2b8a8754c0b078eb2f6c5217ea6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecureDisableDnssecValidation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipCategories")
    def ip_categories(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ipCategories"))

    @ip_categories.setter
    def ip_categories(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f014d156e2c8bd4d2dbc18cac0b25ceace721dfd317b7e86bd517b6887b3cd45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipCategories", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipIndicatorFeeds")
    def ip_indicator_feeds(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ipIndicatorFeeds"))

    @ip_indicator_feeds.setter
    def ip_indicator_feeds(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d989e27447bb19317a76be6b4dfe0c816a6491219e0ff58e835bb359459ed5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipIndicatorFeeds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="overrideHost")
    def override_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overrideHost"))

    @override_host.setter
    def override_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02bf89906aba8fc768c718b27a46d417bbdb17a2b72217c7e29b4b14a2bd7dab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "overrideHost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="overrideIps")
    def override_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "overrideIps"))

    @override_ips.setter
    def override_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcb235300b38c3bc913d31e7540997e53e6b2b3d34b84653711dcf7077567a4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "overrideIps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resolveDnsThroughCloudflare")
    def resolve_dns_through_cloudflare(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "resolveDnsThroughCloudflare"))

    @resolve_dns_through_cloudflare.setter
    def resolve_dns_through_cloudflare(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f244a322bbc2a1c167c15aec0b258cd8699df11dccce657701aba9b74e04f3df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resolveDnsThroughCloudflare", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__817376f6438ce5c9a592596111f84b92b1694af7ef6956d0054320459c45801c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsPayloadLog",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ZeroTrustGatewayPolicyRuleSettingsPayloadLog:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Set to true to enable DLP payload logging for this rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enabled ZeroTrustGatewayPolicy#enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9b51240c3300c0b57214e6902ad1a0ceb3f4e668d2ed20f684b5475d28ffa52)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to enable DLP payload logging for this rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#enabled ZeroTrustGatewayPolicy#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsPayloadLog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c65667181409e7bb7a033d5bb7c77d32d87a33789cff432f6d8cb2dc31045537)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c9824ebf004acc38e59c20e20925665eb2c2d3768d451cf96b49010d5521c4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsPayloadLog]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsPayloadLog]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsPayloadLog]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91ccf9550ba44eee5bccc3ee04815bbe69f75d41d08cf37ea5c47ef167c46c67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsQuarantine",
    jsii_struct_bases=[],
    name_mapping={"file_types": "fileTypes"},
)
class ZeroTrustGatewayPolicyRuleSettingsQuarantine:
    def __init__(
        self,
        *,
        file_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param file_types: Types of files to sandbox. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#file_types ZeroTrustGatewayPolicy#file_types}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ace61b5d6b88eacd5f372fc863b980f22465ab53d84578c3b3c66896d7e53c5)
            check_type(argname="argument file_types", value=file_types, expected_type=type_hints["file_types"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if file_types is not None:
            self._values["file_types"] = file_types

    @builtins.property
    def file_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Types of files to sandbox.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#file_types ZeroTrustGatewayPolicy#file_types}
        '''
        result = self._values.get("file_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsQuarantine(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9370b04fc5d73f1ea31f3fd2fc83689f74ee623d34a330f5897ee37554afe612)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFileTypes")
    def reset_file_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileTypes", []))

    @builtins.property
    @jsii.member(jsii_name="fileTypesInput")
    def file_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "fileTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="fileTypes")
    def file_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "fileTypes"))

    @file_types.setter
    def file_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ab83dcb635ab48265b4c7f5b2b152766fae4fe912f1cd782ba109f1b308ee28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsQuarantine]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsQuarantine]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsQuarantine]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e14e84903829f40bccd24f29d6adb41f2fcab8e1db655ce970e81c79ba8ad263)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsRedirect",
    jsii_struct_bases=[],
    name_mapping={
        "target_uri": "targetUri",
        "include_context": "includeContext",
        "preserve_path_and_query": "preservePathAndQuery",
    },
)
class ZeroTrustGatewayPolicyRuleSettingsRedirect:
    def __init__(
        self,
        *,
        target_uri: builtins.str,
        include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        preserve_path_and_query: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param target_uri: URI to which the user will be redirected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#target_uri ZeroTrustGatewayPolicy#target_uri}
        :param include_context: If true, context information will be passed as query parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#include_context ZeroTrustGatewayPolicy#include_context}
        :param preserve_path_and_query: If true, the path and query parameters from the original request will be appended to target_uri. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#preserve_path_and_query ZeroTrustGatewayPolicy#preserve_path_and_query}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99f46892940c0ed28755555288fa55498abf5c2bf134cd42539ccc961552a961)
            check_type(argname="argument target_uri", value=target_uri, expected_type=type_hints["target_uri"])
            check_type(argname="argument include_context", value=include_context, expected_type=type_hints["include_context"])
            check_type(argname="argument preserve_path_and_query", value=preserve_path_and_query, expected_type=type_hints["preserve_path_and_query"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target_uri": target_uri,
        }
        if include_context is not None:
            self._values["include_context"] = include_context
        if preserve_path_and_query is not None:
            self._values["preserve_path_and_query"] = preserve_path_and_query

    @builtins.property
    def target_uri(self) -> builtins.str:
        '''URI to which the user will be redirected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#target_uri ZeroTrustGatewayPolicy#target_uri}
        '''
        result = self._values.get("target_uri")
        assert result is not None, "Required property 'target_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def include_context(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, context information will be passed as query parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#include_context ZeroTrustGatewayPolicy#include_context}
        '''
        result = self._values.get("include_context")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def preserve_path_and_query(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the path and query parameters from the original request will be appended to target_uri.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#preserve_path_and_query ZeroTrustGatewayPolicy#preserve_path_and_query}
        '''
        result = self._values.get("preserve_path_and_query")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsRedirect(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c2dcb9db5d474672fd9478cc9cdff8686b994c2e619c854050d927b5e49bf9f6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIncludeContext")
    def reset_include_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeContext", []))

    @jsii.member(jsii_name="resetPreservePathAndQuery")
    def reset_preserve_path_and_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreservePathAndQuery", []))

    @builtins.property
    @jsii.member(jsii_name="includeContextInput")
    def include_context_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "includeContextInput"))

    @builtins.property
    @jsii.member(jsii_name="preservePathAndQueryInput")
    def preserve_path_and_query_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "preservePathAndQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="targetUriInput")
    def target_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetUriInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__640980d3d96a315f738589289645e8812cca9051ca386e3a97fb6777933c70dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeContext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preservePathAndQuery")
    def preserve_path_and_query(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "preservePathAndQuery"))

    @preserve_path_and_query.setter
    def preserve_path_and_query(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77d87fc93155b7ae60c72d83f8be8bc767bf7b457b1502d14898637de2c35d1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preservePathAndQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetUri")
    def target_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetUri"))

    @target_uri.setter
    def target_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__150c0b8aed23ed6a3eed03c86399b6d65377530cd4bf611cb68d429723d65698)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetUri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsRedirect]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsRedirect]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsRedirect]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b982388cda8dd65d8199299025571a65c7f158794b92e6b68077620b0e81d57e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally",
    jsii_struct_bases=[],
    name_mapping={"fallback": "fallback", "view_id": "viewId"},
)
class ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally:
    def __init__(
        self,
        *,
        fallback: typing.Optional[builtins.str] = None,
        view_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fallback: The fallback behavior to apply when the internal DNS response code is different from 'NOERROR' or when the response data only contains CNAME records for 'A' or 'AAAA' queries. Available values: "none", "public_dns". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#fallback ZeroTrustGatewayPolicy#fallback}
        :param view_id: The internal DNS view identifier that's passed to the internal DNS service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#view_id ZeroTrustGatewayPolicy#view_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__678eed8410f6f33cf7bfce795dcf50fbfce0f2b2b59f9dda1957bb54d6441246)
            check_type(argname="argument fallback", value=fallback, expected_type=type_hints["fallback"])
            check_type(argname="argument view_id", value=view_id, expected_type=type_hints["view_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if fallback is not None:
            self._values["fallback"] = fallback
        if view_id is not None:
            self._values["view_id"] = view_id

    @builtins.property
    def fallback(self) -> typing.Optional[builtins.str]:
        '''The fallback behavior to apply when the internal DNS response code is different from 'NOERROR' or when the response data only contains CNAME records for 'A' or 'AAAA' queries.

        Available values: "none", "public_dns".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#fallback ZeroTrustGatewayPolicy#fallback}
        '''
        result = self._values.get("fallback")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def view_id(self) -> typing.Optional[builtins.str]:
        '''The internal DNS view identifier that's passed to the internal DNS service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#view_id ZeroTrustGatewayPolicy#view_id}
        '''
        result = self._values.get("view_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9947478036f6da30f3b8648c4224457b7cca7ad70dbdf861b8cdcc8cf35146b9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFallback")
    def reset_fallback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFallback", []))

    @jsii.member(jsii_name="resetViewId")
    def reset_view_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViewId", []))

    @builtins.property
    @jsii.member(jsii_name="fallbackInput")
    def fallback_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fallbackInput"))

    @builtins.property
    @jsii.member(jsii_name="viewIdInput")
    def view_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "viewIdInput"))

    @builtins.property
    @jsii.member(jsii_name="fallback")
    def fallback(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fallback"))

    @fallback.setter
    def fallback(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c466dcd176125ed5a434bf2b93dddb7786eee68ad9c1556c73d28411c7585346)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallback", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="viewId")
    def view_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "viewId"))

    @view_id.setter
    def view_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c52d1968c48926756c5a4583bfb026d0675f6c6d92a8fbf1c5b954d41c09360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "viewId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__984a9ca044b66ea914c4e708d1ca013550975bebcd814cc116adb2ae15f558a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsUntrustedCert",
    jsii_struct_bases=[],
    name_mapping={"action": "action"},
)
class ZeroTrustGatewayPolicyRuleSettingsUntrustedCert:
    def __init__(self, *, action: typing.Optional[builtins.str] = None) -> None:
        '''
        :param action: The action performed when an untrusted certificate is seen. The default action is an error with HTTP code 526. Available values: "pass_through", "block", "error". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#action ZeroTrustGatewayPolicy#action}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b688dd86837fff9fcf647af267f3c878d950d8ea4e7a2a8c9e8c3ce7e09e71fa)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if action is not None:
            self._values["action"] = action

    @builtins.property
    def action(self) -> typing.Optional[builtins.str]:
        '''The action performed when an untrusted certificate is seen.

        The default action is an error with HTTP code 526.
        Available values: "pass_through", "block", "error".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#action ZeroTrustGatewayPolicy#action}
        '''
        result = self._values.get("action")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicyRuleSettingsUntrustedCert(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__af7071c4ca8192d51c7c471be9587d21242e649f892b6474bf5efa053f997942)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAction")
    def reset_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAction", []))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ab7c9f74d80e11871006aeb9dc12808ee977fbebfaba5357da7c34b4e06604e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsUntrustedCert]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsUntrustedCert]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsUntrustedCert]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b4a37808e9878e4b67e98ae7a831999670583ffe153d2849dff1b1a0011d1ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicySchedule",
    jsii_struct_bases=[],
    name_mapping={
        "fri": "fri",
        "mon": "mon",
        "sat": "sat",
        "sun": "sun",
        "thu": "thu",
        "time_zone": "timeZone",
        "tue": "tue",
        "wed": "wed",
    },
)
class ZeroTrustGatewayPolicySchedule:
    def __init__(
        self,
        *,
        fri: typing.Optional[builtins.str] = None,
        mon: typing.Optional[builtins.str] = None,
        sat: typing.Optional[builtins.str] = None,
        sun: typing.Optional[builtins.str] = None,
        thu: typing.Optional[builtins.str] = None,
        time_zone: typing.Optional[builtins.str] = None,
        tue: typing.Optional[builtins.str] = None,
        wed: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fri: The time intervals when the rule will be active on Fridays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Fridays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#fri ZeroTrustGatewayPolicy#fri}
        :param mon: The time intervals when the rule will be active on Mondays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Mondays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#mon ZeroTrustGatewayPolicy#mon}
        :param sat: The time intervals when the rule will be active on Saturdays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Saturdays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#sat ZeroTrustGatewayPolicy#sat}
        :param sun: The time intervals when the rule will be active on Sundays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Sundays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#sun ZeroTrustGatewayPolicy#sun}
        :param thu: The time intervals when the rule will be active on Thursdays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Thursdays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#thu ZeroTrustGatewayPolicy#thu}
        :param time_zone: The time zone the rule will be evaluated against. If a `valid time zone city name <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List>`_ is provided, Gateway will always use the current time at that time zone. If this parameter is omitted, then Gateway will use the time zone inferred from the user's source IP to evaluate the rule. If Gateway cannot determine the time zone from the IP, we will fall back to the time zone of the user's connected data center. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#time_zone ZeroTrustGatewayPolicy#time_zone}
        :param tue: The time intervals when the rule will be active on Tuesdays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Tuesdays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#tue ZeroTrustGatewayPolicy#tue}
        :param wed: The time intervals when the rule will be active on Wednesdays, in increasing order from 00:00-24:00. If this parameter is omitted, the rule will be deactivated on Wednesdays. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#wed ZeroTrustGatewayPolicy#wed}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e33b49ab58e8569fc35612f7e1dae3ac44e9a194deffc800a17bde3f5a76cf5)
            check_type(argname="argument fri", value=fri, expected_type=type_hints["fri"])
            check_type(argname="argument mon", value=mon, expected_type=type_hints["mon"])
            check_type(argname="argument sat", value=sat, expected_type=type_hints["sat"])
            check_type(argname="argument sun", value=sun, expected_type=type_hints["sun"])
            check_type(argname="argument thu", value=thu, expected_type=type_hints["thu"])
            check_type(argname="argument time_zone", value=time_zone, expected_type=type_hints["time_zone"])
            check_type(argname="argument tue", value=tue, expected_type=type_hints["tue"])
            check_type(argname="argument wed", value=wed, expected_type=type_hints["wed"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if fri is not None:
            self._values["fri"] = fri
        if mon is not None:
            self._values["mon"] = mon
        if sat is not None:
            self._values["sat"] = sat
        if sun is not None:
            self._values["sun"] = sun
        if thu is not None:
            self._values["thu"] = thu
        if time_zone is not None:
            self._values["time_zone"] = time_zone
        if tue is not None:
            self._values["tue"] = tue
        if wed is not None:
            self._values["wed"] = wed

    @builtins.property
    def fri(self) -> typing.Optional[builtins.str]:
        '''The time intervals when the rule will be active on Fridays, in increasing order from 00:00-24:00.

        If this parameter is omitted, the rule will be deactivated on Fridays.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#fri ZeroTrustGatewayPolicy#fri}
        '''
        result = self._values.get("fri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mon(self) -> typing.Optional[builtins.str]:
        '''The time intervals when the rule will be active on Mondays, in increasing order from 00:00-24:00.

        If this parameter is omitted, the rule will be deactivated on Mondays.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#mon ZeroTrustGatewayPolicy#mon}
        '''
        result = self._values.get("mon")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sat(self) -> typing.Optional[builtins.str]:
        '''The time intervals when the rule will be active on Saturdays, in increasing order from 00:00-24:00.

        If this parameter is omitted, the rule will be deactivated on Saturdays.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#sat ZeroTrustGatewayPolicy#sat}
        '''
        result = self._values.get("sat")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sun(self) -> typing.Optional[builtins.str]:
        '''The time intervals when the rule will be active on Sundays, in increasing order from 00:00-24:00.

        If this parameter is omitted, the rule will be deactivated on Sundays.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#sun ZeroTrustGatewayPolicy#sun}
        '''
        result = self._values.get("sun")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def thu(self) -> typing.Optional[builtins.str]:
        '''The time intervals when the rule will be active on Thursdays, in increasing order from 00:00-24:00.

        If this parameter is omitted, the rule will be deactivated on Thursdays.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#thu ZeroTrustGatewayPolicy#thu}
        '''
        result = self._values.get("thu")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[builtins.str]:
        '''The time zone the rule will be evaluated against.

        If a `valid time zone city name <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List>`_ is provided, Gateway will always use the current time at that time zone. If this parameter is omitted, then Gateway will use the time zone inferred from the user's source IP to evaluate the rule. If Gateway cannot determine the time zone from the IP, we will fall back to the time zone of the user's connected data center.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#time_zone ZeroTrustGatewayPolicy#time_zone}
        '''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tue(self) -> typing.Optional[builtins.str]:
        '''The time intervals when the rule will be active on Tuesdays, in increasing order from 00:00-24:00.

        If this parameter is omitted, the rule will be deactivated on Tuesdays.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#tue ZeroTrustGatewayPolicy#tue}
        '''
        result = self._values.get("tue")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wed(self) -> typing.Optional[builtins.str]:
        '''The time intervals when the rule will be active on Wednesdays, in increasing order from 00:00-24:00.

        If this parameter is omitted, the rule will be deactivated on Wednesdays.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_gateway_policy#wed ZeroTrustGatewayPolicy#wed}
        '''
        result = self._values.get("wed")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustGatewayPolicySchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustGatewayPolicyScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustGatewayPolicy.ZeroTrustGatewayPolicyScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9ceb2d15871ccc3254fb91ad7050412af3ee52f67851ed184a5fea2ff451692)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFri")
    def reset_fri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFri", []))

    @jsii.member(jsii_name="resetMon")
    def reset_mon(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMon", []))

    @jsii.member(jsii_name="resetSat")
    def reset_sat(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSat", []))

    @jsii.member(jsii_name="resetSun")
    def reset_sun(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSun", []))

    @jsii.member(jsii_name="resetThu")
    def reset_thu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThu", []))

    @jsii.member(jsii_name="resetTimeZone")
    def reset_time_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeZone", []))

    @jsii.member(jsii_name="resetTue")
    def reset_tue(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTue", []))

    @jsii.member(jsii_name="resetWed")
    def reset_wed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWed", []))

    @builtins.property
    @jsii.member(jsii_name="friInput")
    def fri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "friInput"))

    @builtins.property
    @jsii.member(jsii_name="monInput")
    def mon_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "monInput"))

    @builtins.property
    @jsii.member(jsii_name="satInput")
    def sat_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "satInput"))

    @builtins.property
    @jsii.member(jsii_name="sunInput")
    def sun_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sunInput"))

    @builtins.property
    @jsii.member(jsii_name="thuInput")
    def thu_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thuInput"))

    @builtins.property
    @jsii.member(jsii_name="timeZoneInput")
    def time_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="tueInput")
    def tue_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tueInput"))

    @builtins.property
    @jsii.member(jsii_name="wedInput")
    def wed_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wedInput"))

    @builtins.property
    @jsii.member(jsii_name="fri")
    def fri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fri"))

    @fri.setter
    def fri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e80de9aef4fc16dc85a8aaa77d04d65b8558482506a04e14e9804f08f87ac36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mon")
    def mon(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mon"))

    @mon.setter
    def mon(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65bcd1a576f5994614d41abc994c88a46c82d5bcc843da296f1ece6b72ad0ea1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mon", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sat")
    def sat(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sat"))

    @sat.setter
    def sat(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__254acfd028e8dc92b31083d2e8bed3c0b5774c6cff7e13596c58c031328de366)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sun")
    def sun(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sun"))

    @sun.setter
    def sun(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38f988f2e3a3524efc204cb7c1c9939557b881e0ac652f81d2157defb47aea1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="thu")
    def thu(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thu"))

    @thu.setter
    def thu(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af59f8b004c72907ebfc2fd57559f94c6be1768133526629dd8b1d02e893fcc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "thu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZone"))

    @time_zone.setter
    def time_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9b311c28a1aac3dbe6927683a8d02088d6d816d0b2477624f76b823105381f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tue")
    def tue(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tue"))

    @tue.setter
    def tue(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a86d077ae3ef99a6c544f4ff5f84aca770e190c1f620628a5ad4afdff297813d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wed")
    def wed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wed"))

    @wed.setter
    def wed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__062d1ac253adeac573109395b40385963c60c16837141feea29eae45f9268fbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicySchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicySchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicySchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed186d2b1eb9da23194f0fe07ac8118c7ff1ea59e7363d844569b40bf8b98f56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustGatewayPolicy",
    "ZeroTrustGatewayPolicyConfig",
    "ZeroTrustGatewayPolicyExpiration",
    "ZeroTrustGatewayPolicyExpirationOutputReference",
    "ZeroTrustGatewayPolicyRuleSettings",
    "ZeroTrustGatewayPolicyRuleSettingsAuditSsh",
    "ZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls",
    "ZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsBlockPage",
    "ZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsCheckSession",
    "ZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsDnsResolvers",
    "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4",
    "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List",
    "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6",
    "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List",
    "ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsEgress",
    "ZeroTrustGatewayPolicyRuleSettingsEgressOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsL4Override",
    "ZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsNotificationSettings",
    "ZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsPayloadLog",
    "ZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsQuarantine",
    "ZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsRedirect",
    "ZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally",
    "ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference",
    "ZeroTrustGatewayPolicyRuleSettingsUntrustedCert",
    "ZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference",
    "ZeroTrustGatewayPolicySchedule",
    "ZeroTrustGatewayPolicyScheduleOutputReference",
]

publication.publish()

def _typecheckingstub__e786f3b51fdd9d9ed8a9ede6d413dce3bca2cd0cf1cb66429b00315285745858(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    action: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    device_posture: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    expiration: typing.Optional[typing.Union[ZeroTrustGatewayPolicyExpiration, typing.Dict[builtins.str, typing.Any]]] = None,
    filters: typing.Optional[typing.Sequence[builtins.str]] = None,
    identity: typing.Optional[builtins.str] = None,
    precedence: typing.Optional[jsii.Number] = None,
    rule_settings: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[typing.Union[ZeroTrustGatewayPolicySchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    traffic: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__08a82a394c6d2096b6cfe77d2cb2d7a0802d1cb0b8c4111b58a4499f87b9cb2b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0bb7ba5f48d9b8e2a3bb95f022537a9bfc450f3475c72a300c1cae1683f9ec2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7bbd14973f8b3f0a43994b287c91e533e76cb5b8c5e095101c90750c11d93b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83db28167eff420a547cf252dd8e7781e5796c1cace39c68df6c1a06b2da2d0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee39d2975aef69e34e1a231b8e211addc371b9ad64dceb2f20e20d4ae852c237(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45825779e8075f762c6a646e54a09f77631a4328dfb317cc06b661e8121e179b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f18e5f294f5711f739edce78df2d227cbee0051bd29aba76a875d970ca98100b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fff43c71cbeb7eff49371043e13151751ba92b81c1e0493e6f2f3ebce50d929(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa62bd411e5957a4f46d586eb095eb3d653370b09ee649ce6849dd5a2d07624b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5210b06d00643b59aad339b83d84162c64bdb7c26827fb9528babd7e3e61786c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__872dd1a90e3d9f1a1ba75703168e5c9754c8cbf3777f03ea7b5294d225912329(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f3d5137255dbb7219c971b313cd804791e2a0ef37964d8a593b17f6a3718187(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    action: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    device_posture: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    expiration: typing.Optional[typing.Union[ZeroTrustGatewayPolicyExpiration, typing.Dict[builtins.str, typing.Any]]] = None,
    filters: typing.Optional[typing.Sequence[builtins.str]] = None,
    identity: typing.Optional[builtins.str] = None,
    precedence: typing.Optional[jsii.Number] = None,
    rule_settings: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[typing.Union[ZeroTrustGatewayPolicySchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    traffic: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a22e90656dbfb5affc5461cc88f420c65a62504626e8aaae73b67bd55f5d706d(
    *,
    expires_at: builtins.str,
    duration: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acc4a601ddf89bd273cfff3a1f85944fc997bba30d3e4fc12a25695c453beb41(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c3a7530d11d824f05eed7541a667e4d0fff1c0038bdc91d3b18985fb7f71289(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbea57ced4427f47478d49c78359ac3e387fc37d5fc0784f9d2ddbdcfc935173(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffadd22ffcf5404d27322fc7899d4e3fd48372db2388a659b4f6afa1955f4cc5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyExpiration]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea8f89e3048662a05610c3fc4775c975b8cbfc7190cf304482a2b63c0a5c20af(
    *,
    add_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    allow_child_bypass: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    audit_ssh: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsAuditSsh, typing.Dict[builtins.str, typing.Any]]] = None,
    biso_admin_controls: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls, typing.Dict[builtins.str, typing.Any]]] = None,
    block_page: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsBlockPage, typing.Dict[builtins.str, typing.Any]]] = None,
    block_page_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    block_reason: typing.Optional[builtins.str] = None,
    bypass_parent_rule: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    check_session: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsCheckSession, typing.Dict[builtins.str, typing.Any]]] = None,
    dns_resolvers: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsDnsResolvers, typing.Dict[builtins.str, typing.Any]]] = None,
    egress: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsEgress, typing.Dict[builtins.str, typing.Any]]] = None,
    ignore_cname_category_matches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    insecure_disable_dnssec_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ip_categories: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ip_indicator_feeds: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    l4_override: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsL4Override, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_settings: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsNotificationSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    override_host: typing.Optional[builtins.str] = None,
    override_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    payload_log: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsPayloadLog, typing.Dict[builtins.str, typing.Any]]] = None,
    quarantine: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsQuarantine, typing.Dict[builtins.str, typing.Any]]] = None,
    redirect: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsRedirect, typing.Dict[builtins.str, typing.Any]]] = None,
    resolve_dns_internally: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally, typing.Dict[builtins.str, typing.Any]]] = None,
    resolve_dns_through_cloudflare: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    untrusted_cert: typing.Optional[typing.Union[ZeroTrustGatewayPolicyRuleSettingsUntrustedCert, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e13806ef402ec94ed21dd8e335b31ece45f371213e9bd91cd4f83a977b851a3(
    *,
    command_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7cbe1aad2274aab866344e2e4178aa08f6f0894258b0a1d57502ac56a236f45(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e9da99cbe034882dfcd29f81babcb2a2c1f9170d681b8bdcfdf43385b072238(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f5fc353cec0452da1882b51e0644b7d85e988ab68deb41c5016c972fb20c440(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsAuditSsh]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fd65a816aca7befaa772d1c5d0ecc9d1f288ab4e81f1ffdade3c911a0b13b14(
    *,
    copy: typing.Optional[builtins.str] = None,
    dcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dd: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    download: typing.Optional[builtins.str] = None,
    dp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    du: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    keyboard: typing.Optional[builtins.str] = None,
    paste: typing.Optional[builtins.str] = None,
    printing: typing.Optional[builtins.str] = None,
    upload: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e487688fb41ca3eaba6906db9cc86e97d2f8b3c4b56ad97fcb47b4ac4a290d93(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__847e3266c339f242561bab36b9a127e98d78563625e6c532c3f51fd30069bdfa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__264d6acc8cc77cb9a29bf5d3bca13e3646a9de80271af961d75c8520f3629f58(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ee0f17f2cd11bf1a250092ce145d5e79ab393299d65a8706ca616d56b920655(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c5edf013cf0cfbe0cca5e429d20c3df97c1d2f794e73bd5d940a107b4d453dc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc80e10e9fa19e95eec091b3618e843ad611828178978d4763a289ac6426f4eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d21870a1ccb9a308ffaef2e102f2faba77562fc15d375bee975eba9a246f7e00(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89fee6ac0a0cc34d094468baeee53248b29bbc6b4dafdd2bf79e0f1900af59f4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6374e94307d57e43c0ac67c0858375ca82eae0e986e4cc92d4defe244a06ce3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffc1f7f453c402a0aa874558556f56aa275fbcd1783f012e03c5e95d9d702df5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a93839565865f32a568de6c6e02c7a8a72c86935c4fc597a9a9e6a01fa83fecb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92fc6cb26b207b7cf8331a3e49388a9560f205745c7cf1b20e05969d7f5fa793(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4690a0a29a87ddf078dfd55099392f0d402bbb99e1b25b405bd45cd70cb5a144(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b16262088665bd23c4414f6ce9e1ef921a03111175eb5160228b5b8cbdb35cb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBisoAdminControls]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9fb9d94740379040849ad9c6520fb4dd017f7f54c36906c06fad8f870a2d98e(
    *,
    target_uri: builtins.str,
    include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abf8985c3a0d36fee6d72818af6af8191daccacff470b7ce4c76b71c0abc2e60(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__643efd4d4715e0e44f722ba2a63c73c421fee488a6d3ca0ba8da7409708b7439(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d81f95b03c49167f5c7f070994f82470c7aa380b01fd57029028d8ee2f08dfc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0924b10f56d0b14df3284cf60625f495175ec98ac50f5abb71761de13d850b8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsBlockPage]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56199ee2205a76f737af972538e10f89fe9b1ad3b1ae437325cab49c99f6877b(
    *,
    duration: typing.Optional[builtins.str] = None,
    enforce: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64e808649dd9d4901863979bb24d8623d67310b6fc114de70bc108fa8480a248(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33b8a53e3936669c3400cdac4a0dcaa9df95fde0f9b01f93cddf02a0f6de668b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__704639372dcc580a04c74d5c5fb881b8f14087b8aad093f31515ad4d3b70b1b6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7cea6cb3a0aa5166676514ff8fe2f424ad1b786908f73d5bd1b9cc8d02add24(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsCheckSession]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e61e86bdabb946d2d3a72397fbab37eed75de1962c303d02d391da06329eb2b1(
    *,
    ipv4: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ipv6: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c24719bdc3038d165f74ab720bef83026321ba3145104cfaa1c1b20d148cab8(
    *,
    ip: builtins.str,
    port: typing.Optional[jsii.Number] = None,
    route_through_private_network: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vnet_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8325a1a409077918c933b460bfcc5f3a826ee186f245ca9839b836c70d772e06(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__533b1bf8395b943248c885e85812eb93b2a774de10422d63612cf28ac14cafaa(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6c2d41d484fcff6d4869072b8c656d8d1637c6d2ded398ea49a1d65dbaebbd2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89dd7a58248308472bd5468feb92374998e6b7b5590ec736782c3a553637e060(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d71763ee18b7be04bf6a77a7792383688b0cfd8db3c6ed614cd32776113332c6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe57289c5a429db420b6145e99ddaaf5ede4dc135885cf66ffa8e5fa4303b979(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11b79a03168b1f67148b565cda58d26b288c914a1d512954035060c72b5e3d87(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1fd7414892d1597a66dac08101d741d4f8d59be453c0dea8a8d1338514cb5b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48f65de8183eaebfe0f9215db319b0e90ea52991fb28e72d46082a8ace1646ee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4329b10738e673d9049a8ce03c03876d48454709cdddfc3de5497fc5492f8189(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4b0d19c27d6fd136e1e0d206878f3628b4675a45ec9fc28cefe607883cb7397(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3fe51044e877d271f848c76ef15c1b3e10a340760aa9758e97ea688bc18e0a4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f85e4dfa7046f3af0deee7ff5a1e3a4b86af348b71fe1af87e2692b77712992(
    *,
    ip: builtins.str,
    port: typing.Optional[jsii.Number] = None,
    route_through_private_network: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vnet_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e4bfb32196b3551481e8cca349977d12590376dd4642cc0bc2726152543abe8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc981020efa520611da174b7843290c261f1dc2e2a32ec583c026ee3b10931fb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8407ffb93365f1e2e11b27875a35c4dca52915c0e1f10356b9a1e7ef826cbc4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b6117090d75a8b51dc4d30205a60b06123d6019c3934be55e60967b5f4d56c1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f0a68cd7314b423e0e39a7e15fbd9a1108fa2272438d35e24cb18ade3535045(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a80c31a75c73774f61153c8df8e0968b4f59e3a499f73f0e7f101d5efe967bd6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6aefc0967e7ec9bfc17da46922d77545c41748b7953a536aa596d76d466151ba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9d1a1427283f10bb887bae9c8c09aa3473bb39bee635cb748cc7bec7288aff2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0988a9d00ba8ce08c0f3fe89efeabad47e3fd9a2817225d945e7d064436329d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8866e5fdf3ff5e525fe793fa1633c72c80b4ba2ef2047c9e8d0446894140b9ac(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f45582a25857306e9cd17c9127b3d076c4693372dd57adbbf473a7705fc42db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7bb6c8dd0d7cf527e474f84d5a925a39708320a10e08bdafbc5a00915848a41(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfe77d83fd907f5544880a4f430e59c13a1392f63bd7abfafdef6f884393e209(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b669ea23d8599a8644f7eeadecdb0f6bdc876d012383fbd95625edd251989a36(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9dc0db711eacec9887cafb44e734357f3d89b9fb5f4d297e2f7ca1f2c366bd8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__298b64663e24f0ea5c0535778501a4f36f10bbaead2fca81e35f69674e0c9d84(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsDnsResolvers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54c20c20790982b1f4876312fe70df67926222adacb75525c029e94887d98091(
    *,
    ipv4: typing.Optional[builtins.str] = None,
    ipv4_fallback: typing.Optional[builtins.str] = None,
    ipv6: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0796cb8575c970172d0ce9e0ad3d1e0860b3ab8d36b679e13b1f966c06bade9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__966af7cdf684fe3aa938943063e2d7977054accb6cead27577e182dd385c3c7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd6e3514c0230e5012ef0492d45c9d1b43937198b0bd8b5bd65da9a5cc57ee88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a862b5eb8ce043e340f8e643740e87ed76e3bbe47211aecb9ed70ca4ad785c12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6833a6d490876a271d35b87f147a66acb5deb7685ab224819007c64d0e400263(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsEgress]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbef793f0f9dfeabe7b5485433aab6102e162df9a897abc8d4b8aa339fee92ea(
    *,
    ip: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6376ac5fce76140ef3b8fb4f6af9e78a84d144fa24bf3dea6601411840482eb6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a062656fb3774493c7ec44c60f40ddae4dcc2ab4ae76d3fac41cfca847cee672(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5059f6a84f9af734199f2419a73019521b0ef42cdde25d33f3848ffa428e0aa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6992764ef0e447a8c43336bc9eb62ac1a401718853c978e226e191973c17cb66(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsL4Override]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8db5c5eeaf4ff44b629eb99747f03cd75818482acd82211db67f8e37ddf7fc2(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    msg: typing.Optional[builtins.str] = None,
    support_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__727c90cf4d7e78e845de5b7b5c003c1d7edca7319b28566b450c0738e7d213fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e07fe27be482df4e82f9d62e5ba477d03b5e5c742909acc39649a932218a327d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97e07a261b5f0dae0a9dc4c071310288f889a2c94ade0a8e85f3acd49c625170(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dc15ee2beaf4b1d8f0d0378d8e4545b004f7c996e8ae82f6b10748aefad695f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99fef0f410d5c6360be8db0b53fa52f68d0a745a5d8ac7815daf6cddc788b82e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6537fcfae534b3c752b2fbe6489d26533be9a49e9425c470c18a6d3d0f036ea7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsNotificationSettings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f1fbdcc6d5b96639588760d6d409fb65e4ee361bc0d52ea6c5e7f0dbd6ada66(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a1f1f59b388e3b04d2fdc50bcdbc60dff8c312c77394e51f79fc0d9b92f994a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c1fc79c6b71da20148ca5347784263aad3f198663797834c88c471ac2f6931d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c07d9f8c9923508c1d3b62f502d6885231364fd4bb9b55025d663a8724fdbaf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c43883e87bbc6a1c0a0d78726e1e14d93beaa05a21e98daff92bb783685128fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb65d78b3a1632140634e15585710dfceb0568352431b9f8446d8a5724d20f54(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4927b6567e05d6e5b2db1c5b2bda5bf1451af31383f529e592384aa9be803593(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9bcb95e227278b99caf156a3ac3c9bc6a4fa2b8a8754c0b078eb2f6c5217ea6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f014d156e2c8bd4d2dbc18cac0b25ceace721dfd317b7e86bd517b6887b3cd45(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d989e27447bb19317a76be6b4dfe0c816a6491219e0ff58e835bb359459ed5b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02bf89906aba8fc768c718b27a46d417bbdb17a2b72217c7e29b4b14a2bd7dab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcb235300b38c3bc913d31e7540997e53e6b2b3d34b84653711dcf7077567a4f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f244a322bbc2a1c167c15aec0b258cd8699df11dccce657701aba9b74e04f3df(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__817376f6438ce5c9a592596111f84b92b1694af7ef6956d0054320459c45801c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9b51240c3300c0b57214e6902ad1a0ceb3f4e668d2ed20f684b5475d28ffa52(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c65667181409e7bb7a033d5bb7c77d32d87a33789cff432f6d8cb2dc31045537(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c9824ebf004acc38e59c20e20925665eb2c2d3768d451cf96b49010d5521c4e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91ccf9550ba44eee5bccc3ee04815bbe69f75d41d08cf37ea5c47ef167c46c67(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsPayloadLog]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ace61b5d6b88eacd5f372fc863b980f22465ab53d84578c3b3c66896d7e53c5(
    *,
    file_types: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9370b04fc5d73f1ea31f3fd2fc83689f74ee623d34a330f5897ee37554afe612(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ab83dcb635ab48265b4c7f5b2b152766fae4fe912f1cd782ba109f1b308ee28(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e14e84903829f40bccd24f29d6adb41f2fcab8e1db655ce970e81c79ba8ad263(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsQuarantine]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99f46892940c0ed28755555288fa55498abf5c2bf134cd42539ccc961552a961(
    *,
    target_uri: builtins.str,
    include_context: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    preserve_path_and_query: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2dcb9db5d474672fd9478cc9cdff8686b994c2e619c854050d927b5e49bf9f6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__640980d3d96a315f738589289645e8812cca9051ca386e3a97fb6777933c70dc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77d87fc93155b7ae60c72d83f8be8bc767bf7b457b1502d14898637de2c35d1a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__150c0b8aed23ed6a3eed03c86399b6d65377530cd4bf611cb68d429723d65698(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b982388cda8dd65d8199299025571a65c7f158794b92e6b68077620b0e81d57e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsRedirect]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__678eed8410f6f33cf7bfce795dcf50fbfce0f2b2b59f9dda1957bb54d6441246(
    *,
    fallback: typing.Optional[builtins.str] = None,
    view_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9947478036f6da30f3b8648c4224457b7cca7ad70dbdf861b8cdcc8cf35146b9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c466dcd176125ed5a434bf2b93dddb7786eee68ad9c1556c73d28411c7585346(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c52d1968c48926756c5a4583bfb026d0675f6c6d92a8fbf1c5b954d41c09360(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__984a9ca044b66ea914c4e708d1ca013550975bebcd814cc116adb2ae15f558a6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b688dd86837fff9fcf647af267f3c878d950d8ea4e7a2a8c9e8c3ce7e09e71fa(
    *,
    action: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af7071c4ca8192d51c7c471be9587d21242e649f892b6474bf5efa053f997942(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ab7c9f74d80e11871006aeb9dc12808ee977fbebfaba5357da7c34b4e06604e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b4a37808e9878e4b67e98ae7a831999670583ffe153d2849dff1b1a0011d1ba(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicyRuleSettingsUntrustedCert]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e33b49ab58e8569fc35612f7e1dae3ac44e9a194deffc800a17bde3f5a76cf5(
    *,
    fri: typing.Optional[builtins.str] = None,
    mon: typing.Optional[builtins.str] = None,
    sat: typing.Optional[builtins.str] = None,
    sun: typing.Optional[builtins.str] = None,
    thu: typing.Optional[builtins.str] = None,
    time_zone: typing.Optional[builtins.str] = None,
    tue: typing.Optional[builtins.str] = None,
    wed: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9ceb2d15871ccc3254fb91ad7050412af3ee52f67851ed184a5fea2ff451692(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e80de9aef4fc16dc85a8aaa77d04d65b8558482506a04e14e9804f08f87ac36(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65bcd1a576f5994614d41abc994c88a46c82d5bcc843da296f1ece6b72ad0ea1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__254acfd028e8dc92b31083d2e8bed3c0b5774c6cff7e13596c58c031328de366(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38f988f2e3a3524efc204cb7c1c9939557b881e0ac652f81d2157defb47aea1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af59f8b004c72907ebfc2fd57559f94c6be1768133526629dd8b1d02e893fcc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9b311c28a1aac3dbe6927683a8d02088d6d816d0b2477624f76b823105381f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a86d077ae3ef99a6c544f4ff5f84aca770e190c1f620628a5ad4afdff297813d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__062d1ac253adeac573109395b40385963c60c16837141feea29eae45f9268fbf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed186d2b1eb9da23194f0fe07ac8118c7ff1ea59e7363d844569b40bf8b98f56(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustGatewayPolicySchedule]],
) -> None:
    """Type checking stubs"""
    pass
