r'''
# `cloudflare_worker_version`

Refer to the Terraform Registry for docs: [`cloudflare_worker_version`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version).
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


class WorkerVersion(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersion",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version cloudflare_worker_version}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        worker_id: builtins.str,
        annotations: typing.Optional[typing.Union["WorkerVersionAnnotations", typing.Dict[builtins.str, typing.Any]]] = None,
        assets: typing.Optional[typing.Union["WorkerVersionAssets", typing.Dict[builtins.str, typing.Any]]] = None,
        bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        compatibility_date: typing.Optional[builtins.str] = None,
        compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        limits: typing.Optional[typing.Union["WorkerVersionLimits", typing.Dict[builtins.str, typing.Any]]] = None,
        main_module: typing.Optional[builtins.str] = None,
        migrations: typing.Optional[typing.Union["WorkerVersionMigrations", typing.Dict[builtins.str, typing.Any]]] = None,
        modules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionModules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        placement: typing.Optional[typing.Union["WorkerVersionPlacement", typing.Dict[builtins.str, typing.Any]]] = None,
        usage_model: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version cloudflare_worker_version} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#account_id WorkerVersion#account_id}
        :param worker_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#worker_id WorkerVersion#worker_id}
        :param annotations: Metadata about the version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#annotations WorkerVersion#annotations}
        :param assets: Configuration for assets within a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#assets WorkerVersion#assets}
        :param bindings: List of bindings attached to a Worker. You can find more about bindings on our docs: https://developers.cloudflare.com/workers/configuration/multipart-upload-metadata/#bindings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#bindings WorkerVersion#bindings}
        :param compatibility_date: Date indicating targeted support in the Workers runtime. Backwards incompatible fixes to the runtime following this date will not affect this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#compatibility_date WorkerVersion#compatibility_date}
        :param compatibility_flags: Flags that enable or disable certain features in the Workers runtime. Used to enable upcoming features or opt in or out of specific changes not included in a ``compatibility_date``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#compatibility_flags WorkerVersion#compatibility_flags}
        :param limits: Resource limits enforced at runtime. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#limits WorkerVersion#limits}
        :param main_module: The name of the main module in the ``modules`` array (e.g. the name of the module that exports a ``fetch`` handler). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#main_module WorkerVersion#main_module}
        :param migrations: Migrations for Durable Objects associated with the version. Migrations are applied when the version is deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#migrations WorkerVersion#migrations}
        :param modules: Code, sourcemaps, and other content used at runtime. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#modules WorkerVersion#modules}
        :param placement: Placement settings for the version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#placement WorkerVersion#placement}
        :param usage_model: Usage model for the version. Available values: "standard", "bundled", "unbound". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#usage_model WorkerVersion#usage_model}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08ad46a5ce4981a31d82a20a1657bcf81c69265e890a48ed4aed498443854bbe)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = WorkerVersionConfig(
            account_id=account_id,
            worker_id=worker_id,
            annotations=annotations,
            assets=assets,
            bindings=bindings,
            compatibility_date=compatibility_date,
            compatibility_flags=compatibility_flags,
            limits=limits,
            main_module=main_module,
            migrations=migrations,
            modules=modules,
            placement=placement,
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
        '''Generates CDKTF code for importing a WorkerVersion resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the WorkerVersion to import.
        :param import_from_id: The id of the existing WorkerVersion that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the WorkerVersion to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8858d18054a049134a3f21caf9070dc086d77fec99e377405a82e7275e3666f5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAnnotations")
    def put_annotations(
        self,
        *,
        workers_message: typing.Optional[builtins.str] = None,
        workers_tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param workers_message: Human-readable message about the version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#workers_message WorkerVersion#workers_message}
        :param workers_tag: User-provided identifier for the version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#workers_tag WorkerVersion#workers_tag}
        '''
        value = WorkerVersionAnnotations(
            workers_message=workers_message, workers_tag=workers_tag
        )

        return typing.cast(None, jsii.invoke(self, "putAnnotations", [value]))

    @jsii.member(jsii_name="putAssets")
    def put_assets(
        self,
        *,
        config: typing.Optional[typing.Union["WorkerVersionAssetsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        jwt: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: Configuration for assets within a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#config WorkerVersion#config}
        :param jwt: Token provided upon successful upload of all files from a registered manifest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#jwt WorkerVersion#jwt}
        '''
        value = WorkerVersionAssets(config=config, jwt=jwt)

        return typing.cast(None, jsii.invoke(self, "putAssets", [value]))

    @jsii.member(jsii_name="putBindings")
    def put_bindings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionBindings", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__840bfa73e51d1a11e3a7a8c1237d1bd959fd3a5067b4468eaa08dcff1e433b7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBindings", [value]))

    @jsii.member(jsii_name="putLimits")
    def put_limits(self, *, cpu_ms: jsii.Number) -> None:
        '''
        :param cpu_ms: CPU time limit in milliseconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#cpu_ms WorkerVersion#cpu_ms}
        '''
        value = WorkerVersionLimits(cpu_ms=cpu_ms)

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
        renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
        steps: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsSteps", typing.Dict[builtins.str, typing.Any]]]]] = None,
        transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param deleted_classes: A list of classes to delete Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#deleted_classes WorkerVersion#deleted_classes}
        :param new_classes: A list of classes to create Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_classes WorkerVersion#new_classes}
        :param new_sqlite_classes: A list of classes to create Durable Object namespaces with SQLite from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_sqlite_classes WorkerVersion#new_sqlite_classes}
        :param new_tag: Tag to set as the latest migration tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_tag WorkerVersion#new_tag}
        :param old_tag: Tag used to verify against the latest migration tag for this Worker. If they don't match, the upload is rejected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#old_tag WorkerVersion#old_tag}
        :param renamed_classes: A list of classes with Durable Object namespaces that were renamed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#renamed_classes WorkerVersion#renamed_classes}
        :param steps: Migrations to apply in order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#steps WorkerVersion#steps}
        :param transferred_classes: A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#transferred_classes WorkerVersion#transferred_classes}
        '''
        value = WorkerVersionMigrations(
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

    @jsii.member(jsii_name="putModules")
    def put_modules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionModules", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e95f5190f27b284d97a2b893e728bc60d2e3e46601a323db56d180f1f724747c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putModules", [value]))

    @jsii.member(jsii_name="putPlacement")
    def put_placement(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Placement mode for the version. Available values: "smart". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#mode WorkerVersion#mode}
        '''
        value = WorkerVersionPlacement(mode=mode)

        return typing.cast(None, jsii.invoke(self, "putPlacement", [value]))

    @jsii.member(jsii_name="resetAnnotations")
    def reset_annotations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnnotations", []))

    @jsii.member(jsii_name="resetAssets")
    def reset_assets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssets", []))

    @jsii.member(jsii_name="resetBindings")
    def reset_bindings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBindings", []))

    @jsii.member(jsii_name="resetCompatibilityDate")
    def reset_compatibility_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibilityDate", []))

    @jsii.member(jsii_name="resetCompatibilityFlags")
    def reset_compatibility_flags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibilityFlags", []))

    @jsii.member(jsii_name="resetLimits")
    def reset_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLimits", []))

    @jsii.member(jsii_name="resetMainModule")
    def reset_main_module(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMainModule", []))

    @jsii.member(jsii_name="resetMigrations")
    def reset_migrations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMigrations", []))

    @jsii.member(jsii_name="resetModules")
    def reset_modules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModules", []))

    @jsii.member(jsii_name="resetPlacement")
    def reset_placement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlacement", []))

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
    @jsii.member(jsii_name="annotations")
    def annotations(self) -> "WorkerVersionAnnotationsOutputReference":
        return typing.cast("WorkerVersionAnnotationsOutputReference", jsii.get(self, "annotations"))

    @builtins.property
    @jsii.member(jsii_name="assets")
    def assets(self) -> "WorkerVersionAssetsOutputReference":
        return typing.cast("WorkerVersionAssetsOutputReference", jsii.get(self, "assets"))

    @builtins.property
    @jsii.member(jsii_name="bindings")
    def bindings(self) -> "WorkerVersionBindingsList":
        return typing.cast("WorkerVersionBindingsList", jsii.get(self, "bindings"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="limits")
    def limits(self) -> "WorkerVersionLimitsOutputReference":
        return typing.cast("WorkerVersionLimitsOutputReference", jsii.get(self, "limits"))

    @builtins.property
    @jsii.member(jsii_name="migrations")
    def migrations(self) -> "WorkerVersionMigrationsOutputReference":
        return typing.cast("WorkerVersionMigrationsOutputReference", jsii.get(self, "migrations"))

    @builtins.property
    @jsii.member(jsii_name="modules")
    def modules(self) -> "WorkerVersionModulesList":
        return typing.cast("WorkerVersionModulesList", jsii.get(self, "modules"))

    @builtins.property
    @jsii.member(jsii_name="number")
    def number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "number"))

    @builtins.property
    @jsii.member(jsii_name="placement")
    def placement(self) -> "WorkerVersionPlacementOutputReference":
        return typing.cast("WorkerVersionPlacementOutputReference", jsii.get(self, "placement"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="annotationsInput")
    def annotations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionAnnotations"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionAnnotations"]], jsii.get(self, "annotationsInput"))

    @builtins.property
    @jsii.member(jsii_name="assetsInput")
    def assets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionAssets"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionAssets"]], jsii.get(self, "assetsInput"))

    @builtins.property
    @jsii.member(jsii_name="bindingsInput")
    def bindings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionBindings"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionBindings"]]], jsii.get(self, "bindingsInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityDateInput")
    def compatibility_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "compatibilityDateInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlagsInput")
    def compatibility_flags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "compatibilityFlagsInput"))

    @builtins.property
    @jsii.member(jsii_name="limitsInput")
    def limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionLimits"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionLimits"]], jsii.get(self, "limitsInput"))

    @builtins.property
    @jsii.member(jsii_name="mainModuleInput")
    def main_module_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mainModuleInput"))

    @builtins.property
    @jsii.member(jsii_name="migrationsInput")
    def migrations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionMigrations"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionMigrations"]], jsii.get(self, "migrationsInput"))

    @builtins.property
    @jsii.member(jsii_name="modulesInput")
    def modules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionModules"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionModules"]]], jsii.get(self, "modulesInput"))

    @builtins.property
    @jsii.member(jsii_name="placementInput")
    def placement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionPlacement"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionPlacement"]], jsii.get(self, "placementInput"))

    @builtins.property
    @jsii.member(jsii_name="usageModelInput")
    def usage_model_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usageModelInput"))

    @builtins.property
    @jsii.member(jsii_name="workerIdInput")
    def worker_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workerIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dec5cab388eed714c6d39ef5e76bc827c69738d345982e7ffc6579a9a74579d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="compatibilityDate")
    def compatibility_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compatibilityDate"))

    @compatibility_date.setter
    def compatibility_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec243f5551ac782d5f47248be4e8a1b521a1c28df13196a715d9d18468b40a16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compatibilityDate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlags")
    def compatibility_flags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibilityFlags"))

    @compatibility_flags.setter
    def compatibility_flags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5525e47585918fab974a8d6e5433ccecc4e4ffc0a2d2699487f3e3dd723d15f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compatibilityFlags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mainModule")
    def main_module(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mainModule"))

    @main_module.setter
    def main_module(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbfc5b17e0c8bb8c7c81079cfe8631164214ccf1bce5eaf612339531495f9524)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mainModule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usageModel")
    def usage_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usageModel"))

    @usage_model.setter
    def usage_model(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bdb2befb8df817d827b4b3a5e071954483a090ffdb94af0bb1201727238aab0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usageModel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workerId")
    def worker_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workerId"))

    @worker_id.setter
    def worker_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10fc08db63215ff8721a73d6de587b1cdfa3839cd4f51f79085af7db68accf67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workerId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionAnnotations",
    jsii_struct_bases=[],
    name_mapping={"workers_message": "workersMessage", "workers_tag": "workersTag"},
)
class WorkerVersionAnnotations:
    def __init__(
        self,
        *,
        workers_message: typing.Optional[builtins.str] = None,
        workers_tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param workers_message: Human-readable message about the version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#workers_message WorkerVersion#workers_message}
        :param workers_tag: User-provided identifier for the version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#workers_tag WorkerVersion#workers_tag}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__832ae4b4becd4f8273ae4a07ec390fb17c50e0a5faf2ba2376172f94000fcd42)
            check_type(argname="argument workers_message", value=workers_message, expected_type=type_hints["workers_message"])
            check_type(argname="argument workers_tag", value=workers_tag, expected_type=type_hints["workers_tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if workers_message is not None:
            self._values["workers_message"] = workers_message
        if workers_tag is not None:
            self._values["workers_tag"] = workers_tag

    @builtins.property
    def workers_message(self) -> typing.Optional[builtins.str]:
        '''Human-readable message about the version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#workers_message WorkerVersion#workers_message}
        '''
        result = self._values.get("workers_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workers_tag(self) -> typing.Optional[builtins.str]:
        '''User-provided identifier for the version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#workers_tag WorkerVersion#workers_tag}
        '''
        result = self._values.get("workers_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionAnnotations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionAnnotationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionAnnotationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8feb7f5f99433826a177055a4f5f03b130d6fdec7b40155ec3572c056f7c590e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetWorkersMessage")
    def reset_workers_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkersMessage", []))

    @jsii.member(jsii_name="resetWorkersTag")
    def reset_workers_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkersTag", []))

    @builtins.property
    @jsii.member(jsii_name="workersTriggeredBy")
    def workers_triggered_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workersTriggeredBy"))

    @builtins.property
    @jsii.member(jsii_name="workersMessageInput")
    def workers_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workersMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="workersTagInput")
    def workers_tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workersTagInput"))

    @builtins.property
    @jsii.member(jsii_name="workersMessage")
    def workers_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workersMessage"))

    @workers_message.setter
    def workers_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf83c73a709492bb58c82b7ab9d1bfcbcdeb0db9f166df7debd3041e0ce78523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workersMessage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workersTag")
    def workers_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workersTag"))

    @workers_tag.setter
    def workers_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db281bdb371dcf9763be1243186a7e12d155d8591053eed410a9556b01b950cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workersTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAnnotations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAnnotations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAnnotations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__308d915d899e2349ae39f4928d27f62e8bc8c5ae5aa8ec350ebfb5c4a08eb0af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionAssets",
    jsii_struct_bases=[],
    name_mapping={"config": "config", "jwt": "jwt"},
)
class WorkerVersionAssets:
    def __init__(
        self,
        *,
        config: typing.Optional[typing.Union["WorkerVersionAssetsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        jwt: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: Configuration for assets within a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#config WorkerVersion#config}
        :param jwt: Token provided upon successful upload of all files from a registered manifest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#jwt WorkerVersion#jwt}
        '''
        if isinstance(config, dict):
            config = WorkerVersionAssetsConfig(**config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fbde8de83cf28d59b5810a869493fa3932383f8c50d47cbf845ad91fd727428)
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument jwt", value=jwt, expected_type=type_hints["jwt"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config is not None:
            self._values["config"] = config
        if jwt is not None:
            self._values["jwt"] = jwt

    @builtins.property
    def config(self) -> typing.Optional["WorkerVersionAssetsConfig"]:
        '''Configuration for assets within a Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#config WorkerVersion#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional["WorkerVersionAssetsConfig"], result)

    @builtins.property
    def jwt(self) -> typing.Optional[builtins.str]:
        '''Token provided upon successful upload of all files from a registered manifest.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#jwt WorkerVersion#jwt}
        '''
        result = self._values.get("jwt")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionAssets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionAssetsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "html_handling": "htmlHandling",
        "not_found_handling": "notFoundHandling",
        "run_worker_first": "runWorkerFirst",
    },
)
class WorkerVersionAssetsConfig:
    def __init__(
        self,
        *,
        html_handling: typing.Optional[builtins.str] = None,
        not_found_handling: typing.Optional[builtins.str] = None,
        run_worker_first: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param html_handling: Determines the redirects and rewrites of requests for HTML content. Available values: "auto-trailing-slash", "force-trailing-slash", "drop-trailing-slash", "none". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#html_handling WorkerVersion#html_handling}
        :param not_found_handling: Determines the response when a request does not match a static asset, and there is no Worker script. Available values: "none", "404-page", "single-page-application". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#not_found_handling WorkerVersion#not_found_handling}
        :param run_worker_first: Contains a list path rules to control routing to either the Worker or assets. Glob (*) and negative (!) rules are supported. Rules must start with either '/' or '!/'. At least one non-negative rule must be provided, and negative rules have higher precedence than non-negative rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#run_worker_first WorkerVersion#run_worker_first}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5d159be0c569683688603b63651aec4868c913c385ef75fe22d3a327d4204da)
            check_type(argname="argument html_handling", value=html_handling, expected_type=type_hints["html_handling"])
            check_type(argname="argument not_found_handling", value=not_found_handling, expected_type=type_hints["not_found_handling"])
            check_type(argname="argument run_worker_first", value=run_worker_first, expected_type=type_hints["run_worker_first"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if html_handling is not None:
            self._values["html_handling"] = html_handling
        if not_found_handling is not None:
            self._values["not_found_handling"] = not_found_handling
        if run_worker_first is not None:
            self._values["run_worker_first"] = run_worker_first

    @builtins.property
    def html_handling(self) -> typing.Optional[builtins.str]:
        '''Determines the redirects and rewrites of requests for HTML content. Available values: "auto-trailing-slash", "force-trailing-slash", "drop-trailing-slash", "none".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#html_handling WorkerVersion#html_handling}
        '''
        result = self._values.get("html_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_found_handling(self) -> typing.Optional[builtins.str]:
        '''Determines the response when a request does not match a static asset, and there is no Worker script.

        Available values: "none", "404-page", "single-page-application".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#not_found_handling WorkerVersion#not_found_handling}
        '''
        result = self._values.get("not_found_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_worker_first(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Contains a list path rules to control routing to either the Worker or assets.

        Glob (*) and negative (!) rules are supported. Rules must start with either '/' or '!/'. At least one non-negative rule must be provided, and negative rules have higher precedence than non-negative rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#run_worker_first WorkerVersion#run_worker_first}
        '''
        result = self._values.get("run_worker_first")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionAssetsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionAssetsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionAssetsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2158355f0ed29aaee465725331cc0d013fbf3a27cb2044a804ef07bfe834f988)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHtmlHandling")
    def reset_html_handling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHtmlHandling", []))

    @jsii.member(jsii_name="resetNotFoundHandling")
    def reset_not_found_handling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotFoundHandling", []))

    @jsii.member(jsii_name="resetRunWorkerFirst")
    def reset_run_worker_first(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunWorkerFirst", []))

    @builtins.property
    @jsii.member(jsii_name="htmlHandlingInput")
    def html_handling_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "htmlHandlingInput"))

    @builtins.property
    @jsii.member(jsii_name="notFoundHandlingInput")
    def not_found_handling_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notFoundHandlingInput"))

    @builtins.property
    @jsii.member(jsii_name="runWorkerFirstInput")
    def run_worker_first_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "runWorkerFirstInput"))

    @builtins.property
    @jsii.member(jsii_name="htmlHandling")
    def html_handling(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlHandling"))

    @html_handling.setter
    def html_handling(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b4872b1095bb1f2f6e31c7369d55d65e6023549dd9a4bb2b4cd4089f92c5edd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "htmlHandling", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notFoundHandling")
    def not_found_handling(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notFoundHandling"))

    @not_found_handling.setter
    def not_found_handling(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4893dbd85e2b815d5727c4893511fe07bb4ad4edcc3079dd0b346878b2a5695b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notFoundHandling", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runWorkerFirst")
    def run_worker_first(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "runWorkerFirst"))

    @run_worker_first.setter
    def run_worker_first(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bc93d60b83fc08df00c74cae3ce6df83e5c21da4b5f9b09a0db2dca161ba1da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runWorkerFirst", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssetsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssetsConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssetsConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac4bcc29f1eb2461649ab288b21ec276d5ce3981c20e9c3af2f60864012bcdbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkerVersionAssetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionAssetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5337e4c78b57d8af7bce2fa8506eb71c54d46ed37f6ff7acbde87774f78e5ed5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        html_handling: typing.Optional[builtins.str] = None,
        not_found_handling: typing.Optional[builtins.str] = None,
        run_worker_first: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param html_handling: Determines the redirects and rewrites of requests for HTML content. Available values: "auto-trailing-slash", "force-trailing-slash", "drop-trailing-slash", "none". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#html_handling WorkerVersion#html_handling}
        :param not_found_handling: Determines the response when a request does not match a static asset, and there is no Worker script. Available values: "none", "404-page", "single-page-application". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#not_found_handling WorkerVersion#not_found_handling}
        :param run_worker_first: Contains a list path rules to control routing to either the Worker or assets. Glob (*) and negative (!) rules are supported. Rules must start with either '/' or '!/'. At least one non-negative rule must be provided, and negative rules have higher precedence than non-negative rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#run_worker_first WorkerVersion#run_worker_first}
        '''
        value = WorkerVersionAssetsConfig(
            html_handling=html_handling,
            not_found_handling=not_found_handling,
            run_worker_first=run_worker_first,
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
    def config(self) -> WorkerVersionAssetsConfigOutputReference:
        return typing.cast(WorkerVersionAssetsConfigOutputReference, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssetsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssetsConfig]], jsii.get(self, "configInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__9f54c29d5a6c7924ef66ccfeeebb2625f25df52a8c678b777d84eb151621655a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d06c605a59d92168c01a2ddf18a44ff2dd380f01224239712973e51db03cc31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionBindings",
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
class WorkerVersionBindings:
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
        outbound: typing.Optional[typing.Union["WorkerVersionBindingsOutbound", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param name: A JavaScript variable name for the binding. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#name WorkerVersion#name}
        :param type: The kind of resource that the binding provides. Available values: "ai", "analytics_engine", "assets", "browser", "d1", "dispatch_namespace", "durable_object_namespace", "hyperdrive", "json", "kv_namespace", "mtls_certificate", "plain_text", "pipelines", "queue", "r2_bucket", "secret_text", "service", "tail_consumer", "vectorize", "version_metadata", "secrets_store_secret", "secret_key", "workflow". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#type WorkerVersion#type}
        :param algorithm: Algorithm-specific key parameters. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#algorithm>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#algorithm WorkerVersion#algorithm}
        :param bucket_name: R2 bucket to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#bucket_name WorkerVersion#bucket_name}
        :param certificate_id: Identifier of the certificate to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#certificate_id WorkerVersion#certificate_id}
        :param class_name: The exported class name of the Durable Object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#class_name WorkerVersion#class_name}
        :param dataset: The name of the dataset to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#dataset WorkerVersion#dataset}
        :param environment: The environment of the script_name to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#environment WorkerVersion#environment}
        :param format: Data format of the key. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#format>`_. Available values: "raw", "pkcs8", "spki", "jwk". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#format WorkerVersion#format}
        :param id: Identifier of the D1 database to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#id WorkerVersion#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param index_name: Name of the Vectorize index to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#index_name WorkerVersion#index_name}
        :param json: JSON data to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#json WorkerVersion#json}
        :param key_base64: Base64-encoded key data. Required if ``format`` is "raw", "pkcs8", or "spki". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#key_base64 WorkerVersion#key_base64}
        :param key_jwk: Key data in `JSON Web Key <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#json_web_key>`_ format. Required if ``format`` is "jwk". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#key_jwk WorkerVersion#key_jwk}
        :param namespace: Namespace to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#namespace WorkerVersion#namespace}
        :param namespace_id: Namespace identifier tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#namespace_id WorkerVersion#namespace_id}
        :param outbound: Outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#outbound WorkerVersion#outbound}
        :param pipeline: Name of the Pipeline to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#pipeline WorkerVersion#pipeline}
        :param queue_name: Name of the Queue to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#queue_name WorkerVersion#queue_name}
        :param script_name: The script where the Durable Object is defined, if it is external to this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#script_name WorkerVersion#script_name}
        :param secret_name: Name of the secret in the store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#secret_name WorkerVersion#secret_name}
        :param service: Name of Worker to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#service WorkerVersion#service}
        :param store_id: ID of the store containing the secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#store_id WorkerVersion#store_id}
        :param text: The text value to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#text WorkerVersion#text}
        :param usages: Allowed operations with the key. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#keyUsages>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#usages WorkerVersion#usages}
        :param workflow_name: Name of the Workflow to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#workflow_name WorkerVersion#workflow_name}
        '''
        if isinstance(outbound, dict):
            outbound = WorkerVersionBindingsOutbound(**outbound)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12b4737c3be093758d4ca1f447041bcfbcc09934b193ad03c2a73d004dc0744a)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#name WorkerVersion#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The kind of resource that the binding provides.

        Available values: "ai", "analytics_engine", "assets", "browser", "d1", "dispatch_namespace", "durable_object_namespace", "hyperdrive", "json", "kv_namespace", "mtls_certificate", "plain_text", "pipelines", "queue", "r2_bucket", "secret_text", "service", "tail_consumer", "vectorize", "version_metadata", "secrets_store_secret", "secret_key", "workflow".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#type WorkerVersion#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def algorithm(self) -> typing.Optional[builtins.str]:
        '''Algorithm-specific key parameters. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#algorithm>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#algorithm WorkerVersion#algorithm}
        '''
        result = self._values.get("algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''R2 bucket to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#bucket_name WorkerVersion#bucket_name}
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_id(self) -> typing.Optional[builtins.str]:
        '''Identifier of the certificate to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#certificate_id WorkerVersion#certificate_id}
        '''
        result = self._values.get("certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def class_name(self) -> typing.Optional[builtins.str]:
        '''The exported class name of the Durable Object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#class_name WorkerVersion#class_name}
        '''
        result = self._values.get("class_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dataset(self) -> typing.Optional[builtins.str]:
        '''The name of the dataset to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#dataset WorkerVersion#dataset}
        '''
        result = self._values.get("dataset")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(self) -> typing.Optional[builtins.str]:
        '''The environment of the script_name to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#environment WorkerVersion#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''Data format of the key. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#format>`_. Available values: "raw", "pkcs8", "spki", "jwk".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#format WorkerVersion#format}
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Identifier of the D1 database to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#id WorkerVersion#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def index_name(self) -> typing.Optional[builtins.str]:
        '''Name of the Vectorize index to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#index_name WorkerVersion#index_name}
        '''
        result = self._values.get("index_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.str]:
        '''JSON data to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#json WorkerVersion#json}
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_base64(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded key data. Required if ``format`` is "raw", "pkcs8", or "spki".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#key_base64 WorkerVersion#key_base64}
        '''
        result = self._values.get("key_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_jwk(self) -> typing.Optional[builtins.str]:
        '''Key data in `JSON Web Key <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#json_web_key>`_ format. Required if ``format`` is "jwk".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#key_jwk WorkerVersion#key_jwk}
        '''
        result = self._values.get("key_jwk")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Namespace to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#namespace WorkerVersion#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''Namespace identifier tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#namespace_id WorkerVersion#namespace_id}
        '''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outbound(self) -> typing.Optional["WorkerVersionBindingsOutbound"]:
        '''Outbound worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#outbound WorkerVersion#outbound}
        '''
        result = self._values.get("outbound")
        return typing.cast(typing.Optional["WorkerVersionBindingsOutbound"], result)

    @builtins.property
    def pipeline(self) -> typing.Optional[builtins.str]:
        '''Name of the Pipeline to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#pipeline WorkerVersion#pipeline}
        '''
        result = self._values.get("pipeline")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_name(self) -> typing.Optional[builtins.str]:
        '''Name of the Queue to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#queue_name WorkerVersion#queue_name}
        '''
        result = self._values.get("queue_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def script_name(self) -> typing.Optional[builtins.str]:
        '''The script where the Durable Object is defined, if it is external to this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#script_name WorkerVersion#script_name}
        '''
        result = self._values.get("script_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''Name of the secret in the store.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#secret_name WorkerVersion#secret_name}
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''Name of Worker to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#service WorkerVersion#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def store_id(self) -> typing.Optional[builtins.str]:
        '''ID of the store containing the secret.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#store_id WorkerVersion#store_id}
        '''
        result = self._values.get("store_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def text(self) -> typing.Optional[builtins.str]:
        '''The text value to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#text WorkerVersion#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Allowed operations with the key. `Learn more <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey#keyUsages>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#usages WorkerVersion#usages}
        '''
        result = self._values.get("usages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_name(self) -> typing.Optional[builtins.str]:
        '''Name of the Workflow to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#workflow_name WorkerVersion#workflow_name}
        '''
        result = self._values.get("workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionBindingsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionBindingsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5103f322893f06edacd146f2d7ef1605421a039c981628ff2d9b7c435bf54b58)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WorkerVersionBindingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__926e840371b6d2e591826d5665e3ee65ed4a148a9cc51ccf62819d945611323b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkerVersionBindingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f828c7f714ae243807bbabb84b1a6cfa69195d91b3e0a7d5c754f6f441990df)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ad29e39a22917393fcb434e4683ef84316223519adcc27bd0b5c760c2f2d1ca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__311c6d44c7341415f05c425d8f39c7e6255cfde19fb4402fb83d20428158edee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionBindings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionBindings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea2da92a77729c63583e995600eb6e84cf6f0d697893d077ce7b9e039c5a5616)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionBindingsOutbound",
    jsii_struct_bases=[],
    name_mapping={"params": "params", "worker": "worker"},
)
class WorkerVersionBindingsOutbound:
    def __init__(
        self,
        *,
        params: typing.Optional[typing.Sequence[builtins.str]] = None,
        worker: typing.Optional[typing.Union["WorkerVersionBindingsOutboundWorker", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param params: Pass information from the Dispatch Worker to the Outbound Worker through the parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#params WorkerVersion#params}
        :param worker: Outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#worker WorkerVersion#worker}
        '''
        if isinstance(worker, dict):
            worker = WorkerVersionBindingsOutboundWorker(**worker)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2f60aed4a7d58aeeb8d1b764fb0ba450b7970300cdcec9486cd6f95a0b7bb52)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#params WorkerVersion#params}
        '''
        result = self._values.get("params")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def worker(self) -> typing.Optional["WorkerVersionBindingsOutboundWorker"]:
        '''Outbound worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#worker WorkerVersion#worker}
        '''
        result = self._values.get("worker")
        return typing.cast(typing.Optional["WorkerVersionBindingsOutboundWorker"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionBindingsOutbound(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionBindingsOutboundOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionBindingsOutboundOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a20350bbc91caf4d268758d2a8ef06828c6a408198684f002cb2560b58b2251)
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
        :param environment: Environment of the outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#environment WorkerVersion#environment}
        :param service: Name of the outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#service WorkerVersion#service}
        '''
        value = WorkerVersionBindingsOutboundWorker(
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
    def worker(self) -> "WorkerVersionBindingsOutboundWorkerOutputReference":
        return typing.cast("WorkerVersionBindingsOutboundWorkerOutputReference", jsii.get(self, "worker"))

    @builtins.property
    @jsii.member(jsii_name="paramsInput")
    def params_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "paramsInput"))

    @builtins.property
    @jsii.member(jsii_name="workerInput")
    def worker_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionBindingsOutboundWorker"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkerVersionBindingsOutboundWorker"]], jsii.get(self, "workerInput"))

    @builtins.property
    @jsii.member(jsii_name="params")
    def params(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "params"))

    @params.setter
    def params(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9652e370337672846e7c30f2268293f7a3ed1f328e3bc734fc6c1fd373a3bd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "params", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutbound]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutbound]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutbound]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaad2912cbec17dbfad51f1cb616f32c5f6c9eaea160fe457b8b0db0e8ba44fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionBindingsOutboundWorker",
    jsii_struct_bases=[],
    name_mapping={"environment": "environment", "service": "service"},
)
class WorkerVersionBindingsOutboundWorker:
    def __init__(
        self,
        *,
        environment: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param environment: Environment of the outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#environment WorkerVersion#environment}
        :param service: Name of the outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#service WorkerVersion#service}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbb6e3d252b98b73a11aebbe30c46d4a9ab7912b216885120fc84bc945a9e09d)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#environment WorkerVersion#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''Name of the outbound worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#service WorkerVersion#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionBindingsOutboundWorker(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionBindingsOutboundWorkerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionBindingsOutboundWorkerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d7c33e06e1bcb025d36966a39e2097dbe33a93b478162bed0d10088292090d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db58c9e237e7ac26dd04dd7868493cb3fedd72fa3205c7261faa0c289771cc2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__988013ca1ff7bfec683ba6225cfabf0705196e1c48f738ad2cce6455795f7e5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutboundWorker]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutboundWorker]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutboundWorker]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5ff9184dfd22513186b59342643ff276da9e83329d38fc8b8166d1cc27a807c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkerVersionBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionBindingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8abe1fcb29964aab7ca670c59b5005f7036df8ed903c157a65eec0e55431d86)
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
        worker: typing.Optional[typing.Union[WorkerVersionBindingsOutboundWorker, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param params: Pass information from the Dispatch Worker to the Outbound Worker through the parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#params WorkerVersion#params}
        :param worker: Outbound worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#worker WorkerVersion#worker}
        '''
        value = WorkerVersionBindingsOutbound(params=params, worker=worker)

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
    def outbound(self) -> WorkerVersionBindingsOutboundOutputReference:
        return typing.cast(WorkerVersionBindingsOutboundOutputReference, jsii.get(self, "outbound"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutbound]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutbound]], jsii.get(self, "outboundInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__63382341de1e7fa8615aa72c2344ce7d3965eb5421bfff71dda529bafa6846bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4081019aa62313bdd8cf57dc21274b151c576f7e6e3ba9637402b0f5e69cbae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @certificate_id.setter
    def certificate_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce2674a9ef845f1b4d0514022898d6685f9149aff70eea82cf4569f4f074082c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="className")
    def class_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "className"))

    @class_name.setter
    def class_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__171abb82a439261c3ce13d209c0f11641138bed2ef749f506bd0cfe164b042f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "className", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataset")
    def dataset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataset"))

    @dataset.setter
    def dataset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__216f133658a28fffec8b8074315890a16050657ad4c8f4cb6bf3924cd1f46196)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a7b0dba8d4f8d466bcdf0a4e9f067ac473106f78d543a924cb38db0404cbc32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdb06e399512670a2d580cbc36c116c3ca8e6178d3eba9b59c48627527f52270)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f42e969c9244347ddcfe7ca935247703b634c74112040ac8a4fd5c6736c9d4a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indexName")
    def index_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexName"))

    @index_name.setter
    def index_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b9c64d1bc37b148355f79ef127a2459aa3c90fc54492106f477481ad8b0d22c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indexName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="json")
    def json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "json"))

    @json.setter
    def json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a0a77a9abd8fc609d7d52911eb05e446b979b4e953c40c96052133647ccf0fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "json", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyBase64")
    def key_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyBase64"))

    @key_base64.setter
    def key_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7f79a7f9e9d9c4205c1b23c7a449553cce53d17287d7bbf67f2fa98609b6ddc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyBase64", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyJwk")
    def key_jwk(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyJwk"))

    @key_jwk.setter
    def key_jwk(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88b04c2175dffe143951a1088873f24cd95af0ac2e1520399720c7d9ce1c969a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyJwk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1944e667dbe7823f07e97dad4a9605d32a21ad79e95c3cf011c71908407122da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0684bec5c5b2d4be95ca9cec1e29cb1e8da806b2336571feb38c74340eee20d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @namespace_id.setter
    def namespace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f30d2a22c75fb40af5a1de4653bdcd4c038fe345e5db724458eda8c47c6b4280)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipeline"))

    @pipeline.setter
    def pipeline(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3dc919cd7657508a098153277f5aad5856c7379b7ad7f4cbe9caa2f62025ba5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipeline", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueName")
    def queue_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueName"))

    @queue_name.setter
    def queue_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__271d75c8c08afa98bdb7fd1e0eee55bbf3dc546787d98deed83531247a0ff779)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptName")
    def script_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scriptName"))

    @script_name.setter
    def script_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a60948d4107a366dc128bb85fe2c460ef91e4c788c3f2ef14944a00c596c2066)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretName"))

    @secret_name.setter
    def secret_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a56faf6951a41cfa94838dc2b1a956979003d498ee323aefa1d83b557fd69c17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55d2ceadee35483a24912992202283905980d60301a208f2da113f788b2785f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storeId")
    def store_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storeId"))

    @store_id.setter
    def store_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__096c2414b82860e35b50e7ea0d4257be92d420496f9cd2103c054004a5ec99cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "text"))

    @text.setter
    def text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ccc6f65628a40313e8756a2a08b50dc06241b5f6c1961d70cc9b7df5823ef04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b6ee2d3901f0dcf6fc01a1669fe28a5e2f2bda1456779b5a58c018483c39b3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usages")
    def usages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usages"))

    @usages.setter
    def usages(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4278333132f76ae61d01a7be05f6c2e77d2da95dafdb28b7dd205c65d4ce4825)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workflowName")
    def workflow_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workflowName"))

    @workflow_name.setter
    def workflow_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f90f2495bcc2175f1a23084db839a34d1fef1c7ecc99b16ff2999a970c3af184)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workflowName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__886755413e9bcfe0ec2f352164944fd6cfdd9e30aa97e96355b96e285f61bd91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionConfig",
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
        "worker_id": "workerId",
        "annotations": "annotations",
        "assets": "assets",
        "bindings": "bindings",
        "compatibility_date": "compatibilityDate",
        "compatibility_flags": "compatibilityFlags",
        "limits": "limits",
        "main_module": "mainModule",
        "migrations": "migrations",
        "modules": "modules",
        "placement": "placement",
        "usage_model": "usageModel",
    },
)
class WorkerVersionConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        worker_id: builtins.str,
        annotations: typing.Optional[typing.Union[WorkerVersionAnnotations, typing.Dict[builtins.str, typing.Any]]] = None,
        assets: typing.Optional[typing.Union[WorkerVersionAssets, typing.Dict[builtins.str, typing.Any]]] = None,
        bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
        compatibility_date: typing.Optional[builtins.str] = None,
        compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        limits: typing.Optional[typing.Union["WorkerVersionLimits", typing.Dict[builtins.str, typing.Any]]] = None,
        main_module: typing.Optional[builtins.str] = None,
        migrations: typing.Optional[typing.Union["WorkerVersionMigrations", typing.Dict[builtins.str, typing.Any]]] = None,
        modules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionModules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        placement: typing.Optional[typing.Union["WorkerVersionPlacement", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#account_id WorkerVersion#account_id}
        :param worker_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#worker_id WorkerVersion#worker_id}
        :param annotations: Metadata about the version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#annotations WorkerVersion#annotations}
        :param assets: Configuration for assets within a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#assets WorkerVersion#assets}
        :param bindings: List of bindings attached to a Worker. You can find more about bindings on our docs: https://developers.cloudflare.com/workers/configuration/multipart-upload-metadata/#bindings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#bindings WorkerVersion#bindings}
        :param compatibility_date: Date indicating targeted support in the Workers runtime. Backwards incompatible fixes to the runtime following this date will not affect this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#compatibility_date WorkerVersion#compatibility_date}
        :param compatibility_flags: Flags that enable or disable certain features in the Workers runtime. Used to enable upcoming features or opt in or out of specific changes not included in a ``compatibility_date``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#compatibility_flags WorkerVersion#compatibility_flags}
        :param limits: Resource limits enforced at runtime. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#limits WorkerVersion#limits}
        :param main_module: The name of the main module in the ``modules`` array (e.g. the name of the module that exports a ``fetch`` handler). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#main_module WorkerVersion#main_module}
        :param migrations: Migrations for Durable Objects associated with the version. Migrations are applied when the version is deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#migrations WorkerVersion#migrations}
        :param modules: Code, sourcemaps, and other content used at runtime. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#modules WorkerVersion#modules}
        :param placement: Placement settings for the version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#placement WorkerVersion#placement}
        :param usage_model: Usage model for the version. Available values: "standard", "bundled", "unbound". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#usage_model WorkerVersion#usage_model}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(annotations, dict):
            annotations = WorkerVersionAnnotations(**annotations)
        if isinstance(assets, dict):
            assets = WorkerVersionAssets(**assets)
        if isinstance(limits, dict):
            limits = WorkerVersionLimits(**limits)
        if isinstance(migrations, dict):
            migrations = WorkerVersionMigrations(**migrations)
        if isinstance(placement, dict):
            placement = WorkerVersionPlacement(**placement)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2625646c8d4e832444152af6d90a06ff9807b4aedf0f7121aaca5982f0a61fbc)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument worker_id", value=worker_id, expected_type=type_hints["worker_id"])
            check_type(argname="argument annotations", value=annotations, expected_type=type_hints["annotations"])
            check_type(argname="argument assets", value=assets, expected_type=type_hints["assets"])
            check_type(argname="argument bindings", value=bindings, expected_type=type_hints["bindings"])
            check_type(argname="argument compatibility_date", value=compatibility_date, expected_type=type_hints["compatibility_date"])
            check_type(argname="argument compatibility_flags", value=compatibility_flags, expected_type=type_hints["compatibility_flags"])
            check_type(argname="argument limits", value=limits, expected_type=type_hints["limits"])
            check_type(argname="argument main_module", value=main_module, expected_type=type_hints["main_module"])
            check_type(argname="argument migrations", value=migrations, expected_type=type_hints["migrations"])
            check_type(argname="argument modules", value=modules, expected_type=type_hints["modules"])
            check_type(argname="argument placement", value=placement, expected_type=type_hints["placement"])
            check_type(argname="argument usage_model", value=usage_model, expected_type=type_hints["usage_model"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "worker_id": worker_id,
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
        if annotations is not None:
            self._values["annotations"] = annotations
        if assets is not None:
            self._values["assets"] = assets
        if bindings is not None:
            self._values["bindings"] = bindings
        if compatibility_date is not None:
            self._values["compatibility_date"] = compatibility_date
        if compatibility_flags is not None:
            self._values["compatibility_flags"] = compatibility_flags
        if limits is not None:
            self._values["limits"] = limits
        if main_module is not None:
            self._values["main_module"] = main_module
        if migrations is not None:
            self._values["migrations"] = migrations
        if modules is not None:
            self._values["modules"] = modules
        if placement is not None:
            self._values["placement"] = placement
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#account_id WorkerVersion#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def worker_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#worker_id WorkerVersion#worker_id}
        '''
        result = self._values.get("worker_id")
        assert result is not None, "Required property 'worker_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def annotations(self) -> typing.Optional[WorkerVersionAnnotations]:
        '''Metadata about the version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#annotations WorkerVersion#annotations}
        '''
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[WorkerVersionAnnotations], result)

    @builtins.property
    def assets(self) -> typing.Optional[WorkerVersionAssets]:
        '''Configuration for assets within a Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#assets WorkerVersion#assets}
        '''
        result = self._values.get("assets")
        return typing.cast(typing.Optional[WorkerVersionAssets], result)

    @builtins.property
    def bindings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionBindings]]]:
        '''List of bindings attached to a Worker. You can find more about bindings on our docs: https://developers.cloudflare.com/workers/configuration/multipart-upload-metadata/#bindings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#bindings WorkerVersion#bindings}
        '''
        result = self._values.get("bindings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionBindings]]], result)

    @builtins.property
    def compatibility_date(self) -> typing.Optional[builtins.str]:
        '''Date indicating targeted support in the Workers runtime.

        Backwards incompatible fixes to the runtime following this date will not affect this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#compatibility_date WorkerVersion#compatibility_date}
        '''
        result = self._values.get("compatibility_date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compatibility_flags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Flags that enable or disable certain features in the Workers runtime.

        Used to enable upcoming features or opt in or out of specific changes not included in a ``compatibility_date``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#compatibility_flags WorkerVersion#compatibility_flags}
        '''
        result = self._values.get("compatibility_flags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def limits(self) -> typing.Optional["WorkerVersionLimits"]:
        '''Resource limits enforced at runtime.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#limits WorkerVersion#limits}
        '''
        result = self._values.get("limits")
        return typing.cast(typing.Optional["WorkerVersionLimits"], result)

    @builtins.property
    def main_module(self) -> typing.Optional[builtins.str]:
        '''The name of the main module in the ``modules`` array (e.g. the name of the module that exports a ``fetch`` handler).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#main_module WorkerVersion#main_module}
        '''
        result = self._values.get("main_module")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def migrations(self) -> typing.Optional["WorkerVersionMigrations"]:
        '''Migrations for Durable Objects associated with the version. Migrations are applied when the version is deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#migrations WorkerVersion#migrations}
        '''
        result = self._values.get("migrations")
        return typing.cast(typing.Optional["WorkerVersionMigrations"], result)

    @builtins.property
    def modules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionModules"]]]:
        '''Code, sourcemaps, and other content used at runtime.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#modules WorkerVersion#modules}
        '''
        result = self._values.get("modules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionModules"]]], result)

    @builtins.property
    def placement(self) -> typing.Optional["WorkerVersionPlacement"]:
        '''Placement settings for the version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#placement WorkerVersion#placement}
        '''
        result = self._values.get("placement")
        return typing.cast(typing.Optional["WorkerVersionPlacement"], result)

    @builtins.property
    def usage_model(self) -> typing.Optional[builtins.str]:
        '''Usage model for the version. Available values: "standard", "bundled", "unbound".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#usage_model WorkerVersion#usage_model}
        '''
        result = self._values.get("usage_model")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionLimits",
    jsii_struct_bases=[],
    name_mapping={"cpu_ms": "cpuMs"},
)
class WorkerVersionLimits:
    def __init__(self, *, cpu_ms: jsii.Number) -> None:
        '''
        :param cpu_ms: CPU time limit in milliseconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#cpu_ms WorkerVersion#cpu_ms}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__027385c78410c670f0f619602ea744fca8e7eb89dbfbd6cd1014e74d92a03f51)
            check_type(argname="argument cpu_ms", value=cpu_ms, expected_type=type_hints["cpu_ms"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cpu_ms": cpu_ms,
        }

    @builtins.property
    def cpu_ms(self) -> jsii.Number:
        '''CPU time limit in milliseconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#cpu_ms WorkerVersion#cpu_ms}
        '''
        result = self._values.get("cpu_ms")
        assert result is not None, "Required property 'cpu_ms' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3c7d2a114ae9500b38b41d1c82ce342d08fe1a3413ea0b0900f8e56d952795f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__561633cee3047dc89bc4c98ffd26e8551be9fc796118ee745c029360216f975f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da932a0eee045d5e718a7a341b8ec9237d69fba1d991cf964dd5dcb24b7e39ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrations",
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
class WorkerVersionMigrations:
    def __init__(
        self,
        *,
        deleted_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_sqlite_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_tag: typing.Optional[builtins.str] = None,
        old_tag: typing.Optional[builtins.str] = None,
        renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
        steps: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsSteps", typing.Dict[builtins.str, typing.Any]]]]] = None,
        transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param deleted_classes: A list of classes to delete Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#deleted_classes WorkerVersion#deleted_classes}
        :param new_classes: A list of classes to create Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_classes WorkerVersion#new_classes}
        :param new_sqlite_classes: A list of classes to create Durable Object namespaces with SQLite from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_sqlite_classes WorkerVersion#new_sqlite_classes}
        :param new_tag: Tag to set as the latest migration tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_tag WorkerVersion#new_tag}
        :param old_tag: Tag used to verify against the latest migration tag for this Worker. If they don't match, the upload is rejected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#old_tag WorkerVersion#old_tag}
        :param renamed_classes: A list of classes with Durable Object namespaces that were renamed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#renamed_classes WorkerVersion#renamed_classes}
        :param steps: Migrations to apply in order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#steps WorkerVersion#steps}
        :param transferred_classes: A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#transferred_classes WorkerVersion#transferred_classes}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25627b579f196d73a695bec50f13f8bc1e1388a793d512b42a1be87b5d202fc6)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#deleted_classes WorkerVersion#deleted_classes}
        '''
        result = self._values.get("deleted_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to create Durable Object namespaces from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_classes WorkerVersion#new_classes}
        '''
        result = self._values.get("new_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_sqlite_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to create Durable Object namespaces with SQLite from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_sqlite_classes WorkerVersion#new_sqlite_classes}
        '''
        result = self._values.get("new_sqlite_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_tag(self) -> typing.Optional[builtins.str]:
        '''Tag to set as the latest migration tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_tag WorkerVersion#new_tag}
        '''
        result = self._values.get("new_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def old_tag(self) -> typing.Optional[builtins.str]:
        '''Tag used to verify against the latest migration tag for this Worker.

        If they don't match, the upload is rejected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#old_tag WorkerVersion#old_tag}
        '''
        result = self._values.get("old_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def renamed_classes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsRenamedClasses"]]]:
        '''A list of classes with Durable Object namespaces that were renamed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#renamed_classes WorkerVersion#renamed_classes}
        '''
        result = self._values.get("renamed_classes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsRenamedClasses"]]], result)

    @builtins.property
    def steps(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsSteps"]]]:
        '''Migrations to apply in order.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#steps WorkerVersion#steps}
        '''
        result = self._values.get("steps")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsSteps"]]], result)

    @builtins.property
    def transferred_classes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsTransferredClasses"]]]:
        '''A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#transferred_classes WorkerVersion#transferred_classes}
        '''
        result = self._values.get("transferred_classes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsTransferredClasses"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionMigrations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionMigrationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__980551acf542be24c0dc7541518515f4f2005a35524f4bf7df6d7c78e8ad6046)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRenamedClasses")
    def put_renamed_classes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e8ddeb78d4cfbc9dd1c738eb706bec44916932904621b7c72fcce29cb13ce28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRenamedClasses", [value]))

    @jsii.member(jsii_name="putSteps")
    def put_steps(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsSteps", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f4a04966d96506218e527611290587346595d69e56a2038d75524d0828378ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSteps", [value]))

    @jsii.member(jsii_name="putTransferredClasses")
    def put_transferred_classes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c71b5fabdd9afd9be99d3b4a0613730ab60931c0d1e0f56e96cf2007a8428053)
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
    def renamed_classes(self) -> "WorkerVersionMigrationsRenamedClassesList":
        return typing.cast("WorkerVersionMigrationsRenamedClassesList", jsii.get(self, "renamedClasses"))

    @builtins.property
    @jsii.member(jsii_name="steps")
    def steps(self) -> "WorkerVersionMigrationsStepsList":
        return typing.cast("WorkerVersionMigrationsStepsList", jsii.get(self, "steps"))

    @builtins.property
    @jsii.member(jsii_name="transferredClasses")
    def transferred_classes(self) -> "WorkerVersionMigrationsTransferredClassesList":
        return typing.cast("WorkerVersionMigrationsTransferredClassesList", jsii.get(self, "transferredClasses"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsRenamedClasses"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsRenamedClasses"]]], jsii.get(self, "renamedClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="stepsInput")
    def steps_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsSteps"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsSteps"]]], jsii.get(self, "stepsInput"))

    @builtins.property
    @jsii.member(jsii_name="transferredClassesInput")
    def transferred_classes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsTransferredClasses"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsTransferredClasses"]]], jsii.get(self, "transferredClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="deletedClasses")
    def deleted_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "deletedClasses"))

    @deleted_classes.setter
    def deleted_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22114303b69d217320c539b87504c57b67400e4e3f81d22af4fc096e2aeb0c7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletedClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newClasses")
    def new_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newClasses"))

    @new_classes.setter
    def new_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2c297ee056bf4e355cc6c3f629c9f7d03116c0e108187e964b0813227245ff8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newSqliteClasses")
    def new_sqlite_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newSqliteClasses"))

    @new_sqlite_classes.setter
    def new_sqlite_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b72d44e38c71400ceb1871f4acb37dedf268eb878126e4c81bee89cda6abac3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newSqliteClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newTag")
    def new_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "newTag"))

    @new_tag.setter
    def new_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95402ced0e5db7023a986a5463290b9e468fe8e042603c85efbed28eabf539b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oldTag")
    def old_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oldTag"))

    @old_tag.setter
    def old_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cfefcc775a97eb1ab2054e6bb551921d1dc9d23af3e21cafcaf5840267c27a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oldTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c7b1009fbee01bee7f92fd80ee30e7fbaf19cb50067038930b8d87ee8866da9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsRenamedClasses",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "to": "to"},
)
class WorkerVersionMigrationsRenamedClasses:
    def __init__(
        self,
        *,
        from_: typing.Optional[builtins.str] = None,
        to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from WorkerVersion#from}.
        :param to: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#to WorkerVersion#to}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbf980d3d9ae7d1ae11b4d8a01e0dccf98b8394bb5f6f84841f347d4f75a44f0)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument to", value=to, expected_type=type_hints["to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if from_ is not None:
            self._values["from_"] = from_
        if to is not None:
            self._values["to"] = to

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from WorkerVersion#from}.'''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#to WorkerVersion#to}.'''
        result = self._values.get("to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionMigrationsRenamedClasses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionMigrationsRenamedClassesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsRenamedClassesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9118d0b9218fc239572e13ab30adc7d77769f2878b516dc0834cbe9e754a9fac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkerVersionMigrationsRenamedClassesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb2e6cd44faf4774616410f6bcc38fe7ecb443431db3ff8f16a1842122bedcb0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkerVersionMigrationsRenamedClassesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c470d27a97faadba93493bf43410171f2193d1efc4e7428f606872efec0b6f03)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fd032d2a28035b0dcdf7896c1f2c86c84a40b3993cf9c64a94cd94c1af8b371)
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
            type_hints = typing.get_type_hints(_typecheckingstub__95a66b2a91f9eacdce06582e0d19780de87998fd650395cd2e2daf9491a83934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsRenamedClasses]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsRenamedClasses]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsRenamedClasses]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f612216c2377fb903c5be683c726ec92a403f19d1bdbfed26e07836102983f2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkerVersionMigrationsRenamedClassesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsRenamedClassesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ea59223c112cf1ec82a7095ea56a15e1069d2ff24307f6798495a220b69e1f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__19629168a7a336088aa55b422d93cebcb9c2a05053b36b010b05de7f055215b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="to")
    def to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "to"))

    @to.setter
    def to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3993f67bf69368fefa9f2b15237bddedeac15ef629d8e4e86eb10b41af6b9f1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "to", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsRenamedClasses]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsRenamedClasses]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsRenamedClasses]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46cd998dcca134ff9cc9bf98b3bd2281f1480015c350f1531005e0792a40cfd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsSteps",
    jsii_struct_bases=[],
    name_mapping={
        "deleted_classes": "deletedClasses",
        "new_classes": "newClasses",
        "new_sqlite_classes": "newSqliteClasses",
        "renamed_classes": "renamedClasses",
        "transferred_classes": "transferredClasses",
    },
)
class WorkerVersionMigrationsSteps:
    def __init__(
        self,
        *,
        deleted_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        new_sqlite_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsStepsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
        transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsStepsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param deleted_classes: A list of classes to delete Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#deleted_classes WorkerVersion#deleted_classes}
        :param new_classes: A list of classes to create Durable Object namespaces from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_classes WorkerVersion#new_classes}
        :param new_sqlite_classes: A list of classes to create Durable Object namespaces with SQLite from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_sqlite_classes WorkerVersion#new_sqlite_classes}
        :param renamed_classes: A list of classes with Durable Object namespaces that were renamed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#renamed_classes WorkerVersion#renamed_classes}
        :param transferred_classes: A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#transferred_classes WorkerVersion#transferred_classes}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d61070208315d0c0951a1fdb637f5850512293ba6b08afcf327cecd28a42bd4f)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#deleted_classes WorkerVersion#deleted_classes}
        '''
        result = self._values.get("deleted_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to create Durable Object namespaces from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_classes WorkerVersion#new_classes}
        '''
        result = self._values.get("new_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def new_sqlite_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of classes to create Durable Object namespaces with SQLite from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#new_sqlite_classes WorkerVersion#new_sqlite_classes}
        '''
        result = self._values.get("new_sqlite_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def renamed_classes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsStepsRenamedClasses"]]]:
        '''A list of classes with Durable Object namespaces that were renamed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#renamed_classes WorkerVersion#renamed_classes}
        '''
        result = self._values.get("renamed_classes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsStepsRenamedClasses"]]], result)

    @builtins.property
    def transferred_classes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsStepsTransferredClasses"]]]:
        '''A list of transfers for Durable Object namespaces from a different Worker and class to a class defined in this Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#transferred_classes WorkerVersion#transferred_classes}
        '''
        result = self._values.get("transferred_classes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsStepsTransferredClasses"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionMigrationsSteps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionMigrationsStepsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsStepsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e6c218d3339674cce9df03247803cf49c14ee1c00566da5457f3c7c2d5e6666)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WorkerVersionMigrationsStepsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abb9db9dc8c44a38561ec16f6b50836d2779733e09776b31e3bf4b6d6f84a389)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkerVersionMigrationsStepsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__012cde16ce05a59201a39b95ad7ead36dbf02381e5a3cd84e76d088c8bd55f53)
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
            type_hints = typing.get_type_hints(_typecheckingstub__222e60e526cde50332087c347b4630989b72f559af0e90d806f859c02fa96591)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00eb18c7916418670883b62638feb1e2063499352158120f6903bffefcba7a10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsSteps]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsSteps]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsSteps]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__860ef875ace4f27945984b4939dddf49e8e84d8548ec9c3e9b6370aa53a5c534)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkerVersionMigrationsStepsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsStepsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4f6bf850220cd51918b5e288e14a4d65f979dc80324b3e98617a36275d2600e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putRenamedClasses")
    def put_renamed_classes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsStepsRenamedClasses", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b4976072a82a74f505b526d82c07f587e36734111268ba66f2a42fafdb9fde9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRenamedClasses", [value]))

    @jsii.member(jsii_name="putTransferredClasses")
    def put_transferred_classes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkerVersionMigrationsStepsTransferredClasses", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15117d33fad5050ba7a6adb563df889c51592ab7bbede1d49064184052cff30c)
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
    def renamed_classes(self) -> "WorkerVersionMigrationsStepsRenamedClassesList":
        return typing.cast("WorkerVersionMigrationsStepsRenamedClassesList", jsii.get(self, "renamedClasses"))

    @builtins.property
    @jsii.member(jsii_name="transferredClasses")
    def transferred_classes(
        self,
    ) -> "WorkerVersionMigrationsStepsTransferredClassesList":
        return typing.cast("WorkerVersionMigrationsStepsTransferredClassesList", jsii.get(self, "transferredClasses"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsStepsRenamedClasses"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsStepsRenamedClasses"]]], jsii.get(self, "renamedClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="transferredClassesInput")
    def transferred_classes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsStepsTransferredClasses"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkerVersionMigrationsStepsTransferredClasses"]]], jsii.get(self, "transferredClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="deletedClasses")
    def deleted_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "deletedClasses"))

    @deleted_classes.setter
    def deleted_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2760f5dd0cb9addd4d27288efc32de8bf84135e31f49acc73e946031d37a8eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletedClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newClasses")
    def new_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newClasses"))

    @new_classes.setter
    def new_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d4f173c5b5c5ba4210bd9dcbd664205e1addab621a7f268e2c8da735238f16c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newSqliteClasses")
    def new_sqlite_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "newSqliteClasses"))

    @new_sqlite_classes.setter
    def new_sqlite_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f838169f012880000254794d5ceacc06129bb1ef6f65966a8d03141575004ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newSqliteClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsSteps]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsSteps]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsSteps]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00e51d4b22db99ebca062c60688565030ea6fad8657267c1bba73cffb4752301)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsStepsRenamedClasses",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "to": "to"},
)
class WorkerVersionMigrationsStepsRenamedClasses:
    def __init__(
        self,
        *,
        from_: typing.Optional[builtins.str] = None,
        to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from WorkerVersion#from}.
        :param to: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#to WorkerVersion#to}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc380e7e0007cb58a695d1a802727723b46b5e3bf76a5de8a7c2eb84150167d6)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument to", value=to, expected_type=type_hints["to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if from_ is not None:
            self._values["from_"] = from_
        if to is not None:
            self._values["to"] = to

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from WorkerVersion#from}.'''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#to WorkerVersion#to}.'''
        result = self._values.get("to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionMigrationsStepsRenamedClasses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionMigrationsStepsRenamedClassesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsStepsRenamedClassesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__656bd90d203e0753921573f070c7169bd5f86aa3a64c76ac529acf5a658a894b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkerVersionMigrationsStepsRenamedClassesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb2c738cd1bb4677087d30afffcec0032ec57cd3d995d262c3a81a786b0659fc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkerVersionMigrationsStepsRenamedClassesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5849d7badfec625a83a1f3631371216bb76ca8537851ff6d0938113414f56b4c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c85d2ca52fe65349ac5f07c350b05d21c6be80ced4721a3ff6528ab1a97f797a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__41479cae8f68944df4f0e6264cf018ee13a972a978bf5937bbdfb01fd50e768f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsStepsRenamedClasses]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsStepsRenamedClasses]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsStepsRenamedClasses]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__818c2c9b538fabf2bc0f8939d4eb7dfd119d47f39ee912c4c72e1a9c59c7b4c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkerVersionMigrationsStepsRenamedClassesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsStepsRenamedClassesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__94af87d3caf1dd736c77c0cdec7f63b1d117105515ac5f1d6b360c8a76487d5f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7dacf9bddc942bc5e52056d79df417050ebb5bd15d6771048ed3a6ae3d34a4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="to")
    def to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "to"))

    @to.setter
    def to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf4d8513f476bde99a4e6b7c24ee9789b9d9db9bf8acd7b704c155c863a109bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "to", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsStepsRenamedClasses]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsStepsRenamedClasses]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsStepsRenamedClasses]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__200f39b5a4fbd4e9bd7b8a7dc727c0176f5178b19ea65d5f633fd3da91a255d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsStepsTransferredClasses",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "from_script": "fromScript", "to": "to"},
)
class WorkerVersionMigrationsStepsTransferredClasses:
    def __init__(
        self,
        *,
        from_: typing.Optional[builtins.str] = None,
        from_script: typing.Optional[builtins.str] = None,
        to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from WorkerVersion#from}.
        :param from_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from_script WorkerVersion#from_script}.
        :param to: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#to WorkerVersion#to}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abf8ecfdc89455567126299a9defb1e2e7aa1584bd8a7b92cb9cac5780e78058)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from WorkerVersion#from}.'''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_script(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from_script WorkerVersion#from_script}.'''
        result = self._values.get("from_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#to WorkerVersion#to}.'''
        result = self._values.get("to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionMigrationsStepsTransferredClasses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionMigrationsStepsTransferredClassesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsStepsTransferredClassesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd4988b6f2ff8ac6f4216d8c64ed0f816b530692a6ecae4393678ff826ea66a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkerVersionMigrationsStepsTransferredClassesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eca4327a8846003c24118a42a9a788bdd99d39e0f938408fc52700f4a72a170)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkerVersionMigrationsStepsTransferredClassesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70d2f51f360e8a6d222565ab754915616f9d20c252a1f45b6aa9a661946ba1db)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8cd78e26b17d5f96cab8829bee279b639a48b5c17aea9b74b43739889d46399)
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
            type_hints = typing.get_type_hints(_typecheckingstub__93c9bdd54fd9f87b5842e1bb94be1821438999a931105e9c809c84f9c89e26f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsStepsTransferredClasses]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsStepsTransferredClasses]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsStepsTransferredClasses]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15667fe6f33a3002fdf74d3c9cce6e8b7218443c8263d9eff0bb8e2bd861ebaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkerVersionMigrationsStepsTransferredClassesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsStepsTransferredClassesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa642eaa56df13399897920fca99e3cf795e807c0a0528dadb92e798a7ac2871)
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
            type_hints = typing.get_type_hints(_typecheckingstub__817c72ad78b7f94a363e160600c9ab09054e881e57e452bd3fc82882e4f3d2c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fromScript")
    def from_script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fromScript"))

    @from_script.setter
    def from_script(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5760f2273071e305b2fbce33769af495f814b60e30f80e2d318113b635d4c63c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fromScript", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="to")
    def to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "to"))

    @to.setter
    def to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e33f1def3daba44c3ddac087f9d817a7076822f98be7c2aaf73e35308c6ada34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "to", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsStepsTransferredClasses]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsStepsTransferredClasses]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsStepsTransferredClasses]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__505d86bffd88d57e42aef2c0c3f42b2d1416ce63778c3a66e4ac1353c931c9b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsTransferredClasses",
    jsii_struct_bases=[],
    name_mapping={"from_": "from", "from_script": "fromScript", "to": "to"},
)
class WorkerVersionMigrationsTransferredClasses:
    def __init__(
        self,
        *,
        from_: typing.Optional[builtins.str] = None,
        from_script: typing.Optional[builtins.str] = None,
        to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param from_: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from WorkerVersion#from}.
        :param from_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from_script WorkerVersion#from_script}.
        :param to: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#to WorkerVersion#to}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc296b605b1b12071bb121e5cbeab3805a7165b6b780f3e7ce37f78a1d2132e4)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from WorkerVersion#from}.'''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_script(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#from_script WorkerVersion#from_script}.'''
        result = self._values.get("from_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#to WorkerVersion#to}.'''
        result = self._values.get("to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionMigrationsTransferredClasses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionMigrationsTransferredClassesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsTransferredClassesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__038cea57c3de522bc8a833d0ea8914cf5126b645486b5194bd6b646731baf606)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkerVersionMigrationsTransferredClassesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dfb99d4f054f0fed09887f502d20700ca467f41bc06737ff61acf4bb37dda8f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkerVersionMigrationsTransferredClassesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f120549f229175831d61196d1bc22ad8c06d1dc34e6356e52c83fca789e4e3fb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4519684c4860e068d7d9045bc106da70abc12498b3820d19697dec0005c4edb0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ac3d90176f3233668f0dadfedc37d9a744cd5ed8b8826e6bbba158ba5b40a4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsTransferredClasses]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsTransferredClasses]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsTransferredClasses]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95c25513ee7774a33b5d04e1fb5fca8c3215c0aad3e8588dfcf1ade2b85dd95e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkerVersionMigrationsTransferredClassesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionMigrationsTransferredClassesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1053b8087c03f5ba9bc6c1047f72219d2a24c0bdb2f5bbc10689a838a0fade66)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bba86575a7068989cdd0c7fe355754aaeeeaee1087a4236ab448448e13807401)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fromScript")
    def from_script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fromScript"))

    @from_script.setter
    def from_script(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f3162ed4cddb23706e7c95d22f892a35e7ba1061ef4995b3d4b5eb05e9df3b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fromScript", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="to")
    def to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "to"))

    @to.setter
    def to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d130978b0075dcb1a04f3ba622f2b7b69bf06cb2627d648a0c25e3d054a5e36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "to", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsTransferredClasses]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsTransferredClasses]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsTransferredClasses]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2bc854ab6390c717a802a5bd18967e08be030aebd64cd1d49debb19b863fe0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionModules",
    jsii_struct_bases=[],
    name_mapping={
        "content_file": "contentFile",
        "content_type": "contentType",
        "name": "name",
    },
)
class WorkerVersionModules:
    def __init__(
        self,
        *,
        content_file: builtins.str,
        content_type: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param content_file: The file path of the module content. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#content_file WorkerVersion#content_file}
        :param content_type: The content type of the module. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#content_type WorkerVersion#content_type}
        :param name: The name of the module. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#name WorkerVersion#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a36d2f62a3eb360e964dd8f852ca5cae62f9d0132c11f3391594a2ab3d40e76)
            check_type(argname="argument content_file", value=content_file, expected_type=type_hints["content_file"])
            check_type(argname="argument content_type", value=content_type, expected_type=type_hints["content_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content_file": content_file,
            "content_type": content_type,
            "name": name,
        }

    @builtins.property
    def content_file(self) -> builtins.str:
        '''The file path of the module content.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#content_file WorkerVersion#content_file}
        '''
        result = self._values.get("content_file")
        assert result is not None, "Required property 'content_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_type(self) -> builtins.str:
        '''The content type of the module.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#content_type WorkerVersion#content_type}
        '''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the module.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#name WorkerVersion#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionModules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionModulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionModulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a299a036408b2420958e5f246cb4bb49a7a893924fd610322d9ab59684e24f7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WorkerVersionModulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__073cbf2e783f854d93573159533241c270e0376adaa6fd7227f86a6e8cf6adcc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkerVersionModulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e58ef21517ace6ec59fc3c1829e4b609664afcd9053d99d0c4533677fd75a01)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6776037f277206f8a7f6a055a499c34f06d42e4a30db78b4a57f5402af88f0b3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__761e84530475b3a7a4b4a14b22a55fde78e826a36f032524cbfb0f5d30a0085c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionModules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionModules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionModules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be03ee53a2907001636be351d7d18c59bec42fa35568afb05675dddbf215ceef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkerVersionModulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionModulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__468d3ed1c7fba2de96ca5dfa800144251cad01186378183422b960d4be9b738f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="contentSha256")
    def content_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentSha256"))

    @builtins.property
    @jsii.member(jsii_name="contentFileInput")
    def content_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentFileInput"))

    @builtins.property
    @jsii.member(jsii_name="contentTypeInput")
    def content_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="contentFile")
    def content_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentFile"))

    @content_file.setter
    def content_file(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe04ff291adbf6c4d9eaa636bc94f065c359b54dd6af6cd7ca13c90e2232163c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18e8b4a251c76dd12055d17fb8a26f1ec3f5f4c5919988822279d9f9c928ebb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c85822361b99dea3e201f6fddaf636a09fa5bb1cdf33dd8dfeddf698f44a9713)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionModules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionModules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionModules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8694b5e0fa52cd53ba6e52033a4025e9d69fd4a3046d7543be8a262df3e7aa99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionPlacement",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode"},
)
class WorkerVersionPlacement:
    def __init__(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Placement mode for the version. Available values: "smart". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#mode WorkerVersion#mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__785699a973e235aa8df1bcd27b32c89158cf016e294ee36661162f03a417dc45)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Placement mode for the version. Available values: "smart".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/worker_version#mode WorkerVersion#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkerVersionPlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkerVersionPlacementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.workerVersion.WorkerVersionPlacementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__60858a68c3c71b15a7f3feb49ff04e6c6180cfa3c48430236b6d13eaca939aee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__7b105b6692712ffe9444dc994a10e378d5605be1651a083c6c1c6a1dd4a5b199)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionPlacement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionPlacement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionPlacement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e38af827e03d5cdbb0ae675832edd7b0222c049ce260e6dbf36e58a35ac8050f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "WorkerVersion",
    "WorkerVersionAnnotations",
    "WorkerVersionAnnotationsOutputReference",
    "WorkerVersionAssets",
    "WorkerVersionAssetsConfig",
    "WorkerVersionAssetsConfigOutputReference",
    "WorkerVersionAssetsOutputReference",
    "WorkerVersionBindings",
    "WorkerVersionBindingsList",
    "WorkerVersionBindingsOutbound",
    "WorkerVersionBindingsOutboundOutputReference",
    "WorkerVersionBindingsOutboundWorker",
    "WorkerVersionBindingsOutboundWorkerOutputReference",
    "WorkerVersionBindingsOutputReference",
    "WorkerVersionConfig",
    "WorkerVersionLimits",
    "WorkerVersionLimitsOutputReference",
    "WorkerVersionMigrations",
    "WorkerVersionMigrationsOutputReference",
    "WorkerVersionMigrationsRenamedClasses",
    "WorkerVersionMigrationsRenamedClassesList",
    "WorkerVersionMigrationsRenamedClassesOutputReference",
    "WorkerVersionMigrationsSteps",
    "WorkerVersionMigrationsStepsList",
    "WorkerVersionMigrationsStepsOutputReference",
    "WorkerVersionMigrationsStepsRenamedClasses",
    "WorkerVersionMigrationsStepsRenamedClassesList",
    "WorkerVersionMigrationsStepsRenamedClassesOutputReference",
    "WorkerVersionMigrationsStepsTransferredClasses",
    "WorkerVersionMigrationsStepsTransferredClassesList",
    "WorkerVersionMigrationsStepsTransferredClassesOutputReference",
    "WorkerVersionMigrationsTransferredClasses",
    "WorkerVersionMigrationsTransferredClassesList",
    "WorkerVersionMigrationsTransferredClassesOutputReference",
    "WorkerVersionModules",
    "WorkerVersionModulesList",
    "WorkerVersionModulesOutputReference",
    "WorkerVersionPlacement",
    "WorkerVersionPlacementOutputReference",
]

publication.publish()

def _typecheckingstub__08ad46a5ce4981a31d82a20a1657bcf81c69265e890a48ed4aed498443854bbe(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    worker_id: builtins.str,
    annotations: typing.Optional[typing.Union[WorkerVersionAnnotations, typing.Dict[builtins.str, typing.Any]]] = None,
    assets: typing.Optional[typing.Union[WorkerVersionAssets, typing.Dict[builtins.str, typing.Any]]] = None,
    bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    compatibility_date: typing.Optional[builtins.str] = None,
    compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    limits: typing.Optional[typing.Union[WorkerVersionLimits, typing.Dict[builtins.str, typing.Any]]] = None,
    main_module: typing.Optional[builtins.str] = None,
    migrations: typing.Optional[typing.Union[WorkerVersionMigrations, typing.Dict[builtins.str, typing.Any]]] = None,
    modules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionModules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    placement: typing.Optional[typing.Union[WorkerVersionPlacement, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__8858d18054a049134a3f21caf9070dc086d77fec99e377405a82e7275e3666f5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__840bfa73e51d1a11e3a7a8c1237d1bd959fd3a5067b4468eaa08dcff1e433b7e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionBindings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e95f5190f27b284d97a2b893e728bc60d2e3e46601a323db56d180f1f724747c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionModules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dec5cab388eed714c6d39ef5e76bc827c69738d345982e7ffc6579a9a74579d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec243f5551ac782d5f47248be4e8a1b521a1c28df13196a715d9d18468b40a16(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5525e47585918fab974a8d6e5433ccecc4e4ffc0a2d2699487f3e3dd723d15f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbfc5b17e0c8bb8c7c81079cfe8631164214ccf1bce5eaf612339531495f9524(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bdb2befb8df817d827b4b3a5e071954483a090ffdb94af0bb1201727238aab0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10fc08db63215ff8721a73d6de587b1cdfa3839cd4f51f79085af7db68accf67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__832ae4b4becd4f8273ae4a07ec390fb17c50e0a5faf2ba2376172f94000fcd42(
    *,
    workers_message: typing.Optional[builtins.str] = None,
    workers_tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8feb7f5f99433826a177055a4f5f03b130d6fdec7b40155ec3572c056f7c590e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf83c73a709492bb58c82b7ab9d1bfcbcdeb0db9f166df7debd3041e0ce78523(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db281bdb371dcf9763be1243186a7e12d155d8591053eed410a9556b01b950cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__308d915d899e2349ae39f4928d27f62e8bc8c5ae5aa8ec350ebfb5c4a08eb0af(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAnnotations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fbde8de83cf28d59b5810a869493fa3932383f8c50d47cbf845ad91fd727428(
    *,
    config: typing.Optional[typing.Union[WorkerVersionAssetsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    jwt: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5d159be0c569683688603b63651aec4868c913c385ef75fe22d3a327d4204da(
    *,
    html_handling: typing.Optional[builtins.str] = None,
    not_found_handling: typing.Optional[builtins.str] = None,
    run_worker_first: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2158355f0ed29aaee465725331cc0d013fbf3a27cb2044a804ef07bfe834f988(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b4872b1095bb1f2f6e31c7369d55d65e6023549dd9a4bb2b4cd4089f92c5edd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4893dbd85e2b815d5727c4893511fe07bb4ad4edcc3079dd0b346878b2a5695b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bc93d60b83fc08df00c74cae3ce6df83e5c21da4b5f9b09a0db2dca161ba1da(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac4bcc29f1eb2461649ab288b21ec276d5ce3981c20e9c3af2f60864012bcdbd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssetsConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5337e4c78b57d8af7bce2fa8506eb71c54d46ed37f6ff7acbde87774f78e5ed5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f54c29d5a6c7924ef66ccfeeebb2625f25df52a8c678b777d84eb151621655a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d06c605a59d92168c01a2ddf18a44ff2dd380f01224239712973e51db03cc31(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionAssets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12b4737c3be093758d4ca1f447041bcfbcc09934b193ad03c2a73d004dc0744a(
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
    outbound: typing.Optional[typing.Union[WorkerVersionBindingsOutbound, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__5103f322893f06edacd146f2d7ef1605421a039c981628ff2d9b7c435bf54b58(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__926e840371b6d2e591826d5665e3ee65ed4a148a9cc51ccf62819d945611323b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f828c7f714ae243807bbabb84b1a6cfa69195d91b3e0a7d5c754f6f441990df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ad29e39a22917393fcb434e4683ef84316223519adcc27bd0b5c760c2f2d1ca(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__311c6d44c7341415f05c425d8f39c7e6255cfde19fb4402fb83d20428158edee(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea2da92a77729c63583e995600eb6e84cf6f0d697893d077ce7b9e039c5a5616(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionBindings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2f60aed4a7d58aeeb8d1b764fb0ba450b7970300cdcec9486cd6f95a0b7bb52(
    *,
    params: typing.Optional[typing.Sequence[builtins.str]] = None,
    worker: typing.Optional[typing.Union[WorkerVersionBindingsOutboundWorker, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a20350bbc91caf4d268758d2a8ef06828c6a408198684f002cb2560b58b2251(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9652e370337672846e7c30f2268293f7a3ed1f328e3bc734fc6c1fd373a3bd9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaad2912cbec17dbfad51f1cb616f32c5f6c9eaea160fe457b8b0db0e8ba44fc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutbound]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbb6e3d252b98b73a11aebbe30c46d4a9ab7912b216885120fc84bc945a9e09d(
    *,
    environment: typing.Optional[builtins.str] = None,
    service: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d7c33e06e1bcb025d36966a39e2097dbe33a93b478162bed0d10088292090d7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db58c9e237e7ac26dd04dd7868493cb3fedd72fa3205c7261faa0c289771cc2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__988013ca1ff7bfec683ba6225cfabf0705196e1c48f738ad2cce6455795f7e5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5ff9184dfd22513186b59342643ff276da9e83329d38fc8b8166d1cc27a807c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindingsOutboundWorker]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8abe1fcb29964aab7ca670c59b5005f7036df8ed903c157a65eec0e55431d86(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63382341de1e7fa8615aa72c2344ce7d3965eb5421bfff71dda529bafa6846bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4081019aa62313bdd8cf57dc21274b151c576f7e6e3ba9637402b0f5e69cbae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce2674a9ef845f1b4d0514022898d6685f9149aff70eea82cf4569f4f074082c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__171abb82a439261c3ce13d209c0f11641138bed2ef749f506bd0cfe164b042f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__216f133658a28fffec8b8074315890a16050657ad4c8f4cb6bf3924cd1f46196(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a7b0dba8d4f8d466bcdf0a4e9f067ac473106f78d543a924cb38db0404cbc32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdb06e399512670a2d580cbc36c116c3ca8e6178d3eba9b59c48627527f52270(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f42e969c9244347ddcfe7ca935247703b634c74112040ac8a4fd5c6736c9d4a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b9c64d1bc37b148355f79ef127a2459aa3c90fc54492106f477481ad8b0d22c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a0a77a9abd8fc609d7d52911eb05e446b979b4e953c40c96052133647ccf0fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7f79a7f9e9d9c4205c1b23c7a449553cce53d17287d7bbf67f2fa98609b6ddc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88b04c2175dffe143951a1088873f24cd95af0ac2e1520399720c7d9ce1c969a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1944e667dbe7823f07e97dad4a9605d32a21ad79e95c3cf011c71908407122da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0684bec5c5b2d4be95ca9cec1e29cb1e8da806b2336571feb38c74340eee20d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f30d2a22c75fb40af5a1de4653bdcd4c038fe345e5db724458eda8c47c6b4280(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3dc919cd7657508a098153277f5aad5856c7379b7ad7f4cbe9caa2f62025ba5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__271d75c8c08afa98bdb7fd1e0eee55bbf3dc546787d98deed83531247a0ff779(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a60948d4107a366dc128bb85fe2c460ef91e4c788c3f2ef14944a00c596c2066(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a56faf6951a41cfa94838dc2b1a956979003d498ee323aefa1d83b557fd69c17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55d2ceadee35483a24912992202283905980d60301a208f2da113f788b2785f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__096c2414b82860e35b50e7ea0d4257be92d420496f9cd2103c054004a5ec99cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ccc6f65628a40313e8756a2a08b50dc06241b5f6c1961d70cc9b7df5823ef04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b6ee2d3901f0dcf6fc01a1669fe28a5e2f2bda1456779b5a58c018483c39b3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4278333132f76ae61d01a7be05f6c2e77d2da95dafdb28b7dd205c65d4ce4825(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f90f2495bcc2175f1a23084db839a34d1fef1c7ecc99b16ff2999a970c3af184(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__886755413e9bcfe0ec2f352164944fd6cfdd9e30aa97e96355b96e285f61bd91(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionBindings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2625646c8d4e832444152af6d90a06ff9807b4aedf0f7121aaca5982f0a61fbc(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    worker_id: builtins.str,
    annotations: typing.Optional[typing.Union[WorkerVersionAnnotations, typing.Dict[builtins.str, typing.Any]]] = None,
    assets: typing.Optional[typing.Union[WorkerVersionAssets, typing.Dict[builtins.str, typing.Any]]] = None,
    bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    compatibility_date: typing.Optional[builtins.str] = None,
    compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    limits: typing.Optional[typing.Union[WorkerVersionLimits, typing.Dict[builtins.str, typing.Any]]] = None,
    main_module: typing.Optional[builtins.str] = None,
    migrations: typing.Optional[typing.Union[WorkerVersionMigrations, typing.Dict[builtins.str, typing.Any]]] = None,
    modules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionModules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    placement: typing.Optional[typing.Union[WorkerVersionPlacement, typing.Dict[builtins.str, typing.Any]]] = None,
    usage_model: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__027385c78410c670f0f619602ea744fca8e7eb89dbfbd6cd1014e74d92a03f51(
    *,
    cpu_ms: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3c7d2a114ae9500b38b41d1c82ce342d08fe1a3413ea0b0900f8e56d952795f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__561633cee3047dc89bc4c98ffd26e8551be9fc796118ee745c029360216f975f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da932a0eee045d5e718a7a341b8ec9237d69fba1d991cf964dd5dcb24b7e39ff(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25627b579f196d73a695bec50f13f8bc1e1388a793d512b42a1be87b5d202fc6(
    *,
    deleted_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_sqlite_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_tag: typing.Optional[builtins.str] = None,
    old_tag: typing.Optional[builtins.str] = None,
    renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsRenamedClasses, typing.Dict[builtins.str, typing.Any]]]]] = None,
    steps: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsSteps, typing.Dict[builtins.str, typing.Any]]]]] = None,
    transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsTransferredClasses, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__980551acf542be24c0dc7541518515f4f2005a35524f4bf7df6d7c78e8ad6046(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e8ddeb78d4cfbc9dd1c738eb706bec44916932904621b7c72fcce29cb13ce28(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsRenamedClasses, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f4a04966d96506218e527611290587346595d69e56a2038d75524d0828378ff(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsSteps, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c71b5fabdd9afd9be99d3b4a0613730ab60931c0d1e0f56e96cf2007a8428053(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsTransferredClasses, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22114303b69d217320c539b87504c57b67400e4e3f81d22af4fc096e2aeb0c7e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2c297ee056bf4e355cc6c3f629c9f7d03116c0e108187e964b0813227245ff8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b72d44e38c71400ceb1871f4acb37dedf268eb878126e4c81bee89cda6abac3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95402ced0e5db7023a986a5463290b9e468fe8e042603c85efbed28eabf539b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cfefcc775a97eb1ab2054e6bb551921d1dc9d23af3e21cafcaf5840267c27a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c7b1009fbee01bee7f92fd80ee30e7fbaf19cb50067038930b8d87ee8866da9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbf980d3d9ae7d1ae11b4d8a01e0dccf98b8394bb5f6f84841f347d4f75a44f0(
    *,
    from_: typing.Optional[builtins.str] = None,
    to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9118d0b9218fc239572e13ab30adc7d77769f2878b516dc0834cbe9e754a9fac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb2e6cd44faf4774616410f6bcc38fe7ecb443431db3ff8f16a1842122bedcb0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c470d27a97faadba93493bf43410171f2193d1efc4e7428f606872efec0b6f03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fd032d2a28035b0dcdf7896c1f2c86c84a40b3993cf9c64a94cd94c1af8b371(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95a66b2a91f9eacdce06582e0d19780de87998fd650395cd2e2daf9491a83934(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f612216c2377fb903c5be683c726ec92a403f19d1bdbfed26e07836102983f2e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsRenamedClasses]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ea59223c112cf1ec82a7095ea56a15e1069d2ff24307f6798495a220b69e1f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19629168a7a336088aa55b422d93cebcb9c2a05053b36b010b05de7f055215b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3993f67bf69368fefa9f2b15237bddedeac15ef629d8e4e86eb10b41af6b9f1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46cd998dcca134ff9cc9bf98b3bd2281f1480015c350f1531005e0792a40cfd4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsRenamedClasses]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d61070208315d0c0951a1fdb637f5850512293ba6b08afcf327cecd28a42bd4f(
    *,
    deleted_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    new_sqlite_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    renamed_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsStepsRenamedClasses, typing.Dict[builtins.str, typing.Any]]]]] = None,
    transferred_classes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsStepsTransferredClasses, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e6c218d3339674cce9df03247803cf49c14ee1c00566da5457f3c7c2d5e6666(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abb9db9dc8c44a38561ec16f6b50836d2779733e09776b31e3bf4b6d6f84a389(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__012cde16ce05a59201a39b95ad7ead36dbf02381e5a3cd84e76d088c8bd55f53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__222e60e526cde50332087c347b4630989b72f559af0e90d806f859c02fa96591(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00eb18c7916418670883b62638feb1e2063499352158120f6903bffefcba7a10(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__860ef875ace4f27945984b4939dddf49e8e84d8548ec9c3e9b6370aa53a5c534(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsSteps]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4f6bf850220cd51918b5e288e14a4d65f979dc80324b3e98617a36275d2600e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b4976072a82a74f505b526d82c07f587e36734111268ba66f2a42fafdb9fde9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsStepsRenamedClasses, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15117d33fad5050ba7a6adb563df889c51592ab7bbede1d49064184052cff30c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkerVersionMigrationsStepsTransferredClasses, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2760f5dd0cb9addd4d27288efc32de8bf84135e31f49acc73e946031d37a8eb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d4f173c5b5c5ba4210bd9dcbd664205e1addab621a7f268e2c8da735238f16c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f838169f012880000254794d5ceacc06129bb1ef6f65966a8d03141575004ce(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00e51d4b22db99ebca062c60688565030ea6fad8657267c1bba73cffb4752301(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsSteps]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc380e7e0007cb58a695d1a802727723b46b5e3bf76a5de8a7c2eb84150167d6(
    *,
    from_: typing.Optional[builtins.str] = None,
    to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__656bd90d203e0753921573f070c7169bd5f86aa3a64c76ac529acf5a658a894b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb2c738cd1bb4677087d30afffcec0032ec57cd3d995d262c3a81a786b0659fc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5849d7badfec625a83a1f3631371216bb76ca8537851ff6d0938113414f56b4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c85d2ca52fe65349ac5f07c350b05d21c6be80ced4721a3ff6528ab1a97f797a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41479cae8f68944df4f0e6264cf018ee13a972a978bf5937bbdfb01fd50e768f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__818c2c9b538fabf2bc0f8939d4eb7dfd119d47f39ee912c4c72e1a9c59c7b4c4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsStepsRenamedClasses]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94af87d3caf1dd736c77c0cdec7f63b1d117105515ac5f1d6b360c8a76487d5f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7dacf9bddc942bc5e52056d79df417050ebb5bd15d6771048ed3a6ae3d34a4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf4d8513f476bde99a4e6b7c24ee9789b9d9db9bf8acd7b704c155c863a109bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__200f39b5a4fbd4e9bd7b8a7dc727c0176f5178b19ea65d5f633fd3da91a255d3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsStepsRenamedClasses]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abf8ecfdc89455567126299a9defb1e2e7aa1584bd8a7b92cb9cac5780e78058(
    *,
    from_: typing.Optional[builtins.str] = None,
    from_script: typing.Optional[builtins.str] = None,
    to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd4988b6f2ff8ac6f4216d8c64ed0f816b530692a6ecae4393678ff826ea66a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eca4327a8846003c24118a42a9a788bdd99d39e0f938408fc52700f4a72a170(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70d2f51f360e8a6d222565ab754915616f9d20c252a1f45b6aa9a661946ba1db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8cd78e26b17d5f96cab8829bee279b639a48b5c17aea9b74b43739889d46399(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93c9bdd54fd9f87b5842e1bb94be1821438999a931105e9c809c84f9c89e26f2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15667fe6f33a3002fdf74d3c9cce6e8b7218443c8263d9eff0bb8e2bd861ebaf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsStepsTransferredClasses]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa642eaa56df13399897920fca99e3cf795e807c0a0528dadb92e798a7ac2871(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__817c72ad78b7f94a363e160600c9ab09054e881e57e452bd3fc82882e4f3d2c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5760f2273071e305b2fbce33769af495f814b60e30f80e2d318113b635d4c63c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e33f1def3daba44c3ddac087f9d817a7076822f98be7c2aaf73e35308c6ada34(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__505d86bffd88d57e42aef2c0c3f42b2d1416ce63778c3a66e4ac1353c931c9b0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsStepsTransferredClasses]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc296b605b1b12071bb121e5cbeab3805a7165b6b780f3e7ce37f78a1d2132e4(
    *,
    from_: typing.Optional[builtins.str] = None,
    from_script: typing.Optional[builtins.str] = None,
    to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__038cea57c3de522bc8a833d0ea8914cf5126b645486b5194bd6b646731baf606(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dfb99d4f054f0fed09887f502d20700ca467f41bc06737ff61acf4bb37dda8f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f120549f229175831d61196d1bc22ad8c06d1dc34e6356e52c83fca789e4e3fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4519684c4860e068d7d9045bc106da70abc12498b3820d19697dec0005c4edb0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ac3d90176f3233668f0dadfedc37d9a744cd5ed8b8826e6bbba158ba5b40a4e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95c25513ee7774a33b5d04e1fb5fca8c3215c0aad3e8588dfcf1ade2b85dd95e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionMigrationsTransferredClasses]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1053b8087c03f5ba9bc6c1047f72219d2a24c0bdb2f5bbc10689a838a0fade66(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bba86575a7068989cdd0c7fe355754aaeeeaee1087a4236ab448448e13807401(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f3162ed4cddb23706e7c95d22f892a35e7ba1061ef4995b3d4b5eb05e9df3b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d130978b0075dcb1a04f3ba622f2b7b69bf06cb2627d648a0c25e3d054a5e36(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2bc854ab6390c717a802a5bd18967e08be030aebd64cd1d49debb19b863fe0d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionMigrationsTransferredClasses]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a36d2f62a3eb360e964dd8f852ca5cae62f9d0132c11f3391594a2ab3d40e76(
    *,
    content_file: builtins.str,
    content_type: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a299a036408b2420958e5f246cb4bb49a7a893924fd610322d9ab59684e24f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__073cbf2e783f854d93573159533241c270e0376adaa6fd7227f86a6e8cf6adcc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e58ef21517ace6ec59fc3c1829e4b609664afcd9053d99d0c4533677fd75a01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6776037f277206f8a7f6a055a499c34f06d42e4a30db78b4a57f5402af88f0b3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__761e84530475b3a7a4b4a14b22a55fde78e826a36f032524cbfb0f5d30a0085c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be03ee53a2907001636be351d7d18c59bec42fa35568afb05675dddbf215ceef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkerVersionModules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__468d3ed1c7fba2de96ca5dfa800144251cad01186378183422b960d4be9b738f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe04ff291adbf6c4d9eaa636bc94f065c359b54dd6af6cd7ca13c90e2232163c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18e8b4a251c76dd12055d17fb8a26f1ec3f5f4c5919988822279d9f9c928ebb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c85822361b99dea3e201f6fddaf636a09fa5bb1cdf33dd8dfeddf698f44a9713(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8694b5e0fa52cd53ba6e52033a4025e9d69fd4a3046d7543be8a262df3e7aa99(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionModules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__785699a973e235aa8df1bcd27b32c89158cf016e294ee36661162f03a417dc45(
    *,
    mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60858a68c3c71b15a7f3feb49ff04e6c6180cfa3c48430236b6d13eaca939aee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b105b6692712ffe9444dc994a10e378d5605be1651a083c6c1c6a1dd4a5b199(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e38af827e03d5cdbb0ae675832edd7b0222c049ce260e6dbf36e58a35ac8050f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkerVersionPlacement]],
) -> None:
    """Type checking stubs"""
    pass
