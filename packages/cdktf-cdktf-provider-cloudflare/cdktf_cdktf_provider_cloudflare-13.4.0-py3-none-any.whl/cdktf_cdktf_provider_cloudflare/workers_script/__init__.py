r'''
# `cloudflare_workers_script`

Refer to the Terraform Registry for docs: [`cloudflare_workers_script`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script).
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


class WorkersScript(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScript",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script cloudflare_workers_script}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        script_name: builtins.str,
        assets: typing.Optional[typing.Union["WorkersScriptAssets", typing.Dict[builtins.str, typing.Any]]] = None,
        bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        body_part: typing.Optional[builtins.str] = None,
        compatibility_date: typing.Optional[builtins.str] = None,
        compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        content: typing.Optional[builtins.str] = None,
        content_file: typing.Optional[builtins.str] = None,
        content_sha256: typing.Optional[builtins.str] = None,
        content_type: typing.Optional[builtins.str] = None,
        keep_assets: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        keep_bindings: typing.Optional[typing.Sequence[builtins.str]] = None,
        limits: typing.Optional[typing.Union["WorkersScriptLimits", typing.Dict[builtins.str, typing.Any]]] = None,
        logpush: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        main_module: typing.Optional[builtins.str] = None,
        migrations: typing.Optional[typing.Union["WorkersScriptMigrations", typing.Dict[builtins.str, typing.Any]]] = None,
        observability: typing.Optional[typing.Union["WorkersScriptObservability", typing.Dict[builtins.str, typing.Any]]] = None,
        placement: typing.Optional[typing.Union["WorkersScriptPlacement", typing.Dict[builtins.str, typing.Any]]] = None,
        tail_consumers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptTailConsumers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        usage_model: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script cloudflare_workers_script} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#account_id WorkersScript#account_id}
        :param script_name: Name of the script, used in URLs and route configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#script_name WorkersScript#script_name}
        :param assets: Configuration for assets within a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#assets WorkersScript#assets}
        :param bindings: List of bindings attached to a Worker. You can find more about bindings on our docs: https://developers.cloudflare.com/workers/configuration/multipart-upload-metadata/#bindings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#bindings WorkersScript#bindings}
        :param body_part: Name of the part in the multipart request that contains the script (e.g. the file adding a listener to the ``fetch`` event). Indicates a ``service worker syntax`` Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#body_part WorkersScript#body_part}
        :param compatibility_date: Date indicating targeted support in the Workers runtime. Backwards incompatible fixes to the runtime following this date will not affect this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#compatibility_date WorkersScript#compatibility_date}
        :param compatibility_flags: Flags that enable or disable certain features in the Workers runtime. Used to enable upcoming features or opt in or out of specific changes not included in a ``compatibility_date``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#compatibility_flags WorkersScript#compatibility_flags}
        :param content: Module or Service Worker contents of the Worker. Exactly one of ``content`` or ``content_file`` must be specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content WorkersScript#content}
        :param content_file: Path to a file containing the Module or Service Worker contents of the Worker. Exactly one of ``content`` or ``content_file`` must be specified. Must be paired with ``content_sha256``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content_file WorkersScript#content_file}
        :param content_sha256: SHA-256 hash of the Worker contents. Used to trigger updates when source code changes. Must be provided when ``content_file`` is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content_sha256 WorkersScript#content_sha256}
        :param content_type: Content-Type of the Worker. Required if uploading a non-JavaScript Worker (e.g. "text/x-python"). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content_type WorkersScript#content_type}
        :param keep_assets: Retain assets which exist for a previously uploaded Worker version; used in lieu of providing a completion token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#keep_assets WorkersScript#keep_assets}
        :param keep_bindings: List of binding types to keep from previous_upload. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#keep_bindings WorkersScript#keep_bindings}
        :param limits: Limits to apply for this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#limits WorkersScript#limits}
        :param logpush: Whether Logpush is turned on for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#logpush WorkersScript#logpush}
        :param main_module: Name of the part in the multipart request that contains the main module (e.g. the file exporting a ``fetch`` handler). Indicates a ``module syntax`` Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#main_module WorkersScript#main_module}
        :param migrations: Migrations to apply for Durable Objects associated with this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#migrations WorkersScript#migrations}
        :param observability: Observability settings for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#observability WorkersScript#observability}
        :param placement: Configuration for `Smart Placement <https://developers.cloudflare.com/workers/configuration/smart-placement>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#placement WorkersScript#placement}
        :param tail_consumers: List of Workers that will consume logs from the attached Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#tail_consumers WorkersScript#tail_consumers}
        :param usage_model: Usage model for the Worker invocations. Available values: "standard", "bundled", "unbound". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#usage_model WorkersScript#usage_model}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ff91a65eae39ed03c4fdb5f548361f58aa71f020d925825809f305475cc24e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = WorkersScriptConfig(
            account_id=account_id,
            script_name=script_name,
            assets=assets,
            bindings=bindings,
            body_part=body_part,
            compatibility_date=compatibility_date,
            compatibility_flags=compatibility_flags,
            content=content,
            content_file=content_file,
            content_sha256=content_sha256,
            content_type=content_type,
            keep_assets=keep_assets,
            keep_bindings=keep_bindings,
            limits=limits,
            logpush=logpush,
            main_module=main_module,
            migrations=migrations,
            observability=observability,
            placement=placement,
            tail_consumers=tail_consumers,
            usage_model=usage_model,
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
        '''Generates CDKTF code for importing a WorkersScript resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the WorkersScript to import.
        :param import_from_id: The id of the existing WorkersScript that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the WorkersScript to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2a18d8db56da9a802f4ab3dc8c0f4b0e47025df295217c56f9931fd59facc2d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAssets")
    def put_assets(
        self,
        *,
        config: typing.Optional[typing.Union["WorkersScriptAssetsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        jwt: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: Configuration for assets within a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#config WorkersScript#config}
        :param jwt: Token provided upon successful upload of all files from a registered manifest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#jwt WorkersScript#jwt}
        '''
        value = WorkersScriptAssets(config=config, jwt=jwt)

        return typing.cast(None, jsii.invoke(self, "putAssets", [value]))

    @jsii.member(jsii_name="putBindings")
    def put_bindings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptBindings", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d23c2fc7f9a34ba826f0a79d838b04f388555410c3d727a81d005e1d9a445f1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBindings", [value]))

    @jsii.member(jsii_name="putLimits")
    def put_limits(self, *, cpu_ms: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param cpu_ms: The amount of CPU time this Worker can use in milliseconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#cpu_ms WorkersScript#cpu_ms}
        '''
        value = WorkersScriptLimits(cpu_ms=cpu_ms)

        return typing.cast(None, jsii.invoke(self, "putLimits", [value]))

    @jsii.member(jsii_name="putMigrations")
    def put_migrations(
        self,
        *,
        deleted_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_sqlite_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_tag: typing.Optional[builtins.str] = None,
        old_tag: typing.Optional[builtins.str] = None,
        renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
        steps: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsSteps", typing.Dict[builtins.str, typing.Any]]]]] = None,
        transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param deleted_classes: A list of classes to delete Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#deleted_classes WorkersScript#deleted_classes}
        :param new_classes: A list of classes to create Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_classes WorkersScript#new_classes}
        :param new_sqlite_classes: A list of classes to create Durable Object namespaces with SQLite from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_sqlite_classes WorkersScript#new_sqlite_classes}
        :param new_tag: Tag to set as the latest migration tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_tag WorkersScript#new_tag}
        :param old_tag: Tag used to verify against the latest migration tag for this Worker. If they don't match, the upload is rejected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#old_tag WorkersScript#old_tag}
        :param renamed_classes: A list of classes with Durable Object namespaces that were renamed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#renamed_classes WorkersScript#renamed_classes}
        :param steps: Migrations to apply in order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#steps WorkersScript#steps}
        :param transferred_classes: A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#transferred_classes WorkersScript#transferred_classes}
        '''
        value = WorkersScriptMigrations(
            deleted_classes=deleted_classes,
            new_classes=new_classes,
            new_sqlite_classes=new_sqlite_classes,
            new_tag=new_tag,
            old_tag=old_tag,
            renamed_classes=renamed_classes,
            steps=steps,
            transferred_classes=transferred_classes,
        )

        return typing.cast(None, jsii.invoke(self, "putMigrations", [value]))

    @jsii.member(jsii_name="putObservability")
    def put_observability(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        head_sampling_rate: typing.Optional[jsii.Number] = None,
        logs: typing.Optional[typing.Union["WorkersScriptObservabilityLogs", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param enabled: Whether observability is enabled for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#enabled WorkersScript#enabled}
        :param head_sampling_rate: The sampling rate for incoming requests. From 0 to 1 (1 = 100%, 0.1 = 10%). Default is 1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#head_sampling_rate WorkersScript#head_sampling_rate}
        :param logs: Log settings for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#logs WorkersScript#logs}
        '''
        value = WorkersScriptObservability(
            enabled=enabled, head_sampling_rate=head_sampling_rate, logs=logs
        )

        return typing.cast(None, jsii.invoke(self, "putObservability", [value]))

    @jsii.member(jsii_name="putPlacement")
    def put_placement(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Enables `Smart Placement <https://developers.cloudflare.com/workers/configuration/smart-placement>`_. Available values: "smart". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#mode WorkersScript#mode}
        '''
        value = WorkersScriptPlacement(mode=mode)

        return typing.cast(None, jsii.invoke(self, "putPlacement", [value]))

    @jsii.member(jsii_name="putTailConsumers")
    def put_tail_consumers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptTailConsumers", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9dbeb6bf5de037026fd8af0f2821cdf1f095033d5aeb5bea457dbc8b27a0308)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTailConsumers", [value]))

    @jsii.member(jsii_name="resetAssets")
    def reset_assets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssets", []))

    @jsii.member(jsii_name="resetBindings")
    def reset_bindings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBindings", []))

    @jsii.member(jsii_name="resetBodyPart")
    def reset_body_part(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBodyPart", []))

    @jsii.member(jsii_name="resetCompatibilityDate")
    def reset_compatibility_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibilityDate", []))

    @jsii.member(jsii_name="resetCompatibilityFlags")
    def reset_compatibility_flags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibilityFlags", []))

    @jsii.member(jsii_name="resetContent")
    def reset_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContent", []))

    @jsii.member(jsii_name="resetContentFile")
    def reset_content_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentFile", []))

    @jsii.member(jsii_name="resetContentSha256")
    def reset_content_sha256(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentSha256", []))

    @jsii.member(jsii_name="resetContentType")
    def reset_content_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentType", []))

    @jsii.member(jsii_name="resetKeepAssets")
    def reset_keep_assets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepAssets", []))

    @jsii.member(jsii_name="resetKeepBindings")
    def reset_keep_bindings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepBindings", []))

    @jsii.member(jsii_name="resetLimits")
    def reset_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLimits", []))

    @jsii.member(jsii_name="resetLogpush")
    def reset_logpush(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogpush", []))

    @jsii.member(jsii_name="resetMainModule")
    def reset_main_module(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMainModule", []))

    @jsii.member(jsii_name="resetMigrations")
    def reset_migrations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMigrations", []))

    @jsii.member(jsii_name="resetObservability")
    def reset_observability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObservability", []))

    @jsii.member(jsii_name="resetPlacement")
    def reset_placement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlacement", []))

    @jsii.member(jsii_name="resetTailConsumers")
    def reset_tail_consumers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTailConsumers", []))

    @jsii.member(jsii_name="resetUsageModel")
    def reset_usage_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsageModel", []))

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
    @jsii.member(jsii_name="assets")
    def assets(self) -> "WorkersScriptAssetsOutputReference":
        return typing.cast("WorkersScriptAssetsOutputReference", jsii.get(self, "assets"))

    @builtins.property
    @jsii.member(jsii_name="bindings")
    def bindings(self) -> "WorkersScriptBindingsList":
        return typing.cast("WorkersScriptBindingsList", jsii.get(self, "bindings"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property
    @jsii.member(jsii_name="handlers")
    def handlers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "handlers"))

    @builtins.property
    @jsii.member(jsii_name="hasAssets")
    def has_assets(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "hasAssets"))

    @builtins.property
    @jsii.member(jsii_name="hasModules")
    def has_modules(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "hasModules"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="lastDeployedFrom")
    def last_deployed_from(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastDeployedFrom"))

    @builtins.property
    @jsii.member(jsii_name="limits")
    def limits(self) -> "WorkersScriptLimitsOutputReference":
        return typing.cast("WorkersScriptLimitsOutputReference", jsii.get(self, "limits"))

    @builtins.property
    @jsii.member(jsii_name="migrations")
    def migrations(self) -> "WorkersScriptMigrationsOutputReference":
        return typing.cast("WorkersScriptMigrationsOutputReference", jsii.get(self, "migrations"))

    @builtins.property
    @jsii.member(jsii_name="migrationTag")
    def migration_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "migrationTag"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="namedHandlers")
    def named_handlers(self) -> "WorkersScriptNamedHandlersList":
        return typing.cast("WorkersScriptNamedHandlersList", jsii.get(self, "namedHandlers"))

    @builtins.property
    @jsii.member(jsii_name="observability")
    def observability(self) -> "WorkersScriptObservabilityOutputReference":
        return typing.cast("WorkersScriptObservabilityOutputReference", jsii.get(self, "observability"))

    @builtins.property
    @jsii.member(jsii_name="placement")
    def placement(self) -> "WorkersScriptPlacementOutputReference":
        return typing.cast("WorkersScriptPlacementOutputReference", jsii.get(self, "placement"))

    @builtins.property
    @jsii.member(jsii_name="startupTimeMs")
    def startup_time_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startupTimeMs"))

    @builtins.property
    @jsii.member(jsii_name="tailConsumers")
    def tail_consumers(self) -> "WorkersScriptTailConsumersList":
        return typing.cast("WorkersScriptTailConsumersList", jsii.get(self, "tailConsumers"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="assetsInput")
    def assets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptAssets"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptAssets"]], jsii.get(self, "assetsInput"))

    @builtins.property
    @jsii.member(jsii_name="bindingsInput")
    def bindings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptBindings"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptBindings"]]], jsii.get(self, "bindingsInput"))

    @builtins.property
    @jsii.member(jsii_name="bodyPartInput")
    def body_part_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bodyPartInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityDateInput")
    def compatibility_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "compatibilityDateInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlagsInput")
    def compatibility_flags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "compatibilityFlagsInput"))

    @builtins.property
    @jsii.member(jsii_name="contentFileInput")
    def content_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentFileInput"))

    @builtins.property
    @jsii.member(jsii_name="contentInput")
    def content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentInput"))

    @builtins.property
    @jsii.member(jsii_name="contentSha256Input")
    def content_sha256_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentSha256Input"))

    @builtins.property
    @jsii.member(jsii_name="contentTypeInput")
    def content_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="keepAssetsInput")
    def keep_assets_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "keepAssetsInput"))

    @builtins.property
    @jsii.member(jsii_name="keepBindingsInput")
    def keep_bindings_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "keepBindingsInput"))

    @builtins.property
    @jsii.member(jsii_name="limitsInput")
    def limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptLimits"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptLimits"]], jsii.get(self, "limitsInput"))

    @builtins.property
    @jsii.member(jsii_name="logpushInput")
    def logpush_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logpushInput"))

    @builtins.property
    @jsii.member(jsii_name="mainModuleInput")
    def main_module_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mainModuleInput"))

    @builtins.property
    @jsii.member(jsii_name="migrationsInput")
    def migrations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptMigrations"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptMigrations"]], jsii.get(self, "migrationsInput"))

    @builtins.property
    @jsii.member(jsii_name="observabilityInput")
    def observability_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptObservability"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptObservability"]], jsii.get(self, "observabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="placementInput")
    def placement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptPlacement"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptPlacement"]], jsii.get(self, "placementInput"))

    @builtins.property
    @jsii.member(jsii_name="scriptNameInput")
    def script_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptNameInput"))

    @builtins.property
    @jsii.member(jsii_name="tailConsumersInput")
    def tail_consumers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptTailConsumers"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptTailConsumers"]]], jsii.get(self, "tailConsumersInput"))

    @builtins.property
    @jsii.member(jsii_name="usageModelInput")
    def usage_model_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usageModelInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb2ca3c27f6a6700ee28e3832fcae15db049a5d2723a9a5abd3bd88fc910c53c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bodyPart")
    def body_part(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bodyPart"))

    @body_part.setter
    def body_part(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d09ccd2b30c63f9860e38dcd580c84cd7eb4ca4f5afcd9e2db01a50c398d4566)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bodyPart", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="compatibilityDate")
    def compatibility_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compatibilityDate"))

    @compatibility_date.setter
    def compatibility_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a46bd088570853c2b5d25072bad96f40225ab4162b4c5b1822d3c87bd6810a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compatibilityDate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlags")
    def compatibility_flags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibilityFlags"))

    @compatibility_flags.setter
    def compatibility_flags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__decdadb6de4f79ad4960d73aa391c3abf6546ecb024fa20d96613a183d671be1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compatibilityFlags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @content.setter
    def content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__020e04151b7603f4ce7a71ecc71bbe500fe9298103161c4ea64a898fc07bbe21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "content", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contentFile")
    def content_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentFile"))

    @content_file.setter
    def content_file(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b766e3bb95b4cbec0079c5072b6e87240bc4e61fa065986626bff666a944c8ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contentSha256")
    def content_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentSha256"))

    @content_sha256.setter
    def content_sha256(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c1177f60389f5d5320d5b88ee5774d867680c41e0a66621da71a936eda3e441)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentSha256", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f221590a541bf73dba256c50369c0a23c45d4dce5a7874c70e65d1732edb101d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepAssets")
    def keep_assets(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "keepAssets"))

    @keep_assets.setter
    def keep_assets(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13eb92bc492a7673b76351d0dffba81f119311503a2c2ee2517a6e4ef6fc6dc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepAssets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepBindings")
    def keep_bindings(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "keepBindings"))

    @keep_bindings.setter
    def keep_bindings(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dbef9532ad7ff8b5a3102859e96c58db44a4be7e3e5713486f310a1e8893c08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepBindings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logpush")
    def logpush(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logpush"))

    @logpush.setter
    def logpush(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15514dbe74dbfe1fad3f9886bc5c24270ced70991f6ab14e8672103ae6fc8b2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logpush", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mainModule")
    def main_module(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mainModule"))

    @main_module.setter
    def main_module(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__469f27b32ea89216e4dbc4e30a98fb9803600dd95f317d78898dc6d8d95f2b8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mainModule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptName")
    def script_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scriptName"))

    @script_name.setter
    def script_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77dfe2bc85769bce53963ca545bc276956cf465a6f7543034268baf566765a12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usageModel")
    def usage_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usageModel"))

    @usage_model.setter
    def usage_model(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00107ec9a9eb93096aedd4f6f48676a35a7af59c8416e26c3b0970c4caebf720)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usageModel", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptAssets",
    jsii_struct_bases=[],
    name_mapping={"config": "config", "jwt": "jwt"},
)
class WorkersScriptAssets:
    def __init__(
        self,
        *,
        config: typing.Optional[typing.Union["WorkersScriptAssetsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        jwt: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: Configuration for assets within a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#config WorkersScript#config}
        :param jwt: Token provided upon successful upload of all files from a registered manifest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#jwt WorkersScript#jwt}
        '''
        if isinstance(config, dict):
            config = WorkersScriptAssetsConfig(**config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0280169838b98e1dd5475ed04cefe33ccd39cb9f74769d6331f48f2ecde2d191)
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument jwt", value=jwt, expected_type=type_hints["jwt"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config is not None:
            self._values["config"] = config
        if jwt is not None:
            self._values["jwt"] = jwt

    @builtins.property
    def config(self) -> typing.Optional["WorkersScriptAssetsConfig"]:
        '''Configuration for assets within a Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#config WorkersScript#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional["WorkersScriptAssetsConfig"], result)

    @builtins.property
    def jwt(self) -> typing.Optional[builtins.str]:
        '''Token provided upon successful upload of all files from a registered manifest.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#jwt WorkersScript#jwt}
        '''
        result = self._values.get("jwt")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptAssets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptAssetsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "headers": "headers",
        "html_handling": "htmlHandling",
        "not_found_handling": "notFoundHandling",
        "redirects": "redirects",
        "run_worker_first": "runWorkerFirst",
        "serve_directly": "serveDirectly",
    },
)
class WorkersScriptAssetsConfig:
    def __init__(
        self,
        *,
        headers: typing.Optional[builtins.str] = None,
        html_handling: typing.Optional[builtins.str] = None,
        not_found_handling: typing.Optional[builtins.str] = None,
        redirects: typing.Optional[builtins.str] = None,
        run_worker_first: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        serve_directly: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param headers: The contents of a _headers file (used to attach custom headers on asset responses). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#headers WorkersScript#headers}
        :param html_handling: Determines the redirects and rewrites of requests for HTML content. Available values: "auto-trailing-slash", "force-trailing-slash", "drop-trailing-slash", "none". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#html_handling WorkersScript#html_handling}
        :param not_found_handling: Determines the response when a request does not match a static asset, and there is no Worker script. Available values: "none", "404-page", "single-page-application". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#not_found_handling WorkersScript#not_found_handling}
        :param redirects: The contents of a _redirects file (used to apply redirects or proxy paths ahead of asset serving). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#redirects WorkersScript#redirects}
        :param run_worker_first: When true, requests will always invoke the Worker script. Otherwise, attempt to serve an asset matching the request, falling back to the Worker script. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#run_worker_first WorkersScript#run_worker_first}
        :param serve_directly: When true and the incoming request matches an asset, that will be served instead of invoking the Worker script. When false, requests will always invoke the Worker script. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#serve_directly WorkersScript#serve_directly}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe00299ab5032efa34983e9e6ddfdb4b709a45de5199407d803d7a6a6056f081)
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument html_handling", value=html_handling, expected_type=type_hints["html_handling"])
            check_type(argname="argument not_found_handling", value=not_found_handling, expected_type=type_hints["not_found_handling"])
            check_type(argname="argument redirects", value=redirects, expected_type=type_hints["redirects"])
            check_type(argname="argument run_worker_first", value=run_worker_first, expected_type=type_hints["run_worker_first"])
            check_type(argname="argument serve_directly", value=serve_directly, expected_type=type_hints["serve_directly"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if headers is not None:
            self._values["headers"] = headers
        if html_handling is not None:
            self._values["html_handling"] = html_handling
        if not_found_handling is not None:
            self._values["not_found_handling"] = not_found_handling
        if redirects is not None:
            self._values["redirects"] = redirects
        if run_worker_first is not None:
            self._values["run_worker_first"] = run_worker_first
        if serve_directly is not None:
            self._values["serve_directly"] = serve_directly

    @builtins.property
    def headers(self) -> typing.Optional[builtins.str]:
        '''The contents of a _headers file (used to attach custom headers on asset responses).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#headers WorkersScript#headers}
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def html_handling(self) -> typing.Optional[builtins.str]:
        '''Determines the redirects and rewrites of requests for HTML content. Available values: "auto-trailing-slash", "force-trailing-slash", "drop-trailing-slash", "none".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#html_handling WorkersScript#html_handling}
        '''
        result = self._values.get("html_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_found_handling(self) -> typing.Optional[builtins.str]:
        '''Determines the response when a request does not match a static asset, and there is no Worker script.

        Available values: "none", "404-page", "single-page-application".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#not_found_handling WorkersScript#not_found_handling}
        '''
        result = self._values.get("not_found_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redirects(self) -> typing.Optional[builtins.str]:
        '''The contents of a _redirects file (used to apply redirects or proxy paths ahead of asset serving).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#redirects WorkersScript#redirects}
        '''
        result = self._values.get("redirects")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_worker_first(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When true, requests will always invoke the Worker script.

        Otherwise, attempt to serve an asset matching the request, falling back to the Worker script.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#run_worker_first WorkersScript#run_worker_first}
        '''
        result = self._values.get("run_worker_first")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def serve_directly(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When true and the incoming request matches an asset, that will be served instead of invoking the Worker script.

        When false, requests will always invoke the Worker script.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#serve_directly WorkersScript#serve_directly}
        '''
        result = self._values.get("serve_directly")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptAssetsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptAssetsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptAssetsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__746e455dda28a2f2d3f86fb7ac841593886895f7a02c7f0436405f343bef0f8d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @jsii.member(jsii_name="resetHtmlHandling")
    def reset_html_handling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHtmlHandling", []))

    @jsii.member(jsii_name="resetNotFoundHandling")
    def reset_not_found_handling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotFoundHandling", []))

    @jsii.member(jsii_name="resetRedirects")
    def reset_redirects(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirects", []))

    @jsii.member(jsii_name="resetRunWorkerFirst")
    def reset_run_worker_first(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunWorkerFirst", []))

    @jsii.member(jsii_name="resetServeDirectly")
    def reset_serve_directly(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServeDirectly", []))

    @builtins.property
    @jsii.member(jsii_name="headersInput")
    def headers_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headersInput"))

    @builtins.property
    @jsii.member(jsii_name="htmlHandlingInput")
    def html_handling_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "htmlHandlingInput"))

    @builtins.property
    @jsii.member(jsii_name="notFoundHandlingInput")
    def not_found_handling_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notFoundHandlingInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectsInput")
    def redirects_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redirectsInput"))

    @builtins.property
    @jsii.member(jsii_name="runWorkerFirstInput")
    def run_worker_first_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "runWorkerFirstInput"))

    @builtins.property
    @jsii.member(jsii_name="serveDirectlyInput")
    def serve_directly_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serveDirectlyInput"))

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77f454c26d6da8babd045208a102fb098809e8dbca42d49de22d71f66e2693a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="htmlHandling")
    def html_handling(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlHandling"))

    @html_handling.setter
    def html_handling(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42b364bc843bb93e1833e45bd7bf6b22043bc0315751b22989982d9763e1fb8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "htmlHandling", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notFoundHandling")
    def not_found_handling(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notFoundHandling"))

    @not_found_handling.setter
    def not_found_handling(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a01b5ad052c0ef1260bf5e43dc3649c694581c5ec1494e7fa56d3b432d1f080)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notFoundHandling", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="redirects")
    def redirects(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redirects"))

    @redirects.setter
    def redirects(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__341dbc90cb71c1d05f43dc26685a544ddbab8ad8dc2f6954bbefc29222faa969)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redirects", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runWorkerFirst")
    def run_worker_first(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "runWorkerFirst"))

    @run_worker_first.setter
    def run_worker_first(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__104247b332ae471047a1ebd8d23c64839530dc375d9e06deed488d0b3af3e0cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runWorkerFirst", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serveDirectly")
    def serve_directly(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serveDirectly"))

    @serve_directly.setter
    def serve_directly(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7edb6842f86f5b237e1d292f61d454909d8a5bcde705f4aa6949aa51d682c7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serveDirectly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssetsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssetsConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssetsConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0c06c67ecd56e53226fccc96b3dedde70c5ffd4927927d6fde830870fadf520)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkersScriptAssetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptAssetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64a6d8d68c3ae9935622ed6dc67d4b8f0a062261f4ff55043f1a193f49bf4174)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        headers: typing.Optional[builtins.str] = None,
        html_handling: typing.Optional[builtins.str] = None,
        not_found_handling: typing.Optional[builtins.str] = None,
        redirects: typing.Optional[builtins.str] = None,
        run_worker_first: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        serve_directly: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param headers: The contents of a _headers file (used to attach custom headers on asset responses). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#headers WorkersScript#headers}
        :param html_handling: Determines the redirects and rewrites of requests for HTML content. Available values: "auto-trailing-slash", "force-trailing-slash", "drop-trailing-slash", "none". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#html_handling WorkersScript#html_handling}
        :param not_found_handling: Determines the response when a request does not match a static asset, and there is no Worker script. Available values: "none", "404-page", "single-page-application". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#not_found_handling WorkersScript#not_found_handling}
        :param redirects: The contents of a _redirects file (used to apply redirects or proxy paths ahead of asset serving). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#redirects WorkersScript#redirects}
        :param run_worker_first: When true, requests will always invoke the Worker script. Otherwise, attempt to serve an asset matching the request, falling back to the Worker script. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#run_worker_first WorkersScript#run_worker_first}
        :param serve_directly: When true and the incoming request matches an asset, that will be served instead of invoking the Worker script. When false, requests will always invoke the Worker script. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#serve_directly WorkersScript#serve_directly}
        '''
        value = WorkersScriptAssetsConfig(
            headers=headers,
            html_handling=html_handling,
            not_found_handling=not_found_handling,
            redirects=redirects,
            run_worker_first=run_worker_first,
            serve_directly=serve_directly,
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="resetJwt")
    def reset_jwt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwt", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> WorkersScriptAssetsConfigOutputReference:
        return typing.cast(WorkersScriptAssetsConfigOutputReference, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssetsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssetsConfig]], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtInput")
    def jwt_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwtInput"))

    @builtins.property
    @jsii.member(jsii_name="jwt")
    def jwt(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwt"))

    @jwt.setter
    def jwt(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca46c9842b2197b5a2cbd30e9476ec0c318841ae948c62d57f1d412d7995866c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71e386a2d334f9a601c805355df8056f4ebaa7a47f87bb1c6d519fa055c8dd69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptBindings",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "type": "type",
        "algorithm": "algorithm",
        "bucket_name": "bucketName",
        "certificate_id": "certificateId",
        "class_name": "className",
        "dataset": "dataset",
        "environment": "environment",
        "format": "format",
        "id": "id",
        "index_name": "indexName",
        "json": "json",
        "key_base64": "keyBase64",
        "key_jwk": "keyJwk",
        "namespace": "namespace",
        "namespace_id": "namespaceId",
        "outbound": "outbound",
        "pipeline": "pipeline",
        "queue_name": "queueName",
        "script_name": "scriptName",
        "secret_name": "secretName",
        "service": "service",
        "store_id": "storeId",
        "text": "text",
        "usages": "usages",
        "workflow_name": "workflowName",
    },
)
class WorkersScriptBindings:
    def __init__(
        self,
        *,
        name: builtins.str,
        type: builtins.str,
        algorithm: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        certificate_id: typing.Optional[builtins.str] = None,
        class_name: typing.Optional[builtins.str] = None,
        dataset: typing.Optional[builtins.str] = None,
        environment: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        index_name: typing.Optional[builtins.str] = None,
        json: typing.Optional[builtins.str] = None,
        key_base64: typing.Optional[builtins.str] = None,
        key_jwk: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        namespace_id: typing.Optional[builtins.str] = None,
        outbound: typing.Optional[typing.Union["WorkersScriptBindingsOutbound", typing.Dict[builtins.str, typing.Any]]] = None,
        pipeline: typing.Optional[builtins.str] = None,
        queue_name: typing.Optional[builtins.str] = None,
        script_name: typing.Optional[builtins.str] = None,
        secret_name: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
        store_id: typing.Optional[builtins.str] = None,
        text: typing.Optional[builtins.str] = None,
        usages: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: A JavaScript variable name for the binding. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#name WorkersScript#name}
        :param type: The kind of resource that the binding provides. Available values: "ai", "analytics_engine", "assets", "browser", "d1", "dispatch_namespace", "durable_object_namespace", "hyperdrive", "json", "kv_namespace", "mtls_certificate", "plain_text", "pipelines", "queue", "r2_bucket", "secret_text", "service", "tail_consumer", "vectorize", "version_metadata", "secrets_store_secret", "secret_key", "workflow". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#type WorkersScript#type}
        :param algorithm: Algorithm-specific key parameters. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#algorithm>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#algorithm WorkersScript#algorithm}
        :param bucket_name: R2 bucket to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#bucket_name WorkersScript#bucket_name}
        :param certificate_id: Identifier of the certificate to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#certificate_id WorkersScript#certificate_id}
        :param class_name: The exported class name of the Durable Object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#class_name WorkersScript#class_name}
        :param dataset: The name of the dataset to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#dataset WorkersScript#dataset}
        :param environment: The environment of the script_name to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#environment WorkersScript#environment}
        :param format: Data format of the key. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#format>`_. Available values: "raw", "pkcs8", "spki", "jwk". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#format WorkersScript#format}
        :param id: Identifier of the D1 database to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#id WorkersScript#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param index_name: Name of the Vectorize index to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#index_name WorkersScript#index_name}
        :param json: JSON data to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#json WorkersScript#json}
        :param key_base64: Base64-encoded key data. Required if ``format`` is "raw", "pkcs8", or "spki". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#key_base64 WorkersScript#key_base64}
        :param key_jwk: Key data in `JSON Web Key <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#json_web_key>`_ format. Required if ``format`` is "jwk". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#key_jwk WorkersScript#key_jwk}
        :param namespace: Namespace to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#namespace WorkersScript#namespace}
        :param namespace_id: Namespace identifier tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#namespace_id WorkersScript#namespace_id}
        :param outbound: Outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#outbound WorkersScript#outbound}
        :param pipeline: Name of the Pipeline to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#pipeline WorkersScript#pipeline}
        :param queue_name: Name of the Queue to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#queue_name WorkersScript#queue_name}
        :param script_name: The script where the Durable Object is defined, if it is external to this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#script_name WorkersScript#script_name}
        :param secret_name: Name of the secret in the store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#secret_name WorkersScript#secret_name}
        :param service: Name of Worker to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#service WorkersScript#service}
        :param store_id: ID of the store containing the secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#store_id WorkersScript#store_id}
        :param text: The text value to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#text WorkersScript#text}
        :param usages: Allowed operations with the key. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#keyUsages>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#usages WorkersScript#usages}
        :param workflow_name: Name of the Workflow to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#workflow_name WorkersScript#workflow_name}
        '''
        if isinstance(outbound, dict):
            outbound = WorkersScriptBindingsOutbound(**outbound)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b61d1e7c40bebada2a255e436ef8ab893c996c609123dcb85d81f87d7f9989e9)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument algorithm", value=algorithm, expected_type=type_hints["algorithm"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument certificate_id", value=certificate_id, expected_type=type_hints["certificate_id"])
            check_type(argname="argument class_name", value=class_name, expected_type=type_hints["class_name"])
            check_type(argname="argument dataset", value=dataset, expected_type=type_hints["dataset"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument index_name", value=index_name, expected_type=type_hints["index_name"])
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
            check_type(argname="argument key_base64", value=key_base64, expected_type=type_hints["key_base64"])
            check_type(argname="argument key_jwk", value=key_jwk, expected_type=type_hints["key_jwk"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument namespace_id", value=namespace_id, expected_type=type_hints["namespace_id"])
            check_type(argname="argument outbound", value=outbound, expected_type=type_hints["outbound"])
            check_type(argname="argument pipeline", value=pipeline, expected_type=type_hints["pipeline"])
            check_type(argname="argument queue_name", value=queue_name, expected_type=type_hints["queue_name"])
            check_type(argname="argument script_name", value=script_name, expected_type=type_hints["script_name"])
            check_type(argname="argument secret_name", value=secret_name, expected_type=type_hints["secret_name"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument store_id", value=store_id, expected_type=type_hints["store_id"])
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
            check_type(argname="argument usages", value=usages, expected_type=type_hints["usages"])
            check_type(argname="argument workflow_name", value=workflow_name, expected_type=type_hints["workflow_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "type": type,
        }
        if algorithm is not None:
            self._values["algorithm"] = algorithm
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if certificate_id is not None:
            self._values["certificate_id"] = certificate_id
        if class_name is not None:
            self._values["class_name"] = class_name
        if dataset is not None:
            self._values["dataset"] = dataset
        if environment is not None:
            self._values["environment"] = environment
        if format is not None:
            self._values["format"] = format
        if id is not None:
            self._values["id"] = id
        if index_name is not None:
            self._values["index_name"] = index_name
        if json is not None:
            self._values["json"] = json
        if key_base64 is not None:
            self._values["key_base64"] = key_base64
        if key_jwk is not None:
            self._values["key_jwk"] = key_jwk
        if namespace is not None:
            self._values["namespace"] = namespace
        if namespace_id is not None:
            self._values["namespace_id"] = namespace_id
        if outbound is not None:
            self._values["outbound"] = outbound
        if pipeline is not None:
            self._values["pipeline"] = pipeline
        if queue_name is not None:
            self._values["queue_name"] = queue_name
        if script_name is not None:
            self._values["script_name"] = script_name
        if secret_name is not None:
            self._values["secret_name"] = secret_name
        if service is not None:
            self._values["service"] = service
        if store_id is not None:
            self._values["store_id"] = store_id
        if text is not None:
            self._values["text"] = text
        if usages is not None:
            self._values["usages"] = usages
        if workflow_name is not None:
            self._values["workflow_name"] = workflow_name

    @builtins.property
    def name(self) -> builtins.str:
        '''A JavaScript variable name for the binding.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#name WorkersScript#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The kind of resource that the binding provides.

        Available values: "ai", "analytics_engine", "assets", "browser", "d1", "dispatch_namespace", "durable_object_namespace", "hyperdrive", "json", "kv_namespace", "mtls_certificate", "plain_text", "pipelines", "queue", "r2_bucket", "secret_text", "service", "tail_consumer", "vectorize", "version_metadata", "secrets_store_secret", "secret_key", "workflow".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#type WorkersScript#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def algorithm(self) -> typing.Optional[builtins.str]:
        '''Algorithm-specific key parameters. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#algorithm>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#algorithm WorkersScript#algorithm}
        '''
        result = self._values.get("algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''R2 bucket to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#bucket_name WorkersScript#bucket_name}
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_id(self) -> typing.Optional[builtins.str]:
        '''Identifier of the certificate to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#certificate_id WorkersScript#certificate_id}
        '''
        result = self._values.get("certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def class_name(self) -> typing.Optional[builtins.str]:
        '''The exported class name of the Durable Object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#class_name WorkersScript#class_name}
        '''
        result = self._values.get("class_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dataset(self) -> typing.Optional[builtins.str]:
        '''The name of the dataset to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#dataset WorkersScript#dataset}
        '''
        result = self._values.get("dataset")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(self) -> typing.Optional[builtins.str]:
        '''The environment of the script_name to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#environment WorkersScript#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''Data format of the key. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#format>`_. Available values: "raw", "pkcs8", "spki", "jwk".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#format WorkersScript#format}
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Identifier of the D1 database to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#id WorkersScript#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def index_name(self) -> typing.Optional[builtins.str]:
        '''Name of the Vectorize index to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#index_name WorkersScript#index_name}
        '''
        result = self._values.get("index_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.str]:
        '''JSON data to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#json WorkersScript#json}
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_base64(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded key data. Required if ``format`` is "raw", "pkcs8", or "spki".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#key_base64 WorkersScript#key_base64}
        '''
        result = self._values.get("key_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_jwk(self) -> typing.Optional[builtins.str]:
        '''Key data in `JSON Web Key <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#json_web_key>`_ format. Required if ``format`` is "jwk".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#key_jwk WorkersScript#key_jwk}
        '''
        result = self._values.get("key_jwk")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Namespace to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#namespace WorkersScript#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''Namespace identifier tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#namespace_id WorkersScript#namespace_id}
        '''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outbound(self) -> typing.Optional["WorkersScriptBindingsOutbound"]:
        '''Outbound worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#outbound WorkersScript#outbound}
        '''
        result = self._values.get("outbound")
        return typing.cast(typing.Optional["WorkersScriptBindingsOutbound"], result)

    @builtins.property
    def pipeline(self) -> typing.Optional[builtins.str]:
        '''Name of the Pipeline to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#pipeline WorkersScript#pipeline}
        '''
        result = self._values.get("pipeline")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_name(self) -> typing.Optional[builtins.str]:
        '''Name of the Queue to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#queue_name WorkersScript#queue_name}
        '''
        result = self._values.get("queue_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def script_name(self) -> typing.Optional[builtins.str]:
        '''The script where the Durable Object is defined, if it is external to this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#script_name WorkersScript#script_name}
        '''
        result = self._values.get("script_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''Name of the secret in the store.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#secret_name WorkersScript#secret_name}
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''Name of Worker to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#service WorkersScript#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def store_id(self) -> typing.Optional[builtins.str]:
        '''ID of the store containing the secret.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#store_id WorkersScript#store_id}
        '''
        result = self._values.get("store_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def text(self) -> typing.Optional[builtins.str]:
        '''The text value to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#text WorkersScript#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Allowed operations with the key. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#keyUsages>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#usages WorkersScript#usages}
        '''
        result = self._values.get("usages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_name(self) -> typing.Optional[builtins.str]:
        '''Name of the Workflow to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#workflow_name WorkersScript#workflow_name}
        '''
        result = self._values.get("workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptBindingsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptBindingsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__22fd74e4bbd5d37c5f7a5116356d5a78f68459d2f339ecb3ea460f2fa9047e6e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WorkersScriptBindingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f203cc2acefcf9a907926138510d4b566b5d09628d01b2064551434554f04a27)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkersScriptBindingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95e931abe6354b1b2a87f1927cc877dd0ad67fc7e8429e0686b09c121152b988)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d429a070c8b188df76d2d71300ac12e55c803cddbefe044bd70aa06ecae284ef)
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
            type_hints = typing.get_type_hints(_typecheckingstub__78e054b9c082b32591ddfe41ec96812b44995792af370356b9d5dd26ae61c1fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptBindings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptBindings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e7a2f980380a05ad6558974a946c22d9d94fe64d39904c8e8b81288b4b7afe4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptBindingsOutbound",
    jsii_struct_bases=[],
    name_mapping={"params": "params", "worker": "worker"},
)
class WorkersScriptBindingsOutbound:
    def __init__(
        self,
        *,
        params: typing.Optional[typing.Sequence[builtins.str]] = None,
        worker: typing.Optional[typing.Union["WorkersScriptBindingsOutboundWorker", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param params: Pass information from the Dispatch Worker to the Outbound Worker through the parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#params WorkersScript#params}
        :param worker: Outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#worker WorkersScript#worker}
        '''
        if isinstance(worker, dict):
            worker = WorkersScriptBindingsOutboundWorker(**worker)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42893e7ebd3958fd1cc929145825ad087e77aacea5a98a7563d9a4382714f7bd)
            check_type(argname="argument params", value=params, expected_type=type_hints["params"])
            check_type(argname="argument worker", value=worker, expected_type=type_hints["worker"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if params is not None:
            self._values["params"] = params
        if worker is not None:
            self._values["worker"] = worker

    @builtins.property
    def params(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Pass information from the Dispatch Worker to the Outbound Worker through the parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#params WorkersScript#params}
        '''
        result = self._values.get("params")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def worker(self) -> typing.Optional["WorkersScriptBindingsOutboundWorker"]:
        '''Outbound worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#worker WorkersScript#worker}
        '''
        result = self._values.get("worker")
        return typing.cast(typing.Optional["WorkersScriptBindingsOutboundWorker"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptBindingsOutbound(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptBindingsOutboundOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptBindingsOutboundOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc99053fd850aad1578c9416bcd8ee065a876afebe4d47a2a9def53efb2d1a47)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWorker")
    def put_worker(
        self,
        *,
        environment: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param environment: Environment of the outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#environment WorkersScript#environment}
        :param service: Name of the outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#service WorkersScript#service}
        '''
        value = WorkersScriptBindingsOutboundWorker(
            environment=environment, service=service
        )

        return typing.cast(None, jsii.invoke(self, "putWorker", [value]))

    @jsii.member(jsii_name="resetParams")
    def reset_params(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParams", []))

    @jsii.member(jsii_name="resetWorker")
    def reset_worker(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorker", []))

    @builtins.property
    @jsii.member(jsii_name="worker")
    def worker(self) -> "WorkersScriptBindingsOutboundWorkerOutputReference":
        return typing.cast("WorkersScriptBindingsOutboundWorkerOutputReference", jsii.get(self, "worker"))

    @builtins.property
    @jsii.member(jsii_name="paramsInput")
    def params_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "paramsInput"))

    @builtins.property
    @jsii.member(jsii_name="workerInput")
    def worker_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptBindingsOutboundWorker"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkersScriptBindingsOutboundWorker"]], jsii.get(self, "workerInput"))

    @builtins.property
    @jsii.member(jsii_name="params")
    def params(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "params"))

    @params.setter
    def params(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b981d90d4713da263c45af01b1470dca97d573c6a34476d46c5da25c394955bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "params", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutbound]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutbound]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutbound]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9d2a6826e3099c3bb5549220e4ab2610dc2782d327facce1f8b2b9cd5900ce9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptBindingsOutboundWorker",
    jsii_struct_bases=[],
    name_mapping={"environment": "environment", "service": "service"},
)
class WorkersScriptBindingsOutboundWorker:
    def __init__(
        self,
        *,
        environment: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param environment: Environment of the outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#environment WorkersScript#environment}
        :param service: Name of the outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#service WorkersScript#service}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c7d2882f02e7863b065a181ae729d61ee225344a2b2955458bad097c74f28ee)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if environment is not None:
            self._values["environment"] = environment
        if service is not None:
            self._values["service"] = service

    @builtins.property
    def environment(self) -> typing.Optional[builtins.str]:
        '''Environment of the outbound worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#environment WorkersScript#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''Name of the outbound worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#service WorkersScript#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptBindingsOutboundWorker(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptBindingsOutboundWorkerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptBindingsOutboundWorkerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3aa9152f12943a7277de7e8ceef2d5b91142965cd6d5fa78ea657249477393f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetService")
    def reset_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetService", []))

    @builtins.property
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b862bac4475430d037fe626e2c415f898d4cdca691dcb020c84228a3126fce71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e7a2a096f6de47d028f5d5144f4e22875fc9e1320dbb1d35b56130a0d7fdc9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutboundWorker]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutboundWorker]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutboundWorker]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c562c2a850cbb50ba6bf98d451ea4ef817af47374e98daccd42e9dd86679f43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkersScriptBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptBindingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c95d274e697944ed975e9157998d6563d6073c32d1c336b90be63cbebe5e7176)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putOutbound")
    def put_outbound(
        self,
        *,
        params: typing.Optional[typing.Sequence[builtins.str]] = None,
        worker: typing.Optional[typing.Union[WorkersScriptBindingsOutboundWorker, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param params: Pass information from the Dispatch Worker to the Outbound Worker through the parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#params WorkersScript#params}
        :param worker: Outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#worker WorkersScript#worker}
        '''
        value = WorkersScriptBindingsOutbound(params=params, worker=worker)

        return typing.cast(None, jsii.invoke(self, "putOutbound", [value]))

    @jsii.member(jsii_name="resetAlgorithm")
    def reset_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlgorithm", []))

    @jsii.member(jsii_name="resetBucketName")
    def reset_bucket_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketName", []))

    @jsii.member(jsii_name="resetCertificateId")
    def reset_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateId", []))

    @jsii.member(jsii_name="resetClassName")
    def reset_class_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClassName", []))

    @jsii.member(jsii_name="resetDataset")
    def reset_dataset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataset", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetFormat")
    def reset_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFormat", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIndexName")
    def reset_index_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexName", []))

    @jsii.member(jsii_name="resetJson")
    def reset_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJson", []))

    @jsii.member(jsii_name="resetKeyBase64")
    def reset_key_base64(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyBase64", []))

    @jsii.member(jsii_name="resetKeyJwk")
    def reset_key_jwk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyJwk", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNamespaceId")
    def reset_namespace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespaceId", []))

    @jsii.member(jsii_name="resetOutbound")
    def reset_outbound(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutbound", []))

    @jsii.member(jsii_name="resetPipeline")
    def reset_pipeline(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPipeline", []))

    @jsii.member(jsii_name="resetQueueName")
    def reset_queue_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueName", []))

    @jsii.member(jsii_name="resetScriptName")
    def reset_script_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScriptName", []))

    @jsii.member(jsii_name="resetSecretName")
    def reset_secret_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretName", []))

    @jsii.member(jsii_name="resetService")
    def reset_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetService", []))

    @jsii.member(jsii_name="resetStoreId")
    def reset_store_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStoreId", []))

    @jsii.member(jsii_name="resetText")
    def reset_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetText", []))

    @jsii.member(jsii_name="resetUsages")
    def reset_usages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsages", []))

    @jsii.member(jsii_name="resetWorkflowName")
    def reset_workflow_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkflowName", []))

    @builtins.property
    @jsii.member(jsii_name="outbound")
    def outbound(self) -> WorkersScriptBindingsOutboundOutputReference:
        return typing.cast(WorkersScriptBindingsOutboundOutputReference, jsii.get(self, "outbound"))

    @builtins.property
    @jsii.member(jsii_name="algorithmInput")
    def algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateIdInput")
    def certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="classNameInput")
    def class_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "classNameInput"))

    @builtins.property
    @jsii.member(jsii_name="datasetInput")
    def dataset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datasetInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentInput"))

    @builtins.property
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="indexNameInput")
    def index_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexNameInput"))

    @builtins.property
    @jsii.member(jsii_name="jsonInput")
    def json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jsonInput"))

    @builtins.property
    @jsii.member(jsii_name="keyBase64Input")
    def key_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyBase64Input"))

    @builtins.property
    @jsii.member(jsii_name="keyJwkInput")
    def key_jwk_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyJwkInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceIdInput")
    def namespace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="outboundInput")
    def outbound_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutbound]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutbound]], jsii.get(self, "outboundInput"))

    @builtins.property
    @jsii.member(jsii_name="pipelineInput")
    def pipeline_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineInput"))

    @builtins.property
    @jsii.member(jsii_name="queueNameInput")
    def queue_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueNameInput"))

    @builtins.property
    @jsii.member(jsii_name="scriptNameInput")
    def script_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptNameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretNameInput")
    def secret_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretNameInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="storeIdInput")
    def store_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "textInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="usagesInput")
    def usages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "usagesInput"))

    @builtins.property
    @jsii.member(jsii_name="workflowNameInput")
    def workflow_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workflowNameInput"))

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d8da6c217083da43f9fbae3fd76210cd2a2ee915639db5e3e583188f05fb72e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8a779c82c826100fc81b98c35624bd5ad811c928eddf25fa1e92ff2219459e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @certificate_id.setter
    def certificate_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e39c4bdbe773a57798cd3abfd05f659cf19af768580420c269de874c986d33e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="className")
    def class_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "className"))

    @class_name.setter
    def class_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4d1c0c56c280d7b2c048e0243c7391d47355eab98a5b6a1d038482841f58879)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "className", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataset")
    def dataset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataset"))

    @dataset.setter
    def dataset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17a9525542eab50f162e55680a182e7df08e500b47daecc13fb6ca72bbbfaa19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b5c1626dba443fff1b2e1d7d685c32fc2b02cfadb479eac5eb6661e6c2ea50c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e183047c670d2913a0fd38ecdbd2f7af7f9d2405ab722bb74e4989f43d48f43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2025a3b54af033604f886b327b336ffb942d0daad28797a7648a76b31a0ce46b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indexName")
    def index_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexName"))

    @index_name.setter
    def index_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08d04845e6a253874845b4e2dad19a99d1006d5be6df6ba815a7a69dddbb79f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indexName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="json")
    def json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "json"))

    @json.setter
    def json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ea86dfb1cde467fa2c4618d9860b497268a1ead62e91d5ddad1525d537f7a15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "json", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyBase64")
    def key_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyBase64"))

    @key_base64.setter
    def key_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e81295a08e8550d8130710623f4c537417ab1fe461b06a43db1e27d414ddfec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyBase64", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyJwk")
    def key_jwk(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyJwk"))

    @key_jwk.setter
    def key_jwk(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bfd2b40211081925f46bf8a11a5b5b5eb04ed318efce4e24052b1fc1aaf44d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyJwk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15ecd500e9fda52af87afba24b63f8d226b1ef75b2b2ec89339804359a5077cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcd99b6c81a5cd4b8555dc81220aa9062c14699173515c04cb3653f20435f964)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @namespace_id.setter
    def namespace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__664d64d41cddeafaa662fa805a51556fdbcd8f38fa838c5fd7998c8d7f30daf0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipeline"))

    @pipeline.setter
    def pipeline(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7655c395ad064669979c4ed1b1b7126dfa10ee66abf279e98f0f8bd8bf13a866)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipeline", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueName")
    def queue_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueName"))

    @queue_name.setter
    def queue_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3648680f16d5df7207a52af00dea2dea1e8b6701b20ee81dac245471db23aae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptName")
    def script_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scriptName"))

    @script_name.setter
    def script_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45fc6a0d45910713f4e44557d4157869408c16c8c8823e01ac78e914f76710f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretName"))

    @secret_name.setter
    def secret_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__098dbc790763ff46689b3b01350da49bb7c2f889cdb6e5c122a3e1584aaaf9bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68ff7dfe193f227adda8b6d18bfd0d7345558e80047a3dcabeeff60bf089d3e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storeId")
    def store_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storeId"))

    @store_id.setter
    def store_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__236d09e67110d04da1681ba8633950d1bc9c993c1b70286ec1f76e98d9075c27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "text"))

    @text.setter
    def text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b471b63623dfbfeefe96dfd91853bed731634ed3bb1434dd1c6caaa704b1ce9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dd05dc209008fc1a00a0a07785af54dd86d9b863219f82eddd9f982b031d212)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usages")
    def usages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usages"))

    @usages.setter
    def usages(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16528bea302fe26845c0382e7f2b80de0fd142e6a0eb61c43f2162e9d402d5e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workflowName")
    def workflow_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workflowName"))

    @workflow_name.setter
    def workflow_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0977d8f9875dd4ba7cc0971ba533a10968879ff0fec1d329040cda6d7df9d52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workflowName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99e61e388553893c668d9929734de44bbedd293c514a9a31dd50106199b65875)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptConfig",
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
        "script_name": "scriptName",
        "assets": "assets",
        "bindings": "bindings",
        "body_part": "bodyPart",
        "compatibility_date": "compatibilityDate",
        "compatibility_flags": "compatibilityFlags",
        "content": "content",
        "content_file": "contentFile",
        "content_sha256": "contentSha256",
        "content_type": "contentType",
        "keep_assets": "keepAssets",
        "keep_bindings": "keepBindings",
        "limits": "limits",
        "logpush": "logpush",
        "main_module": "mainModule",
        "migrations": "migrations",
        "observability": "observability",
        "placement": "placement",
        "tail_consumers": "tailConsumers",
        "usage_model": "usageModel",
    },
)
class WorkersScriptConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        script_name: builtins.str,
        assets: typing.Optional[typing.Union[WorkersScriptAssets, typing.Dict[builtins.str, typing.Any]]] = None,
        bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
        body_part: typing.Optional[builtins.str] = None,
        compatibility_date: typing.Optional[builtins.str] = None,
        compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        content: typing.Optional[builtins.str] = None,
        content_file: typing.Optional[builtins.str] = None,
        content_sha256: typing.Optional[builtins.str] = None,
        content_type: typing.Optional[builtins.str] = None,
        keep_assets: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        keep_bindings: typing.Optional[typing.Sequence[builtins.str]] = None,
        limits: typing.Optional[typing.Union["WorkersScriptLimits", typing.Dict[builtins.str, typing.Any]]] = None,
        logpush: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        main_module: typing.Optional[builtins.str] = None,
        migrations: typing.Optional[typing.Union["WorkersScriptMigrations", typing.Dict[builtins.str, typing.Any]]] = None,
        observability: typing.Optional[typing.Union["WorkersScriptObservability", typing.Dict[builtins.str, typing.Any]]] = None,
        placement: typing.Optional[typing.Union["WorkersScriptPlacement", typing.Dict[builtins.str, typing.Any]]] = None,
        tail_consumers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptTailConsumers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        usage_model: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#account_id WorkersScript#account_id}
        :param script_name: Name of the script, used in URLs and route configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#script_name WorkersScript#script_name}
        :param assets: Configuration for assets within a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#assets WorkersScript#assets}
        :param bindings: List of bindings attached to a Worker. You can find more about bindings on our docs: https://developers.cloudflare.com/workers/configuration/multipart-upload-metadata/#bindings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#bindings WorkersScript#bindings}
        :param body_part: Name of the part in the multipart request that contains the script (e.g. the file adding a listener to the ``fetch`` event). Indicates a ``service worker syntax`` Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#body_part WorkersScript#body_part}
        :param compatibility_date: Date indicating targeted support in the Workers runtime. Backwards incompatible fixes to the runtime following this date will not affect this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#compatibility_date WorkersScript#compatibility_date}
        :param compatibility_flags: Flags that enable or disable certain features in the Workers runtime. Used to enable upcoming features or opt in or out of specific changes not included in a ``compatibility_date``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#compatibility_flags WorkersScript#compatibility_flags}
        :param content: Module or Service Worker contents of the Worker. Exactly one of ``content`` or ``content_file`` must be specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content WorkersScript#content}
        :param content_file: Path to a file containing the Module or Service Worker contents of the Worker. Exactly one of ``content`` or ``content_file`` must be specified. Must be paired with ``content_sha256``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content_file WorkersScript#content_file}
        :param content_sha256: SHA-256 hash of the Worker contents. Used to trigger updates when source code changes. Must be provided when ``content_file`` is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content_sha256 WorkersScript#content_sha256}
        :param content_type: Content-Type of the Worker. Required if uploading a non-JavaScript Worker (e.g. "text/x-python"). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content_type WorkersScript#content_type}
        :param keep_assets: Retain assets which exist for a previously uploaded Worker version; used in lieu of providing a completion token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#keep_assets WorkersScript#keep_assets}
        :param keep_bindings: List of binding types to keep from previous_upload. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#keep_bindings WorkersScript#keep_bindings}
        :param limits: Limits to apply for this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#limits WorkersScript#limits}
        :param logpush: Whether Logpush is turned on for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#logpush WorkersScript#logpush}
        :param main_module: Name of the part in the multipart request that contains the main module (e.g. the file exporting a ``fetch`` handler). Indicates a ``module syntax`` Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#main_module WorkersScript#main_module}
        :param migrations: Migrations to apply for Durable Objects associated with this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#migrations WorkersScript#migrations}
        :param observability: Observability settings for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#observability WorkersScript#observability}
        :param placement: Configuration for `Smart Placement <https://developers.cloudflare.com/workers/configuration/smart-placement>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#placement WorkersScript#placement}
        :param tail_consumers: List of Workers that will consume logs from the attached Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#tail_consumers WorkersScript#tail_consumers}
        :param usage_model: Usage model for the Worker invocations. Available values: "standard", "bundled", "unbound". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#usage_model WorkersScript#usage_model}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(assets, dict):
            assets = WorkersScriptAssets(**assets)
        if isinstance(limits, dict):
            limits = WorkersScriptLimits(**limits)
        if isinstance(migrations, dict):
            migrations = WorkersScriptMigrations(**migrations)
        if isinstance(observability, dict):
            observability = WorkersScriptObservability(**observability)
        if isinstance(placement, dict):
            placement = WorkersScriptPlacement(**placement)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fff7b79f452a4dac9e7059b6adbee078a1b1970a8ad1c6c8b7a71849b9988441)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument script_name", value=script_name, expected_type=type_hints["script_name"])
            check_type(argname="argument assets", value=assets, expected_type=type_hints["assets"])
            check_type(argname="argument bindings", value=bindings, expected_type=type_hints["bindings"])
            check_type(argname="argument body_part", value=body_part, expected_type=type_hints["body_part"])
            check_type(argname="argument compatibility_date", value=compatibility_date, expected_type=type_hints["compatibility_date"])
            check_type(argname="argument compatibility_flags", value=compatibility_flags, expected_type=type_hints["compatibility_flags"])
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument content_file", value=content_file, expected_type=type_hints["content_file"])
            check_type(argname="argument content_sha256", value=content_sha256, expected_type=type_hints["content_sha256"])
            check_type(argname="argument content_type", value=content_type, expected_type=type_hints["content_type"])
            check_type(argname="argument keep_assets", value=keep_assets, expected_type=type_hints["keep_assets"])
            check_type(argname="argument keep_bindings", value=keep_bindings, expected_type=type_hints["keep_bindings"])
            check_type(argname="argument limits", value=limits, expected_type=type_hints["limits"])
            check_type(argname="argument logpush", value=logpush, expected_type=type_hints["logpush"])
            check_type(argname="argument main_module", value=main_module, expected_type=type_hints["main_module"])
            check_type(argname="argument migrations", value=migrations, expected_type=type_hints["migrations"])
            check_type(argname="argument observability", value=observability, expected_type=type_hints["observability"])
            check_type(argname="argument placement", value=placement, expected_type=type_hints["placement"])
            check_type(argname="argument tail_consumers", value=tail_consumers, expected_type=type_hints["tail_consumers"])
            check_type(argname="argument usage_model", value=usage_model, expected_type=type_hints["usage_model"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "script_name": script_name,
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
        if assets is not None:
            self._values["assets"] = assets
        if bindings is not None:
            self._values["bindings"] = bindings
        if body_part is not None:
            self._values["body_part"] = body_part
        if compatibility_date is not None:
            self._values["compatibility_date"] = compatibility_date
        if compatibility_flags is not None:
            self._values["compatibility_flags"] = compatibility_flags
        if content is not None:
            self._values["content"] = content
        if content_file is not None:
            self._values["content_file"] = content_file
        if content_sha256 is not None:
            self._values["content_sha256"] = content_sha256
        if content_type is not None:
            self._values["content_type"] = content_type
        if keep_assets is not None:
            self._values["keep_assets"] = keep_assets
        if keep_bindings is not None:
            self._values["keep_bindings"] = keep_bindings
        if limits is not None:
            self._values["limits"] = limits
        if logpush is not None:
            self._values["logpush"] = logpush
        if main_module is not None:
            self._values["main_module"] = main_module
        if migrations is not None:
            self._values["migrations"] = migrations
        if observability is not None:
            self._values["observability"] = observability
        if placement is not None:
            self._values["placement"] = placement
        if tail_consumers is not None:
            self._values["tail_consumers"] = tail_consumers
        if usage_model is not None:
            self._values["usage_model"] = usage_model

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#account_id WorkersScript#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def script_name(self) -> builtins.str:
        '''Name of the script, used in URLs and route configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#script_name WorkersScript#script_name}
        '''
        result = self._values.get("script_name")
        assert result is not None, "Required property 'script_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assets(self) -> typing.Optional[WorkersScriptAssets]:
        '''Configuration for assets within a Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#assets WorkersScript#assets}
        '''
        result = self._values.get("assets")
        return typing.cast(typing.Optional[WorkersScriptAssets], result)

    @builtins.property
    def bindings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptBindings]]]:
        '''List of bindings attached to a Worker. You can find more about bindings on our docs: https://developers.cloudflare.com/workers/configuration/multipart-upload-metadata/#bindings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#bindings WorkersScript#bindings}
        '''
        result = self._values.get("bindings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptBindings]]], result)

    @builtins.property
    def body_part(self) -> typing.Optional[builtins.str]:
        '''Name of the part in the multipart request that contains the script (e.g. the file adding a listener to the ``fetch`` event). Indicates a ``service worker syntax`` Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#body_part WorkersScript#body_part}
        '''
        result = self._values.get("body_part")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compatibility_date(self) -> typing.Optional[builtins.str]:
        '''Date indicating targeted support in the Workers runtime.

        Backwards incompatible fixes to the runtime following this date will not affect this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#compatibility_date WorkersScript#compatibility_date}
        '''
        result = self._values.get("compatibility_date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compatibility_flags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Flags that enable or disable certain features in the Workers runtime.

        Used to enable upcoming features or opt in or out of specific changes not included in a ``compatibility_date``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#compatibility_flags WorkersScript#compatibility_flags}
        '''
        result = self._values.get("compatibility_flags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def content(self) -> typing.Optional[builtins.str]:
        '''Module or Service Worker contents of the Worker. Exactly one of ``content`` or ``content_file`` must be specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content WorkersScript#content}
        '''
        result = self._values.get("content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_file(self) -> typing.Optional[builtins.str]:
        '''Path to a file containing the Module or Service Worker contents of the Worker.

        Exactly one of ``content`` or ``content_file`` must be specified. Must be paired with ``content_sha256``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content_file WorkersScript#content_file}
        '''
        result = self._values.get("content_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_sha256(self) -> typing.Optional[builtins.str]:
        '''SHA-256 hash of the Worker contents.

        Used to trigger updates when source code changes. Must be provided when ``content_file`` is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content_sha256 WorkersScript#content_sha256}
        '''
        result = self._values.get("content_sha256")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_type(self) -> typing.Optional[builtins.str]:
        '''Content-Type of the Worker. Required if uploading a non-JavaScript Worker (e.g. "text/x-python").

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#content_type WorkersScript#content_type}
        '''
        result = self._values.get("content_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keep_assets(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Retain assets which exist for a previously uploaded Worker version; used in lieu of providing a completion token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#keep_assets WorkersScript#keep_assets}
        '''
        result = self._values.get("keep_assets")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def keep_bindings(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of binding types to keep from previous_upload.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#keep_bindings WorkersScript#keep_bindings}
        '''
        result = self._values.get("keep_bindings")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def limits(self) -> typing.Optional["WorkersScriptLimits"]:
        '''Limits to apply for this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#limits WorkersScript#limits}
        '''
        result = self._values.get("limits")
        return typing.cast(typing.Optional["WorkersScriptLimits"], result)

    @builtins.property
    def logpush(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether Logpush is turned on for the Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#logpush WorkersScript#logpush}
        '''
        result = self._values.get("logpush")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def main_module(self) -> typing.Optional[builtins.str]:
        '''Name of the part in the multipart request that contains the main module (e.g. the file exporting a ``fetch`` handler). Indicates a ``module syntax`` Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#main_module WorkersScript#main_module}
        '''
        result = self._values.get("main_module")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def migrations(self) -> typing.Optional["WorkersScriptMigrations"]:
        '''Migrations to apply for Durable Objects associated with this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#migrations WorkersScript#migrations}
        '''
        result = self._values.get("migrations")
        return typing.cast(typing.Optional["WorkersScriptMigrations"], result)

    @builtins.property
    def observability(self) -> typing.Optional["WorkersScriptObservability"]:
        '''Observability settings for the Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#observability WorkersScript#observability}
        '''
        result = self._values.get("observability")
        return typing.cast(typing.Optional["WorkersScriptObservability"], result)

    @builtins.property
    def placement(self) -> typing.Optional["WorkersScriptPlacement"]:
        '''Configuration for `Smart Placement <https://developers.cloudflare.com/workers/configuration/smart-placement>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#placement WorkersScript#placement}
        '''
        result = self._values.get("placement")
        return typing.cast(typing.Optional["WorkersScriptPlacement"], result)

    @builtins.property
    def tail_consumers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptTailConsumers"]]]:
        '''List of Workers that will consume logs from the attached Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#tail_consumers WorkersScript#tail_consumers}
        '''
        result = self._values.get("tail_consumers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptTailConsumers"]]], result)

    @builtins.property
    def usage_model(self) -> typing.Optional[builtins.str]:
        '''Usage model for the Worker invocations. Available values: "standard", "bundled", "unbound".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#usage_model WorkersScript#usage_model}
        '''
        result = self._values.get("usage_model")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptLimits",
    jsii_struct_bases=[],
    name_mapping={"cpu_ms": "cpuMs"},
)
class WorkersScriptLimits:
    def __init__(self, *, cpu_ms: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param cpu_ms: The amount of CPU time this Worker can use in milliseconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#cpu_ms WorkersScript#cpu_ms}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71656eebc2684f7c37b369344313de0545c44180e9cd8f8a2b7fc76b8552b8cb)
            check_type(argname="argument cpu_ms", value=cpu_ms, expected_type=type_hints["cpu_ms"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_ms is not None:
            self._values["cpu_ms"] = cpu_ms

    @builtins.property
    def cpu_ms(self) -> typing.Optional[jsii.Number]:
        '''The amount of CPU time this Worker can use in milliseconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#cpu_ms WorkersScript#cpu_ms}
        '''
        result = self._values.get("cpu_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4b30c3c82bea317877a43e80efb8857ccbbe8eeacc79d4661b4dd769c4e702a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCpuMs")
    def reset_cpu_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuMs", []))

    @builtins.property
    @jsii.member(jsii_name="cpuMsInput")
    def cpu_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuMsInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuMs")
    def cpu_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuMs"))

    @cpu_ms.setter
    def cpu_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35d555feeaa7d1f85dbba38809ec62e2eccbde1189338fb492018b8038f8817a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b01655482ecbe77b284c1cfbe2844b37c395a455cdb20b310c57a1ee6cd3b27a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrations",
    jsii_struct_bases=[],
    name_mapping={
        "deleted_classes": "deletedClasses",
        "new_classes": "newClasses",
        "new_sqlite_classes": "newSqliteClasses",
        "new_tag": "newTag",
        "old_tag": "oldTag",
        "renamed_classes": "renamedClasses",
        "steps": "steps",
        "transferred_classes": "transferredClasses",
    },
)
class WorkersScriptMigrations:
    def __init__(
        self,
        *,
        deleted_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_sqlite_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_tag: typing.Optional[builtins.str] = None,
        old_tag: typing.Optional[builtins.str] = None,
        renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
        steps: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsSteps", typing.Dict[builtins.str, typing.Any]]]]] = None,
        transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param deleted_classes: A list of classes to delete Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#deleted_classes WorkersScript#deleted_classes}
        :param new_classes: A list of classes to create Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_classes WorkersScript#new_classes}
        :param new_sqlite_classes: A list of classes to create Durable Object namespaces with SQLite from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_sqlite_classes WorkersScript#new_sqlite_classes}
        :param new_tag: Tag to set as the latest migration tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_tag WorkersScript#new_tag}
        :param old_tag: Tag used to verify against the latest migration tag for this Worker. If they don't match, the upload is rejected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#old_tag WorkersScript#old_tag}
        :param renamed_classes: A list of classes with Durable Object namespaces that were renamed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#renamed_classes WorkersScript#renamed_classes}
        :param steps: Migrations to apply in order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#steps WorkersScript#steps}
        :param transferred_classes: A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#transferred_classes WorkersScript#transferred_classes}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77884fd0089d9fc6de63726c3542daed6f561fc4a2c618da9b4a2b863fddadd6)
            check_type(argname="argument deleted_classes", value=deleted_classes, expected_type=type_hints["deleted_classes"])
            check_type(argname="argument new_classes", value=new_classes, expected_type=type_hints["new_classes"])
            check_type(argname="argument new_sqlite_classes", value=new_sqlite_classes, expected_type=type_hints["new_sqlite_classes"])
            check_type(argname="argument new_tag", value=new_tag, expected_type=type_hints["new_tag"])
            check_type(argname="argument old_tag", value=old_tag, expected_type=type_hints["old_tag"])
            check_type(argname="argument renamed_classes", value=renamed_classes, expected_type=type_hints["renamed_classes"])
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
            check_type(argname="argument transferred_classes", value=transferred_classes, expected_type=type_hints["transferred_classes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deleted_classes is not None:
            self._values["deleted_classes"] = deleted_classes
        if new_classes is not None:
            self._values["new_classes"] = new_classes
        if new_sqlite_classes is not None:
            self._values["new_sqlite_classes"] = new_sqlite_classes
        if new_tag is not None:
            self._values["new_tag"] = new_tag
        if old_tag is not None:
            self._values["old_tag"] = old_tag
        if renamed_classes is not None:
            self._values["renamed_classes"] = renamed_classes
        if steps is not None:
            self._values["steps"] = steps
        if transferred_classes is not None:
            self._values["transferred_classes"] = transferred_classes

    @builtins.property
    def deleted_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to delete Durable Object namespaces from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#deleted_classes WorkersScript#deleted_classes}
        '''
        result = self._values.get("deleted_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to create Durable Object namespaces from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_classes WorkersScript#new_classes}
        '''
        result = self._values.get("new_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_sqlite_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to create Durable Object namespaces with SQLite from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_sqlite_classes WorkersScript#new_sqlite_classes}
        '''
        result = self._values.get("new_sqlite_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_tag(self) -> typing.Optional[builtins.str]:
        '''Tag to set as the latest migration tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_tag WorkersScript#new_tag}
        '''
        result = self._values.get("new_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def old_tag(self) -> typing.Optional[builtins.str]:
        '''Tag used to verify against the latest migration tag for this Worker.

        If they don't match, the upload is rejected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#old_tag WorkersScript#old_tag}
        '''
        result = self._values.get("old_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def renamed_classes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsRenamedClasses"]]]:
        '''A list of classes with Durable Object namespaces that were renamed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#renamed_classes WorkersScript#renamed_classes}
        '''
        result = self._values.get("renamed_classes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsRenamedClasses"]]], result)

    @builtins.property
    def steps(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsSteps"]]]:
        '''Migrations to apply in order.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#steps WorkersScript#steps}
        '''
        result = self._values.get("steps")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsSteps"]]], result)

    @builtins.property
    def transferred_classes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsTransferredClasses"]]]:
        '''A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#transferred_classes WorkersScript#transferred_classes}
        '''
        result = self._values.get("transferred_classes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsTransferredClasses"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptMigrations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptMigrationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__93d7850a844e7140864fee10d0d2a30c31598e87f5e82dde40e22e28be126efa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRenamedClasses")
    def put_renamed_classes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6227d44996bdb22fe6946420d21a32ec33158318e461b8db5d862272cc48571)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRenamedClasses", [value]))

    @jsii.member(jsii_name="putSteps")
    def put_steps(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsSteps", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac42f14b0096001cc42e9558cab4b6e353cbf7f75906b0ebd0092b5c2f7f899d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSteps", [value]))

    @jsii.member(jsii_name="putTransferredClasses")
    def put_transferred_classes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__604ab05bde36cb6742ea627b751232ed4c8389f76bffa909396f90bd73553aa5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTransferredClasses", [value]))

    @jsii.member(jsii_name="resetDeletedClasses")
    def reset_deleted_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletedClasses", []))

    @jsii.member(jsii_name="resetNewClasses")
    def reset_new_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewClasses", []))

    @jsii.member(jsii_name="resetNewSqliteClasses")
    def reset_new_sqlite_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewSqliteClasses", []))

    @jsii.member(jsii_name="resetNewTag")
    def reset_new_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewTag", []))

    @jsii.member(jsii_name="resetOldTag")
    def reset_old_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOldTag", []))

    @jsii.member(jsii_name="resetRenamedClasses")
    def reset_renamed_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRenamedClasses", []))

    @jsii.member(jsii_name="resetSteps")
    def reset_steps(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSteps", []))

    @jsii.member(jsii_name="resetTransferredClasses")
    def reset_transferred_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransferredClasses", []))

    @builtins.property
    @jsii.member(jsii_name="renamedClasses")
    def renamed_classes(self) -> "WorkersScriptMigrationsRenamedClassesList":
        return typing.cast("WorkersScriptMigrationsRenamedClassesList", jsii.get(self, "renamedClasses"))

    @builtins.property
    @jsii.member(jsii_name="steps")
    def steps(self) -> "WorkersScriptMigrationsStepsList":
        return typing.cast("WorkersScriptMigrationsStepsList", jsii.get(self, "steps"))

    @builtins.property
    @jsii.member(jsii_name="transferredClasses")
    def transferred_classes(self) -> "WorkersScriptMigrationsTransferredClassesList":
        return typing.cast("WorkersScriptMigrationsTransferredClassesList", jsii.get(self, "transferredClasses"))

    @builtins.property
    @jsii.member(jsii_name="deletedClassesInput")
    def deleted_classes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "deletedClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="newClassesInput")
    def new_classes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "newClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="newSqliteClassesInput")
    def new_sqlite_classes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "newSqliteClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="newTagInput")
    def new_tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "newTagInput"))

    @builtins.property
    @jsii.member(jsii_name="oldTagInput")
    def old_tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oldTagInput"))

    @builtins.property
    @jsii.member(jsii_name="renamedClassesInput")
    def renamed_classes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsRenamedClasses"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsRenamedClasses"]]], jsii.get(self, "renamedClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="stepsInput")
    def steps_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsSteps"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsSteps"]]], jsii.get(self, "stepsInput"))

    @builtins.property
    @jsii.member(jsii_name="transferredClassesInput")
    def transferred_classes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsTransferredClasses"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsTransferredClasses"]]], jsii.get(self, "transferredClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="deletedClasses")
    def deleted_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "deletedClasses"))

    @deleted_classes.setter
    def deleted_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d7d96657384239204a35ebbd05c02cca84b0c4410409bc2afda3d49ccd105f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletedClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newClasses")
    def new_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newClasses"))

    @new_classes.setter
    def new_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2e5984b12f70f2bd7b94ca326708a20c257b922a332a14a5efc64731d6e5078)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newSqliteClasses")
    def new_sqlite_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newSqliteClasses"))

    @new_sqlite_classes.setter
    def new_sqlite_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__420864f79612ba129607c232ac612e2c6d3c52885be1533baf6ba7688f108b4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newSqliteClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newTag")
    def new_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "newTag"))

    @new_tag.setter
    def new_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0123e7d495d6f64723477e3711b901f171353b660c3d7d11184cebbeff9561d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oldTag")
    def old_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oldTag"))

    @old_tag.setter
    def old_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__798e5c6b620f8472c739129265dfafe965371de33c6db1b799ef080463e107e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oldTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d3913ed4b23253bd5b2c133a94e88a367ab3962a2df7676f86076b059bc1466)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsRenamedClasses",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "to": "to"},
)
class WorkersScriptMigrationsRenamedClasses:
    def __init__(
        self,
        *,
        from_: typing.Optional[builtins.str] = None,
        to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from WorkersScript#from}.
        :param to: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#to WorkersScript#to}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c473aa6edad6297eb6470bd211c3b55050d3a85e023697d7536058100c3686c5)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument to", value=to, expected_type=type_hints["to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if from_ is not None:
            self._values["from_"] = from_
        if to is not None:
            self._values["to"] = to

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from WorkersScript#from}.'''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#to WorkersScript#to}.'''
        result = self._values.get("to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptMigrationsRenamedClasses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptMigrationsRenamedClassesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsRenamedClassesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8c31fa0f36b6bb24eae891b21681a225daf4767d06e7757c78fd847a7e6bf05)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkersScriptMigrationsRenamedClassesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90ce64adef6fcb1e0e47e33581529abb73d31ad0bb717b9364ed96bc059c9171)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkersScriptMigrationsRenamedClassesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__996289685e5e1a9029db7a598bc5ad807e12206f80d44f01248a9c8604f5850e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a682eab16cc2f693d1d94a71601cccf52fcfdc1bdc9d563e6a85af6f3aa2dba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e60d789a4a0ab378627f28ab6f2e8b6f3a0aa5d3237771fcfcee0942ffba9e95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsRenamedClasses]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsRenamedClasses]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsRenamedClasses]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7b53783dfacf563f9b8f3aaa1e02c4c4c5449b331b40d8bc9f172147c273143)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkersScriptMigrationsRenamedClassesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsRenamedClassesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__326db70df2d4b0741588cf9a3e377cf0ae7ac83882be603c645f4740437a403a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetFrom")
    def reset_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrom", []))

    @jsii.member(jsii_name="resetTo")
    def reset_to(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTo", []))

    @builtins.property
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromInput"))

    @builtins.property
    @jsii.member(jsii_name="toInput")
    def to_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "toInput"))

    @builtins.property
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1770f17205ea949072f6b28512bd631b141a0ba5f79889fd879e01a3d1a87b26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="to")
    def to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "to"))

    @to.setter
    def to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dba1d54c71e9286a33d3109962b89de489507851cd1368ee42da1c3e5918bf65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "to", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsRenamedClasses]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsRenamedClasses]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsRenamedClasses]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fbd4c5d0a35c84706335c75b508dd28b0936681e3a2ae66a23ee11fc1a4806a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsSteps",
    jsii_struct_bases=[],
    name_mapping={
        "deleted_classes": "deletedClasses",
        "new_classes": "newClasses",
        "new_sqlite_classes": "newSqliteClasses",
        "renamed_classes": "renamedClasses",
        "transferred_classes": "transferredClasses",
    },
)
class WorkersScriptMigrationsSteps:
    def __init__(
        self,
        *,
        deleted_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_sqlite_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsStepsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
        transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsStepsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param deleted_classes: A list of classes to delete Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#deleted_classes WorkersScript#deleted_classes}
        :param new_classes: A list of classes to create Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_classes WorkersScript#new_classes}
        :param new_sqlite_classes: A list of classes to create Durable Object namespaces with SQLite from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_sqlite_classes WorkersScript#new_sqlite_classes}
        :param renamed_classes: A list of classes with Durable Object namespaces that were renamed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#renamed_classes WorkersScript#renamed_classes}
        :param transferred_classes: A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#transferred_classes WorkersScript#transferred_classes}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7088493dad55bf3b63a5dc6c7b485d9468f93173690f0154b136848b317c558)
            check_type(argname="argument deleted_classes", value=deleted_classes, expected_type=type_hints["deleted_classes"])
            check_type(argname="argument new_classes", value=new_classes, expected_type=type_hints["new_classes"])
            check_type(argname="argument new_sqlite_classes", value=new_sqlite_classes, expected_type=type_hints["new_sqlite_classes"])
            check_type(argname="argument renamed_classes", value=renamed_classes, expected_type=type_hints["renamed_classes"])
            check_type(argname="argument transferred_classes", value=transferred_classes, expected_type=type_hints["transferred_classes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deleted_classes is not None:
            self._values["deleted_classes"] = deleted_classes
        if new_classes is not None:
            self._values["new_classes"] = new_classes
        if new_sqlite_classes is not None:
            self._values["new_sqlite_classes"] = new_sqlite_classes
        if renamed_classes is not None:
            self._values["renamed_classes"] = renamed_classes
        if transferred_classes is not None:
            self._values["transferred_classes"] = transferred_classes

    @builtins.property
    def deleted_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to delete Durable Object namespaces from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#deleted_classes WorkersScript#deleted_classes}
        '''
        result = self._values.get("deleted_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to create Durable Object namespaces from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_classes WorkersScript#new_classes}
        '''
        result = self._values.get("new_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_sqlite_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to create Durable Object namespaces with SQLite from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#new_sqlite_classes WorkersScript#new_sqlite_classes}
        '''
        result = self._values.get("new_sqlite_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def renamed_classes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsStepsRenamedClasses"]]]:
        '''A list of classes with Durable Object namespaces that were renamed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#renamed_classes WorkersScript#renamed_classes}
        '''
        result = self._values.get("renamed_classes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsStepsRenamedClasses"]]], result)

    @builtins.property
    def transferred_classes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsStepsTransferredClasses"]]]:
        '''A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#transferred_classes WorkersScript#transferred_classes}
        '''
        result = self._values.get("transferred_classes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsStepsTransferredClasses"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptMigrationsSteps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptMigrationsStepsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsStepsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb2c79a86857a2fcc5e8cdfb845243f2f512709e44251502906834e11804bcee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WorkersScriptMigrationsStepsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e95b8e72ab77b716bb7483ba7af7b766104e68c41473482b780ccd4481fda28)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkersScriptMigrationsStepsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8f54ab0db04c1f6c43cf4a876b4a35166d396af87c2274b7e73246c5ce22d94)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe26b73d5954bef85a76b52df3b1a23d2527e42705eda33abc5d51884a94bfb6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d63b484b3c6faa10e7af65b993d170e1789c2305f7fb3e0776b063201a26ef9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsSteps]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsSteps]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsSteps]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__030c0ae12f81276af708dd066bb0393930eb4a2931342312abc507b26f3e6d74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkersScriptMigrationsStepsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsStepsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf627c724e6ae51204db0eb927dc18a5bc0ef8c68aeab6e83a6efdd457e6cf7c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putRenamedClasses")
    def put_renamed_classes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsStepsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9327d1eee1acd901a58fe956648286b12c98f2f7764169c32f20797d289ab5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRenamedClasses", [value]))

    @jsii.member(jsii_name="putTransferredClasses")
    def put_transferred_classes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkersScriptMigrationsStepsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae496eb45e48966aadedde5488a496483a1c4ab8f5c900e7c3ca78ec515fa52b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTransferredClasses", [value]))

    @jsii.member(jsii_name="resetDeletedClasses")
    def reset_deleted_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletedClasses", []))

    @jsii.member(jsii_name="resetNewClasses")
    def reset_new_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewClasses", []))

    @jsii.member(jsii_name="resetNewSqliteClasses")
    def reset_new_sqlite_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewSqliteClasses", []))

    @jsii.member(jsii_name="resetRenamedClasses")
    def reset_renamed_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRenamedClasses", []))

    @jsii.member(jsii_name="resetTransferredClasses")
    def reset_transferred_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransferredClasses", []))

    @builtins.property
    @jsii.member(jsii_name="renamedClasses")
    def renamed_classes(self) -> "WorkersScriptMigrationsStepsRenamedClassesList":
        return typing.cast("WorkersScriptMigrationsStepsRenamedClassesList", jsii.get(self, "renamedClasses"))

    @builtins.property
    @jsii.member(jsii_name="transferredClasses")
    def transferred_classes(
        self,
    ) -> "WorkersScriptMigrationsStepsTransferredClassesList":
        return typing.cast("WorkersScriptMigrationsStepsTransferredClassesList", jsii.get(self, "transferredClasses"))

    @builtins.property
    @jsii.member(jsii_name="deletedClassesInput")
    def deleted_classes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "deletedClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="newClassesInput")
    def new_classes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "newClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="newSqliteClassesInput")
    def new_sqlite_classes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "newSqliteClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="renamedClassesInput")
    def renamed_classes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsStepsRenamedClasses"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsStepsRenamedClasses"]]], jsii.get(self, "renamedClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="transferredClassesInput")
    def transferred_classes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsStepsTransferredClasses"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkersScriptMigrationsStepsTransferredClasses"]]], jsii.get(self, "transferredClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="deletedClasses")
    def deleted_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "deletedClasses"))

    @deleted_classes.setter
    def deleted_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06dc2f6f382a8ae83a27f296714f02a8a9d2cf91b07cfa4afe4a95e5482e79e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletedClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newClasses")
    def new_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newClasses"))

    @new_classes.setter
    def new_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7f651ebf455b2ce52562a27c7ff92485069db65166777d6d700625049e29478)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newSqliteClasses")
    def new_sqlite_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newSqliteClasses"))

    @new_sqlite_classes.setter
    def new_sqlite_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93b89c1dbb7fb03604e6146462899fcd516bb2577677f58d7be14ec88772b2ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newSqliteClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsSteps]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsSteps]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsSteps]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f69415da994f02140d4f2227860179dd297476135258fc41491074770467d863)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsStepsRenamedClasses",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "to": "to"},
)
class WorkersScriptMigrationsStepsRenamedClasses:
    def __init__(
        self,
        *,
        from_: typing.Optional[builtins.str] = None,
        to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from WorkersScript#from}.
        :param to: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#to WorkersScript#to}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__592737dd703b540f7e62e1c70f832fcc880711a482e6c817832565fc8eb518ec)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument to", value=to, expected_type=type_hints["to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if from_ is not None:
            self._values["from_"] = from_
        if to is not None:
            self._values["to"] = to

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from WorkersScript#from}.'''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#to WorkersScript#to}.'''
        result = self._values.get("to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptMigrationsStepsRenamedClasses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptMigrationsStepsRenamedClassesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsStepsRenamedClassesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__10b7c66b7db39e43eaf79fe0856333dfc604cb9cd64aae889221bd1dbb24de55)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkersScriptMigrationsStepsRenamedClassesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ac747b043cf737b3d153964641c72d063b07c514a9ef05a8b91f4e211bb84dc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkersScriptMigrationsStepsRenamedClassesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__926d8182ba34061ca3d1f146a43e8f04a4d42f7978e50045738a5d277db30ce7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e4a1e43bcf2bb630f72d9403e8c6003eeb1b392dd38691005ee4b6384456e49b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__609403a09bd1fb12a975722f671846298d066b611455f31e3a0f6be98192529a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsStepsRenamedClasses]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsStepsRenamedClasses]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsStepsRenamedClasses]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02fb04885d7f1b50c49982e286223a6cf3b9fd7e6248602453b2451e26ea0fe2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkersScriptMigrationsStepsRenamedClassesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsStepsRenamedClassesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__411e15b679a7b413b5d2d4e3ea454b89c195c691adb4a3fa459f636835a6fcce)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetFrom")
    def reset_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrom", []))

    @jsii.member(jsii_name="resetTo")
    def reset_to(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTo", []))

    @builtins.property
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromInput"))

    @builtins.property
    @jsii.member(jsii_name="toInput")
    def to_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "toInput"))

    @builtins.property
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34b20ded3c2dba41ef195cf26ca95aa7061bc1f0ba676d75bc1e5c3cfe8441de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="to")
    def to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "to"))

    @to.setter
    def to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc4146353d041ea0551a89da50bd3cd82804d3935e26336c5d2d229e49578cb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "to", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsStepsRenamedClasses]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsStepsRenamedClasses]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsStepsRenamedClasses]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a75d65bf7124e8060213b2f5de011a9f6a9f98e64c8ba456d24f33a2035102b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsStepsTransferredClasses",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "from_script": "fromScript", "to": "to"},
)
class WorkersScriptMigrationsStepsTransferredClasses:
    def __init__(
        self,
        *,
        from_: typing.Optional[builtins.str] = None,
        from_script: typing.Optional[builtins.str] = None,
        to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from WorkersScript#from}.
        :param from_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from_script WorkersScript#from_script}.
        :param to: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#to WorkersScript#to}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57445ce1958205b95ca6beccd2520856bae790d1d926767c8076d017e3bbf492)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument from_script", value=from_script, expected_type=type_hints["from_script"])
            check_type(argname="argument to", value=to, expected_type=type_hints["to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if from_ is not None:
            self._values["from_"] = from_
        if from_script is not None:
            self._values["from_script"] = from_script
        if to is not None:
            self._values["to"] = to

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from WorkersScript#from}.'''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_script(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from_script WorkersScript#from_script}.'''
        result = self._values.get("from_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#to WorkersScript#to}.'''
        result = self._values.get("to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptMigrationsStepsTransferredClasses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptMigrationsStepsTransferredClassesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsStepsTransferredClassesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2540c3fca44319bb4d5a018ecb1f6ae5ceed60b8238560bdef192ac39128a256)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkersScriptMigrationsStepsTransferredClassesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1be5a8f5d2d31d51d53355ef0786c3887adad981452e8dc60881685fb075ea0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkersScriptMigrationsStepsTransferredClassesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc2d2e679148cdcf6d2d916bd4e3ee21084c314d9ef9641f16e7b1ed2f1c3526)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a042e42b65b7ea5be695530458f4cecd434c20268dd61c3c4bbe1afcdf0a64bb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c35573ccb69edee4f041c3398d262b425d4f2c70334f70855b711e4b8f5a09df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsStepsTransferredClasses]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsStepsTransferredClasses]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsStepsTransferredClasses]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__222f328e658bd1844a862269974346e124585737dbaa5ce14eb2d3b216cdd890)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkersScriptMigrationsStepsTransferredClassesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsStepsTransferredClassesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__98c9c1f9f1870d659f5f0d9b5def43e82759836382521096c12fac4519a964c8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetFrom")
    def reset_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrom", []))

    @jsii.member(jsii_name="resetFromScript")
    def reset_from_script(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFromScript", []))

    @jsii.member(jsii_name="resetTo")
    def reset_to(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTo", []))

    @builtins.property
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromInput"))

    @builtins.property
    @jsii.member(jsii_name="fromScriptInput")
    def from_script_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromScriptInput"))

    @builtins.property
    @jsii.member(jsii_name="toInput")
    def to_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "toInput"))

    @builtins.property
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0bec8334b08e601a641f22cc0707323843e941e9ac0a2203e3343e7a4c1b04e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fromScript")
    def from_script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fromScript"))

    @from_script.setter
    def from_script(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81d1209f7f3b4e1460e8f037cbffb1e656507c35b732ff348c638fe469b5dc32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fromScript", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="to")
    def to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "to"))

    @to.setter
    def to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ea69e264c9a0404f8d1a4039cb1f1c3a9124475e9b8fc73656ec35298ba4a04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "to", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsStepsTransferredClasses]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsStepsTransferredClasses]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsStepsTransferredClasses]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6efc371c931e70d1a83692ed34f994e0239251f26f8ab4ce36f0f91ae29de25f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsTransferredClasses",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "from_script": "fromScript", "to": "to"},
)
class WorkersScriptMigrationsTransferredClasses:
    def __init__(
        self,
        *,
        from_: typing.Optional[builtins.str] = None,
        from_script: typing.Optional[builtins.str] = None,
        to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from WorkersScript#from}.
        :param from_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from_script WorkersScript#from_script}.
        :param to: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#to WorkersScript#to}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c6c7274eaf13cbfc51c641d11f7658d743dc4ce38075cfad5ea60c991edca7c)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument from_script", value=from_script, expected_type=type_hints["from_script"])
            check_type(argname="argument to", value=to, expected_type=type_hints["to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if from_ is not None:
            self._values["from_"] = from_
        if from_script is not None:
            self._values["from_script"] = from_script
        if to is not None:
            self._values["to"] = to

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from WorkersScript#from}.'''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_script(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#from_script WorkersScript#from_script}.'''
        result = self._values.get("from_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#to WorkersScript#to}.'''
        result = self._values.get("to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptMigrationsTransferredClasses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptMigrationsTransferredClassesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsTransferredClassesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3513662db909869d90c8386008965e2cd405b75c6a9eb4f14e08ab883e6924f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkersScriptMigrationsTransferredClassesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecf5fd7487fcb02de31a29e3844cf83a4420f1183e7ee10dcf4226dbfe2aebec)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkersScriptMigrationsTransferredClassesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__271de41dd32b28b191a8ec592dc56565d35d83b68b294335daa3f35df6e2bb44)
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
            type_hints = typing.get_type_hints(_typecheckingstub__008da140af124637f89156223daf3f6ceee27030a9c7613f790d1e713824fabd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__16f2dee1f6c969b0ae8e9c6ab698e52c1edb153b87b3387477fd7d107b11084f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsTransferredClasses]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsTransferredClasses]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsTransferredClasses]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de918e1edc94f7d61e9415da376645dd745f15dce916191bb41a012b29c19d7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkersScriptMigrationsTransferredClassesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptMigrationsTransferredClassesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__307267e63a2cd6695ddaead91126b8e62a28be3017aebc5f78241aad13d741c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetFrom")
    def reset_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrom", []))

    @jsii.member(jsii_name="resetFromScript")
    def reset_from_script(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFromScript", []))

    @jsii.member(jsii_name="resetTo")
    def reset_to(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTo", []))

    @builtins.property
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromInput"))

    @builtins.property
    @jsii.member(jsii_name="fromScriptInput")
    def from_script_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromScriptInput"))

    @builtins.property
    @jsii.member(jsii_name="toInput")
    def to_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "toInput"))

    @builtins.property
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6968dc48a17fc4e5af18e9b75d2ea6e1c4c1a2af3e298c8a69b120e4a4e1e17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fromScript")
    def from_script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fromScript"))

    @from_script.setter
    def from_script(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a9c1759bcebe318362470363f9c66febfba070af468c813c5fc24b06984e984)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fromScript", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="to")
    def to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "to"))

    @to.setter
    def to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41c3e155af9013221bf4d4af2f46bd441d08d66c40a3df2d12f4d51674f43b4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "to", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsTransferredClasses]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsTransferredClasses]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsTransferredClasses]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d228fdd76609a6c9d336b885095aa6a64726dbfbee03e96e3ed0db7e36498775)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptNamedHandlers",
    jsii_struct_bases=[],
    name_mapping={},
)
class WorkersScriptNamedHandlers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptNamedHandlers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptNamedHandlersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptNamedHandlersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3bfd0fb8b8f89f975968ba16e5d763fb3df67d76ba9a3d28e75490fdbdc71ca2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WorkersScriptNamedHandlersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7445fe6f07391b11219adf4953a96c78c379384e998353a52b2a2ca0cb607ea3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkersScriptNamedHandlersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c24240c393c7aa42e033deb1fdba71239b1521b1daba5ae52c3ac443f4fb5dfe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1bf727c7459447bbb1f2d20c3004bc2d1d437444a98fa0d58229b9783e94834)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5809334428577add7a35558c290f64e0f2ba6d301ab6347671b9d5316d19d308)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class WorkersScriptNamedHandlersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptNamedHandlersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca38724820be7f6dbb07fd92079338a96ea521a8325449522965d4aa6cf3ffd0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="handlers")
    def handlers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "handlers"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkersScriptNamedHandlers]:
        return typing.cast(typing.Optional[WorkersScriptNamedHandlers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkersScriptNamedHandlers],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4197b6afc12d33e5f41cb1e3631fbbddd9751b00cc8a09ab5d6830c700bf08d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptObservability",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "head_sampling_rate": "headSamplingRate",
        "logs": "logs",
    },
)
class WorkersScriptObservability:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        head_sampling_rate: typing.Optional[jsii.Number] = None,
        logs: typing.Optional[typing.Union["WorkersScriptObservabilityLogs", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param enabled: Whether observability is enabled for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#enabled WorkersScript#enabled}
        :param head_sampling_rate: The sampling rate for incoming requests. From 0 to 1 (1 = 100%, 0.1 = 10%). Default is 1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#head_sampling_rate WorkersScript#head_sampling_rate}
        :param logs: Log settings for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#logs WorkersScript#logs}
        '''
        if isinstance(logs, dict):
            logs = WorkersScriptObservabilityLogs(**logs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5029f4c4d5da0eec3392e66fd84fd5c15490980c4a078e1373af3c21ee72537)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument head_sampling_rate", value=head_sampling_rate, expected_type=type_hints["head_sampling_rate"])
            check_type(argname="argument logs", value=logs, expected_type=type_hints["logs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enabled": enabled,
        }
        if head_sampling_rate is not None:
            self._values["head_sampling_rate"] = head_sampling_rate
        if logs is not None:
            self._values["logs"] = logs

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Whether observability is enabled for the Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#enabled WorkersScript#enabled}
        '''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def head_sampling_rate(self) -> typing.Optional[jsii.Number]:
        '''The sampling rate for incoming requests. From 0 to 1 (1 = 100%, 0.1 = 10%). Default is 1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#head_sampling_rate WorkersScript#head_sampling_rate}
        '''
        result = self._values.get("head_sampling_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def logs(self) -> typing.Optional["WorkersScriptObservabilityLogs"]:
        '''Log settings for the Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#logs WorkersScript#logs}
        '''
        result = self._values.get("logs")
        return typing.cast(typing.Optional["WorkersScriptObservabilityLogs"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptObservability(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptObservabilityLogs",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "invocation_logs": "invocationLogs",
        "head_sampling_rate": "headSamplingRate",
    },
)
class WorkersScriptObservabilityLogs:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        invocation_logs: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        head_sampling_rate: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Whether logs are enabled for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#enabled WorkersScript#enabled}
        :param invocation_logs: Whether `invocation logs <https://developers.cloudflare.com/workers/observability/logs/workers-logs/#invocation-logs>`_ are enabled for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#invocation_logs WorkersScript#invocation_logs}
        :param head_sampling_rate: The sampling rate for logs. From 0 to 1 (1 = 100%, 0.1 = 10%). Default is 1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#head_sampling_rate WorkersScript#head_sampling_rate}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04afd411ba28ecc838e5dcb95018522e1621a9adab3a72b94418ebaeff55daa6)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument invocation_logs", value=invocation_logs, expected_type=type_hints["invocation_logs"])
            check_type(argname="argument head_sampling_rate", value=head_sampling_rate, expected_type=type_hints["head_sampling_rate"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enabled": enabled,
            "invocation_logs": invocation_logs,
        }
        if head_sampling_rate is not None:
            self._values["head_sampling_rate"] = head_sampling_rate

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Whether logs are enabled for the Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#enabled WorkersScript#enabled}
        '''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def invocation_logs(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Whether `invocation logs <https://developers.cloudflare.com/workers/observability/logs/workers-logs/#invocation-logs>`_ are enabled for the Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#invocation_logs WorkersScript#invocation_logs}
        '''
        result = self._values.get("invocation_logs")
        assert result is not None, "Required property 'invocation_logs' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def head_sampling_rate(self) -> typing.Optional[jsii.Number]:
        '''The sampling rate for logs. From 0 to 1 (1 = 100%, 0.1 = 10%). Default is 1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#head_sampling_rate WorkersScript#head_sampling_rate}
        '''
        result = self._values.get("head_sampling_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptObservabilityLogs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptObservabilityLogsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptObservabilityLogsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__58d899a12d289839829fdde23759a85188ca067663257ef9ac88fc071644bf5e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHeadSamplingRate")
    def reset_head_sampling_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeadSamplingRate", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="headSamplingRateInput")
    def head_sampling_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "headSamplingRateInput"))

    @builtins.property
    @jsii.member(jsii_name="invocationLogsInput")
    def invocation_logs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "invocationLogsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__c74a09975767b6738bc584f41de0ffb3624d0e6f659d3541a85d60a740c4c58e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headSamplingRate")
    def head_sampling_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "headSamplingRate"))

    @head_sampling_rate.setter
    def head_sampling_rate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20ab74cc60b754b266f48ec9b2ed99939b79d12afe2f6aefa76aaaaf406bbe47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headSamplingRate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="invocationLogs")
    def invocation_logs(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "invocationLogs"))

    @invocation_logs.setter
    def invocation_logs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66bff00bd740e5fe57ba8f716e539e20d67a98cada1e25b5cbd20193f915444e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "invocationLogs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservabilityLogs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservabilityLogs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservabilityLogs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4a7fa1e9562244dc0c433c97f29bfda73e646c0055c2cb8fb6fef3ed3cc9d82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkersScriptObservabilityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptObservabilityOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dbd09163816e15efad432407d02c0161e9cf9dba1518025605e37b478a7dd15d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putLogs")
    def put_logs(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        invocation_logs: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        head_sampling_rate: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Whether logs are enabled for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#enabled WorkersScript#enabled}
        :param invocation_logs: Whether `invocation logs <https://developers.cloudflare.com/workers/observability/logs/workers-logs/#invocation-logs>`_ are enabled for the Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#invocation_logs WorkersScript#invocation_logs}
        :param head_sampling_rate: The sampling rate for logs. From 0 to 1 (1 = 100%, 0.1 = 10%). Default is 1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#head_sampling_rate WorkersScript#head_sampling_rate}
        '''
        value = WorkersScriptObservabilityLogs(
            enabled=enabled,
            invocation_logs=invocation_logs,
            head_sampling_rate=head_sampling_rate,
        )

        return typing.cast(None, jsii.invoke(self, "putLogs", [value]))

    @jsii.member(jsii_name="resetHeadSamplingRate")
    def reset_head_sampling_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeadSamplingRate", []))

    @jsii.member(jsii_name="resetLogs")
    def reset_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogs", []))

    @builtins.property
    @jsii.member(jsii_name="logs")
    def logs(self) -> WorkersScriptObservabilityLogsOutputReference:
        return typing.cast(WorkersScriptObservabilityLogsOutputReference, jsii.get(self, "logs"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="headSamplingRateInput")
    def head_sampling_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "headSamplingRateInput"))

    @builtins.property
    @jsii.member(jsii_name="logsInput")
    def logs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservabilityLogs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservabilityLogs]], jsii.get(self, "logsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__98c2fde9f53fbd878ebfe2cdefa07a4d13a1af644fd05adfe771517f606dcc73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headSamplingRate")
    def head_sampling_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "headSamplingRate"))

    @head_sampling_rate.setter
    def head_sampling_rate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2833e1b5ea6fba1c430b60f64786966b0ef7760890de66de1ab70844161b8c8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headSamplingRate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservability]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservability]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservability]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e278571f493e634ee19df983eb46ce629c3afcc1de1364447ed1a9b469002e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptPlacement",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode"},
)
class WorkersScriptPlacement:
    def __init__(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Enables `Smart Placement <https://developers.cloudflare.com/workers/configuration/smart-placement>`_. Available values: "smart". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#mode WorkersScript#mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5e4978ff81453269afcd828d0429a67b9641991131251e08ef91557a3cab1ea)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Enables `Smart Placement <https://developers.cloudflare.com/workers/configuration/smart-placement>`_. Available values: "smart".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#mode WorkersScript#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptPlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptPlacementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptPlacementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0a158c6e91af48c4f305bec5f3dd074b7898a16087f8fb8d6760231f63f750f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @builtins.property
    @jsii.member(jsii_name="lastAnalyzedAt")
    def last_analyzed_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastAnalyzedAt"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0efbc9bf511fddd2db4b69eab68daae2a4eb96a27da4c0d7144c960dd2835f6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptPlacement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptPlacement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptPlacement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71ccdfa338a27dc2280667eadc3dfa61b4800c5eb4db50906cc4755c705744a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptTailConsumers",
    jsii_struct_bases=[],
    name_mapping={
        "service": "service",
        "environment": "environment",
        "namespace": "namespace",
    },
)
class WorkersScriptTailConsumers:
    def __init__(
        self,
        *,
        service: builtins.str,
        environment: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service: Name of Worker that is to be the consumer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#service WorkersScript#service}
        :param environment: Optional environment if the Worker utilizes one. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#environment WorkersScript#environment}
        :param namespace: Optional dispatch namespace the script belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#namespace WorkersScript#namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f868a8834bd616dcea77e492f38ea77965690708a1dc09fc6c8060f3652f44ea)
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service": service,
        }
        if environment is not None:
            self._values["environment"] = environment
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def service(self) -> builtins.str:
        '''Name of Worker that is to be the consumer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#service WorkersScript#service}
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def environment(self) -> typing.Optional[builtins.str]:
        '''Optional environment if the Worker utilizes one.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#environment WorkersScript#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Optional dispatch namespace the script belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/workers_script#namespace WorkersScript#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkersScriptTailConsumers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkersScriptTailConsumersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptTailConsumersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c474f127ed43e98c10a336a0b56d2c61ef35b0aa7170059c0b3850686204a493)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WorkersScriptTailConsumersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94e44d87d24709ddac3be921b14b16da32f8ec189918dfdd4cc2ae3dd50ee03b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkersScriptTailConsumersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__601b6abe8af7e1b47e07ae8ec147298c3ba6ef76826d0948931330ce1ad71d11)
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
            type_hints = typing.get_type_hints(_typecheckingstub__73db8851f1d5fbffe886629c7415cfb493d228f4d2076dbc7fef3844af34b8e8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__93e55630a459fea1a360ef12551c7f42f7e1dc04c77c58d2cf6ded04b3bd353f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptTailConsumers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptTailConsumers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptTailConsumers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17c20bbbb48ad6c5447801aba5675e88690213431e411b8a3abde1dabde1dde9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkersScriptTailConsumersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workersScript.WorkersScriptTailConsumersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e1b8d20abe80031548d626c3fff1c66a999b4325160d67e9a92248ca997d3e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @builtins.property
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__734378b4355822cceaa55527578766172a32cd5dc6fcb59b8b0e6dd95b48940f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66e5b7292052ec49c45b197f169ec100fedc33104823c74e749bdb92ea81edf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__173787c724655fcddafe1342ebdb871165e382707dad2d8c7bbf5f7183f4e6d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptTailConsumers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptTailConsumers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptTailConsumers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7d164d2afc247c9121fd9af27a6b9bc0ea23a2ca969aa1644b6dd23a16a26dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "WorkersScript",
    "WorkersScriptAssets",
    "WorkersScriptAssetsConfig",
    "WorkersScriptAssetsConfigOutputReference",
    "WorkersScriptAssetsOutputReference",
    "WorkersScriptBindings",
    "WorkersScriptBindingsList",
    "WorkersScriptBindingsOutbound",
    "WorkersScriptBindingsOutboundOutputReference",
    "WorkersScriptBindingsOutboundWorker",
    "WorkersScriptBindingsOutboundWorkerOutputReference",
    "WorkersScriptBindingsOutputReference",
    "WorkersScriptConfig",
    "WorkersScriptLimits",
    "WorkersScriptLimitsOutputReference",
    "WorkersScriptMigrations",
    "WorkersScriptMigrationsOutputReference",
    "WorkersScriptMigrationsRenamedClasses",
    "WorkersScriptMigrationsRenamedClassesList",
    "WorkersScriptMigrationsRenamedClassesOutputReference",
    "WorkersScriptMigrationsSteps",
    "WorkersScriptMigrationsStepsList",
    "WorkersScriptMigrationsStepsOutputReference",
    "WorkersScriptMigrationsStepsRenamedClasses",
    "WorkersScriptMigrationsStepsRenamedClassesList",
    "WorkersScriptMigrationsStepsRenamedClassesOutputReference",
    "WorkersScriptMigrationsStepsTransferredClasses",
    "WorkersScriptMigrationsStepsTransferredClassesList",
    "WorkersScriptMigrationsStepsTransferredClassesOutputReference",
    "WorkersScriptMigrationsTransferredClasses",
    "WorkersScriptMigrationsTransferredClassesList",
    "WorkersScriptMigrationsTransferredClassesOutputReference",
    "WorkersScriptNamedHandlers",
    "WorkersScriptNamedHandlersList",
    "WorkersScriptNamedHandlersOutputReference",
    "WorkersScriptObservability",
    "WorkersScriptObservabilityLogs",
    "WorkersScriptObservabilityLogsOutputReference",
    "WorkersScriptObservabilityOutputReference",
    "WorkersScriptPlacement",
    "WorkersScriptPlacementOutputReference",
    "WorkersScriptTailConsumers",
    "WorkersScriptTailConsumersList",
    "WorkersScriptTailConsumersOutputReference",
]

publication.publish()

def _typecheckingstub__9ff91a65eae39ed03c4fdb5f548361f58aa71f020d925825809f305475cc24e5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    script_name: builtins.str,
    assets: typing.Optional[typing.Union[WorkersScriptAssets, typing.Dict[builtins.str, typing.Any]]] = None,
    bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    body_part: typing.Optional[builtins.str] = None,
    compatibility_date: typing.Optional[builtins.str] = None,
    compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    content: typing.Optional[builtins.str] = None,
    content_file: typing.Optional[builtins.str] = None,
    content_sha256: typing.Optional[builtins.str] = None,
    content_type: typing.Optional[builtins.str] = None,
    keep_assets: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    keep_bindings: typing.Optional[typing.Sequence[builtins.str]] = None,
    limits: typing.Optional[typing.Union[WorkersScriptLimits, typing.Dict[builtins.str, typing.Any]]] = None,
    logpush: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    main_module: typing.Optional[builtins.str] = None,
    migrations: typing.Optional[typing.Union[WorkersScriptMigrations, typing.Dict[builtins.str, typing.Any]]] = None,
    observability: typing.Optional[typing.Union[WorkersScriptObservability, typing.Dict[builtins.str, typing.Any]]] = None,
    placement: typing.Optional[typing.Union[WorkersScriptPlacement, typing.Dict[builtins.str, typing.Any]]] = None,
    tail_consumers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptTailConsumers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    usage_model: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__b2a18d8db56da9a802f4ab3dc8c0f4b0e47025df295217c56f9931fd59facc2d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d23c2fc7f9a34ba826f0a79d838b04f388555410c3d727a81d005e1d9a445f1d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptBindings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9dbeb6bf5de037026fd8af0f2821cdf1f095033d5aeb5bea457dbc8b27a0308(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptTailConsumers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb2ca3c27f6a6700ee28e3832fcae15db049a5d2723a9a5abd3bd88fc910c53c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d09ccd2b30c63f9860e38dcd580c84cd7eb4ca4f5afcd9e2db01a50c398d4566(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a46bd088570853c2b5d25072bad96f40225ab4162b4c5b1822d3c87bd6810a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__decdadb6de4f79ad4960d73aa391c3abf6546ecb024fa20d96613a183d671be1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__020e04151b7603f4ce7a71ecc71bbe500fe9298103161c4ea64a898fc07bbe21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b766e3bb95b4cbec0079c5072b6e87240bc4e61fa065986626bff666a944c8ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c1177f60389f5d5320d5b88ee5774d867680c41e0a66621da71a936eda3e441(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f221590a541bf73dba256c50369c0a23c45d4dce5a7874c70e65d1732edb101d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13eb92bc492a7673b76351d0dffba81f119311503a2c2ee2517a6e4ef6fc6dc8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dbef9532ad7ff8b5a3102859e96c58db44a4be7e3e5713486f310a1e8893c08(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15514dbe74dbfe1fad3f9886bc5c24270ced70991f6ab14e8672103ae6fc8b2f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__469f27b32ea89216e4dbc4e30a98fb9803600dd95f317d78898dc6d8d95f2b8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77dfe2bc85769bce53963ca545bc276956cf465a6f7543034268baf566765a12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00107ec9a9eb93096aedd4f6f48676a35a7af59c8416e26c3b0970c4caebf720(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0280169838b98e1dd5475ed04cefe33ccd39cb9f74769d6331f48f2ecde2d191(
    *,
    config: typing.Optional[typing.Union[WorkersScriptAssetsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    jwt: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe00299ab5032efa34983e9e6ddfdb4b709a45de5199407d803d7a6a6056f081(
    *,
    headers: typing.Optional[builtins.str] = None,
    html_handling: typing.Optional[builtins.str] = None,
    not_found_handling: typing.Optional[builtins.str] = None,
    redirects: typing.Optional[builtins.str] = None,
    run_worker_first: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    serve_directly: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__746e455dda28a2f2d3f86fb7ac841593886895f7a02c7f0436405f343bef0f8d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77f454c26d6da8babd045208a102fb098809e8dbca42d49de22d71f66e2693a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42b364bc843bb93e1833e45bd7bf6b22043bc0315751b22989982d9763e1fb8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a01b5ad052c0ef1260bf5e43dc3649c694581c5ec1494e7fa56d3b432d1f080(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__341dbc90cb71c1d05f43dc26685a544ddbab8ad8dc2f6954bbefc29222faa969(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__104247b332ae471047a1ebd8d23c64839530dc375d9e06deed488d0b3af3e0cf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7edb6842f86f5b237e1d292f61d454909d8a5bcde705f4aa6949aa51d682c7a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0c06c67ecd56e53226fccc96b3dedde70c5ffd4927927d6fde830870fadf520(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssetsConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64a6d8d68c3ae9935622ed6dc67d4b8f0a062261f4ff55043f1a193f49bf4174(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca46c9842b2197b5a2cbd30e9476ec0c318841ae948c62d57f1d412d7995866c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71e386a2d334f9a601c805355df8056f4ebaa7a47f87bb1c6d519fa055c8dd69(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptAssets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b61d1e7c40bebada2a255e436ef8ab893c996c609123dcb85d81f87d7f9989e9(
    *,
    name: builtins.str,
    type: builtins.str,
    algorithm: typing.Optional[builtins.str] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    certificate_id: typing.Optional[builtins.str] = None,
    class_name: typing.Optional[builtins.str] = None,
    dataset: typing.Optional[builtins.str] = None,
    environment: typing.Optional[builtins.str] = None,
    format: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    index_name: typing.Optional[builtins.str] = None,
    json: typing.Optional[builtins.str] = None,
    key_base64: typing.Optional[builtins.str] = None,
    key_jwk: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    namespace_id: typing.Optional[builtins.str] = None,
    outbound: typing.Optional[typing.Union[WorkersScriptBindingsOutbound, typing.Dict[builtins.str, typing.Any]]] = None,
    pipeline: typing.Optional[builtins.str] = None,
    queue_name: typing.Optional[builtins.str] = None,
    script_name: typing.Optional[builtins.str] = None,
    secret_name: typing.Optional[builtins.str] = None,
    service: typing.Optional[builtins.str] = None,
    store_id: typing.Optional[builtins.str] = None,
    text: typing.Optional[builtins.str] = None,
    usages: typing.Optional[typing.Sequence[builtins.str]] = None,
    workflow_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22fd74e4bbd5d37c5f7a5116356d5a78f68459d2f339ecb3ea460f2fa9047e6e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f203cc2acefcf9a907926138510d4b566b5d09628d01b2064551434554f04a27(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95e931abe6354b1b2a87f1927cc877dd0ad67fc7e8429e0686b09c121152b988(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d429a070c8b188df76d2d71300ac12e55c803cddbefe044bd70aa06ecae284ef(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78e054b9c082b32591ddfe41ec96812b44995792af370356b9d5dd26ae61c1fe(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e7a2f980380a05ad6558974a946c22d9d94fe64d39904c8e8b81288b4b7afe4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptBindings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42893e7ebd3958fd1cc929145825ad087e77aacea5a98a7563d9a4382714f7bd(
    *,
    params: typing.Optional[typing.Sequence[builtins.str]] = None,
    worker: typing.Optional[typing.Union[WorkersScriptBindingsOutboundWorker, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc99053fd850aad1578c9416bcd8ee065a876afebe4d47a2a9def53efb2d1a47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b981d90d4713da263c45af01b1470dca97d573c6a34476d46c5da25c394955bc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9d2a6826e3099c3bb5549220e4ab2610dc2782d327facce1f8b2b9cd5900ce9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutbound]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c7d2882f02e7863b065a181ae729d61ee225344a2b2955458bad097c74f28ee(
    *,
    environment: typing.Optional[builtins.str] = None,
    service: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aa9152f12943a7277de7e8ceef2d5b91142965cd6d5fa78ea657249477393f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b862bac4475430d037fe626e2c415f898d4cdca691dcb020c84228a3126fce71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e7a2a096f6de47d028f5d5144f4e22875fc9e1320dbb1d35b56130a0d7fdc9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c562c2a850cbb50ba6bf98d451ea4ef817af47374e98daccd42e9dd86679f43(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindingsOutboundWorker]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c95d274e697944ed975e9157998d6563d6073c32d1c336b90be63cbebe5e7176(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d8da6c217083da43f9fbae3fd76210cd2a2ee915639db5e3e583188f05fb72e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8a779c82c826100fc81b98c35624bd5ad811c928eddf25fa1e92ff2219459e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e39c4bdbe773a57798cd3abfd05f659cf19af768580420c269de874c986d33e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4d1c0c56c280d7b2c048e0243c7391d47355eab98a5b6a1d038482841f58879(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17a9525542eab50f162e55680a182e7df08e500b47daecc13fb6ca72bbbfaa19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b5c1626dba443fff1b2e1d7d685c32fc2b02cfadb479eac5eb6661e6c2ea50c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e183047c670d2913a0fd38ecdbd2f7af7f9d2405ab722bb74e4989f43d48f43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2025a3b54af033604f886b327b336ffb942d0daad28797a7648a76b31a0ce46b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08d04845e6a253874845b4e2dad19a99d1006d5be6df6ba815a7a69dddbb79f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ea86dfb1cde467fa2c4618d9860b497268a1ead62e91d5ddad1525d537f7a15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e81295a08e8550d8130710623f4c537417ab1fe461b06a43db1e27d414ddfec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bfd2b40211081925f46bf8a11a5b5b5eb04ed318efce4e24052b1fc1aaf44d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15ecd500e9fda52af87afba24b63f8d226b1ef75b2b2ec89339804359a5077cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcd99b6c81a5cd4b8555dc81220aa9062c14699173515c04cb3653f20435f964(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__664d64d41cddeafaa662fa805a51556fdbcd8f38fa838c5fd7998c8d7f30daf0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7655c395ad064669979c4ed1b1b7126dfa10ee66abf279e98f0f8bd8bf13a866(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3648680f16d5df7207a52af00dea2dea1e8b6701b20ee81dac245471db23aae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45fc6a0d45910713f4e44557d4157869408c16c8c8823e01ac78e914f76710f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__098dbc790763ff46689b3b01350da49bb7c2f889cdb6e5c122a3e1584aaaf9bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68ff7dfe193f227adda8b6d18bfd0d7345558e80047a3dcabeeff60bf089d3e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__236d09e67110d04da1681ba8633950d1bc9c993c1b70286ec1f76e98d9075c27(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b471b63623dfbfeefe96dfd91853bed731634ed3bb1434dd1c6caaa704b1ce9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dd05dc209008fc1a00a0a07785af54dd86d9b863219f82eddd9f982b031d212(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16528bea302fe26845c0382e7f2b80de0fd142e6a0eb61c43f2162e9d402d5e4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0977d8f9875dd4ba7cc0971ba533a10968879ff0fec1d329040cda6d7df9d52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99e61e388553893c668d9929734de44bbedd293c514a9a31dd50106199b65875(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptBindings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fff7b79f452a4dac9e7059b6adbee078a1b1970a8ad1c6c8b7a71849b9988441(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    script_name: builtins.str,
    assets: typing.Optional[typing.Union[WorkersScriptAssets, typing.Dict[builtins.str, typing.Any]]] = None,
    bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    body_part: typing.Optional[builtins.str] = None,
    compatibility_date: typing.Optional[builtins.str] = None,
    compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    content: typing.Optional[builtins.str] = None,
    content_file: typing.Optional[builtins.str] = None,
    content_sha256: typing.Optional[builtins.str] = None,
    content_type: typing.Optional[builtins.str] = None,
    keep_assets: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    keep_bindings: typing.Optional[typing.Sequence[builtins.str]] = None,
    limits: typing.Optional[typing.Union[WorkersScriptLimits, typing.Dict[builtins.str, typing.Any]]] = None,
    logpush: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    main_module: typing.Optional[builtins.str] = None,
    migrations: typing.Optional[typing.Union[WorkersScriptMigrations, typing.Dict[builtins.str, typing.Any]]] = None,
    observability: typing.Optional[typing.Union[WorkersScriptObservability, typing.Dict[builtins.str, typing.Any]]] = None,
    placement: typing.Optional[typing.Union[WorkersScriptPlacement, typing.Dict[builtins.str, typing.Any]]] = None,
    tail_consumers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptTailConsumers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    usage_model: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71656eebc2684f7c37b369344313de0545c44180e9cd8f8a2b7fc76b8552b8cb(
    *,
    cpu_ms: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4b30c3c82bea317877a43e80efb8857ccbbe8eeacc79d4661b4dd769c4e702a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35d555feeaa7d1f85dbba38809ec62e2eccbde1189338fb492018b8038f8817a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b01655482ecbe77b284c1cfbe2844b37c395a455cdb20b310c57a1ee6cd3b27a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77884fd0089d9fc6de63726c3542daed6f561fc4a2c618da9b4a2b863fddadd6(
    *,
    deleted_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_sqlite_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_tag: typing.Optional[builtins.str] = None,
    old_tag: typing.Optional[builtins.str] = None,
    renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsRenamedClasses, typing.Dict[builtins.str, typing.Any]]]]] = None,
    steps: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsSteps, typing.Dict[builtins.str, typing.Any]]]]] = None,
    transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsTransferredClasses, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93d7850a844e7140864fee10d0d2a30c31598e87f5e82dde40e22e28be126efa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6227d44996bdb22fe6946420d21a32ec33158318e461b8db5d862272cc48571(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsRenamedClasses, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac42f14b0096001cc42e9558cab4b6e353cbf7f75906b0ebd0092b5c2f7f899d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsSteps, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__604ab05bde36cb6742ea627b751232ed4c8389f76bffa909396f90bd73553aa5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsTransferredClasses, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d7d96657384239204a35ebbd05c02cca84b0c4410409bc2afda3d49ccd105f4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2e5984b12f70f2bd7b94ca326708a20c257b922a332a14a5efc64731d6e5078(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__420864f79612ba129607c232ac612e2c6d3c52885be1533baf6ba7688f108b4f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0123e7d495d6f64723477e3711b901f171353b660c3d7d11184cebbeff9561d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__798e5c6b620f8472c739129265dfafe965371de33c6db1b799ef080463e107e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d3913ed4b23253bd5b2c133a94e88a367ab3962a2df7676f86076b059bc1466(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c473aa6edad6297eb6470bd211c3b55050d3a85e023697d7536058100c3686c5(
    *,
    from_: typing.Optional[builtins.str] = None,
    to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8c31fa0f36b6bb24eae891b21681a225daf4767d06e7757c78fd847a7e6bf05(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90ce64adef6fcb1e0e47e33581529abb73d31ad0bb717b9364ed96bc059c9171(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__996289685e5e1a9029db7a598bc5ad807e12206f80d44f01248a9c8604f5850e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a682eab16cc2f693d1d94a71601cccf52fcfdc1bdc9d563e6a85af6f3aa2dba(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e60d789a4a0ab378627f28ab6f2e8b6f3a0aa5d3237771fcfcee0942ffba9e95(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7b53783dfacf563f9b8f3aaa1e02c4c4c5449b331b40d8bc9f172147c273143(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsRenamedClasses]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__326db70df2d4b0741588cf9a3e377cf0ae7ac83882be603c645f4740437a403a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1770f17205ea949072f6b28512bd631b141a0ba5f79889fd879e01a3d1a87b26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dba1d54c71e9286a33d3109962b89de489507851cd1368ee42da1c3e5918bf65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fbd4c5d0a35c84706335c75b508dd28b0936681e3a2ae66a23ee11fc1a4806a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsRenamedClasses]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7088493dad55bf3b63a5dc6c7b485d9468f93173690f0154b136848b317c558(
    *,
    deleted_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_sqlite_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsStepsRenamedClasses, typing.Dict[builtins.str, typing.Any]]]]] = None,
    transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsStepsTransferredClasses, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb2c79a86857a2fcc5e8cdfb845243f2f512709e44251502906834e11804bcee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e95b8e72ab77b716bb7483ba7af7b766104e68c41473482b780ccd4481fda28(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8f54ab0db04c1f6c43cf4a876b4a35166d396af87c2274b7e73246c5ce22d94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe26b73d5954bef85a76b52df3b1a23d2527e42705eda33abc5d51884a94bfb6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d63b484b3c6faa10e7af65b993d170e1789c2305f7fb3e0776b063201a26ef9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__030c0ae12f81276af708dd066bb0393930eb4a2931342312abc507b26f3e6d74(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsSteps]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf627c724e6ae51204db0eb927dc18a5bc0ef8c68aeab6e83a6efdd457e6cf7c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9327d1eee1acd901a58fe956648286b12c98f2f7764169c32f20797d289ab5a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsStepsRenamedClasses, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae496eb45e48966aadedde5488a496483a1c4ab8f5c900e7c3ca78ec515fa52b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkersScriptMigrationsStepsTransferredClasses, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06dc2f6f382a8ae83a27f296714f02a8a9d2cf91b07cfa4afe4a95e5482e79e1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7f651ebf455b2ce52562a27c7ff92485069db65166777d6d700625049e29478(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93b89c1dbb7fb03604e6146462899fcd516bb2577677f58d7be14ec88772b2ae(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f69415da994f02140d4f2227860179dd297476135258fc41491074770467d863(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsSteps]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__592737dd703b540f7e62e1c70f832fcc880711a482e6c817832565fc8eb518ec(
    *,
    from_: typing.Optional[builtins.str] = None,
    to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b7c66b7db39e43eaf79fe0856333dfc604cb9cd64aae889221bd1dbb24de55(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ac747b043cf737b3d153964641c72d063b07c514a9ef05a8b91f4e211bb84dc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__926d8182ba34061ca3d1f146a43e8f04a4d42f7978e50045738a5d277db30ce7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4a1e43bcf2bb630f72d9403e8c6003eeb1b392dd38691005ee4b6384456e49b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__609403a09bd1fb12a975722f671846298d066b611455f31e3a0f6be98192529a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02fb04885d7f1b50c49982e286223a6cf3b9fd7e6248602453b2451e26ea0fe2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsStepsRenamedClasses]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__411e15b679a7b413b5d2d4e3ea454b89c195c691adb4a3fa459f636835a6fcce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34b20ded3c2dba41ef195cf26ca95aa7061bc1f0ba676d75bc1e5c3cfe8441de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc4146353d041ea0551a89da50bd3cd82804d3935e26336c5d2d229e49578cb5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a75d65bf7124e8060213b2f5de011a9f6a9f98e64c8ba456d24f33a2035102b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsStepsRenamedClasses]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57445ce1958205b95ca6beccd2520856bae790d1d926767c8076d017e3bbf492(
    *,
    from_: typing.Optional[builtins.str] = None,
    from_script: typing.Optional[builtins.str] = None,
    to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2540c3fca44319bb4d5a018ecb1f6ae5ceed60b8238560bdef192ac39128a256(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1be5a8f5d2d31d51d53355ef0786c3887adad981452e8dc60881685fb075ea0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc2d2e679148cdcf6d2d916bd4e3ee21084c314d9ef9641f16e7b1ed2f1c3526(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a042e42b65b7ea5be695530458f4cecd434c20268dd61c3c4bbe1afcdf0a64bb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c35573ccb69edee4f041c3398d262b425d4f2c70334f70855b711e4b8f5a09df(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__222f328e658bd1844a862269974346e124585737dbaa5ce14eb2d3b216cdd890(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsStepsTransferredClasses]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98c9c1f9f1870d659f5f0d9b5def43e82759836382521096c12fac4519a964c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0bec8334b08e601a641f22cc0707323843e941e9ac0a2203e3343e7a4c1b04e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81d1209f7f3b4e1460e8f037cbffb1e656507c35b732ff348c638fe469b5dc32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ea69e264c9a0404f8d1a4039cb1f1c3a9124475e9b8fc73656ec35298ba4a04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6efc371c931e70d1a83692ed34f994e0239251f26f8ab4ce36f0f91ae29de25f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsStepsTransferredClasses]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c6c7274eaf13cbfc51c641d11f7658d743dc4ce38075cfad5ea60c991edca7c(
    *,
    from_: typing.Optional[builtins.str] = None,
    from_script: typing.Optional[builtins.str] = None,
    to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3513662db909869d90c8386008965e2cd405b75c6a9eb4f14e08ab883e6924f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecf5fd7487fcb02de31a29e3844cf83a4420f1183e7ee10dcf4226dbfe2aebec(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__271de41dd32b28b191a8ec592dc56565d35d83b68b294335daa3f35df6e2bb44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__008da140af124637f89156223daf3f6ceee27030a9c7613f790d1e713824fabd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16f2dee1f6c969b0ae8e9c6ab698e52c1edb153b87b3387477fd7d107b11084f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de918e1edc94f7d61e9415da376645dd745f15dce916191bb41a012b29c19d7a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptMigrationsTransferredClasses]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__307267e63a2cd6695ddaead91126b8e62a28be3017aebc5f78241aad13d741c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6968dc48a17fc4e5af18e9b75d2ea6e1c4c1a2af3e298c8a69b120e4a4e1e17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a9c1759bcebe318362470363f9c66febfba070af468c813c5fc24b06984e984(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41c3e155af9013221bf4d4af2f46bd441d08d66c40a3df2d12f4d51674f43b4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d228fdd76609a6c9d336b885095aa6a64726dbfbee03e96e3ed0db7e36498775(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptMigrationsTransferredClasses]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bfd0fb8b8f89f975968ba16e5d763fb3df67d76ba9a3d28e75490fdbdc71ca2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7445fe6f07391b11219adf4953a96c78c379384e998353a52b2a2ca0cb607ea3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c24240c393c7aa42e033deb1fdba71239b1521b1daba5ae52c3ac443f4fb5dfe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1bf727c7459447bbb1f2d20c3004bc2d1d437444a98fa0d58229b9783e94834(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5809334428577add7a35558c290f64e0f2ba6d301ab6347671b9d5316d19d308(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca38724820be7f6dbb07fd92079338a96ea521a8325449522965d4aa6cf3ffd0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4197b6afc12d33e5f41cb1e3631fbbddd9751b00cc8a09ab5d6830c700bf08d(
    value: typing.Optional[WorkersScriptNamedHandlers],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5029f4c4d5da0eec3392e66fd84fd5c15490980c4a078e1373af3c21ee72537(
    *,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    head_sampling_rate: typing.Optional[jsii.Number] = None,
    logs: typing.Optional[typing.Union[WorkersScriptObservabilityLogs, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04afd411ba28ecc838e5dcb95018522e1621a9adab3a72b94418ebaeff55daa6(
    *,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    invocation_logs: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    head_sampling_rate: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58d899a12d289839829fdde23759a85188ca067663257ef9ac88fc071644bf5e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c74a09975767b6738bc584f41de0ffb3624d0e6f659d3541a85d60a740c4c58e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20ab74cc60b754b266f48ec9b2ed99939b79d12afe2f6aefa76aaaaf406bbe47(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66bff00bd740e5fe57ba8f716e539e20d67a98cada1e25b5cbd20193f915444e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4a7fa1e9562244dc0c433c97f29bfda73e646c0055c2cb8fb6fef3ed3cc9d82(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservabilityLogs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbd09163816e15efad432407d02c0161e9cf9dba1518025605e37b478a7dd15d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98c2fde9f53fbd878ebfe2cdefa07a4d13a1af644fd05adfe771517f606dcc73(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2833e1b5ea6fba1c430b60f64786966b0ef7760890de66de1ab70844161b8c8f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e278571f493e634ee19df983eb46ce629c3afcc1de1364447ed1a9b469002e7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptObservability]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5e4978ff81453269afcd828d0429a67b9641991131251e08ef91557a3cab1ea(
    *,
    mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0a158c6e91af48c4f305bec5f3dd074b7898a16087f8fb8d6760231f63f750f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0efbc9bf511fddd2db4b69eab68daae2a4eb96a27da4c0d7144c960dd2835f6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71ccdfa338a27dc2280667eadc3dfa61b4800c5eb4db50906cc4755c705744a8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptPlacement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f868a8834bd616dcea77e492f38ea77965690708a1dc09fc6c8060f3652f44ea(
    *,
    service: builtins.str,
    environment: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c474f127ed43e98c10a336a0b56d2c61ef35b0aa7170059c0b3850686204a493(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94e44d87d24709ddac3be921b14b16da32f8ec189918dfdd4cc2ae3dd50ee03b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__601b6abe8af7e1b47e07ae8ec147298c3ba6ef76826d0948931330ce1ad71d11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73db8851f1d5fbffe886629c7415cfb493d228f4d2076dbc7fef3844af34b8e8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93e55630a459fea1a360ef12551c7f42f7e1dc04c77c58d2cf6ded04b3bd353f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17c20bbbb48ad6c5447801aba5675e88690213431e411b8a3abde1dabde1dde9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkersScriptTailConsumers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e1b8d20abe80031548d626c3fff1c66a999b4325160d67e9a92248ca997d3e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__734378b4355822cceaa55527578766172a32cd5dc6fcb59b8b0e6dd95b48940f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66e5b7292052ec49c45b197f169ec100fedc33104823c74e749bdb92ea81edf2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__173787c724655fcddafe1342ebdb871165e382707dad2d8c7bbf5f7183f4e6d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7d164d2afc247c9121fd9af27a6b9bc0ea23a2ca969aa1644b6dd23a16a26dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkersScriptTailConsumers]],
) -> None:
    """Type checking stubs"""
    pass
