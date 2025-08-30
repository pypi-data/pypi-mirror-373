r'''
# `cloudflare_waiting_room_event`

Refer to the Terraform Registry for docs: [`cloudflare_waiting_room_event`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event).
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


class WaitingRoomEvent(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.waitingRoomEvent.WaitingRoomEvent",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event cloudflare_waiting_room_event}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        event_end_time: builtins.str,
        event_start_time: builtins.str,
        name: builtins.str,
        waiting_room_id: builtins.str,
        zone_id: builtins.str,
        custom_page_html: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_session_renewal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        new_users_per_minute: typing.Optional[jsii.Number] = None,
        prequeue_start_time: typing.Optional[builtins.str] = None,
        queueing_method: typing.Optional[builtins.str] = None,
        session_duration: typing.Optional[jsii.Number] = None,
        shuffle_at_event_start: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        suspended: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        total_active_users: typing.Optional[jsii.Number] = None,
        turnstile_action: typing.Optional[builtins.str] = None,
        turnstile_mode: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event cloudflare_waiting_room_event} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param event_end_time: An ISO 8601 timestamp that marks the end of the event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#event_end_time WaitingRoomEvent#event_end_time}
        :param event_start_time: An ISO 8601 timestamp that marks the start of the event. At this time, queued users will be processed with the event's configuration. The start time must be at least one minute before ``event_end_time``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#event_start_time WaitingRoomEvent#event_start_time}
        :param name: A unique name to identify the event. Only alphanumeric characters, hyphens and underscores are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#name WaitingRoomEvent#name}
        :param waiting_room_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#waiting_room_id WaitingRoomEvent#waiting_room_id}.
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#zone_id WaitingRoomEvent#zone_id}
        :param custom_page_html: If set, the event will override the waiting room's ``custom_page_html`` property while it is active. If null, the event will inherit it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#custom_page_html WaitingRoomEvent#custom_page_html}
        :param description: A note that you can use to add more details about the event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#description WaitingRoomEvent#description}
        :param disable_session_renewal: If set, the event will override the waiting room's ``disable_session_renewal`` property while it is active. If null, the event will inherit it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#disable_session_renewal WaitingRoomEvent#disable_session_renewal}
        :param new_users_per_minute: If set, the event will override the waiting room's ``new_users_per_minute`` property while it is active. If null, the event will inherit it. This can only be set if the event's ``total_active_users`` property is also set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#new_users_per_minute WaitingRoomEvent#new_users_per_minute}
        :param prequeue_start_time: An ISO 8601 timestamp that marks when to begin queueing all users before the event starts. The prequeue must start at least five minutes before ``event_start_time``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#prequeue_start_time WaitingRoomEvent#prequeue_start_time}
        :param queueing_method: If set, the event will override the waiting room's ``queueing_method`` property while it is active. If null, the event will inherit it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#queueing_method WaitingRoomEvent#queueing_method}
        :param session_duration: If set, the event will override the waiting room's ``session_duration`` property while it is active. If null, the event will inherit it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#session_duration WaitingRoomEvent#session_duration}
        :param shuffle_at_event_start: If enabled, users in the prequeue will be shuffled randomly at the ``event_start_time``. Requires that ``prequeue_start_time`` is not null. This is useful for situations when many users will join the event prequeue at the same time and you want to shuffle them to ensure fairness. Naturally, it makes the most sense to enable this feature when the ``queueing_method`` during the event respects ordering such as **fifo**, or else the shuffling may be unnecessary. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#shuffle_at_event_start WaitingRoomEvent#shuffle_at_event_start}
        :param suspended: Suspends or allows an event. If set to ``true``, the event is ignored and traffic will be handled based on the waiting room configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#suspended WaitingRoomEvent#suspended}
        :param total_active_users: If set, the event will override the waiting room's ``total_active_users`` property while it is active. If null, the event will inherit it. This can only be set if the event's ``new_users_per_minute`` property is also set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#total_active_users WaitingRoomEvent#total_active_users}
        :param turnstile_action: If set, the event will override the waiting room's ``turnstile_action`` property while it is active. If null, the event will inherit it. Available values: "log", "infinite_queue". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#turnstile_action WaitingRoomEvent#turnstile_action}
        :param turnstile_mode: If set, the event will override the waiting room's ``turnstile_mode`` property while it is active. If null, the event will inherit it. Available values: "off", "invisible", "visible_non_interactive", "visible_managed". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#turnstile_mode WaitingRoomEvent#turnstile_mode}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__470f196609d88d3ea2ed05ccbca600f7162cea0fc71df59da428a3b5737d47b9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = WaitingRoomEventConfig(
            event_end_time=event_end_time,
            event_start_time=event_start_time,
            name=name,
            waiting_room_id=waiting_room_id,
            zone_id=zone_id,
            custom_page_html=custom_page_html,
            description=description,
            disable_session_renewal=disable_session_renewal,
            new_users_per_minute=new_users_per_minute,
            prequeue_start_time=prequeue_start_time,
            queueing_method=queueing_method,
            session_duration=session_duration,
            shuffle_at_event_start=shuffle_at_event_start,
            suspended=suspended,
            total_active_users=total_active_users,
            turnstile_action=turnstile_action,
            turnstile_mode=turnstile_mode,
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
        '''Generates CDKTF code for importing a WaitingRoomEvent resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the WaitingRoomEvent to import.
        :param import_from_id: The id of the existing WaitingRoomEvent that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the WaitingRoomEvent to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f2b63c97cc4e388c6bad2706e148da943a1abda98024171ec13ec8ad9570336)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCustomPageHtml")
    def reset_custom_page_html(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomPageHtml", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisableSessionRenewal")
    def reset_disable_session_renewal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableSessionRenewal", []))

    @jsii.member(jsii_name="resetNewUsersPerMinute")
    def reset_new_users_per_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewUsersPerMinute", []))

    @jsii.member(jsii_name="resetPrequeueStartTime")
    def reset_prequeue_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrequeueStartTime", []))

    @jsii.member(jsii_name="resetQueueingMethod")
    def reset_queueing_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueingMethod", []))

    @jsii.member(jsii_name="resetSessionDuration")
    def reset_session_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionDuration", []))

    @jsii.member(jsii_name="resetShuffleAtEventStart")
    def reset_shuffle_at_event_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShuffleAtEventStart", []))

    @jsii.member(jsii_name="resetSuspended")
    def reset_suspended(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuspended", []))

    @jsii.member(jsii_name="resetTotalActiveUsers")
    def reset_total_active_users(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTotalActiveUsers", []))

    @jsii.member(jsii_name="resetTurnstileAction")
    def reset_turnstile_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTurnstileAction", []))

    @jsii.member(jsii_name="resetTurnstileMode")
    def reset_turnstile_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTurnstileMode", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="customPageHtmlInput")
    def custom_page_html_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customPageHtmlInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="disableSessionRenewalInput")
    def disable_session_renewal_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableSessionRenewalInput"))

    @builtins.property
    @jsii.member(jsii_name="eventEndTimeInput")
    def event_end_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventEndTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="eventStartTimeInput")
    def event_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="newUsersPerMinuteInput")
    def new_users_per_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "newUsersPerMinuteInput"))

    @builtins.property
    @jsii.member(jsii_name="prequeueStartTimeInput")
    def prequeue_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prequeueStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="queueingMethodInput")
    def queueing_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueingMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionDurationInput")
    def session_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sessionDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="shuffleAtEventStartInput")
    def shuffle_at_event_start_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shuffleAtEventStartInput"))

    @builtins.property
    @jsii.member(jsii_name="suspendedInput")
    def suspended_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "suspendedInput"))

    @builtins.property
    @jsii.member(jsii_name="totalActiveUsersInput")
    def total_active_users_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "totalActiveUsersInput"))

    @builtins.property
    @jsii.member(jsii_name="turnstileActionInput")
    def turnstile_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "turnstileActionInput"))

    @builtins.property
    @jsii.member(jsii_name="turnstileModeInput")
    def turnstile_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "turnstileModeInput"))

    @builtins.property
    @jsii.member(jsii_name="waitingRoomIdInput")
    def waiting_room_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "waitingRoomIdInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customPageHtml")
    def custom_page_html(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customPageHtml"))

    @custom_page_html.setter
    def custom_page_html(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__300683805346e75bd0911b1cfde5c4e76c1853f94a8b69f66e61ec137a25bd12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customPageHtml", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__126c955f64f38efd2b21ef584cecfcf017ee90d05e42f66a40633ff5b399ae85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableSessionRenewal")
    def disable_session_renewal(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableSessionRenewal"))

    @disable_session_renewal.setter
    def disable_session_renewal(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f752f60e93417202a4c0220cd0ca5d7f17d2e5980d022370c1bc8947ec5e3b96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableSessionRenewal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eventEndTime")
    def event_end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventEndTime"))

    @event_end_time.setter
    def event_end_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fbe8d609c9e266d0884f58d6d05352b7d4553d178a633297c909857a7b3ef4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventEndTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eventStartTime")
    def event_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventStartTime"))

    @event_start_time.setter
    def event_start_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9b8668fd539ed5d9dfc0fc1934e7e2daff3212ae0731d671313fbde6ba54ea3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventStartTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88969a7c2e8e0447e2dc8406fd9dff1ce567a7dc673bf25ab42e1bcae01a0e1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newUsersPerMinute")
    def new_users_per_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "newUsersPerMinute"))

    @new_users_per_minute.setter
    def new_users_per_minute(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6609f0ff00809e9977a166ed7482a31a70ecb94f2a35d8acdfd3a77d7ea521a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newUsersPerMinute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prequeueStartTime")
    def prequeue_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prequeueStartTime"))

    @prequeue_start_time.setter
    def prequeue_start_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b37241b3d9d3c94d2fedf3abd6871bc7301ac848adf1d91430d7f95e00f2184a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prequeueStartTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueingMethod")
    def queueing_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueingMethod"))

    @queueing_method.setter
    def queueing_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1f6535d775453a96f73332ebcecdc1a0022547d6e9aa670502c786337797073)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueingMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionDuration")
    def session_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sessionDuration"))

    @session_duration.setter
    def session_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__238d25de30a21a9eb4d1195ea0ba8c139dc0ac47d324e13111600ee34265bdbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shuffleAtEventStart")
    def shuffle_at_event_start(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shuffleAtEventStart"))

    @shuffle_at_event_start.setter
    def shuffle_at_event_start(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a7792621e5341cf2470873d881e32e39573b968d73280cecc3a578981975c64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shuffleAtEventStart", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="suspended")
    def suspended(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "suspended"))

    @suspended.setter
    def suspended(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e9c396ec60dc1154d1c2da16b6ca868bef8b67bc02f1f046c6253040d4d083b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suspended", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalActiveUsers")
    def total_active_users(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalActiveUsers"))

    @total_active_users.setter
    def total_active_users(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ea6e5d9a673dcfe0fe0205f68c798c469df4838ade2f44dd331fc53cb44107e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalActiveUsers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="turnstileAction")
    def turnstile_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "turnstileAction"))

    @turnstile_action.setter
    def turnstile_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3a82f5cfee37a1d9620951f13288820df34599a70fcbaf7c03181b3e787bbff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "turnstileAction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="turnstileMode")
    def turnstile_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "turnstileMode"))

    @turnstile_mode.setter
    def turnstile_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbf913565536fa4cf7b0c0e481f7f499d206cb082a494694ef535de428d52bbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "turnstileMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="waitingRoomId")
    def waiting_room_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "waitingRoomId"))

    @waiting_room_id.setter
    def waiting_room_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ab762d11d282bc5819acae9e97c76bbac7f487c4b55e8194c16b62b2e9aee91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waitingRoomId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4ef88db3881308893e899f54a64faa6c253e2879a2a55c252b1e138e40f6d30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.waitingRoomEvent.WaitingRoomEventConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "event_end_time": "eventEndTime",
        "event_start_time": "eventStartTime",
        "name": "name",
        "waiting_room_id": "waitingRoomId",
        "zone_id": "zoneId",
        "custom_page_html": "customPageHtml",
        "description": "description",
        "disable_session_renewal": "disableSessionRenewal",
        "new_users_per_minute": "newUsersPerMinute",
        "prequeue_start_time": "prequeueStartTime",
        "queueing_method": "queueingMethod",
        "session_duration": "sessionDuration",
        "shuffle_at_event_start": "shuffleAtEventStart",
        "suspended": "suspended",
        "total_active_users": "totalActiveUsers",
        "turnstile_action": "turnstileAction",
        "turnstile_mode": "turnstileMode",
    },
)
class WaitingRoomEventConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        event_end_time: builtins.str,
        event_start_time: builtins.str,
        name: builtins.str,
        waiting_room_id: builtins.str,
        zone_id: builtins.str,
        custom_page_html: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_session_renewal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        new_users_per_minute: typing.Optional[jsii.Number] = None,
        prequeue_start_time: typing.Optional[builtins.str] = None,
        queueing_method: typing.Optional[builtins.str] = None,
        session_duration: typing.Optional[jsii.Number] = None,
        shuffle_at_event_start: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        suspended: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        total_active_users: typing.Optional[jsii.Number] = None,
        turnstile_action: typing.Optional[builtins.str] = None,
        turnstile_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param event_end_time: An ISO 8601 timestamp that marks the end of the event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#event_end_time WaitingRoomEvent#event_end_time}
        :param event_start_time: An ISO 8601 timestamp that marks the start of the event. At this time, queued users will be processed with the event's configuration. The start time must be at least one minute before ``event_end_time``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#event_start_time WaitingRoomEvent#event_start_time}
        :param name: A unique name to identify the event. Only alphanumeric characters, hyphens and underscores are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#name WaitingRoomEvent#name}
        :param waiting_room_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#waiting_room_id WaitingRoomEvent#waiting_room_id}.
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#zone_id WaitingRoomEvent#zone_id}
        :param custom_page_html: If set, the event will override the waiting room's ``custom_page_html`` property while it is active. If null, the event will inherit it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#custom_page_html WaitingRoomEvent#custom_page_html}
        :param description: A note that you can use to add more details about the event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#description WaitingRoomEvent#description}
        :param disable_session_renewal: If set, the event will override the waiting room's ``disable_session_renewal`` property while it is active. If null, the event will inherit it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#disable_session_renewal WaitingRoomEvent#disable_session_renewal}
        :param new_users_per_minute: If set, the event will override the waiting room's ``new_users_per_minute`` property while it is active. If null, the event will inherit it. This can only be set if the event's ``total_active_users`` property is also set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#new_users_per_minute WaitingRoomEvent#new_users_per_minute}
        :param prequeue_start_time: An ISO 8601 timestamp that marks when to begin queueing all users before the event starts. The prequeue must start at least five minutes before ``event_start_time``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#prequeue_start_time WaitingRoomEvent#prequeue_start_time}
        :param queueing_method: If set, the event will override the waiting room's ``queueing_method`` property while it is active. If null, the event will inherit it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#queueing_method WaitingRoomEvent#queueing_method}
        :param session_duration: If set, the event will override the waiting room's ``session_duration`` property while it is active. If null, the event will inherit it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#session_duration WaitingRoomEvent#session_duration}
        :param shuffle_at_event_start: If enabled, users in the prequeue will be shuffled randomly at the ``event_start_time``. Requires that ``prequeue_start_time`` is not null. This is useful for situations when many users will join the event prequeue at the same time and you want to shuffle them to ensure fairness. Naturally, it makes the most sense to enable this feature when the ``queueing_method`` during the event respects ordering such as **fifo**, or else the shuffling may be unnecessary. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#shuffle_at_event_start WaitingRoomEvent#shuffle_at_event_start}
        :param suspended: Suspends or allows an event. If set to ``true``, the event is ignored and traffic will be handled based on the waiting room configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#suspended WaitingRoomEvent#suspended}
        :param total_active_users: If set, the event will override the waiting room's ``total_active_users`` property while it is active. If null, the event will inherit it. This can only be set if the event's ``new_users_per_minute`` property is also set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#total_active_users WaitingRoomEvent#total_active_users}
        :param turnstile_action: If set, the event will override the waiting room's ``turnstile_action`` property while it is active. If null, the event will inherit it. Available values: "log", "infinite_queue". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#turnstile_action WaitingRoomEvent#turnstile_action}
        :param turnstile_mode: If set, the event will override the waiting room's ``turnstile_mode`` property while it is active. If null, the event will inherit it. Available values: "off", "invisible", "visible_non_interactive", "visible_managed". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#turnstile_mode WaitingRoomEvent#turnstile_mode}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fa2aa1e1c796917fa845969f3faf8e2a4276403ad85fc498ed39f37fa9a5e5d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument event_end_time", value=event_end_time, expected_type=type_hints["event_end_time"])
            check_type(argname="argument event_start_time", value=event_start_time, expected_type=type_hints["event_start_time"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument waiting_room_id", value=waiting_room_id, expected_type=type_hints["waiting_room_id"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument custom_page_html", value=custom_page_html, expected_type=type_hints["custom_page_html"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_session_renewal", value=disable_session_renewal, expected_type=type_hints["disable_session_renewal"])
            check_type(argname="argument new_users_per_minute", value=new_users_per_minute, expected_type=type_hints["new_users_per_minute"])
            check_type(argname="argument prequeue_start_time", value=prequeue_start_time, expected_type=type_hints["prequeue_start_time"])
            check_type(argname="argument queueing_method", value=queueing_method, expected_type=type_hints["queueing_method"])
            check_type(argname="argument session_duration", value=session_duration, expected_type=type_hints["session_duration"])
            check_type(argname="argument shuffle_at_event_start", value=shuffle_at_event_start, expected_type=type_hints["shuffle_at_event_start"])
            check_type(argname="argument suspended", value=suspended, expected_type=type_hints["suspended"])
            check_type(argname="argument total_active_users", value=total_active_users, expected_type=type_hints["total_active_users"])
            check_type(argname="argument turnstile_action", value=turnstile_action, expected_type=type_hints["turnstile_action"])
            check_type(argname="argument turnstile_mode", value=turnstile_mode, expected_type=type_hints["turnstile_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "event_end_time": event_end_time,
            "event_start_time": event_start_time,
            "name": name,
            "waiting_room_id": waiting_room_id,
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
        if custom_page_html is not None:
            self._values["custom_page_html"] = custom_page_html
        if description is not None:
            self._values["description"] = description
        if disable_session_renewal is not None:
            self._values["disable_session_renewal"] = disable_session_renewal
        if new_users_per_minute is not None:
            self._values["new_users_per_minute"] = new_users_per_minute
        if prequeue_start_time is not None:
            self._values["prequeue_start_time"] = prequeue_start_time
        if queueing_method is not None:
            self._values["queueing_method"] = queueing_method
        if session_duration is not None:
            self._values["session_duration"] = session_duration
        if shuffle_at_event_start is not None:
            self._values["shuffle_at_event_start"] = shuffle_at_event_start
        if suspended is not None:
            self._values["suspended"] = suspended
        if total_active_users is not None:
            self._values["total_active_users"] = total_active_users
        if turnstile_action is not None:
            self._values["turnstile_action"] = turnstile_action
        if turnstile_mode is not None:
            self._values["turnstile_mode"] = turnstile_mode

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
    def event_end_time(self) -> builtins.str:
        '''An ISO 8601 timestamp that marks the end of the event.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#event_end_time WaitingRoomEvent#event_end_time}
        '''
        result = self._values.get("event_end_time")
        assert result is not None, "Required property 'event_end_time' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def event_start_time(self) -> builtins.str:
        '''An ISO 8601 timestamp that marks the start of the event.

        At this time, queued users will be processed with the event's configuration. The start time must be at least one minute before ``event_end_time``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#event_start_time WaitingRoomEvent#event_start_time}
        '''
        result = self._values.get("event_start_time")
        assert result is not None, "Required property 'event_start_time' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''A unique name to identify the event. Only alphanumeric characters, hyphens and underscores are allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#name WaitingRoomEvent#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def waiting_room_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#waiting_room_id WaitingRoomEvent#waiting_room_id}.'''
        result = self._values.get("waiting_room_id")
        assert result is not None, "Required property 'waiting_room_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#zone_id WaitingRoomEvent#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_page_html(self) -> typing.Optional[builtins.str]:
        '''If set, the event will override the waiting room's ``custom_page_html`` property while it is active.

        If null, the event will inherit it.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#custom_page_html WaitingRoomEvent#custom_page_html}
        '''
        result = self._values.get("custom_page_html")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A note that you can use to add more details about the event.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#description WaitingRoomEvent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_session_renewal(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, the event will override the waiting room's ``disable_session_renewal`` property while it is active.

        If null, the event will inherit it.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#disable_session_renewal WaitingRoomEvent#disable_session_renewal}
        '''
        result = self._values.get("disable_session_renewal")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def new_users_per_minute(self) -> typing.Optional[jsii.Number]:
        '''If set, the event will override the waiting room's ``new_users_per_minute`` property while it is active.

        If null, the event will inherit it. This can only be set if the event's ``total_active_users`` property is also set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#new_users_per_minute WaitingRoomEvent#new_users_per_minute}
        '''
        result = self._values.get("new_users_per_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def prequeue_start_time(self) -> typing.Optional[builtins.str]:
        '''An ISO 8601 timestamp that marks when to begin queueing all users before the event starts.

        The prequeue must start at least five minutes before ``event_start_time``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#prequeue_start_time WaitingRoomEvent#prequeue_start_time}
        '''
        result = self._values.get("prequeue_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queueing_method(self) -> typing.Optional[builtins.str]:
        '''If set, the event will override the waiting room's ``queueing_method`` property while it is active.

        If null, the event will inherit it.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#queueing_method WaitingRoomEvent#queueing_method}
        '''
        result = self._values.get("queueing_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_duration(self) -> typing.Optional[jsii.Number]:
        '''If set, the event will override the waiting room's ``session_duration`` property while it is active.

        If null, the event will inherit it.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#session_duration WaitingRoomEvent#session_duration}
        '''
        result = self._values.get("session_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def shuffle_at_event_start(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If enabled, users in the prequeue will be shuffled randomly at the ``event_start_time``.

        Requires that ``prequeue_start_time`` is not null. This is useful for situations when many users will join the event prequeue at the same time and you want to shuffle them to ensure fairness. Naturally, it makes the most sense to enable this feature when the ``queueing_method`` during the event respects ordering such as **fifo**, or else the shuffling may be unnecessary.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#shuffle_at_event_start WaitingRoomEvent#shuffle_at_event_start}
        '''
        result = self._values.get("shuffle_at_event_start")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def suspended(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Suspends or allows an event.

        If set to ``true``, the event is ignored and traffic will be handled based on the waiting room configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#suspended WaitingRoomEvent#suspended}
        '''
        result = self._values.get("suspended")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def total_active_users(self) -> typing.Optional[jsii.Number]:
        '''If set, the event will override the waiting room's ``total_active_users`` property while it is active.

        If null, the event will inherit it. This can only be set if the event's ``new_users_per_minute`` property is also set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#total_active_users WaitingRoomEvent#total_active_users}
        '''
        result = self._values.get("total_active_users")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def turnstile_action(self) -> typing.Optional[builtins.str]:
        '''If set, the event will override the waiting room's ``turnstile_action`` property while it is active.

        If null, the event will inherit it.
        Available values: "log", "infinite_queue".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#turnstile_action WaitingRoomEvent#turnstile_action}
        '''
        result = self._values.get("turnstile_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def turnstile_mode(self) -> typing.Optional[builtins.str]:
        '''If set, the event will override the waiting room's ``turnstile_mode`` property while it is active.

        If null, the event will inherit it.
        Available values: "off", "invisible", "visible_non_interactive", "visible_managed".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room_event#turnstile_mode WaitingRoomEvent#turnstile_mode}
        '''
        result = self._values.get("turnstile_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaitingRoomEventConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "WaitingRoomEvent",
    "WaitingRoomEventConfig",
]

publication.publish()

def _typecheckingstub__470f196609d88d3ea2ed05ccbca600f7162cea0fc71df59da428a3b5737d47b9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    event_end_time: builtins.str,
    event_start_time: builtins.str,
    name: builtins.str,
    waiting_room_id: builtins.str,
    zone_id: builtins.str,
    custom_page_html: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    disable_session_renewal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    new_users_per_minute: typing.Optional[jsii.Number] = None,
    prequeue_start_time: typing.Optional[builtins.str] = None,
    queueing_method: typing.Optional[builtins.str] = None,
    session_duration: typing.Optional[jsii.Number] = None,
    shuffle_at_event_start: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    suspended: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    total_active_users: typing.Optional[jsii.Number] = None,
    turnstile_action: typing.Optional[builtins.str] = None,
    turnstile_mode: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__0f2b63c97cc4e388c6bad2706e148da943a1abda98024171ec13ec8ad9570336(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__300683805346e75bd0911b1cfde5c4e76c1853f94a8b69f66e61ec137a25bd12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__126c955f64f38efd2b21ef584cecfcf017ee90d05e42f66a40633ff5b399ae85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f752f60e93417202a4c0220cd0ca5d7f17d2e5980d022370c1bc8947ec5e3b96(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fbe8d609c9e266d0884f58d6d05352b7d4553d178a633297c909857a7b3ef4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9b8668fd539ed5d9dfc0fc1934e7e2daff3212ae0731d671313fbde6ba54ea3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88969a7c2e8e0447e2dc8406fd9dff1ce567a7dc673bf25ab42e1bcae01a0e1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6609f0ff00809e9977a166ed7482a31a70ecb94f2a35d8acdfd3a77d7ea521a0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b37241b3d9d3c94d2fedf3abd6871bc7301ac848adf1d91430d7f95e00f2184a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1f6535d775453a96f73332ebcecdc1a0022547d6e9aa670502c786337797073(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__238d25de30a21a9eb4d1195ea0ba8c139dc0ac47d324e13111600ee34265bdbf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a7792621e5341cf2470873d881e32e39573b968d73280cecc3a578981975c64(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e9c396ec60dc1154d1c2da16b6ca868bef8b67bc02f1f046c6253040d4d083b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ea6e5d9a673dcfe0fe0205f68c798c469df4838ade2f44dd331fc53cb44107e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3a82f5cfee37a1d9620951f13288820df34599a70fcbaf7c03181b3e787bbff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbf913565536fa4cf7b0c0e481f7f499d206cb082a494694ef535de428d52bbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ab762d11d282bc5819acae9e97c76bbac7f487c4b55e8194c16b62b2e9aee91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4ef88db3881308893e899f54a64faa6c253e2879a2a55c252b1e138e40f6d30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fa2aa1e1c796917fa845969f3faf8e2a4276403ad85fc498ed39f37fa9a5e5d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    event_end_time: builtins.str,
    event_start_time: builtins.str,
    name: builtins.str,
    waiting_room_id: builtins.str,
    zone_id: builtins.str,
    custom_page_html: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    disable_session_renewal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    new_users_per_minute: typing.Optional[jsii.Number] = None,
    prequeue_start_time: typing.Optional[builtins.str] = None,
    queueing_method: typing.Optional[builtins.str] = None,
    session_duration: typing.Optional[jsii.Number] = None,
    shuffle_at_event_start: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    suspended: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    total_active_users: typing.Optional[jsii.Number] = None,
    turnstile_action: typing.Optional[builtins.str] = None,
    turnstile_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
