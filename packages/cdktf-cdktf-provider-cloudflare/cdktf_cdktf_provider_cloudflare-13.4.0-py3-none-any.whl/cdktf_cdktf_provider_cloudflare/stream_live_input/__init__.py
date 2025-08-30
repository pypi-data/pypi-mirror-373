r'''
# `cloudflare_stream_live_input`

Refer to the Terraform Registry for docs: [`cloudflare_stream_live_input`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input).
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


class StreamLiveInput(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInput",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input cloudflare_stream_live_input}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        default_creator: typing.Optional[builtins.str] = None,
        delete_recording_after_days: typing.Optional[jsii.Number] = None,
        live_input_identifier: typing.Optional[builtins.str] = None,
        meta: typing.Optional[builtins.str] = None,
        recording: typing.Optional[typing.Union["StreamLiveInputRecording", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input cloudflare_stream_live_input} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#account_id StreamLiveInput#account_id}
        :param default_creator: Sets the creator ID asssociated with this live input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#default_creator StreamLiveInput#default_creator}
        :param delete_recording_after_days: Indicates the number of days after which the live inputs recordings will be deleted. When a stream completes and the recording is ready, the value is used to calculate a scheduled deletion date for that recording. Omit the field to indicate no change, or include with a ``null`` value to remove an existing scheduled deletion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#delete_recording_after_days StreamLiveInput#delete_recording_after_days}
        :param live_input_identifier: A unique identifier for a live input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#live_input_identifier StreamLiveInput#live_input_identifier}
        :param meta: A user modifiable key-value store used to reference other systems of record for managing live inputs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#meta StreamLiveInput#meta}
        :param recording: Records the input to a Cloudflare Stream video. Behavior depends on the mode. In most cases, the video will initially be viewable as a live video and transition to on-demand after a condition is satisfied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#recording StreamLiveInput#recording}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__088908ad533aa1dc757fc17e35dfdf9ea90ed9c74528b38bc89cf100ea929b63)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = StreamLiveInputConfig(
            account_id=account_id,
            default_creator=default_creator,
            delete_recording_after_days=delete_recording_after_days,
            live_input_identifier=live_input_identifier,
            meta=meta,
            recording=recording,
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
        '''Generates CDKTF code for importing a StreamLiveInput resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the StreamLiveInput to import.
        :param import_from_id: The id of the existing StreamLiveInput that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the StreamLiveInput to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c7eb64b09566686d4d0ccf6dc1ce904a93278bf076a175ceba8ec9ea28a38d6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putRecording")
    def put_recording(
        self,
        *,
        allowed_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        hide_live_viewer_count: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        mode: typing.Optional[builtins.str] = None,
        require_signed_urls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allowed_origins: Lists the origins allowed to display videos created with this input. Enter allowed origin domains in an array and use ``*`` for wildcard subdomains. An empty array allows videos to be viewed on any origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#allowed_origins StreamLiveInput#allowed_origins}
        :param hide_live_viewer_count: Disables reporting the number of live viewers when this property is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#hide_live_viewer_count StreamLiveInput#hide_live_viewer_count}
        :param mode: Specifies the recording behavior for the live input. Set this value to ``off`` to prevent a recording. Set the value to ``automatic`` to begin a recording and transition to on-demand after Stream Live stops receiving input. Available values: "off", "automatic". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#mode StreamLiveInput#mode}
        :param require_signed_urls: Indicates if a video using the live input has the ``requireSignedURLs`` property set. Also enforces access controls on any video recording of the livestream with the live input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#require_signed_urls StreamLiveInput#require_signed_urls}
        :param timeout_seconds: Determines the amount of time a live input configured in ``automatic`` mode should wait before a recording transitions from live to on-demand. ``0`` is recommended for most use cases and indicates the platform default should be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#timeout_seconds StreamLiveInput#timeout_seconds}
        '''
        value = StreamLiveInputRecording(
            allowed_origins=allowed_origins,
            hide_live_viewer_count=hide_live_viewer_count,
            mode=mode,
            require_signed_urls=require_signed_urls,
            timeout_seconds=timeout_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putRecording", [value]))

    @jsii.member(jsii_name="resetDefaultCreator")
    def reset_default_creator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultCreator", []))

    @jsii.member(jsii_name="resetDeleteRecordingAfterDays")
    def reset_delete_recording_after_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteRecordingAfterDays", []))

    @jsii.member(jsii_name="resetLiveInputIdentifier")
    def reset_live_input_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLiveInputIdentifier", []))

    @jsii.member(jsii_name="resetMeta")
    def reset_meta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMeta", []))

    @jsii.member(jsii_name="resetRecording")
    def reset_recording(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecording", []))

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
    @jsii.member(jsii_name="modified")
    def modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modified"))

    @builtins.property
    @jsii.member(jsii_name="recording")
    def recording(self) -> "StreamLiveInputRecordingOutputReference":
        return typing.cast("StreamLiveInputRecordingOutputReference", jsii.get(self, "recording"))

    @builtins.property
    @jsii.member(jsii_name="rtmps")
    def rtmps(self) -> "StreamLiveInputRtmpsOutputReference":
        return typing.cast("StreamLiveInputRtmpsOutputReference", jsii.get(self, "rtmps"))

    @builtins.property
    @jsii.member(jsii_name="rtmpsPlayback")
    def rtmps_playback(self) -> "StreamLiveInputRtmpsPlaybackOutputReference":
        return typing.cast("StreamLiveInputRtmpsPlaybackOutputReference", jsii.get(self, "rtmpsPlayback"))

    @builtins.property
    @jsii.member(jsii_name="srt")
    def srt(self) -> "StreamLiveInputSrtOutputReference":
        return typing.cast("StreamLiveInputSrtOutputReference", jsii.get(self, "srt"))

    @builtins.property
    @jsii.member(jsii_name="srtPlayback")
    def srt_playback(self) -> "StreamLiveInputSrtPlaybackOutputReference":
        return typing.cast("StreamLiveInputSrtPlaybackOutputReference", jsii.get(self, "srtPlayback"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="webRtc")
    def web_rtc(self) -> "StreamLiveInputWebRtcOutputReference":
        return typing.cast("StreamLiveInputWebRtcOutputReference", jsii.get(self, "webRtc"))

    @builtins.property
    @jsii.member(jsii_name="webRtcPlayback")
    def web_rtc_playback(self) -> "StreamLiveInputWebRtcPlaybackOutputReference":
        return typing.cast("StreamLiveInputWebRtcPlaybackOutputReference", jsii.get(self, "webRtcPlayback"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultCreatorInput")
    def default_creator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultCreatorInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteRecordingAfterDaysInput")
    def delete_recording_after_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deleteRecordingAfterDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="liveInputIdentifierInput")
    def live_input_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "liveInputIdentifierInput"))

    @builtins.property
    @jsii.member(jsii_name="metaInput")
    def meta_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metaInput"))

    @builtins.property
    @jsii.member(jsii_name="recordingInput")
    def recording_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamLiveInputRecording"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamLiveInputRecording"]], jsii.get(self, "recordingInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d5272e13cdee786560aa8402647be5069a141dcd771b707a50f8784c6f0508d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultCreator")
    def default_creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultCreator"))

    @default_creator.setter
    def default_creator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84633d8faf9db13b478f6745f48325b7b861cd7ad82ac7ea12014f8cebc791ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultCreator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deleteRecordingAfterDays")
    def delete_recording_after_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deleteRecordingAfterDays"))

    @delete_recording_after_days.setter
    def delete_recording_after_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a8e30287186029f5b447d11738afbd88f4a0208e6a94f313bb7557ae9e56e89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteRecordingAfterDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="liveInputIdentifier")
    def live_input_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "liveInputIdentifier"))

    @live_input_identifier.setter
    def live_input_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dbad3321c18aea4a8e30fdf9dc1a35279ad6d93287213334632f580fcd78cae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "liveInputIdentifier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="meta")
    def meta(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "meta"))

    @meta.setter
    def meta(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f39d13e35b4822d65ae19f7c1af39c10bd531bcc1e75464d6d26e38044913c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "meta", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputConfig",
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
        "default_creator": "defaultCreator",
        "delete_recording_after_days": "deleteRecordingAfterDays",
        "live_input_identifier": "liveInputIdentifier",
        "meta": "meta",
        "recording": "recording",
    },
)
class StreamLiveInputConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        default_creator: typing.Optional[builtins.str] = None,
        delete_recording_after_days: typing.Optional[jsii.Number] = None,
        live_input_identifier: typing.Optional[builtins.str] = None,
        meta: typing.Optional[builtins.str] = None,
        recording: typing.Optional[typing.Union["StreamLiveInputRecording", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#account_id StreamLiveInput#account_id}
        :param default_creator: Sets the creator ID asssociated with this live input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#default_creator StreamLiveInput#default_creator}
        :param delete_recording_after_days: Indicates the number of days after which the live inputs recordings will be deleted. When a stream completes and the recording is ready, the value is used to calculate a scheduled deletion date for that recording. Omit the field to indicate no change, or include with a ``null`` value to remove an existing scheduled deletion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#delete_recording_after_days StreamLiveInput#delete_recording_after_days}
        :param live_input_identifier: A unique identifier for a live input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#live_input_identifier StreamLiveInput#live_input_identifier}
        :param meta: A user modifiable key-value store used to reference other systems of record for managing live inputs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#meta StreamLiveInput#meta}
        :param recording: Records the input to a Cloudflare Stream video. Behavior depends on the mode. In most cases, the video will initially be viewable as a live video and transition to on-demand after a condition is satisfied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#recording StreamLiveInput#recording}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(recording, dict):
            recording = StreamLiveInputRecording(**recording)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94a2999b489082d620557d728e444ee9161b26ae27aac1808f8f2640512bf8d8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument default_creator", value=default_creator, expected_type=type_hints["default_creator"])
            check_type(argname="argument delete_recording_after_days", value=delete_recording_after_days, expected_type=type_hints["delete_recording_after_days"])
            check_type(argname="argument live_input_identifier", value=live_input_identifier, expected_type=type_hints["live_input_identifier"])
            check_type(argname="argument meta", value=meta, expected_type=type_hints["meta"])
            check_type(argname="argument recording", value=recording, expected_type=type_hints["recording"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
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
        if default_creator is not None:
            self._values["default_creator"] = default_creator
        if delete_recording_after_days is not None:
            self._values["delete_recording_after_days"] = delete_recording_after_days
        if live_input_identifier is not None:
            self._values["live_input_identifier"] = live_input_identifier
        if meta is not None:
            self._values["meta"] = meta
        if recording is not None:
            self._values["recording"] = recording

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#account_id StreamLiveInput#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def default_creator(self) -> typing.Optional[builtins.str]:
        '''Sets the creator ID asssociated with this live input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#default_creator StreamLiveInput#default_creator}
        '''
        result = self._values.get("default_creator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_recording_after_days(self) -> typing.Optional[jsii.Number]:
        '''Indicates the number of days after which the live inputs recordings will be deleted.

        When a stream completes and the recording is ready, the value is used to calculate a scheduled deletion date for that recording. Omit the field to indicate no change, or include with a ``null`` value to remove an existing scheduled deletion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#delete_recording_after_days StreamLiveInput#delete_recording_after_days}
        '''
        result = self._values.get("delete_recording_after_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def live_input_identifier(self) -> typing.Optional[builtins.str]:
        '''A unique identifier for a live input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#live_input_identifier StreamLiveInput#live_input_identifier}
        '''
        result = self._values.get("live_input_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def meta(self) -> typing.Optional[builtins.str]:
        '''A user modifiable key-value store used to reference other systems of record for managing live inputs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#meta StreamLiveInput#meta}
        '''
        result = self._values.get("meta")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recording(self) -> typing.Optional["StreamLiveInputRecording"]:
        '''Records the input to a Cloudflare Stream video.

        Behavior depends on the mode. In most cases, the video will initially be viewable as a live video and transition to on-demand after a condition is satisfied.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#recording StreamLiveInput#recording}
        '''
        result = self._values.get("recording")
        return typing.cast(typing.Optional["StreamLiveInputRecording"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamLiveInputConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputRecording",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_origins": "allowedOrigins",
        "hide_live_viewer_count": "hideLiveViewerCount",
        "mode": "mode",
        "require_signed_urls": "requireSignedUrls",
        "timeout_seconds": "timeoutSeconds",
    },
)
class StreamLiveInputRecording:
    def __init__(
        self,
        *,
        allowed_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        hide_live_viewer_count: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        mode: typing.Optional[builtins.str] = None,
        require_signed_urls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allowed_origins: Lists the origins allowed to display videos created with this input. Enter allowed origin domains in an array and use ``*`` for wildcard subdomains. An empty array allows videos to be viewed on any origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#allowed_origins StreamLiveInput#allowed_origins}
        :param hide_live_viewer_count: Disables reporting the number of live viewers when this property is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#hide_live_viewer_count StreamLiveInput#hide_live_viewer_count}
        :param mode: Specifies the recording behavior for the live input. Set this value to ``off`` to prevent a recording. Set the value to ``automatic`` to begin a recording and transition to on-demand after Stream Live stops receiving input. Available values: "off", "automatic". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#mode StreamLiveInput#mode}
        :param require_signed_urls: Indicates if a video using the live input has the ``requireSignedURLs`` property set. Also enforces access controls on any video recording of the livestream with the live input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#require_signed_urls StreamLiveInput#require_signed_urls}
        :param timeout_seconds: Determines the amount of time a live input configured in ``automatic`` mode should wait before a recording transitions from live to on-demand. ``0`` is recommended for most use cases and indicates the platform default should be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#timeout_seconds StreamLiveInput#timeout_seconds}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30bbe0fb3c47d7546da04989a7481a28ef3729eda1bce1f03b1fc4a2b1c0d15e)
            check_type(argname="argument allowed_origins", value=allowed_origins, expected_type=type_hints["allowed_origins"])
            check_type(argname="argument hide_live_viewer_count", value=hide_live_viewer_count, expected_type=type_hints["hide_live_viewer_count"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument require_signed_urls", value=require_signed_urls, expected_type=type_hints["require_signed_urls"])
            check_type(argname="argument timeout_seconds", value=timeout_seconds, expected_type=type_hints["timeout_seconds"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_origins is not None:
            self._values["allowed_origins"] = allowed_origins
        if hide_live_viewer_count is not None:
            self._values["hide_live_viewer_count"] = hide_live_viewer_count
        if mode is not None:
            self._values["mode"] = mode
        if require_signed_urls is not None:
            self._values["require_signed_urls"] = require_signed_urls
        if timeout_seconds is not None:
            self._values["timeout_seconds"] = timeout_seconds

    @builtins.property
    def allowed_origins(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Lists the origins allowed to display videos created with this input.

        Enter allowed origin domains in an array and use ``*`` for wildcard subdomains. An empty array allows videos to be viewed on any origin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#allowed_origins StreamLiveInput#allowed_origins}
        '''
        result = self._values.get("allowed_origins")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def hide_live_viewer_count(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disables reporting the number of live viewers when this property is set to ``true``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#hide_live_viewer_count StreamLiveInput#hide_live_viewer_count}
        '''
        result = self._values.get("hide_live_viewer_count")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Specifies the recording behavior for the live input.

        Set this value to ``off`` to prevent a recording. Set the value to ``automatic`` to begin a recording and transition to on-demand after Stream Live stops receiving input.
        Available values: "off", "automatic".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#mode StreamLiveInput#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def require_signed_urls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if a video using the live input has the ``requireSignedURLs`` property set.

        Also enforces access controls on any video recording of the livestream with the live input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#require_signed_urls StreamLiveInput#require_signed_urls}
        '''
        result = self._values.get("require_signed_urls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Determines the amount of time a live input configured in ``automatic`` mode should wait before a recording transitions from live to on-demand.

        ``0`` is recommended for most use cases and indicates the platform default should be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream_live_input#timeout_seconds StreamLiveInput#timeout_seconds}
        '''
        result = self._values.get("timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamLiveInputRecording(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamLiveInputRecordingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputRecordingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2e5db24a571356b64689b09d444fa5b86c3bf54bacbaf9ee6dc8c75da73b91f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowedOrigins")
    def reset_allowed_origins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOrigins", []))

    @jsii.member(jsii_name="resetHideLiveViewerCount")
    def reset_hide_live_viewer_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHideLiveViewerCount", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetRequireSignedUrls")
    def reset_require_signed_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireSignedUrls", []))

    @jsii.member(jsii_name="resetTimeoutSeconds")
    def reset_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutSeconds", []))

    @builtins.property
    @jsii.member(jsii_name="allowedOriginsInput")
    def allowed_origins_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOriginsInput"))

    @builtins.property
    @jsii.member(jsii_name="hideLiveViewerCountInput")
    def hide_live_viewer_count_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hideLiveViewerCountInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="requireSignedUrlsInput")
    def require_signed_urls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requireSignedUrlsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutSecondsInput")
    def timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedOrigins")
    def allowed_origins(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOrigins"))

    @allowed_origins.setter
    def allowed_origins(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a56c5d466763c8b6a93ce7f008a5480cbcffa726600b272ccc895da9de7c6fe7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedOrigins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hideLiveViewerCount")
    def hide_live_viewer_count(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "hideLiveViewerCount"))

    @hide_live_viewer_count.setter
    def hide_live_viewer_count(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b988bc80d6d1aeb7f456fe75ee399a4feef15b1d68b21c2a7a8930286e8f6493)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hideLiveViewerCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34b4d318a8881be21bc198a8db5835a6cfe20ee4d7ba98c3f5f5672fdac1a0e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requireSignedUrls")
    def require_signed_urls(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "requireSignedUrls"))

    @require_signed_urls.setter
    def require_signed_urls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80cdc1e76889cb5d5cb31dd810134cbd860e73d8fa4a88ab467a7396083acb83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireSignedUrls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeoutSeconds")
    def timeout_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutSeconds"))

    @timeout_seconds.setter
    def timeout_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__644f8543dc96d42febb0c78ac6fe1d461df156038ed7f6d116fcfcec1d94de33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamLiveInputRecording]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamLiveInputRecording]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamLiveInputRecording]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__493d70fd4352c546c51018908749c03c484c297e03a060d7120a3d9f572d7a65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputRtmps",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamLiveInputRtmps:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamLiveInputRtmps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamLiveInputRtmpsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputRtmpsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da42ec97522e2abfa7a19233b79ffda9287d1a4492deec85fd96a033c5fd06f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="streamKey")
    def stream_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamKey"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamLiveInputRtmps]:
        return typing.cast(typing.Optional[StreamLiveInputRtmps], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StreamLiveInputRtmps]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__884152b07f3ec7e6cb644a62fe25062f9de25ade596ac8d923212a38a67df874)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputRtmpsPlayback",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamLiveInputRtmpsPlayback:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamLiveInputRtmpsPlayback(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamLiveInputRtmpsPlaybackOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputRtmpsPlaybackOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2f7f05cefb3f4a730c0ef01da6fcbf9a477847850aad66e863ad681403a99511)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="streamKey")
    def stream_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamKey"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamLiveInputRtmpsPlayback]:
        return typing.cast(typing.Optional[StreamLiveInputRtmpsPlayback], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StreamLiveInputRtmpsPlayback],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf17a17c7f8b281fdcd0a5b82c6792106e7e618e681caf5a9c709a159052d3ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputSrt",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamLiveInputSrt:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamLiveInputSrt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamLiveInputSrtOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputSrtOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2f5de9a7e1516b12f97e5c8c8981da6ef5a42bf6ac8641ad3a322183d69a5eb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="passphrase")
    def passphrase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passphrase"))

    @builtins.property
    @jsii.member(jsii_name="streamId")
    def stream_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamId"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamLiveInputSrt]:
        return typing.cast(typing.Optional[StreamLiveInputSrt], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StreamLiveInputSrt]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d6347fca1d426b09e21858e531317ed2cfb5aaf1705021aa44ade2f59f6f6e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputSrtPlayback",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamLiveInputSrtPlayback:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamLiveInputSrtPlayback(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamLiveInputSrtPlaybackOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputSrtPlaybackOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ad592f553912d2705621ef33e4b7525e47aae9f5db6e41c816e0063044a3d25)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="passphrase")
    def passphrase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passphrase"))

    @builtins.property
    @jsii.member(jsii_name="streamId")
    def stream_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamId"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamLiveInputSrtPlayback]:
        return typing.cast(typing.Optional[StreamLiveInputSrtPlayback], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StreamLiveInputSrtPlayback],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a61dd5bc41298c4ab0c91cf363278214e0f0eb503db1a0bafa0323c174fbd00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputWebRtc",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamLiveInputWebRtc:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamLiveInputWebRtc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamLiveInputWebRtcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputWebRtcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26e2d67aa47cfa0b6aaa89e5c53fd3eaaafcdc997e6c391d78940e0c6e42a824)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamLiveInputWebRtc]:
        return typing.cast(typing.Optional[StreamLiveInputWebRtc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StreamLiveInputWebRtc]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__445e7a5c687f82f7698d3b5709c5d6f44f7a82bd92a3e9f11ccb7036b4c4b24d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputWebRtcPlayback",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamLiveInputWebRtcPlayback:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamLiveInputWebRtcPlayback(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamLiveInputWebRtcPlaybackOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.streamLiveInput.StreamLiveInputWebRtcPlaybackOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8135bc8aebc35790a9b09cc58866b9a9e963e387395bf2d86bd0110240aef89a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamLiveInputWebRtcPlayback]:
        return typing.cast(typing.Optional[StreamLiveInputWebRtcPlayback], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StreamLiveInputWebRtcPlayback],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bfad4e1beccd4dacad59fc30a0bab266316f8465ec5100b4f9d0add203eebbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "StreamLiveInput",
    "StreamLiveInputConfig",
    "StreamLiveInputRecording",
    "StreamLiveInputRecordingOutputReference",
    "StreamLiveInputRtmps",
    "StreamLiveInputRtmpsOutputReference",
    "StreamLiveInputRtmpsPlayback",
    "StreamLiveInputRtmpsPlaybackOutputReference",
    "StreamLiveInputSrt",
    "StreamLiveInputSrtOutputReference",
    "StreamLiveInputSrtPlayback",
    "StreamLiveInputSrtPlaybackOutputReference",
    "StreamLiveInputWebRtc",
    "StreamLiveInputWebRtcOutputReference",
    "StreamLiveInputWebRtcPlayback",
    "StreamLiveInputWebRtcPlaybackOutputReference",
]

publication.publish()

def _typecheckingstub__088908ad533aa1dc757fc17e35dfdf9ea90ed9c74528b38bc89cf100ea929b63(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    default_creator: typing.Optional[builtins.str] = None,
    delete_recording_after_days: typing.Optional[jsii.Number] = None,
    live_input_identifier: typing.Optional[builtins.str] = None,
    meta: typing.Optional[builtins.str] = None,
    recording: typing.Optional[typing.Union[StreamLiveInputRecording, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__3c7eb64b09566686d4d0ccf6dc1ce904a93278bf076a175ceba8ec9ea28a38d6(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d5272e13cdee786560aa8402647be5069a141dcd771b707a50f8784c6f0508d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84633d8faf9db13b478f6745f48325b7b861cd7ad82ac7ea12014f8cebc791ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a8e30287186029f5b447d11738afbd88f4a0208e6a94f313bb7557ae9e56e89(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dbad3321c18aea4a8e30fdf9dc1a35279ad6d93287213334632f580fcd78cae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f39d13e35b4822d65ae19f7c1af39c10bd531bcc1e75464d6d26e38044913c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a2999b489082d620557d728e444ee9161b26ae27aac1808f8f2640512bf8d8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    default_creator: typing.Optional[builtins.str] = None,
    delete_recording_after_days: typing.Optional[jsii.Number] = None,
    live_input_identifier: typing.Optional[builtins.str] = None,
    meta: typing.Optional[builtins.str] = None,
    recording: typing.Optional[typing.Union[StreamLiveInputRecording, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30bbe0fb3c47d7546da04989a7481a28ef3729eda1bce1f03b1fc4a2b1c0d15e(
    *,
    allowed_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
    hide_live_viewer_count: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    mode: typing.Optional[builtins.str] = None,
    require_signed_urls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    timeout_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2e5db24a571356b64689b09d444fa5b86c3bf54bacbaf9ee6dc8c75da73b91f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a56c5d466763c8b6a93ce7f008a5480cbcffa726600b272ccc895da9de7c6fe7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b988bc80d6d1aeb7f456fe75ee399a4feef15b1d68b21c2a7a8930286e8f6493(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34b4d318a8881be21bc198a8db5835a6cfe20ee4d7ba98c3f5f5672fdac1a0e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80cdc1e76889cb5d5cb31dd810134cbd860e73d8fa4a88ab467a7396083acb83(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__644f8543dc96d42febb0c78ac6fe1d461df156038ed7f6d116fcfcec1d94de33(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__493d70fd4352c546c51018908749c03c484c297e03a060d7120a3d9f572d7a65(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamLiveInputRecording]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da42ec97522e2abfa7a19233b79ffda9287d1a4492deec85fd96a033c5fd06f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__884152b07f3ec7e6cb644a62fe25062f9de25ade596ac8d923212a38a67df874(
    value: typing.Optional[StreamLiveInputRtmps],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f7f05cefb3f4a730c0ef01da6fcbf9a477847850aad66e863ad681403a99511(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf17a17c7f8b281fdcd0a5b82c6792106e7e618e681caf5a9c709a159052d3ed(
    value: typing.Optional[StreamLiveInputRtmpsPlayback],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f5de9a7e1516b12f97e5c8c8981da6ef5a42bf6ac8641ad3a322183d69a5eb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d6347fca1d426b09e21858e531317ed2cfb5aaf1705021aa44ade2f59f6f6e3(
    value: typing.Optional[StreamLiveInputSrt],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ad592f553912d2705621ef33e4b7525e47aae9f5db6e41c816e0063044a3d25(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a61dd5bc41298c4ab0c91cf363278214e0f0eb503db1a0bafa0323c174fbd00(
    value: typing.Optional[StreamLiveInputSrtPlayback],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26e2d67aa47cfa0b6aaa89e5c53fd3eaaafcdc997e6c391d78940e0c6e42a824(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__445e7a5c687f82f7698d3b5709c5d6f44f7a82bd92a3e9f11ccb7036b4c4b24d(
    value: typing.Optional[StreamLiveInputWebRtc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8135bc8aebc35790a9b09cc58866b9a9e963e387395bf2d86bd0110240aef89a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bfad4e1beccd4dacad59fc30a0bab266316f8465ec5100b4f9d0add203eebbc(
    value: typing.Optional[StreamLiveInputWebRtcPlayback],
) -> None:
    """Type checking stubs"""
    pass
