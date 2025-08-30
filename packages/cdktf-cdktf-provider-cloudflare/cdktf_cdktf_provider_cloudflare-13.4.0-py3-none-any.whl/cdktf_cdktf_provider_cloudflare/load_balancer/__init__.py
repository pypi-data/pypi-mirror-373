r'''
# `cloudflare_load_balancer`

Refer to the Terraform Registry for docs: [`cloudflare_load_balancer`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer).
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


class LoadBalancer(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancer",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer cloudflare_load_balancer}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        default_pools: typing.Sequence[builtins.str],
        fallback_pool: builtins.str,
        name: builtins.str,
        zone_id: builtins.str,
        adaptive_routing: typing.Optional[typing.Union["LoadBalancerAdaptiveRouting", typing.Dict[builtins.str, typing.Any]]] = None,
        country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        location_strategy: typing.Optional[typing.Union["LoadBalancerLocationStrategy", typing.Dict[builtins.str, typing.Any]]] = None,
        networks: typing.Optional[typing.Sequence[builtins.str]] = None,
        pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        random_steering: typing.Optional[typing.Union["LoadBalancerRandomSteering", typing.Dict[builtins.str, typing.Any]]] = None,
        region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadBalancerRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        session_affinity: typing.Optional[builtins.str] = None,
        session_affinity_attributes: typing.Optional[typing.Union["LoadBalancerSessionAffinityAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        session_affinity_ttl: typing.Optional[jsii.Number] = None,
        steering_policy: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer cloudflare_load_balancer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param default_pools: A list of pool IDs ordered by their failover priority. Pools defined here are used by default, or when region_pools are not configured for a given region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_pools LoadBalancer#default_pools}
        :param fallback_pool: The pool ID to use when all other pools are detected as unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#fallback_pool LoadBalancer#fallback_pool}
        :param name: The DNS hostname to associate with your Load Balancer. If this hostname already exists as a DNS record in Cloudflare's DNS, the Load Balancer will take precedence and the DNS record will not be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#name LoadBalancer#name}
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#zone_id LoadBalancer#zone_id}.
        :param adaptive_routing: Controls features that modify the routing of requests to pools and origins in response to dynamic conditions, such as during the interval between active health monitoring requests. For example, zero-downtime failover occurs immediately when an origin becomes unavailable due to HTTP 521, 522, or 523 response codes. If there is another healthy origin in the same pool, the request is retried once against this alternate origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#adaptive_routing LoadBalancer#adaptive_routing}
        :param country_pools: A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country. Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#country_pools LoadBalancer#country_pools}
        :param description: Object description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#description LoadBalancer#description}
        :param enabled: Whether to enable (the default) this load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#enabled LoadBalancer#enabled}
        :param location_strategy: Controls location-based steering for non-proxied requests. See ``steering_policy`` to learn how steering is affected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#location_strategy LoadBalancer#location_strategy}
        :param networks: List of networks where Load Balancer or Pool is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#networks LoadBalancer#networks}
        :param pop_pools: Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter). Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pop_pools LoadBalancer#pop_pools}
        :param proxied: Whether the hostname should be gray clouded (false) or orange clouded (true). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#proxied LoadBalancer#proxied}
        :param random_steering: Configures pool weights. - ``steering_policy="random"``: A random pool is selected with probability proportional to pool weights. - ``steering_policy="least_outstanding_requests"``: Use pool weights to scale each pool's outstanding requests. - ``steering_policy="least_connections"``: Use pool weights to scale each pool's open connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#random_steering LoadBalancer#random_steering}
        :param region_pools: A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region. Any regions not explicitly defined will fall back to using default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#region_pools LoadBalancer#region_pools}
        :param rules: BETA Field Not General Access: A list of rules for this load balancer to execute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#rules LoadBalancer#rules}
        :param session_affinity: Specifies the type of session affinity the load balancer should use unless specified as ``"none"``. The supported types are: - ``"cookie"``: On the first request to a proxied load balancer, a cookie is generated, encoding information of which origin the request will be forwarded to. Subsequent requests, by the same client to the same load balancer, will be sent to the origin server the cookie encodes, for the duration of the cookie and as long as the origin server remains healthy. If the cookie has expired or the origin server is unhealthy, then a new origin server is calculated and used. - ``"ip_cookie"``: Behaves the same as ``"cookie"`` except the initial origin selection is stable and based on the client's ip address. - ``"header"``: On the first request to a proxied load balancer, a session key based on the configured HTTP headers (see ``session_affinity_attributes.headers``) is generated, encoding the request headers used for storing in the load balancer session state which origin the request will be forwarded to. Subsequent requests to the load balancer with the same headers will be sent to the same origin server, for the duration of the session and as long as the origin server remains healthy. If the session has been idle for the duration of ``session_affinity_ttl`` seconds or the origin server is unhealthy, then a new origin server is calculated and used. See ``headers`` in ``session_affinity_attributes`` for additional required configuration. Available values: "none", "cookie", "ip_cookie", "header". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity LoadBalancer#session_affinity}
        :param session_affinity_attributes: Configures attributes for session affinity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_attributes LoadBalancer#session_affinity_attributes}
        :param session_affinity_ttl: Time, in seconds, until a client's session expires after being created. Once the expiry time has been reached, subsequent requests may get sent to a different origin server. The accepted ranges per ``session_affinity`` policy are: - ``"cookie"`` / ``"ip_cookie"``: The current default of 23 hours will be used unless explicitly set. The accepted range of values is between [1800, 604800]. - ``"header"``: The current default of 1800 seconds will be used unless explicitly set. The accepted range of values is between [30, 3600]. Note: With session affinity by header, sessions only expire after they haven't been used for the number of seconds specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_ttl LoadBalancer#session_affinity_ttl}
        :param steering_policy: Steering Policy for this load balancer. - ``"off"``: Use ``default_pools``. - ``"geo"``: Use ``region_pools``/``country_pools``/``pop_pools``. For non-proxied requests, the country for ``country_pools`` is determined by ``location_strategy``. - ``"random"``: Select a pool randomly. - ``"dynamic_latency"``: Use round trip time to select the closest pool in default_pools (requires pool health checks). - ``"proximity"``: Use the pools' latitude and longitude to select the closest pool using the Cloudflare PoP location for proxied requests or the location determined by ``location_strategy`` for non-proxied requests. - ``"least_outstanding_requests"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of outstanding requests. Pools with more pending requests are weighted proportionately less relative to others. - ``"least_connections"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of open connections. Pools with more open connections are weighted proportionately less relative to others. Supported for HTTP/1 and HTTP/2 connections. - ``""``: Will map to ``"geo"`` if you use ``region_pools``/``country_pools``/``pop_pools`` otherwise ``"off"``. Available values: "off", "geo", "random", "dynamic_latency", "proximity", "least_outstanding_requests", "least_connections", "". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#steering_policy LoadBalancer#steering_policy}
        :param ttl: Time to live (TTL) of the DNS entry for the IP address returned by this load balancer. This only applies to gray-clouded (unproxied) load balancers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#ttl LoadBalancer#ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0015049507828df93e92dfe6c1bca8e51a3ffecfec278ed1f472e11b1c5ed18f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = LoadBalancerConfig(
            default_pools=default_pools,
            fallback_pool=fallback_pool,
            name=name,
            zone_id=zone_id,
            adaptive_routing=adaptive_routing,
            country_pools=country_pools,
            description=description,
            enabled=enabled,
            location_strategy=location_strategy,
            networks=networks,
            pop_pools=pop_pools,
            proxied=proxied,
            random_steering=random_steering,
            region_pools=region_pools,
            rules=rules,
            session_affinity=session_affinity,
            session_affinity_attributes=session_affinity_attributes,
            session_affinity_ttl=session_affinity_ttl,
            steering_policy=steering_policy,
            ttl=ttl,
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
        '''Generates CDKTF code for importing a LoadBalancer resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the LoadBalancer to import.
        :param import_from_id: The id of the existing LoadBalancer that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the LoadBalancer to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b042f6d1d03c54f4854ecae07c5c93a2cc8e8f808d873ddcaf6b7961345a6554)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAdaptiveRouting")
    def put_adaptive_routing(
        self,
        *,
        failover_across_pools: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param failover_across_pools: Extends zero-downtime failover of requests to healthy origins from alternate pools, when no healthy alternate exists in the same pool, according to the failover order defined by traffic and origin steering. When set false (the default) zero-downtime failover will only occur between origins within the same pool. See ``session_affinity_attributes`` for control over when sessions are broken or reassigned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#failover_across_pools LoadBalancer#failover_across_pools}
        '''
        value = LoadBalancerAdaptiveRouting(
            failover_across_pools=failover_across_pools
        )

        return typing.cast(None, jsii.invoke(self, "putAdaptiveRouting", [value]))

    @jsii.member(jsii_name="putLocationStrategy")
    def put_location_strategy(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        prefer_ecs: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mode: Determines the authoritative location when ECS is not preferred, does not exist in the request, or its GeoIP lookup is unsuccessful. - ``"pop"``: Use the Cloudflare PoP location. - ``"resolver_ip"``: Use the DNS resolver GeoIP location. If the GeoIP lookup is unsuccessful, use the Cloudflare PoP location. Available values: "pop", "resolver_ip". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#mode LoadBalancer#mode}
        :param prefer_ecs: Whether the EDNS Client Subnet (ECS) GeoIP should be preferred as the authoritative location. - ``"always"``: Always prefer ECS. - ``"never"``: Never prefer ECS. - ``"proximity"``: Prefer ECS only when ``steering_policy="proximity"``. - ``"geo"``: Prefer ECS only when ``steering_policy="geo"``. Available values: "always", "never", "proximity", "geo". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#prefer_ecs LoadBalancer#prefer_ecs}
        '''
        value = LoadBalancerLocationStrategy(mode=mode, prefer_ecs=prefer_ecs)

        return typing.cast(None, jsii.invoke(self, "putLocationStrategy", [value]))

    @jsii.member(jsii_name="putRandomSteering")
    def put_random_steering(
        self,
        *,
        default_weight: typing.Optional[jsii.Number] = None,
        pool_weights: typing.Optional[typing.Mapping[builtins.str, jsii.Number]] = None,
    ) -> None:
        '''
        :param default_weight: The default weight for pools in the load balancer that are not specified in the pool_weights map. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_weight LoadBalancer#default_weight}
        :param pool_weights: A mapping of pool IDs to custom weights. The weight is relative to other pools in the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pool_weights LoadBalancer#pool_weights}
        '''
        value = LoadBalancerRandomSteering(
            default_weight=default_weight, pool_weights=pool_weights
        )

        return typing.cast(None, jsii.invoke(self, "putRandomSteering", [value]))

    @jsii.member(jsii_name="putRules")
    def put_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadBalancerRules", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__713bf22a49b1560498a800316f840069503b2323554a05dc728d48b4c9dca764)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRules", [value]))

    @jsii.member(jsii_name="putSessionAffinityAttributes")
    def put_session_affinity_attributes(
        self,
        *,
        drain_duration: typing.Optional[jsii.Number] = None,
        headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        require_all_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        samesite: typing.Optional[builtins.str] = None,
        secure: typing.Optional[builtins.str] = None,
        zero_downtime_failover: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param drain_duration: Configures the drain duration in seconds. This field is only used when session affinity is enabled on the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#drain_duration LoadBalancer#drain_duration}
        :param headers: Configures the names of HTTP headers to base session affinity on when header ``session_affinity`` is enabled. At least one HTTP header name must be provided. To specify the exact cookies to be used, include an item in the following format: ``"cookie:<cookie-name-1>,<cookie-name-2>"`` (example) where everything after the colon is a comma-separated list of cookie names. Providing only ``"cookie"`` will result in all cookies being used. The default max number of HTTP header names that can be provided depends on your plan: 5 for Enterprise, 1 for all other plans. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#headers LoadBalancer#headers}
        :param require_all_headers: When header ``session_affinity`` is enabled, this option can be used to specify how HTTP headers on load balancing requests will be used. The supported values are: - ``"true"``: Load balancing requests must contain *all* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. - ``"false"``: Load balancing requests must contain *at least one* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#require_all_headers LoadBalancer#require_all_headers}
        :param samesite: Configures the SameSite attribute on session affinity cookie. Value "Auto" will be translated to "Lax" or "None" depending if Always Use HTTPS is enabled. Note: when using value "None", the secure attribute can not be set to "Never". Available values: "Auto", "Lax", "None", "Strict". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#samesite LoadBalancer#samesite}
        :param secure: Configures the Secure attribute on session affinity cookie. Value "Always" indicates the Secure attribute will be set in the Set-Cookie header, "Never" indicates the Secure attribute will not be set, and "Auto" will set the Secure attribute depending if Always Use HTTPS is enabled. Available values: "Auto", "Always", "Never". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#secure LoadBalancer#secure}
        :param zero_downtime_failover: Configures the zero-downtime failover between origins within a pool when session affinity is enabled. This feature is currently incompatible with Argo, Tiered Cache, and Bandwidth Alliance. The supported values are: - ``"none"``: No failover takes place for sessions pinned to the origin (default). - ``"temporary"``: Traffic will be sent to another other healthy origin until the originally pinned origin is available; note that this can potentially result in heavy origin flapping. - ``"sticky"``: The session affinity cookie is updated and subsequent requests are sent to the new origin. Note: Zero-downtime failover with sticky sessions is currently not supported for session affinity by header. Available values: "none", "temporary", "sticky". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#zero_downtime_failover LoadBalancer#zero_downtime_failover}
        '''
        value = LoadBalancerSessionAffinityAttributes(
            drain_duration=drain_duration,
            headers=headers,
            require_all_headers=require_all_headers,
            samesite=samesite,
            secure=secure,
            zero_downtime_failover=zero_downtime_failover,
        )

        return typing.cast(None, jsii.invoke(self, "putSessionAffinityAttributes", [value]))

    @jsii.member(jsii_name="resetAdaptiveRouting")
    def reset_adaptive_routing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdaptiveRouting", []))

    @jsii.member(jsii_name="resetCountryPools")
    def reset_country_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountryPools", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetLocationStrategy")
    def reset_location_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocationStrategy", []))

    @jsii.member(jsii_name="resetNetworks")
    def reset_networks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworks", []))

    @jsii.member(jsii_name="resetPopPools")
    def reset_pop_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPopPools", []))

    @jsii.member(jsii_name="resetProxied")
    def reset_proxied(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProxied", []))

    @jsii.member(jsii_name="resetRandomSteering")
    def reset_random_steering(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRandomSteering", []))

    @jsii.member(jsii_name="resetRegionPools")
    def reset_region_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionPools", []))

    @jsii.member(jsii_name="resetRules")
    def reset_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRules", []))

    @jsii.member(jsii_name="resetSessionAffinity")
    def reset_session_affinity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionAffinity", []))

    @jsii.member(jsii_name="resetSessionAffinityAttributes")
    def reset_session_affinity_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionAffinityAttributes", []))

    @jsii.member(jsii_name="resetSessionAffinityTtl")
    def reset_session_affinity_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionAffinityTtl", []))

    @jsii.member(jsii_name="resetSteeringPolicy")
    def reset_steering_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSteeringPolicy", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

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
    @jsii.member(jsii_name="adaptiveRouting")
    def adaptive_routing(self) -> "LoadBalancerAdaptiveRoutingOutputReference":
        return typing.cast("LoadBalancerAdaptiveRoutingOutputReference", jsii.get(self, "adaptiveRouting"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="locationStrategy")
    def location_strategy(self) -> "LoadBalancerLocationStrategyOutputReference":
        return typing.cast("LoadBalancerLocationStrategyOutputReference", jsii.get(self, "locationStrategy"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="randomSteering")
    def random_steering(self) -> "LoadBalancerRandomSteeringOutputReference":
        return typing.cast("LoadBalancerRandomSteeringOutputReference", jsii.get(self, "randomSteering"))

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> "LoadBalancerRulesList":
        return typing.cast("LoadBalancerRulesList", jsii.get(self, "rules"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityAttributes")
    def session_affinity_attributes(
        self,
    ) -> "LoadBalancerSessionAffinityAttributesOutputReference":
        return typing.cast("LoadBalancerSessionAffinityAttributesOutputReference", jsii.get(self, "sessionAffinityAttributes"))

    @builtins.property
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @builtins.property
    @jsii.member(jsii_name="adaptiveRoutingInput")
    def adaptive_routing_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerAdaptiveRouting"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerAdaptiveRouting"]], jsii.get(self, "adaptiveRoutingInput"))

    @builtins.property
    @jsii.member(jsii_name="countryPoolsInput")
    def country_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "countryPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultPoolsInput")
    def default_pools_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "defaultPoolsInput"))

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
    @jsii.member(jsii_name="fallbackPoolInput")
    def fallback_pool_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fallbackPoolInput"))

    @builtins.property
    @jsii.member(jsii_name="locationStrategyInput")
    def location_strategy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerLocationStrategy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerLocationStrategy"]], jsii.get(self, "locationStrategyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networksInput")
    def networks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "networksInput"))

    @builtins.property
    @jsii.member(jsii_name="popPoolsInput")
    def pop_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "popPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="proxiedInput")
    def proxied_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "proxiedInput"))

    @builtins.property
    @jsii.member(jsii_name="randomSteeringInput")
    def random_steering_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerRandomSteering"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerRandomSteering"]], jsii.get(self, "randomSteeringInput"))

    @builtins.property
    @jsii.member(jsii_name="regionPoolsInput")
    def region_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "regionPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="rulesInput")
    def rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadBalancerRules"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadBalancerRules"]]], jsii.get(self, "rulesInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityAttributesInput")
    def session_affinity_attributes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerSessionAffinityAttributes"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerSessionAffinityAttributes"]], jsii.get(self, "sessionAffinityAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityInput")
    def session_affinity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionAffinityInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityTtlInput")
    def session_affinity_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sessionAffinityTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="steeringPolicyInput")
    def steering_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "steeringPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="countryPools")
    def country_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "countryPools"))

    @country_pools.setter
    def country_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a5ade0a0a29ac9271b21ba639ddda8beae0b01fd7d163371f75847397c48669)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultPools")
    def default_pools(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "defaultPools"))

    @default_pools.setter
    def default_pools(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dd3c521e6f1c952de609d8259bea28eb62676dddbfd5dc0939f75a2980e421f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__749c6dd92b9de55f6f692a104109a7a8c0140668d57a671f2f4096578fa936a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__83c6dec4fe321e227c8d9680880282305431f4dba6c380b6d1257f0b33508764)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fallbackPool")
    def fallback_pool(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fallbackPool"))

    @fallback_pool.setter
    def fallback_pool(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e367360d0eb0a6e0af31ad6ea22ccbacd3116a3a31c0f7fe37b0c0856bbde90c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallbackPool", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__549a6fc7dd52b05e493a75e851006eb3ff4b1b5be4e31f42a3e0fba8a3e7992c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networks")
    def networks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networks"))

    @networks.setter
    def networks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8b3a62b3a4ae7b0e56cd604e01c17dfd1006a3608eb3327aabac26d319ab590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="popPools")
    def pop_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "popPools"))

    @pop_pools.setter
    def pop_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f4ee4593aefbaaf723108ef8a0742472ab2f8fc5971c47b5806c44843ca8a6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "popPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proxied")
    def proxied(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "proxied"))

    @proxied.setter
    def proxied(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e098d3c0597e3524b55c3627f9a3bb7992a85e831d4f688b06dfff6966b3988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxied", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionPools")
    def region_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "regionPools"))

    @region_pools.setter
    def region_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e7bbeeed712104f7d319eb93d1399f8b375a07f5b5985db6265286cd664c8bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionAffinity")
    def session_affinity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionAffinity"))

    @session_affinity.setter
    def session_affinity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0750582d833b47b92d0f19d520eb3c3efdee362ea8a4097af61978e00dce967a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionAffinity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityTtl")
    def session_affinity_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sessionAffinityTtl"))

    @session_affinity_ttl.setter
    def session_affinity_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce0cd47fb3f2073bbd91e71dcb6d52e072ba67430ce8b3bd46319e7ae25f9afd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionAffinityTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="steeringPolicy")
    def steering_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "steeringPolicy"))

    @steering_policy.setter
    def steering_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f38cc45e4ba523e71f68dc6122fbd27e2295e3f03fc8776d0f26210fe4925bd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "steeringPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80fcc62043aca63d073f33eb1730d5f1b0708a90f7fa61ae55fbbe0cebee22ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21bb86cc37c1ec4ce7603426eab2a13a53a3024685a2262c80dcf7351190a31b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerAdaptiveRouting",
    jsii_struct_bases=[],
    name_mapping={"failover_across_pools": "failoverAcrossPools"},
)
class LoadBalancerAdaptiveRouting:
    def __init__(
        self,
        *,
        failover_across_pools: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param failover_across_pools: Extends zero-downtime failover of requests to healthy origins from alternate pools, when no healthy alternate exists in the same pool, according to the failover order defined by traffic and origin steering. When set false (the default) zero-downtime failover will only occur between origins within the same pool. See ``session_affinity_attributes`` for control over when sessions are broken or reassigned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#failover_across_pools LoadBalancer#failover_across_pools}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__303c8d660d7ff911b7607b1ed365324cf95aef52ab574f4228534f17fbfe1953)
            check_type(argname="argument failover_across_pools", value=failover_across_pools, expected_type=type_hints["failover_across_pools"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if failover_across_pools is not None:
            self._values["failover_across_pools"] = failover_across_pools

    @builtins.property
    def failover_across_pools(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Extends zero-downtime failover of requests to healthy origins from alternate pools, when no healthy alternate exists in the same pool, according to the failover order defined by traffic and origin steering.

        When set false (the default) zero-downtime failover will only occur between origins within the same pool. See ``session_affinity_attributes`` for control over when sessions are broken or reassigned.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#failover_across_pools LoadBalancer#failover_across_pools}
        '''
        result = self._values.get("failover_across_pools")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerAdaptiveRouting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerAdaptiveRoutingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerAdaptiveRoutingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d41d79f69f4c4baa892cc9881ebe8a3b44e49a9e164ded9e679d66e3b05302c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFailoverAcrossPools")
    def reset_failover_across_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailoverAcrossPools", []))

    @builtins.property
    @jsii.member(jsii_name="failoverAcrossPoolsInput")
    def failover_across_pools_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "failoverAcrossPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="failoverAcrossPools")
    def failover_across_pools(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "failoverAcrossPools"))

    @failover_across_pools.setter
    def failover_across_pools(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__483f29751055bdcab9b5325a954524c06820b6aca2f5bdcef6272c6c5e8f633d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failoverAcrossPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerAdaptiveRouting]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerAdaptiveRouting]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerAdaptiveRouting]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4657374ad9caf633eb09b1d65ba4e5b4f17d06e0b28714a28b13cdc210bd62a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "default_pools": "defaultPools",
        "fallback_pool": "fallbackPool",
        "name": "name",
        "zone_id": "zoneId",
        "adaptive_routing": "adaptiveRouting",
        "country_pools": "countryPools",
        "description": "description",
        "enabled": "enabled",
        "location_strategy": "locationStrategy",
        "networks": "networks",
        "pop_pools": "popPools",
        "proxied": "proxied",
        "random_steering": "randomSteering",
        "region_pools": "regionPools",
        "rules": "rules",
        "session_affinity": "sessionAffinity",
        "session_affinity_attributes": "sessionAffinityAttributes",
        "session_affinity_ttl": "sessionAffinityTtl",
        "steering_policy": "steeringPolicy",
        "ttl": "ttl",
    },
)
class LoadBalancerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        default_pools: typing.Sequence[builtins.str],
        fallback_pool: builtins.str,
        name: builtins.str,
        zone_id: builtins.str,
        adaptive_routing: typing.Optional[typing.Union[LoadBalancerAdaptiveRouting, typing.Dict[builtins.str, typing.Any]]] = None,
        country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        location_strategy: typing.Optional[typing.Union["LoadBalancerLocationStrategy", typing.Dict[builtins.str, typing.Any]]] = None,
        networks: typing.Optional[typing.Sequence[builtins.str]] = None,
        pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        random_steering: typing.Optional[typing.Union["LoadBalancerRandomSteering", typing.Dict[builtins.str, typing.Any]]] = None,
        region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadBalancerRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        session_affinity: typing.Optional[builtins.str] = None,
        session_affinity_attributes: typing.Optional[typing.Union["LoadBalancerSessionAffinityAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        session_affinity_ttl: typing.Optional[jsii.Number] = None,
        steering_policy: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param default_pools: A list of pool IDs ordered by their failover priority. Pools defined here are used by default, or when region_pools are not configured for a given region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_pools LoadBalancer#default_pools}
        :param fallback_pool: The pool ID to use when all other pools are detected as unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#fallback_pool LoadBalancer#fallback_pool}
        :param name: The DNS hostname to associate with your Load Balancer. If this hostname already exists as a DNS record in Cloudflare's DNS, the Load Balancer will take precedence and the DNS record will not be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#name LoadBalancer#name}
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#zone_id LoadBalancer#zone_id}.
        :param adaptive_routing: Controls features that modify the routing of requests to pools and origins in response to dynamic conditions, such as during the interval between active health monitoring requests. For example, zero-downtime failover occurs immediately when an origin becomes unavailable due to HTTP 521, 522, or 523 response codes. If there is another healthy origin in the same pool, the request is retried once against this alternate origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#adaptive_routing LoadBalancer#adaptive_routing}
        :param country_pools: A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country. Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#country_pools LoadBalancer#country_pools}
        :param description: Object description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#description LoadBalancer#description}
        :param enabled: Whether to enable (the default) this load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#enabled LoadBalancer#enabled}
        :param location_strategy: Controls location-based steering for non-proxied requests. See ``steering_policy`` to learn how steering is affected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#location_strategy LoadBalancer#location_strategy}
        :param networks: List of networks where Load Balancer or Pool is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#networks LoadBalancer#networks}
        :param pop_pools: Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter). Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pop_pools LoadBalancer#pop_pools}
        :param proxied: Whether the hostname should be gray clouded (false) or orange clouded (true). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#proxied LoadBalancer#proxied}
        :param random_steering: Configures pool weights. - ``steering_policy="random"``: A random pool is selected with probability proportional to pool weights. - ``steering_policy="least_outstanding_requests"``: Use pool weights to scale each pool's outstanding requests. - ``steering_policy="least_connections"``: Use pool weights to scale each pool's open connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#random_steering LoadBalancer#random_steering}
        :param region_pools: A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region. Any regions not explicitly defined will fall back to using default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#region_pools LoadBalancer#region_pools}
        :param rules: BETA Field Not General Access: A list of rules for this load balancer to execute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#rules LoadBalancer#rules}
        :param session_affinity: Specifies the type of session affinity the load balancer should use unless specified as ``"none"``. The supported types are: - ``"cookie"``: On the first request to a proxied load balancer, a cookie is generated, encoding information of which origin the request will be forwarded to. Subsequent requests, by the same client to the same load balancer, will be sent to the origin server the cookie encodes, for the duration of the cookie and as long as the origin server remains healthy. If the cookie has expired or the origin server is unhealthy, then a new origin server is calculated and used. - ``"ip_cookie"``: Behaves the same as ``"cookie"`` except the initial origin selection is stable and based on the client's ip address. - ``"header"``: On the first request to a proxied load balancer, a session key based on the configured HTTP headers (see ``session_affinity_attributes.headers``) is generated, encoding the request headers used for storing in the load balancer session state which origin the request will be forwarded to. Subsequent requests to the load balancer with the same headers will be sent to the same origin server, for the duration of the session and as long as the origin server remains healthy. If the session has been idle for the duration of ``session_affinity_ttl`` seconds or the origin server is unhealthy, then a new origin server is calculated and used. See ``headers`` in ``session_affinity_attributes`` for additional required configuration. Available values: "none", "cookie", "ip_cookie", "header". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity LoadBalancer#session_affinity}
        :param session_affinity_attributes: Configures attributes for session affinity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_attributes LoadBalancer#session_affinity_attributes}
        :param session_affinity_ttl: Time, in seconds, until a client's session expires after being created. Once the expiry time has been reached, subsequent requests may get sent to a different origin server. The accepted ranges per ``session_affinity`` policy are: - ``"cookie"`` / ``"ip_cookie"``: The current default of 23 hours will be used unless explicitly set. The accepted range of values is between [1800, 604800]. - ``"header"``: The current default of 1800 seconds will be used unless explicitly set. The accepted range of values is between [30, 3600]. Note: With session affinity by header, sessions only expire after they haven't been used for the number of seconds specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_ttl LoadBalancer#session_affinity_ttl}
        :param steering_policy: Steering Policy for this load balancer. - ``"off"``: Use ``default_pools``. - ``"geo"``: Use ``region_pools``/``country_pools``/``pop_pools``. For non-proxied requests, the country for ``country_pools`` is determined by ``location_strategy``. - ``"random"``: Select a pool randomly. - ``"dynamic_latency"``: Use round trip time to select the closest pool in default_pools (requires pool health checks). - ``"proximity"``: Use the pools' latitude and longitude to select the closest pool using the Cloudflare PoP location for proxied requests or the location determined by ``location_strategy`` for non-proxied requests. - ``"least_outstanding_requests"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of outstanding requests. Pools with more pending requests are weighted proportionately less relative to others. - ``"least_connections"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of open connections. Pools with more open connections are weighted proportionately less relative to others. Supported for HTTP/1 and HTTP/2 connections. - ``""``: Will map to ``"geo"`` if you use ``region_pools``/``country_pools``/``pop_pools`` otherwise ``"off"``. Available values: "off", "geo", "random", "dynamic_latency", "proximity", "least_outstanding_requests", "least_connections", "". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#steering_policy LoadBalancer#steering_policy}
        :param ttl: Time to live (TTL) of the DNS entry for the IP address returned by this load balancer. This only applies to gray-clouded (unproxied) load balancers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#ttl LoadBalancer#ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(adaptive_routing, dict):
            adaptive_routing = LoadBalancerAdaptiveRouting(**adaptive_routing)
        if isinstance(location_strategy, dict):
            location_strategy = LoadBalancerLocationStrategy(**location_strategy)
        if isinstance(random_steering, dict):
            random_steering = LoadBalancerRandomSteering(**random_steering)
        if isinstance(session_affinity_attributes, dict):
            session_affinity_attributes = LoadBalancerSessionAffinityAttributes(**session_affinity_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__179a274ba88b1187743571bdcd7d729435f5abbf8faf21f1b93231a9af798a1f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument default_pools", value=default_pools, expected_type=type_hints["default_pools"])
            check_type(argname="argument fallback_pool", value=fallback_pool, expected_type=type_hints["fallback_pool"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument adaptive_routing", value=adaptive_routing, expected_type=type_hints["adaptive_routing"])
            check_type(argname="argument country_pools", value=country_pools, expected_type=type_hints["country_pools"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument location_strategy", value=location_strategy, expected_type=type_hints["location_strategy"])
            check_type(argname="argument networks", value=networks, expected_type=type_hints["networks"])
            check_type(argname="argument pop_pools", value=pop_pools, expected_type=type_hints["pop_pools"])
            check_type(argname="argument proxied", value=proxied, expected_type=type_hints["proxied"])
            check_type(argname="argument random_steering", value=random_steering, expected_type=type_hints["random_steering"])
            check_type(argname="argument region_pools", value=region_pools, expected_type=type_hints["region_pools"])
            check_type(argname="argument rules", value=rules, expected_type=type_hints["rules"])
            check_type(argname="argument session_affinity", value=session_affinity, expected_type=type_hints["session_affinity"])
            check_type(argname="argument session_affinity_attributes", value=session_affinity_attributes, expected_type=type_hints["session_affinity_attributes"])
            check_type(argname="argument session_affinity_ttl", value=session_affinity_ttl, expected_type=type_hints["session_affinity_ttl"])
            check_type(argname="argument steering_policy", value=steering_policy, expected_type=type_hints["steering_policy"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "default_pools": default_pools,
            "fallback_pool": fallback_pool,
            "name": name,
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
        if adaptive_routing is not None:
            self._values["adaptive_routing"] = adaptive_routing
        if country_pools is not None:
            self._values["country_pools"] = country_pools
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if location_strategy is not None:
            self._values["location_strategy"] = location_strategy
        if networks is not None:
            self._values["networks"] = networks
        if pop_pools is not None:
            self._values["pop_pools"] = pop_pools
        if proxied is not None:
            self._values["proxied"] = proxied
        if random_steering is not None:
            self._values["random_steering"] = random_steering
        if region_pools is not None:
            self._values["region_pools"] = region_pools
        if rules is not None:
            self._values["rules"] = rules
        if session_affinity is not None:
            self._values["session_affinity"] = session_affinity
        if session_affinity_attributes is not None:
            self._values["session_affinity_attributes"] = session_affinity_attributes
        if session_affinity_ttl is not None:
            self._values["session_affinity_ttl"] = session_affinity_ttl
        if steering_policy is not None:
            self._values["steering_policy"] = steering_policy
        if ttl is not None:
            self._values["ttl"] = ttl

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
    def default_pools(self) -> typing.List[builtins.str]:
        '''A list of pool IDs ordered by their failover priority.

        Pools defined here are used by default, or when region_pools are not configured for a given region.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_pools LoadBalancer#default_pools}
        '''
        result = self._values.get("default_pools")
        assert result is not None, "Required property 'default_pools' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def fallback_pool(self) -> builtins.str:
        '''The pool ID to use when all other pools are detected as unhealthy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#fallback_pool LoadBalancer#fallback_pool}
        '''
        result = self._values.get("fallback_pool")
        assert result is not None, "Required property 'fallback_pool' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The DNS hostname to associate with your Load Balancer.

        If this hostname already exists as a DNS record in Cloudflare's DNS, the Load Balancer will take precedence and the DNS record will not be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#name LoadBalancer#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#zone_id LoadBalancer#zone_id}.'''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def adaptive_routing(self) -> typing.Optional[LoadBalancerAdaptiveRouting]:
        '''Controls features that modify the routing of requests to pools and origins in response to dynamic conditions, such as during the interval between active health monitoring requests.

        For example, zero-downtime failover occurs immediately when an origin becomes unavailable due to HTTP 521, 522, or 523 response codes. If there is another healthy origin in the same pool, the request is retried once against this alternate origin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#adaptive_routing LoadBalancer#adaptive_routing}
        '''
        result = self._values.get("adaptive_routing")
        return typing.cast(typing.Optional[LoadBalancerAdaptiveRouting], result)

    @builtins.property
    def country_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country.

        Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#country_pools LoadBalancer#country_pools}
        '''
        result = self._values.get("country_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Object description.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#description LoadBalancer#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to enable (the default) this load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#enabled LoadBalancer#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def location_strategy(self) -> typing.Optional["LoadBalancerLocationStrategy"]:
        '''Controls location-based steering for non-proxied requests. See ``steering_policy`` to learn how steering is affected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#location_strategy LoadBalancer#location_strategy}
        '''
        result = self._values.get("location_strategy")
        return typing.cast(typing.Optional["LoadBalancerLocationStrategy"], result)

    @builtins.property
    def networks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of networks where Load Balancer or Pool is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#networks LoadBalancer#networks}
        '''
        result = self._values.get("networks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pop_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter).

        Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pop_pools LoadBalancer#pop_pools}
        '''
        result = self._values.get("pop_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def proxied(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether the hostname should be gray clouded (false) or orange clouded (true).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#proxied LoadBalancer#proxied}
        '''
        result = self._values.get("proxied")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def random_steering(self) -> typing.Optional["LoadBalancerRandomSteering"]:
        '''Configures pool weights.

        - ``steering_policy="random"``: A random pool is selected with probability proportional to pool weights.
        - ``steering_policy="least_outstanding_requests"``: Use pool weights to scale each pool's outstanding requests.
        - ``steering_policy="least_connections"``: Use pool weights to scale each pool's open connections.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#random_steering LoadBalancer#random_steering}
        '''
        result = self._values.get("random_steering")
        return typing.cast(typing.Optional["LoadBalancerRandomSteering"], result)

    @builtins.property
    def region_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region.

        Any regions not explicitly defined will fall back to using default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#region_pools LoadBalancer#region_pools}
        '''
        result = self._values.get("region_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def rules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadBalancerRules"]]]:
        '''BETA Field Not General Access: A list of rules for this load balancer to execute.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#rules LoadBalancer#rules}
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadBalancerRules"]]], result)

    @builtins.property
    def session_affinity(self) -> typing.Optional[builtins.str]:
        '''Specifies the type of session affinity the load balancer should use unless specified as ``"none"``.

        The supported types are: - ``"cookie"``: On the first request to a proxied load balancer, a cookie is generated, encoding information of which origin the request will be forwarded to. Subsequent requests, by the same client to the same load balancer, will be sent to the origin server the cookie encodes, for the duration of the cookie and as long as the origin server remains healthy. If the cookie has expired or the origin server is unhealthy, then a new origin server is calculated and used. - ``"ip_cookie"``: Behaves the same as ``"cookie"`` except the initial origin selection is stable and based on the client's ip address. - ``"header"``: On the first request to a proxied load balancer, a session key based on the configured HTTP headers (see ``session_affinity_attributes.headers``) is generated, encoding the request headers used for storing in the load balancer session state which origin the request will be forwarded to. Subsequent requests to the load balancer with the same headers will be sent to the same origin server, for the duration of the session and as long as the origin server remains healthy. If the session has been idle for the duration of ``session_affinity_ttl`` seconds or the origin server is unhealthy, then a new origin server is calculated and used. See ``headers`` in ``session_affinity_attributes`` for additional required configuration.
        Available values: "none", "cookie", "ip_cookie", "header".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity LoadBalancer#session_affinity}
        '''
        result = self._values.get("session_affinity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_affinity_attributes(
        self,
    ) -> typing.Optional["LoadBalancerSessionAffinityAttributes"]:
        '''Configures attributes for session affinity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_attributes LoadBalancer#session_affinity_attributes}
        '''
        result = self._values.get("session_affinity_attributes")
        return typing.cast(typing.Optional["LoadBalancerSessionAffinityAttributes"], result)

    @builtins.property
    def session_affinity_ttl(self) -> typing.Optional[jsii.Number]:
        '''Time, in seconds, until a client's session expires after being created.

        Once the expiry time has been reached, subsequent requests may get sent to a different origin server. The accepted ranges per ``session_affinity`` policy are: - ``"cookie"`` / ``"ip_cookie"``: The current default of 23 hours will be used unless explicitly set. The accepted range of values is between [1800, 604800]. - ``"header"``: The current default of 1800 seconds will be used unless explicitly set. The accepted range of values is between [30, 3600]. Note: With session affinity by header, sessions only expire after they haven't been used for the number of seconds specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_ttl LoadBalancer#session_affinity_ttl}
        '''
        result = self._values.get("session_affinity_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def steering_policy(self) -> typing.Optional[builtins.str]:
        '''Steering Policy for this load balancer.

        - ``"off"``: Use ``default_pools``.
        - ``"geo"``: Use ``region_pools``/``country_pools``/``pop_pools``. For non-proxied requests, the country for ``country_pools`` is determined by ``location_strategy``.
        - ``"random"``: Select a pool randomly.
        - ``"dynamic_latency"``: Use round trip time to select the closest pool in default_pools (requires pool health checks).
        - ``"proximity"``: Use the pools' latitude and longitude to select the closest pool using the Cloudflare PoP location for proxied requests or the location determined by ``location_strategy`` for non-proxied requests.
        - ``"least_outstanding_requests"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of outstanding requests. Pools with more pending requests are weighted proportionately less relative to others.
        - ``"least_connections"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of open connections. Pools with more open connections are weighted proportionately less relative to others. Supported for HTTP/1 and HTTP/2 connections.
        - ``""``: Will map to ``"geo"`` if you use ``region_pools``/``country_pools``/``pop_pools`` otherwise ``"off"``.
          Available values: "off", "geo", "random", "dynamic_latency", "proximity", "least_outstanding_requests", "least_connections", "".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#steering_policy LoadBalancer#steering_policy}
        '''
        result = self._values.get("steering_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''Time to live (TTL) of the DNS entry for the IP address returned by this load balancer.

        This only applies to gray-clouded (unproxied) load balancers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#ttl LoadBalancer#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerLocationStrategy",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "prefer_ecs": "preferEcs"},
)
class LoadBalancerLocationStrategy:
    def __init__(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        prefer_ecs: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mode: Determines the authoritative location when ECS is not preferred, does not exist in the request, or its GeoIP lookup is unsuccessful. - ``"pop"``: Use the Cloudflare PoP location. - ``"resolver_ip"``: Use the DNS resolver GeoIP location. If the GeoIP lookup is unsuccessful, use the Cloudflare PoP location. Available values: "pop", "resolver_ip". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#mode LoadBalancer#mode}
        :param prefer_ecs: Whether the EDNS Client Subnet (ECS) GeoIP should be preferred as the authoritative location. - ``"always"``: Always prefer ECS. - ``"never"``: Never prefer ECS. - ``"proximity"``: Prefer ECS only when ``steering_policy="proximity"``. - ``"geo"``: Prefer ECS only when ``steering_policy="geo"``. Available values: "always", "never", "proximity", "geo". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#prefer_ecs LoadBalancer#prefer_ecs}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71d0457eea690b702cd82d00d1d62a0d5a8fe1280f78f5baff5cd4e5a844b3b2)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument prefer_ecs", value=prefer_ecs, expected_type=type_hints["prefer_ecs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if prefer_ecs is not None:
            self._values["prefer_ecs"] = prefer_ecs

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Determines the authoritative location when ECS is not preferred, does not exist in the request, or its GeoIP lookup is unsuccessful.

        - ``"pop"``: Use the Cloudflare PoP location.
        - ``"resolver_ip"``: Use the DNS resolver GeoIP location. If the GeoIP lookup is unsuccessful, use the Cloudflare PoP location.
          Available values: "pop", "resolver_ip".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#mode LoadBalancer#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefer_ecs(self) -> typing.Optional[builtins.str]:
        '''Whether the EDNS Client Subnet (ECS) GeoIP should be preferred as the authoritative location.

        - ``"always"``: Always prefer ECS.
        - ``"never"``: Never prefer ECS.
        - ``"proximity"``: Prefer ECS only when ``steering_policy="proximity"``.
        - ``"geo"``: Prefer ECS only when ``steering_policy="geo"``.
          Available values: "always", "never", "proximity", "geo".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#prefer_ecs LoadBalancer#prefer_ecs}
        '''
        result = self._values.get("prefer_ecs")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerLocationStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerLocationStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerLocationStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e81b5884646eb683c1088e82b1ba373165f971f9550ab7a9950624c0fa774f6f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetPreferEcs")
    def reset_prefer_ecs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferEcs", []))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="preferEcsInput")
    def prefer_ecs_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferEcsInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__283834d4efe18f2ecca14babcc0cff3cc686560412d787bb702fb0f888ee83e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferEcs")
    def prefer_ecs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferEcs"))

    @prefer_ecs.setter
    def prefer_ecs(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e7502d6738609e16ad083c65590cb0aae8820f91260ffc08dc679caa3a79d05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferEcs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerLocationStrategy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerLocationStrategy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerLocationStrategy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__154dac22f09bd45bd574fb93d3a050a49415bdd268301d55ed3771479657a7a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRandomSteering",
    jsii_struct_bases=[],
    name_mapping={"default_weight": "defaultWeight", "pool_weights": "poolWeights"},
)
class LoadBalancerRandomSteering:
    def __init__(
        self,
        *,
        default_weight: typing.Optional[jsii.Number] = None,
        pool_weights: typing.Optional[typing.Mapping[builtins.str, jsii.Number]] = None,
    ) -> None:
        '''
        :param default_weight: The default weight for pools in the load balancer that are not specified in the pool_weights map. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_weight LoadBalancer#default_weight}
        :param pool_weights: A mapping of pool IDs to custom weights. The weight is relative to other pools in the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pool_weights LoadBalancer#pool_weights}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee03b4afc82f161efabb876910cdab21e26982c73d8eef161bdf1806f028519b)
            check_type(argname="argument default_weight", value=default_weight, expected_type=type_hints["default_weight"])
            check_type(argname="argument pool_weights", value=pool_weights, expected_type=type_hints["pool_weights"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if default_weight is not None:
            self._values["default_weight"] = default_weight
        if pool_weights is not None:
            self._values["pool_weights"] = pool_weights

    @builtins.property
    def default_weight(self) -> typing.Optional[jsii.Number]:
        '''The default weight for pools in the load balancer that are not specified in the pool_weights map.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_weight LoadBalancer#default_weight}
        '''
        result = self._values.get("default_weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pool_weights(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, jsii.Number]]:
        '''A mapping of pool IDs to custom weights. The weight is relative to other pools in the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pool_weights LoadBalancer#pool_weights}
        '''
        result = self._values.get("pool_weights")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerRandomSteering(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerRandomSteeringOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRandomSteeringOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5eff3856a00584fdf493670649b9ffda272af232d2ba2774e2a2317ee7892ea4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDefaultWeight")
    def reset_default_weight(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultWeight", []))

    @jsii.member(jsii_name="resetPoolWeights")
    def reset_pool_weights(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPoolWeights", []))

    @builtins.property
    @jsii.member(jsii_name="defaultWeightInput")
    def default_weight_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultWeightInput"))

    @builtins.property
    @jsii.member(jsii_name="poolWeightsInput")
    def pool_weights_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, jsii.Number]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, jsii.Number]], jsii.get(self, "poolWeightsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultWeight")
    def default_weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultWeight"))

    @default_weight.setter
    def default_weight(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64146deae2c3ed36b3305117fa981b5b7c9a1164677f036cb508f162493c0086)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultWeight", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="poolWeights")
    def pool_weights(self) -> typing.Mapping[builtins.str, jsii.Number]:
        return typing.cast(typing.Mapping[builtins.str, jsii.Number], jsii.get(self, "poolWeights"))

    @pool_weights.setter
    def pool_weights(self, value: typing.Mapping[builtins.str, jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9973a0c91cce2364e7bca20eead582d2bb02780a7f8a4182cefbd38c49d0b90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "poolWeights", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRandomSteering]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRandomSteering]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRandomSteering]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aecaf7995fee6243343cf4dfffae58904bdf43c75cc42227c30cfacfa4083ed8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRules",
    jsii_struct_bases=[],
    name_mapping={
        "condition": "condition",
        "disabled": "disabled",
        "fixed_response": "fixedResponse",
        "name": "name",
        "overrides": "overrides",
        "priority": "priority",
        "terminates": "terminates",
    },
)
class LoadBalancerRules:
    def __init__(
        self,
        *,
        condition: typing.Optional[builtins.str] = None,
        disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fixed_response: typing.Optional[typing.Union["LoadBalancerRulesFixedResponse", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        overrides: typing.Optional[typing.Union["LoadBalancerRulesOverrides", typing.Dict[builtins.str, typing.Any]]] = None,
        priority: typing.Optional[jsii.Number] = None,
        terminates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param condition: The condition expressions to evaluate. If the condition evaluates to true, the overrides or fixed_response in this rule will be applied. An empty condition is always true. For more details on condition expressions, please see https://developers.cloudflare.com/load-balancing/understand-basics/load-balancing-rules/expressions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#condition LoadBalancer#condition}
        :param disabled: Disable this specific rule. It will no longer be evaluated by this load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#disabled LoadBalancer#disabled}
        :param fixed_response: A collection of fields used to directly respond to the eyeball instead of routing to a pool. If a fixed_response is supplied the rule will be marked as terminates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#fixed_response LoadBalancer#fixed_response}
        :param name: Name of this rule. Only used for human readability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#name LoadBalancer#name}
        :param overrides: A collection of overrides to apply to the load balancer when this rule's condition is true. All fields are optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#overrides LoadBalancer#overrides}
        :param priority: The order in which rules should be executed in relation to each other. Lower values are executed first. Values do not need to be sequential. If no value is provided for any rule the array order of the rules field will be used to assign a priority. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#priority LoadBalancer#priority}
        :param terminates: If this rule's condition is true, this causes rule evaluation to stop after processing this rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#terminates LoadBalancer#terminates}
        '''
        if isinstance(fixed_response, dict):
            fixed_response = LoadBalancerRulesFixedResponse(**fixed_response)
        if isinstance(overrides, dict):
            overrides = LoadBalancerRulesOverrides(**overrides)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fdf42061a6652ffd6986a8e2ec9edad4427316f2d7a2321fe44f8214e666716)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument disabled", value=disabled, expected_type=type_hints["disabled"])
            check_type(argname="argument fixed_response", value=fixed_response, expected_type=type_hints["fixed_response"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument overrides", value=overrides, expected_type=type_hints["overrides"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument terminates", value=terminates, expected_type=type_hints["terminates"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if condition is not None:
            self._values["condition"] = condition
        if disabled is not None:
            self._values["disabled"] = disabled
        if fixed_response is not None:
            self._values["fixed_response"] = fixed_response
        if name is not None:
            self._values["name"] = name
        if overrides is not None:
            self._values["overrides"] = overrides
        if priority is not None:
            self._values["priority"] = priority
        if terminates is not None:
            self._values["terminates"] = terminates

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''The condition expressions to evaluate.

        If the condition evaluates to true, the overrides or fixed_response in this rule will be applied. An empty condition is always true. For more details on condition expressions, please see https://developers.cloudflare.com/load-balancing/understand-basics/load-balancing-rules/expressions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#condition LoadBalancer#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable this specific rule. It will no longer be evaluated by this load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#disabled LoadBalancer#disabled}
        '''
        result = self._values.get("disabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def fixed_response(self) -> typing.Optional["LoadBalancerRulesFixedResponse"]:
        '''A collection of fields used to directly respond to the eyeball instead of routing to a pool.

        If a fixed_response is supplied the rule will be marked as terminates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#fixed_response LoadBalancer#fixed_response}
        '''
        result = self._values.get("fixed_response")
        return typing.cast(typing.Optional["LoadBalancerRulesFixedResponse"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of this rule. Only used for human readability.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#name LoadBalancer#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def overrides(self) -> typing.Optional["LoadBalancerRulesOverrides"]:
        '''A collection of overrides to apply to the load balancer when this rule's condition is true.

        All fields are optional.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#overrides LoadBalancer#overrides}
        '''
        result = self._values.get("overrides")
        return typing.cast(typing.Optional["LoadBalancerRulesOverrides"], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''The order in which rules should be executed in relation to each other.

        Lower values are executed first. Values do not need to be sequential. If no value is provided for any rule the array order of the rules field will be used to assign a priority.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#priority LoadBalancer#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def terminates(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If this rule's condition is true, this causes rule evaluation to stop after processing this rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#terminates LoadBalancer#terminates}
        '''
        result = self._values.get("terminates")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesFixedResponse",
    jsii_struct_bases=[],
    name_mapping={
        "content_type": "contentType",
        "location": "location",
        "message_body": "messageBody",
        "status_code": "statusCode",
    },
)
class LoadBalancerRulesFixedResponse:
    def __init__(
        self,
        *,
        content_type: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
        message_body: typing.Optional[builtins.str] = None,
        status_code: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content_type: The http 'Content-Type' header to include in the response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#content_type LoadBalancer#content_type}
        :param location: The http 'Location' header to include in the response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#location LoadBalancer#location}
        :param message_body: Text to include as the http body. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#message_body LoadBalancer#message_body}
        :param status_code: The http status code to respond with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#status_code LoadBalancer#status_code}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e06a358aa30363c798305232d6e623350e1f1c44109315e688dbf167c0529967)
            check_type(argname="argument content_type", value=content_type, expected_type=type_hints["content_type"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument message_body", value=message_body, expected_type=type_hints["message_body"])
            check_type(argname="argument status_code", value=status_code, expected_type=type_hints["status_code"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if content_type is not None:
            self._values["content_type"] = content_type
        if location is not None:
            self._values["location"] = location
        if message_body is not None:
            self._values["message_body"] = message_body
        if status_code is not None:
            self._values["status_code"] = status_code

    @builtins.property
    def content_type(self) -> typing.Optional[builtins.str]:
        '''The http 'Content-Type' header to include in the response.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#content_type LoadBalancer#content_type}
        '''
        result = self._values.get("content_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def location(self) -> typing.Optional[builtins.str]:
        '''The http 'Location' header to include in the response.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#location LoadBalancer#location}
        '''
        result = self._values.get("location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_body(self) -> typing.Optional[builtins.str]:
        '''Text to include as the http body.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#message_body LoadBalancer#message_body}
        '''
        result = self._values.get("message_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status_code(self) -> typing.Optional[jsii.Number]:
        '''The http status code to respond with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#status_code LoadBalancer#status_code}
        '''
        result = self._values.get("status_code")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerRulesFixedResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerRulesFixedResponseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesFixedResponseOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__80108d9aa8c23f36e4b7063ba0aa4b31c3e1275949022514800f4c8eb0d14916)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetContentType")
    def reset_content_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentType", []))

    @jsii.member(jsii_name="resetLocation")
    def reset_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocation", []))

    @jsii.member(jsii_name="resetMessageBody")
    def reset_message_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageBody", []))

    @jsii.member(jsii_name="resetStatusCode")
    def reset_status_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatusCode", []))

    @builtins.property
    @jsii.member(jsii_name="contentTypeInput")
    def content_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="messageBodyInput")
    def message_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageBodyInput"))

    @builtins.property
    @jsii.member(jsii_name="statusCodeInput")
    def status_code_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "statusCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86270d9848d23db8e4200b0e35ebc9fc45e5da1d517d6a31bc7780f890383a91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87b015c6e42a266873f9a700c8a31631697378013d1c81a51f6dee7696471a23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messageBody")
    def message_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageBody"))

    @message_body.setter
    def message_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69434f811e173e46da313f9aedd1026400d0a3b9a0174f3f0300bfbc6774e9f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageBody", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cf77b24367c791875e918c3a9cedf3f2147f45e4dacbb0aeb750962fad39bd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statusCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesFixedResponse]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesFixedResponse]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesFixedResponse]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1307772712904f3a25b1d8ff5167a3a18cacea694ac2ce73bd9c48607726e4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadBalancerRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__59baa239d8e3ea247aac1525b719e2de365c0547c13a6e6738e91104b679e18f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "LoadBalancerRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dd5d663b462645948272bde24a3e6a192a833e4d72fadcfbe9d26e8affa9a19)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("LoadBalancerRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddd04c38c24c581759071ae44418fc173fd284b9cd0edbbd2f85e435c9c1c578)
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
            type_hints = typing.get_type_hints(_typecheckingstub__521357c4039603ba4551315908639be87cc4d2d45ba7c9ab2982e88e9e19fe09)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3db24e37e9660436ce55e2591e403ae318662c1893aea722586425995eeb689f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadBalancerRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadBalancerRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadBalancerRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2aab7db6cb77dc7546b011c288f299e644f90b4e6681a5fadb150655069bd9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadBalancerRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eeb822e0195a87da51205f90f18bdae2e8a011b0c0b8be0a23f2767a53a54c34)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putFixedResponse")
    def put_fixed_response(
        self,
        *,
        content_type: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
        message_body: typing.Optional[builtins.str] = None,
        status_code: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param content_type: The http 'Content-Type' header to include in the response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#content_type LoadBalancer#content_type}
        :param location: The http 'Location' header to include in the response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#location LoadBalancer#location}
        :param message_body: Text to include as the http body. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#message_body LoadBalancer#message_body}
        :param status_code: The http status code to respond with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#status_code LoadBalancer#status_code}
        '''
        value = LoadBalancerRulesFixedResponse(
            content_type=content_type,
            location=location,
            message_body=message_body,
            status_code=status_code,
        )

        return typing.cast(None, jsii.invoke(self, "putFixedResponse", [value]))

    @jsii.member(jsii_name="putOverrides")
    def put_overrides(
        self,
        *,
        adaptive_routing: typing.Optional[typing.Union["LoadBalancerRulesOverridesAdaptiveRouting", typing.Dict[builtins.str, typing.Any]]] = None,
        country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        default_pools: typing.Optional[typing.Sequence[builtins.str]] = None,
        fallback_pool: typing.Optional[builtins.str] = None,
        location_strategy: typing.Optional[typing.Union["LoadBalancerRulesOverridesLocationStrategy", typing.Dict[builtins.str, typing.Any]]] = None,
        pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        random_steering: typing.Optional[typing.Union["LoadBalancerRulesOverridesRandomSteering", typing.Dict[builtins.str, typing.Any]]] = None,
        region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        session_affinity: typing.Optional[builtins.str] = None,
        session_affinity_attributes: typing.Optional[typing.Union["LoadBalancerRulesOverridesSessionAffinityAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        session_affinity_ttl: typing.Optional[jsii.Number] = None,
        steering_policy: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param adaptive_routing: Controls features that modify the routing of requests to pools and origins in response to dynamic conditions, such as during the interval between active health monitoring requests. For example, zero-downtime failover occurs immediately when an origin becomes unavailable due to HTTP 521, 522, or 523 response codes. If there is another healthy origin in the same pool, the request is retried once against this alternate origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#adaptive_routing LoadBalancer#adaptive_routing}
        :param country_pools: A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country. Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#country_pools LoadBalancer#country_pools}
        :param default_pools: A list of pool IDs ordered by their failover priority. Pools defined here are used by default, or when region_pools are not configured for a given region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_pools LoadBalancer#default_pools}
        :param fallback_pool: The pool ID to use when all other pools are detected as unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#fallback_pool LoadBalancer#fallback_pool}
        :param location_strategy: Controls location-based steering for non-proxied requests. See ``steering_policy`` to learn how steering is affected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#location_strategy LoadBalancer#location_strategy}
        :param pop_pools: Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter). Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pop_pools LoadBalancer#pop_pools}
        :param random_steering: Configures pool weights. - ``steering_policy="random"``: A random pool is selected with probability proportional to pool weights. - ``steering_policy="least_outstanding_requests"``: Use pool weights to scale each pool's outstanding requests. - ``steering_policy="least_connections"``: Use pool weights to scale each pool's open connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#random_steering LoadBalancer#random_steering}
        :param region_pools: A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region. Any regions not explicitly defined will fall back to using default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#region_pools LoadBalancer#region_pools}
        :param session_affinity: Specifies the type of session affinity the load balancer should use unless specified as ``"none"``. The supported types are: - ``"cookie"``: On the first request to a proxied load balancer, a cookie is generated, encoding information of which origin the request will be forwarded to. Subsequent requests, by the same client to the same load balancer, will be sent to the origin server the cookie encodes, for the duration of the cookie and as long as the origin server remains healthy. If the cookie has expired or the origin server is unhealthy, then a new origin server is calculated and used. - ``"ip_cookie"``: Behaves the same as ``"cookie"`` except the initial origin selection is stable and based on the client's ip address. - ``"header"``: On the first request to a proxied load balancer, a session key based on the configured HTTP headers (see ``session_affinity_attributes.headers``) is generated, encoding the request headers used for storing in the load balancer session state which origin the request will be forwarded to. Subsequent requests to the load balancer with the same headers will be sent to the same origin server, for the duration of the session and as long as the origin server remains healthy. If the session has been idle for the duration of ``session_affinity_ttl`` seconds or the origin server is unhealthy, then a new origin server is calculated and used. See ``headers`` in ``session_affinity_attributes`` for additional required configuration. Available values: "none", "cookie", "ip_cookie", "header". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity LoadBalancer#session_affinity}
        :param session_affinity_attributes: Configures attributes for session affinity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_attributes LoadBalancer#session_affinity_attributes}
        :param session_affinity_ttl: Time, in seconds, until a client's session expires after being created. Once the expiry time has been reached, subsequent requests may get sent to a different origin server. The accepted ranges per ``session_affinity`` policy are: - ``"cookie"`` / ``"ip_cookie"``: The current default of 23 hours will be used unless explicitly set. The accepted range of values is between [1800, 604800]. - ``"header"``: The current default of 1800 seconds will be used unless explicitly set. The accepted range of values is between [30, 3600]. Note: With session affinity by header, sessions only expire after they haven't been used for the number of seconds specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_ttl LoadBalancer#session_affinity_ttl}
        :param steering_policy: Steering Policy for this load balancer. - ``"off"``: Use ``default_pools``. - ``"geo"``: Use ``region_pools``/``country_pools``/``pop_pools``. For non-proxied requests, the country for ``country_pools`` is determined by ``location_strategy``. - ``"random"``: Select a pool randomly. - ``"dynamic_latency"``: Use round trip time to select the closest pool in default_pools (requires pool health checks). - ``"proximity"``: Use the pools' latitude and longitude to select the closest pool using the Cloudflare PoP location for proxied requests or the location determined by ``location_strategy`` for non-proxied requests. - ``"least_outstanding_requests"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of outstanding requests. Pools with more pending requests are weighted proportionately less relative to others. - ``"least_connections"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of open connections. Pools with more open connections are weighted proportionately less relative to others. Supported for HTTP/1 and HTTP/2 connections. - ``""``: Will map to ``"geo"`` if you use ``region_pools``/``country_pools``/``pop_pools`` otherwise ``"off"``. Available values: "off", "geo", "random", "dynamic_latency", "proximity", "least_outstanding_requests", "least_connections", "". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#steering_policy LoadBalancer#steering_policy}
        :param ttl: Time to live (TTL) of the DNS entry for the IP address returned by this load balancer. This only applies to gray-clouded (unproxied) load balancers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#ttl LoadBalancer#ttl}
        '''
        value = LoadBalancerRulesOverrides(
            adaptive_routing=adaptive_routing,
            country_pools=country_pools,
            default_pools=default_pools,
            fallback_pool=fallback_pool,
            location_strategy=location_strategy,
            pop_pools=pop_pools,
            random_steering=random_steering,
            region_pools=region_pools,
            session_affinity=session_affinity,
            session_affinity_attributes=session_affinity_attributes,
            session_affinity_ttl=session_affinity_ttl,
            steering_policy=steering_policy,
            ttl=ttl,
        )

        return typing.cast(None, jsii.invoke(self, "putOverrides", [value]))

    @jsii.member(jsii_name="resetCondition")
    def reset_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCondition", []))

    @jsii.member(jsii_name="resetDisabled")
    def reset_disabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisabled", []))

    @jsii.member(jsii_name="resetFixedResponse")
    def reset_fixed_response(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFixedResponse", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOverrides")
    def reset_overrides(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrides", []))

    @jsii.member(jsii_name="resetPriority")
    def reset_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPriority", []))

    @jsii.member(jsii_name="resetTerminates")
    def reset_terminates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminates", []))

    @builtins.property
    @jsii.member(jsii_name="fixedResponse")
    def fixed_response(self) -> LoadBalancerRulesFixedResponseOutputReference:
        return typing.cast(LoadBalancerRulesFixedResponseOutputReference, jsii.get(self, "fixedResponse"))

    @builtins.property
    @jsii.member(jsii_name="overrides")
    def overrides(self) -> "LoadBalancerRulesOverridesOutputReference":
        return typing.cast("LoadBalancerRulesOverridesOutputReference", jsii.get(self, "overrides"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="disabledInput")
    def disabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disabledInput"))

    @builtins.property
    @jsii.member(jsii_name="fixedResponseInput")
    def fixed_response_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesFixedResponse]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesFixedResponse]], jsii.get(self, "fixedResponseInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="overridesInput")
    def overrides_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerRulesOverrides"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerRulesOverrides"]], jsii.get(self, "overridesInput"))

    @builtins.property
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property
    @jsii.member(jsii_name="terminatesInput")
    def terminates_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "terminatesInput"))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "condition"))

    @condition.setter
    def condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc94eb429048c5fdcba032f9097bff452e96a8b87a21ed14207910ff9ebd8e56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "condition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disabled")
    def disabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disabled"))

    @disabled.setter
    def disabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__970524bed5e99690908d85d4d7ac78a7ba44a085d24880cb72687193e0e9bc09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7098ca56037e693d628373e3a6f18993274641304d612d1ad77069af9d82e1ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec3294de3d4a5c794f3bceef16b338e69245d8e1474e2ca04d3e6c6914850bd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terminates")
    def terminates(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "terminates"))

    @terminates.setter
    def terminates(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66223bd8cfe2d18c3c9439fce67488c94926fc3e7f8f4f9a245979aa2a5bdce8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2be777163ff6c1b6b7d0e9fbbc7f8a8d9c7d76e6976ca4eeac1712b453685526)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverrides",
    jsii_struct_bases=[],
    name_mapping={
        "adaptive_routing": "adaptiveRouting",
        "country_pools": "countryPools",
        "default_pools": "defaultPools",
        "fallback_pool": "fallbackPool",
        "location_strategy": "locationStrategy",
        "pop_pools": "popPools",
        "random_steering": "randomSteering",
        "region_pools": "regionPools",
        "session_affinity": "sessionAffinity",
        "session_affinity_attributes": "sessionAffinityAttributes",
        "session_affinity_ttl": "sessionAffinityTtl",
        "steering_policy": "steeringPolicy",
        "ttl": "ttl",
    },
)
class LoadBalancerRulesOverrides:
    def __init__(
        self,
        *,
        adaptive_routing: typing.Optional[typing.Union["LoadBalancerRulesOverridesAdaptiveRouting", typing.Dict[builtins.str, typing.Any]]] = None,
        country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        default_pools: typing.Optional[typing.Sequence[builtins.str]] = None,
        fallback_pool: typing.Optional[builtins.str] = None,
        location_strategy: typing.Optional[typing.Union["LoadBalancerRulesOverridesLocationStrategy", typing.Dict[builtins.str, typing.Any]]] = None,
        pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        random_steering: typing.Optional[typing.Union["LoadBalancerRulesOverridesRandomSteering", typing.Dict[builtins.str, typing.Any]]] = None,
        region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
        session_affinity: typing.Optional[builtins.str] = None,
        session_affinity_attributes: typing.Optional[typing.Union["LoadBalancerRulesOverridesSessionAffinityAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        session_affinity_ttl: typing.Optional[jsii.Number] = None,
        steering_policy: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param adaptive_routing: Controls features that modify the routing of requests to pools and origins in response to dynamic conditions, such as during the interval between active health monitoring requests. For example, zero-downtime failover occurs immediately when an origin becomes unavailable due to HTTP 521, 522, or 523 response codes. If there is another healthy origin in the same pool, the request is retried once against this alternate origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#adaptive_routing LoadBalancer#adaptive_routing}
        :param country_pools: A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country. Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#country_pools LoadBalancer#country_pools}
        :param default_pools: A list of pool IDs ordered by their failover priority. Pools defined here are used by default, or when region_pools are not configured for a given region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_pools LoadBalancer#default_pools}
        :param fallback_pool: The pool ID to use when all other pools are detected as unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#fallback_pool LoadBalancer#fallback_pool}
        :param location_strategy: Controls location-based steering for non-proxied requests. See ``steering_policy`` to learn how steering is affected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#location_strategy LoadBalancer#location_strategy}
        :param pop_pools: Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter). Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pop_pools LoadBalancer#pop_pools}
        :param random_steering: Configures pool weights. - ``steering_policy="random"``: A random pool is selected with probability proportional to pool weights. - ``steering_policy="least_outstanding_requests"``: Use pool weights to scale each pool's outstanding requests. - ``steering_policy="least_connections"``: Use pool weights to scale each pool's open connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#random_steering LoadBalancer#random_steering}
        :param region_pools: A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region. Any regions not explicitly defined will fall back to using default_pools. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#region_pools LoadBalancer#region_pools}
        :param session_affinity: Specifies the type of session affinity the load balancer should use unless specified as ``"none"``. The supported types are: - ``"cookie"``: On the first request to a proxied load balancer, a cookie is generated, encoding information of which origin the request will be forwarded to. Subsequent requests, by the same client to the same load balancer, will be sent to the origin server the cookie encodes, for the duration of the cookie and as long as the origin server remains healthy. If the cookie has expired or the origin server is unhealthy, then a new origin server is calculated and used. - ``"ip_cookie"``: Behaves the same as ``"cookie"`` except the initial origin selection is stable and based on the client's ip address. - ``"header"``: On the first request to a proxied load balancer, a session key based on the configured HTTP headers (see ``session_affinity_attributes.headers``) is generated, encoding the request headers used for storing in the load balancer session state which origin the request will be forwarded to. Subsequent requests to the load balancer with the same headers will be sent to the same origin server, for the duration of the session and as long as the origin server remains healthy. If the session has been idle for the duration of ``session_affinity_ttl`` seconds or the origin server is unhealthy, then a new origin server is calculated and used. See ``headers`` in ``session_affinity_attributes`` for additional required configuration. Available values: "none", "cookie", "ip_cookie", "header". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity LoadBalancer#session_affinity}
        :param session_affinity_attributes: Configures attributes for session affinity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_attributes LoadBalancer#session_affinity_attributes}
        :param session_affinity_ttl: Time, in seconds, until a client's session expires after being created. Once the expiry time has been reached, subsequent requests may get sent to a different origin server. The accepted ranges per ``session_affinity`` policy are: - ``"cookie"`` / ``"ip_cookie"``: The current default of 23 hours will be used unless explicitly set. The accepted range of values is between [1800, 604800]. - ``"header"``: The current default of 1800 seconds will be used unless explicitly set. The accepted range of values is between [30, 3600]. Note: With session affinity by header, sessions only expire after they haven't been used for the number of seconds specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_ttl LoadBalancer#session_affinity_ttl}
        :param steering_policy: Steering Policy for this load balancer. - ``"off"``: Use ``default_pools``. - ``"geo"``: Use ``region_pools``/``country_pools``/``pop_pools``. For non-proxied requests, the country for ``country_pools`` is determined by ``location_strategy``. - ``"random"``: Select a pool randomly. - ``"dynamic_latency"``: Use round trip time to select the closest pool in default_pools (requires pool health checks). - ``"proximity"``: Use the pools' latitude and longitude to select the closest pool using the Cloudflare PoP location for proxied requests or the location determined by ``location_strategy`` for non-proxied requests. - ``"least_outstanding_requests"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of outstanding requests. Pools with more pending requests are weighted proportionately less relative to others. - ``"least_connections"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of open connections. Pools with more open connections are weighted proportionately less relative to others. Supported for HTTP/1 and HTTP/2 connections. - ``""``: Will map to ``"geo"`` if you use ``region_pools``/``country_pools``/``pop_pools`` otherwise ``"off"``. Available values: "off", "geo", "random", "dynamic_latency", "proximity", "least_outstanding_requests", "least_connections", "". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#steering_policy LoadBalancer#steering_policy}
        :param ttl: Time to live (TTL) of the DNS entry for the IP address returned by this load balancer. This only applies to gray-clouded (unproxied) load balancers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#ttl LoadBalancer#ttl}
        '''
        if isinstance(adaptive_routing, dict):
            adaptive_routing = LoadBalancerRulesOverridesAdaptiveRouting(**adaptive_routing)
        if isinstance(location_strategy, dict):
            location_strategy = LoadBalancerRulesOverridesLocationStrategy(**location_strategy)
        if isinstance(random_steering, dict):
            random_steering = LoadBalancerRulesOverridesRandomSteering(**random_steering)
        if isinstance(session_affinity_attributes, dict):
            session_affinity_attributes = LoadBalancerRulesOverridesSessionAffinityAttributes(**session_affinity_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75f9ec836d04efd6df32310c87de2c9677c1832a61280179f4a5f5628a3a2bdc)
            check_type(argname="argument adaptive_routing", value=adaptive_routing, expected_type=type_hints["adaptive_routing"])
            check_type(argname="argument country_pools", value=country_pools, expected_type=type_hints["country_pools"])
            check_type(argname="argument default_pools", value=default_pools, expected_type=type_hints["default_pools"])
            check_type(argname="argument fallback_pool", value=fallback_pool, expected_type=type_hints["fallback_pool"])
            check_type(argname="argument location_strategy", value=location_strategy, expected_type=type_hints["location_strategy"])
            check_type(argname="argument pop_pools", value=pop_pools, expected_type=type_hints["pop_pools"])
            check_type(argname="argument random_steering", value=random_steering, expected_type=type_hints["random_steering"])
            check_type(argname="argument region_pools", value=region_pools, expected_type=type_hints["region_pools"])
            check_type(argname="argument session_affinity", value=session_affinity, expected_type=type_hints["session_affinity"])
            check_type(argname="argument session_affinity_attributes", value=session_affinity_attributes, expected_type=type_hints["session_affinity_attributes"])
            check_type(argname="argument session_affinity_ttl", value=session_affinity_ttl, expected_type=type_hints["session_affinity_ttl"])
            check_type(argname="argument steering_policy", value=steering_policy, expected_type=type_hints["steering_policy"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if adaptive_routing is not None:
            self._values["adaptive_routing"] = adaptive_routing
        if country_pools is not None:
            self._values["country_pools"] = country_pools
        if default_pools is not None:
            self._values["default_pools"] = default_pools
        if fallback_pool is not None:
            self._values["fallback_pool"] = fallback_pool
        if location_strategy is not None:
            self._values["location_strategy"] = location_strategy
        if pop_pools is not None:
            self._values["pop_pools"] = pop_pools
        if random_steering is not None:
            self._values["random_steering"] = random_steering
        if region_pools is not None:
            self._values["region_pools"] = region_pools
        if session_affinity is not None:
            self._values["session_affinity"] = session_affinity
        if session_affinity_attributes is not None:
            self._values["session_affinity_attributes"] = session_affinity_attributes
        if session_affinity_ttl is not None:
            self._values["session_affinity_ttl"] = session_affinity_ttl
        if steering_policy is not None:
            self._values["steering_policy"] = steering_policy
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def adaptive_routing(
        self,
    ) -> typing.Optional["LoadBalancerRulesOverridesAdaptiveRouting"]:
        '''Controls features that modify the routing of requests to pools and origins in response to dynamic conditions, such as during the interval between active health monitoring requests.

        For example, zero-downtime failover occurs immediately when an origin becomes unavailable due to HTTP 521, 522, or 523 response codes. If there is another healthy origin in the same pool, the request is retried once against this alternate origin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#adaptive_routing LoadBalancer#adaptive_routing}
        '''
        result = self._values.get("adaptive_routing")
        return typing.cast(typing.Optional["LoadBalancerRulesOverridesAdaptiveRouting"], result)

    @builtins.property
    def country_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''A mapping of country codes to a list of pool IDs (ordered by their failover priority) for the given country.

        Any country not explicitly defined will fall back to using the corresponding region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#country_pools LoadBalancer#country_pools}
        '''
        result = self._values.get("country_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def default_pools(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of pool IDs ordered by their failover priority.

        Pools defined here are used by default, or when region_pools are not configured for a given region.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_pools LoadBalancer#default_pools}
        '''
        result = self._values.get("default_pools")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def fallback_pool(self) -> typing.Optional[builtins.str]:
        '''The pool ID to use when all other pools are detected as unhealthy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#fallback_pool LoadBalancer#fallback_pool}
        '''
        result = self._values.get("fallback_pool")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def location_strategy(
        self,
    ) -> typing.Optional["LoadBalancerRulesOverridesLocationStrategy"]:
        '''Controls location-based steering for non-proxied requests. See ``steering_policy`` to learn how steering is affected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#location_strategy LoadBalancer#location_strategy}
        '''
        result = self._values.get("location_strategy")
        return typing.cast(typing.Optional["LoadBalancerRulesOverridesLocationStrategy"], result)

    @builtins.property
    def pop_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''Enterprise only: A mapping of Cloudflare PoP identifiers to a list of pool IDs (ordered by their failover priority) for the PoP (datacenter).

        Any PoPs not explicitly defined will fall back to using the corresponding country_pool, then region_pool mapping if it exists else to default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pop_pools LoadBalancer#pop_pools}
        '''
        result = self._values.get("pop_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def random_steering(
        self,
    ) -> typing.Optional["LoadBalancerRulesOverridesRandomSteering"]:
        '''Configures pool weights.

        - ``steering_policy="random"``: A random pool is selected with probability proportional to pool weights.
        - ``steering_policy="least_outstanding_requests"``: Use pool weights to scale each pool's outstanding requests.
        - ``steering_policy="least_connections"``: Use pool weights to scale each pool's open connections.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#random_steering LoadBalancer#random_steering}
        '''
        result = self._values.get("random_steering")
        return typing.cast(typing.Optional["LoadBalancerRulesOverridesRandomSteering"], result)

    @builtins.property
    def region_pools(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        '''A mapping of region codes to a list of pool IDs (ordered by their failover priority) for the given region.

        Any regions not explicitly defined will fall back to using default_pools.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#region_pools LoadBalancer#region_pools}
        '''
        result = self._values.get("region_pools")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], result)

    @builtins.property
    def session_affinity(self) -> typing.Optional[builtins.str]:
        '''Specifies the type of session affinity the load balancer should use unless specified as ``"none"``.

        The supported types are: - ``"cookie"``: On the first request to a proxied load balancer, a cookie is generated, encoding information of which origin the request will be forwarded to. Subsequent requests, by the same client to the same load balancer, will be sent to the origin server the cookie encodes, for the duration of the cookie and as long as the origin server remains healthy. If the cookie has expired or the origin server is unhealthy, then a new origin server is calculated and used. - ``"ip_cookie"``: Behaves the same as ``"cookie"`` except the initial origin selection is stable and based on the client's ip address. - ``"header"``: On the first request to a proxied load balancer, a session key based on the configured HTTP headers (see ``session_affinity_attributes.headers``) is generated, encoding the request headers used for storing in the load balancer session state which origin the request will be forwarded to. Subsequent requests to the load balancer with the same headers will be sent to the same origin server, for the duration of the session and as long as the origin server remains healthy. If the session has been idle for the duration of ``session_affinity_ttl`` seconds or the origin server is unhealthy, then a new origin server is calculated and used. See ``headers`` in ``session_affinity_attributes`` for additional required configuration.
        Available values: "none", "cookie", "ip_cookie", "header".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity LoadBalancer#session_affinity}
        '''
        result = self._values.get("session_affinity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_affinity_attributes(
        self,
    ) -> typing.Optional["LoadBalancerRulesOverridesSessionAffinityAttributes"]:
        '''Configures attributes for session affinity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_attributes LoadBalancer#session_affinity_attributes}
        '''
        result = self._values.get("session_affinity_attributes")
        return typing.cast(typing.Optional["LoadBalancerRulesOverridesSessionAffinityAttributes"], result)

    @builtins.property
    def session_affinity_ttl(self) -> typing.Optional[jsii.Number]:
        '''Time, in seconds, until a client's session expires after being created.

        Once the expiry time has been reached, subsequent requests may get sent to a different origin server. The accepted ranges per ``session_affinity`` policy are: - ``"cookie"`` / ``"ip_cookie"``: The current default of 23 hours will be used unless explicitly set. The accepted range of values is between [1800, 604800]. - ``"header"``: The current default of 1800 seconds will be used unless explicitly set. The accepted range of values is between [30, 3600]. Note: With session affinity by header, sessions only expire after they haven't been used for the number of seconds specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#session_affinity_ttl LoadBalancer#session_affinity_ttl}
        '''
        result = self._values.get("session_affinity_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def steering_policy(self) -> typing.Optional[builtins.str]:
        '''Steering Policy for this load balancer.

        - ``"off"``: Use ``default_pools``.
        - ``"geo"``: Use ``region_pools``/``country_pools``/``pop_pools``. For non-proxied requests, the country for ``country_pools`` is determined by ``location_strategy``.
        - ``"random"``: Select a pool randomly.
        - ``"dynamic_latency"``: Use round trip time to select the closest pool in default_pools (requires pool health checks).
        - ``"proximity"``: Use the pools' latitude and longitude to select the closest pool using the Cloudflare PoP location for proxied requests or the location determined by ``location_strategy`` for non-proxied requests.
        - ``"least_outstanding_requests"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of outstanding requests. Pools with more pending requests are weighted proportionately less relative to others.
        - ``"least_connections"``: Select a pool by taking into consideration ``random_steering`` weights, as well as each pool's number of open connections. Pools with more open connections are weighted proportionately less relative to others. Supported for HTTP/1 and HTTP/2 connections.
        - ``""``: Will map to ``"geo"`` if you use ``region_pools``/``country_pools``/``pop_pools`` otherwise ``"off"``.
          Available values: "off", "geo", "random", "dynamic_latency", "proximity", "least_outstanding_requests", "least_connections", "".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#steering_policy LoadBalancer#steering_policy}
        '''
        result = self._values.get("steering_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''Time to live (TTL) of the DNS entry for the IP address returned by this load balancer.

        This only applies to gray-clouded (unproxied) load balancers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#ttl LoadBalancer#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerRulesOverrides(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverridesAdaptiveRouting",
    jsii_struct_bases=[],
    name_mapping={"failover_across_pools": "failoverAcrossPools"},
)
class LoadBalancerRulesOverridesAdaptiveRouting:
    def __init__(
        self,
        *,
        failover_across_pools: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param failover_across_pools: Extends zero-downtime failover of requests to healthy origins from alternate pools, when no healthy alternate exists in the same pool, according to the failover order defined by traffic and origin steering. When set false (the default) zero-downtime failover will only occur between origins within the same pool. See ``session_affinity_attributes`` for control over when sessions are broken or reassigned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#failover_across_pools LoadBalancer#failover_across_pools}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04e2e8cb8e4a79360b5de5e2325232e4c6100f6a32a2ab352bcb66c2d74ad625)
            check_type(argname="argument failover_across_pools", value=failover_across_pools, expected_type=type_hints["failover_across_pools"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if failover_across_pools is not None:
            self._values["failover_across_pools"] = failover_across_pools

    @builtins.property
    def failover_across_pools(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Extends zero-downtime failover of requests to healthy origins from alternate pools, when no healthy alternate exists in the same pool, according to the failover order defined by traffic and origin steering.

        When set false (the default) zero-downtime failover will only occur between origins within the same pool. See ``session_affinity_attributes`` for control over when sessions are broken or reassigned.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#failover_across_pools LoadBalancer#failover_across_pools}
        '''
        result = self._values.get("failover_across_pools")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerRulesOverridesAdaptiveRouting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerRulesOverridesAdaptiveRoutingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverridesAdaptiveRoutingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a7efd7e78658287b28e5ba6c9d99fd5f22803fb81fd0c9a750d67e5c32faa5f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFailoverAcrossPools")
    def reset_failover_across_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailoverAcrossPools", []))

    @builtins.property
    @jsii.member(jsii_name="failoverAcrossPoolsInput")
    def failover_across_pools_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "failoverAcrossPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="failoverAcrossPools")
    def failover_across_pools(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "failoverAcrossPools"))

    @failover_across_pools.setter
    def failover_across_pools(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba808bf362e4eba92256ff998ed3db7c2a9341a8469fb85e0563777f8442a0f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failoverAcrossPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesAdaptiveRouting]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesAdaptiveRouting]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesAdaptiveRouting]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eacd7002058763798e137aaa37b1041267fb13953033e1caaf6edee7a3356bc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverridesLocationStrategy",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "prefer_ecs": "preferEcs"},
)
class LoadBalancerRulesOverridesLocationStrategy:
    def __init__(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        prefer_ecs: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mode: Determines the authoritative location when ECS is not preferred, does not exist in the request, or its GeoIP lookup is unsuccessful. - ``"pop"``: Use the Cloudflare PoP location. - ``"resolver_ip"``: Use the DNS resolver GeoIP location. If the GeoIP lookup is unsuccessful, use the Cloudflare PoP location. Available values: "pop", "resolver_ip". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#mode LoadBalancer#mode}
        :param prefer_ecs: Whether the EDNS Client Subnet (ECS) GeoIP should be preferred as the authoritative location. - ``"always"``: Always prefer ECS. - ``"never"``: Never prefer ECS. - ``"proximity"``: Prefer ECS only when ``steering_policy="proximity"``. - ``"geo"``: Prefer ECS only when ``steering_policy="geo"``. Available values: "always", "never", "proximity", "geo". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#prefer_ecs LoadBalancer#prefer_ecs}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7071e21700e31fa074b8b5a8eaf06b619702a637def0209b2bdd1687d7355b4d)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument prefer_ecs", value=prefer_ecs, expected_type=type_hints["prefer_ecs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if prefer_ecs is not None:
            self._values["prefer_ecs"] = prefer_ecs

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Determines the authoritative location when ECS is not preferred, does not exist in the request, or its GeoIP lookup is unsuccessful.

        - ``"pop"``: Use the Cloudflare PoP location.
        - ``"resolver_ip"``: Use the DNS resolver GeoIP location. If the GeoIP lookup is unsuccessful, use the Cloudflare PoP location.
          Available values: "pop", "resolver_ip".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#mode LoadBalancer#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefer_ecs(self) -> typing.Optional[builtins.str]:
        '''Whether the EDNS Client Subnet (ECS) GeoIP should be preferred as the authoritative location.

        - ``"always"``: Always prefer ECS.
        - ``"never"``: Never prefer ECS.
        - ``"proximity"``: Prefer ECS only when ``steering_policy="proximity"``.
        - ``"geo"``: Prefer ECS only when ``steering_policy="geo"``.
          Available values: "always", "never", "proximity", "geo".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#prefer_ecs LoadBalancer#prefer_ecs}
        '''
        result = self._values.get("prefer_ecs")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerRulesOverridesLocationStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerRulesOverridesLocationStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverridesLocationStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__30a0b307a30466237be574a87cdd5702cd9422a2a7e41360c7c9d139a12a13e4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetPreferEcs")
    def reset_prefer_ecs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferEcs", []))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="preferEcsInput")
    def prefer_ecs_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferEcsInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f13fca12df2c10577502f0351db487d810d4b94dc8597c923a699d999c6fd7a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferEcs")
    def prefer_ecs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferEcs"))

    @prefer_ecs.setter
    def prefer_ecs(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7707eb1046a2a52ab76b39bfc611852997beee3f5cdb6c4daaa504f72a21bb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferEcs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesLocationStrategy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesLocationStrategy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesLocationStrategy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d41515753604db88b8a568c09f635d7871ab23948ab008963bb5bd6b91a07c93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadBalancerRulesOverridesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverridesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6e3db2746899b32772fe9f12603f7f273304443e2cde098ff2fb855c3740b76)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAdaptiveRouting")
    def put_adaptive_routing(
        self,
        *,
        failover_across_pools: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param failover_across_pools: Extends zero-downtime failover of requests to healthy origins from alternate pools, when no healthy alternate exists in the same pool, according to the failover order defined by traffic and origin steering. When set false (the default) zero-downtime failover will only occur between origins within the same pool. See ``session_affinity_attributes`` for control over when sessions are broken or reassigned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#failover_across_pools LoadBalancer#failover_across_pools}
        '''
        value = LoadBalancerRulesOverridesAdaptiveRouting(
            failover_across_pools=failover_across_pools
        )

        return typing.cast(None, jsii.invoke(self, "putAdaptiveRouting", [value]))

    @jsii.member(jsii_name="putLocationStrategy")
    def put_location_strategy(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        prefer_ecs: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mode: Determines the authoritative location when ECS is not preferred, does not exist in the request, or its GeoIP lookup is unsuccessful. - ``"pop"``: Use the Cloudflare PoP location. - ``"resolver_ip"``: Use the DNS resolver GeoIP location. If the GeoIP lookup is unsuccessful, use the Cloudflare PoP location. Available values: "pop", "resolver_ip". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#mode LoadBalancer#mode}
        :param prefer_ecs: Whether the EDNS Client Subnet (ECS) GeoIP should be preferred as the authoritative location. - ``"always"``: Always prefer ECS. - ``"never"``: Never prefer ECS. - ``"proximity"``: Prefer ECS only when ``steering_policy="proximity"``. - ``"geo"``: Prefer ECS only when ``steering_policy="geo"``. Available values: "always", "never", "proximity", "geo". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#prefer_ecs LoadBalancer#prefer_ecs}
        '''
        value = LoadBalancerRulesOverridesLocationStrategy(
            mode=mode, prefer_ecs=prefer_ecs
        )

        return typing.cast(None, jsii.invoke(self, "putLocationStrategy", [value]))

    @jsii.member(jsii_name="putRandomSteering")
    def put_random_steering(
        self,
        *,
        default_weight: typing.Optional[jsii.Number] = None,
        pool_weights: typing.Optional[typing.Mapping[builtins.str, jsii.Number]] = None,
    ) -> None:
        '''
        :param default_weight: The default weight for pools in the load balancer that are not specified in the pool_weights map. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_weight LoadBalancer#default_weight}
        :param pool_weights: A mapping of pool IDs to custom weights. The weight is relative to other pools in the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pool_weights LoadBalancer#pool_weights}
        '''
        value = LoadBalancerRulesOverridesRandomSteering(
            default_weight=default_weight, pool_weights=pool_weights
        )

        return typing.cast(None, jsii.invoke(self, "putRandomSteering", [value]))

    @jsii.member(jsii_name="putSessionAffinityAttributes")
    def put_session_affinity_attributes(
        self,
        *,
        drain_duration: typing.Optional[jsii.Number] = None,
        headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        require_all_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        samesite: typing.Optional[builtins.str] = None,
        secure: typing.Optional[builtins.str] = None,
        zero_downtime_failover: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param drain_duration: Configures the drain duration in seconds. This field is only used when session affinity is enabled on the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#drain_duration LoadBalancer#drain_duration}
        :param headers: Configures the names of HTTP headers to base session affinity on when header ``session_affinity`` is enabled. At least one HTTP header name must be provided. To specify the exact cookies to be used, include an item in the following format: ``"cookie:<cookie-name-1>,<cookie-name-2>"`` (example) where everything after the colon is a comma-separated list of cookie names. Providing only ``"cookie"`` will result in all cookies being used. The default max number of HTTP header names that can be provided depends on your plan: 5 for Enterprise, 1 for all other plans. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#headers LoadBalancer#headers}
        :param require_all_headers: When header ``session_affinity`` is enabled, this option can be used to specify how HTTP headers on load balancing requests will be used. The supported values are: - ``"true"``: Load balancing requests must contain *all* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. - ``"false"``: Load balancing requests must contain *at least one* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#require_all_headers LoadBalancer#require_all_headers}
        :param samesite: Configures the SameSite attribute on session affinity cookie. Value "Auto" will be translated to "Lax" or "None" depending if Always Use HTTPS is enabled. Note: when using value "None", the secure attribute can not be set to "Never". Available values: "Auto", "Lax", "None", "Strict". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#samesite LoadBalancer#samesite}
        :param secure: Configures the Secure attribute on session affinity cookie. Value "Always" indicates the Secure attribute will be set in the Set-Cookie header, "Never" indicates the Secure attribute will not be set, and "Auto" will set the Secure attribute depending if Always Use HTTPS is enabled. Available values: "Auto", "Always", "Never". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#secure LoadBalancer#secure}
        :param zero_downtime_failover: Configures the zero-downtime failover between origins within a pool when session affinity is enabled. This feature is currently incompatible with Argo, Tiered Cache, and Bandwidth Alliance. The supported values are: - ``"none"``: No failover takes place for sessions pinned to the origin (default). - ``"temporary"``: Traffic will be sent to another other healthy origin until the originally pinned origin is available; note that this can potentially result in heavy origin flapping. - ``"sticky"``: The session affinity cookie is updated and subsequent requests are sent to the new origin. Note: Zero-downtime failover with sticky sessions is currently not supported for session affinity by header. Available values: "none", "temporary", "sticky". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#zero_downtime_failover LoadBalancer#zero_downtime_failover}
        '''
        value = LoadBalancerRulesOverridesSessionAffinityAttributes(
            drain_duration=drain_duration,
            headers=headers,
            require_all_headers=require_all_headers,
            samesite=samesite,
            secure=secure,
            zero_downtime_failover=zero_downtime_failover,
        )

        return typing.cast(None, jsii.invoke(self, "putSessionAffinityAttributes", [value]))

    @jsii.member(jsii_name="resetAdaptiveRouting")
    def reset_adaptive_routing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdaptiveRouting", []))

    @jsii.member(jsii_name="resetCountryPools")
    def reset_country_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountryPools", []))

    @jsii.member(jsii_name="resetDefaultPools")
    def reset_default_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultPools", []))

    @jsii.member(jsii_name="resetFallbackPool")
    def reset_fallback_pool(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFallbackPool", []))

    @jsii.member(jsii_name="resetLocationStrategy")
    def reset_location_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocationStrategy", []))

    @jsii.member(jsii_name="resetPopPools")
    def reset_pop_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPopPools", []))

    @jsii.member(jsii_name="resetRandomSteering")
    def reset_random_steering(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRandomSteering", []))

    @jsii.member(jsii_name="resetRegionPools")
    def reset_region_pools(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionPools", []))

    @jsii.member(jsii_name="resetSessionAffinity")
    def reset_session_affinity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionAffinity", []))

    @jsii.member(jsii_name="resetSessionAffinityAttributes")
    def reset_session_affinity_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionAffinityAttributes", []))

    @jsii.member(jsii_name="resetSessionAffinityTtl")
    def reset_session_affinity_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionAffinityTtl", []))

    @jsii.member(jsii_name="resetSteeringPolicy")
    def reset_steering_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSteeringPolicy", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @builtins.property
    @jsii.member(jsii_name="adaptiveRouting")
    def adaptive_routing(
        self,
    ) -> LoadBalancerRulesOverridesAdaptiveRoutingOutputReference:
        return typing.cast(LoadBalancerRulesOverridesAdaptiveRoutingOutputReference, jsii.get(self, "adaptiveRouting"))

    @builtins.property
    @jsii.member(jsii_name="locationStrategy")
    def location_strategy(
        self,
    ) -> LoadBalancerRulesOverridesLocationStrategyOutputReference:
        return typing.cast(LoadBalancerRulesOverridesLocationStrategyOutputReference, jsii.get(self, "locationStrategy"))

    @builtins.property
    @jsii.member(jsii_name="randomSteering")
    def random_steering(
        self,
    ) -> "LoadBalancerRulesOverridesRandomSteeringOutputReference":
        return typing.cast("LoadBalancerRulesOverridesRandomSteeringOutputReference", jsii.get(self, "randomSteering"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityAttributes")
    def session_affinity_attributes(
        self,
    ) -> "LoadBalancerRulesOverridesSessionAffinityAttributesOutputReference":
        return typing.cast("LoadBalancerRulesOverridesSessionAffinityAttributesOutputReference", jsii.get(self, "sessionAffinityAttributes"))

    @builtins.property
    @jsii.member(jsii_name="adaptiveRoutingInput")
    def adaptive_routing_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesAdaptiveRouting]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesAdaptiveRouting]], jsii.get(self, "adaptiveRoutingInput"))

    @builtins.property
    @jsii.member(jsii_name="countryPoolsInput")
    def country_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "countryPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultPoolsInput")
    def default_pools_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "defaultPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="fallbackPoolInput")
    def fallback_pool_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fallbackPoolInput"))

    @builtins.property
    @jsii.member(jsii_name="locationStrategyInput")
    def location_strategy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesLocationStrategy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesLocationStrategy]], jsii.get(self, "locationStrategyInput"))

    @builtins.property
    @jsii.member(jsii_name="popPoolsInput")
    def pop_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "popPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="randomSteeringInput")
    def random_steering_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerRulesOverridesRandomSteering"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerRulesOverridesRandomSteering"]], jsii.get(self, "randomSteeringInput"))

    @builtins.property
    @jsii.member(jsii_name="regionPoolsInput")
    def region_pools_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]], jsii.get(self, "regionPoolsInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityAttributesInput")
    def session_affinity_attributes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerRulesOverridesSessionAffinityAttributes"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerRulesOverridesSessionAffinityAttributes"]], jsii.get(self, "sessionAffinityAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityInput")
    def session_affinity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionAffinityInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityTtlInput")
    def session_affinity_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sessionAffinityTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="steeringPolicyInput")
    def steering_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "steeringPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="countryPools")
    def country_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "countryPools"))

    @country_pools.setter
    def country_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdcd21a0a26ec91f0e8e0ed58155048f9dc3ffbfdca83f2897f9d9c769a4cdf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultPools")
    def default_pools(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "defaultPools"))

    @default_pools.setter
    def default_pools(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06b23a730bb6221ed135022ddefe56c86eb339adfcc39f52819954e7fa4ab46b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fallbackPool")
    def fallback_pool(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fallbackPool"))

    @fallback_pool.setter
    def fallback_pool(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87420889d83d51684a80a5b6b9732740355fca6a277bd0004154f57e679dfab0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallbackPool", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="popPools")
    def pop_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "popPools"))

    @pop_pools.setter
    def pop_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__035f2996b1a2670784f806d0a81a183d1836dacb81fca48d27692100a4ca338d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "popPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionPools")
    def region_pools(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]], jsii.get(self, "regionPools"))

    @region_pools.setter
    def region_pools(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db7a66cd64b9e6495d0e3097a77ece5a47c0cdc7bdbae6cea660a340286b888e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionPools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionAffinity")
    def session_affinity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionAffinity"))

    @session_affinity.setter
    def session_affinity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf2135424592a76b8f56aebfbdbd15a33640fb261375c502e64873fae4cbbb98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionAffinity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionAffinityTtl")
    def session_affinity_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sessionAffinityTtl"))

    @session_affinity_ttl.setter
    def session_affinity_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de7baa10ee941f7fac036d41647ca1bea605e34eae207a186012c3dd5e3d2142)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionAffinityTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="steeringPolicy")
    def steering_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "steeringPolicy"))

    @steering_policy.setter
    def steering_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4aac55686332dc3a0f2cab81ca46ae265a196d9b495e788347670f4b34d5bcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "steeringPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ba5df896ef2aab0c87f8466c80dd544574233b28e071a41e00576be3ecf36fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverrides]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverrides]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverrides]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__978d57080a6f56d402e0e02c1bfbe681c0f68e6a9a73c1cf5ab8401ed2f86167)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverridesRandomSteering",
    jsii_struct_bases=[],
    name_mapping={"default_weight": "defaultWeight", "pool_weights": "poolWeights"},
)
class LoadBalancerRulesOverridesRandomSteering:
    def __init__(
        self,
        *,
        default_weight: typing.Optional[jsii.Number] = None,
        pool_weights: typing.Optional[typing.Mapping[builtins.str, jsii.Number]] = None,
    ) -> None:
        '''
        :param default_weight: The default weight for pools in the load balancer that are not specified in the pool_weights map. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_weight LoadBalancer#default_weight}
        :param pool_weights: A mapping of pool IDs to custom weights. The weight is relative to other pools in the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pool_weights LoadBalancer#pool_weights}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__814c297157044678c5e2ceeefc86eb0d85f8b545d8d3ebf40f27a00b57851fa8)
            check_type(argname="argument default_weight", value=default_weight, expected_type=type_hints["default_weight"])
            check_type(argname="argument pool_weights", value=pool_weights, expected_type=type_hints["pool_weights"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if default_weight is not None:
            self._values["default_weight"] = default_weight
        if pool_weights is not None:
            self._values["pool_weights"] = pool_weights

    @builtins.property
    def default_weight(self) -> typing.Optional[jsii.Number]:
        '''The default weight for pools in the load balancer that are not specified in the pool_weights map.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#default_weight LoadBalancer#default_weight}
        '''
        result = self._values.get("default_weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pool_weights(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, jsii.Number]]:
        '''A mapping of pool IDs to custom weights. The weight is relative to other pools in the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#pool_weights LoadBalancer#pool_weights}
        '''
        result = self._values.get("pool_weights")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerRulesOverridesRandomSteering(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerRulesOverridesRandomSteeringOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverridesRandomSteeringOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5b2d542c2795328bfc394989129f5dbfdca043e9a83038e624a9420b89d61ce)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDefaultWeight")
    def reset_default_weight(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultWeight", []))

    @jsii.member(jsii_name="resetPoolWeights")
    def reset_pool_weights(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPoolWeights", []))

    @builtins.property
    @jsii.member(jsii_name="defaultWeightInput")
    def default_weight_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultWeightInput"))

    @builtins.property
    @jsii.member(jsii_name="poolWeightsInput")
    def pool_weights_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, jsii.Number]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, jsii.Number]], jsii.get(self, "poolWeightsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultWeight")
    def default_weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultWeight"))

    @default_weight.setter
    def default_weight(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__976e1879118b3b9cb7164040c9c8c6689e1fb358b87d54fe6ca924b8acbba5d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultWeight", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="poolWeights")
    def pool_weights(self) -> typing.Mapping[builtins.str, jsii.Number]:
        return typing.cast(typing.Mapping[builtins.str, jsii.Number], jsii.get(self, "poolWeights"))

    @pool_weights.setter
    def pool_weights(self, value: typing.Mapping[builtins.str, jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abdee6acee4f1ad305fe73df9fed1e5c23781c31a2fb93c4affefd6f908beabf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "poolWeights", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesRandomSteering]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesRandomSteering]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesRandomSteering]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eddaf802316fdf31096e07403abb5527856dd04d08509e317383300813b7b023)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverridesSessionAffinityAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "drain_duration": "drainDuration",
        "headers": "headers",
        "require_all_headers": "requireAllHeaders",
        "samesite": "samesite",
        "secure": "secure",
        "zero_downtime_failover": "zeroDowntimeFailover",
    },
)
class LoadBalancerRulesOverridesSessionAffinityAttributes:
    def __init__(
        self,
        *,
        drain_duration: typing.Optional[jsii.Number] = None,
        headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        require_all_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        samesite: typing.Optional[builtins.str] = None,
        secure: typing.Optional[builtins.str] = None,
        zero_downtime_failover: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param drain_duration: Configures the drain duration in seconds. This field is only used when session affinity is enabled on the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#drain_duration LoadBalancer#drain_duration}
        :param headers: Configures the names of HTTP headers to base session affinity on when header ``session_affinity`` is enabled. At least one HTTP header name must be provided. To specify the exact cookies to be used, include an item in the following format: ``"cookie:<cookie-name-1>,<cookie-name-2>"`` (example) where everything after the colon is a comma-separated list of cookie names. Providing only ``"cookie"`` will result in all cookies being used. The default max number of HTTP header names that can be provided depends on your plan: 5 for Enterprise, 1 for all other plans. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#headers LoadBalancer#headers}
        :param require_all_headers: When header ``session_affinity`` is enabled, this option can be used to specify how HTTP headers on load balancing requests will be used. The supported values are: - ``"true"``: Load balancing requests must contain *all* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. - ``"false"``: Load balancing requests must contain *at least one* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#require_all_headers LoadBalancer#require_all_headers}
        :param samesite: Configures the SameSite attribute on session affinity cookie. Value "Auto" will be translated to "Lax" or "None" depending if Always Use HTTPS is enabled. Note: when using value "None", the secure attribute can not be set to "Never". Available values: "Auto", "Lax", "None", "Strict". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#samesite LoadBalancer#samesite}
        :param secure: Configures the Secure attribute on session affinity cookie. Value "Always" indicates the Secure attribute will be set in the Set-Cookie header, "Never" indicates the Secure attribute will not be set, and "Auto" will set the Secure attribute depending if Always Use HTTPS is enabled. Available values: "Auto", "Always", "Never". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#secure LoadBalancer#secure}
        :param zero_downtime_failover: Configures the zero-downtime failover between origins within a pool when session affinity is enabled. This feature is currently incompatible with Argo, Tiered Cache, and Bandwidth Alliance. The supported values are: - ``"none"``: No failover takes place for sessions pinned to the origin (default). - ``"temporary"``: Traffic will be sent to another other healthy origin until the originally pinned origin is available; note that this can potentially result in heavy origin flapping. - ``"sticky"``: The session affinity cookie is updated and subsequent requests are sent to the new origin. Note: Zero-downtime failover with sticky sessions is currently not supported for session affinity by header. Available values: "none", "temporary", "sticky". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#zero_downtime_failover LoadBalancer#zero_downtime_failover}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__212cea52e61ad9e0d84095358ac0976bb725aae5de5c796154a817496e2d4cf4)
            check_type(argname="argument drain_duration", value=drain_duration, expected_type=type_hints["drain_duration"])
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument require_all_headers", value=require_all_headers, expected_type=type_hints["require_all_headers"])
            check_type(argname="argument samesite", value=samesite, expected_type=type_hints["samesite"])
            check_type(argname="argument secure", value=secure, expected_type=type_hints["secure"])
            check_type(argname="argument zero_downtime_failover", value=zero_downtime_failover, expected_type=type_hints["zero_downtime_failover"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if drain_duration is not None:
            self._values["drain_duration"] = drain_duration
        if headers is not None:
            self._values["headers"] = headers
        if require_all_headers is not None:
            self._values["require_all_headers"] = require_all_headers
        if samesite is not None:
            self._values["samesite"] = samesite
        if secure is not None:
            self._values["secure"] = secure
        if zero_downtime_failover is not None:
            self._values["zero_downtime_failover"] = zero_downtime_failover

    @builtins.property
    def drain_duration(self) -> typing.Optional[jsii.Number]:
        '''Configures the drain duration in seconds.

        This field is only used when session affinity is enabled on the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#drain_duration LoadBalancer#drain_duration}
        '''
        result = self._values.get("drain_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Configures the names of HTTP headers to base session affinity on when header ``session_affinity`` is enabled.

        At least one HTTP header name must be provided. To specify the exact cookies to be used, include an item in the following format: ``"cookie:<cookie-name-1>,<cookie-name-2>"`` (example) where everything after the colon is a comma-separated list of cookie names. Providing only ``"cookie"`` will result in all cookies being used. The default max number of HTTP header names that can be provided depends on your plan: 5 for Enterprise, 1 for all other plans.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#headers LoadBalancer#headers}
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def require_all_headers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When header ``session_affinity`` is enabled, this option can be used to specify how HTTP headers on load balancing requests will be used.

        The supported values are: - ``"true"``: Load balancing requests must contain *all* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. - ``"false"``: Load balancing requests must contain *at least one* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#require_all_headers LoadBalancer#require_all_headers}
        '''
        result = self._values.get("require_all_headers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def samesite(self) -> typing.Optional[builtins.str]:
        '''Configures the SameSite attribute on session affinity cookie.

        Value "Auto" will be translated to "Lax" or "None" depending if Always Use HTTPS is enabled. Note: when using value "None", the secure attribute can not be set to "Never".
        Available values: "Auto", "Lax", "None", "Strict".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#samesite LoadBalancer#samesite}
        '''
        result = self._values.get("samesite")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure(self) -> typing.Optional[builtins.str]:
        '''Configures the Secure attribute on session affinity cookie.

        Value "Always" indicates the Secure attribute will be set in the Set-Cookie header, "Never" indicates the Secure attribute will not be set, and "Auto" will set the Secure attribute depending if Always Use HTTPS is enabled.
        Available values: "Auto", "Always", "Never".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#secure LoadBalancer#secure}
        '''
        result = self._values.get("secure")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zero_downtime_failover(self) -> typing.Optional[builtins.str]:
        '''Configures the zero-downtime failover between origins within a pool when session affinity is enabled.

        This feature is currently incompatible with Argo, Tiered Cache, and Bandwidth Alliance. The supported values are: - ``"none"``: No failover takes place for sessions pinned to the origin (default). - ``"temporary"``: Traffic will be sent to another other healthy origin until the originally pinned origin is available; note that this can potentially result in heavy origin flapping. - ``"sticky"``: The session affinity cookie is updated and subsequent requests are sent to the new origin. Note: Zero-downtime failover with sticky sessions is currently not supported for session affinity by header.
        Available values: "none", "temporary", "sticky".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#zero_downtime_failover LoadBalancer#zero_downtime_failover}
        '''
        result = self._values.get("zero_downtime_failover")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerRulesOverridesSessionAffinityAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerRulesOverridesSessionAffinityAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerRulesOverridesSessionAffinityAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a83ec0764af83719b0db1bbb49dee56a2d5268d80cf54458649c83037e68ff3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDrainDuration")
    def reset_drain_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainDuration", []))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @jsii.member(jsii_name="resetRequireAllHeaders")
    def reset_require_all_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireAllHeaders", []))

    @jsii.member(jsii_name="resetSamesite")
    def reset_samesite(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamesite", []))

    @jsii.member(jsii_name="resetSecure")
    def reset_secure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecure", []))

    @jsii.member(jsii_name="resetZeroDowntimeFailover")
    def reset_zero_downtime_failover(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZeroDowntimeFailover", []))

    @builtins.property
    @jsii.member(jsii_name="drainDurationInput")
    def drain_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="headersInput")
    def headers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "headersInput"))

    @builtins.property
    @jsii.member(jsii_name="requireAllHeadersInput")
    def require_all_headers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requireAllHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="samesiteInput")
    def samesite_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "samesiteInput"))

    @builtins.property
    @jsii.member(jsii_name="secureInput")
    def secure_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureInput"))

    @builtins.property
    @jsii.member(jsii_name="zeroDowntimeFailoverInput")
    def zero_downtime_failover_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zeroDowntimeFailoverInput"))

    @builtins.property
    @jsii.member(jsii_name="drainDuration")
    def drain_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainDuration"))

    @drain_duration.setter
    def drain_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8df774c5ab6cdc17915467d260b7141b3316f7dcde59e450c6545c821b0400d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45ea8046777719d6fd6f2028f6595415295d638c9ec6cfe9000725027efbb1de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requireAllHeaders")
    def require_all_headers(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "requireAllHeaders"))

    @require_all_headers.setter
    def require_all_headers(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fedd1e5746747530523484f1e4e85ac7db54886ac13b9d83d153e00ce16782a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireAllHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="samesite")
    def samesite(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samesite"))

    @samesite.setter
    def samesite(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38f27b6e0216a6d9a5700548b0527d3d55525db02714af5d1766b69234d33832)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samesite", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secure")
    def secure(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secure"))

    @secure.setter
    def secure(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a13569d07983e16bdfe0f077fbb0dea59e0ea80c3939ed063162aa491a32457)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zeroDowntimeFailover")
    def zero_downtime_failover(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zeroDowntimeFailover"))

    @zero_downtime_failover.setter
    def zero_downtime_failover(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9316bf4dd7ccbb813f02707b4489c845d6b8d3502347be3db440dd168cbb3db5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zeroDowntimeFailover", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesSessionAffinityAttributes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesSessionAffinityAttributes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesSessionAffinityAttributes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cddde1ce5b15a67558e5cc4750144d42d7846d714bec1f90c5166eaf8de29fc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerSessionAffinityAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "drain_duration": "drainDuration",
        "headers": "headers",
        "require_all_headers": "requireAllHeaders",
        "samesite": "samesite",
        "secure": "secure",
        "zero_downtime_failover": "zeroDowntimeFailover",
    },
)
class LoadBalancerSessionAffinityAttributes:
    def __init__(
        self,
        *,
        drain_duration: typing.Optional[jsii.Number] = None,
        headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        require_all_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        samesite: typing.Optional[builtins.str] = None,
        secure: typing.Optional[builtins.str] = None,
        zero_downtime_failover: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param drain_duration: Configures the drain duration in seconds. This field is only used when session affinity is enabled on the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#drain_duration LoadBalancer#drain_duration}
        :param headers: Configures the names of HTTP headers to base session affinity on when header ``session_affinity`` is enabled. At least one HTTP header name must be provided. To specify the exact cookies to be used, include an item in the following format: ``"cookie:<cookie-name-1>,<cookie-name-2>"`` (example) where everything after the colon is a comma-separated list of cookie names. Providing only ``"cookie"`` will result in all cookies being used. The default max number of HTTP header names that can be provided depends on your plan: 5 for Enterprise, 1 for all other plans. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#headers LoadBalancer#headers}
        :param require_all_headers: When header ``session_affinity`` is enabled, this option can be used to specify how HTTP headers on load balancing requests will be used. The supported values are: - ``"true"``: Load balancing requests must contain *all* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. - ``"false"``: Load balancing requests must contain *at least one* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#require_all_headers LoadBalancer#require_all_headers}
        :param samesite: Configures the SameSite attribute on session affinity cookie. Value "Auto" will be translated to "Lax" or "None" depending if Always Use HTTPS is enabled. Note: when using value "None", the secure attribute can not be set to "Never". Available values: "Auto", "Lax", "None", "Strict". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#samesite LoadBalancer#samesite}
        :param secure: Configures the Secure attribute on session affinity cookie. Value "Always" indicates the Secure attribute will be set in the Set-Cookie header, "Never" indicates the Secure attribute will not be set, and "Auto" will set the Secure attribute depending if Always Use HTTPS is enabled. Available values: "Auto", "Always", "Never". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#secure LoadBalancer#secure}
        :param zero_downtime_failover: Configures the zero-downtime failover between origins within a pool when session affinity is enabled. This feature is currently incompatible with Argo, Tiered Cache, and Bandwidth Alliance. The supported values are: - ``"none"``: No failover takes place for sessions pinned to the origin (default). - ``"temporary"``: Traffic will be sent to another other healthy origin until the originally pinned origin is available; note that this can potentially result in heavy origin flapping. - ``"sticky"``: The session affinity cookie is updated and subsequent requests are sent to the new origin. Note: Zero-downtime failover with sticky sessions is currently not supported for session affinity by header. Available values: "none", "temporary", "sticky". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#zero_downtime_failover LoadBalancer#zero_downtime_failover}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__403f65be5844ed82ef2acb3e7a6d5fa371512a5ae5cc8925ecfed7a28c819c81)
            check_type(argname="argument drain_duration", value=drain_duration, expected_type=type_hints["drain_duration"])
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument require_all_headers", value=require_all_headers, expected_type=type_hints["require_all_headers"])
            check_type(argname="argument samesite", value=samesite, expected_type=type_hints["samesite"])
            check_type(argname="argument secure", value=secure, expected_type=type_hints["secure"])
            check_type(argname="argument zero_downtime_failover", value=zero_downtime_failover, expected_type=type_hints["zero_downtime_failover"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if drain_duration is not None:
            self._values["drain_duration"] = drain_duration
        if headers is not None:
            self._values["headers"] = headers
        if require_all_headers is not None:
            self._values["require_all_headers"] = require_all_headers
        if samesite is not None:
            self._values["samesite"] = samesite
        if secure is not None:
            self._values["secure"] = secure
        if zero_downtime_failover is not None:
            self._values["zero_downtime_failover"] = zero_downtime_failover

    @builtins.property
    def drain_duration(self) -> typing.Optional[jsii.Number]:
        '''Configures the drain duration in seconds.

        This field is only used when session affinity is enabled on the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#drain_duration LoadBalancer#drain_duration}
        '''
        result = self._values.get("drain_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Configures the names of HTTP headers to base session affinity on when header ``session_affinity`` is enabled.

        At least one HTTP header name must be provided. To specify the exact cookies to be used, include an item in the following format: ``"cookie:<cookie-name-1>,<cookie-name-2>"`` (example) where everything after the colon is a comma-separated list of cookie names. Providing only ``"cookie"`` will result in all cookies being used. The default max number of HTTP header names that can be provided depends on your plan: 5 for Enterprise, 1 for all other plans.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#headers LoadBalancer#headers}
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def require_all_headers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When header ``session_affinity`` is enabled, this option can be used to specify how HTTP headers on load balancing requests will be used.

        The supported values are: - ``"true"``: Load balancing requests must contain *all* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created. - ``"false"``: Load balancing requests must contain *at least one* of the HTTP headers specified by the ``headers`` session affinity attribute, otherwise sessions aren't created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#require_all_headers LoadBalancer#require_all_headers}
        '''
        result = self._values.get("require_all_headers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def samesite(self) -> typing.Optional[builtins.str]:
        '''Configures the SameSite attribute on session affinity cookie.

        Value "Auto" will be translated to "Lax" or "None" depending if Always Use HTTPS is enabled. Note: when using value "None", the secure attribute can not be set to "Never".
        Available values: "Auto", "Lax", "None", "Strict".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#samesite LoadBalancer#samesite}
        '''
        result = self._values.get("samesite")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure(self) -> typing.Optional[builtins.str]:
        '''Configures the Secure attribute on session affinity cookie.

        Value "Always" indicates the Secure attribute will be set in the Set-Cookie header, "Never" indicates the Secure attribute will not be set, and "Auto" will set the Secure attribute depending if Always Use HTTPS is enabled.
        Available values: "Auto", "Always", "Never".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#secure LoadBalancer#secure}
        '''
        result = self._values.get("secure")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zero_downtime_failover(self) -> typing.Optional[builtins.str]:
        '''Configures the zero-downtime failover between origins within a pool when session affinity is enabled.

        This feature is currently incompatible with Argo, Tiered Cache, and Bandwidth Alliance. The supported values are: - ``"none"``: No failover takes place for sessions pinned to the origin (default). - ``"temporary"``: Traffic will be sent to another other healthy origin until the originally pinned origin is available; note that this can potentially result in heavy origin flapping. - ``"sticky"``: The session affinity cookie is updated and subsequent requests are sent to the new origin. Note: Zero-downtime failover with sticky sessions is currently not supported for session affinity by header.
        Available values: "none", "temporary", "sticky".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer#zero_downtime_failover LoadBalancer#zero_downtime_failover}
        '''
        result = self._values.get("zero_downtime_failover")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerSessionAffinityAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerSessionAffinityAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancer.LoadBalancerSessionAffinityAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ea7a957e0edd8d304605cb4403473de01064cca85eb0e09931670911def1cbc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDrainDuration")
    def reset_drain_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainDuration", []))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @jsii.member(jsii_name="resetRequireAllHeaders")
    def reset_require_all_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireAllHeaders", []))

    @jsii.member(jsii_name="resetSamesite")
    def reset_samesite(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamesite", []))

    @jsii.member(jsii_name="resetSecure")
    def reset_secure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecure", []))

    @jsii.member(jsii_name="resetZeroDowntimeFailover")
    def reset_zero_downtime_failover(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZeroDowntimeFailover", []))

    @builtins.property
    @jsii.member(jsii_name="drainDurationInput")
    def drain_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="headersInput")
    def headers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "headersInput"))

    @builtins.property
    @jsii.member(jsii_name="requireAllHeadersInput")
    def require_all_headers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requireAllHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="samesiteInput")
    def samesite_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "samesiteInput"))

    @builtins.property
    @jsii.member(jsii_name="secureInput")
    def secure_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureInput"))

    @builtins.property
    @jsii.member(jsii_name="zeroDowntimeFailoverInput")
    def zero_downtime_failover_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zeroDowntimeFailoverInput"))

    @builtins.property
    @jsii.member(jsii_name="drainDuration")
    def drain_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainDuration"))

    @drain_duration.setter
    def drain_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77eda3569a69ee49399d900cb7ce1042765598cca9379bdbeff97071f9a52f3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a4b9e644a2227466c84d8f14c46794815d2ef354a463b535342f4dc006e6824)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requireAllHeaders")
    def require_all_headers(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "requireAllHeaders"))

    @require_all_headers.setter
    def require_all_headers(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e5cd4f8a15465ca15488c527bb19834e9b57c5df959f8ee725901b051d95bcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireAllHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="samesite")
    def samesite(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samesite"))

    @samesite.setter
    def samesite(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eb428f1c01da5d8f8fae1299dfccd66e1f8f402d195782a79328ced1b712598)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samesite", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secure")
    def secure(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secure"))

    @secure.setter
    def secure(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07ceba26ecc59b5392f1e2d0eef2dc5838dcb0050d14feff0099c1374cfa9fa6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zeroDowntimeFailover")
    def zero_downtime_failover(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zeroDowntimeFailover"))

    @zero_downtime_failover.setter
    def zero_downtime_failover(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17459ec5207fe5828cef08a782e123e0f1187b543d7b8283e4982ce692f66ccd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zeroDowntimeFailover", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerSessionAffinityAttributes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerSessionAffinityAttributes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerSessionAffinityAttributes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08a3129d21e85210d72757defb5853cdc413e7e551a7fdf077d5776eeedb81db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "LoadBalancer",
    "LoadBalancerAdaptiveRouting",
    "LoadBalancerAdaptiveRoutingOutputReference",
    "LoadBalancerConfig",
    "LoadBalancerLocationStrategy",
    "LoadBalancerLocationStrategyOutputReference",
    "LoadBalancerRandomSteering",
    "LoadBalancerRandomSteeringOutputReference",
    "LoadBalancerRules",
    "LoadBalancerRulesFixedResponse",
    "LoadBalancerRulesFixedResponseOutputReference",
    "LoadBalancerRulesList",
    "LoadBalancerRulesOutputReference",
    "LoadBalancerRulesOverrides",
    "LoadBalancerRulesOverridesAdaptiveRouting",
    "LoadBalancerRulesOverridesAdaptiveRoutingOutputReference",
    "LoadBalancerRulesOverridesLocationStrategy",
    "LoadBalancerRulesOverridesLocationStrategyOutputReference",
    "LoadBalancerRulesOverridesOutputReference",
    "LoadBalancerRulesOverridesRandomSteering",
    "LoadBalancerRulesOverridesRandomSteeringOutputReference",
    "LoadBalancerRulesOverridesSessionAffinityAttributes",
    "LoadBalancerRulesOverridesSessionAffinityAttributesOutputReference",
    "LoadBalancerSessionAffinityAttributes",
    "LoadBalancerSessionAffinityAttributesOutputReference",
]

publication.publish()

def _typecheckingstub__0015049507828df93e92dfe6c1bca8e51a3ffecfec278ed1f472e11b1c5ed18f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    default_pools: typing.Sequence[builtins.str],
    fallback_pool: builtins.str,
    name: builtins.str,
    zone_id: builtins.str,
    adaptive_routing: typing.Optional[typing.Union[LoadBalancerAdaptiveRouting, typing.Dict[builtins.str, typing.Any]]] = None,
    country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    location_strategy: typing.Optional[typing.Union[LoadBalancerLocationStrategy, typing.Dict[builtins.str, typing.Any]]] = None,
    networks: typing.Optional[typing.Sequence[builtins.str]] = None,
    pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    random_steering: typing.Optional[typing.Union[LoadBalancerRandomSteering, typing.Dict[builtins.str, typing.Any]]] = None,
    region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadBalancerRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    session_affinity: typing.Optional[builtins.str] = None,
    session_affinity_attributes: typing.Optional[typing.Union[LoadBalancerSessionAffinityAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    session_affinity_ttl: typing.Optional[jsii.Number] = None,
    steering_policy: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__b042f6d1d03c54f4854ecae07c5c93a2cc8e8f808d873ddcaf6b7961345a6554(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__713bf22a49b1560498a800316f840069503b2323554a05dc728d48b4c9dca764(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadBalancerRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a5ade0a0a29ac9271b21ba639ddda8beae0b01fd7d163371f75847397c48669(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dd3c521e6f1c952de609d8259bea28eb62676dddbfd5dc0939f75a2980e421f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__749c6dd92b9de55f6f692a104109a7a8c0140668d57a671f2f4096578fa936a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83c6dec4fe321e227c8d9680880282305431f4dba6c380b6d1257f0b33508764(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e367360d0eb0a6e0af31ad6ea22ccbacd3116a3a31c0f7fe37b0c0856bbde90c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__549a6fc7dd52b05e493a75e851006eb3ff4b1b5be4e31f42a3e0fba8a3e7992c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8b3a62b3a4ae7b0e56cd604e01c17dfd1006a3608eb3327aabac26d319ab590(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f4ee4593aefbaaf723108ef8a0742472ab2f8fc5971c47b5806c44843ca8a6f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e098d3c0597e3524b55c3627f9a3bb7992a85e831d4f688b06dfff6966b3988(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e7bbeeed712104f7d319eb93d1399f8b375a07f5b5985db6265286cd664c8bd(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0750582d833b47b92d0f19d520eb3c3efdee362ea8a4097af61978e00dce967a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce0cd47fb3f2073bbd91e71dcb6d52e072ba67430ce8b3bd46319e7ae25f9afd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f38cc45e4ba523e71f68dc6122fbd27e2295e3f03fc8776d0f26210fe4925bd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80fcc62043aca63d073f33eb1730d5f1b0708a90f7fa61ae55fbbe0cebee22ce(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21bb86cc37c1ec4ce7603426eab2a13a53a3024685a2262c80dcf7351190a31b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__303c8d660d7ff911b7607b1ed365324cf95aef52ab574f4228534f17fbfe1953(
    *,
    failover_across_pools: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d41d79f69f4c4baa892cc9881ebe8a3b44e49a9e164ded9e679d66e3b05302c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__483f29751055bdcab9b5325a954524c06820b6aca2f5bdcef6272c6c5e8f633d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4657374ad9caf633eb09b1d65ba4e5b4f17d06e0b28714a28b13cdc210bd62a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerAdaptiveRouting]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__179a274ba88b1187743571bdcd7d729435f5abbf8faf21f1b93231a9af798a1f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    default_pools: typing.Sequence[builtins.str],
    fallback_pool: builtins.str,
    name: builtins.str,
    zone_id: builtins.str,
    adaptive_routing: typing.Optional[typing.Union[LoadBalancerAdaptiveRouting, typing.Dict[builtins.str, typing.Any]]] = None,
    country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    location_strategy: typing.Optional[typing.Union[LoadBalancerLocationStrategy, typing.Dict[builtins.str, typing.Any]]] = None,
    networks: typing.Optional[typing.Sequence[builtins.str]] = None,
    pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    proxied: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    random_steering: typing.Optional[typing.Union[LoadBalancerRandomSteering, typing.Dict[builtins.str, typing.Any]]] = None,
    region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadBalancerRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    session_affinity: typing.Optional[builtins.str] = None,
    session_affinity_attributes: typing.Optional[typing.Union[LoadBalancerSessionAffinityAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    session_affinity_ttl: typing.Optional[jsii.Number] = None,
    steering_policy: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d0457eea690b702cd82d00d1d62a0d5a8fe1280f78f5baff5cd4e5a844b3b2(
    *,
    mode: typing.Optional[builtins.str] = None,
    prefer_ecs: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e81b5884646eb683c1088e82b1ba373165f971f9550ab7a9950624c0fa774f6f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__283834d4efe18f2ecca14babcc0cff3cc686560412d787bb702fb0f888ee83e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e7502d6738609e16ad083c65590cb0aae8820f91260ffc08dc679caa3a79d05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__154dac22f09bd45bd574fb93d3a050a49415bdd268301d55ed3771479657a7a2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerLocationStrategy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee03b4afc82f161efabb876910cdab21e26982c73d8eef161bdf1806f028519b(
    *,
    default_weight: typing.Optional[jsii.Number] = None,
    pool_weights: typing.Optional[typing.Mapping[builtins.str, jsii.Number]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eff3856a00584fdf493670649b9ffda272af232d2ba2774e2a2317ee7892ea4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64146deae2c3ed36b3305117fa981b5b7c9a1164677f036cb508f162493c0086(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9973a0c91cce2364e7bca20eead582d2bb02780a7f8a4182cefbd38c49d0b90(
    value: typing.Mapping[builtins.str, jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aecaf7995fee6243343cf4dfffae58904bdf43c75cc42227c30cfacfa4083ed8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRandomSteering]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fdf42061a6652ffd6986a8e2ec9edad4427316f2d7a2321fe44f8214e666716(
    *,
    condition: typing.Optional[builtins.str] = None,
    disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fixed_response: typing.Optional[typing.Union[LoadBalancerRulesFixedResponse, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    overrides: typing.Optional[typing.Union[LoadBalancerRulesOverrides, typing.Dict[builtins.str, typing.Any]]] = None,
    priority: typing.Optional[jsii.Number] = None,
    terminates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e06a358aa30363c798305232d6e623350e1f1c44109315e688dbf167c0529967(
    *,
    content_type: typing.Optional[builtins.str] = None,
    location: typing.Optional[builtins.str] = None,
    message_body: typing.Optional[builtins.str] = None,
    status_code: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80108d9aa8c23f36e4b7063ba0aa4b31c3e1275949022514800f4c8eb0d14916(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86270d9848d23db8e4200b0e35ebc9fc45e5da1d517d6a31bc7780f890383a91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87b015c6e42a266873f9a700c8a31631697378013d1c81a51f6dee7696471a23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69434f811e173e46da313f9aedd1026400d0a3b9a0174f3f0300bfbc6774e9f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cf77b24367c791875e918c3a9cedf3f2147f45e4dacbb0aeb750962fad39bd1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1307772712904f3a25b1d8ff5167a3a18cacea694ac2ce73bd9c48607726e4a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesFixedResponse]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59baa239d8e3ea247aac1525b719e2de365c0547c13a6e6738e91104b679e18f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dd5d663b462645948272bde24a3e6a192a833e4d72fadcfbe9d26e8affa9a19(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddd04c38c24c581759071ae44418fc173fd284b9cd0edbbd2f85e435c9c1c578(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__521357c4039603ba4551315908639be87cc4d2d45ba7c9ab2982e88e9e19fe09(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3db24e37e9660436ce55e2591e403ae318662c1893aea722586425995eeb689f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2aab7db6cb77dc7546b011c288f299e644f90b4e6681a5fadb150655069bd9f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadBalancerRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb822e0195a87da51205f90f18bdae2e8a011b0c0b8be0a23f2767a53a54c34(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc94eb429048c5fdcba032f9097bff452e96a8b87a21ed14207910ff9ebd8e56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__970524bed5e99690908d85d4d7ac78a7ba44a085d24880cb72687193e0e9bc09(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7098ca56037e693d628373e3a6f18993274641304d612d1ad77069af9d82e1ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec3294de3d4a5c794f3bceef16b338e69245d8e1474e2ca04d3e6c6914850bd6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66223bd8cfe2d18c3c9439fce67488c94926fc3e7f8f4f9a245979aa2a5bdce8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2be777163ff6c1b6b7d0e9fbbc7f8a8d9c7d76e6976ca4eeac1712b453685526(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75f9ec836d04efd6df32310c87de2c9677c1832a61280179f4a5f5628a3a2bdc(
    *,
    adaptive_routing: typing.Optional[typing.Union[LoadBalancerRulesOverridesAdaptiveRouting, typing.Dict[builtins.str, typing.Any]]] = None,
    country_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    default_pools: typing.Optional[typing.Sequence[builtins.str]] = None,
    fallback_pool: typing.Optional[builtins.str] = None,
    location_strategy: typing.Optional[typing.Union[LoadBalancerRulesOverridesLocationStrategy, typing.Dict[builtins.str, typing.Any]]] = None,
    pop_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    random_steering: typing.Optional[typing.Union[LoadBalancerRulesOverridesRandomSteering, typing.Dict[builtins.str, typing.Any]]] = None,
    region_pools: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Sequence[builtins.str]]]] = None,
    session_affinity: typing.Optional[builtins.str] = None,
    session_affinity_attributes: typing.Optional[typing.Union[LoadBalancerRulesOverridesSessionAffinityAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    session_affinity_ttl: typing.Optional[jsii.Number] = None,
    steering_policy: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04e2e8cb8e4a79360b5de5e2325232e4c6100f6a32a2ab352bcb66c2d74ad625(
    *,
    failover_across_pools: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a7efd7e78658287b28e5ba6c9d99fd5f22803fb81fd0c9a750d67e5c32faa5f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba808bf362e4eba92256ff998ed3db7c2a9341a8469fb85e0563777f8442a0f5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eacd7002058763798e137aaa37b1041267fb13953033e1caaf6edee7a3356bc0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesAdaptiveRouting]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7071e21700e31fa074b8b5a8eaf06b619702a637def0209b2bdd1687d7355b4d(
    *,
    mode: typing.Optional[builtins.str] = None,
    prefer_ecs: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30a0b307a30466237be574a87cdd5702cd9422a2a7e41360c7c9d139a12a13e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f13fca12df2c10577502f0351db487d810d4b94dc8597c923a699d999c6fd7a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7707eb1046a2a52ab76b39bfc611852997beee3f5cdb6c4daaa504f72a21bb3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d41515753604db88b8a568c09f635d7871ab23948ab008963bb5bd6b91a07c93(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesLocationStrategy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6e3db2746899b32772fe9f12603f7f273304443e2cde098ff2fb855c3740b76(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdcd21a0a26ec91f0e8e0ed58155048f9dc3ffbfdca83f2897f9d9c769a4cdf2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06b23a730bb6221ed135022ddefe56c86eb339adfcc39f52819954e7fa4ab46b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87420889d83d51684a80a5b6b9732740355fca6a277bd0004154f57e679dfab0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__035f2996b1a2670784f806d0a81a183d1836dacb81fca48d27692100a4ca338d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db7a66cd64b9e6495d0e3097a77ece5a47c0cdc7bdbae6cea660a340286b888e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.List[builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2135424592a76b8f56aebfbdbd15a33640fb261375c502e64873fae4cbbb98(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de7baa10ee941f7fac036d41647ca1bea605e34eae207a186012c3dd5e3d2142(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4aac55686332dc3a0f2cab81ca46ae265a196d9b495e788347670f4b34d5bcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ba5df896ef2aab0c87f8466c80dd544574233b28e071a41e00576be3ecf36fc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__978d57080a6f56d402e0e02c1bfbe681c0f68e6a9a73c1cf5ab8401ed2f86167(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverrides]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__814c297157044678c5e2ceeefc86eb0d85f8b545d8d3ebf40f27a00b57851fa8(
    *,
    default_weight: typing.Optional[jsii.Number] = None,
    pool_weights: typing.Optional[typing.Mapping[builtins.str, jsii.Number]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5b2d542c2795328bfc394989129f5dbfdca043e9a83038e624a9420b89d61ce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__976e1879118b3b9cb7164040c9c8c6689e1fb358b87d54fe6ca924b8acbba5d0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abdee6acee4f1ad305fe73df9fed1e5c23781c31a2fb93c4affefd6f908beabf(
    value: typing.Mapping[builtins.str, jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eddaf802316fdf31096e07403abb5527856dd04d08509e317383300813b7b023(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesRandomSteering]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__212cea52e61ad9e0d84095358ac0976bb725aae5de5c796154a817496e2d4cf4(
    *,
    drain_duration: typing.Optional[jsii.Number] = None,
    headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    require_all_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    samesite: typing.Optional[builtins.str] = None,
    secure: typing.Optional[builtins.str] = None,
    zero_downtime_failover: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a83ec0764af83719b0db1bbb49dee56a2d5268d80cf54458649c83037e68ff3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8df774c5ab6cdc17915467d260b7141b3316f7dcde59e450c6545c821b0400d5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45ea8046777719d6fd6f2028f6595415295d638c9ec6cfe9000725027efbb1de(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fedd1e5746747530523484f1e4e85ac7db54886ac13b9d83d153e00ce16782a9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38f27b6e0216a6d9a5700548b0527d3d55525db02714af5d1766b69234d33832(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a13569d07983e16bdfe0f077fbb0dea59e0ea80c3939ed063162aa491a32457(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9316bf4dd7ccbb813f02707b4489c845d6b8d3502347be3db440dd168cbb3db5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cddde1ce5b15a67558e5cc4750144d42d7846d714bec1f90c5166eaf8de29fc0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerRulesOverridesSessionAffinityAttributes]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__403f65be5844ed82ef2acb3e7a6d5fa371512a5ae5cc8925ecfed7a28c819c81(
    *,
    drain_duration: typing.Optional[jsii.Number] = None,
    headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    require_all_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    samesite: typing.Optional[builtins.str] = None,
    secure: typing.Optional[builtins.str] = None,
    zero_downtime_failover: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ea7a957e0edd8d304605cb4403473de01064cca85eb0e09931670911def1cbc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77eda3569a69ee49399d900cb7ce1042765598cca9379bdbeff97071f9a52f3a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a4b9e644a2227466c84d8f14c46794815d2ef354a463b535342f4dc006e6824(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e5cd4f8a15465ca15488c527bb19834e9b57c5df959f8ee725901b051d95bcb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eb428f1c01da5d8f8fae1299dfccd66e1f8f402d195782a79328ced1b712598(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07ceba26ecc59b5392f1e2d0eef2dc5838dcb0050d14feff0099c1374cfa9fa6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17459ec5207fe5828cef08a782e123e0f1187b543d7b8283e4982ce692f66ccd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08a3129d21e85210d72757defb5853cdc413e7e551a7fdf077d5776eeedb81db(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerSessionAffinityAttributes]],
) -> None:
    """Type checking stubs"""
    pass
