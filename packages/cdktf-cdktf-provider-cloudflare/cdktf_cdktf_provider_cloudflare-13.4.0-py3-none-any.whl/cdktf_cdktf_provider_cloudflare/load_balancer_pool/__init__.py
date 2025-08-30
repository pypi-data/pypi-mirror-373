r'''
# `cloudflare_load_balancer_pool`

Refer to the Terraform Registry for docs: [`cloudflare_load_balancer_pool`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool).
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


class LoadBalancerPool(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPool",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool cloudflare_load_balancer_pool}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        name: builtins.str,
        origins: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadBalancerPoolOrigins", typing.Dict[builtins.str, typing.Any]]]],
        check_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        latitude: typing.Optional[jsii.Number] = None,
        load_shedding: typing.Optional[typing.Union["LoadBalancerPoolLoadShedding", typing.Dict[builtins.str, typing.Any]]] = None,
        longitude: typing.Optional[jsii.Number] = None,
        minimum_origins: typing.Optional[jsii.Number] = None,
        monitor: typing.Optional[builtins.str] = None,
        notification_email: typing.Optional[builtins.str] = None,
        notification_filter: typing.Optional[typing.Union["LoadBalancerPoolNotificationFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        origin_steering: typing.Optional[typing.Union["LoadBalancerPoolOriginSteering", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool cloudflare_load_balancer_pool} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#account_id LoadBalancerPool#account_id}
        :param name: A short name (tag) for the pool. Only alphanumeric characters, hyphens, and underscores are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#name LoadBalancerPool#name}
        :param origins: The list of origins within this pool. Traffic directed at this pool is balanced across all currently healthy origins, provided the pool itself is healthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#origins LoadBalancerPool#origins}
        :param check_regions: A list of regions from which to run health checks. Null means every Cloudflare data center. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#check_regions LoadBalancerPool#check_regions}
        :param description: A human-readable description of the pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#description LoadBalancerPool#description}
        :param enabled: Whether to enable (the default) or disable this pool. Disabled pools will not receive traffic and are excluded from health checks. Disabling a pool will cause any load balancers using it to failover to the next pool (if any). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#enabled LoadBalancerPool#enabled}
        :param latitude: The latitude of the data center containing the origins used in this pool in decimal degrees. If this is set, longitude must also be set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#latitude LoadBalancerPool#latitude}
        :param load_shedding: Configures load shedding policies and percentages for the pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#load_shedding LoadBalancerPool#load_shedding}
        :param longitude: The longitude of the data center containing the origins used in this pool in decimal degrees. If this is set, latitude must also be set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#longitude LoadBalancerPool#longitude}
        :param minimum_origins: The minimum number of origins that must be healthy for this pool to serve traffic. If the number of healthy origins falls below this number, the pool will be marked unhealthy and will failover to the next available pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#minimum_origins LoadBalancerPool#minimum_origins}
        :param monitor: The ID of the Monitor to use for checking the health of origins within this pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#monitor LoadBalancerPool#monitor}
        :param notification_email: This field is now deprecated. It has been moved to Cloudflare's Centralized Notification service https://developers.cloudflare.com/fundamentals/notifications/. The email address to send health status notifications to. This can be an individual mailbox or a mailing list. Multiple emails can be supplied as a comma delimited list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#notification_email LoadBalancerPool#notification_email}
        :param notification_filter: Filter pool and origin health notifications by resource type or health status. Use null to reset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#notification_filter LoadBalancerPool#notification_filter}
        :param origin_steering: Configures origin steering for the pool. Controls how origins are selected for new sessions and traffic without session affinity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#origin_steering LoadBalancerPool#origin_steering}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b3b552a4bb4fcad5284c6e7ceae7509e70e4b0d04ba7128f3442cfb122a502e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = LoadBalancerPoolConfig(
            account_id=account_id,
            name=name,
            origins=origins,
            check_regions=check_regions,
            description=description,
            enabled=enabled,
            latitude=latitude,
            load_shedding=load_shedding,
            longitude=longitude,
            minimum_origins=minimum_origins,
            monitor=monitor,
            notification_email=notification_email,
            notification_filter=notification_filter,
            origin_steering=origin_steering,
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
        '''Generates CDKTF code for importing a LoadBalancerPool resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the LoadBalancerPool to import.
        :param import_from_id: The id of the existing LoadBalancerPool that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the LoadBalancerPool to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a4b435d783daa203a7c3ff4dd1269a34bfb2f03b43143276797d73c1a93e83d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putLoadShedding")
    def put_load_shedding(
        self,
        *,
        default_percent: typing.Optional[jsii.Number] = None,
        default_policy: typing.Optional[builtins.str] = None,
        session_percent: typing.Optional[jsii.Number] = None,
        session_policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_percent: The percent of traffic to shed from the pool, according to the default policy. Applies to new sessions and traffic without session affinity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#default_percent LoadBalancerPool#default_percent}
        :param default_policy: The default policy to use when load shedding. A random policy randomly sheds a given percent of requests. A hash policy computes a hash over the CF-Connecting-IP address and sheds all requests originating from a percent of IPs. Available values: "random", "hash". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#default_policy LoadBalancerPool#default_policy}
        :param session_percent: The percent of existing sessions to shed from the pool, according to the session policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#session_percent LoadBalancerPool#session_percent}
        :param session_policy: Only the hash policy is supported for existing sessions (to avoid exponential decay). Available values: "hash". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#session_policy LoadBalancerPool#session_policy}
        '''
        value = LoadBalancerPoolLoadShedding(
            default_percent=default_percent,
            default_policy=default_policy,
            session_percent=session_percent,
            session_policy=session_policy,
        )

        return typing.cast(None, jsii.invoke(self, "putLoadShedding", [value]))

    @jsii.member(jsii_name="putNotificationFilter")
    def put_notification_filter(
        self,
        *,
        origin: typing.Optional[typing.Union["LoadBalancerPoolNotificationFilterOrigin", typing.Dict[builtins.str, typing.Any]]] = None,
        pool: typing.Optional[typing.Union["LoadBalancerPoolNotificationFilterPool", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param origin: Filter options for a particular resource type (pool or origin). Use null to reset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#origin LoadBalancerPool#origin}
        :param pool: Filter options for a particular resource type (pool or origin). Use null to reset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#pool LoadBalancerPool#pool}
        '''
        value = LoadBalancerPoolNotificationFilter(origin=origin, pool=pool)

        return typing.cast(None, jsii.invoke(self, "putNotificationFilter", [value]))

    @jsii.member(jsii_name="putOrigins")
    def put_origins(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadBalancerPoolOrigins", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c121b925d3abbb25d2118b367ce0380dff98fa541f5975eed6a6c6fb0cb8408)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOrigins", [value]))

    @jsii.member(jsii_name="putOriginSteering")
    def put_origin_steering(
        self,
        *,
        policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param policy: The type of origin steering policy to use. - ``"random"``: Select an origin randomly. - ``"hash"``: Select an origin by computing a hash over the CF-Connecting-IP address. - ``"least_outstanding_requests"``: Select an origin by taking into consideration origin weights, as well as each origin's number of outstanding requests. Origins with more pending requests are weighted proportionately less relative to others. - ``"least_connections"``: Select an origin by taking into consideration origin weights, as well as each origin's number of open connections. Origins with more open connections are weighted proportionately less relative to others. Supported for HTTP/1 and HTTP/2 connections. Available values: "random", "hash", "least_outstanding_requests", "least_connections". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#policy LoadBalancerPool#policy}
        '''
        value = LoadBalancerPoolOriginSteering(policy=policy)

        return typing.cast(None, jsii.invoke(self, "putOriginSteering", [value]))

    @jsii.member(jsii_name="resetCheckRegions")
    def reset_check_regions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckRegions", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetLatitude")
    def reset_latitude(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatitude", []))

    @jsii.member(jsii_name="resetLoadShedding")
    def reset_load_shedding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoadShedding", []))

    @jsii.member(jsii_name="resetLongitude")
    def reset_longitude(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLongitude", []))

    @jsii.member(jsii_name="resetMinimumOrigins")
    def reset_minimum_origins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumOrigins", []))

    @jsii.member(jsii_name="resetMonitor")
    def reset_monitor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMonitor", []))

    @jsii.member(jsii_name="resetNotificationEmail")
    def reset_notification_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotificationEmail", []))

    @jsii.member(jsii_name="resetNotificationFilter")
    def reset_notification_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotificationFilter", []))

    @jsii.member(jsii_name="resetOriginSteering")
    def reset_origin_steering(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginSteering", []))

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
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="disabledAt")
    def disabled_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "disabledAt"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="loadShedding")
    def load_shedding(self) -> "LoadBalancerPoolLoadSheddingOutputReference":
        return typing.cast("LoadBalancerPoolLoadSheddingOutputReference", jsii.get(self, "loadShedding"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="networks")
    def networks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networks"))

    @builtins.property
    @jsii.member(jsii_name="notificationFilter")
    def notification_filter(
        self,
    ) -> "LoadBalancerPoolNotificationFilterOutputReference":
        return typing.cast("LoadBalancerPoolNotificationFilterOutputReference", jsii.get(self, "notificationFilter"))

    @builtins.property
    @jsii.member(jsii_name="origins")
    def origins(self) -> "LoadBalancerPoolOriginsList":
        return typing.cast("LoadBalancerPoolOriginsList", jsii.get(self, "origins"))

    @builtins.property
    @jsii.member(jsii_name="originSteering")
    def origin_steering(self) -> "LoadBalancerPoolOriginSteeringOutputReference":
        return typing.cast("LoadBalancerPoolOriginSteeringOutputReference", jsii.get(self, "originSteering"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="checkRegionsInput")
    def check_regions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "checkRegionsInput"))

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
    @jsii.member(jsii_name="latitudeInput")
    def latitude_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "latitudeInput"))

    @builtins.property
    @jsii.member(jsii_name="loadSheddingInput")
    def load_shedding_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerPoolLoadShedding"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerPoolLoadShedding"]], jsii.get(self, "loadSheddingInput"))

    @builtins.property
    @jsii.member(jsii_name="longitudeInput")
    def longitude_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "longitudeInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumOriginsInput")
    def minimum_origins_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimumOriginsInput"))

    @builtins.property
    @jsii.member(jsii_name="monitorInput")
    def monitor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "monitorInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="notificationEmailInput")
    def notification_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notificationEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="notificationFilterInput")
    def notification_filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerPoolNotificationFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerPoolNotificationFilter"]], jsii.get(self, "notificationFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="originsInput")
    def origins_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadBalancerPoolOrigins"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadBalancerPoolOrigins"]]], jsii.get(self, "originsInput"))

    @builtins.property
    @jsii.member(jsii_name="originSteeringInput")
    def origin_steering_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerPoolOriginSteering"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerPoolOriginSteering"]], jsii.get(self, "originSteeringInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc7655c428291295f13b8a8549a5b31763c437d4aa3caa50e2004124d8f279ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="checkRegions")
    def check_regions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "checkRegions"))

    @check_regions.setter
    def check_regions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1df46dadbc869b69bf00a93133d03ab47a6c4d110af26188392c7e686ea5d20e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checkRegions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98b2946ee1610ea56c64dcaaf5a28d0a9f99200b04c7eb60a1fb911664745339)
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
            type_hints = typing.get_type_hints(_typecheckingstub__54fc7e2c8f0ae31a734fad756123843b3b67b2d43b2bb601d2bfc407b6b818fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latitude")
    def latitude(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latitude"))

    @latitude.setter
    def latitude(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22267cc88a52d94ca349e2203675b062f62d8fca908e7efb3e19b1e65233223a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latitude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="longitude")
    def longitude(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longitude"))

    @longitude.setter
    def longitude(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b68c5ed8f3ff9288b85c250a4bc5a9a367c37e24f429991ba75ce5810775d5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "longitude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimumOrigins")
    def minimum_origins(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minimumOrigins"))

    @minimum_origins.setter
    def minimum_origins(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__680cc5b0e6ad8f2c57288213ada1b7416958798bbd10111e259890ee254cec7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimumOrigins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="monitor")
    def monitor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitor"))

    @monitor.setter
    def monitor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0021e9e6ab33a6755e73e21dd3835cdd1f3e4d1df975065652d7e5e5d970c6af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "monitor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__279398a20e435d18cba92073a866ee24e2823f892776ceef2a64e19cbdc257dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notificationEmail")
    def notification_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationEmail"))

    @notification_email.setter
    def notification_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68707b6b4521f1ad052dd7715e9b7a481d169aa0e312c7aaaddcd27fcb8bd41a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notificationEmail", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolConfig",
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
        "name": "name",
        "origins": "origins",
        "check_regions": "checkRegions",
        "description": "description",
        "enabled": "enabled",
        "latitude": "latitude",
        "load_shedding": "loadShedding",
        "longitude": "longitude",
        "minimum_origins": "minimumOrigins",
        "monitor": "monitor",
        "notification_email": "notificationEmail",
        "notification_filter": "notificationFilter",
        "origin_steering": "originSteering",
    },
)
class LoadBalancerPoolConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        origins: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadBalancerPoolOrigins", typing.Dict[builtins.str, typing.Any]]]],
        check_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        latitude: typing.Optional[jsii.Number] = None,
        load_shedding: typing.Optional[typing.Union["LoadBalancerPoolLoadShedding", typing.Dict[builtins.str, typing.Any]]] = None,
        longitude: typing.Optional[jsii.Number] = None,
        minimum_origins: typing.Optional[jsii.Number] = None,
        monitor: typing.Optional[builtins.str] = None,
        notification_email: typing.Optional[builtins.str] = None,
        notification_filter: typing.Optional[typing.Union["LoadBalancerPoolNotificationFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        origin_steering: typing.Optional[typing.Union["LoadBalancerPoolOriginSteering", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#account_id LoadBalancerPool#account_id}
        :param name: A short name (tag) for the pool. Only alphanumeric characters, hyphens, and underscores are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#name LoadBalancerPool#name}
        :param origins: The list of origins within this pool. Traffic directed at this pool is balanced across all currently healthy origins, provided the pool itself is healthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#origins LoadBalancerPool#origins}
        :param check_regions: A list of regions from which to run health checks. Null means every Cloudflare data center. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#check_regions LoadBalancerPool#check_regions}
        :param description: A human-readable description of the pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#description LoadBalancerPool#description}
        :param enabled: Whether to enable (the default) or disable this pool. Disabled pools will not receive traffic and are excluded from health checks. Disabling a pool will cause any load balancers using it to failover to the next pool (if any). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#enabled LoadBalancerPool#enabled}
        :param latitude: The latitude of the data center containing the origins used in this pool in decimal degrees. If this is set, longitude must also be set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#latitude LoadBalancerPool#latitude}
        :param load_shedding: Configures load shedding policies and percentages for the pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#load_shedding LoadBalancerPool#load_shedding}
        :param longitude: The longitude of the data center containing the origins used in this pool in decimal degrees. If this is set, latitude must also be set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#longitude LoadBalancerPool#longitude}
        :param minimum_origins: The minimum number of origins that must be healthy for this pool to serve traffic. If the number of healthy origins falls below this number, the pool will be marked unhealthy and will failover to the next available pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#minimum_origins LoadBalancerPool#minimum_origins}
        :param monitor: The ID of the Monitor to use for checking the health of origins within this pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#monitor LoadBalancerPool#monitor}
        :param notification_email: This field is now deprecated. It has been moved to Cloudflare's Centralized Notification service https://developers.cloudflare.com/fundamentals/notifications/. The email address to send health status notifications to. This can be an individual mailbox or a mailing list. Multiple emails can be supplied as a comma delimited list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#notification_email LoadBalancerPool#notification_email}
        :param notification_filter: Filter pool and origin health notifications by resource type or health status. Use null to reset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#notification_filter LoadBalancerPool#notification_filter}
        :param origin_steering: Configures origin steering for the pool. Controls how origins are selected for new sessions and traffic without session affinity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#origin_steering LoadBalancerPool#origin_steering}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(load_shedding, dict):
            load_shedding = LoadBalancerPoolLoadShedding(**load_shedding)
        if isinstance(notification_filter, dict):
            notification_filter = LoadBalancerPoolNotificationFilter(**notification_filter)
        if isinstance(origin_steering, dict):
            origin_steering = LoadBalancerPoolOriginSteering(**origin_steering)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__692be5c2b081be7d23745f651c1b30e04c41009d4b1d5588cec705f651d298f9)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument origins", value=origins, expected_type=type_hints["origins"])
            check_type(argname="argument check_regions", value=check_regions, expected_type=type_hints["check_regions"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument latitude", value=latitude, expected_type=type_hints["latitude"])
            check_type(argname="argument load_shedding", value=load_shedding, expected_type=type_hints["load_shedding"])
            check_type(argname="argument longitude", value=longitude, expected_type=type_hints["longitude"])
            check_type(argname="argument minimum_origins", value=minimum_origins, expected_type=type_hints["minimum_origins"])
            check_type(argname="argument monitor", value=monitor, expected_type=type_hints["monitor"])
            check_type(argname="argument notification_email", value=notification_email, expected_type=type_hints["notification_email"])
            check_type(argname="argument notification_filter", value=notification_filter, expected_type=type_hints["notification_filter"])
            check_type(argname="argument origin_steering", value=origin_steering, expected_type=type_hints["origin_steering"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "name": name,
            "origins": origins,
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
        if check_regions is not None:
            self._values["check_regions"] = check_regions
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if latitude is not None:
            self._values["latitude"] = latitude
        if load_shedding is not None:
            self._values["load_shedding"] = load_shedding
        if longitude is not None:
            self._values["longitude"] = longitude
        if minimum_origins is not None:
            self._values["minimum_origins"] = minimum_origins
        if monitor is not None:
            self._values["monitor"] = monitor
        if notification_email is not None:
            self._values["notification_email"] = notification_email
        if notification_filter is not None:
            self._values["notification_filter"] = notification_filter
        if origin_steering is not None:
            self._values["origin_steering"] = origin_steering

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
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#account_id LoadBalancerPool#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''A short name (tag) for the pool. Only alphanumeric characters, hyphens, and underscores are allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#name LoadBalancerPool#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def origins(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadBalancerPoolOrigins"]]:
        '''The list of origins within this pool.

        Traffic directed at this pool is balanced across all currently healthy origins, provided the pool itself is healthy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#origins LoadBalancerPool#origins}
        '''
        result = self._values.get("origins")
        assert result is not None, "Required property 'origins' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadBalancerPoolOrigins"]], result)

    @builtins.property
    def check_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of regions from which to run health checks. Null means every Cloudflare data center.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#check_regions LoadBalancerPool#check_regions}
        '''
        result = self._values.get("check_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A human-readable description of the pool.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#description LoadBalancerPool#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to enable (the default) or disable this pool.

        Disabled pools will not receive traffic and are excluded from health checks. Disabling a pool will cause any load balancers using it to failover to the next pool (if any).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#enabled LoadBalancerPool#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def latitude(self) -> typing.Optional[jsii.Number]:
        '''The latitude of the data center containing the origins used in this pool in decimal degrees.

        If this is set, longitude must also be set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#latitude LoadBalancerPool#latitude}
        '''
        result = self._values.get("latitude")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def load_shedding(self) -> typing.Optional["LoadBalancerPoolLoadShedding"]:
        '''Configures load shedding policies and percentages for the pool.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#load_shedding LoadBalancerPool#load_shedding}
        '''
        result = self._values.get("load_shedding")
        return typing.cast(typing.Optional["LoadBalancerPoolLoadShedding"], result)

    @builtins.property
    def longitude(self) -> typing.Optional[jsii.Number]:
        '''The longitude of the data center containing the origins used in this pool in decimal degrees.

        If this is set, latitude must also be set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#longitude LoadBalancerPool#longitude}
        '''
        result = self._values.get("longitude")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minimum_origins(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of origins that must be healthy for this pool to serve traffic.

        If the number of healthy origins falls below this number, the pool will be marked unhealthy and will failover to the next available pool.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#minimum_origins LoadBalancerPool#minimum_origins}
        '''
        result = self._values.get("minimum_origins")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def monitor(self) -> typing.Optional[builtins.str]:
        '''The ID of the Monitor to use for checking the health of origins within this pool.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#monitor LoadBalancerPool#monitor}
        '''
        result = self._values.get("monitor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_email(self) -> typing.Optional[builtins.str]:
        '''This field is now deprecated.

        It has been moved to Cloudflare's Centralized Notification service https://developers.cloudflare.com/fundamentals/notifications/. The email address to send health status notifications to. This can be an individual mailbox or a mailing list. Multiple emails can be supplied as a comma delimited list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#notification_email LoadBalancerPool#notification_email}
        '''
        result = self._values.get("notification_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_filter(
        self,
    ) -> typing.Optional["LoadBalancerPoolNotificationFilter"]:
        '''Filter pool and origin health notifications by resource type or health status. Use null to reset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#notification_filter LoadBalancerPool#notification_filter}
        '''
        result = self._values.get("notification_filter")
        return typing.cast(typing.Optional["LoadBalancerPoolNotificationFilter"], result)

    @builtins.property
    def origin_steering(self) -> typing.Optional["LoadBalancerPoolOriginSteering"]:
        '''Configures origin steering for the pool. Controls how origins are selected for new sessions and traffic without session affinity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#origin_steering LoadBalancerPool#origin_steering}
        '''
        result = self._values.get("origin_steering")
        return typing.cast(typing.Optional["LoadBalancerPoolOriginSteering"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerPoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolLoadShedding",
    jsii_struct_bases=[],
    name_mapping={
        "default_percent": "defaultPercent",
        "default_policy": "defaultPolicy",
        "session_percent": "sessionPercent",
        "session_policy": "sessionPolicy",
    },
)
class LoadBalancerPoolLoadShedding:
    def __init__(
        self,
        *,
        default_percent: typing.Optional[jsii.Number] = None,
        default_policy: typing.Optional[builtins.str] = None,
        session_percent: typing.Optional[jsii.Number] = None,
        session_policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_percent: The percent of traffic to shed from the pool, according to the default policy. Applies to new sessions and traffic without session affinity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#default_percent LoadBalancerPool#default_percent}
        :param default_policy: The default policy to use when load shedding. A random policy randomly sheds a given percent of requests. A hash policy computes a hash over the CF-Connecting-IP address and sheds all requests originating from a percent of IPs. Available values: "random", "hash". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#default_policy LoadBalancerPool#default_policy}
        :param session_percent: The percent of existing sessions to shed from the pool, according to the session policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#session_percent LoadBalancerPool#session_percent}
        :param session_policy: Only the hash policy is supported for existing sessions (to avoid exponential decay). Available values: "hash". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#session_policy LoadBalancerPool#session_policy}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__715bb646fc17ccd60bd6a750e5f890dfa8638411709d825bbab4a7257d205450)
            check_type(argname="argument default_percent", value=default_percent, expected_type=type_hints["default_percent"])
            check_type(argname="argument default_policy", value=default_policy, expected_type=type_hints["default_policy"])
            check_type(argname="argument session_percent", value=session_percent, expected_type=type_hints["session_percent"])
            check_type(argname="argument session_policy", value=session_policy, expected_type=type_hints["session_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if default_percent is not None:
            self._values["default_percent"] = default_percent
        if default_policy is not None:
            self._values["default_policy"] = default_policy
        if session_percent is not None:
            self._values["session_percent"] = session_percent
        if session_policy is not None:
            self._values["session_policy"] = session_policy

    @builtins.property
    def default_percent(self) -> typing.Optional[jsii.Number]:
        '''The percent of traffic to shed from the pool, according to the default policy.

        Applies to new sessions and traffic without session affinity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#default_percent LoadBalancerPool#default_percent}
        '''
        result = self._values.get("default_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_policy(self) -> typing.Optional[builtins.str]:
        '''The default policy to use when load shedding.

        A random policy randomly sheds a given percent of requests. A hash policy computes a hash over the CF-Connecting-IP address and sheds all requests originating from a percent of IPs.
        Available values: "random", "hash".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#default_policy LoadBalancerPool#default_policy}
        '''
        result = self._values.get("default_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_percent(self) -> typing.Optional[jsii.Number]:
        '''The percent of existing sessions to shed from the pool, according to the session policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#session_percent LoadBalancerPool#session_percent}
        '''
        result = self._values.get("session_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def session_policy(self) -> typing.Optional[builtins.str]:
        '''Only the hash policy is supported for existing sessions (to avoid exponential decay). Available values: "hash".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#session_policy LoadBalancerPool#session_policy}
        '''
        result = self._values.get("session_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerPoolLoadShedding(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerPoolLoadSheddingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolLoadSheddingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__216363376007d395389870494823e1b7ea92cc0e6909469dd60dcf0c590f8b9e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDefaultPercent")
    def reset_default_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultPercent", []))

    @jsii.member(jsii_name="resetDefaultPolicy")
    def reset_default_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultPolicy", []))

    @jsii.member(jsii_name="resetSessionPercent")
    def reset_session_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionPercent", []))

    @jsii.member(jsii_name="resetSessionPolicy")
    def reset_session_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionPolicy", []))

    @builtins.property
    @jsii.member(jsii_name="defaultPercentInput")
    def default_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultPercentInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultPolicyInput")
    def default_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionPercentInput")
    def session_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sessionPercentInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionPolicyInput")
    def session_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultPercent")
    def default_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultPercent"))

    @default_percent.setter
    def default_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83f687fc7787be4b00c893df736871340a1cfa4c8754f5395541bad06c11092c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultPercent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultPolicy")
    def default_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultPolicy"))

    @default_policy.setter
    def default_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad6ac1cc657cb03727e9475fe58f521ad724f021e9a686ab395c3ce5e172c260)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionPercent")
    def session_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sessionPercent"))

    @session_percent.setter
    def session_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd0eda545ddbf8d12c6b5fa423f48997ddd255ddb77ba59b1b3ea6684578af6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionPercent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionPolicy")
    def session_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionPolicy"))

    @session_policy.setter
    def session_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f300582bfd2527b41f89748513f616ca3f392344544f7fac53380c18b70a7ab2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolLoadShedding]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolLoadShedding]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolLoadShedding]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdb48881143b7edfa84451d97f301d404fa8b4787eafb1bab0f5ca773ee75ddd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolNotificationFilter",
    jsii_struct_bases=[],
    name_mapping={"origin": "origin", "pool": "pool"},
)
class LoadBalancerPoolNotificationFilter:
    def __init__(
        self,
        *,
        origin: typing.Optional[typing.Union["LoadBalancerPoolNotificationFilterOrigin", typing.Dict[builtins.str, typing.Any]]] = None,
        pool: typing.Optional[typing.Union["LoadBalancerPoolNotificationFilterPool", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param origin: Filter options for a particular resource type (pool or origin). Use null to reset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#origin LoadBalancerPool#origin}
        :param pool: Filter options for a particular resource type (pool or origin). Use null to reset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#pool LoadBalancerPool#pool}
        '''
        if isinstance(origin, dict):
            origin = LoadBalancerPoolNotificationFilterOrigin(**origin)
        if isinstance(pool, dict):
            pool = LoadBalancerPoolNotificationFilterPool(**pool)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72b7b8e2d3501a6e1764f678f4198d8639fcaeede8362c4a92a47c8642df6e82)
            check_type(argname="argument origin", value=origin, expected_type=type_hints["origin"])
            check_type(argname="argument pool", value=pool, expected_type=type_hints["pool"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if origin is not None:
            self._values["origin"] = origin
        if pool is not None:
            self._values["pool"] = pool

    @builtins.property
    def origin(self) -> typing.Optional["LoadBalancerPoolNotificationFilterOrigin"]:
        '''Filter options for a particular resource type (pool or origin). Use null to reset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#origin LoadBalancerPool#origin}
        '''
        result = self._values.get("origin")
        return typing.cast(typing.Optional["LoadBalancerPoolNotificationFilterOrigin"], result)

    @builtins.property
    def pool(self) -> typing.Optional["LoadBalancerPoolNotificationFilterPool"]:
        '''Filter options for a particular resource type (pool or origin). Use null to reset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#pool LoadBalancerPool#pool}
        '''
        result = self._values.get("pool")
        return typing.cast(typing.Optional["LoadBalancerPoolNotificationFilterPool"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerPoolNotificationFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolNotificationFilterOrigin",
    jsii_struct_bases=[],
    name_mapping={"disable": "disable", "healthy": "healthy"},
)
class LoadBalancerPoolNotificationFilterOrigin:
    def __init__(
        self,
        *,
        disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        healthy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param disable: If set true, disable notifications for this type of resource (pool or origin). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#disable LoadBalancerPool#disable}
        :param healthy: If present, send notifications only for this health status (e.g. false for only DOWN events). Use null to reset (all events). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#healthy LoadBalancerPool#healthy}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a29399290db2668acc77e99314889fe6a60cc82404498f7f3e7db7361505c162)
            check_type(argname="argument disable", value=disable, expected_type=type_hints["disable"])
            check_type(argname="argument healthy", value=healthy, expected_type=type_hints["healthy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if disable is not None:
            self._values["disable"] = disable
        if healthy is not None:
            self._values["healthy"] = healthy

    @builtins.property
    def disable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set true, disable notifications for this type of resource (pool or origin).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#disable LoadBalancerPool#disable}
        '''
        result = self._values.get("disable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def healthy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If present, send notifications only for this health status (e.g. false for only DOWN events). Use null to reset (all events).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#healthy LoadBalancerPool#healthy}
        '''
        result = self._values.get("healthy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerPoolNotificationFilterOrigin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerPoolNotificationFilterOriginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolNotificationFilterOriginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e3049fdcdc53efbfb8f3da5d45e988ebecec226933e6318b09c868344f0a30f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDisable")
    def reset_disable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisable", []))

    @jsii.member(jsii_name="resetHealthy")
    def reset_healthy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthy", []))

    @builtins.property
    @jsii.member(jsii_name="disableInput")
    def disable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableInput"))

    @builtins.property
    @jsii.member(jsii_name="healthyInput")
    def healthy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "healthyInput"))

    @builtins.property
    @jsii.member(jsii_name="disable")
    def disable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disable"))

    @disable.setter
    def disable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__794ba1f55491e323823daeaee259cd5bb12770f17dec42c3fb19b1f0020abb71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthy")
    def healthy(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "healthy"))

    @healthy.setter
    def healthy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a31e810cb342aad2609e70d80068cfb4d9577d515db284b0dbace836a10e3a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterOrigin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterOrigin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterOrigin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f071e2e89c07bc9e62ed1c503d62afcf0ae4a8ae75ef4e8ea873e22293069e11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadBalancerPoolNotificationFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolNotificationFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f0fa0152c5a545b246061fc5b7651542ff7d4faa88a2343a45d350b67dcd6db1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOrigin")
    def put_origin(
        self,
        *,
        disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        healthy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param disable: If set true, disable notifications for this type of resource (pool or origin). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#disable LoadBalancerPool#disable}
        :param healthy: If present, send notifications only for this health status (e.g. false for only DOWN events). Use null to reset (all events). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#healthy LoadBalancerPool#healthy}
        '''
        value = LoadBalancerPoolNotificationFilterOrigin(
            disable=disable, healthy=healthy
        )

        return typing.cast(None, jsii.invoke(self, "putOrigin", [value]))

    @jsii.member(jsii_name="putPool")
    def put_pool(
        self,
        *,
        disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        healthy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param disable: If set true, disable notifications for this type of resource (pool or origin). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#disable LoadBalancerPool#disable}
        :param healthy: If present, send notifications only for this health status (e.g. false for only DOWN events). Use null to reset (all events). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#healthy LoadBalancerPool#healthy}
        '''
        value = LoadBalancerPoolNotificationFilterPool(
            disable=disable, healthy=healthy
        )

        return typing.cast(None, jsii.invoke(self, "putPool", [value]))

    @jsii.member(jsii_name="resetOrigin")
    def reset_origin(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrigin", []))

    @jsii.member(jsii_name="resetPool")
    def reset_pool(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPool", []))

    @builtins.property
    @jsii.member(jsii_name="origin")
    def origin(self) -> LoadBalancerPoolNotificationFilterOriginOutputReference:
        return typing.cast(LoadBalancerPoolNotificationFilterOriginOutputReference, jsii.get(self, "origin"))

    @builtins.property
    @jsii.member(jsii_name="pool")
    def pool(self) -> "LoadBalancerPoolNotificationFilterPoolOutputReference":
        return typing.cast("LoadBalancerPoolNotificationFilterPoolOutputReference", jsii.get(self, "pool"))

    @builtins.property
    @jsii.member(jsii_name="originInput")
    def origin_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterOrigin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterOrigin]], jsii.get(self, "originInput"))

    @builtins.property
    @jsii.member(jsii_name="poolInput")
    def pool_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerPoolNotificationFilterPool"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LoadBalancerPoolNotificationFilterPool"]], jsii.get(self, "poolInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0079a95b81e37a62827f84e56f94b252538e5ca99ed54761db5acd868b7b2290)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolNotificationFilterPool",
    jsii_struct_bases=[],
    name_mapping={"disable": "disable", "healthy": "healthy"},
)
class LoadBalancerPoolNotificationFilterPool:
    def __init__(
        self,
        *,
        disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        healthy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param disable: If set true, disable notifications for this type of resource (pool or origin). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#disable LoadBalancerPool#disable}
        :param healthy: If present, send notifications only for this health status (e.g. false for only DOWN events). Use null to reset (all events). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#healthy LoadBalancerPool#healthy}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19a02cfea9301552242c157e0b64052be5a45b348a51e874a10de46f99495e15)
            check_type(argname="argument disable", value=disable, expected_type=type_hints["disable"])
            check_type(argname="argument healthy", value=healthy, expected_type=type_hints["healthy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if disable is not None:
            self._values["disable"] = disable
        if healthy is not None:
            self._values["healthy"] = healthy

    @builtins.property
    def disable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set true, disable notifications for this type of resource (pool or origin).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#disable LoadBalancerPool#disable}
        '''
        result = self._values.get("disable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def healthy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If present, send notifications only for this health status (e.g. false for only DOWN events). Use null to reset (all events).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#healthy LoadBalancerPool#healthy}
        '''
        result = self._values.get("healthy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerPoolNotificationFilterPool(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerPoolNotificationFilterPoolOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolNotificationFilterPoolOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__880c2fbbb2fddd1c3f274597504118973d1bd1d8ec68c568edaff0235a433dc8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDisable")
    def reset_disable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisable", []))

    @jsii.member(jsii_name="resetHealthy")
    def reset_healthy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthy", []))

    @builtins.property
    @jsii.member(jsii_name="disableInput")
    def disable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableInput"))

    @builtins.property
    @jsii.member(jsii_name="healthyInput")
    def healthy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "healthyInput"))

    @builtins.property
    @jsii.member(jsii_name="disable")
    def disable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disable"))

    @disable.setter
    def disable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2edce83b2b3991a8eb4de99d4c8d9bfe6d68200c3b80731f15da1bf1c263ed8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthy")
    def healthy(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "healthy"))

    @healthy.setter
    def healthy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c60efb860ab554cd4328e186dbbc3b6d02f85a7d779aa159646834c69ab07078)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterPool]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterPool]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterPool]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca9253f53634bf6ad886e8942f86dd0d20d7b88185852fa477bf14d08a2fdcaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolOriginSteering",
    jsii_struct_bases=[],
    name_mapping={"policy": "policy"},
)
class LoadBalancerPoolOriginSteering:
    def __init__(self, *, policy: typing.Optional[builtins.str] = None) -> None:
        '''
        :param policy: The type of origin steering policy to use. - ``"random"``: Select an origin randomly. - ``"hash"``: Select an origin by computing a hash over the CF-Connecting-IP address. - ``"least_outstanding_requests"``: Select an origin by taking into consideration origin weights, as well as each origin's number of outstanding requests. Origins with more pending requests are weighted proportionately less relative to others. - ``"least_connections"``: Select an origin by taking into consideration origin weights, as well as each origin's number of open connections. Origins with more open connections are weighted proportionately less relative to others. Supported for HTTP/1 and HTTP/2 connections. Available values: "random", "hash", "least_outstanding_requests", "least_connections". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#policy LoadBalancerPool#policy}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c72c8eb26ee3b133606b600532da2142af1e8f1791717295c41c7778ed236dc)
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if policy is not None:
            self._values["policy"] = policy

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''The type of origin steering policy to use.

        - ``"random"``: Select an origin randomly.
        - ``"hash"``: Select an origin by computing a hash over the CF-Connecting-IP address.
        - ``"least_outstanding_requests"``: Select an origin by taking into consideration origin weights, as well as each origin's number of outstanding requests. Origins with more pending requests are weighted proportionately less relative to others.
        - ``"least_connections"``: Select an origin by taking into consideration origin weights, as well as each origin's number of open connections. Origins with more open connections are weighted proportionately less relative to others. Supported for HTTP/1 and HTTP/2 connections.
          Available values: "random", "hash", "least_outstanding_requests", "least_connections".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#policy LoadBalancerPool#policy}
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerPoolOriginSteering(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerPoolOriginSteeringOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolOriginSteeringOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d75ba71413daca192bad8a16102726dda08fd5a033408ea85dbd3fe05d383f62)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @builtins.property
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61e0a410d1ebd8ccc9fb5aa24f64a14f7b813c0e25e637b4c0b727e3df2ae1c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginSteering]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginSteering]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginSteering]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__221251a3706dee0b19d8623c6786f866e55a00ef603e10c85185b5aa9d9b0766)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolOrigins",
    jsii_struct_bases=[],
    name_mapping={
        "address": "address",
        "enabled": "enabled",
        "header": "header",
        "name": "name",
        "port": "port",
        "virtual_network_id": "virtualNetworkId",
        "weight": "weight",
    },
)
class LoadBalancerPoolOrigins:
    def __init__(
        self,
        *,
        address: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        header: typing.Optional[typing.Union["LoadBalancerPoolOriginsHeader", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        virtual_network_id: typing.Optional[builtins.str] = None,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param address: The IP address (IPv4 or IPv6) of the origin, or its publicly addressable hostname. Hostnames entered here should resolve directly to the origin, and not be a hostname proxied by Cloudflare. To set an internal/reserved address, virtual_network_id must also be set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#address LoadBalancerPool#address}
        :param enabled: Whether to enable (the default) this origin within the pool. Disabled origins will not receive traffic and are excluded from health checks. The origin will only be disabled for the current pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#enabled LoadBalancerPool#enabled}
        :param header: The request header is used to pass additional information with an HTTP request. Currently supported header is 'Host'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#header LoadBalancerPool#header}
        :param name: A human-identifiable name for the origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#name LoadBalancerPool#name}
        :param port: The port for upstream connections. A value of 0 means the default port for the protocol will be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#port LoadBalancerPool#port}
        :param virtual_network_id: The virtual network subnet ID the origin belongs in. Virtual network must also belong to the account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#virtual_network_id LoadBalancerPool#virtual_network_id}
        :param weight: The weight of this origin relative to other origins in the pool. Based on the configured weight the total traffic is distributed among origins within the pool. - ``origin_steering.policy="least_outstanding_requests"``: Use weight to scale the origin's outstanding requests. - ``origin_steering.policy="least_connections"``: Use weight to scale the origin's open connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#weight LoadBalancerPool#weight}
        '''
        if isinstance(header, dict):
            header = LoadBalancerPoolOriginsHeader(**header)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fa2420bd66ef218996632a7196f195d33fe95eaa8e0c6af6e1a3921395cd41b)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument header", value=header, expected_type=type_hints["header"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument virtual_network_id", value=virtual_network_id, expected_type=type_hints["virtual_network_id"])
            check_type(argname="argument weight", value=weight, expected_type=type_hints["weight"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if address is not None:
            self._values["address"] = address
        if enabled is not None:
            self._values["enabled"] = enabled
        if header is not None:
            self._values["header"] = header
        if name is not None:
            self._values["name"] = name
        if port is not None:
            self._values["port"] = port
        if virtual_network_id is not None:
            self._values["virtual_network_id"] = virtual_network_id
        if weight is not None:
            self._values["weight"] = weight

    @builtins.property
    def address(self) -> typing.Optional[builtins.str]:
        '''The IP address (IPv4 or IPv6) of the origin, or its publicly addressable hostname.

        Hostnames entered here should resolve directly to the origin, and not be a hostname proxied by Cloudflare. To set an internal/reserved address, virtual_network_id must also be set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#address LoadBalancerPool#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to enable (the default) this origin within the pool.

        Disabled origins will not receive traffic and are excluded from health checks. The origin will only be disabled for the current pool.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#enabled LoadBalancerPool#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def header(self) -> typing.Optional["LoadBalancerPoolOriginsHeader"]:
        '''The request header is used to pass additional information with an HTTP request. Currently supported header is 'Host'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#header LoadBalancerPool#header}
        '''
        result = self._values.get("header")
        return typing.cast(typing.Optional["LoadBalancerPoolOriginsHeader"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''A human-identifiable name for the origin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#name LoadBalancerPool#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The port for upstream connections. A value of 0 means the default port for the protocol will be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#port LoadBalancerPool#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def virtual_network_id(self) -> typing.Optional[builtins.str]:
        '''The virtual network subnet ID the origin belongs in. Virtual network must also belong to the account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#virtual_network_id LoadBalancerPool#virtual_network_id}
        '''
        result = self._values.get("virtual_network_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def weight(self) -> typing.Optional[jsii.Number]:
        '''The weight of this origin relative to other origins in the pool.

        Based on the configured weight the total traffic is distributed among origins within the pool.

        - ``origin_steering.policy="least_outstanding_requests"``: Use weight to scale the origin's outstanding requests.
        - ``origin_steering.policy="least_connections"``: Use weight to scale the origin's open connections.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#weight LoadBalancerPool#weight}
        '''
        result = self._values.get("weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerPoolOrigins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolOriginsHeader",
    jsii_struct_bases=[],
    name_mapping={"host": "host"},
)
class LoadBalancerPoolOriginsHeader:
    def __init__(
        self,
        *,
        host: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param host: The 'Host' header allows to override the hostname set in the HTTP request. Current support is 1 'Host' header override per origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#host LoadBalancerPool#host}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__341602971ceb0c2249b031606eb62902eaca9fb381b7141e848415dfb8c2272c)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if host is not None:
            self._values["host"] = host

    @builtins.property
    def host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The 'Host' header allows to override the hostname set in the HTTP request.

        Current support is 1 'Host' header override per origin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#host LoadBalancerPool#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerPoolOriginsHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerPoolOriginsHeaderOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolOriginsHeaderOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__52e430333cb1cccb5662d819056cf5ebb3fce0ccb0db3b2b07da7e7f71f85192)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "host"))

    @host.setter
    def host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__057f817edbcc3497a1ee4e539fd38cb5497507a5458537d2f50567114a30862d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginsHeader]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginsHeader]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginsHeader]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa25a684f7465ec5a3d108a975bfc1719f9ac2a525d86c74a7decdd33332c34b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadBalancerPoolOriginsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolOriginsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b89cf595bdc66572070fd0ac3bf46db245adb30c940ea9e23b30c31f8800297)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "LoadBalancerPoolOriginsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__075031e82b917393d5ec53c8833bb3d0decd5c9cad76d85a9296c225edba8bb9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("LoadBalancerPoolOriginsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8efa4d8c3ec1c3cf331ccb9c7bba7c4777bef5c9114d5204e6794d1e373b5cf3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8327a70d3f6860970bf1f55b0b1391f066771a7136faf4bf0f2da27e8de0f555)
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
            type_hints = typing.get_type_hints(_typecheckingstub__677d4893c66570f3d5813e097d63866c7203c4cf298e77c84aa1eace2800ba65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadBalancerPoolOrigins]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadBalancerPoolOrigins]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadBalancerPoolOrigins]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b301155d9d8ac8030420756216d87f19d458db58ba95091b2e4b6a83198eef2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadBalancerPoolOriginsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.loadBalancerPool.LoadBalancerPoolOriginsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea9a95c81bf62ddf8299ca0c8e3f3c110498404b905b5c61881b66c681dd3911)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putHeader")
    def put_header(
        self,
        *,
        host: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param host: The 'Host' header allows to override the hostname set in the HTTP request. Current support is 1 'Host' header override per origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/load_balancer_pool#host LoadBalancerPool#host}
        '''
        value = LoadBalancerPoolOriginsHeader(host=host)

        return typing.cast(None, jsii.invoke(self, "putHeader", [value]))

    @jsii.member(jsii_name="resetAddress")
    def reset_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddress", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetHeader")
    def reset_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeader", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetVirtualNetworkId")
    def reset_virtual_network_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualNetworkId", []))

    @jsii.member(jsii_name="resetWeight")
    def reset_weight(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeight", []))

    @builtins.property
    @jsii.member(jsii_name="disabledAt")
    def disabled_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "disabledAt"))

    @builtins.property
    @jsii.member(jsii_name="header")
    def header(self) -> LoadBalancerPoolOriginsHeaderOutputReference:
        return typing.cast(LoadBalancerPoolOriginsHeaderOutputReference, jsii.get(self, "header"))

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="headerInput")
    def header_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginsHeader]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginsHeader]], jsii.get(self, "headerInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkIdInput")
    def virtual_network_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualNetworkIdInput"))

    @builtins.property
    @jsii.member(jsii_name="weightInput")
    def weight_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "weightInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e93178082349f1ff50ea8227dcf6d8c732258853a13c0ba3749d774b7032a19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__9ecd93a4e787115ed3f52bb1be6341f9f785c557638452028f00ee74407650a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5a5fc1fbede8d1b9fd8b05a385a204d60c667f10fa373c9de7f857524991c55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a3d82b6280c3790ca53aa000256dffdd4258a19cf0cede0630d894f17d4f42d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkId")
    def virtual_network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualNetworkId"))

    @virtual_network_id.setter
    def virtual_network_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d218d2d2bb51d4af09bae86ea92bd7b89eac7744e8f6efb2f7c6a105615f02e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualNetworkId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="weight")
    def weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weight"))

    @weight.setter
    def weight(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c070f1d9d759410d13a999a3aec55880a13d209243be37c7988ed2809a29fc4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "weight", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOrigins]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOrigins]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOrigins]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2afdb8a3dba053cd228e17329b27bc8a62a0a971ba48bc8b3364ff9c690cee09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "LoadBalancerPool",
    "LoadBalancerPoolConfig",
    "LoadBalancerPoolLoadShedding",
    "LoadBalancerPoolLoadSheddingOutputReference",
    "LoadBalancerPoolNotificationFilter",
    "LoadBalancerPoolNotificationFilterOrigin",
    "LoadBalancerPoolNotificationFilterOriginOutputReference",
    "LoadBalancerPoolNotificationFilterOutputReference",
    "LoadBalancerPoolNotificationFilterPool",
    "LoadBalancerPoolNotificationFilterPoolOutputReference",
    "LoadBalancerPoolOriginSteering",
    "LoadBalancerPoolOriginSteeringOutputReference",
    "LoadBalancerPoolOrigins",
    "LoadBalancerPoolOriginsHeader",
    "LoadBalancerPoolOriginsHeaderOutputReference",
    "LoadBalancerPoolOriginsList",
    "LoadBalancerPoolOriginsOutputReference",
]

publication.publish()

def _typecheckingstub__0b3b552a4bb4fcad5284c6e7ceae7509e70e4b0d04ba7128f3442cfb122a502e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    name: builtins.str,
    origins: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadBalancerPoolOrigins, typing.Dict[builtins.str, typing.Any]]]],
    check_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    latitude: typing.Optional[jsii.Number] = None,
    load_shedding: typing.Optional[typing.Union[LoadBalancerPoolLoadShedding, typing.Dict[builtins.str, typing.Any]]] = None,
    longitude: typing.Optional[jsii.Number] = None,
    minimum_origins: typing.Optional[jsii.Number] = None,
    monitor: typing.Optional[builtins.str] = None,
    notification_email: typing.Optional[builtins.str] = None,
    notification_filter: typing.Optional[typing.Union[LoadBalancerPoolNotificationFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    origin_steering: typing.Optional[typing.Union[LoadBalancerPoolOriginSteering, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__6a4b435d783daa203a7c3ff4dd1269a34bfb2f03b43143276797d73c1a93e83d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c121b925d3abbb25d2118b367ce0380dff98fa541f5975eed6a6c6fb0cb8408(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadBalancerPoolOrigins, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc7655c428291295f13b8a8549a5b31763c437d4aa3caa50e2004124d8f279ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1df46dadbc869b69bf00a93133d03ab47a6c4d110af26188392c7e686ea5d20e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98b2946ee1610ea56c64dcaaf5a28d0a9f99200b04c7eb60a1fb911664745339(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54fc7e2c8f0ae31a734fad756123843b3b67b2d43b2bb601d2bfc407b6b818fc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22267cc88a52d94ca349e2203675b062f62d8fca908e7efb3e19b1e65233223a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b68c5ed8f3ff9288b85c250a4bc5a9a367c37e24f429991ba75ce5810775d5f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__680cc5b0e6ad8f2c57288213ada1b7416958798bbd10111e259890ee254cec7b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0021e9e6ab33a6755e73e21dd3835cdd1f3e4d1df975065652d7e5e5d970c6af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__279398a20e435d18cba92073a866ee24e2823f892776ceef2a64e19cbdc257dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68707b6b4521f1ad052dd7715e9b7a481d169aa0e312c7aaaddcd27fcb8bd41a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692be5c2b081be7d23745f651c1b30e04c41009d4b1d5588cec705f651d298f9(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    name: builtins.str,
    origins: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadBalancerPoolOrigins, typing.Dict[builtins.str, typing.Any]]]],
    check_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    latitude: typing.Optional[jsii.Number] = None,
    load_shedding: typing.Optional[typing.Union[LoadBalancerPoolLoadShedding, typing.Dict[builtins.str, typing.Any]]] = None,
    longitude: typing.Optional[jsii.Number] = None,
    minimum_origins: typing.Optional[jsii.Number] = None,
    monitor: typing.Optional[builtins.str] = None,
    notification_email: typing.Optional[builtins.str] = None,
    notification_filter: typing.Optional[typing.Union[LoadBalancerPoolNotificationFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    origin_steering: typing.Optional[typing.Union[LoadBalancerPoolOriginSteering, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__715bb646fc17ccd60bd6a750e5f890dfa8638411709d825bbab4a7257d205450(
    *,
    default_percent: typing.Optional[jsii.Number] = None,
    default_policy: typing.Optional[builtins.str] = None,
    session_percent: typing.Optional[jsii.Number] = None,
    session_policy: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__216363376007d395389870494823e1b7ea92cc0e6909469dd60dcf0c590f8b9e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83f687fc7787be4b00c893df736871340a1cfa4c8754f5395541bad06c11092c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad6ac1cc657cb03727e9475fe58f521ad724f021e9a686ab395c3ce5e172c260(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd0eda545ddbf8d12c6b5fa423f48997ddd255ddb77ba59b1b3ea6684578af6d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f300582bfd2527b41f89748513f616ca3f392344544f7fac53380c18b70a7ab2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdb48881143b7edfa84451d97f301d404fa8b4787eafb1bab0f5ca773ee75ddd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolLoadShedding]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72b7b8e2d3501a6e1764f678f4198d8639fcaeede8362c4a92a47c8642df6e82(
    *,
    origin: typing.Optional[typing.Union[LoadBalancerPoolNotificationFilterOrigin, typing.Dict[builtins.str, typing.Any]]] = None,
    pool: typing.Optional[typing.Union[LoadBalancerPoolNotificationFilterPool, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a29399290db2668acc77e99314889fe6a60cc82404498f7f3e7db7361505c162(
    *,
    disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    healthy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3049fdcdc53efbfb8f3da5d45e988ebecec226933e6318b09c868344f0a30f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__794ba1f55491e323823daeaee259cd5bb12770f17dec42c3fb19b1f0020abb71(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a31e810cb342aad2609e70d80068cfb4d9577d515db284b0dbace836a10e3a8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f071e2e89c07bc9e62ed1c503d62afcf0ae4a8ae75ef4e8ea873e22293069e11(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterOrigin]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0fa0152c5a545b246061fc5b7651542ff7d4faa88a2343a45d350b67dcd6db1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0079a95b81e37a62827f84e56f94b252538e5ca99ed54761db5acd868b7b2290(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19a02cfea9301552242c157e0b64052be5a45b348a51e874a10de46f99495e15(
    *,
    disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    healthy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__880c2fbbb2fddd1c3f274597504118973d1bd1d8ec68c568edaff0235a433dc8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2edce83b2b3991a8eb4de99d4c8d9bfe6d68200c3b80731f15da1bf1c263ed8e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c60efb860ab554cd4328e186dbbc3b6d02f85a7d779aa159646834c69ab07078(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca9253f53634bf6ad886e8942f86dd0d20d7b88185852fa477bf14d08a2fdcaa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolNotificationFilterPool]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c72c8eb26ee3b133606b600532da2142af1e8f1791717295c41c7778ed236dc(
    *,
    policy: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d75ba71413daca192bad8a16102726dda08fd5a033408ea85dbd3fe05d383f62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61e0a410d1ebd8ccc9fb5aa24f64a14f7b813c0e25e637b4c0b727e3df2ae1c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__221251a3706dee0b19d8623c6786f866e55a00ef603e10c85185b5aa9d9b0766(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginSteering]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fa2420bd66ef218996632a7196f195d33fe95eaa8e0c6af6e1a3921395cd41b(
    *,
    address: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    header: typing.Optional[typing.Union[LoadBalancerPoolOriginsHeader, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
    virtual_network_id: typing.Optional[builtins.str] = None,
    weight: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__341602971ceb0c2249b031606eb62902eaca9fb381b7141e848415dfb8c2272c(
    *,
    host: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52e430333cb1cccb5662d819056cf5ebb3fce0ccb0db3b2b07da7e7f71f85192(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__057f817edbcc3497a1ee4e539fd38cb5497507a5458537d2f50567114a30862d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa25a684f7465ec5a3d108a975bfc1719f9ac2a525d86c74a7decdd33332c34b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOriginsHeader]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b89cf595bdc66572070fd0ac3bf46db245adb30c940ea9e23b30c31f8800297(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__075031e82b917393d5ec53c8833bb3d0decd5c9cad76d85a9296c225edba8bb9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8efa4d8c3ec1c3cf331ccb9c7bba7c4777bef5c9114d5204e6794d1e373b5cf3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8327a70d3f6860970bf1f55b0b1391f066771a7136faf4bf0f2da27e8de0f555(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__677d4893c66570f3d5813e097d63866c7203c4cf298e77c84aa1eace2800ba65(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b301155d9d8ac8030420756216d87f19d458db58ba95091b2e4b6a83198eef2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadBalancerPoolOrigins]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9a95c81bf62ddf8299ca0c8e3f3c110498404b905b5c61881b66c681dd3911(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e93178082349f1ff50ea8227dcf6d8c732258853a13c0ba3749d774b7032a19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ecd93a4e787115ed3f52bb1be6341f9f785c557638452028f00ee74407650a8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5a5fc1fbede8d1b9fd8b05a385a204d60c667f10fa373c9de7f857524991c55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a3d82b6280c3790ca53aa000256dffdd4258a19cf0cede0630d894f17d4f42d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d218d2d2bb51d4af09bae86ea92bd7b89eac7744e8f6efb2f7c6a105615f02e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c070f1d9d759410d13a999a3aec55880a13d209243be37c7988ed2809a29fc4b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2afdb8a3dba053cd228e17329b27bc8a62a0a971ba48bc8b3364ff9c690cee09(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadBalancerPoolOrigins]],
) -> None:
    """Type checking stubs"""
    pass
