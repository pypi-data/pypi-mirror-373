r'''
# `cloudflare_stream`

Refer to the Terraform Registry for docs: [`cloudflare_stream`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream).
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


class Stream(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.stream.Stream",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream cloudflare_stream}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        allowed_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        creator: typing.Optional[builtins.str] = None,
        identifier: typing.Optional[builtins.str] = None,
        max_duration_seconds: typing.Optional[jsii.Number] = None,
        meta: typing.Optional[builtins.str] = None,
        require_signed_urls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scheduled_deletion: typing.Optional[builtins.str] = None,
        thumbnail_timestamp_pct: typing.Optional[jsii.Number] = None,
        upload_expiry: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream cloudflare_stream} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The account identifier tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#account_id Stream#account_id}
        :param allowed_origins: Lists the origins allowed to display the video. Enter allowed origin domains in an array and use ``*`` for wildcard subdomains. Empty arrays allow the video to be viewed on any origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#allowed_origins Stream#allowed_origins}
        :param creator: A user-defined identifier for the media creator. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#creator Stream#creator}
        :param identifier: A Cloudflare-generated unique identifier for a media item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#identifier Stream#identifier}
        :param max_duration_seconds: The maximum duration in seconds for a video upload. Can be set for a video that is not yet uploaded to limit its duration. Uploads that exceed the specified duration will fail during processing. A value of ``-1`` means the value is unknown. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#max_duration_seconds Stream#max_duration_seconds}
        :param meta: A user modifiable key-value store used to reference other systems of record for managing videos. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#meta Stream#meta}
        :param require_signed_urls: Indicates whether the video can be a accessed using the UID. When set to ``true``, a signed token must be generated with a signing key to view the video. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#require_signed_urls Stream#require_signed_urls}
        :param scheduled_deletion: Indicates the date and time at which the video will be deleted. Omit the field to indicate no change, or include with a ``null`` value to remove an existing scheduled deletion. If specified, must be at least 30 days from upload time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#scheduled_deletion Stream#scheduled_deletion}
        :param thumbnail_timestamp_pct: The timestamp for a thumbnail image calculated as a percentage value of the video's duration. To convert from a second-wise timestamp to a percentage, divide the desired timestamp by the total duration of the video. If this value is not set, the default thumbnail image is taken from 0s of the video. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#thumbnail_timestamp_pct Stream#thumbnail_timestamp_pct}
        :param upload_expiry: The date and time when the video upload URL is no longer valid for direct user uploads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#upload_expiry Stream#upload_expiry}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f526664dc1e0dd4bb2cd6262169984b97470ce79f821c92ab87a21cbd69b9f2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = StreamConfig(
            account_id=account_id,
            allowed_origins=allowed_origins,
            creator=creator,
            identifier=identifier,
            max_duration_seconds=max_duration_seconds,
            meta=meta,
            require_signed_urls=require_signed_urls,
            scheduled_deletion=scheduled_deletion,
            thumbnail_timestamp_pct=thumbnail_timestamp_pct,
            upload_expiry=upload_expiry,
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
        '''Generates CDKTF code for importing a Stream resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Stream to import.
        :param import_from_id: The id of the existing Stream that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Stream to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9af9603ec2768f54b9dd355413c07e66e37455fddf577653ee255c97af9b4989)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowedOrigins")
    def reset_allowed_origins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOrigins", []))

    @jsii.member(jsii_name="resetCreator")
    def reset_creator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreator", []))

    @jsii.member(jsii_name="resetIdentifier")
    def reset_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentifier", []))

    @jsii.member(jsii_name="resetMaxDurationSeconds")
    def reset_max_duration_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxDurationSeconds", []))

    @jsii.member(jsii_name="resetMeta")
    def reset_meta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMeta", []))

    @jsii.member(jsii_name="resetRequireSignedUrls")
    def reset_require_signed_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireSignedUrls", []))

    @jsii.member(jsii_name="resetScheduledDeletion")
    def reset_scheduled_deletion(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheduledDeletion", []))

    @jsii.member(jsii_name="resetThumbnailTimestampPct")
    def reset_thumbnail_timestamp_pct(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThumbnailTimestampPct", []))

    @jsii.member(jsii_name="resetUploadExpiry")
    def reset_upload_expiry(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUploadExpiry", []))

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
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @builtins.property
    @jsii.member(jsii_name="input")
    def input(self) -> "StreamInputOutputReference":
        return typing.cast("StreamInputOutputReference", jsii.get(self, "input"))

    @builtins.property
    @jsii.member(jsii_name="liveInput")
    def live_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "liveInput"))

    @builtins.property
    @jsii.member(jsii_name="modified")
    def modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modified"))

    @builtins.property
    @jsii.member(jsii_name="playback")
    def playback(self) -> "StreamPlaybackOutputReference":
        return typing.cast("StreamPlaybackOutputReference", jsii.get(self, "playback"))

    @builtins.property
    @jsii.member(jsii_name="preview")
    def preview(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preview"))

    @builtins.property
    @jsii.member(jsii_name="readyToStream")
    def ready_to_stream(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "readyToStream"))

    @builtins.property
    @jsii.member(jsii_name="readyToStreamAt")
    def ready_to_stream_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readyToStreamAt"))

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> "StreamStatusOutputReference":
        return typing.cast("StreamStatusOutputReference", jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="thumbnail")
    def thumbnail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thumbnail"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="uploaded")
    def uploaded(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uploaded"))

    @builtins.property
    @jsii.member(jsii_name="watermark")
    def watermark(self) -> "StreamWatermarkOutputReference":
        return typing.cast("StreamWatermarkOutputReference", jsii.get(self, "watermark"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedOriginsInput")
    def allowed_origins_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOriginsInput"))

    @builtins.property
    @jsii.member(jsii_name="creatorInput")
    def creator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creatorInput"))

    @builtins.property
    @jsii.member(jsii_name="identifierInput")
    def identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifierInput"))

    @builtins.property
    @jsii.member(jsii_name="maxDurationSecondsInput")
    def max_duration_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxDurationSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="metaInput")
    def meta_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metaInput"))

    @builtins.property
    @jsii.member(jsii_name="requireSignedUrlsInput")
    def require_signed_urls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requireSignedUrlsInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduledDeletionInput")
    def scheduled_deletion_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scheduledDeletionInput"))

    @builtins.property
    @jsii.member(jsii_name="thumbnailTimestampPctInput")
    def thumbnail_timestamp_pct_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thumbnailTimestampPctInput"))

    @builtins.property
    @jsii.member(jsii_name="uploadExpiryInput")
    def upload_expiry_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uploadExpiryInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73dc4eb3fbef06f5081e73a214abd00364859847ac6859d8e1312214cbd9ce47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedOrigins")
    def allowed_origins(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOrigins"))

    @allowed_origins.setter
    def allowed_origins(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad5fe7e0816990650058e78b8fad2c4d3958a4a4a454efed71972c2e7e3e6d9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedOrigins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @creator.setter
    def creator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b60c1842689776def038a1c953def0a18c4e440bd292dc17a8d23d33169cc3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identifier"))

    @identifier.setter
    def identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1301fae358fcf779252422e703e6921e139fa780f53066406c02788f2d5fd0f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identifier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxDurationSeconds")
    def max_duration_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxDurationSeconds"))

    @max_duration_seconds.setter
    def max_duration_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca93ef2a2742473b00e2a46c5c8e65fb52c9df790308f1eef0b437b3dc6e8ba2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxDurationSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="meta")
    def meta(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "meta"))

    @meta.setter
    def meta(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1eb0f1d5ab6d52088a8518543e31e0e5f6d7a350fb448e9d5a4c3acc43a2986)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "meta", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__ae2c7c14f1705ce1b89f8db33ed8a678f766201c92728e42cc56b99008debfa2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireSignedUrls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scheduledDeletion")
    def scheduled_deletion(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheduledDeletion"))

    @scheduled_deletion.setter
    def scheduled_deletion(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a68f88a86e3b2e00bac86fb512e28a94d3cbfbc2155403710fc9aff2c7fd9ce8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheduledDeletion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="thumbnailTimestampPct")
    def thumbnail_timestamp_pct(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "thumbnailTimestampPct"))

    @thumbnail_timestamp_pct.setter
    def thumbnail_timestamp_pct(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92e711ba03f3c83bc67d40c264c232cde5bc77e9d02c9b44de0198ea4252b368)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "thumbnailTimestampPct", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uploadExpiry")
    def upload_expiry(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uploadExpiry"))

    @upload_expiry.setter
    def upload_expiry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d3b6b3d394f24787579a64dcd8eeebdb2b420509513b6f30ce5fe26f9ae966a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uploadExpiry", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.stream.StreamConfig",
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
        "allowed_origins": "allowedOrigins",
        "creator": "creator",
        "identifier": "identifier",
        "max_duration_seconds": "maxDurationSeconds",
        "meta": "meta",
        "require_signed_urls": "requireSignedUrls",
        "scheduled_deletion": "scheduledDeletion",
        "thumbnail_timestamp_pct": "thumbnailTimestampPct",
        "upload_expiry": "uploadExpiry",
    },
)
class StreamConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allowed_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        creator: typing.Optional[builtins.str] = None,
        identifier: typing.Optional[builtins.str] = None,
        max_duration_seconds: typing.Optional[jsii.Number] = None,
        meta: typing.Optional[builtins.str] = None,
        require_signed_urls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scheduled_deletion: typing.Optional[builtins.str] = None,
        thumbnail_timestamp_pct: typing.Optional[jsii.Number] = None,
        upload_expiry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: The account identifier tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#account_id Stream#account_id}
        :param allowed_origins: Lists the origins allowed to display the video. Enter allowed origin domains in an array and use ``*`` for wildcard subdomains. Empty arrays allow the video to be viewed on any origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#allowed_origins Stream#allowed_origins}
        :param creator: A user-defined identifier for the media creator. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#creator Stream#creator}
        :param identifier: A Cloudflare-generated unique identifier for a media item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#identifier Stream#identifier}
        :param max_duration_seconds: The maximum duration in seconds for a video upload. Can be set for a video that is not yet uploaded to limit its duration. Uploads that exceed the specified duration will fail during processing. A value of ``-1`` means the value is unknown. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#max_duration_seconds Stream#max_duration_seconds}
        :param meta: A user modifiable key-value store used to reference other systems of record for managing videos. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#meta Stream#meta}
        :param require_signed_urls: Indicates whether the video can be a accessed using the UID. When set to ``true``, a signed token must be generated with a signing key to view the video. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#require_signed_urls Stream#require_signed_urls}
        :param scheduled_deletion: Indicates the date and time at which the video will be deleted. Omit the field to indicate no change, or include with a ``null`` value to remove an existing scheduled deletion. If specified, must be at least 30 days from upload time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#scheduled_deletion Stream#scheduled_deletion}
        :param thumbnail_timestamp_pct: The timestamp for a thumbnail image calculated as a percentage value of the video's duration. To convert from a second-wise timestamp to a percentage, divide the desired timestamp by the total duration of the video. If this value is not set, the default thumbnail image is taken from 0s of the video. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#thumbnail_timestamp_pct Stream#thumbnail_timestamp_pct}
        :param upload_expiry: The date and time when the video upload URL is no longer valid for direct user uploads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#upload_expiry Stream#upload_expiry}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a708985c272c9c0a997e36ffa3882dfedede079bdd2d9b2124c4b95405a7811f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument allowed_origins", value=allowed_origins, expected_type=type_hints["allowed_origins"])
            check_type(argname="argument creator", value=creator, expected_type=type_hints["creator"])
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument max_duration_seconds", value=max_duration_seconds, expected_type=type_hints["max_duration_seconds"])
            check_type(argname="argument meta", value=meta, expected_type=type_hints["meta"])
            check_type(argname="argument require_signed_urls", value=require_signed_urls, expected_type=type_hints["require_signed_urls"])
            check_type(argname="argument scheduled_deletion", value=scheduled_deletion, expected_type=type_hints["scheduled_deletion"])
            check_type(argname="argument thumbnail_timestamp_pct", value=thumbnail_timestamp_pct, expected_type=type_hints["thumbnail_timestamp_pct"])
            check_type(argname="argument upload_expiry", value=upload_expiry, expected_type=type_hints["upload_expiry"])
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
        if allowed_origins is not None:
            self._values["allowed_origins"] = allowed_origins
        if creator is not None:
            self._values["creator"] = creator
        if identifier is not None:
            self._values["identifier"] = identifier
        if max_duration_seconds is not None:
            self._values["max_duration_seconds"] = max_duration_seconds
        if meta is not None:
            self._values["meta"] = meta
        if require_signed_urls is not None:
            self._values["require_signed_urls"] = require_signed_urls
        if scheduled_deletion is not None:
            self._values["scheduled_deletion"] = scheduled_deletion
        if thumbnail_timestamp_pct is not None:
            self._values["thumbnail_timestamp_pct"] = thumbnail_timestamp_pct
        if upload_expiry is not None:
            self._values["upload_expiry"] = upload_expiry

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
        '''The account identifier tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#account_id Stream#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_origins(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Lists the origins allowed to display the video.

        Enter allowed origin domains in an array and use ``*`` for wildcard subdomains. Empty arrays allow the video to be viewed on any origin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#allowed_origins Stream#allowed_origins}
        '''
        result = self._values.get("allowed_origins")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def creator(self) -> typing.Optional[builtins.str]:
        '''A user-defined identifier for the media creator.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#creator Stream#creator}
        '''
        result = self._values.get("creator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''A Cloudflare-generated unique identifier for a media item.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#identifier Stream#identifier}
        '''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_duration_seconds(self) -> typing.Optional[jsii.Number]:
        '''The maximum duration in seconds for a video upload.

        Can be set for a video that is not yet uploaded to limit its duration. Uploads that exceed the specified duration will fail during processing. A value of ``-1`` means the value is unknown.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#max_duration_seconds Stream#max_duration_seconds}
        '''
        result = self._values.get("max_duration_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def meta(self) -> typing.Optional[builtins.str]:
        '''A user modifiable key-value store used to reference other systems of record for managing videos.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#meta Stream#meta}
        '''
        result = self._values.get("meta")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def require_signed_urls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether the video can be a accessed using the UID.

        When set to ``true``, a signed token must be generated with a signing key to view the video.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#require_signed_urls Stream#require_signed_urls}
        '''
        result = self._values.get("require_signed_urls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def scheduled_deletion(self) -> typing.Optional[builtins.str]:
        '''Indicates the date and time at which the video will be deleted.

        Omit the field to indicate no change, or include with a ``null`` value to remove an existing scheduled deletion. If specified, must be at least 30 days from upload time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#scheduled_deletion Stream#scheduled_deletion}
        '''
        result = self._values.get("scheduled_deletion")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def thumbnail_timestamp_pct(self) -> typing.Optional[jsii.Number]:
        '''The timestamp for a thumbnail image calculated as a percentage value of the video's duration.

        To convert from a second-wise timestamp to a percentage, divide the desired timestamp by the total duration of the video.  If this value is not set, the default thumbnail image is taken from 0s of the video.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#thumbnail_timestamp_pct Stream#thumbnail_timestamp_pct}
        '''
        result = self._values.get("thumbnail_timestamp_pct")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def upload_expiry(self) -> typing.Optional[builtins.str]:
        '''The date and time when the video upload URL is no longer valid for direct user uploads.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/stream#upload_expiry Stream#upload_expiry}
        '''
        result = self._values.get("upload_expiry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.stream.StreamInput",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamInput:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamInput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamInputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.stream.StreamInputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e2fba45158b1cbbf14a32ac94aea01ad7b4fbf8fe94bfcd9a9f4c405e1e3ab7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="height")
    def height(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "height"))

    @builtins.property
    @jsii.member(jsii_name="width")
    def width(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "width"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamInput]:
        return typing.cast(typing.Optional[StreamInput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StreamInput]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84215a8d73bbe4646ac1dac8b57c1be2fc813f758add93cb01a2135782eae9f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.stream.StreamPlayback",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamPlayback:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamPlayback(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamPlaybackOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.stream.StreamPlaybackOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e82364a6fdc5c03b7fce0c90b5f6abd17dec013a938621119819d990cc3d47e7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="dash")
    def dash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dash"))

    @builtins.property
    @jsii.member(jsii_name="hls")
    def hls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hls"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamPlayback]:
        return typing.cast(typing.Optional[StreamPlayback], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StreamPlayback]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__339b590d8f319ec9d862c872ef3f488f9a49e1ba6c057d566f2a2a6a99ab2823)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.stream.StreamStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.stream.StreamStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e3464106605f203002d51af58125354684183b172608ca0e17f40b324c9bd66)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="errorReasonCode")
    def error_reason_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorReasonCode"))

    @builtins.property
    @jsii.member(jsii_name="errorReasonText")
    def error_reason_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorReasonText"))

    @builtins.property
    @jsii.member(jsii_name="pctComplete")
    def pct_complete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pctComplete"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamStatus]:
        return typing.cast(typing.Optional[StreamStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StreamStatus]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab2c24df4874def2defcda3d21cc09b3f35e2e787cca0eb186bbe262d5f485c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.stream.StreamWatermark",
    jsii_struct_bases=[],
    name_mapping={},
)
class StreamWatermark:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamWatermark(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamWatermarkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.stream.StreamWatermarkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9d4d44ca9944837df18c59da07e7c84d22e8a224c426da8ac259bb5729bee355)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="created")
    def created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "created"))

    @builtins.property
    @jsii.member(jsii_name="downloadedFrom")
    def downloaded_from(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "downloadedFrom"))

    @builtins.property
    @jsii.member(jsii_name="height")
    def height(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "height"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="opacity")
    def opacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "opacity"))

    @builtins.property
    @jsii.member(jsii_name="padding")
    def padding(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "padding"))

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "position"))

    @builtins.property
    @jsii.member(jsii_name="scale")
    def scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scale"))

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="width")
    def width(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "width"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamWatermark]:
        return typing.cast(typing.Optional[StreamWatermark], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StreamWatermark]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2a2e1ec5810a30ed3d02dec10287496ba71b8701e62d2a609091f664487619c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Stream",
    "StreamConfig",
    "StreamInput",
    "StreamInputOutputReference",
    "StreamPlayback",
    "StreamPlaybackOutputReference",
    "StreamStatus",
    "StreamStatusOutputReference",
    "StreamWatermark",
    "StreamWatermarkOutputReference",
]

publication.publish()

def _typecheckingstub__2f526664dc1e0dd4bb2cd6262169984b97470ce79f821c92ab87a21cbd69b9f2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    allowed_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
    creator: typing.Optional[builtins.str] = None,
    identifier: typing.Optional[builtins.str] = None,
    max_duration_seconds: typing.Optional[jsii.Number] = None,
    meta: typing.Optional[builtins.str] = None,
    require_signed_urls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    scheduled_deletion: typing.Optional[builtins.str] = None,
    thumbnail_timestamp_pct: typing.Optional[jsii.Number] = None,
    upload_expiry: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__9af9603ec2768f54b9dd355413c07e66e37455fddf577653ee255c97af9b4989(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73dc4eb3fbef06f5081e73a214abd00364859847ac6859d8e1312214cbd9ce47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad5fe7e0816990650058e78b8fad2c4d3958a4a4a454efed71972c2e7e3e6d9b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b60c1842689776def038a1c953def0a18c4e440bd292dc17a8d23d33169cc3c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1301fae358fcf779252422e703e6921e139fa780f53066406c02788f2d5fd0f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca93ef2a2742473b00e2a46c5c8e65fb52c9df790308f1eef0b437b3dc6e8ba2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1eb0f1d5ab6d52088a8518543e31e0e5f6d7a350fb448e9d5a4c3acc43a2986(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae2c7c14f1705ce1b89f8db33ed8a678f766201c92728e42cc56b99008debfa2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a68f88a86e3b2e00bac86fb512e28a94d3cbfbc2155403710fc9aff2c7fd9ce8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92e711ba03f3c83bc67d40c264c232cde5bc77e9d02c9b44de0198ea4252b368(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d3b6b3d394f24787579a64dcd8eeebdb2b420509513b6f30ce5fe26f9ae966a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a708985c272c9c0a997e36ffa3882dfedede079bdd2d9b2124c4b95405a7811f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    allowed_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
    creator: typing.Optional[builtins.str] = None,
    identifier: typing.Optional[builtins.str] = None,
    max_duration_seconds: typing.Optional[jsii.Number] = None,
    meta: typing.Optional[builtins.str] = None,
    require_signed_urls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    scheduled_deletion: typing.Optional[builtins.str] = None,
    thumbnail_timestamp_pct: typing.Optional[jsii.Number] = None,
    upload_expiry: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e2fba45158b1cbbf14a32ac94aea01ad7b4fbf8fe94bfcd9a9f4c405e1e3ab7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84215a8d73bbe4646ac1dac8b57c1be2fc813f758add93cb01a2135782eae9f4(
    value: typing.Optional[StreamInput],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e82364a6fdc5c03b7fce0c90b5f6abd17dec013a938621119819d990cc3d47e7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__339b590d8f319ec9d862c872ef3f488f9a49e1ba6c057d566f2a2a6a99ab2823(
    value: typing.Optional[StreamPlayback],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e3464106605f203002d51af58125354684183b172608ca0e17f40b324c9bd66(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab2c24df4874def2defcda3d21cc09b3f35e2e787cca0eb186bbe262d5f485c4(
    value: typing.Optional[StreamStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d4d44ca9944837df18c59da07e7c84d22e8a224c426da8ac259bb5729bee355(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2a2e1ec5810a30ed3d02dec10287496ba71b8701e62d2a609091f664487619c(
    value: typing.Optional[StreamWatermark],
) -> None:
    """Type checking stubs"""
    pass
