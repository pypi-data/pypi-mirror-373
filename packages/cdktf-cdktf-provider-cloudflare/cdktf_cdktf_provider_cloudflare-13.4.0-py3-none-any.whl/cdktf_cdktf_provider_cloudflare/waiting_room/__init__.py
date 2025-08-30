r'''
# `cloudflare_waiting_room`

Refer to the Terraform Registry for docs: [`cloudflare_waiting_room`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room).
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


class WaitingRoom(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.waitingRoom.WaitingRoom",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room cloudflare_waiting_room}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        host: builtins.str,
        name: builtins.str,
        new_users_per_minute: jsii.Number,
        total_active_users: jsii.Number,
        zone_id: builtins.str,
        additional_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WaitingRoomAdditionalRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
        cookie_attributes: typing.Optional[typing.Union["WaitingRoomCookieAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        cookie_suffix: typing.Optional[builtins.str] = None,
        custom_page_html: typing.Optional[builtins.str] = None,
        default_template_language: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_session_renewal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled_origin_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        json_response_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        path: typing.Optional[builtins.str] = None,
        queue_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        queueing_method: typing.Optional[builtins.str] = None,
        queueing_status_code: typing.Optional[jsii.Number] = None,
        session_duration: typing.Optional[jsii.Number] = None,
        suspended: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room cloudflare_waiting_room} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param host: The host name to which the waiting room will be applied (no wildcards). Please do not include the scheme (http:// or https://). The host and path combination must be unique. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#host WaitingRoom#host}
        :param name: A unique name to identify the waiting room. Only alphanumeric characters, hyphens and underscores are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#name WaitingRoom#name}
        :param new_users_per_minute: Sets the number of new users that will be let into the route every minute. This value is used as baseline for the number of users that are let in per minute. So it is possible that there is a little more or little less traffic coming to the route based on the traffic patterns at that time around the world. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#new_users_per_minute WaitingRoom#new_users_per_minute}
        :param total_active_users: Sets the total number of active user sessions on the route at a point in time. A route is a combination of host and path on which a waiting room is available. This value is used as a baseline for the total number of active user sessions on the route. It is possible to have a situation where there are more or less active users sessions on the route based on the traffic patterns at that time around the world. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#total_active_users WaitingRoom#total_active_users}
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#zone_id WaitingRoom#zone_id}
        :param additional_routes: Only available for the Waiting Room Advanced subscription. Additional hostname and path combinations to which this waiting room will be applied. There is an implied wildcard at the end of the path. The hostname and path combination must be unique to this and all other waiting rooms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#additional_routes WaitingRoom#additional_routes}
        :param cookie_attributes: Configures cookie attributes for the waiting room cookie. This encrypted cookie stores a user's status in the waiting room, such as queue position. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#cookie_attributes WaitingRoom#cookie_attributes}
        :param cookie_suffix: Appends a '_' + a custom suffix to the end of Cloudflare Waiting Room's cookie name(__cf_waitingroom). If ``cookie_suffix`` is "abcd", the cookie name will be ``__cf_waitingroom_abcd``. This field is required if using ``additional_routes``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#cookie_suffix WaitingRoom#cookie_suffix}
        :param custom_page_html: Only available for the Waiting Room Advanced subscription. This is a template html file that will be rendered at the edge. If no custom_page_html is provided, the default waiting room will be used. The template is based on mustache ( https://mustache.github.io/ ). There are several variables that are evaluated by the Cloudflare edge: 1. {{``waitTimeKnown``}} Acts like a boolean value that indicates the behavior to take when wait time is not available, for instance when queue_all is **true**. 2. {{``waitTimeFormatted``}} Estimated wait time for the user. For example, five minutes. Alternatively, you can use: 3. {{``waitTime``}} Number of minutes of estimated wait for a user. 4. {{``waitTimeHours``}} Number of hours of estimated wait for a user (``Math.floor(waitTime/60)``). 5. {{``waitTimeHourMinutes``}} Number of minutes above the ``waitTimeHours`` value (``waitTime%60``). 6. {{``queueIsFull``}} Changes to **true** when no more people can be added to the queue. To view the full list of variables, look at the ``cfWaitingRoom`` object described under the ``json_response_enabled`` property in other Waiting Room API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#custom_page_html WaitingRoom#custom_page_html}
        :param default_template_language: The language of the default page template. If no default_template_language is provided, then ``en-US`` (English) will be used. Available values: "en-US", "es-ES", "de-DE", "fr-FR", "it-IT", "ja-JP", "ko-KR", "pt-BR", "zh-CN", "zh-TW", "nl-NL", "pl-PL", "id-ID", "tr-TR", "ar-EG", "ru-RU", "fa-IR", "bg-BG", "hr-HR", "cs-CZ", "da-DK", "fi-FI", "lt-LT", "ms-MY", "nb-NO", "ro-RO", "el-GR", "he-IL", "hi-IN", "hu-HU", "sr-BA", "sk-SK", "sl-SI", "sv-SE", "tl-PH", "th-TH", "uk-UA", "vi-VN". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#default_template_language WaitingRoom#default_template_language}
        :param description: A note that you can use to add more details about the waiting room. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#description WaitingRoom#description}
        :param disable_session_renewal: Only available for the Waiting Room Advanced subscription. Disables automatic renewal of session cookies. If ``true``, an accepted user will have session_duration minutes to browse the site. After that, they will have to go through the waiting room again. If ``false``, a user's session cookie will be automatically renewed on every request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#disable_session_renewal WaitingRoom#disable_session_renewal}
        :param enabled_origin_commands: A list of enabled origin commands. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#enabled_origin_commands WaitingRoom#enabled_origin_commands}
        :param json_response_enabled: Only available for the Waiting Room Advanced subscription. If ``true``, requests to the waiting room with the header ``Accept: application/json`` will receive a JSON response object with information on the user's status in the waiting room as opposed to the configured static HTML page. This JSON response object has one property ``cfWaitingRoom`` which is an object containing the following fields: 1. ``inWaitingRoom``: Boolean indicating if the user is in the waiting room (always **true**). 2. ``waitTimeKnown``: Boolean indicating if the current estimated wait times are accurate. If **false**, they are not available. 3. ``waitTime``: Valid only when ``waitTimeKnown`` is **true**. Integer indicating the current estimated time in minutes the user will wait in the waiting room. When ``queueingMethod`` is **random**, this is set to ``waitTime50Percentile``. 4. ``waitTime25Percentile``: Valid only when ``queueingMethod`` is **random** and ``waitTimeKnown`` is **true**. Integer indicating the current estimated maximum wait time for the 25% of users that gain entry the fastest (25th percentile). 5. ``waitTime50Percentile``: Valid only when ``queueingMethod`` is **random** and ``waitTimeKnown`` is **true**. Integer indicating the current estimated maximum wait time for the 50% of users that gain entry the fastest (50th percentile). In other words, half of the queued users are expected to let into the origin website before ``waitTime50Percentile`` and half are expected to be let in after it. 6. ``waitTime75Percentile``: Valid only when ``queueingMethod`` is **random** and ``waitTimeKnown`` is **true**. Integer indicating the current estimated maximum wait time for the 75% of users that gain entry the fastest (75th percentile). 7. ``waitTimeFormatted``: String displaying the ``waitTime`` formatted in English for users. If ``waitTimeKnown`` is **false**, ``waitTimeFormatted`` will display **unavailable**. 8. ``queueIsFull``: Boolean indicating if the waiting room's queue is currently full and not accepting new users at the moment. 9. ``queueAll``: Boolean indicating if all users will be queued in the waiting room and no one will be let into the origin website. 10. ``lastUpdated``: String displaying the timestamp as an ISO 8601 string of the user's last attempt to leave the waiting room and be let into the origin website. The user is able to make another attempt after ``refreshIntervalSeconds`` past this time. If the user makes a request too soon, it will be ignored and ``lastUpdated`` will not change. 11. ``refreshIntervalSeconds``: Integer indicating the number of seconds after ``lastUpdated`` until the user is able to make another attempt to leave the waiting room and be let into the origin website. When the ``queueingMethod`` is ``reject``, there is no specified refresh time —_it will always be **zero**. 12. ``queueingMethod``: The queueing method currently used by the waiting room. It is either **fifo**, **random**, **passthrough**, or **reject**. 13. ``isFIFOQueue``: Boolean indicating if the waiting room uses a FIFO (First-In-First-Out) queue. 14. ``isRandomQueue``: Boolean indicating if the waiting room uses a Random queue where users gain access randomly. 15. ``isPassthroughQueue``: Boolean indicating if the waiting room uses a passthrough queue. Keep in mind that when passthrough is enabled, this JSON response will only exist when ``queueAll`` is **true** or ``isEventPrequeueing`` is **true** because in all other cases requests will go directly to the origin. 16. ``isRejectQueue``: Boolean indicating if the waiting room uses a reject queue. 17. ``isEventActive``: Boolean indicating if an event is currently occurring. Events are able to change a waiting room's behavior during a specified period of time. For additional information, look at the event properties ``prequeue_start_time``, ``event_start_time``, and ``event_end_time`` in the documentation for creating waiting room events. Events are considered active between these start and end times, as well as during the prequeueing period if it exists. 18. ``isEventPrequeueing``: Valid only when ``isEventActive`` is **true**. Boolean indicating if an event is currently prequeueing users before it starts. 19. ``timeUntilEventStart``: Valid only when ``isEventPrequeueing`` is **true**. Integer indicating the number of minutes until the event starts. 20. ``timeUntilEventStartFormatted``: String displaying the ``timeUntilEventStart`` formatted in English for users. If ``isEventPrequeueing`` is **false**, ``timeUntilEventStartFormatted`` will display **unavailable**. 21. ``timeUntilEventEnd``: Valid only when ``isEventActive`` is **true**. Integer indicating the number of minutes until the event ends. 22. ``timeUntilEventEndFormatted``: String displaying the ``timeUntilEventEnd`` formatted in English for users. If ``isEventActive`` is **false**, ``timeUntilEventEndFormatted`` will display **unavailable**. 23. ``shuffleAtEventStart``: Valid only when ``isEventActive`` is **true**. Boolean indicating if the users in the prequeue are shuffled randomly when the event starts. 24. ``turnstile``: Empty when turnstile isn't enabled. String displaying an html tag to display the Turnstile widget. Please add the ``{{{turnstile}}}`` tag to the ``custom_html`` template to ensure the Turnstile widget appears. 25. ``infiniteQueue``: Boolean indicating whether the response is for a user in the infinite queue. An example cURL to a waiting room could be:: curl -X GET "https://example.com/waitingroom" \\ -H "Accept: application/json" If ``json_response_enabled`` is **true** and the request hits the waiting room, an example JSON response when ``queueingMethod`` is **fifo** and no event is active could be:: { "cfWaitingRoom": { "inWaitingRoom": true, "waitTimeKnown": true, "waitTime": 10, "waitTime25Percentile": 0, "waitTime50Percentile": 0, "waitTime75Percentile": 0, "waitTimeFormatted": "10 minutes", "queueIsFull": false, "queueAll": false, "lastUpdated": "2020-08-03T23:46:00.000Z", "refreshIntervalSeconds": 20, "queueingMethod": "fifo", "isFIFOQueue": true, "isRandomQueue": false, "isPassthroughQueue": false, "isRejectQueue": false, "isEventActive": false, "isEventPrequeueing": false, "timeUntilEventStart": 0, "timeUntilEventStartFormatted": "unavailable", "timeUntilEventEnd": 0, "timeUntilEventEndFormatted": "unavailable", "shuffleAtEventStart": false } } If ``json_response_enabled`` is **true** and the request hits the waiting room, an example JSON response when ``queueingMethod`` is **random** and an event is active could be:: { "cfWaitingRoom": { "inWaitingRoom": true, "waitTimeKnown": true, "waitTime": 10, "waitTime25Percentile": 5, "waitTime50Percentile": 10, "waitTime75Percentile": 15, "waitTimeFormatted": "5 minutes to 15 minutes", "queueIsFull": false, "queueAll": false, "lastUpdated": "2020-08-03T23:46:00.000Z", "refreshIntervalSeconds": 20, "queueingMethod": "random", "isFIFOQueue": false, "isRandomQueue": true, "isPassthroughQueue": false, "isRejectQueue": false, "isEventActive": true, "isEventPrequeueing": false, "timeUntilEventStart": 0, "timeUntilEventStartFormatted": "unavailable", "timeUntilEventEnd": 15, "timeUntilEventEndFormatted": "15 minutes", "shuffleAtEventStart": true } } Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#json_response_enabled WaitingRoom#json_response_enabled}
        :param path: Sets the path within the host to enable the waiting room on. The waiting room will be enabled for all subpaths as well. If there are two waiting rooms on the same subpath, the waiting room for the most specific path will be chosen. Wildcards and query parameters are not supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#path WaitingRoom#path}
        :param queue_all: If queue_all is ``true``, all the traffic that is coming to a route will be sent to the waiting room. No new traffic can get to the route once this field is set and estimated time will become unavailable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#queue_all WaitingRoom#queue_all}
        :param queueing_method: Sets the queueing method used by the waiting room. Changing this parameter from the **default** queueing method is only available for the Waiting Room Advanced subscription. Regardless of the queueing method, if ``queue_all`` is enabled or an event is prequeueing, users in the waiting room will not be accepted to the origin. These users will always see a waiting room page that refreshes automatically. The valid queueing methods are: 1. ``fifo`` **(default)**: First-In-First-Out queue where customers gain access in the order they arrived. 2. ``random``: Random queue where customers gain access randomly, regardless of arrival time. 3. ``passthrough``: Users will pass directly through the waiting room and into the origin website. As a result, any configured limits will not be respected while this is enabled. This method can be used as an alternative to disabling a waiting room (with ``suspended``) so that analytics are still reported. This can be used if you wish to allow all traffic normally, but want to restrict traffic during a waiting room event, or vice versa. 4. ``reject``: Users will be immediately rejected from the waiting room. As a result, no users will reach the origin website while this is enabled. This can be used if you wish to reject all traffic while performing maintenance, block traffic during a specified period of time (an event), or block traffic while events are not occurring. Consider a waiting room used for vaccine distribution that only allows traffic during sign-up events, and otherwise blocks all traffic. For this case, the waiting room uses ``reject``, and its events override this with ``fifo``, ``random``, or ``passthrough``. When this queueing method is enabled and neither ``queueAll`` is enabled nor an event is prequeueing, the waiting room page **will not refresh automatically**. Available values: "fifo", "random", "passthrough", "reject". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#queueing_method WaitingRoom#queueing_method}
        :param queueing_status_code: HTTP status code returned to a user while in the queue. Available values: 200, 202, 429. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#queueing_status_code WaitingRoom#queueing_status_code}
        :param session_duration: Lifetime of a cookie (in minutes) set by Cloudflare for users who get access to the route. If a user is not seen by Cloudflare again in that time period, they will be treated as a new user that visits the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#session_duration WaitingRoom#session_duration}
        :param suspended: Suspends or allows traffic going to the waiting room. If set to ``true``, the traffic will not go to the waiting room. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#suspended WaitingRoom#suspended}
        :param turnstile_action: Which action to take when a bot is detected using Turnstile. ``log`` will have no impact on queueing behavior, simply keeping track of how many bots are detected in Waiting Room Analytics. ``infinite_queue`` will send bots to a false queueing state, where they will never reach your origin. ``infinite_queue`` requires Advanced Waiting Room. Available values: "log", "infinite_queue". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#turnstile_action WaitingRoom#turnstile_action}
        :param turnstile_mode: Which Turnstile widget type to use for detecting bot traffic. See `the Turnstile documentation <https://developers.cloudflare.com/turnstile/concepts/widget/#widget-types>`_ for the definitions of these widget types. Set to ``off`` to disable the Turnstile integration entirely. Setting this to anything other than ``off`` or ``invisible`` requires Advanced Waiting Room. Available values: "off", "invisible", "visible_non_interactive", "visible_managed". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#turnstile_mode WaitingRoom#turnstile_mode}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d737128371b91dc67e76dc498443dc339a660aa9509d247243c49a6c9f5a6d80)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = WaitingRoomConfig(
            host=host,
            name=name,
            new_users_per_minute=new_users_per_minute,
            total_active_users=total_active_users,
            zone_id=zone_id,
            additional_routes=additional_routes,
            cookie_attributes=cookie_attributes,
            cookie_suffix=cookie_suffix,
            custom_page_html=custom_page_html,
            default_template_language=default_template_language,
            description=description,
            disable_session_renewal=disable_session_renewal,
            enabled_origin_commands=enabled_origin_commands,
            json_response_enabled=json_response_enabled,
            path=path,
            queue_all=queue_all,
            queueing_method=queueing_method,
            queueing_status_code=queueing_status_code,
            session_duration=session_duration,
            suspended=suspended,
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
        '''Generates CDKTF code for importing a WaitingRoom resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the WaitingRoom to import.
        :param import_from_id: The id of the existing WaitingRoom that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the WaitingRoom to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c8ba1a8303d4f5bf6554fd049a351613fed75363ba1b8207380deee3bce37c6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAdditionalRoutes")
    def put_additional_routes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WaitingRoomAdditionalRoutes", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cf4353ea8ebcd430fd9bd55b8073b7d188c7ae9fea814051bc1ae54f12b393c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAdditionalRoutes", [value]))

    @jsii.member(jsii_name="putCookieAttributes")
    def put_cookie_attributes(
        self,
        *,
        samesite: typing.Optional[builtins.str] = None,
        secure: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param samesite: Configures the SameSite attribute on the waiting room cookie. Value ``auto`` will be translated to ``lax`` or ``none`` depending if **Always Use HTTPS** is enabled. Note that when using value ``none``, the secure attribute cannot be set to ``never``. Available values: "auto", "lax", "none", "strict". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#samesite WaitingRoom#samesite}
        :param secure: Configures the Secure attribute on the waiting room cookie. Value ``always`` indicates that the Secure attribute will be set in the Set-Cookie header, ``never`` indicates that the Secure attribute will not be set, and ``auto`` will set the Secure attribute depending if **Always Use HTTPS** is enabled. Available values: "auto", "always", "never". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#secure WaitingRoom#secure}
        '''
        value = WaitingRoomCookieAttributes(samesite=samesite, secure=secure)

        return typing.cast(None, jsii.invoke(self, "putCookieAttributes", [value]))

    @jsii.member(jsii_name="resetAdditionalRoutes")
    def reset_additional_routes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalRoutes", []))

    @jsii.member(jsii_name="resetCookieAttributes")
    def reset_cookie_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCookieAttributes", []))

    @jsii.member(jsii_name="resetCookieSuffix")
    def reset_cookie_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCookieSuffix", []))

    @jsii.member(jsii_name="resetCustomPageHtml")
    def reset_custom_page_html(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomPageHtml", []))

    @jsii.member(jsii_name="resetDefaultTemplateLanguage")
    def reset_default_template_language(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTemplateLanguage", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisableSessionRenewal")
    def reset_disable_session_renewal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableSessionRenewal", []))

    @jsii.member(jsii_name="resetEnabledOriginCommands")
    def reset_enabled_origin_commands(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabledOriginCommands", []))

    @jsii.member(jsii_name="resetJsonResponseEnabled")
    def reset_json_response_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJsonResponseEnabled", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetQueueAll")
    def reset_queue_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueAll", []))

    @jsii.member(jsii_name="resetQueueingMethod")
    def reset_queueing_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueingMethod", []))

    @jsii.member(jsii_name="resetQueueingStatusCode")
    def reset_queueing_status_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueingStatusCode", []))

    @jsii.member(jsii_name="resetSessionDuration")
    def reset_session_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionDuration", []))

    @jsii.member(jsii_name="resetSuspended")
    def reset_suspended(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuspended", []))

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
    @jsii.member(jsii_name="additionalRoutes")
    def additional_routes(self) -> "WaitingRoomAdditionalRoutesList":
        return typing.cast("WaitingRoomAdditionalRoutesList", jsii.get(self, "additionalRoutes"))

    @builtins.property
    @jsii.member(jsii_name="cookieAttributes")
    def cookie_attributes(self) -> "WaitingRoomCookieAttributesOutputReference":
        return typing.cast("WaitingRoomCookieAttributesOutputReference", jsii.get(self, "cookieAttributes"))

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
    @jsii.member(jsii_name="nextEventPrequeueStartTime")
    def next_event_prequeue_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nextEventPrequeueStartTime"))

    @builtins.property
    @jsii.member(jsii_name="nextEventStartTime")
    def next_event_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nextEventStartTime"))

    @builtins.property
    @jsii.member(jsii_name="additionalRoutesInput")
    def additional_routes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WaitingRoomAdditionalRoutes"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WaitingRoomAdditionalRoutes"]]], jsii.get(self, "additionalRoutesInput"))

    @builtins.property
    @jsii.member(jsii_name="cookieAttributesInput")
    def cookie_attributes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaitingRoomCookieAttributes"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaitingRoomCookieAttributes"]], jsii.get(self, "cookieAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="cookieSuffixInput")
    def cookie_suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cookieSuffixInput"))

    @builtins.property
    @jsii.member(jsii_name="customPageHtmlInput")
    def custom_page_html_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customPageHtmlInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultTemplateLanguageInput")
    def default_template_language_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultTemplateLanguageInput"))

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
    @jsii.member(jsii_name="enabledOriginCommandsInput")
    def enabled_origin_commands_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "enabledOriginCommandsInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="jsonResponseEnabledInput")
    def json_response_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "jsonResponseEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="newUsersPerMinuteInput")
    def new_users_per_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "newUsersPerMinuteInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="queueAllInput")
    def queue_all_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "queueAllInput"))

    @builtins.property
    @jsii.member(jsii_name="queueingMethodInput")
    def queueing_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueingMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="queueingStatusCodeInput")
    def queueing_status_code_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "queueingStatusCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionDurationInput")
    def session_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sessionDurationInput"))

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
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="cookieSuffix")
    def cookie_suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cookieSuffix"))

    @cookie_suffix.setter
    def cookie_suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0113aba5715352b30835ab2d9521bab3d08fa5ca2d22378d460cf321e5d02ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cookieSuffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customPageHtml")
    def custom_page_html(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customPageHtml"))

    @custom_page_html.setter
    def custom_page_html(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00c09cb9ece44f399d78d953e46df87b8436fa04c2cc6fb0c118c0589e144379)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customPageHtml", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultTemplateLanguage")
    def default_template_language(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultTemplateLanguage"))

    @default_template_language.setter
    def default_template_language(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__969d8244c2f72aaa4ee1c5d68a01df650631f899d5b3592e6c7ee246068a7d9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTemplateLanguage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f30d0cb2906b147f6cf4f8372df5283d1e846cd119a8d8f23eb3a868af4060b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__59ad261883326e9a9804b22864a7b94dfd7185bd735cb99ac76189594fceeb6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableSessionRenewal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabledOriginCommands")
    def enabled_origin_commands(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "enabledOriginCommands"))

    @enabled_origin_commands.setter
    def enabled_origin_commands(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f64d94b76d28912d5562eb5e34e60e37d2d378c66178b5ed480801772015ddb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabledOriginCommands", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0209441a13abea89a612cc455d474cffbe978ccfa3e6c7641606c3fba5d750f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jsonResponseEnabled")
    def json_response_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "jsonResponseEnabled"))

    @json_response_enabled.setter
    def json_response_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7f88dea94bc4c673e79b7e30ffd6b4785c3765bba6d21634ec47ba87f61fbaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jsonResponseEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdf77968b4f2854b1a4a67b3e46d1fdbbb3011fd2a8971cffb8747bdc0c164df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newUsersPerMinute")
    def new_users_per_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "newUsersPerMinute"))

    @new_users_per_minute.setter
    def new_users_per_minute(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a1b91c649c55391030282e67f922293c72f360190666c593e9f9b3f762b814e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newUsersPerMinute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__311db3e13367a00c1bb9bc9f9fbe22338d52ed8c9b53246bf0187ddfd2fdb7eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueAll")
    def queue_all(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "queueAll"))

    @queue_all.setter
    def queue_all(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41e8a601ee2eec0d8b5e3ecd699e09e9dffc8c546ae84b92f3b49e540d19df79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueAll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueingMethod")
    def queueing_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueingMethod"))

    @queueing_method.setter
    def queueing_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__387c1b2a7e715268ed49e011f33ac68b2248b2cb9a60e2890b342126fbf89951)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueingMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueingStatusCode")
    def queueing_status_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "queueingStatusCode"))

    @queueing_status_code.setter
    def queueing_status_code(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df84ee66405b1bdbe97546ad84ba7bb8bf0cd76cf474540a9423919af13caba4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueingStatusCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionDuration")
    def session_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sessionDuration"))

    @session_duration.setter
    def session_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b38fc44390838c7fa98c179cc12a76e97e9c10f093104ed6754915746232677)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionDuration", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__cb516a930e2ad062317a964a4c17be49c8ecc7f83a1e24818b756377ec64b1b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suspended", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalActiveUsers")
    def total_active_users(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalActiveUsers"))

    @total_active_users.setter
    def total_active_users(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00e9745f39e08ed798ec32b953cbf71156d2913ae8b2d984cab9cc9d13cfb961)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalActiveUsers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="turnstileAction")
    def turnstile_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "turnstileAction"))

    @turnstile_action.setter
    def turnstile_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5bfbfd5ae94b2f7b2772f5577c5175157b9a7758b204dd4829eb012304366f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "turnstileAction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="turnstileMode")
    def turnstile_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "turnstileMode"))

    @turnstile_mode.setter
    def turnstile_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0564066a94ab07953f33cf0221de344342aea75dbba4c72c17ca4f398915e0cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "turnstileMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bda4fb123f4ab106fe556d19e569abbfda45e0f076496ba9135d7b7fe0fd3df1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.waitingRoom.WaitingRoomAdditionalRoutes",
    jsii_struct_bases=[],
    name_mapping={"host": "host", "path": "path"},
)
class WaitingRoomAdditionalRoutes:
    def __init__(
        self,
        *,
        host: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host: The hostname to which this waiting room will be applied (no wildcards). The hostname must be the primary domain, subdomain, or custom hostname (if using SSL for SaaS) of this zone. Please do not include the scheme (http:// or https://). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#host WaitingRoom#host}
        :param path: Sets the path within the host to enable the waiting room on. The waiting room will be enabled for all subpaths as well. If there are two waiting rooms on the same subpath, the waiting room for the most specific path will be chosen. Wildcards and query parameters are not supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#path WaitingRoom#path}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdfb6532add76d6bea1045eb30caceb1f75cf06fdedee2355b6d15b3b113b375)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if host is not None:
            self._values["host"] = host
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''The hostname to which this waiting room will be applied (no wildcards).

        The hostname must be the primary domain, subdomain, or custom hostname (if using SSL for SaaS) of this zone. Please do not include the scheme (http:// or https://).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#host WaitingRoom#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Sets the path within the host to enable the waiting room on.

        The waiting room will be enabled for all subpaths as well. If there are two waiting rooms on the same subpath, the waiting room for the most specific path will be chosen. Wildcards and query parameters are not supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#path WaitingRoom#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaitingRoomAdditionalRoutes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WaitingRoomAdditionalRoutesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.waitingRoom.WaitingRoomAdditionalRoutesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__82391e6cadf783ca577cb508838d2cc2140d044d5624c6b1c65bf18a97a398f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WaitingRoomAdditionalRoutesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aea769387e6f82ba47a2044f42f4687b3886f293372d42a2fb6459cff30376d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WaitingRoomAdditionalRoutesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e48b982227594aab1578a69edfe2e290766f80393d50ed3c9f0f11954b480246)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b946c5e29b6d714e1e62260433ae316faf1a62690702a9a6b3396de960a30d43)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ebbc2d995b57d9deb7580125263db7d4fe9133607b85905dad058812cd53620)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WaitingRoomAdditionalRoutes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WaitingRoomAdditionalRoutes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WaitingRoomAdditionalRoutes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f8a5d3fbbdb2a76e2352943ee304b19ae87f4d317001e2a71d6c8fc7789e449)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WaitingRoomAdditionalRoutesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.waitingRoom.WaitingRoomAdditionalRoutesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae709a4421a77f02eae903189df705a706e8919fa8f3f135527012f3297dc7d4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed57513211478266f9b051b8c668000cc0d134b466eb0bec7c8e967f354a339a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__589cf52257c11028282e63efcb47d19ab246f8d5a311a7ac332ac4e679c12add)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaitingRoomAdditionalRoutes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaitingRoomAdditionalRoutes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaitingRoomAdditionalRoutes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fcee894f2e2742c6a802808f752867aa6223bb8e2aa064484658c530f0e9882)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.waitingRoom.WaitingRoomConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "host": "host",
        "name": "name",
        "new_users_per_minute": "newUsersPerMinute",
        "total_active_users": "totalActiveUsers",
        "zone_id": "zoneId",
        "additional_routes": "additionalRoutes",
        "cookie_attributes": "cookieAttributes",
        "cookie_suffix": "cookieSuffix",
        "custom_page_html": "customPageHtml",
        "default_template_language": "defaultTemplateLanguage",
        "description": "description",
        "disable_session_renewal": "disableSessionRenewal",
        "enabled_origin_commands": "enabledOriginCommands",
        "json_response_enabled": "jsonResponseEnabled",
        "path": "path",
        "queue_all": "queueAll",
        "queueing_method": "queueingMethod",
        "queueing_status_code": "queueingStatusCode",
        "session_duration": "sessionDuration",
        "suspended": "suspended",
        "turnstile_action": "turnstileAction",
        "turnstile_mode": "turnstileMode",
    },
)
class WaitingRoomConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        host: builtins.str,
        name: builtins.str,
        new_users_per_minute: jsii.Number,
        total_active_users: jsii.Number,
        zone_id: builtins.str,
        additional_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WaitingRoomAdditionalRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
        cookie_attributes: typing.Optional[typing.Union["WaitingRoomCookieAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        cookie_suffix: typing.Optional[builtins.str] = None,
        custom_page_html: typing.Optional[builtins.str] = None,
        default_template_language: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_session_renewal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled_origin_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        json_response_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        path: typing.Optional[builtins.str] = None,
        queue_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        queueing_method: typing.Optional[builtins.str] = None,
        queueing_status_code: typing.Optional[jsii.Number] = None,
        session_duration: typing.Optional[jsii.Number] = None,
        suspended: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param host: The host name to which the waiting room will be applied (no wildcards). Please do not include the scheme (http:// or https://). The host and path combination must be unique. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#host WaitingRoom#host}
        :param name: A unique name to identify the waiting room. Only alphanumeric characters, hyphens and underscores are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#name WaitingRoom#name}
        :param new_users_per_minute: Sets the number of new users that will be let into the route every minute. This value is used as baseline for the number of users that are let in per minute. So it is possible that there is a little more or little less traffic coming to the route based on the traffic patterns at that time around the world. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#new_users_per_minute WaitingRoom#new_users_per_minute}
        :param total_active_users: Sets the total number of active user sessions on the route at a point in time. A route is a combination of host and path on which a waiting room is available. This value is used as a baseline for the total number of active user sessions on the route. It is possible to have a situation where there are more or less active users sessions on the route based on the traffic patterns at that time around the world. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#total_active_users WaitingRoom#total_active_users}
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#zone_id WaitingRoom#zone_id}
        :param additional_routes: Only available for the Waiting Room Advanced subscription. Additional hostname and path combinations to which this waiting room will be applied. There is an implied wildcard at the end of the path. The hostname and path combination must be unique to this and all other waiting rooms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#additional_routes WaitingRoom#additional_routes}
        :param cookie_attributes: Configures cookie attributes for the waiting room cookie. This encrypted cookie stores a user's status in the waiting room, such as queue position. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#cookie_attributes WaitingRoom#cookie_attributes}
        :param cookie_suffix: Appends a '_' + a custom suffix to the end of Cloudflare Waiting Room's cookie name(__cf_waitingroom). If ``cookie_suffix`` is "abcd", the cookie name will be ``__cf_waitingroom_abcd``. This field is required if using ``additional_routes``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#cookie_suffix WaitingRoom#cookie_suffix}
        :param custom_page_html: Only available for the Waiting Room Advanced subscription. This is a template html file that will be rendered at the edge. If no custom_page_html is provided, the default waiting room will be used. The template is based on mustache ( https://mustache.github.io/ ). There are several variables that are evaluated by the Cloudflare edge: 1. {{``waitTimeKnown``}} Acts like a boolean value that indicates the behavior to take when wait time is not available, for instance when queue_all is **true**. 2. {{``waitTimeFormatted``}} Estimated wait time for the user. For example, five minutes. Alternatively, you can use: 3. {{``waitTime``}} Number of minutes of estimated wait for a user. 4. {{``waitTimeHours``}} Number of hours of estimated wait for a user (``Math.floor(waitTime/60)``). 5. {{``waitTimeHourMinutes``}} Number of minutes above the ``waitTimeHours`` value (``waitTime%60``). 6. {{``queueIsFull``}} Changes to **true** when no more people can be added to the queue. To view the full list of variables, look at the ``cfWaitingRoom`` object described under the ``json_response_enabled`` property in other Waiting Room API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#custom_page_html WaitingRoom#custom_page_html}
        :param default_template_language: The language of the default page template. If no default_template_language is provided, then ``en-US`` (English) will be used. Available values: "en-US", "es-ES", "de-DE", "fr-FR", "it-IT", "ja-JP", "ko-KR", "pt-BR", "zh-CN", "zh-TW", "nl-NL", "pl-PL", "id-ID", "tr-TR", "ar-EG", "ru-RU", "fa-IR", "bg-BG", "hr-HR", "cs-CZ", "da-DK", "fi-FI", "lt-LT", "ms-MY", "nb-NO", "ro-RO", "el-GR", "he-IL", "hi-IN", "hu-HU", "sr-BA", "sk-SK", "sl-SI", "sv-SE", "tl-PH", "th-TH", "uk-UA", "vi-VN". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#default_template_language WaitingRoom#default_template_language}
        :param description: A note that you can use to add more details about the waiting room. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#description WaitingRoom#description}
        :param disable_session_renewal: Only available for the Waiting Room Advanced subscription. Disables automatic renewal of session cookies. If ``true``, an accepted user will have session_duration minutes to browse the site. After that, they will have to go through the waiting room again. If ``false``, a user's session cookie will be automatically renewed on every request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#disable_session_renewal WaitingRoom#disable_session_renewal}
        :param enabled_origin_commands: A list of enabled origin commands. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#enabled_origin_commands WaitingRoom#enabled_origin_commands}
        :param json_response_enabled: Only available for the Waiting Room Advanced subscription. If ``true``, requests to the waiting room with the header ``Accept: application/json`` will receive a JSON response object with information on the user's status in the waiting room as opposed to the configured static HTML page. This JSON response object has one property ``cfWaitingRoom`` which is an object containing the following fields: 1. ``inWaitingRoom``: Boolean indicating if the user is in the waiting room (always **true**). 2. ``waitTimeKnown``: Boolean indicating if the current estimated wait times are accurate. If **false**, they are not available. 3. ``waitTime``: Valid only when ``waitTimeKnown`` is **true**. Integer indicating the current estimated time in minutes the user will wait in the waiting room. When ``queueingMethod`` is **random**, this is set to ``waitTime50Percentile``. 4. ``waitTime25Percentile``: Valid only when ``queueingMethod`` is **random** and ``waitTimeKnown`` is **true**. Integer indicating the current estimated maximum wait time for the 25% of users that gain entry the fastest (25th percentile). 5. ``waitTime50Percentile``: Valid only when ``queueingMethod`` is **random** and ``waitTimeKnown`` is **true**. Integer indicating the current estimated maximum wait time for the 50% of users that gain entry the fastest (50th percentile). In other words, half of the queued users are expected to let into the origin website before ``waitTime50Percentile`` and half are expected to be let in after it. 6. ``waitTime75Percentile``: Valid only when ``queueingMethod`` is **random** and ``waitTimeKnown`` is **true**. Integer indicating the current estimated maximum wait time for the 75% of users that gain entry the fastest (75th percentile). 7. ``waitTimeFormatted``: String displaying the ``waitTime`` formatted in English for users. If ``waitTimeKnown`` is **false**, ``waitTimeFormatted`` will display **unavailable**. 8. ``queueIsFull``: Boolean indicating if the waiting room's queue is currently full and not accepting new users at the moment. 9. ``queueAll``: Boolean indicating if all users will be queued in the waiting room and no one will be let into the origin website. 10. ``lastUpdated``: String displaying the timestamp as an ISO 8601 string of the user's last attempt to leave the waiting room and be let into the origin website. The user is able to make another attempt after ``refreshIntervalSeconds`` past this time. If the user makes a request too soon, it will be ignored and ``lastUpdated`` will not change. 11. ``refreshIntervalSeconds``: Integer indicating the number of seconds after ``lastUpdated`` until the user is able to make another attempt to leave the waiting room and be let into the origin website. When the ``queueingMethod`` is ``reject``, there is no specified refresh time —_it will always be **zero**. 12. ``queueingMethod``: The queueing method currently used by the waiting room. It is either **fifo**, **random**, **passthrough**, or **reject**. 13. ``isFIFOQueue``: Boolean indicating if the waiting room uses a FIFO (First-In-First-Out) queue. 14. ``isRandomQueue``: Boolean indicating if the waiting room uses a Random queue where users gain access randomly. 15. ``isPassthroughQueue``: Boolean indicating if the waiting room uses a passthrough queue. Keep in mind that when passthrough is enabled, this JSON response will only exist when ``queueAll`` is **true** or ``isEventPrequeueing`` is **true** because in all other cases requests will go directly to the origin. 16. ``isRejectQueue``: Boolean indicating if the waiting room uses a reject queue. 17. ``isEventActive``: Boolean indicating if an event is currently occurring. Events are able to change a waiting room's behavior during a specified period of time. For additional information, look at the event properties ``prequeue_start_time``, ``event_start_time``, and ``event_end_time`` in the documentation for creating waiting room events. Events are considered active between these start and end times, as well as during the prequeueing period if it exists. 18. ``isEventPrequeueing``: Valid only when ``isEventActive`` is **true**. Boolean indicating if an event is currently prequeueing users before it starts. 19. ``timeUntilEventStart``: Valid only when ``isEventPrequeueing`` is **true**. Integer indicating the number of minutes until the event starts. 20. ``timeUntilEventStartFormatted``: String displaying the ``timeUntilEventStart`` formatted in English for users. If ``isEventPrequeueing`` is **false**, ``timeUntilEventStartFormatted`` will display **unavailable**. 21. ``timeUntilEventEnd``: Valid only when ``isEventActive`` is **true**. Integer indicating the number of minutes until the event ends. 22. ``timeUntilEventEndFormatted``: String displaying the ``timeUntilEventEnd`` formatted in English for users. If ``isEventActive`` is **false**, ``timeUntilEventEndFormatted`` will display **unavailable**. 23. ``shuffleAtEventStart``: Valid only when ``isEventActive`` is **true**. Boolean indicating if the users in the prequeue are shuffled randomly when the event starts. 24. ``turnstile``: Empty when turnstile isn't enabled. String displaying an html tag to display the Turnstile widget. Please add the ``{{{turnstile}}}`` tag to the ``custom_html`` template to ensure the Turnstile widget appears. 25. ``infiniteQueue``: Boolean indicating whether the response is for a user in the infinite queue. An example cURL to a waiting room could be:: curl -X GET "https://example.com/waitingroom" \\ -H "Accept: application/json" If ``json_response_enabled`` is **true** and the request hits the waiting room, an example JSON response when ``queueingMethod`` is **fifo** and no event is active could be:: { "cfWaitingRoom": { "inWaitingRoom": true, "waitTimeKnown": true, "waitTime": 10, "waitTime25Percentile": 0, "waitTime50Percentile": 0, "waitTime75Percentile": 0, "waitTimeFormatted": "10 minutes", "queueIsFull": false, "queueAll": false, "lastUpdated": "2020-08-03T23:46:00.000Z", "refreshIntervalSeconds": 20, "queueingMethod": "fifo", "isFIFOQueue": true, "isRandomQueue": false, "isPassthroughQueue": false, "isRejectQueue": false, "isEventActive": false, "isEventPrequeueing": false, "timeUntilEventStart": 0, "timeUntilEventStartFormatted": "unavailable", "timeUntilEventEnd": 0, "timeUntilEventEndFormatted": "unavailable", "shuffleAtEventStart": false } } If ``json_response_enabled`` is **true** and the request hits the waiting room, an example JSON response when ``queueingMethod`` is **random** and an event is active could be:: { "cfWaitingRoom": { "inWaitingRoom": true, "waitTimeKnown": true, "waitTime": 10, "waitTime25Percentile": 5, "waitTime50Percentile": 10, "waitTime75Percentile": 15, "waitTimeFormatted": "5 minutes to 15 minutes", "queueIsFull": false, "queueAll": false, "lastUpdated": "2020-08-03T23:46:00.000Z", "refreshIntervalSeconds": 20, "queueingMethod": "random", "isFIFOQueue": false, "isRandomQueue": true, "isPassthroughQueue": false, "isRejectQueue": false, "isEventActive": true, "isEventPrequeueing": false, "timeUntilEventStart": 0, "timeUntilEventStartFormatted": "unavailable", "timeUntilEventEnd": 15, "timeUntilEventEndFormatted": "15 minutes", "shuffleAtEventStart": true } } Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#json_response_enabled WaitingRoom#json_response_enabled}
        :param path: Sets the path within the host to enable the waiting room on. The waiting room will be enabled for all subpaths as well. If there are two waiting rooms on the same subpath, the waiting room for the most specific path will be chosen. Wildcards and query parameters are not supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#path WaitingRoom#path}
        :param queue_all: If queue_all is ``true``, all the traffic that is coming to a route will be sent to the waiting room. No new traffic can get to the route once this field is set and estimated time will become unavailable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#queue_all WaitingRoom#queue_all}
        :param queueing_method: Sets the queueing method used by the waiting room. Changing this parameter from the **default** queueing method is only available for the Waiting Room Advanced subscription. Regardless of the queueing method, if ``queue_all`` is enabled or an event is prequeueing, users in the waiting room will not be accepted to the origin. These users will always see a waiting room page that refreshes automatically. The valid queueing methods are: 1. ``fifo`` **(default)**: First-In-First-Out queue where customers gain access in the order they arrived. 2. ``random``: Random queue where customers gain access randomly, regardless of arrival time. 3. ``passthrough``: Users will pass directly through the waiting room and into the origin website. As a result, any configured limits will not be respected while this is enabled. This method can be used as an alternative to disabling a waiting room (with ``suspended``) so that analytics are still reported. This can be used if you wish to allow all traffic normally, but want to restrict traffic during a waiting room event, or vice versa. 4. ``reject``: Users will be immediately rejected from the waiting room. As a result, no users will reach the origin website while this is enabled. This can be used if you wish to reject all traffic while performing maintenance, block traffic during a specified period of time (an event), or block traffic while events are not occurring. Consider a waiting room used for vaccine distribution that only allows traffic during sign-up events, and otherwise blocks all traffic. For this case, the waiting room uses ``reject``, and its events override this with ``fifo``, ``random``, or ``passthrough``. When this queueing method is enabled and neither ``queueAll`` is enabled nor an event is prequeueing, the waiting room page **will not refresh automatically**. Available values: "fifo", "random", "passthrough", "reject". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#queueing_method WaitingRoom#queueing_method}
        :param queueing_status_code: HTTP status code returned to a user while in the queue. Available values: 200, 202, 429. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#queueing_status_code WaitingRoom#queueing_status_code}
        :param session_duration: Lifetime of a cookie (in minutes) set by Cloudflare for users who get access to the route. If a user is not seen by Cloudflare again in that time period, they will be treated as a new user that visits the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#session_duration WaitingRoom#session_duration}
        :param suspended: Suspends or allows traffic going to the waiting room. If set to ``true``, the traffic will not go to the waiting room. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#suspended WaitingRoom#suspended}
        :param turnstile_action: Which action to take when a bot is detected using Turnstile. ``log`` will have no impact on queueing behavior, simply keeping track of how many bots are detected in Waiting Room Analytics. ``infinite_queue`` will send bots to a false queueing state, where they will never reach your origin. ``infinite_queue`` requires Advanced Waiting Room. Available values: "log", "infinite_queue". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#turnstile_action WaitingRoom#turnstile_action}
        :param turnstile_mode: Which Turnstile widget type to use for detecting bot traffic. See `the Turnstile documentation <https://developers.cloudflare.com/turnstile/concepts/widget/#widget-types>`_ for the definitions of these widget types. Set to ``off`` to disable the Turnstile integration entirely. Setting this to anything other than ``off`` or ``invisible`` requires Advanced Waiting Room. Available values: "off", "invisible", "visible_non_interactive", "visible_managed". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#turnstile_mode WaitingRoom#turnstile_mode}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cookie_attributes, dict):
            cookie_attributes = WaitingRoomCookieAttributes(**cookie_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71218a0efc55f5ae63de81f8f8687b06300c02b6514087e449eefe5fcf43c58c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument new_users_per_minute", value=new_users_per_minute, expected_type=type_hints["new_users_per_minute"])
            check_type(argname="argument total_active_users", value=total_active_users, expected_type=type_hints["total_active_users"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument additional_routes", value=additional_routes, expected_type=type_hints["additional_routes"])
            check_type(argname="argument cookie_attributes", value=cookie_attributes, expected_type=type_hints["cookie_attributes"])
            check_type(argname="argument cookie_suffix", value=cookie_suffix, expected_type=type_hints["cookie_suffix"])
            check_type(argname="argument custom_page_html", value=custom_page_html, expected_type=type_hints["custom_page_html"])
            check_type(argname="argument default_template_language", value=default_template_language, expected_type=type_hints["default_template_language"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_session_renewal", value=disable_session_renewal, expected_type=type_hints["disable_session_renewal"])
            check_type(argname="argument enabled_origin_commands", value=enabled_origin_commands, expected_type=type_hints["enabled_origin_commands"])
            check_type(argname="argument json_response_enabled", value=json_response_enabled, expected_type=type_hints["json_response_enabled"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument queue_all", value=queue_all, expected_type=type_hints["queue_all"])
            check_type(argname="argument queueing_method", value=queueing_method, expected_type=type_hints["queueing_method"])
            check_type(argname="argument queueing_status_code", value=queueing_status_code, expected_type=type_hints["queueing_status_code"])
            check_type(argname="argument session_duration", value=session_duration, expected_type=type_hints["session_duration"])
            check_type(argname="argument suspended", value=suspended, expected_type=type_hints["suspended"])
            check_type(argname="argument turnstile_action", value=turnstile_action, expected_type=type_hints["turnstile_action"])
            check_type(argname="argument turnstile_mode", value=turnstile_mode, expected_type=type_hints["turnstile_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host": host,
            "name": name,
            "new_users_per_minute": new_users_per_minute,
            "total_active_users": total_active_users,
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
        if additional_routes is not None:
            self._values["additional_routes"] = additional_routes
        if cookie_attributes is not None:
            self._values["cookie_attributes"] = cookie_attributes
        if cookie_suffix is not None:
            self._values["cookie_suffix"] = cookie_suffix
        if custom_page_html is not None:
            self._values["custom_page_html"] = custom_page_html
        if default_template_language is not None:
            self._values["default_template_language"] = default_template_language
        if description is not None:
            self._values["description"] = description
        if disable_session_renewal is not None:
            self._values["disable_session_renewal"] = disable_session_renewal
        if enabled_origin_commands is not None:
            self._values["enabled_origin_commands"] = enabled_origin_commands
        if json_response_enabled is not None:
            self._values["json_response_enabled"] = json_response_enabled
        if path is not None:
            self._values["path"] = path
        if queue_all is not None:
            self._values["queue_all"] = queue_all
        if queueing_method is not None:
            self._values["queueing_method"] = queueing_method
        if queueing_status_code is not None:
            self._values["queueing_status_code"] = queueing_status_code
        if session_duration is not None:
            self._values["session_duration"] = session_duration
        if suspended is not None:
            self._values["suspended"] = suspended
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
    def host(self) -> builtins.str:
        '''The host name to which the waiting room will be applied (no wildcards).

        Please do not include the scheme (http:// or https://). The host and path combination must be unique.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#host WaitingRoom#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''A unique name to identify the waiting room. Only alphanumeric characters, hyphens and underscores are allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#name WaitingRoom#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def new_users_per_minute(self) -> jsii.Number:
        '''Sets the number of new users that will be let into the route every minute.

        This value is used as baseline for the number of users that are let in per minute. So it is possible that there is a little more or little less traffic coming to the route based on the traffic patterns at that time around the world.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#new_users_per_minute WaitingRoom#new_users_per_minute}
        '''
        result = self._values.get("new_users_per_minute")
        assert result is not None, "Required property 'new_users_per_minute' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def total_active_users(self) -> jsii.Number:
        '''Sets the total number of active user sessions on the route at a point in time.

        A route is a combination of host and path on which a waiting room is available. This value is used as a baseline for the total number of active user sessions on the route. It is possible to have a situation where there are more or less active users sessions on the route based on the traffic patterns at that time around the world.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#total_active_users WaitingRoom#total_active_users}
        '''
        result = self._values.get("total_active_users")
        assert result is not None, "Required property 'total_active_users' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def zone_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#zone_id WaitingRoom#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_routes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WaitingRoomAdditionalRoutes]]]:
        '''Only available for the Waiting Room Advanced subscription.

        Additional hostname and path combinations to which this waiting room will be applied. There is an implied wildcard at the end of the path. The hostname and path combination must be unique to this and all other waiting rooms.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#additional_routes WaitingRoom#additional_routes}
        '''
        result = self._values.get("additional_routes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WaitingRoomAdditionalRoutes]]], result)

    @builtins.property
    def cookie_attributes(self) -> typing.Optional["WaitingRoomCookieAttributes"]:
        '''Configures cookie attributes for the waiting room cookie.

        This encrypted cookie stores a user's status in the waiting room, such as queue position.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#cookie_attributes WaitingRoom#cookie_attributes}
        '''
        result = self._values.get("cookie_attributes")
        return typing.cast(typing.Optional["WaitingRoomCookieAttributes"], result)

    @builtins.property
    def cookie_suffix(self) -> typing.Optional[builtins.str]:
        '''Appends a '_' + a custom suffix to the end of Cloudflare Waiting Room's cookie name(__cf_waitingroom).

        If ``cookie_suffix`` is "abcd", the cookie name will be ``__cf_waitingroom_abcd``. This field is required if using ``additional_routes``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#cookie_suffix WaitingRoom#cookie_suffix}
        '''
        result = self._values.get("cookie_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_page_html(self) -> typing.Optional[builtins.str]:
        '''Only available for the Waiting Room Advanced subscription.

        This is a template html file that will be rendered at the edge. If no custom_page_html is provided, the default waiting room will be used. The template is based on mustache ( https://mustache.github.io/ ). There are several variables that are evaluated by the Cloudflare edge:

        1. {{``waitTimeKnown``}} Acts like a boolean value that indicates the behavior to take when wait time is not available, for instance when queue_all is **true**.
        2. {{``waitTimeFormatted``}} Estimated wait time for the user. For example, five minutes. Alternatively, you can use:
        3. {{``waitTime``}} Number of minutes of estimated wait for a user.
        4. {{``waitTimeHours``}} Number of hours of estimated wait for a user (``Math.floor(waitTime/60)``).
        5. {{``waitTimeHourMinutes``}} Number of minutes above the ``waitTimeHours`` value (``waitTime%60``).
        6. {{``queueIsFull``}} Changes to **true** when no more people can be added to the queue.

        To view the full list of variables, look at the ``cfWaitingRoom`` object described under the ``json_response_enabled`` property in other Waiting Room API calls.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#custom_page_html WaitingRoom#custom_page_html}
        '''
        result = self._values.get("custom_page_html")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_template_language(self) -> typing.Optional[builtins.str]:
        '''The language of the default page template.

        If no default_template_language is provided, then ``en-US`` (English) will be used.
        Available values: "en-US", "es-ES", "de-DE", "fr-FR", "it-IT", "ja-JP", "ko-KR", "pt-BR", "zh-CN", "zh-TW", "nl-NL", "pl-PL", "id-ID", "tr-TR", "ar-EG", "ru-RU", "fa-IR", "bg-BG", "hr-HR", "cs-CZ", "da-DK", "fi-FI", "lt-LT", "ms-MY", "nb-NO", "ro-RO", "el-GR", "he-IL", "hi-IN", "hu-HU", "sr-BA", "sk-SK", "sl-SI", "sv-SE", "tl-PH", "th-TH", "uk-UA", "vi-VN".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#default_template_language WaitingRoom#default_template_language}
        '''
        result = self._values.get("default_template_language")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A note that you can use to add more details about the waiting room.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#description WaitingRoom#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_session_renewal(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Only available for the Waiting Room Advanced subscription.

        Disables automatic renewal of session cookies. If ``true``, an accepted user will have session_duration minutes to browse the site. After that, they will have to go through the waiting room again. If ``false``, a user's session cookie will be automatically renewed on every request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#disable_session_renewal WaitingRoom#disable_session_renewal}
        '''
        result = self._values.get("disable_session_renewal")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled_origin_commands(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of enabled origin commands.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#enabled_origin_commands WaitingRoom#enabled_origin_commands}
        '''
        result = self._values.get("enabled_origin_commands")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def json_response_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Only available for the Waiting Room Advanced subscription.

        If ``true``, requests to the waiting room with the header ``Accept: application/json`` will receive a JSON response object with information on the user's status in the waiting room as opposed to the configured static HTML page. This JSON response object has one property ``cfWaitingRoom`` which is an object containing the following fields:

        1. ``inWaitingRoom``: Boolean indicating if the user is in the waiting room (always **true**).
        2. ``waitTimeKnown``: Boolean indicating if the current estimated wait times are accurate. If **false**, they are not available.
        3. ``waitTime``: Valid only when ``waitTimeKnown`` is **true**. Integer indicating the current estimated time in minutes the user will wait in the waiting room. When ``queueingMethod`` is **random**, this is set to ``waitTime50Percentile``.
        4. ``waitTime25Percentile``: Valid only when ``queueingMethod`` is **random** and ``waitTimeKnown`` is **true**. Integer indicating the current estimated maximum wait time for the 25% of users that gain entry the fastest (25th percentile).
        5. ``waitTime50Percentile``: Valid only when ``queueingMethod`` is **random** and ``waitTimeKnown`` is **true**. Integer indicating the current estimated maximum wait time for the 50% of users that gain entry the fastest (50th percentile). In other words, half of the queued users are expected to let into the origin website before ``waitTime50Percentile`` and half are expected to be let in after it.
        6. ``waitTime75Percentile``: Valid only when ``queueingMethod`` is **random** and ``waitTimeKnown`` is **true**. Integer indicating the current estimated maximum wait time for the 75% of users that gain entry the fastest (75th percentile).
        7. ``waitTimeFormatted``: String displaying the ``waitTime`` formatted in English for users. If ``waitTimeKnown`` is **false**, ``waitTimeFormatted`` will display **unavailable**.
        8. ``queueIsFull``: Boolean indicating if the waiting room's queue is currently full and not accepting new users at the moment.
        9. ``queueAll``: Boolean indicating if all users will be queued in the waiting room and no one will be let into the origin website.
        10. ``lastUpdated``: String displaying the timestamp as an ISO 8601 string of the user's last attempt to leave the waiting room and be let into the origin website. The user is able to make another attempt after ``refreshIntervalSeconds`` past this time. If the user makes a request too soon, it will be ignored and ``lastUpdated`` will not change.
        11. ``refreshIntervalSeconds``: Integer indicating the number of seconds after ``lastUpdated`` until the user is able to make another attempt to leave the waiting room and be let into the origin website. When the ``queueingMethod`` is ``reject``, there is no specified refresh time —_it will always be **zero**.
        12. ``queueingMethod``: The queueing method currently used by the waiting room. It is either **fifo**, **random**, **passthrough**, or **reject**.
        13. ``isFIFOQueue``: Boolean indicating if the waiting room uses a FIFO (First-In-First-Out) queue.
        14. ``isRandomQueue``: Boolean indicating if the waiting room uses a Random queue where users gain access randomly.
        15. ``isPassthroughQueue``: Boolean indicating if the waiting room uses a passthrough queue. Keep in mind that when passthrough is enabled, this JSON response will only exist when ``queueAll`` is **true** or ``isEventPrequeueing`` is **true** because in all other cases requests will go directly to the origin.
        16. ``isRejectQueue``: Boolean indicating if the waiting room uses a reject queue.
        17. ``isEventActive``: Boolean indicating if an event is currently occurring. Events are able to change a waiting room's behavior during a specified period of time. For additional information, look at the event properties ``prequeue_start_time``, ``event_start_time``, and ``event_end_time`` in the documentation for creating waiting room events. Events are considered active between these start and end times, as well as during the prequeueing period if it exists.
        18. ``isEventPrequeueing``: Valid only when ``isEventActive`` is **true**. Boolean indicating if an event is currently prequeueing users before it starts.
        19. ``timeUntilEventStart``: Valid only when ``isEventPrequeueing`` is **true**. Integer indicating the number of minutes until the event starts.
        20. ``timeUntilEventStartFormatted``: String displaying the ``timeUntilEventStart`` formatted in English for users. If ``isEventPrequeueing`` is **false**, ``timeUntilEventStartFormatted`` will display **unavailable**.
        21. ``timeUntilEventEnd``: Valid only when ``isEventActive`` is **true**. Integer indicating the number of minutes until the event ends.
        22. ``timeUntilEventEndFormatted``: String displaying the ``timeUntilEventEnd`` formatted in English for users. If ``isEventActive`` is **false**, ``timeUntilEventEndFormatted`` will display **unavailable**.
        23. ``shuffleAtEventStart``: Valid only when ``isEventActive`` is **true**. Boolean indicating if the users in the prequeue are shuffled randomly when the event starts.
        24. ``turnstile``: Empty when turnstile isn't enabled. String displaying an html tag to display the Turnstile widget. Please add the ``{{{turnstile}}}`` tag to the ``custom_html`` template to ensure the Turnstile widget appears.
        25. ``infiniteQueue``: Boolean indicating whether the response is for a user in the infinite queue.

        An example cURL to a waiting room could be::

           curl -X GET "https://example.com/waitingroom" \\
           	-H "Accept: application/json"

        If ``json_response_enabled`` is **true** and the request hits the waiting room, an example JSON response when ``queueingMethod`` is **fifo** and no event is active could be::

           {
           	"cfWaitingRoom": {
           		"inWaitingRoom": true,
           		"waitTimeKnown": true,
           		"waitTime": 10,
           		"waitTime25Percentile": 0,
           		"waitTime50Percentile": 0,
           		"waitTime75Percentile": 0,
           		"waitTimeFormatted": "10 minutes",
           		"queueIsFull": false,
           		"queueAll": false,
           		"lastUpdated": "2020-08-03T23:46:00.000Z",
           		"refreshIntervalSeconds": 20,
           		"queueingMethod": "fifo",
           		"isFIFOQueue": true,
           		"isRandomQueue": false,
           		"isPassthroughQueue": false,
           		"isRejectQueue": false,
           		"isEventActive": false,
           		"isEventPrequeueing": false,
           		"timeUntilEventStart": 0,
           		"timeUntilEventStartFormatted": "unavailable",
           		"timeUntilEventEnd": 0,
           		"timeUntilEventEndFormatted": "unavailable",
           		"shuffleAtEventStart": false
           	}
           }

        If ``json_response_enabled`` is **true** and the request hits the waiting room, an example JSON response when ``queueingMethod`` is **random** and an event is active could be::

           {
           	"cfWaitingRoom": {
           		"inWaitingRoom": true,
           		"waitTimeKnown": true,
           		"waitTime": 10,
           		"waitTime25Percentile": 5,
           		"waitTime50Percentile": 10,
           		"waitTime75Percentile": 15,
           		"waitTimeFormatted": "5 minutes to 15 minutes",
           		"queueIsFull": false,
           		"queueAll": false,
           		"lastUpdated": "2020-08-03T23:46:00.000Z",
           		"refreshIntervalSeconds": 20,
           		"queueingMethod": "random",
           		"isFIFOQueue": false,
           		"isRandomQueue": true,
           		"isPassthroughQueue": false,
           		"isRejectQueue": false,
           		"isEventActive": true,
           		"isEventPrequeueing": false,
           		"timeUntilEventStart": 0,
           		"timeUntilEventStartFormatted": "unavailable",
           		"timeUntilEventEnd": 15,
           		"timeUntilEventEndFormatted": "15 minutes",
           		"shuffleAtEventStart": true
           	}
           }

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#json_response_enabled WaitingRoom#json_response_enabled}
        '''
        result = self._values.get("json_response_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Sets the path within the host to enable the waiting room on.

        The waiting room will be enabled for all subpaths as well. If there are two waiting rooms on the same subpath, the waiting room for the most specific path will be chosen. Wildcards and query parameters are not supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#path WaitingRoom#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_all(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If queue_all is ``true``, all the traffic that is coming to a route will be sent to the waiting room.

        No new traffic can get to the route once this field is set and estimated time will become unavailable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#queue_all WaitingRoom#queue_all}
        '''
        result = self._values.get("queue_all")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def queueing_method(self) -> typing.Optional[builtins.str]:
        '''Sets the queueing method used by the waiting room.

        Changing this parameter from the **default** queueing method is only available for the Waiting Room Advanced subscription. Regardless of the queueing method, if ``queue_all`` is enabled or an event is prequeueing, users in the waiting room will not be accepted to the origin. These users will always see a waiting room page that refreshes automatically. The valid queueing methods are:

        1. ``fifo`` **(default)**: First-In-First-Out queue where customers gain access in the order they arrived.
        2. ``random``: Random queue where customers gain access randomly, regardless of arrival time.
        3. ``passthrough``: Users will pass directly through the waiting room and into the origin website. As a result, any configured limits will not be respected while this is enabled. This method can be used as an alternative to disabling a waiting room (with ``suspended``) so that analytics are still reported. This can be used if you wish to allow all traffic normally, but want to restrict traffic during a waiting room event, or vice versa.
        4. ``reject``: Users will be immediately rejected from the waiting room. As a result, no users will reach the origin website while this is enabled. This can be used if you wish to reject all traffic while performing maintenance, block traffic during a specified period of time (an event), or block traffic while events are not occurring. Consider a waiting room used for vaccine distribution that only allows traffic during sign-up events, and otherwise blocks all traffic. For this case, the waiting room uses ``reject``, and its events override this with ``fifo``, ``random``, or ``passthrough``. When this queueing method is enabled and neither ``queueAll`` is enabled nor an event is prequeueing, the waiting room page **will not refresh automatically**.
           Available values: "fifo", "random", "passthrough", "reject".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#queueing_method WaitingRoom#queueing_method}
        '''
        result = self._values.get("queueing_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queueing_status_code(self) -> typing.Optional[jsii.Number]:
        '''HTTP status code returned to a user while in the queue. Available values: 200, 202, 429.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#queueing_status_code WaitingRoom#queueing_status_code}
        '''
        result = self._values.get("queueing_status_code")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def session_duration(self) -> typing.Optional[jsii.Number]:
        '''Lifetime of a cookie (in minutes) set by Cloudflare for users who get access to the route.

        If a user is not seen by Cloudflare again in that time period, they will be treated as a new user that visits the route.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#session_duration WaitingRoom#session_duration}
        '''
        result = self._values.get("session_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def suspended(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Suspends or allows traffic going to the waiting room.

        If set to ``true``, the traffic will not go to the waiting room.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#suspended WaitingRoom#suspended}
        '''
        result = self._values.get("suspended")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def turnstile_action(self) -> typing.Optional[builtins.str]:
        '''Which action to take when a bot is detected using Turnstile.

        ``log`` will
        have no impact on queueing behavior, simply keeping track of how many
        bots are detected in Waiting Room Analytics. ``infinite_queue`` will send
        bots to a false queueing state, where they will never reach your
        origin. ``infinite_queue`` requires Advanced Waiting Room.
        Available values: "log", "infinite_queue".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#turnstile_action WaitingRoom#turnstile_action}
        '''
        result = self._values.get("turnstile_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def turnstile_mode(self) -> typing.Optional[builtins.str]:
        '''Which Turnstile widget type to use for detecting bot traffic.

        See
        `the Turnstile documentation <https://developers.cloudflare.com/turnstile/concepts/widget/#widget-types>`_
        for the definitions of these widget types. Set to ``off`` to disable the
        Turnstile integration entirely. Setting this to anything other than
        ``off`` or ``invisible`` requires Advanced Waiting Room.
        Available values: "off", "invisible", "visible_non_interactive", "visible_managed".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#turnstile_mode WaitingRoom#turnstile_mode}
        '''
        result = self._values.get("turnstile_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaitingRoomConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.waitingRoom.WaitingRoomCookieAttributes",
    jsii_struct_bases=[],
    name_mapping={"samesite": "samesite", "secure": "secure"},
)
class WaitingRoomCookieAttributes:
    def __init__(
        self,
        *,
        samesite: typing.Optional[builtins.str] = None,
        secure: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param samesite: Configures the SameSite attribute on the waiting room cookie. Value ``auto`` will be translated to ``lax`` or ``none`` depending if **Always Use HTTPS** is enabled. Note that when using value ``none``, the secure attribute cannot be set to ``never``. Available values: "auto", "lax", "none", "strict". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#samesite WaitingRoom#samesite}
        :param secure: Configures the Secure attribute on the waiting room cookie. Value ``always`` indicates that the Secure attribute will be set in the Set-Cookie header, ``never`` indicates that the Secure attribute will not be set, and ``auto`` will set the Secure attribute depending if **Always Use HTTPS** is enabled. Available values: "auto", "always", "never". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#secure WaitingRoom#secure}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b152f7e9a5b2530e1e588756865297e6fb46b755b208383c21519bbd904c9878)
            check_type(argname="argument samesite", value=samesite, expected_type=type_hints["samesite"])
            check_type(argname="argument secure", value=secure, expected_type=type_hints["secure"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if samesite is not None:
            self._values["samesite"] = samesite
        if secure is not None:
            self._values["secure"] = secure

    @builtins.property
    def samesite(self) -> typing.Optional[builtins.str]:
        '''Configures the SameSite attribute on the waiting room cookie.

        Value ``auto`` will be translated to ``lax`` or ``none`` depending if **Always Use HTTPS** is enabled. Note that when using value ``none``, the secure attribute cannot be set to ``never``.
        Available values: "auto", "lax", "none", "strict".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#samesite WaitingRoom#samesite}
        '''
        result = self._values.get("samesite")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure(self) -> typing.Optional[builtins.str]:
        '''Configures the Secure attribute on the waiting room cookie.

        Value ``always`` indicates that the Secure attribute will be set in the Set-Cookie header, ``never`` indicates that the Secure attribute will not be set, and ``auto`` will set the Secure attribute depending if **Always Use HTTPS** is enabled.
        Available values: "auto", "always", "never".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/waiting_room#secure WaitingRoom#secure}
        '''
        result = self._values.get("secure")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaitingRoomCookieAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WaitingRoomCookieAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.waitingRoom.WaitingRoomCookieAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d817515f42e11fb213c1c3c2ec770e2a2ee4fa1d0b40a28142808c8ef1811be3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSamesite")
    def reset_samesite(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamesite", []))

    @jsii.member(jsii_name="resetSecure")
    def reset_secure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecure", []))

    @builtins.property
    @jsii.member(jsii_name="samesiteInput")
    def samesite_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "samesiteInput"))

    @builtins.property
    @jsii.member(jsii_name="secureInput")
    def secure_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureInput"))

    @builtins.property
    @jsii.member(jsii_name="samesite")
    def samesite(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samesite"))

    @samesite.setter
    def samesite(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__629d7f39375a838d1965745fef2926005ea5ea8d384d2eb0aa2c4f53c588c6a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samesite", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secure")
    def secure(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secure"))

    @secure.setter
    def secure(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06dcf769dd21703f080a4abf1a68a099aa7e5f472866f4ebf4d4228001215a03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaitingRoomCookieAttributes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaitingRoomCookieAttributes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaitingRoomCookieAttributes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41b7adbfd4ce8f70600e23419c557c9e31422db5834774711fd5c411ab8d99f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "WaitingRoom",
    "WaitingRoomAdditionalRoutes",
    "WaitingRoomAdditionalRoutesList",
    "WaitingRoomAdditionalRoutesOutputReference",
    "WaitingRoomConfig",
    "WaitingRoomCookieAttributes",
    "WaitingRoomCookieAttributesOutputReference",
]

publication.publish()

def _typecheckingstub__d737128371b91dc67e76dc498443dc339a660aa9509d247243c49a6c9f5a6d80(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    host: builtins.str,
    name: builtins.str,
    new_users_per_minute: jsii.Number,
    total_active_users: jsii.Number,
    zone_id: builtins.str,
    additional_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WaitingRoomAdditionalRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cookie_attributes: typing.Optional[typing.Union[WaitingRoomCookieAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    cookie_suffix: typing.Optional[builtins.str] = None,
    custom_page_html: typing.Optional[builtins.str] = None,
    default_template_language: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    disable_session_renewal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled_origin_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    json_response_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    path: typing.Optional[builtins.str] = None,
    queue_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    queueing_method: typing.Optional[builtins.str] = None,
    queueing_status_code: typing.Optional[jsii.Number] = None,
    session_duration: typing.Optional[jsii.Number] = None,
    suspended: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__2c8ba1a8303d4f5bf6554fd049a351613fed75363ba1b8207380deee3bce37c6(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cf4353ea8ebcd430fd9bd55b8073b7d188c7ae9fea814051bc1ae54f12b393c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WaitingRoomAdditionalRoutes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0113aba5715352b30835ab2d9521bab3d08fa5ca2d22378d460cf321e5d02ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00c09cb9ece44f399d78d953e46df87b8436fa04c2cc6fb0c118c0589e144379(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__969d8244c2f72aaa4ee1c5d68a01df650631f899d5b3592e6c7ee246068a7d9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f30d0cb2906b147f6cf4f8372df5283d1e846cd119a8d8f23eb3a868af4060b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59ad261883326e9a9804b22864a7b94dfd7185bd735cb99ac76189594fceeb6f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f64d94b76d28912d5562eb5e34e60e37d2d378c66178b5ed480801772015ddb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0209441a13abea89a612cc455d474cffbe978ccfa3e6c7641606c3fba5d750f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7f88dea94bc4c673e79b7e30ffd6b4785c3765bba6d21634ec47ba87f61fbaa(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdf77968b4f2854b1a4a67b3e46d1fdbbb3011fd2a8971cffb8747bdc0c164df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a1b91c649c55391030282e67f922293c72f360190666c593e9f9b3f762b814e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__311db3e13367a00c1bb9bc9f9fbe22338d52ed8c9b53246bf0187ddfd2fdb7eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41e8a601ee2eec0d8b5e3ecd699e09e9dffc8c546ae84b92f3b49e540d19df79(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__387c1b2a7e715268ed49e011f33ac68b2248b2cb9a60e2890b342126fbf89951(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df84ee66405b1bdbe97546ad84ba7bb8bf0cd76cf474540a9423919af13caba4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b38fc44390838c7fa98c179cc12a76e97e9c10f093104ed6754915746232677(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb516a930e2ad062317a964a4c17be49c8ecc7f83a1e24818b756377ec64b1b9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00e9745f39e08ed798ec32b953cbf71156d2913ae8b2d984cab9cc9d13cfb961(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5bfbfd5ae94b2f7b2772f5577c5175157b9a7758b204dd4829eb012304366f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0564066a94ab07953f33cf0221de344342aea75dbba4c72c17ca4f398915e0cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bda4fb123f4ab106fe556d19e569abbfda45e0f076496ba9135d7b7fe0fd3df1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdfb6532add76d6bea1045eb30caceb1f75cf06fdedee2355b6d15b3b113b375(
    *,
    host: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82391e6cadf783ca577cb508838d2cc2140d044d5624c6b1c65bf18a97a398f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aea769387e6f82ba47a2044f42f4687b3886f293372d42a2fb6459cff30376d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e48b982227594aab1578a69edfe2e290766f80393d50ed3c9f0f11954b480246(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b946c5e29b6d714e1e62260433ae316faf1a62690702a9a6b3396de960a30d43(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ebbc2d995b57d9deb7580125263db7d4fe9133607b85905dad058812cd53620(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f8a5d3fbbdb2a76e2352943ee304b19ae87f4d317001e2a71d6c8fc7789e449(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WaitingRoomAdditionalRoutes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae709a4421a77f02eae903189df705a706e8919fa8f3f135527012f3297dc7d4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed57513211478266f9b051b8c668000cc0d134b466eb0bec7c8e967f354a339a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__589cf52257c11028282e63efcb47d19ab246f8d5a311a7ac332ac4e679c12add(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fcee894f2e2742c6a802808f752867aa6223bb8e2aa064484658c530f0e9882(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaitingRoomAdditionalRoutes]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71218a0efc55f5ae63de81f8f8687b06300c02b6514087e449eefe5fcf43c58c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    host: builtins.str,
    name: builtins.str,
    new_users_per_minute: jsii.Number,
    total_active_users: jsii.Number,
    zone_id: builtins.str,
    additional_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WaitingRoomAdditionalRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cookie_attributes: typing.Optional[typing.Union[WaitingRoomCookieAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    cookie_suffix: typing.Optional[builtins.str] = None,
    custom_page_html: typing.Optional[builtins.str] = None,
    default_template_language: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    disable_session_renewal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled_origin_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    json_response_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    path: typing.Optional[builtins.str] = None,
    queue_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    queueing_method: typing.Optional[builtins.str] = None,
    queueing_status_code: typing.Optional[jsii.Number] = None,
    session_duration: typing.Optional[jsii.Number] = None,
    suspended: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    turnstile_action: typing.Optional[builtins.str] = None,
    turnstile_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b152f7e9a5b2530e1e588756865297e6fb46b755b208383c21519bbd904c9878(
    *,
    samesite: typing.Optional[builtins.str] = None,
    secure: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d817515f42e11fb213c1c3c2ec770e2a2ee4fa1d0b40a28142808c8ef1811be3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__629d7f39375a838d1965745fef2926005ea5ea8d384d2eb0aa2c4f53c588c6a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06dcf769dd21703f080a4abf1a68a099aa7e5f472866f4ebf4d4228001215a03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41b7adbfd4ce8f70600e23419c557c9e31422db5834774711fd5c411ab8d99f7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaitingRoomCookieAttributes]],
) -> None:
    """Type checking stubs"""
    pass
