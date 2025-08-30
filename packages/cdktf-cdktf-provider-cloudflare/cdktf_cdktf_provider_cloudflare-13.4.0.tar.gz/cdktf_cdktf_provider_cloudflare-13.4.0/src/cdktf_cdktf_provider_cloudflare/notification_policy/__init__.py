r'''
# `cloudflare_notification_policy`

Refer to the Terraform Registry for docs: [`cloudflare_notification_policy`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy).
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


class NotificationPolicy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy cloudflare_notification_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        alert_type: builtins.str,
        mechanisms: typing.Union["NotificationPolicyMechanisms", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        alert_interval: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        filters: typing.Optional[typing.Union["NotificationPolicyFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy cloudflare_notification_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The account id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#account_id NotificationPolicy#account_id}
        :param alert_type: Refers to which event will trigger a Notification dispatch. You can use the endpoint to get available alert types which then will give you a list of possible values. Available values: "access_custom_certificate_expiration_type", "advanced_ddos_attack_l4_alert", "advanced_ddos_attack_l7_alert", "advanced_http_alert_error", "bgp_hijack_notification", "billing_usage_alert", "block_notification_block_removed", "block_notification_new_block", "block_notification_review_rejected", "bot_traffic_basic_alert", "brand_protection_alert", "brand_protection_digest", "clickhouse_alert_fw_anomaly", "clickhouse_alert_fw_ent_anomaly", "cloudforce_one_request_notification", "custom_analytics", "custom_bot_detection_alert", "custom_ssl_certificate_event_type", "dedicated_ssl_certificate_event_type", "device_connectivity_anomaly_alert", "dos_attack_l4", "dos_attack_l7", "expiring_service_token_alert", "failing_logpush_job_disabled_alert", "fbm_auto_advertisement", "fbm_dosd_attack", "fbm_volumetric_attack", "health_check_status_notification", "hostname_aop_custom_certificate_expiration_type", "http_alert_edge_error", "http_alert_origin_error", "image_notification", "image_resizing_notification", "incident_alert", "load_balancing_health_alert", "load_balancing_pool_enablement_alert", "logo_match_alert", "magic_tunnel_health_check_event", "magic_wan_tunnel_health", "maintenance_event_notification", "mtls_certificate_store_certificate_expiration_type", "pages_event_alert", "radar_notification", "real_origin_monitoring", "scriptmonitor_alert_new_code_change_detections", "scriptmonitor_alert_new_hosts", "scriptmonitor_alert_new_malicious_hosts", "scriptmonitor_alert_new_malicious_scripts", "scriptmonitor_alert_new_malicious_url", "scriptmonitor_alert_new_max_length_resource_url", "scriptmonitor_alert_new_resources", "secondary_dns_all_primaries_failing", "secondary_dns_primaries_failing", "secondary_dns_warning", "secondary_dns_zone_successfully_updated", "secondary_dns_zone_validation_warning", "security_insights_alert", "sentinel_alert", "stream_live_notifications", "synthetic_test_latency_alert", "synthetic_test_low_availability_alert", "traffic_anomalies_alert", "tunnel_health_event", "tunnel_update_event", "universal_ssl_event_type", "web_analytics_metrics_update", "zone_aop_custom_certificate_expiration_type". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_type NotificationPolicy#alert_type}
        :param mechanisms: List of IDs that will be used when dispatching a notification. IDs for email type will be the email address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#mechanisms NotificationPolicy#mechanisms}
        :param name: Name of the policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#name NotificationPolicy#name}
        :param alert_interval: Optional specification of how often to re-alert from the same incident, not support on all alert types. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_interval NotificationPolicy#alert_interval}
        :param description: Optional description for the Notification policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#description NotificationPolicy#description}
        :param enabled: Whether or not the Notification policy is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#enabled NotificationPolicy#enabled}
        :param filters: Optional filters that allow you to be alerted only on a subset of events for that alert type based on some criteria. This is only available for select alert types. See alert type documentation for more details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#filters NotificationPolicy#filters}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d26986a49b23bd0b8c252e62235f69de0aed407a858eb18dec93b2afb89ac0f4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = NotificationPolicyConfig(
            account_id=account_id,
            alert_type=alert_type,
            mechanisms=mechanisms,
            name=name,
            alert_interval=alert_interval,
            description=description,
            enabled=enabled,
            filters=filters,
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
        '''Generates CDKTF code for importing a NotificationPolicy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the NotificationPolicy to import.
        :param import_from_id: The id of the existing NotificationPolicy that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the NotificationPolicy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__125b1431b5b31917f637f01b7497a9caaaa8b98ffa586ee484008a61b146f960)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFilters")
    def put_filters(
        self,
        *,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        affected_asns: typing.Optional[typing.Sequence[builtins.str]] = None,
        affected_components: typing.Optional[typing.Sequence[builtins.str]] = None,
        affected_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        airport_code: typing.Optional[typing.Sequence[builtins.str]] = None,
        alert_trigger_preferences: typing.Optional[typing.Sequence[builtins.str]] = None,
        alert_trigger_preferences_value: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[typing.Sequence[builtins.str]] = None,
        environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        event: typing.Optional[typing.Sequence[builtins.str]] = None,
        event_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        event_type: typing.Optional[typing.Sequence[builtins.str]] = None,
        group_by: typing.Optional[typing.Sequence[builtins.str]] = None,
        health_check_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        incident_impact: typing.Optional[typing.Sequence[builtins.str]] = None,
        input_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        insight_class: typing.Optional[typing.Sequence[builtins.str]] = None,
        limit: typing.Optional[typing.Sequence[builtins.str]] = None,
        logo_tag: typing.Optional[typing.Sequence[builtins.str]] = None,
        megabits_per_second: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_health: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_status: typing.Optional[typing.Sequence[builtins.str]] = None,
        packets_per_second: typing.Optional[typing.Sequence[builtins.str]] = None,
        pool_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        pop_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        product: typing.Optional[typing.Sequence[builtins.str]] = None,
        project_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        protocol: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_tag: typing.Optional[typing.Sequence[builtins.str]] = None,
        requests_per_second: typing.Optional[typing.Sequence[builtins.str]] = None,
        selectors: typing.Optional[typing.Sequence[builtins.str]] = None,
        services: typing.Optional[typing.Sequence[builtins.str]] = None,
        slo: typing.Optional[typing.Sequence[builtins.str]] = None,
        status: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_hostname: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_ip: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_zone_name: typing.Optional[typing.Sequence[builtins.str]] = None,
        traffic_exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tunnel_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        tunnel_name: typing.Optional[typing.Sequence[builtins.str]] = None,
        where: typing.Optional[typing.Sequence[builtins.str]] = None,
        zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param actions: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#actions NotificationPolicy#actions}
        :param affected_asns: Used for configuring radar_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#affected_asns NotificationPolicy#affected_asns}
        :param affected_components: Used for configuring incident_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#affected_components NotificationPolicy#affected_components}
        :param affected_locations: Used for configuring radar_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#affected_locations NotificationPolicy#affected_locations}
        :param airport_code: Used for configuring maintenance_event_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#airport_code NotificationPolicy#airport_code}
        :param alert_trigger_preferences: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_trigger_preferences NotificationPolicy#alert_trigger_preferences}
        :param alert_trigger_preferences_value: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_trigger_preferences_value NotificationPolicy#alert_trigger_preferences_value}
        :param enabled: Used for configuring load_balancing_pool_enablement_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#enabled NotificationPolicy#enabled}
        :param environment: Used for configuring pages_event_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#environment NotificationPolicy#environment}
        :param event: Used for configuring pages_event_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#event NotificationPolicy#event}
        :param event_source: Used for configuring load_balancing_health_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#event_source NotificationPolicy#event_source}
        :param event_type: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#event_type NotificationPolicy#event_type}
        :param group_by: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#group_by NotificationPolicy#group_by}
        :param health_check_id: Used for configuring health_check_status_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#health_check_id NotificationPolicy#health_check_id}
        :param incident_impact: Used for configuring incident_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#incident_impact NotificationPolicy#incident_impact}
        :param input_id: Used for configuring stream_live_notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#input_id NotificationPolicy#input_id}
        :param insight_class: Used for configuring security_insights_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#insight_class NotificationPolicy#insight_class}
        :param limit: Used for configuring billing_usage_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#limit NotificationPolicy#limit}
        :param logo_tag: Used for configuring logo_match_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#logo_tag NotificationPolicy#logo_tag}
        :param megabits_per_second: Used for configuring advanced_ddos_attack_l4_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#megabits_per_second NotificationPolicy#megabits_per_second}
        :param new_health: Used for configuring load_balancing_health_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#new_health NotificationPolicy#new_health}
        :param new_status: Used for configuring tunnel_health_event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#new_status NotificationPolicy#new_status}
        :param packets_per_second: Used for configuring advanced_ddos_attack_l4_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#packets_per_second NotificationPolicy#packets_per_second}
        :param pool_id: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#pool_id NotificationPolicy#pool_id}
        :param pop_names: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#pop_names NotificationPolicy#pop_names}
        :param product: Used for configuring billing_usage_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#product NotificationPolicy#product}
        :param project_id: Used for configuring pages_event_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#project_id NotificationPolicy#project_id}
        :param protocol: Used for configuring advanced_ddos_attack_l4_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#protocol NotificationPolicy#protocol}
        :param query_tag: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#query_tag NotificationPolicy#query_tag}
        :param requests_per_second: Used for configuring advanced_ddos_attack_l7_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#requests_per_second NotificationPolicy#requests_per_second}
        :param selectors: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#selectors NotificationPolicy#selectors}
        :param services: Used for configuring clickhouse_alert_fw_ent_anomaly. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#services NotificationPolicy#services}
        :param slo: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#slo NotificationPolicy#slo}
        :param status: Used for configuring health_check_status_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#status NotificationPolicy#status}
        :param target_hostname: Used for configuring advanced_ddos_attack_l7_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#target_hostname NotificationPolicy#target_hostname}
        :param target_ip: Used for configuring advanced_ddos_attack_l4_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#target_ip NotificationPolicy#target_ip}
        :param target_zone_name: Used for configuring advanced_ddos_attack_l7_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#target_zone_name NotificationPolicy#target_zone_name}
        :param traffic_exclusions: Used for configuring traffic_anomalies_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#traffic_exclusions NotificationPolicy#traffic_exclusions}
        :param tunnel_id: Used for configuring tunnel_health_event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#tunnel_id NotificationPolicy#tunnel_id}
        :param tunnel_name: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#tunnel_name NotificationPolicy#tunnel_name}
        :param where: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#where NotificationPolicy#where}
        :param zones: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#zones NotificationPolicy#zones}
        '''
        value = NotificationPolicyFilters(
            actions=actions,
            affected_asns=affected_asns,
            affected_components=affected_components,
            affected_locations=affected_locations,
            airport_code=airport_code,
            alert_trigger_preferences=alert_trigger_preferences,
            alert_trigger_preferences_value=alert_trigger_preferences_value,
            enabled=enabled,
            environment=environment,
            event=event,
            event_source=event_source,
            event_type=event_type,
            group_by=group_by,
            health_check_id=health_check_id,
            incident_impact=incident_impact,
            input_id=input_id,
            insight_class=insight_class,
            limit=limit,
            logo_tag=logo_tag,
            megabits_per_second=megabits_per_second,
            new_health=new_health,
            new_status=new_status,
            packets_per_second=packets_per_second,
            pool_id=pool_id,
            pop_names=pop_names,
            product=product,
            project_id=project_id,
            protocol=protocol,
            query_tag=query_tag,
            requests_per_second=requests_per_second,
            selectors=selectors,
            services=services,
            slo=slo,
            status=status,
            target_hostname=target_hostname,
            target_ip=target_ip,
            target_zone_name=target_zone_name,
            traffic_exclusions=traffic_exclusions,
            tunnel_id=tunnel_id,
            tunnel_name=tunnel_name,
            where=where,
            zones=zones,
        )

        return typing.cast(None, jsii.invoke(self, "putFilters", [value]))

    @jsii.member(jsii_name="putMechanisms")
    def put_mechanisms(
        self,
        *,
        email: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NotificationPolicyMechanismsEmail", typing.Dict[builtins.str, typing.Any]]]]] = None,
        pagerduty: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NotificationPolicyMechanismsPagerduty", typing.Dict[builtins.str, typing.Any]]]]] = None,
        webhooks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NotificationPolicyMechanismsWebhooks", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#email NotificationPolicy#email}.
        :param pagerduty: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#pagerduty NotificationPolicy#pagerduty}.
        :param webhooks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#webhooks NotificationPolicy#webhooks}.
        '''
        value = NotificationPolicyMechanisms(
            email=email, pagerduty=pagerduty, webhooks=webhooks
        )

        return typing.cast(None, jsii.invoke(self, "putMechanisms", [value]))

    @jsii.member(jsii_name="resetAlertInterval")
    def reset_alert_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertInterval", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetFilters")
    def reset_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilters", []))

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
    @jsii.member(jsii_name="created")
    def created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "created"))

    @builtins.property
    @jsii.member(jsii_name="filters")
    def filters(self) -> "NotificationPolicyFiltersOutputReference":
        return typing.cast("NotificationPolicyFiltersOutputReference", jsii.get(self, "filters"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="mechanisms")
    def mechanisms(self) -> "NotificationPolicyMechanismsOutputReference":
        return typing.cast("NotificationPolicyMechanismsOutputReference", jsii.get(self, "mechanisms"))

    @builtins.property
    @jsii.member(jsii_name="modified")
    def modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modified"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="alertIntervalInput")
    def alert_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alertIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="alertTypeInput")
    def alert_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alertTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="filtersInput")
    def filters_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "NotificationPolicyFilters"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "NotificationPolicyFilters"]], jsii.get(self, "filtersInput"))

    @builtins.property
    @jsii.member(jsii_name="mechanismsInput")
    def mechanisms_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "NotificationPolicyMechanisms"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "NotificationPolicyMechanisms"]], jsii.get(self, "mechanismsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12d61495632773ce0d55188dd5c264531790da548ad26191efd65e253d9ad7eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alertInterval")
    def alert_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alertInterval"))

    @alert_interval.setter
    def alert_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c9a9e9c1d66b8191cb35de5ab8690ce0b3a2fc36dee8347cd64eeb1e4793036)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alertType")
    def alert_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alertType"))

    @alert_type.setter
    def alert_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6c59bc8c4d370898c433afe11d54353dbb01e0117c5e68b0ebcca68e7bcdf69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df1ca562165db15d390fd123cc403797076f4dd2d4772623a50ab8a708b70143)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__b59f2fa90359289bd4f53cbe0d77c9cf06b5a6eee45e84f5d1ad1ad9d7481c80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c32685b847789725af6a3b296bc5149261a762977bb9e1060f4aedc88b42c842)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyConfig",
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
        "alert_type": "alertType",
        "mechanisms": "mechanisms",
        "name": "name",
        "alert_interval": "alertInterval",
        "description": "description",
        "enabled": "enabled",
        "filters": "filters",
    },
)
class NotificationPolicyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        alert_type: builtins.str,
        mechanisms: typing.Union["NotificationPolicyMechanisms", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        alert_interval: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        filters: typing.Optional[typing.Union["NotificationPolicyFilters", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: The account id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#account_id NotificationPolicy#account_id}
        :param alert_type: Refers to which event will trigger a Notification dispatch. You can use the endpoint to get available alert types which then will give you a list of possible values. Available values: "access_custom_certificate_expiration_type", "advanced_ddos_attack_l4_alert", "advanced_ddos_attack_l7_alert", "advanced_http_alert_error", "bgp_hijack_notification", "billing_usage_alert", "block_notification_block_removed", "block_notification_new_block", "block_notification_review_rejected", "bot_traffic_basic_alert", "brand_protection_alert", "brand_protection_digest", "clickhouse_alert_fw_anomaly", "clickhouse_alert_fw_ent_anomaly", "cloudforce_one_request_notification", "custom_analytics", "custom_bot_detection_alert", "custom_ssl_certificate_event_type", "dedicated_ssl_certificate_event_type", "device_connectivity_anomaly_alert", "dos_attack_l4", "dos_attack_l7", "expiring_service_token_alert", "failing_logpush_job_disabled_alert", "fbm_auto_advertisement", "fbm_dosd_attack", "fbm_volumetric_attack", "health_check_status_notification", "hostname_aop_custom_certificate_expiration_type", "http_alert_edge_error", "http_alert_origin_error", "image_notification", "image_resizing_notification", "incident_alert", "load_balancing_health_alert", "load_balancing_pool_enablement_alert", "logo_match_alert", "magic_tunnel_health_check_event", "magic_wan_tunnel_health", "maintenance_event_notification", "mtls_certificate_store_certificate_expiration_type", "pages_event_alert", "radar_notification", "real_origin_monitoring", "scriptmonitor_alert_new_code_change_detections", "scriptmonitor_alert_new_hosts", "scriptmonitor_alert_new_malicious_hosts", "scriptmonitor_alert_new_malicious_scripts", "scriptmonitor_alert_new_malicious_url", "scriptmonitor_alert_new_max_length_resource_url", "scriptmonitor_alert_new_resources", "secondary_dns_all_primaries_failing", "secondary_dns_primaries_failing", "secondary_dns_warning", "secondary_dns_zone_successfully_updated", "secondary_dns_zone_validation_warning", "security_insights_alert", "sentinel_alert", "stream_live_notifications", "synthetic_test_latency_alert", "synthetic_test_low_availability_alert", "traffic_anomalies_alert", "tunnel_health_event", "tunnel_update_event", "universal_ssl_event_type", "web_analytics_metrics_update", "zone_aop_custom_certificate_expiration_type". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_type NotificationPolicy#alert_type}
        :param mechanisms: List of IDs that will be used when dispatching a notification. IDs for email type will be the email address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#mechanisms NotificationPolicy#mechanisms}
        :param name: Name of the policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#name NotificationPolicy#name}
        :param alert_interval: Optional specification of how often to re-alert from the same incident, not support on all alert types. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_interval NotificationPolicy#alert_interval}
        :param description: Optional description for the Notification policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#description NotificationPolicy#description}
        :param enabled: Whether or not the Notification policy is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#enabled NotificationPolicy#enabled}
        :param filters: Optional filters that allow you to be alerted only on a subset of events for that alert type based on some criteria. This is only available for select alert types. See alert type documentation for more details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#filters NotificationPolicy#filters}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(mechanisms, dict):
            mechanisms = NotificationPolicyMechanisms(**mechanisms)
        if isinstance(filters, dict):
            filters = NotificationPolicyFilters(**filters)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bfdad0ea3b671f6ddd7c3f93399e6b1e1dbbec330f6748078f80895b3d1a900)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument alert_type", value=alert_type, expected_type=type_hints["alert_type"])
            check_type(argname="argument mechanisms", value=mechanisms, expected_type=type_hints["mechanisms"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument alert_interval", value=alert_interval, expected_type=type_hints["alert_interval"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "alert_type": alert_type,
            "mechanisms": mechanisms,
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
        if alert_interval is not None:
            self._values["alert_interval"] = alert_interval
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if filters is not None:
            self._values["filters"] = filters

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
        '''The account id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#account_id NotificationPolicy#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alert_type(self) -> builtins.str:
        '''Refers to which event will trigger a Notification dispatch.

        You can use the endpoint to get available alert types which then will give you a list of possible values.
        Available values: "access_custom_certificate_expiration_type", "advanced_ddos_attack_l4_alert", "advanced_ddos_attack_l7_alert", "advanced_http_alert_error", "bgp_hijack_notification", "billing_usage_alert", "block_notification_block_removed", "block_notification_new_block", "block_notification_review_rejected", "bot_traffic_basic_alert", "brand_protection_alert", "brand_protection_digest", "clickhouse_alert_fw_anomaly", "clickhouse_alert_fw_ent_anomaly", "cloudforce_one_request_notification", "custom_analytics", "custom_bot_detection_alert", "custom_ssl_certificate_event_type", "dedicated_ssl_certificate_event_type", "device_connectivity_anomaly_alert", "dos_attack_l4", "dos_attack_l7", "expiring_service_token_alert", "failing_logpush_job_disabled_alert", "fbm_auto_advertisement", "fbm_dosd_attack", "fbm_volumetric_attack", "health_check_status_notification", "hostname_aop_custom_certificate_expiration_type", "http_alert_edge_error", "http_alert_origin_error", "image_notification", "image_resizing_notification", "incident_alert", "load_balancing_health_alert", "load_balancing_pool_enablement_alert", "logo_match_alert", "magic_tunnel_health_check_event", "magic_wan_tunnel_health", "maintenance_event_notification", "mtls_certificate_store_certificate_expiration_type", "pages_event_alert", "radar_notification", "real_origin_monitoring", "scriptmonitor_alert_new_code_change_detections", "scriptmonitor_alert_new_hosts", "scriptmonitor_alert_new_malicious_hosts", "scriptmonitor_alert_new_malicious_scripts", "scriptmonitor_alert_new_malicious_url", "scriptmonitor_alert_new_max_length_resource_url", "scriptmonitor_alert_new_resources", "secondary_dns_all_primaries_failing", "secondary_dns_primaries_failing", "secondary_dns_warning", "secondary_dns_zone_successfully_updated", "secondary_dns_zone_validation_warning", "security_insights_alert", "sentinel_alert", "stream_live_notifications", "synthetic_test_latency_alert", "synthetic_test_low_availability_alert", "traffic_anomalies_alert", "tunnel_health_event", "tunnel_update_event", "universal_ssl_event_type", "web_analytics_metrics_update", "zone_aop_custom_certificate_expiration_type".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_type NotificationPolicy#alert_type}
        '''
        result = self._values.get("alert_type")
        assert result is not None, "Required property 'alert_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mechanisms(self) -> "NotificationPolicyMechanisms":
        '''List of IDs that will be used when dispatching a notification.

        IDs for email type will be the email address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#mechanisms NotificationPolicy#mechanisms}
        '''
        result = self._values.get("mechanisms")
        assert result is not None, "Required property 'mechanisms' is missing"
        return typing.cast("NotificationPolicyMechanisms", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#name NotificationPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alert_interval(self) -> typing.Optional[builtins.str]:
        '''Optional specification of how often to re-alert from the same incident, not support on all alert types.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_interval NotificationPolicy#alert_interval}
        '''
        result = self._values.get("alert_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Optional description for the Notification policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#description NotificationPolicy#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether or not the Notification policy is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#enabled NotificationPolicy#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def filters(self) -> typing.Optional["NotificationPolicyFilters"]:
        '''Optional filters that allow you to be alerted only on a subset of events for that alert type based on some criteria.

        This is only available for select alert types. See alert type documentation for more details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#filters NotificationPolicy#filters}
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional["NotificationPolicyFilters"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyFilters",
    jsii_struct_bases=[],
    name_mapping={
        "actions": "actions",
        "affected_asns": "affectedAsns",
        "affected_components": "affectedComponents",
        "affected_locations": "affectedLocations",
        "airport_code": "airportCode",
        "alert_trigger_preferences": "alertTriggerPreferences",
        "alert_trigger_preferences_value": "alertTriggerPreferencesValue",
        "enabled": "enabled",
        "environment": "environment",
        "event": "event",
        "event_source": "eventSource",
        "event_type": "eventType",
        "group_by": "groupBy",
        "health_check_id": "healthCheckId",
        "incident_impact": "incidentImpact",
        "input_id": "inputId",
        "insight_class": "insightClass",
        "limit": "limit",
        "logo_tag": "logoTag",
        "megabits_per_second": "megabitsPerSecond",
        "new_health": "newHealth",
        "new_status": "newStatus",
        "packets_per_second": "packetsPerSecond",
        "pool_id": "poolId",
        "pop_names": "popNames",
        "product": "product",
        "project_id": "projectId",
        "protocol": "protocol",
        "query_tag": "queryTag",
        "requests_per_second": "requestsPerSecond",
        "selectors": "selectors",
        "services": "services",
        "slo": "slo",
        "status": "status",
        "target_hostname": "targetHostname",
        "target_ip": "targetIp",
        "target_zone_name": "targetZoneName",
        "traffic_exclusions": "trafficExclusions",
        "tunnel_id": "tunnelId",
        "tunnel_name": "tunnelName",
        "where": "where",
        "zones": "zones",
    },
)
class NotificationPolicyFilters:
    def __init__(
        self,
        *,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        affected_asns: typing.Optional[typing.Sequence[builtins.str]] = None,
        affected_components: typing.Optional[typing.Sequence[builtins.str]] = None,
        affected_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        airport_code: typing.Optional[typing.Sequence[builtins.str]] = None,
        alert_trigger_preferences: typing.Optional[typing.Sequence[builtins.str]] = None,
        alert_trigger_preferences_value: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[typing.Sequence[builtins.str]] = None,
        environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        event: typing.Optional[typing.Sequence[builtins.str]] = None,
        event_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        event_type: typing.Optional[typing.Sequence[builtins.str]] = None,
        group_by: typing.Optional[typing.Sequence[builtins.str]] = None,
        health_check_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        incident_impact: typing.Optional[typing.Sequence[builtins.str]] = None,
        input_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        insight_class: typing.Optional[typing.Sequence[builtins.str]] = None,
        limit: typing.Optional[typing.Sequence[builtins.str]] = None,
        logo_tag: typing.Optional[typing.Sequence[builtins.str]] = None,
        megabits_per_second: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_health: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_status: typing.Optional[typing.Sequence[builtins.str]] = None,
        packets_per_second: typing.Optional[typing.Sequence[builtins.str]] = None,
        pool_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        pop_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        product: typing.Optional[typing.Sequence[builtins.str]] = None,
        project_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        protocol: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_tag: typing.Optional[typing.Sequence[builtins.str]] = None,
        requests_per_second: typing.Optional[typing.Sequence[builtins.str]] = None,
        selectors: typing.Optional[typing.Sequence[builtins.str]] = None,
        services: typing.Optional[typing.Sequence[builtins.str]] = None,
        slo: typing.Optional[typing.Sequence[builtins.str]] = None,
        status: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_hostname: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_ip: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_zone_name: typing.Optional[typing.Sequence[builtins.str]] = None,
        traffic_exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tunnel_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        tunnel_name: typing.Optional[typing.Sequence[builtins.str]] = None,
        where: typing.Optional[typing.Sequence[builtins.str]] = None,
        zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param actions: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#actions NotificationPolicy#actions}
        :param affected_asns: Used for configuring radar_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#affected_asns NotificationPolicy#affected_asns}
        :param affected_components: Used for configuring incident_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#affected_components NotificationPolicy#affected_components}
        :param affected_locations: Used for configuring radar_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#affected_locations NotificationPolicy#affected_locations}
        :param airport_code: Used for configuring maintenance_event_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#airport_code NotificationPolicy#airport_code}
        :param alert_trigger_preferences: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_trigger_preferences NotificationPolicy#alert_trigger_preferences}
        :param alert_trigger_preferences_value: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_trigger_preferences_value NotificationPolicy#alert_trigger_preferences_value}
        :param enabled: Used for configuring load_balancing_pool_enablement_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#enabled NotificationPolicy#enabled}
        :param environment: Used for configuring pages_event_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#environment NotificationPolicy#environment}
        :param event: Used for configuring pages_event_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#event NotificationPolicy#event}
        :param event_source: Used for configuring load_balancing_health_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#event_source NotificationPolicy#event_source}
        :param event_type: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#event_type NotificationPolicy#event_type}
        :param group_by: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#group_by NotificationPolicy#group_by}
        :param health_check_id: Used for configuring health_check_status_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#health_check_id NotificationPolicy#health_check_id}
        :param incident_impact: Used for configuring incident_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#incident_impact NotificationPolicy#incident_impact}
        :param input_id: Used for configuring stream_live_notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#input_id NotificationPolicy#input_id}
        :param insight_class: Used for configuring security_insights_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#insight_class NotificationPolicy#insight_class}
        :param limit: Used for configuring billing_usage_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#limit NotificationPolicy#limit}
        :param logo_tag: Used for configuring logo_match_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#logo_tag NotificationPolicy#logo_tag}
        :param megabits_per_second: Used for configuring advanced_ddos_attack_l4_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#megabits_per_second NotificationPolicy#megabits_per_second}
        :param new_health: Used for configuring load_balancing_health_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#new_health NotificationPolicy#new_health}
        :param new_status: Used for configuring tunnel_health_event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#new_status NotificationPolicy#new_status}
        :param packets_per_second: Used for configuring advanced_ddos_attack_l4_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#packets_per_second NotificationPolicy#packets_per_second}
        :param pool_id: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#pool_id NotificationPolicy#pool_id}
        :param pop_names: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#pop_names NotificationPolicy#pop_names}
        :param product: Used for configuring billing_usage_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#product NotificationPolicy#product}
        :param project_id: Used for configuring pages_event_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#project_id NotificationPolicy#project_id}
        :param protocol: Used for configuring advanced_ddos_attack_l4_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#protocol NotificationPolicy#protocol}
        :param query_tag: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#query_tag NotificationPolicy#query_tag}
        :param requests_per_second: Used for configuring advanced_ddos_attack_l7_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#requests_per_second NotificationPolicy#requests_per_second}
        :param selectors: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#selectors NotificationPolicy#selectors}
        :param services: Used for configuring clickhouse_alert_fw_ent_anomaly. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#services NotificationPolicy#services}
        :param slo: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#slo NotificationPolicy#slo}
        :param status: Used for configuring health_check_status_notification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#status NotificationPolicy#status}
        :param target_hostname: Used for configuring advanced_ddos_attack_l7_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#target_hostname NotificationPolicy#target_hostname}
        :param target_ip: Used for configuring advanced_ddos_attack_l4_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#target_ip NotificationPolicy#target_ip}
        :param target_zone_name: Used for configuring advanced_ddos_attack_l7_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#target_zone_name NotificationPolicy#target_zone_name}
        :param traffic_exclusions: Used for configuring traffic_anomalies_alert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#traffic_exclusions NotificationPolicy#traffic_exclusions}
        :param tunnel_id: Used for configuring tunnel_health_event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#tunnel_id NotificationPolicy#tunnel_id}
        :param tunnel_name: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#tunnel_name NotificationPolicy#tunnel_name}
        :param where: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#where NotificationPolicy#where}
        :param zones: Usage depends on specific alert type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#zones NotificationPolicy#zones}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5326ebf108453b36da8e814edd860719cbe2916d2193ee3d49f18c8694c6ff6)
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument affected_asns", value=affected_asns, expected_type=type_hints["affected_asns"])
            check_type(argname="argument affected_components", value=affected_components, expected_type=type_hints["affected_components"])
            check_type(argname="argument affected_locations", value=affected_locations, expected_type=type_hints["affected_locations"])
            check_type(argname="argument airport_code", value=airport_code, expected_type=type_hints["airport_code"])
            check_type(argname="argument alert_trigger_preferences", value=alert_trigger_preferences, expected_type=type_hints["alert_trigger_preferences"])
            check_type(argname="argument alert_trigger_preferences_value", value=alert_trigger_preferences_value, expected_type=type_hints["alert_trigger_preferences_value"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument event", value=event, expected_type=type_hints["event"])
            check_type(argname="argument event_source", value=event_source, expected_type=type_hints["event_source"])
            check_type(argname="argument event_type", value=event_type, expected_type=type_hints["event_type"])
            check_type(argname="argument group_by", value=group_by, expected_type=type_hints["group_by"])
            check_type(argname="argument health_check_id", value=health_check_id, expected_type=type_hints["health_check_id"])
            check_type(argname="argument incident_impact", value=incident_impact, expected_type=type_hints["incident_impact"])
            check_type(argname="argument input_id", value=input_id, expected_type=type_hints["input_id"])
            check_type(argname="argument insight_class", value=insight_class, expected_type=type_hints["insight_class"])
            check_type(argname="argument limit", value=limit, expected_type=type_hints["limit"])
            check_type(argname="argument logo_tag", value=logo_tag, expected_type=type_hints["logo_tag"])
            check_type(argname="argument megabits_per_second", value=megabits_per_second, expected_type=type_hints["megabits_per_second"])
            check_type(argname="argument new_health", value=new_health, expected_type=type_hints["new_health"])
            check_type(argname="argument new_status", value=new_status, expected_type=type_hints["new_status"])
            check_type(argname="argument packets_per_second", value=packets_per_second, expected_type=type_hints["packets_per_second"])
            check_type(argname="argument pool_id", value=pool_id, expected_type=type_hints["pool_id"])
            check_type(argname="argument pop_names", value=pop_names, expected_type=type_hints["pop_names"])
            check_type(argname="argument product", value=product, expected_type=type_hints["product"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument query_tag", value=query_tag, expected_type=type_hints["query_tag"])
            check_type(argname="argument requests_per_second", value=requests_per_second, expected_type=type_hints["requests_per_second"])
            check_type(argname="argument selectors", value=selectors, expected_type=type_hints["selectors"])
            check_type(argname="argument services", value=services, expected_type=type_hints["services"])
            check_type(argname="argument slo", value=slo, expected_type=type_hints["slo"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument target_hostname", value=target_hostname, expected_type=type_hints["target_hostname"])
            check_type(argname="argument target_ip", value=target_ip, expected_type=type_hints["target_ip"])
            check_type(argname="argument target_zone_name", value=target_zone_name, expected_type=type_hints["target_zone_name"])
            check_type(argname="argument traffic_exclusions", value=traffic_exclusions, expected_type=type_hints["traffic_exclusions"])
            check_type(argname="argument tunnel_id", value=tunnel_id, expected_type=type_hints["tunnel_id"])
            check_type(argname="argument tunnel_name", value=tunnel_name, expected_type=type_hints["tunnel_name"])
            check_type(argname="argument where", value=where, expected_type=type_hints["where"])
            check_type(argname="argument zones", value=zones, expected_type=type_hints["zones"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if actions is not None:
            self._values["actions"] = actions
        if affected_asns is not None:
            self._values["affected_asns"] = affected_asns
        if affected_components is not None:
            self._values["affected_components"] = affected_components
        if affected_locations is not None:
            self._values["affected_locations"] = affected_locations
        if airport_code is not None:
            self._values["airport_code"] = airport_code
        if alert_trigger_preferences is not None:
            self._values["alert_trigger_preferences"] = alert_trigger_preferences
        if alert_trigger_preferences_value is not None:
            self._values["alert_trigger_preferences_value"] = alert_trigger_preferences_value
        if enabled is not None:
            self._values["enabled"] = enabled
        if environment is not None:
            self._values["environment"] = environment
        if event is not None:
            self._values["event"] = event
        if event_source is not None:
            self._values["event_source"] = event_source
        if event_type is not None:
            self._values["event_type"] = event_type
        if group_by is not None:
            self._values["group_by"] = group_by
        if health_check_id is not None:
            self._values["health_check_id"] = health_check_id
        if incident_impact is not None:
            self._values["incident_impact"] = incident_impact
        if input_id is not None:
            self._values["input_id"] = input_id
        if insight_class is not None:
            self._values["insight_class"] = insight_class
        if limit is not None:
            self._values["limit"] = limit
        if logo_tag is not None:
            self._values["logo_tag"] = logo_tag
        if megabits_per_second is not None:
            self._values["megabits_per_second"] = megabits_per_second
        if new_health is not None:
            self._values["new_health"] = new_health
        if new_status is not None:
            self._values["new_status"] = new_status
        if packets_per_second is not None:
            self._values["packets_per_second"] = packets_per_second
        if pool_id is not None:
            self._values["pool_id"] = pool_id
        if pop_names is not None:
            self._values["pop_names"] = pop_names
        if product is not None:
            self._values["product"] = product
        if project_id is not None:
            self._values["project_id"] = project_id
        if protocol is not None:
            self._values["protocol"] = protocol
        if query_tag is not None:
            self._values["query_tag"] = query_tag
        if requests_per_second is not None:
            self._values["requests_per_second"] = requests_per_second
        if selectors is not None:
            self._values["selectors"] = selectors
        if services is not None:
            self._values["services"] = services
        if slo is not None:
            self._values["slo"] = slo
        if status is not None:
            self._values["status"] = status
        if target_hostname is not None:
            self._values["target_hostname"] = target_hostname
        if target_ip is not None:
            self._values["target_ip"] = target_ip
        if target_zone_name is not None:
            self._values["target_zone_name"] = target_zone_name
        if traffic_exclusions is not None:
            self._values["traffic_exclusions"] = traffic_exclusions
        if tunnel_id is not None:
            self._values["tunnel_id"] = tunnel_id
        if tunnel_name is not None:
            self._values["tunnel_name"] = tunnel_name
        if where is not None:
            self._values["where"] = where
        if zones is not None:
            self._values["zones"] = zones

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#actions NotificationPolicy#actions}
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def affected_asns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring radar_notification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#affected_asns NotificationPolicy#affected_asns}
        '''
        result = self._values.get("affected_asns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def affected_components(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring incident_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#affected_components NotificationPolicy#affected_components}
        '''
        result = self._values.get("affected_components")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def affected_locations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring radar_notification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#affected_locations NotificationPolicy#affected_locations}
        '''
        result = self._values.get("affected_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def airport_code(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring maintenance_event_notification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#airport_code NotificationPolicy#airport_code}
        '''
        result = self._values.get("airport_code")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def alert_trigger_preferences(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_trigger_preferences NotificationPolicy#alert_trigger_preferences}
        '''
        result = self._values.get("alert_trigger_preferences")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def alert_trigger_preferences_value(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#alert_trigger_preferences_value NotificationPolicy#alert_trigger_preferences_value}
        '''
        result = self._values.get("alert_trigger_preferences_value")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring load_balancing_pool_enablement_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#enabled NotificationPolicy#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring pages_event_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#environment NotificationPolicy#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def event(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring pages_event_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#event NotificationPolicy#event}
        '''
        result = self._values.get("event")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def event_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring load_balancing_health_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#event_source NotificationPolicy#event_source}
        '''
        result = self._values.get("event_source")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def event_type(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#event_type NotificationPolicy#event_type}
        '''
        result = self._values.get("event_type")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def group_by(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#group_by NotificationPolicy#group_by}
        '''
        result = self._values.get("group_by")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def health_check_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring health_check_status_notification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#health_check_id NotificationPolicy#health_check_id}
        '''
        result = self._values.get("health_check_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def incident_impact(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring incident_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#incident_impact NotificationPolicy#incident_impact}
        '''
        result = self._values.get("incident_impact")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def input_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring stream_live_notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#input_id NotificationPolicy#input_id}
        '''
        result = self._values.get("input_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def insight_class(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring security_insights_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#insight_class NotificationPolicy#insight_class}
        '''
        result = self._values.get("insight_class")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def limit(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring billing_usage_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#limit NotificationPolicy#limit}
        '''
        result = self._values.get("limit")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def logo_tag(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring logo_match_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#logo_tag NotificationPolicy#logo_tag}
        '''
        result = self._values.get("logo_tag")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def megabits_per_second(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring advanced_ddos_attack_l4_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#megabits_per_second NotificationPolicy#megabits_per_second}
        '''
        result = self._values.get("megabits_per_second")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_health(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring load_balancing_health_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#new_health NotificationPolicy#new_health}
        '''
        result = self._values.get("new_health")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_status(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring tunnel_health_event.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#new_status NotificationPolicy#new_status}
        '''
        result = self._values.get("new_status")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def packets_per_second(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring advanced_ddos_attack_l4_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#packets_per_second NotificationPolicy#packets_per_second}
        '''
        result = self._values.get("packets_per_second")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pool_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#pool_id NotificationPolicy#pool_id}
        '''
        result = self._values.get("pool_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pop_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#pop_names NotificationPolicy#pop_names}
        '''
        result = self._values.get("pop_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def product(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring billing_usage_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#product NotificationPolicy#product}
        '''
        result = self._values.get("product")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def project_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring pages_event_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#project_id NotificationPolicy#project_id}
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def protocol(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring advanced_ddos_attack_l4_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#protocol NotificationPolicy#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_tag(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#query_tag NotificationPolicy#query_tag}
        '''
        result = self._values.get("query_tag")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def requests_per_second(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring advanced_ddos_attack_l7_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#requests_per_second NotificationPolicy#requests_per_second}
        '''
        result = self._values.get("requests_per_second")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def selectors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#selectors NotificationPolicy#selectors}
        '''
        result = self._values.get("selectors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def services(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring clickhouse_alert_fw_ent_anomaly.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#services NotificationPolicy#services}
        '''
        result = self._values.get("services")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def slo(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#slo NotificationPolicy#slo}
        '''
        result = self._values.get("slo")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def status(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring health_check_status_notification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#status NotificationPolicy#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_hostname(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring advanced_ddos_attack_l7_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#target_hostname NotificationPolicy#target_hostname}
        '''
        result = self._values.get("target_hostname")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_ip(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring advanced_ddos_attack_l4_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#target_ip NotificationPolicy#target_ip}
        '''
        result = self._values.get("target_ip")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_zone_name(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring advanced_ddos_attack_l7_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#target_zone_name NotificationPolicy#target_zone_name}
        '''
        result = self._values.get("target_zone_name")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def traffic_exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring traffic_anomalies_alert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#traffic_exclusions NotificationPolicy#traffic_exclusions}
        '''
        result = self._values.get("traffic_exclusions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tunnel_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Used for configuring tunnel_health_event.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#tunnel_id NotificationPolicy#tunnel_id}
        '''
        result = self._values.get("tunnel_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tunnel_name(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#tunnel_name NotificationPolicy#tunnel_name}
        '''
        result = self._values.get("tunnel_name")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def where(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#where NotificationPolicy#where}
        '''
        result = self._values.get("where")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Usage depends on specific alert type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#zones NotificationPolicy#zones}
        '''
        result = self._values.get("zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationPolicyFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationPolicyFiltersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyFiltersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8f31f649dafa1c3b6903338e913d967b05f75e2592e91fc18bbbf5a9a72cbcb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetActions")
    def reset_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActions", []))

    @jsii.member(jsii_name="resetAffectedAsns")
    def reset_affected_asns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAffectedAsns", []))

    @jsii.member(jsii_name="resetAffectedComponents")
    def reset_affected_components(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAffectedComponents", []))

    @jsii.member(jsii_name="resetAffectedLocations")
    def reset_affected_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAffectedLocations", []))

    @jsii.member(jsii_name="resetAirportCode")
    def reset_airport_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAirportCode", []))

    @jsii.member(jsii_name="resetAlertTriggerPreferences")
    def reset_alert_trigger_preferences(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertTriggerPreferences", []))

    @jsii.member(jsii_name="resetAlertTriggerPreferencesValue")
    def reset_alert_trigger_preferences_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertTriggerPreferencesValue", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetEvent")
    def reset_event(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvent", []))

    @jsii.member(jsii_name="resetEventSource")
    def reset_event_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventSource", []))

    @jsii.member(jsii_name="resetEventType")
    def reset_event_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventType", []))

    @jsii.member(jsii_name="resetGroupBy")
    def reset_group_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupBy", []))

    @jsii.member(jsii_name="resetHealthCheckId")
    def reset_health_check_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckId", []))

    @jsii.member(jsii_name="resetIncidentImpact")
    def reset_incident_impact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncidentImpact", []))

    @jsii.member(jsii_name="resetInputId")
    def reset_input_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInputId", []))

    @jsii.member(jsii_name="resetInsightClass")
    def reset_insight_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsightClass", []))

    @jsii.member(jsii_name="resetLimit")
    def reset_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLimit", []))

    @jsii.member(jsii_name="resetLogoTag")
    def reset_logo_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogoTag", []))

    @jsii.member(jsii_name="resetMegabitsPerSecond")
    def reset_megabits_per_second(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMegabitsPerSecond", []))

    @jsii.member(jsii_name="resetNewHealth")
    def reset_new_health(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewHealth", []))

    @jsii.member(jsii_name="resetNewStatus")
    def reset_new_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewStatus", []))

    @jsii.member(jsii_name="resetPacketsPerSecond")
    def reset_packets_per_second(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPacketsPerSecond", []))

    @jsii.member(jsii_name="resetPoolId")
    def reset_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPoolId", []))

    @jsii.member(jsii_name="resetPopNames")
    def reset_pop_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPopNames", []))

    @jsii.member(jsii_name="resetProduct")
    def reset_product(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProduct", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @jsii.member(jsii_name="resetQueryTag")
    def reset_query_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryTag", []))

    @jsii.member(jsii_name="resetRequestsPerSecond")
    def reset_requests_per_second(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestsPerSecond", []))

    @jsii.member(jsii_name="resetSelectors")
    def reset_selectors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelectors", []))

    @jsii.member(jsii_name="resetServices")
    def reset_services(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServices", []))

    @jsii.member(jsii_name="resetSlo")
    def reset_slo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlo", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetTargetHostname")
    def reset_target_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetHostname", []))

    @jsii.member(jsii_name="resetTargetIp")
    def reset_target_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetIp", []))

    @jsii.member(jsii_name="resetTargetZoneName")
    def reset_target_zone_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetZoneName", []))

    @jsii.member(jsii_name="resetTrafficExclusions")
    def reset_traffic_exclusions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrafficExclusions", []))

    @jsii.member(jsii_name="resetTunnelId")
    def reset_tunnel_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTunnelId", []))

    @jsii.member(jsii_name="resetTunnelName")
    def reset_tunnel_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTunnelName", []))

    @jsii.member(jsii_name="resetWhere")
    def reset_where(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhere", []))

    @jsii.member(jsii_name="resetZones")
    def reset_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZones", []))

    @builtins.property
    @jsii.member(jsii_name="actionsInput")
    def actions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "actionsInput"))

    @builtins.property
    @jsii.member(jsii_name="affectedAsnsInput")
    def affected_asns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "affectedAsnsInput"))

    @builtins.property
    @jsii.member(jsii_name="affectedComponentsInput")
    def affected_components_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "affectedComponentsInput"))

    @builtins.property
    @jsii.member(jsii_name="affectedLocationsInput")
    def affected_locations_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "affectedLocationsInput"))

    @builtins.property
    @jsii.member(jsii_name="airportCodeInput")
    def airport_code_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "airportCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="alertTriggerPreferencesInput")
    def alert_trigger_preferences_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "alertTriggerPreferencesInput"))

    @builtins.property
    @jsii.member(jsii_name="alertTriggerPreferencesValueInput")
    def alert_trigger_preferences_value_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "alertTriggerPreferencesValueInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "environmentInput"))

    @builtins.property
    @jsii.member(jsii_name="eventInput")
    def event_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventInput"))

    @builtins.property
    @jsii.member(jsii_name="eventSourceInput")
    def event_source_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventSourceInput"))

    @builtins.property
    @jsii.member(jsii_name="eventTypeInput")
    def event_type_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="groupByInput")
    def group_by_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "groupByInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckIdInput")
    def health_check_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "healthCheckIdInput"))

    @builtins.property
    @jsii.member(jsii_name="incidentImpactInput")
    def incident_impact_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "incidentImpactInput"))

    @builtins.property
    @jsii.member(jsii_name="inputIdInput")
    def input_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "inputIdInput"))

    @builtins.property
    @jsii.member(jsii_name="insightClassInput")
    def insight_class_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "insightClassInput"))

    @builtins.property
    @jsii.member(jsii_name="limitInput")
    def limit_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "limitInput"))

    @builtins.property
    @jsii.member(jsii_name="logoTagInput")
    def logo_tag_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "logoTagInput"))

    @builtins.property
    @jsii.member(jsii_name="megabitsPerSecondInput")
    def megabits_per_second_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "megabitsPerSecondInput"))

    @builtins.property
    @jsii.member(jsii_name="newHealthInput")
    def new_health_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "newHealthInput"))

    @builtins.property
    @jsii.member(jsii_name="newStatusInput")
    def new_status_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "newStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="packetsPerSecondInput")
    def packets_per_second_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "packetsPerSecondInput"))

    @builtins.property
    @jsii.member(jsii_name="poolIdInput")
    def pool_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "poolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="popNamesInput")
    def pop_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "popNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="productInput")
    def product_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "productInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="queryTagInput")
    def query_tag_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "queryTagInput"))

    @builtins.property
    @jsii.member(jsii_name="requestsPerSecondInput")
    def requests_per_second_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "requestsPerSecondInput"))

    @builtins.property
    @jsii.member(jsii_name="selectorsInput")
    def selectors_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "selectorsInput"))

    @builtins.property
    @jsii.member(jsii_name="servicesInput")
    def services_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "servicesInput"))

    @builtins.property
    @jsii.member(jsii_name="sloInput")
    def slo_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sloInput"))

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="targetHostnameInput")
    def target_hostname_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetHostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="targetIpInput")
    def target_ip_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetIpInput"))

    @builtins.property
    @jsii.member(jsii_name="targetZoneNameInput")
    def target_zone_name_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetZoneNameInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficExclusionsInput")
    def traffic_exclusions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "trafficExclusionsInput"))

    @builtins.property
    @jsii.member(jsii_name="tunnelIdInput")
    def tunnel_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tunnelIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tunnelNameInput")
    def tunnel_name_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tunnelNameInput"))

    @builtins.property
    @jsii.member(jsii_name="whereInput")
    def where_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "whereInput"))

    @builtins.property
    @jsii.member(jsii_name="zonesInput")
    def zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "zonesInput"))

    @builtins.property
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "actions"))

    @actions.setter
    def actions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cbd740b090d5dcb3f98c1a4b6ff1a0651678c49b1243b284e7acc76e721589c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="affectedAsns")
    def affected_asns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "affectedAsns"))

    @affected_asns.setter
    def affected_asns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca8453685cafe9cd71fdae536de943da85d58d601fa0d3597cf5e8edaf3ed821)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "affectedAsns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="affectedComponents")
    def affected_components(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "affectedComponents"))

    @affected_components.setter
    def affected_components(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__115da5f87a19dafbf96877c6df454a434fa82dee931e598988a1c5ff0eca9fa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "affectedComponents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="affectedLocations")
    def affected_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "affectedLocations"))

    @affected_locations.setter
    def affected_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25aa83c53d8d267873a08acb206693fadb0f1763dbade9e3e7f9192a48724a7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "affectedLocations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="airportCode")
    def airport_code(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "airportCode"))

    @airport_code.setter
    def airport_code(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d941b7b7c50ceac8552ec74cb449a272d2e6a82dbca9e8d05722e7093b8aa012)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "airportCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alertTriggerPreferences")
    def alert_trigger_preferences(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "alertTriggerPreferences"))

    @alert_trigger_preferences.setter
    def alert_trigger_preferences(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a8320bc1ab0055c005acf8e4d040f5ec3002105ebf206ab47f5525b66cdf017)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertTriggerPreferences", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alertTriggerPreferencesValue")
    def alert_trigger_preferences_value(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "alertTriggerPreferencesValue"))

    @alert_trigger_preferences_value.setter
    def alert_trigger_preferences_value(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4112ba005a7db01c8e0a5f36be0b9011cf9cfc9c7584ec2ad4b2c99beccacc43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertTriggerPreferencesValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b6ee8a77ab98e8abcf11477f1b4e4218a4a26478a7b259ee789af85016e8618)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb0a14683d0f88547af387c7869591ec8197b90a02b0892486f5d8c23ef17565)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="event")
    def event(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "event"))

    @event.setter
    def event(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a4a91dd52f49b0fec512d8e17d8b8240f99bc3f39fa0ee67625df8dace723e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "event", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eventSource")
    def event_source(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventSource"))

    @event_source.setter
    def event_source(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3df89f3b37f251c30996df91f244b0e38e4c03fd32e227ef4866d53db10c4f71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventSource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventType"))

    @event_type.setter
    def event_type(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86846fba85173ea61eaef275166914e708d9a78cc98774322e89a5507120a689)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupBy")
    def group_by(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "groupBy"))

    @group_by.setter
    def group_by(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e978f4cf3db6c6b55f6b53bb973d85fa4170a68f295507309a67a4f395b50c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckId")
    def health_check_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "healthCheckId"))

    @health_check_id.setter
    def health_check_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c36e1d871dafdc1ec7b5ca7ef3c1e55d5e3fffff205f8f6e393e16559a71d94a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="incidentImpact")
    def incident_impact(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "incidentImpact"))

    @incident_impact.setter
    def incident_impact(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13313e393833d80e078d2cd462aff18800b7798f22b77741274bf92e597618cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "incidentImpact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inputId")
    def input_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "inputId"))

    @input_id.setter
    def input_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13749ce4d14ee4d47ca2b743593e0ea6f8c5d1e90db0b4187cef46c6281fc868)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insightClass")
    def insight_class(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "insightClass"))

    @insight_class.setter
    def insight_class(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e1e16b04dba7e10647a5a79797d98239ca7aa833ce837df866e84c002fbea0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insightClass", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="limit")
    def limit(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "limit"))

    @limit.setter
    def limit(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c7cb06df8ae94848c7d39371bb6bd7cafdd6893fc1fa40c3e9a95e769691bbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "limit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logoTag")
    def logo_tag(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "logoTag"))

    @logo_tag.setter
    def logo_tag(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71e2349bff2229c072d107c896611c7fc7aae80dcd678fe364f22e72fe48d52e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logoTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="megabitsPerSecond")
    def megabits_per_second(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "megabitsPerSecond"))

    @megabits_per_second.setter
    def megabits_per_second(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2e46433a07b7996ca9c557720a807d2654d178508bcf210b8a79c277a55678d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "megabitsPerSecond", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newHealth")
    def new_health(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newHealth"))

    @new_health.setter
    def new_health(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__966097109aab71dd336a62096323ee6c5a20d6f9e5eb6ad3da692d10466d7f30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newHealth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newStatus")
    def new_status(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newStatus"))

    @new_status.setter
    def new_status(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9d1aedf12f36c5e87a2c7c4dd88494cd6c4ed2ef80edab2f726408ac75ffa3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="packetsPerSecond")
    def packets_per_second(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "packetsPerSecond"))

    @packets_per_second.setter
    def packets_per_second(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5426e77e9e8c318d485d667eeae7786bf21d76bb73e66167a78b6e56bd60a267)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "packetsPerSecond", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="poolId")
    def pool_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "poolId"))

    @pool_id.setter
    def pool_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc505ad097f5dfa3183501da19ee617059ab758a68300726c93efd8db22c9581)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "poolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="popNames")
    def pop_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "popNames"))

    @pop_names.setter
    def pop_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dbf97e89228341486c4942909cd1030b0d64a351358f834cd61ecfee203d92e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "popNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="product")
    def product(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "product"))

    @product.setter
    def product(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2734761a5311a1478499b1a47a670c6c381a85a844cad3ede6ff97dd200176c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "product", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00c01b98586d5f97b73f117d41a62c0b7ee62fdc73706705cda00665cc6fe996)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb8231efaeb8ff5412b70a100e1e1e8fe333cd173c99bba7c99c2add01119d6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryTag")
    def query_tag(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "queryTag"))

    @query_tag.setter
    def query_tag(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f55e35df35e567089be6cac46d39fdd9427559f5de41d9da0828c53ee12ed37f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestsPerSecond")
    def requests_per_second(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "requestsPerSecond"))

    @requests_per_second.setter
    def requests_per_second(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0210adff9def3da2b344737aced573e739cc90b4b559ab475c8dcf6ad23fcce2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestsPerSecond", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="selectors")
    def selectors(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "selectors"))

    @selectors.setter
    def selectors(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc62169f354fdaea6f58699f464b357e6594dfba5c9b5213d1e9c8e6e093a980)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "selectors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="services")
    def services(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "services"))

    @services.setter
    def services(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38946182c0876ef8edde111dcf158bdfa520e63003a1842b6d12b654e0811177)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "services", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="slo")
    def slo(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "slo"))

    @slo.setter
    def slo(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddac2950663962abc49fa4b4a3de241a9dc8347bc8504783957b28abed41bc26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "status"))

    @status.setter
    def status(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc5e44de392b4c9224fa1e9e69a47d71fe69a9b09a5f72294f83d7b44ae057e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetHostname")
    def target_hostname(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetHostname"))

    @target_hostname.setter
    def target_hostname(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ee145ec9ca264bfd11e1e013c478b3e6a8c893d6acce284138697a69c109afa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetHostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetIp")
    def target_ip(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetIp"))

    @target_ip.setter
    def target_ip(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1efa3e3d8317d012dba9b2b9a4f09b288d162b18f556ccb80f040e7519ec04db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetZoneName")
    def target_zone_name(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetZoneName"))

    @target_zone_name.setter
    def target_zone_name(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__929a1c9b8b107397727ee7bcaa081ba130753718ffe3fd830d9854fd007b171a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetZoneName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trafficExclusions")
    def traffic_exclusions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "trafficExclusions"))

    @traffic_exclusions.setter
    def traffic_exclusions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f70e288d422408326db4ca1ef1ca2b3bd2b875187af2e4a3aebb46a6b0c9157)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trafficExclusions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tunnelId")
    def tunnel_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tunnelId"))

    @tunnel_id.setter
    def tunnel_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ea02582293c26043e9546d2e9124ee900459a5719e024032bfee8893a039071)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tunnelId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tunnelName")
    def tunnel_name(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tunnelName"))

    @tunnel_name.setter
    def tunnel_name(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9eea45a5a7c3cd29b86a701dfbac6025ea8efa606b3016108959b7a5718f5c16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tunnelName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="where")
    def where(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "where"))

    @where.setter
    def where(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0125865a7a67cb69fbb62c26e94245929beab4f8931d71649d8fb0abd7233f9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "where", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zones")
    def zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "zones"))

    @zones.setter
    def zones(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fb662b6bb44dcbe00b0cb7d46a78ad122a89d20f0f4ef981e54665d2a423f6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zones", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyFilters]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyFilters]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyFilters]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90a7709fbc2441ad30314af92ed6b3df73d6f83c4a876a9bfa7366752bf3ab12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanisms",
    jsii_struct_bases=[],
    name_mapping={"email": "email", "pagerduty": "pagerduty", "webhooks": "webhooks"},
)
class NotificationPolicyMechanisms:
    def __init__(
        self,
        *,
        email: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NotificationPolicyMechanismsEmail", typing.Dict[builtins.str, typing.Any]]]]] = None,
        pagerduty: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NotificationPolicyMechanismsPagerduty", typing.Dict[builtins.str, typing.Any]]]]] = None,
        webhooks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NotificationPolicyMechanismsWebhooks", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#email NotificationPolicy#email}.
        :param pagerduty: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#pagerduty NotificationPolicy#pagerduty}.
        :param webhooks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#webhooks NotificationPolicy#webhooks}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa9172272313a313a8c9b9ad7b95484eb04f6901a262bd20c993b0db9de63493)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument pagerduty", value=pagerduty, expected_type=type_hints["pagerduty"])
            check_type(argname="argument webhooks", value=webhooks, expected_type=type_hints["webhooks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if email is not None:
            self._values["email"] = email
        if pagerduty is not None:
            self._values["pagerduty"] = pagerduty
        if webhooks is not None:
            self._values["webhooks"] = webhooks

    @builtins.property
    def email(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsEmail"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#email NotificationPolicy#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsEmail"]]], result)

    @builtins.property
    def pagerduty(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsPagerduty"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#pagerduty NotificationPolicy#pagerduty}.'''
        result = self._values.get("pagerduty")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsPagerduty"]]], result)

    @builtins.property
    def webhooks(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsWebhooks"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#webhooks NotificationPolicy#webhooks}.'''
        result = self._values.get("webhooks")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsWebhooks"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationPolicyMechanisms(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsEmail",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class NotificationPolicyMechanismsEmail:
    def __init__(self, *, id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param id: The email address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#id NotificationPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92df04218bf0643c0adef6b1eaa273d5c3f68c44811782131ab7ba77c5eb53d9)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''The email address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#id NotificationPolicy#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationPolicyMechanismsEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationPolicyMechanismsEmailList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsEmailList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9d547a2b65954448842fd5a42921eb210f754c778a2c53294b746dbf7320c9a0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NotificationPolicyMechanismsEmailOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06b138c67c0287308f36f090112761ffa795a57e95475bb270008877dd6271a3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NotificationPolicyMechanismsEmailOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4b675b315370d8e7fba923d765f765ec971069367a0e8c69eecc8b2e5adeea0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7be2e2c3fd1f2ef837191e25a60b0d90e1c041ab06594c309508aa248363d5dc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__64a2f153ee171db1be7966c96a931ceb735a767813fbfb843fcd35c539e44f14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsEmail]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsEmail]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsEmail]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7d87862f276736d44db381f615efea5d266947013b2359812fffa696bb25efe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class NotificationPolicyMechanismsEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__407a98a25384b7c6d07bfc54015281c4ee872690d9bd08815130a59be6ad4318)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__1a482db11fb9c11739636a2aae51b9c9a42e6b5ed11ad8fc0bc4e1912b1e616b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsEmail]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsEmail]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d94efa9c35370f33c2352376b2df42947df348f7ecb15024547ba7d399a3a51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class NotificationPolicyMechanismsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__04d4a245dc86dcbb95e30861aa4f3c7974100e9d3eeb17a81b886d7648416a38)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEmail")
    def put_email(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[NotificationPolicyMechanismsEmail, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c744e4ad3d6299b7efb9a632985bf699eba66f0f8f04a5284c2e5f5a5e5af9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEmail", [value]))

    @jsii.member(jsii_name="putPagerduty")
    def put_pagerduty(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NotificationPolicyMechanismsPagerduty", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__785aa7bbe33bc3f44bdc11ebf7e6c7151f7c319b0f0c139da57a7d5f5f800957)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPagerduty", [value]))

    @jsii.member(jsii_name="putWebhooks")
    def put_webhooks(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NotificationPolicyMechanismsWebhooks", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad70dc72ad10a2b59bf34ce2ee84d229ff00e7ceba276f11b869cda81fca9fb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putWebhooks", [value]))

    @jsii.member(jsii_name="resetEmail")
    def reset_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmail", []))

    @jsii.member(jsii_name="resetPagerduty")
    def reset_pagerduty(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPagerduty", []))

    @jsii.member(jsii_name="resetWebhooks")
    def reset_webhooks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebhooks", []))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> NotificationPolicyMechanismsEmailList:
        return typing.cast(NotificationPolicyMechanismsEmailList, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="pagerduty")
    def pagerduty(self) -> "NotificationPolicyMechanismsPagerdutyList":
        return typing.cast("NotificationPolicyMechanismsPagerdutyList", jsii.get(self, "pagerduty"))

    @builtins.property
    @jsii.member(jsii_name="webhooks")
    def webhooks(self) -> "NotificationPolicyMechanismsWebhooksList":
        return typing.cast("NotificationPolicyMechanismsWebhooksList", jsii.get(self, "webhooks"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsEmail]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsEmail]]], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="pagerdutyInput")
    def pagerduty_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsPagerduty"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsPagerduty"]]], jsii.get(self, "pagerdutyInput"))

    @builtins.property
    @jsii.member(jsii_name="webhooksInput")
    def webhooks_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsWebhooks"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NotificationPolicyMechanismsWebhooks"]]], jsii.get(self, "webhooksInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanisms]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanisms]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanisms]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dc09e7cdfb92bc2e296002c1b4e10fd05f0ac38cb3e9d1b8b8163716feba2da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsPagerduty",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class NotificationPolicyMechanismsPagerduty:
    def __init__(self, *, id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param id: UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#id NotificationPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33c4d2ec03aa7c42c1e8011d9525a8f6c76a0cca4e3133f2c6679de026108999)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#id NotificationPolicy#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationPolicyMechanismsPagerduty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationPolicyMechanismsPagerdutyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsPagerdutyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__635c1b5afc120d7763a2b92a8e8caec51893deb46ee253a0965eb349c7a0221e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NotificationPolicyMechanismsPagerdutyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c39417b4993919abd94b37edcee10194438d5a453202fe36ac69362af0d66fbb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NotificationPolicyMechanismsPagerdutyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c6d9ba81df7d5cab2daaee6e2a54c82fbaf2e7bf7b74d8a3cd5c2dce6c9b285)
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
            type_hints = typing.get_type_hints(_typecheckingstub__56b1aa5986e9bcfe21fa7c15c1d6dcf74bffe86e27fc37ae1cb95018fc5253ce)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d790a2905a34ce0745f2495981b6f7045f1f155d041751b4d22f4799c1ac013e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsPagerduty]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsPagerduty]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsPagerduty]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fe8f92bd2f1b88886a02e3064cf904069be11046b64336907e3683d8f6f1ca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class NotificationPolicyMechanismsPagerdutyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsPagerdutyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8bf2f5b6805ed7a7e77db34eaebd434636eb2383d1e232be509ed17f56e63d73)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__02982d2c6e72075602dd23ee0c774a16a50843aa8fb6ec78adae902470797b38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsPagerduty]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsPagerduty]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsPagerduty]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__988465390d83155e546ddcde438a722c84c75196211b2326de31355bb9452df2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsWebhooks",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class NotificationPolicyMechanismsWebhooks:
    def __init__(self, *, id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param id: UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#id NotificationPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd84be65942bf9e507cc5f8b484055a5c807c3fb487811c47478de1815281932)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/notification_policy#id NotificationPolicy#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationPolicyMechanismsWebhooks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationPolicyMechanismsWebhooksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsWebhooksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__33a95f9527dc8ed59af0fb4bdab7b6d482a98c27d7a2c63668dde348faef3d2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NotificationPolicyMechanismsWebhooksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e564e5a016e9152a50376dae2d7b42004b3eb39277100cd670268fd31563dcb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NotificationPolicyMechanismsWebhooksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b656e6d14db742a7ad05eb747c05eb521b42afbc645af472cf809361117630d9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa2153996fca3ee9d29e8bf5f92f5da7d6e651853f319f61471633c92fbd9d9d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a79ba40e01eeb723f648a6e44b72ec95d16c14ff5eef09de55998279be02ab10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsWebhooks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsWebhooks]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsWebhooks]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24f5df8de924b6688f363f0d089fba604eb79914b53ed210bccc520e033678cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class NotificationPolicyMechanismsWebhooksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.notificationPolicy.NotificationPolicyMechanismsWebhooksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ae6b636e77cb664024863cc61d1667515c55e05b29655e9405b63e4e8f7706c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__506b43c917fe0629e69ae784f062275a4fbf25c41c8d0926ee7ffc96f860695f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsWebhooks]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsWebhooks]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsWebhooks]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbce71e57384c9120d9207c2f2c4c83ef3e7f2d48b69ecdddaf99b00b3bbbbba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "NotificationPolicy",
    "NotificationPolicyConfig",
    "NotificationPolicyFilters",
    "NotificationPolicyFiltersOutputReference",
    "NotificationPolicyMechanisms",
    "NotificationPolicyMechanismsEmail",
    "NotificationPolicyMechanismsEmailList",
    "NotificationPolicyMechanismsEmailOutputReference",
    "NotificationPolicyMechanismsOutputReference",
    "NotificationPolicyMechanismsPagerduty",
    "NotificationPolicyMechanismsPagerdutyList",
    "NotificationPolicyMechanismsPagerdutyOutputReference",
    "NotificationPolicyMechanismsWebhooks",
    "NotificationPolicyMechanismsWebhooksList",
    "NotificationPolicyMechanismsWebhooksOutputReference",
]

publication.publish()

def _typecheckingstub__d26986a49b23bd0b8c252e62235f69de0aed407a858eb18dec93b2afb89ac0f4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    alert_type: builtins.str,
    mechanisms: typing.Union[NotificationPolicyMechanisms, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    alert_interval: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    filters: typing.Optional[typing.Union[NotificationPolicyFilters, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__125b1431b5b31917f637f01b7497a9caaaa8b98ffa586ee484008a61b146f960(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12d61495632773ce0d55188dd5c264531790da548ad26191efd65e253d9ad7eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c9a9e9c1d66b8191cb35de5ab8690ce0b3a2fc36dee8347cd64eeb1e4793036(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6c59bc8c4d370898c433afe11d54353dbb01e0117c5e68b0ebcca68e7bcdf69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df1ca562165db15d390fd123cc403797076f4dd2d4772623a50ab8a708b70143(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b59f2fa90359289bd4f53cbe0d77c9cf06b5a6eee45e84f5d1ad1ad9d7481c80(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c32685b847789725af6a3b296bc5149261a762977bb9e1060f4aedc88b42c842(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bfdad0ea3b671f6ddd7c3f93399e6b1e1dbbec330f6748078f80895b3d1a900(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    alert_type: builtins.str,
    mechanisms: typing.Union[NotificationPolicyMechanisms, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    alert_interval: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    filters: typing.Optional[typing.Union[NotificationPolicyFilters, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5326ebf108453b36da8e814edd860719cbe2916d2193ee3d49f18c8694c6ff6(
    *,
    actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    affected_asns: typing.Optional[typing.Sequence[builtins.str]] = None,
    affected_components: typing.Optional[typing.Sequence[builtins.str]] = None,
    affected_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    airport_code: typing.Optional[typing.Sequence[builtins.str]] = None,
    alert_trigger_preferences: typing.Optional[typing.Sequence[builtins.str]] = None,
    alert_trigger_preferences_value: typing.Optional[typing.Sequence[builtins.str]] = None,
    enabled: typing.Optional[typing.Sequence[builtins.str]] = None,
    environment: typing.Optional[typing.Sequence[builtins.str]] = None,
    event: typing.Optional[typing.Sequence[builtins.str]] = None,
    event_source: typing.Optional[typing.Sequence[builtins.str]] = None,
    event_type: typing.Optional[typing.Sequence[builtins.str]] = None,
    group_by: typing.Optional[typing.Sequence[builtins.str]] = None,
    health_check_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    incident_impact: typing.Optional[typing.Sequence[builtins.str]] = None,
    input_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    insight_class: typing.Optional[typing.Sequence[builtins.str]] = None,
    limit: typing.Optional[typing.Sequence[builtins.str]] = None,
    logo_tag: typing.Optional[typing.Sequence[builtins.str]] = None,
    megabits_per_second: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_health: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_status: typing.Optional[typing.Sequence[builtins.str]] = None,
    packets_per_second: typing.Optional[typing.Sequence[builtins.str]] = None,
    pool_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    pop_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    product: typing.Optional[typing.Sequence[builtins.str]] = None,
    project_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    protocol: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_tag: typing.Optional[typing.Sequence[builtins.str]] = None,
    requests_per_second: typing.Optional[typing.Sequence[builtins.str]] = None,
    selectors: typing.Optional[typing.Sequence[builtins.str]] = None,
    services: typing.Optional[typing.Sequence[builtins.str]] = None,
    slo: typing.Optional[typing.Sequence[builtins.str]] = None,
    status: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_hostname: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_ip: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_zone_name: typing.Optional[typing.Sequence[builtins.str]] = None,
    traffic_exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
    tunnel_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    tunnel_name: typing.Optional[typing.Sequence[builtins.str]] = None,
    where: typing.Optional[typing.Sequence[builtins.str]] = None,
    zones: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8f31f649dafa1c3b6903338e913d967b05f75e2592e91fc18bbbf5a9a72cbcb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cbd740b090d5dcb3f98c1a4b6ff1a0651678c49b1243b284e7acc76e721589c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca8453685cafe9cd71fdae536de943da85d58d601fa0d3597cf5e8edaf3ed821(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__115da5f87a19dafbf96877c6df454a434fa82dee931e598988a1c5ff0eca9fa9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25aa83c53d8d267873a08acb206693fadb0f1763dbade9e3e7f9192a48724a7d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d941b7b7c50ceac8552ec74cb449a272d2e6a82dbca9e8d05722e7093b8aa012(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a8320bc1ab0055c005acf8e4d040f5ec3002105ebf206ab47f5525b66cdf017(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4112ba005a7db01c8e0a5f36be0b9011cf9cfc9c7584ec2ad4b2c99beccacc43(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b6ee8a77ab98e8abcf11477f1b4e4218a4a26478a7b259ee789af85016e8618(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb0a14683d0f88547af387c7869591ec8197b90a02b0892486f5d8c23ef17565(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a4a91dd52f49b0fec512d8e17d8b8240f99bc3f39fa0ee67625df8dace723e4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df89f3b37f251c30996df91f244b0e38e4c03fd32e227ef4866d53db10c4f71(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86846fba85173ea61eaef275166914e708d9a78cc98774322e89a5507120a689(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e978f4cf3db6c6b55f6b53bb973d85fa4170a68f295507309a67a4f395b50c7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36e1d871dafdc1ec7b5ca7ef3c1e55d5e3fffff205f8f6e393e16559a71d94a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13313e393833d80e078d2cd462aff18800b7798f22b77741274bf92e597618cb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13749ce4d14ee4d47ca2b743593e0ea6f8c5d1e90db0b4187cef46c6281fc868(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e1e16b04dba7e10647a5a79797d98239ca7aa833ce837df866e84c002fbea0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c7cb06df8ae94848c7d39371bb6bd7cafdd6893fc1fa40c3e9a95e769691bbb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71e2349bff2229c072d107c896611c7fc7aae80dcd678fe364f22e72fe48d52e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2e46433a07b7996ca9c557720a807d2654d178508bcf210b8a79c277a55678d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__966097109aab71dd336a62096323ee6c5a20d6f9e5eb6ad3da692d10466d7f30(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9d1aedf12f36c5e87a2c7c4dd88494cd6c4ed2ef80edab2f726408ac75ffa3c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5426e77e9e8c318d485d667eeae7786bf21d76bb73e66167a78b6e56bd60a267(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc505ad097f5dfa3183501da19ee617059ab758a68300726c93efd8db22c9581(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dbf97e89228341486c4942909cd1030b0d64a351358f834cd61ecfee203d92e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2734761a5311a1478499b1a47a670c6c381a85a844cad3ede6ff97dd200176c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00c01b98586d5f97b73f117d41a62c0b7ee62fdc73706705cda00665cc6fe996(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb8231efaeb8ff5412b70a100e1e1e8fe333cd173c99bba7c99c2add01119d6e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f55e35df35e567089be6cac46d39fdd9427559f5de41d9da0828c53ee12ed37f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0210adff9def3da2b344737aced573e739cc90b4b559ab475c8dcf6ad23fcce2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc62169f354fdaea6f58699f464b357e6594dfba5c9b5213d1e9c8e6e093a980(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38946182c0876ef8edde111dcf158bdfa520e63003a1842b6d12b654e0811177(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddac2950663962abc49fa4b4a3de241a9dc8347bc8504783957b28abed41bc26(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc5e44de392b4c9224fa1e9e69a47d71fe69a9b09a5f72294f83d7b44ae057e7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ee145ec9ca264bfd11e1e013c478b3e6a8c893d6acce284138697a69c109afa(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1efa3e3d8317d012dba9b2b9a4f09b288d162b18f556ccb80f040e7519ec04db(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__929a1c9b8b107397727ee7bcaa081ba130753718ffe3fd830d9854fd007b171a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f70e288d422408326db4ca1ef1ca2b3bd2b875187af2e4a3aebb46a6b0c9157(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ea02582293c26043e9546d2e9124ee900459a5719e024032bfee8893a039071(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eea45a5a7c3cd29b86a701dfbac6025ea8efa606b3016108959b7a5718f5c16(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0125865a7a67cb69fbb62c26e94245929beab4f8931d71649d8fb0abd7233f9f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fb662b6bb44dcbe00b0cb7d46a78ad122a89d20f0f4ef981e54665d2a423f6e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90a7709fbc2441ad30314af92ed6b3df73d6f83c4a876a9bfa7366752bf3ab12(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyFilters]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa9172272313a313a8c9b9ad7b95484eb04f6901a262bd20c993b0db9de63493(
    *,
    email: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[NotificationPolicyMechanismsEmail, typing.Dict[builtins.str, typing.Any]]]]] = None,
    pagerduty: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[NotificationPolicyMechanismsPagerduty, typing.Dict[builtins.str, typing.Any]]]]] = None,
    webhooks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[NotificationPolicyMechanismsWebhooks, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92df04218bf0643c0adef6b1eaa273d5c3f68c44811782131ab7ba77c5eb53d9(
    *,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d547a2b65954448842fd5a42921eb210f754c778a2c53294b746dbf7320c9a0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06b138c67c0287308f36f090112761ffa795a57e95475bb270008877dd6271a3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4b675b315370d8e7fba923d765f765ec971069367a0e8c69eecc8b2e5adeea0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7be2e2c3fd1f2ef837191e25a60b0d90e1c041ab06594c309508aa248363d5dc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64a2f153ee171db1be7966c96a931ceb735a767813fbfb843fcd35c539e44f14(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7d87862f276736d44db381f615efea5d266947013b2359812fffa696bb25efe(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsEmail]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__407a98a25384b7c6d07bfc54015281c4ee872690d9bd08815130a59be6ad4318(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a482db11fb9c11739636a2aae51b9c9a42e6b5ed11ad8fc0bc4e1912b1e616b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d94efa9c35370f33c2352376b2df42947df348f7ecb15024547ba7d399a3a51(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsEmail]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04d4a245dc86dcbb95e30861aa4f3c7974100e9d3eeb17a81b886d7648416a38(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c744e4ad3d6299b7efb9a632985bf699eba66f0f8f04a5284c2e5f5a5e5af9a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[NotificationPolicyMechanismsEmail, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__785aa7bbe33bc3f44bdc11ebf7e6c7151f7c319b0f0c139da57a7d5f5f800957(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[NotificationPolicyMechanismsPagerduty, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad70dc72ad10a2b59bf34ce2ee84d229ff00e7ceba276f11b869cda81fca9fb7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[NotificationPolicyMechanismsWebhooks, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dc09e7cdfb92bc2e296002c1b4e10fd05f0ac38cb3e9d1b8b8163716feba2da(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanisms]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33c4d2ec03aa7c42c1e8011d9525a8f6c76a0cca4e3133f2c6679de026108999(
    *,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__635c1b5afc120d7763a2b92a8e8caec51893deb46ee253a0965eb349c7a0221e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c39417b4993919abd94b37edcee10194438d5a453202fe36ac69362af0d66fbb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c6d9ba81df7d5cab2daaee6e2a54c82fbaf2e7bf7b74d8a3cd5c2dce6c9b285(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56b1aa5986e9bcfe21fa7c15c1d6dcf74bffe86e27fc37ae1cb95018fc5253ce(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d790a2905a34ce0745f2495981b6f7045f1f155d041751b4d22f4799c1ac013e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fe8f92bd2f1b88886a02e3064cf904069be11046b64336907e3683d8f6f1ca4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsPagerduty]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bf2f5b6805ed7a7e77db34eaebd434636eb2383d1e232be509ed17f56e63d73(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02982d2c6e72075602dd23ee0c774a16a50843aa8fb6ec78adae902470797b38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__988465390d83155e546ddcde438a722c84c75196211b2326de31355bb9452df2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsPagerduty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd84be65942bf9e507cc5f8b484055a5c807c3fb487811c47478de1815281932(
    *,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33a95f9527dc8ed59af0fb4bdab7b6d482a98c27d7a2c63668dde348faef3d2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e564e5a016e9152a50376dae2d7b42004b3eb39277100cd670268fd31563dcb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b656e6d14db742a7ad05eb747c05eb521b42afbc645af472cf809361117630d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa2153996fca3ee9d29e8bf5f92f5da7d6e651853f319f61471633c92fbd9d9d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a79ba40e01eeb723f648a6e44b72ec95d16c14ff5eef09de55998279be02ab10(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24f5df8de924b6688f363f0d089fba604eb79914b53ed210bccc520e033678cc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NotificationPolicyMechanismsWebhooks]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ae6b636e77cb664024863cc61d1667515c55e05b29655e9405b63e4e8f7706c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__506b43c917fe0629e69ae784f062275a4fbf25c41c8d0926ee7ffc96f860695f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbce71e57384c9120d9207c2f2c4c83ef3e7f2d48b69ecdddaf99b00b3bbbbba(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, NotificationPolicyMechanismsWebhooks]],
) -> None:
    """Type checking stubs"""
    pass
