r'''
# `cloudflare_pages_project`

Refer to the Terraform Registry for docs: [`cloudflare_pages_project`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project).
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


class PagesProject(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProject",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project cloudflare_pages_project}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        name: builtins.str,
        build_config: typing.Optional[typing.Union["PagesProjectBuildConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        deployment_configs: typing.Optional[typing.Union["PagesProjectDeploymentConfigs", typing.Dict[builtins.str, typing.Any]]] = None,
        production_branch: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Union["PagesProjectSource", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project cloudflare_pages_project} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#account_id PagesProject#account_id}
        :param name: Name of the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        :param build_config: Configs for the project build process. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#build_config PagesProject#build_config}
        :param deployment_configs: Configs for deployments in a project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#deployment_configs PagesProject#deployment_configs}
        :param production_branch: Production branch of the project. Used to identify production deployments. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production_branch PagesProject#production_branch}
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#source PagesProject#source}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32c8bd3ba18e0650df846b2d2e37dfef810ae73f984dcc34617f1efd60225d71)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = PagesProjectConfig(
            account_id=account_id,
            name=name,
            build_config=build_config,
            deployment_configs=deployment_configs,
            production_branch=production_branch,
            source=source,
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
        '''Generates CDKTF code for importing a PagesProject resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PagesProject to import.
        :param import_from_id: The id of the existing PagesProject that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PagesProject to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dacbc7e3bfed7ff93406fa665eba6d271e30ed7a3fbcc183f148159745f21a2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putBuildConfig")
    def put_build_config(
        self,
        *,
        build_caching: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        build_command: typing.Optional[builtins.str] = None,
        destination_dir: typing.Optional[builtins.str] = None,
        root_dir: typing.Optional[builtins.str] = None,
        web_analytics_tag: typing.Optional[builtins.str] = None,
        web_analytics_token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param build_caching: Enable build caching for the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#build_caching PagesProject#build_caching}
        :param build_command: Command used to build project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#build_command PagesProject#build_command}
        :param destination_dir: Output directory of the build. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#destination_dir PagesProject#destination_dir}
        :param root_dir: Directory to run the command. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#root_dir PagesProject#root_dir}
        :param web_analytics_tag: The classifying tag for analytics. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#web_analytics_tag PagesProject#web_analytics_tag}
        :param web_analytics_token: The auth token for analytics. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#web_analytics_token PagesProject#web_analytics_token}
        '''
        value = PagesProjectBuildConfig(
            build_caching=build_caching,
            build_command=build_command,
            destination_dir=destination_dir,
            root_dir=root_dir,
            web_analytics_tag=web_analytics_tag,
            web_analytics_token=web_analytics_token,
        )

        return typing.cast(None, jsii.invoke(self, "putBuildConfig", [value]))

    @jsii.member(jsii_name="putDeploymentConfigs")
    def put_deployment_configs(
        self,
        *,
        preview: typing.Optional[typing.Union["PagesProjectDeploymentConfigsPreview", typing.Dict[builtins.str, typing.Any]]] = None,
        production: typing.Optional[typing.Union["PagesProjectDeploymentConfigsProduction", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param preview: Configs for preview deploys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview PagesProject#preview}
        :param production: Configs for production deploys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production PagesProject#production}
        '''
        value = PagesProjectDeploymentConfigs(preview=preview, production=production)

        return typing.cast(None, jsii.invoke(self, "putDeploymentConfigs", [value]))

    @jsii.member(jsii_name="putSource")
    def put_source(
        self,
        *,
        config: typing.Optional[typing.Union["PagesProjectSourceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#config PagesProject#config}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#type PagesProject#type}.
        '''
        value = PagesProjectSource(config=config, type=type)

        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="resetBuildConfig")
    def reset_build_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildConfig", []))

    @jsii.member(jsii_name="resetDeploymentConfigs")
    def reset_deployment_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentConfigs", []))

    @jsii.member(jsii_name="resetProductionBranch")
    def reset_production_branch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProductionBranch", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

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
    @jsii.member(jsii_name="buildConfig")
    def build_config(self) -> "PagesProjectBuildConfigOutputReference":
        return typing.cast("PagesProjectBuildConfigOutputReference", jsii.get(self, "buildConfig"))

    @builtins.property
    @jsii.member(jsii_name="canonicalDeployment")
    def canonical_deployment(self) -> "PagesProjectCanonicalDeploymentOutputReference":
        return typing.cast("PagesProjectCanonicalDeploymentOutputReference", jsii.get(self, "canonicalDeployment"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="deploymentConfigs")
    def deployment_configs(self) -> "PagesProjectDeploymentConfigsOutputReference":
        return typing.cast("PagesProjectDeploymentConfigsOutputReference", jsii.get(self, "deploymentConfigs"))

    @builtins.property
    @jsii.member(jsii_name="domains")
    def domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domains"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="latestDeployment")
    def latest_deployment(self) -> "PagesProjectLatestDeploymentOutputReference":
        return typing.cast("PagesProjectLatestDeploymentOutputReference", jsii.get(self, "latestDeployment"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "PagesProjectSourceOutputReference":
        return typing.cast("PagesProjectSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="subdomain")
    def subdomain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subdomain"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="buildConfigInput")
    def build_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectBuildConfig"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectBuildConfig"]], jsii.get(self, "buildConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentConfigsInput")
    def deployment_configs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigs"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigs"]], jsii.get(self, "deploymentConfigsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="productionBranchInput")
    def production_branch_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "productionBranchInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectSource"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectSource"]], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e25d24d3b5e4450d1d1b773c3f5902e9faec8325dd51fa04efa4d99ffdce1420)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcae619adfa6aa5276e7477d32740b0f98c950ea03e86467e16d2f2afa4af2f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="productionBranch")
    def production_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "productionBranch"))

    @production_branch.setter
    def production_branch(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6748f02b291e15157b0dfdadc8ffde3dfabf3d9c406daafd12d4c241863b058c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "productionBranch", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectBuildConfig",
    jsii_struct_bases=[],
    name_mapping={
        "build_caching": "buildCaching",
        "build_command": "buildCommand",
        "destination_dir": "destinationDir",
        "root_dir": "rootDir",
        "web_analytics_tag": "webAnalyticsTag",
        "web_analytics_token": "webAnalyticsToken",
    },
)
class PagesProjectBuildConfig:
    def __init__(
        self,
        *,
        build_caching: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        build_command: typing.Optional[builtins.str] = None,
        destination_dir: typing.Optional[builtins.str] = None,
        root_dir: typing.Optional[builtins.str] = None,
        web_analytics_tag: typing.Optional[builtins.str] = None,
        web_analytics_token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param build_caching: Enable build caching for the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#build_caching PagesProject#build_caching}
        :param build_command: Command used to build project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#build_command PagesProject#build_command}
        :param destination_dir: Output directory of the build. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#destination_dir PagesProject#destination_dir}
        :param root_dir: Directory to run the command. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#root_dir PagesProject#root_dir}
        :param web_analytics_tag: The classifying tag for analytics. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#web_analytics_tag PagesProject#web_analytics_tag}
        :param web_analytics_token: The auth token for analytics. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#web_analytics_token PagesProject#web_analytics_token}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2ddb1767df2790103b319dd95302c1ef2dcfeee4080c9df13a6923c7f947ef6)
            check_type(argname="argument build_caching", value=build_caching, expected_type=type_hints["build_caching"])
            check_type(argname="argument build_command", value=build_command, expected_type=type_hints["build_command"])
            check_type(argname="argument destination_dir", value=destination_dir, expected_type=type_hints["destination_dir"])
            check_type(argname="argument root_dir", value=root_dir, expected_type=type_hints["root_dir"])
            check_type(argname="argument web_analytics_tag", value=web_analytics_tag, expected_type=type_hints["web_analytics_tag"])
            check_type(argname="argument web_analytics_token", value=web_analytics_token, expected_type=type_hints["web_analytics_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if build_caching is not None:
            self._values["build_caching"] = build_caching
        if build_command is not None:
            self._values["build_command"] = build_command
        if destination_dir is not None:
            self._values["destination_dir"] = destination_dir
        if root_dir is not None:
            self._values["root_dir"] = root_dir
        if web_analytics_tag is not None:
            self._values["web_analytics_tag"] = web_analytics_tag
        if web_analytics_token is not None:
            self._values["web_analytics_token"] = web_analytics_token

    @builtins.property
    def build_caching(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable build caching for the project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#build_caching PagesProject#build_caching}
        '''
        result = self._values.get("build_caching")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def build_command(self) -> typing.Optional[builtins.str]:
        '''Command used to build project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#build_command PagesProject#build_command}
        '''
        result = self._values.get("build_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_dir(self) -> typing.Optional[builtins.str]:
        '''Output directory of the build.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#destination_dir PagesProject#destination_dir}
        '''
        result = self._values.get("destination_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def root_dir(self) -> typing.Optional[builtins.str]:
        '''Directory to run the command.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#root_dir PagesProject#root_dir}
        '''
        result = self._values.get("root_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def web_analytics_tag(self) -> typing.Optional[builtins.str]:
        '''The classifying tag for analytics.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#web_analytics_tag PagesProject#web_analytics_tag}
        '''
        result = self._values.get("web_analytics_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def web_analytics_token(self) -> typing.Optional[builtins.str]:
        '''The auth token for analytics.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#web_analytics_token PagesProject#web_analytics_token}
        '''
        result = self._values.get("web_analytics_token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectBuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectBuildConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectBuildConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a960c98b224c6cf61805a912db83a0d50aa489fd1ddff0a1969c14872ac349d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBuildCaching")
    def reset_build_caching(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildCaching", []))

    @jsii.member(jsii_name="resetBuildCommand")
    def reset_build_command(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildCommand", []))

    @jsii.member(jsii_name="resetDestinationDir")
    def reset_destination_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationDir", []))

    @jsii.member(jsii_name="resetRootDir")
    def reset_root_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootDir", []))

    @jsii.member(jsii_name="resetWebAnalyticsTag")
    def reset_web_analytics_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebAnalyticsTag", []))

    @jsii.member(jsii_name="resetWebAnalyticsToken")
    def reset_web_analytics_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebAnalyticsToken", []))

    @builtins.property
    @jsii.member(jsii_name="buildCachingInput")
    def build_caching_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "buildCachingInput"))

    @builtins.property
    @jsii.member(jsii_name="buildCommandInput")
    def build_command_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buildCommandInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationDirInput")
    def destination_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationDirInput"))

    @builtins.property
    @jsii.member(jsii_name="rootDirInput")
    def root_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rootDirInput"))

    @builtins.property
    @jsii.member(jsii_name="webAnalyticsTagInput")
    def web_analytics_tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webAnalyticsTagInput"))

    @builtins.property
    @jsii.member(jsii_name="webAnalyticsTokenInput")
    def web_analytics_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webAnalyticsTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="buildCaching")
    def build_caching(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "buildCaching"))

    @build_caching.setter
    def build_caching(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78a34e8873fac06a15386e22b65c8a2fe110ba2fbcb68fa0e2079b6dcf081b55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildCaching", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="buildCommand")
    def build_command(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildCommand"))

    @build_command.setter
    def build_command(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd7be84ce85b9c62ce32b5dc2e25735ef178a42ae6c4e9c1119dfd8daf83ded4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildCommand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationDir")
    def destination_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationDir"))

    @destination_dir.setter
    def destination_dir(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5424df13dad2e1fd5edffc5ddcc1e83930ce5a31274ecb5d8574ef5c73362c58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationDir", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rootDir")
    def root_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootDir"))

    @root_dir.setter
    def root_dir(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4625699986a8ee4c0655efa7eeabca037c039abe2c03b7d7bcf3b7602be7d76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rootDir", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="webAnalyticsTag")
    def web_analytics_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webAnalyticsTag"))

    @web_analytics_tag.setter
    def web_analytics_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b3a0913a4c6ccf4b97d8ec54a927ea9f9838b946db5e9009609ac0ce769a21a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webAnalyticsTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="webAnalyticsToken")
    def web_analytics_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webAnalyticsToken"))

    @web_analytics_token.setter
    def web_analytics_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e76185d7b63462d674120a4c7e55a708a813fbeeaeb708206c04147ae22731b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webAnalyticsToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectBuildConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectBuildConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectBuildConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e2551caeefe9277427f352093f8384ff5673336bce649412aec8f7afec41509)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeployment",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectCanonicalDeployment:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectCanonicalDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentBuildConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectCanonicalDeploymentBuildConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectCanonicalDeploymentBuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectCanonicalDeploymentBuildConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentBuildConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fab6fb69a586f514abfc6672e7abdb50b431450a1cb59d4b5c273fb9b303d916)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="buildCaching")
    def build_caching(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "buildCaching"))

    @builtins.property
    @jsii.member(jsii_name="buildCommand")
    def build_command(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildCommand"))

    @builtins.property
    @jsii.member(jsii_name="destinationDir")
    def destination_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationDir"))

    @builtins.property
    @jsii.member(jsii_name="rootDir")
    def root_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootDir"))

    @builtins.property
    @jsii.member(jsii_name="webAnalyticsTag")
    def web_analytics_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webAnalyticsTag"))

    @builtins.property
    @jsii.member(jsii_name="webAnalyticsToken")
    def web_analytics_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webAnalyticsToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectCanonicalDeploymentBuildConfig]:
        return typing.cast(typing.Optional[PagesProjectCanonicalDeploymentBuildConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectCanonicalDeploymentBuildConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b6544be7cdc35b767f75636387bc8ef775f67ee4d042a1a62cea6bf2c12defd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentDeploymentTrigger",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectCanonicalDeploymentDeploymentTrigger:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectCanonicalDeploymentDeploymentTrigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentDeploymentTriggerMetadata",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectCanonicalDeploymentDeploymentTriggerMetadata:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectCanonicalDeploymentDeploymentTriggerMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b279c8df05ed387eb05716851878de7e78a3b8ce85e8419d5e42b398c26d2eaa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="branch")
    def branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branch"))

    @builtins.property
    @jsii.member(jsii_name="commitHash")
    def commit_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commitHash"))

    @builtins.property
    @jsii.member(jsii_name="commitMessage")
    def commit_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commitMessage"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectCanonicalDeploymentDeploymentTriggerMetadata]:
        return typing.cast(typing.Optional[PagesProjectCanonicalDeploymentDeploymentTriggerMetadata], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectCanonicalDeploymentDeploymentTriggerMetadata],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__314b7e3f0a32ecbd526f71824c68b61bb1cda87d0bf22800e917acd8a991b8f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectCanonicalDeploymentDeploymentTriggerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentDeploymentTriggerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb357e9e029f679e3526dcca18296c57f500f9e468c84048e23715c9f2bf1405)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(
        self,
    ) -> PagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference:
        return typing.cast(PagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference, jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectCanonicalDeploymentDeploymentTrigger]:
        return typing.cast(typing.Optional[PagesProjectCanonicalDeploymentDeploymentTrigger], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectCanonicalDeploymentDeploymentTrigger],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dce8ce9a1217d10a7946098e47f11c56f07e86676700420b1f9655d58b6ca7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentEnvVars",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectCanonicalDeploymentEnvVars:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectCanonicalDeploymentEnvVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectCanonicalDeploymentEnvVarsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentEnvVarsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dbb920126cc725c7102ee52d446413ca91cf3574a7d3e0fb6a76b2922a74dec1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectCanonicalDeploymentEnvVarsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bb47cc9773d0a73ead31a3f02d7e748b2a9bda8fb0b94a7cc3e97d8dd40ca6c)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectCanonicalDeploymentEnvVarsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aed9a8e8dba0511ce3e733ae21581d11ba999088b3e9c17fd596c2a6fd44546b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__29eb05adbf32944bbb6d0aba00c4570fcee1e2f3e262754248077dff428e646b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class PagesProjectCanonicalDeploymentEnvVarsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentEnvVarsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__501854349c1906b7982335bb299a7f4812a0869f6ea625be339d44c088c7778e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PagesProjectCanonicalDeploymentEnvVars]:
        return typing.cast(typing.Optional[PagesProjectCanonicalDeploymentEnvVars], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectCanonicalDeploymentEnvVars],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08d822ca4a00abac12c6f3cde6f521d6e0356c45272f076497de130558cd0488)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentLatestStage",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectCanonicalDeploymentLatestStage:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectCanonicalDeploymentLatestStage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectCanonicalDeploymentLatestStageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentLatestStageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__25a774369c7f1e6f663dd126fbf9a5723bc2803e04d50b6668172fef2a36abc2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="endedOn")
    def ended_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endedOn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="startedOn")
    def started_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startedOn"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectCanonicalDeploymentLatestStage]:
        return typing.cast(typing.Optional[PagesProjectCanonicalDeploymentLatestStage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectCanonicalDeploymentLatestStage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__563792ff5844edac35512cc5333a246564f688edd47b20ca3d2fbf0a35ca4a3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectCanonicalDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf3fe4d6f664c28e7546705dfb53608a637c0d3378c96b493a52061993f259df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "aliases"))

    @builtins.property
    @jsii.member(jsii_name="buildConfig")
    def build_config(self) -> PagesProjectCanonicalDeploymentBuildConfigOutputReference:
        return typing.cast(PagesProjectCanonicalDeploymentBuildConfigOutputReference, jsii.get(self, "buildConfig"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="deploymentTrigger")
    def deployment_trigger(
        self,
    ) -> PagesProjectCanonicalDeploymentDeploymentTriggerOutputReference:
        return typing.cast(PagesProjectCanonicalDeploymentDeploymentTriggerOutputReference, jsii.get(self, "deploymentTrigger"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @builtins.property
    @jsii.member(jsii_name="envVars")
    def env_vars(self) -> PagesProjectCanonicalDeploymentEnvVarsMap:
        return typing.cast(PagesProjectCanonicalDeploymentEnvVarsMap, jsii.get(self, "envVars"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="isSkipped")
    def is_skipped(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "isSkipped"))

    @builtins.property
    @jsii.member(jsii_name="latestStage")
    def latest_stage(self) -> PagesProjectCanonicalDeploymentLatestStageOutputReference:
        return typing.cast(PagesProjectCanonicalDeploymentLatestStageOutputReference, jsii.get(self, "latestStage"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @builtins.property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectName"))

    @builtins.property
    @jsii.member(jsii_name="shortId")
    def short_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shortId"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "PagesProjectCanonicalDeploymentSourceOutputReference":
        return typing.cast("PagesProjectCanonicalDeploymentSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> "PagesProjectCanonicalDeploymentStagesList":
        return typing.cast("PagesProjectCanonicalDeploymentStagesList", jsii.get(self, "stages"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PagesProjectCanonicalDeployment]:
        return typing.cast(typing.Optional[PagesProjectCanonicalDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectCanonicalDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41aa1031f49109411801d151b4bf6c3ffda14f2cc861bfcc27da774edebb771a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentSource",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectCanonicalDeploymentSource:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectCanonicalDeploymentSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentSourceConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectCanonicalDeploymentSourceConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectCanonicalDeploymentSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectCanonicalDeploymentSourceConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentSourceConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba84a37a6cd59ce90562c2b9c9c9f27f6f68c850f60d538fbe58029f54312b6a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="deploymentsEnabled")
    def deployments_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "deploymentsEnabled"))

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property
    @jsii.member(jsii_name="pathExcludes")
    def path_excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pathExcludes"))

    @builtins.property
    @jsii.member(jsii_name="pathIncludes")
    def path_includes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pathIncludes"))

    @builtins.property
    @jsii.member(jsii_name="prCommentsEnabled")
    def pr_comments_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "prCommentsEnabled"))

    @builtins.property
    @jsii.member(jsii_name="previewBranchExcludes")
    def preview_branch_excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "previewBranchExcludes"))

    @builtins.property
    @jsii.member(jsii_name="previewBranchIncludes")
    def preview_branch_includes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "previewBranchIncludes"))

    @builtins.property
    @jsii.member(jsii_name="previewDeploymentSetting")
    def preview_deployment_setting(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "previewDeploymentSetting"))

    @builtins.property
    @jsii.member(jsii_name="productionBranch")
    def production_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "productionBranch"))

    @builtins.property
    @jsii.member(jsii_name="productionDeploymentsEnabled")
    def production_deployments_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "productionDeploymentsEnabled"))

    @builtins.property
    @jsii.member(jsii_name="repoName")
    def repo_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectCanonicalDeploymentSourceConfig]:
        return typing.cast(typing.Optional[PagesProjectCanonicalDeploymentSourceConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectCanonicalDeploymentSourceConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab5cafd6cf45359135425a491f331e24bee341f61d8d66ebe93faad7a8265f62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectCanonicalDeploymentSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__28d5251f27d36526665548ca74b9ba0465b443fcbe959a1d2fc74dbc08a9d812)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> PagesProjectCanonicalDeploymentSourceConfigOutputReference:
        return typing.cast(PagesProjectCanonicalDeploymentSourceConfigOutputReference, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PagesProjectCanonicalDeploymentSource]:
        return typing.cast(typing.Optional[PagesProjectCanonicalDeploymentSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectCanonicalDeploymentSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0190d8358654d7451047fa6dc8144c09de7e1a626ae3993beae4be619f8d1dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentStages",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectCanonicalDeploymentStages:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectCanonicalDeploymentStages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectCanonicalDeploymentStagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentStagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9784a4c312ac28de6d1c63d63e04e5b734f56bdd8412609b58d912baaa2fe51)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "PagesProjectCanonicalDeploymentStagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbc8efbf48f82016669a367554d9b6f734ed3d3d04f755365d1dbb36619a4924)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PagesProjectCanonicalDeploymentStagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6955d640b54dbfed37ce66817e96f64a3d04008b473c4662a39e8732c9c27bd6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c04edebc76cd1d2c3ee3c6dd3d167c1ab84a73d48a614aac760808366d89a15)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0021535833e3759c981cd8644e56d3443d568f0fd1c5ecfe16d018a31602987a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class PagesProjectCanonicalDeploymentStagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectCanonicalDeploymentStagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdc9fccdffcd6ee7d9d16c50fb135dfc410f6e40163229f1f7e0f17a12572156)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="endedOn")
    def ended_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endedOn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="startedOn")
    def started_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startedOn"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PagesProjectCanonicalDeploymentStages]:
        return typing.cast(typing.Optional[PagesProjectCanonicalDeploymentStages], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectCanonicalDeploymentStages],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4a71ca73107bcd82c0c34f81799ac40e3f3a094a3ccf11625f0082eae044715)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectConfig",
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
        "build_config": "buildConfig",
        "deployment_configs": "deploymentConfigs",
        "production_branch": "productionBranch",
        "source": "source",
    },
)
class PagesProjectConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        build_config: typing.Optional[typing.Union[PagesProjectBuildConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        deployment_configs: typing.Optional[typing.Union["PagesProjectDeploymentConfigs", typing.Dict[builtins.str, typing.Any]]] = None,
        production_branch: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Union["PagesProjectSource", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#account_id PagesProject#account_id}
        :param name: Name of the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        :param build_config: Configs for the project build process. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#build_config PagesProject#build_config}
        :param deployment_configs: Configs for deployments in a project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#deployment_configs PagesProject#deployment_configs}
        :param production_branch: Production branch of the project. Used to identify production deployments. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production_branch PagesProject#production_branch}
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#source PagesProject#source}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(build_config, dict):
            build_config = PagesProjectBuildConfig(**build_config)
        if isinstance(deployment_configs, dict):
            deployment_configs = PagesProjectDeploymentConfigs(**deployment_configs)
        if isinstance(source, dict):
            source = PagesProjectSource(**source)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0094d200e654f606607f96b58892accd8ce9d503242b6f5c7d06a2ae11897e53)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument build_config", value=build_config, expected_type=type_hints["build_config"])
            check_type(argname="argument deployment_configs", value=deployment_configs, expected_type=type_hints["deployment_configs"])
            check_type(argname="argument production_branch", value=production_branch, expected_type=type_hints["production_branch"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
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
        if build_config is not None:
            self._values["build_config"] = build_config
        if deployment_configs is not None:
            self._values["deployment_configs"] = deployment_configs
        if production_branch is not None:
            self._values["production_branch"] = production_branch
        if source is not None:
            self._values["source"] = source

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#account_id PagesProject#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_config(self) -> typing.Optional[PagesProjectBuildConfig]:
        '''Configs for the project build process.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#build_config PagesProject#build_config}
        '''
        result = self._values.get("build_config")
        return typing.cast(typing.Optional[PagesProjectBuildConfig], result)

    @builtins.property
    def deployment_configs(self) -> typing.Optional["PagesProjectDeploymentConfigs"]:
        '''Configs for deployments in a project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#deployment_configs PagesProject#deployment_configs}
        '''
        result = self._values.get("deployment_configs")
        return typing.cast(typing.Optional["PagesProjectDeploymentConfigs"], result)

    @builtins.property
    def production_branch(self) -> typing.Optional[builtins.str]:
        '''Production branch of the project. Used to identify production deployments.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production_branch PagesProject#production_branch}
        '''
        result = self._values.get("production_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional["PagesProjectSource"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#source PagesProject#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional["PagesProjectSource"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigs",
    jsii_struct_bases=[],
    name_mapping={"preview": "preview", "production": "production"},
)
class PagesProjectDeploymentConfigs:
    def __init__(
        self,
        *,
        preview: typing.Optional[typing.Union["PagesProjectDeploymentConfigsPreview", typing.Dict[builtins.str, typing.Any]]] = None,
        production: typing.Optional[typing.Union["PagesProjectDeploymentConfigsProduction", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param preview: Configs for preview deploys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview PagesProject#preview}
        :param production: Configs for production deploys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production PagesProject#production}
        '''
        if isinstance(preview, dict):
            preview = PagesProjectDeploymentConfigsPreview(**preview)
        if isinstance(production, dict):
            production = PagesProjectDeploymentConfigsProduction(**production)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7823fdc9b0a09eac3b8f24725ee9162c17ddca7ff78a36cba5175fe819813991)
            check_type(argname="argument preview", value=preview, expected_type=type_hints["preview"])
            check_type(argname="argument production", value=production, expected_type=type_hints["production"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if preview is not None:
            self._values["preview"] = preview
        if production is not None:
            self._values["production"] = production

    @builtins.property
    def preview(self) -> typing.Optional["PagesProjectDeploymentConfigsPreview"]:
        '''Configs for preview deploys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview PagesProject#preview}
        '''
        result = self._values.get("preview")
        return typing.cast(typing.Optional["PagesProjectDeploymentConfigsPreview"], result)

    @builtins.property
    def production(self) -> typing.Optional["PagesProjectDeploymentConfigsProduction"]:
        '''Configs for production deploys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production PagesProject#production}
        '''
        result = self._values.get("production")
        return typing.cast(typing.Optional["PagesProjectDeploymentConfigsProduction"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9bfb360ea6a026f85cc04fa09830e4f97ca1f925ad9c49edc82b2bf67135a9d1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPreview")
    def put_preview(
        self,
        *,
        ai_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewAiBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        analytics_engine_datasets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        browsers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewBrowsers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        compatibility_date: typing.Optional[builtins.str] = None,
        compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        d1_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewD1Databases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        durable_object_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        env_vars: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewEnvVars", typing.Dict[builtins.str, typing.Any]]]]] = None,
        hyperdrive_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewHyperdriveBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        kv_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewKvNamespaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        mtls_certificates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewMtlsCertificates", typing.Dict[builtins.str, typing.Any]]]]] = None,
        placement: typing.Optional[typing.Union["PagesProjectDeploymentConfigsPreviewPlacement", typing.Dict[builtins.str, typing.Any]]] = None,
        queue_producers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewQueueProducers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        r2_buckets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewR2Buckets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewServices", typing.Dict[builtins.str, typing.Any]]]]] = None,
        vectorize_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewVectorizeBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param ai_bindings: Constellation bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#ai_bindings PagesProject#ai_bindings}
        :param analytics_engine_datasets: Analytics Engine bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#analytics_engine_datasets PagesProject#analytics_engine_datasets}
        :param browsers: Browser bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#browsers PagesProject#browsers}
        :param compatibility_date: Compatibility date used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_date PagesProject#compatibility_date}
        :param compatibility_flags: Compatibility flags used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_flags PagesProject#compatibility_flags}
        :param d1_databases: D1 databases used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#d1_databases PagesProject#d1_databases}
        :param durable_object_namespaces: Durable Object namespaces used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#durable_object_namespaces PagesProject#durable_object_namespaces}
        :param env_vars: Environment variables used for builds and Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#env_vars PagesProject#env_vars}
        :param hyperdrive_bindings: Hyperdrive bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#hyperdrive_bindings PagesProject#hyperdrive_bindings}
        :param kv_namespaces: KV namespaces used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#kv_namespaces PagesProject#kv_namespaces}
        :param mtls_certificates: mTLS bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mtls_certificates PagesProject#mtls_certificates}
        :param placement: Placement setting used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#placement PagesProject#placement}
        :param queue_producers: Queue Producer bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#queue_producers PagesProject#queue_producers}
        :param r2_buckets: R2 buckets used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#r2_buckets PagesProject#r2_buckets}
        :param services: Services used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#services PagesProject#services}
        :param vectorize_bindings: Vectorize bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#vectorize_bindings PagesProject#vectorize_bindings}
        '''
        value = PagesProjectDeploymentConfigsPreview(
            ai_bindings=ai_bindings,
            analytics_engine_datasets=analytics_engine_datasets,
            browsers=browsers,
            compatibility_date=compatibility_date,
            compatibility_flags=compatibility_flags,
            d1_databases=d1_databases,
            durable_object_namespaces=durable_object_namespaces,
            env_vars=env_vars,
            hyperdrive_bindings=hyperdrive_bindings,
            kv_namespaces=kv_namespaces,
            mtls_certificates=mtls_certificates,
            placement=placement,
            queue_producers=queue_producers,
            r2_buckets=r2_buckets,
            services=services,
            vectorize_bindings=vectorize_bindings,
        )

        return typing.cast(None, jsii.invoke(self, "putPreview", [value]))

    @jsii.member(jsii_name="putProduction")
    def put_production(
        self,
        *,
        ai_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionAiBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        analytics_engine_datasets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        browsers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionBrowsers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        compatibility_date: typing.Optional[builtins.str] = None,
        compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        d1_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionD1Databases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        durable_object_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionDurableObjectNamespaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        env_vars: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionEnvVars", typing.Dict[builtins.str, typing.Any]]]]] = None,
        hyperdrive_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionHyperdriveBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        kv_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionKvNamespaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        mtls_certificates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionMtlsCertificates", typing.Dict[builtins.str, typing.Any]]]]] = None,
        placement: typing.Optional[typing.Union["PagesProjectDeploymentConfigsProductionPlacement", typing.Dict[builtins.str, typing.Any]]] = None,
        queue_producers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionQueueProducers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        r2_buckets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionR2Buckets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionServices", typing.Dict[builtins.str, typing.Any]]]]] = None,
        vectorize_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionVectorizeBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param ai_bindings: Constellation bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#ai_bindings PagesProject#ai_bindings}
        :param analytics_engine_datasets: Analytics Engine bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#analytics_engine_datasets PagesProject#analytics_engine_datasets}
        :param browsers: Browser bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#browsers PagesProject#browsers}
        :param compatibility_date: Compatibility date used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_date PagesProject#compatibility_date}
        :param compatibility_flags: Compatibility flags used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_flags PagesProject#compatibility_flags}
        :param d1_databases: D1 databases used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#d1_databases PagesProject#d1_databases}
        :param durable_object_namespaces: Durable Object namespaces used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#durable_object_namespaces PagesProject#durable_object_namespaces}
        :param env_vars: Environment variables used for builds and Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#env_vars PagesProject#env_vars}
        :param hyperdrive_bindings: Hyperdrive bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#hyperdrive_bindings PagesProject#hyperdrive_bindings}
        :param kv_namespaces: KV namespaces used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#kv_namespaces PagesProject#kv_namespaces}
        :param mtls_certificates: mTLS bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mtls_certificates PagesProject#mtls_certificates}
        :param placement: Placement setting used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#placement PagesProject#placement}
        :param queue_producers: Queue Producer bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#queue_producers PagesProject#queue_producers}
        :param r2_buckets: R2 buckets used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#r2_buckets PagesProject#r2_buckets}
        :param services: Services used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#services PagesProject#services}
        :param vectorize_bindings: Vectorize bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#vectorize_bindings PagesProject#vectorize_bindings}
        '''
        value = PagesProjectDeploymentConfigsProduction(
            ai_bindings=ai_bindings,
            analytics_engine_datasets=analytics_engine_datasets,
            browsers=browsers,
            compatibility_date=compatibility_date,
            compatibility_flags=compatibility_flags,
            d1_databases=d1_databases,
            durable_object_namespaces=durable_object_namespaces,
            env_vars=env_vars,
            hyperdrive_bindings=hyperdrive_bindings,
            kv_namespaces=kv_namespaces,
            mtls_certificates=mtls_certificates,
            placement=placement,
            queue_producers=queue_producers,
            r2_buckets=r2_buckets,
            services=services,
            vectorize_bindings=vectorize_bindings,
        )

        return typing.cast(None, jsii.invoke(self, "putProduction", [value]))

    @jsii.member(jsii_name="resetPreview")
    def reset_preview(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreview", []))

    @jsii.member(jsii_name="resetProduction")
    def reset_production(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProduction", []))

    @builtins.property
    @jsii.member(jsii_name="preview")
    def preview(self) -> "PagesProjectDeploymentConfigsPreviewOutputReference":
        return typing.cast("PagesProjectDeploymentConfigsPreviewOutputReference", jsii.get(self, "preview"))

    @builtins.property
    @jsii.member(jsii_name="production")
    def production(self) -> "PagesProjectDeploymentConfigsProductionOutputReference":
        return typing.cast("PagesProjectDeploymentConfigsProductionOutputReference", jsii.get(self, "production"))

    @builtins.property
    @jsii.member(jsii_name="previewInput")
    def preview_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigsPreview"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigsPreview"]], jsii.get(self, "previewInput"))

    @builtins.property
    @jsii.member(jsii_name="productionInput")
    def production_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigsProduction"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigsProduction"]], jsii.get(self, "productionInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bda509eaf75eb329c80e5e350ce8997a151563c736cfdcf50a669a795ffaa07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreview",
    jsii_struct_bases=[],
    name_mapping={
        "ai_bindings": "aiBindings",
        "analytics_engine_datasets": "analyticsEngineDatasets",
        "browsers": "browsers",
        "compatibility_date": "compatibilityDate",
        "compatibility_flags": "compatibilityFlags",
        "d1_databases": "d1Databases",
        "durable_object_namespaces": "durableObjectNamespaces",
        "env_vars": "envVars",
        "hyperdrive_bindings": "hyperdriveBindings",
        "kv_namespaces": "kvNamespaces",
        "mtls_certificates": "mtlsCertificates",
        "placement": "placement",
        "queue_producers": "queueProducers",
        "r2_buckets": "r2Buckets",
        "services": "services",
        "vectorize_bindings": "vectorizeBindings",
    },
)
class PagesProjectDeploymentConfigsPreview:
    def __init__(
        self,
        *,
        ai_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewAiBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        analytics_engine_datasets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        browsers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewBrowsers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        compatibility_date: typing.Optional[builtins.str] = None,
        compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        d1_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewD1Databases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        durable_object_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        env_vars: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewEnvVars", typing.Dict[builtins.str, typing.Any]]]]] = None,
        hyperdrive_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewHyperdriveBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        kv_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewKvNamespaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        mtls_certificates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewMtlsCertificates", typing.Dict[builtins.str, typing.Any]]]]] = None,
        placement: typing.Optional[typing.Union["PagesProjectDeploymentConfigsPreviewPlacement", typing.Dict[builtins.str, typing.Any]]] = None,
        queue_producers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewQueueProducers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        r2_buckets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewR2Buckets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewServices", typing.Dict[builtins.str, typing.Any]]]]] = None,
        vectorize_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewVectorizeBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param ai_bindings: Constellation bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#ai_bindings PagesProject#ai_bindings}
        :param analytics_engine_datasets: Analytics Engine bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#analytics_engine_datasets PagesProject#analytics_engine_datasets}
        :param browsers: Browser bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#browsers PagesProject#browsers}
        :param compatibility_date: Compatibility date used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_date PagesProject#compatibility_date}
        :param compatibility_flags: Compatibility flags used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_flags PagesProject#compatibility_flags}
        :param d1_databases: D1 databases used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#d1_databases PagesProject#d1_databases}
        :param durable_object_namespaces: Durable Object namespaces used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#durable_object_namespaces PagesProject#durable_object_namespaces}
        :param env_vars: Environment variables used for builds and Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#env_vars PagesProject#env_vars}
        :param hyperdrive_bindings: Hyperdrive bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#hyperdrive_bindings PagesProject#hyperdrive_bindings}
        :param kv_namespaces: KV namespaces used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#kv_namespaces PagesProject#kv_namespaces}
        :param mtls_certificates: mTLS bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mtls_certificates PagesProject#mtls_certificates}
        :param placement: Placement setting used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#placement PagesProject#placement}
        :param queue_producers: Queue Producer bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#queue_producers PagesProject#queue_producers}
        :param r2_buckets: R2 buckets used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#r2_buckets PagesProject#r2_buckets}
        :param services: Services used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#services PagesProject#services}
        :param vectorize_bindings: Vectorize bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#vectorize_bindings PagesProject#vectorize_bindings}
        '''
        if isinstance(placement, dict):
            placement = PagesProjectDeploymentConfigsPreviewPlacement(**placement)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74e03862ac074ef15f724d9cc40bca42af7e9390d107765128d30dfa4a96e2ff)
            check_type(argname="argument ai_bindings", value=ai_bindings, expected_type=type_hints["ai_bindings"])
            check_type(argname="argument analytics_engine_datasets", value=analytics_engine_datasets, expected_type=type_hints["analytics_engine_datasets"])
            check_type(argname="argument browsers", value=browsers, expected_type=type_hints["browsers"])
            check_type(argname="argument compatibility_date", value=compatibility_date, expected_type=type_hints["compatibility_date"])
            check_type(argname="argument compatibility_flags", value=compatibility_flags, expected_type=type_hints["compatibility_flags"])
            check_type(argname="argument d1_databases", value=d1_databases, expected_type=type_hints["d1_databases"])
            check_type(argname="argument durable_object_namespaces", value=durable_object_namespaces, expected_type=type_hints["durable_object_namespaces"])
            check_type(argname="argument env_vars", value=env_vars, expected_type=type_hints["env_vars"])
            check_type(argname="argument hyperdrive_bindings", value=hyperdrive_bindings, expected_type=type_hints["hyperdrive_bindings"])
            check_type(argname="argument kv_namespaces", value=kv_namespaces, expected_type=type_hints["kv_namespaces"])
            check_type(argname="argument mtls_certificates", value=mtls_certificates, expected_type=type_hints["mtls_certificates"])
            check_type(argname="argument placement", value=placement, expected_type=type_hints["placement"])
            check_type(argname="argument queue_producers", value=queue_producers, expected_type=type_hints["queue_producers"])
            check_type(argname="argument r2_buckets", value=r2_buckets, expected_type=type_hints["r2_buckets"])
            check_type(argname="argument services", value=services, expected_type=type_hints["services"])
            check_type(argname="argument vectorize_bindings", value=vectorize_bindings, expected_type=type_hints["vectorize_bindings"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ai_bindings is not None:
            self._values["ai_bindings"] = ai_bindings
        if analytics_engine_datasets is not None:
            self._values["analytics_engine_datasets"] = analytics_engine_datasets
        if browsers is not None:
            self._values["browsers"] = browsers
        if compatibility_date is not None:
            self._values["compatibility_date"] = compatibility_date
        if compatibility_flags is not None:
            self._values["compatibility_flags"] = compatibility_flags
        if d1_databases is not None:
            self._values["d1_databases"] = d1_databases
        if durable_object_namespaces is not None:
            self._values["durable_object_namespaces"] = durable_object_namespaces
        if env_vars is not None:
            self._values["env_vars"] = env_vars
        if hyperdrive_bindings is not None:
            self._values["hyperdrive_bindings"] = hyperdrive_bindings
        if kv_namespaces is not None:
            self._values["kv_namespaces"] = kv_namespaces
        if mtls_certificates is not None:
            self._values["mtls_certificates"] = mtls_certificates
        if placement is not None:
            self._values["placement"] = placement
        if queue_producers is not None:
            self._values["queue_producers"] = queue_producers
        if r2_buckets is not None:
            self._values["r2_buckets"] = r2_buckets
        if services is not None:
            self._values["services"] = services
        if vectorize_bindings is not None:
            self._values["vectorize_bindings"] = vectorize_bindings

    @builtins.property
    def ai_bindings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewAiBindings"]]]:
        '''Constellation bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#ai_bindings PagesProject#ai_bindings}
        '''
        result = self._values.get("ai_bindings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewAiBindings"]]], result)

    @builtins.property
    def analytics_engine_datasets(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets"]]]:
        '''Analytics Engine bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#analytics_engine_datasets PagesProject#analytics_engine_datasets}
        '''
        result = self._values.get("analytics_engine_datasets")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets"]]], result)

    @builtins.property
    def browsers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewBrowsers"]]]:
        '''Browser bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#browsers PagesProject#browsers}
        '''
        result = self._values.get("browsers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewBrowsers"]]], result)

    @builtins.property
    def compatibility_date(self) -> typing.Optional[builtins.str]:
        '''Compatibility date used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_date PagesProject#compatibility_date}
        '''
        result = self._values.get("compatibility_date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compatibility_flags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Compatibility flags used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_flags PagesProject#compatibility_flags}
        '''
        result = self._values.get("compatibility_flags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def d1_databases(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewD1Databases"]]]:
        '''D1 databases used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#d1_databases PagesProject#d1_databases}
        '''
        result = self._values.get("d1_databases")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewD1Databases"]]], result)

    @builtins.property
    def durable_object_namespaces(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces"]]]:
        '''Durable Object namespaces used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#durable_object_namespaces PagesProject#durable_object_namespaces}
        '''
        result = self._values.get("durable_object_namespaces")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces"]]], result)

    @builtins.property
    def env_vars(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewEnvVars"]]]:
        '''Environment variables used for builds and Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#env_vars PagesProject#env_vars}
        '''
        result = self._values.get("env_vars")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewEnvVars"]]], result)

    @builtins.property
    def hyperdrive_bindings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewHyperdriveBindings"]]]:
        '''Hyperdrive bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#hyperdrive_bindings PagesProject#hyperdrive_bindings}
        '''
        result = self._values.get("hyperdrive_bindings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewHyperdriveBindings"]]], result)

    @builtins.property
    def kv_namespaces(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewKvNamespaces"]]]:
        '''KV namespaces used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#kv_namespaces PagesProject#kv_namespaces}
        '''
        result = self._values.get("kv_namespaces")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewKvNamespaces"]]], result)

    @builtins.property
    def mtls_certificates(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewMtlsCertificates"]]]:
        '''mTLS bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mtls_certificates PagesProject#mtls_certificates}
        '''
        result = self._values.get("mtls_certificates")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewMtlsCertificates"]]], result)

    @builtins.property
    def placement(
        self,
    ) -> typing.Optional["PagesProjectDeploymentConfigsPreviewPlacement"]:
        '''Placement setting used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#placement PagesProject#placement}
        '''
        result = self._values.get("placement")
        return typing.cast(typing.Optional["PagesProjectDeploymentConfigsPreviewPlacement"], result)

    @builtins.property
    def queue_producers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewQueueProducers"]]]:
        '''Queue Producer bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#queue_producers PagesProject#queue_producers}
        '''
        result = self._values.get("queue_producers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewQueueProducers"]]], result)

    @builtins.property
    def r2_buckets(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewR2Buckets"]]]:
        '''R2 buckets used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#r2_buckets PagesProject#r2_buckets}
        '''
        result = self._values.get("r2_buckets")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewR2Buckets"]]], result)

    @builtins.property
    def services(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewServices"]]]:
        '''Services used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#services PagesProject#services}
        '''
        result = self._values.get("services")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewServices"]]], result)

    @builtins.property
    def vectorize_bindings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewVectorizeBindings"]]]:
        '''Vectorize bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#vectorize_bindings PagesProject#vectorize_bindings}
        '''
        result = self._values.get("vectorize_bindings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewVectorizeBindings"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreview(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewAiBindings",
    jsii_struct_bases=[],
    name_mapping={"project_id": "projectId"},
)
class PagesProjectDeploymentConfigsPreviewAiBindings:
    def __init__(self, *, project_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#project_id PagesProject#project_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4e7080c58251d0cc4979dc0fd9658db010c20ab8db857bc75a43da58fb29152)
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if project_id is not None:
            self._values["project_id"] = project_id

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#project_id PagesProject#project_id}.'''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewAiBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewAiBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewAiBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6447a23135c261e551f5b40eb414278fae80e4948bdd10d121fc4ca7c8b3dd1c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewAiBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__817c94370882ca531583c09348b11c7152c6d7c14c822763a18d6120d0533a7a)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewAiBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e244bc0bef2bcd30e37800f00bfc1d1084e33a3e2e4623d3e7495d9b6153ff55)
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
            type_hints = typing.get_type_hints(_typecheckingstub__66e243a53146ba5c0dfef90e05889f3823d62f9b532ca49d967b5122aa0b548b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAiBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAiBindings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAiBindings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__044d4ae2475c0e8b69637c1e7f40f48ffafa209d2577ec121a5737135a93f087)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewAiBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewAiBindingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b64b2ec1611270b71532d4325de2c7ee0977695540a14a78bec003d9a692f530)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__254a42f33889a14c98ab220820fe0d6197ed647ef7d51f7d16c64c961d34d334)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewAiBindings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewAiBindings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewAiBindings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1b8439899d3dd507d605ef164b005887b71e84c1359ed7e8bc9146e31296808)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets",
    jsii_struct_bases=[],
    name_mapping={"dataset": "dataset"},
)
class PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets:
    def __init__(self, *, dataset: typing.Optional[builtins.str] = None) -> None:
        '''
        :param dataset: Name of the dataset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#dataset PagesProject#dataset}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bc092bac2c921f626ec8ad3b11190ba67135434d86e6ea53b5044cf8d4883d9)
            check_type(argname="argument dataset", value=dataset, expected_type=type_hints["dataset"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dataset is not None:
            self._values["dataset"] = dataset

    @builtins.property
    def dataset(self) -> typing.Optional[builtins.str]:
        '''Name of the dataset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#dataset PagesProject#dataset}
        '''
        result = self._values.get("dataset")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__464d9fd64d7fd499bcc369dca55469e9c6b338bcbfde6dd73422b9089baf7234)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cce5fdef506322fc6ece6b9260eb738ac2c5da7827dc9bf29dcf52639c50cc9e)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__260eda28f8043f6f4d42c8c1fb1f4f187694fcb3e39e577dbfd968dc10fbfc3e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d0e1e10cb7092dba15007c9412700dcc88e55e1dab6a6316c0a77359aad130b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd65de245433737b67d081eb86e87987b4604448bcddca89e60ff5dd020475dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc4f4aa6ef83343154074d5f969581ae140eccc97308c9a122d285350efacc40)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetDataset")
    def reset_dataset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataset", []))

    @builtins.property
    @jsii.member(jsii_name="datasetInput")
    def dataset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datasetInput"))

    @builtins.property
    @jsii.member(jsii_name="dataset")
    def dataset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataset"))

    @dataset.setter
    def dataset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__beb463f861239c66e3308b78f58cac00cc3acae12477ec567fdd3b27a6f533c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6987ae207b90baf03ffa6e1c780e391ed6d04d21d1f2f8d4c64be9a06d9e36d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewBrowsers",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectDeploymentConfigsPreviewBrowsers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewBrowsers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewBrowsersMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewBrowsersMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed71074bab39997d3870877a088e000ac3b746c7e2332c2409e0ac8c79794c83)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewBrowsersOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dd9443e085fc681d1834be46f2943158181767761cf50584ebacacf595cfd66)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewBrowsersOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91f8313b78c6665ae9483bc9353ce7debed25761c3b3b71fec6e7f89b8613445)
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
            type_hints = typing.get_type_hints(_typecheckingstub__768b7280ecae4f7894069975d5f8affe11a9726d3989e8c9cd309238cab50daf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewBrowsers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewBrowsers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewBrowsers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efc1379215b0d512bdfd7fedd2e0840ee79bba7c599a87cec7c4e18bffb071f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewBrowsersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewBrowsersOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18873b1894809d293986afe55ec8413a0e927554c0c425347f2719fdb36ee529)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewBrowsers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewBrowsers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewBrowsers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efb6ba55c1e150bda4aeeb4399dcacdda30c7a4ba17ab4230854e03fd32092f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewD1Databases",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class PagesProjectDeploymentConfigsPreviewD1Databases:
    def __init__(self, *, id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param id: UUID of the D1 database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#id PagesProject#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63acaff423ee97600848c94bd9a53d20556f3f5aaf9da1cdd5165ca8da07bf3b)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''UUID of the D1 database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#id PagesProject#id}

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
        return "PagesProjectDeploymentConfigsPreviewD1Databases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewD1DatabasesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewD1DatabasesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__06df61a96aeb7ad876110b0c3624ec5bcd14486f64792cc7d50254bac34bb0ea)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fa97d138549b90a12eb12d9bec7a9b3167b3a60339114c62a20e08ec71ab9a1)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__284a8c6fc1d0508d3e44901fc07e5749e7b15fe63a686c18444c02b4fb2ce4fc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8d6818fe4827e3131e56c99a720b4e073757f8c7888e22247df7481dda19d45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewD1Databases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewD1Databases]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewD1Databases]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1169209129547ef9bf96247c6ca572c04f7cdb13a9254aa57802b257fca21ac8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c969cf784235d26042fc458f98954f6af0fe030d0645c001959ae778fa29cc8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

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
            type_hints = typing.get_type_hints(_typecheckingstub__80f350896a5b258072e77244466da4b30ea02083b1b962022b0b4909b04dd55e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewD1Databases]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewD1Databases]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewD1Databases]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ad973cd82972e5785d4059c043900c1391486220c31ce9ff2107ac03b75adc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces",
    jsii_struct_bases=[],
    name_mapping={"namespace_id": "namespaceId"},
)
class PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces:
    def __init__(self, *, namespace_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param namespace_id: ID of the Durable Object namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#namespace_id PagesProject#namespace_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30e173176a8977d674bb610006e706cab93da0a36bd7858d6f6ba86f8ac5780b)
            check_type(argname="argument namespace_id", value=namespace_id, expected_type=type_hints["namespace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if namespace_id is not None:
            self._values["namespace_id"] = namespace_id

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''ID of the Durable Object namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#namespace_id PagesProject#namespace_id}
        '''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__70d4f33240623ffb0b4a51b79d3f87b301c13262a076532bbd117346fe9fbf5a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4781c0e4dcaf71bd3993e236f4b74c26db32d635f412e5cc3dc8bc0d29e3ddba)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5561bd76e2c8e41f4b614fe0e51a402b61e64c86de8e315dc95c7fccf08fcad1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__40e3f523bea433806dcb3543e5d38600506b85d494e8c7c754f201a28903ad09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e159049a476960c71e5b2bf7179f9b5ba79780a78cf4fbe5fbf6b9dac2c3d6de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d235a5974c9b9dc2831108c112113199a1d4a85ec89d8d262a21adb29b87f5c4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetNamespaceId")
    def reset_namespace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespaceId", []))

    @builtins.property
    @jsii.member(jsii_name="namespaceIdInput")
    def namespace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @namespace_id.setter
    def namespace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33b74e7c5ae02104e0099e592086b79bdd5a5f355996759385d51dda2ebc2478)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0a9908634a3e6c03272c358bc6368bfabd9530a0e2a870d941a5d78754e9c01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewEnvVars",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "value": "value"},
)
class PagesProjectDeploymentConfigsPreviewEnvVars:
    def __init__(self, *, type: builtins.str, value: builtins.str) -> None:
        '''
        :param type: Available values: "plain_text", "secret_text". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#type PagesProject#type}
        :param value: Environment variable value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#value PagesProject#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15b67416fedaaf4c1d8dca670bd8e1223ac77d74742a159a3b53906ea3b98007)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
            "value": value,
        }

    @builtins.property
    def type(self) -> builtins.str:
        '''Available values: "plain_text", "secret_text".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#type PagesProject#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Environment variable value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#value PagesProject#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewEnvVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewEnvVarsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewEnvVarsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e4569f3cca6af930788f119ccacb9bbe5595f72cad22293055927275379d47b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewEnvVarsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c0876b15d4c2dbde4144116cecdfa9b0fb42a5b2690db28542e77bb8d0e1aa5)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewEnvVarsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28b1ed089e02de80c84e0c267d7c3b62d1f4cbed99185d493363092672f01375)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec8a3caa8196bfcf5cc9316ff35ff81539433f92d29018fa39431fe67b3e909f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewEnvVars]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewEnvVars]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewEnvVars]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93e16a749bb972af2900934197c0b062119e2f729123dbad14c6640e143ed34d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewEnvVarsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewEnvVarsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f7c9cdf013166c01961d1774e717e90ac28f04f74117ad615062978cc674e79)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1aac0ee5e2ca24da8d5a95af2feb9012edd9f8a0c4d091b2e6a1af1c9366c999)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30c2013bbd585025eb5248e486983a48a912492ee3e25951a1ba1881c0facc72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewEnvVars]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewEnvVars]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewEnvVars]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08f9322992d57063eda4d53ac61af83ec8d8fe10e16dedebb6e9302805b83ff0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewHyperdriveBindings",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class PagesProjectDeploymentConfigsPreviewHyperdriveBindings:
    def __init__(self, *, id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#id PagesProject#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__192e99c9daaf49be6f483e85b29fceebfaa8a954bec17155d9a6dd7e47f1313a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#id PagesProject#id}.

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
        return "PagesProjectDeploymentConfigsPreviewHyperdriveBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a259d1c91d187e0999ac0db86e397c241068b6c53ead37206549c4b0a6007cb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fc4ffdc3674d8e11d6bc946cecd4585ca35a7129c39792f766dd50b406604e1)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7f9ba377c1971687adaa2cc1e790660411deeaa9a84f453f2f732bbcce79982)
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
            type_hints = typing.get_type_hints(_typecheckingstub__da4ad5de267e78e8ce6acf57f8517e8a7bc49a0a05cbcda5f82ae62bcad647ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9510d808e53696aa432112c53b99bd5a487293a06babcb9059713c26de38ff08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8358a526f7a4f88f8bd92fa408d2d506b1268c75038fbb8f6c5c86de2772ae69)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

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
            type_hints = typing.get_type_hints(_typecheckingstub__72679c84e70af5bf17ad9f9ebe43076747d738e44e1ecade4befc37e7be934b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55fa879f06ae2ae97b07f5e9a4ccf19730737c58b7fb36663c1daa92a1568546)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewKvNamespaces",
    jsii_struct_bases=[],
    name_mapping={"namespace_id": "namespaceId"},
)
class PagesProjectDeploymentConfigsPreviewKvNamespaces:
    def __init__(self, *, namespace_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param namespace_id: ID of the KV namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#namespace_id PagesProject#namespace_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0091c6bfff792edf941b777181d73d21ec638f02e8da108a889c8a6bca156b39)
            check_type(argname="argument namespace_id", value=namespace_id, expected_type=type_hints["namespace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if namespace_id is not None:
            self._values["namespace_id"] = namespace_id

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''ID of the KV namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#namespace_id PagesProject#namespace_id}
        '''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewKvNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewKvNamespacesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewKvNamespacesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa81e369fb82e5898fd03ba97308131ffbd9af0bb54e206b4814bb15a797052f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f71b654da1e06d473d99add3109ca9624208d1d6d4d7eeca728d24cbd6b8c428)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28884ded9dbc2911ac11e8d0beaa20600018d35aa3b38d32abafca8a84da8037)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6385ededa8ee31f22d820781fba220289351df744da55e68e772ad2e10f905e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewKvNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewKvNamespaces]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewKvNamespaces]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca9ade684d0e68576b0b70625dba79a8153d92bd612f12b93368278b8376d607)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1c12591f9c5d871e4cdd86154f22a28596e4ced890d0e7775428af9a48bd5d5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetNamespaceId")
    def reset_namespace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespaceId", []))

    @builtins.property
    @jsii.member(jsii_name="namespaceIdInput")
    def namespace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @namespace_id.setter
    def namespace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46170dbbf3bf9e0b75a2fb9f6b20d3242612d11275000b71269367bffc2b55c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewKvNamespaces]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewKvNamespaces]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewKvNamespaces]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86f148d59de412be1e62afa1994535accb078aa24bd810a94c5a4aa0ea507359)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewMtlsCertificates",
    jsii_struct_bases=[],
    name_mapping={"certificate_id": "certificateId"},
)
class PagesProjectDeploymentConfigsPreviewMtlsCertificates:
    def __init__(self, *, certificate_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param certificate_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#certificate_id PagesProject#certificate_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a18e5c004f2f37aedc7e4d9fc4e2f37c5411c2a6f3f77f920a8beb235fc64eda)
            check_type(argname="argument certificate_id", value=certificate_id, expected_type=type_hints["certificate_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if certificate_id is not None:
            self._values["certificate_id"] = certificate_id

    @builtins.property
    def certificate_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#certificate_id PagesProject#certificate_id}.'''
        result = self._values.get("certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewMtlsCertificates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewMtlsCertificatesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewMtlsCertificatesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__036a5539f8a755616a7be05fe77721fa2b275a43ec7db0aeb8c184fefbb1d73b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a672fc9370e709d418edd64075f87e948dd3a77bfc6c18b28bb2590d169d999d)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c53044c39bdd000bedb93d90d13f40d7a107d2215ea7169426dd860825a2f463)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa99f3351382915e9b7d35e6935225df2164c966f179d23bf818039c1268d37a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewMtlsCertificates]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewMtlsCertificates]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewMtlsCertificates]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acfdb63c6fd89cd4148690dc777531a22c7280547a71581b17822c9dda27de17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f05ad09691210667252ed44f11031a6fe96d87429fe8ece51f6b97a1fd7f00bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetCertificateId")
    def reset_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateId", []))

    @builtins.property
    @jsii.member(jsii_name="certificateIdInput")
    def certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @certificate_id.setter
    def certificate_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9504eb3738e939ac9b5ea1e32d6612729db2fe16feb45dcc4fb4a8aef39cf65a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewMtlsCertificates]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewMtlsCertificates]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewMtlsCertificates]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f179eb1f5dad0461bd66c21b747183f1853f306b71b0d83397f7a7b2f587ccc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae1a53fd86f66b2bd391be423e5c8d24aeb47824bd64d504a301cf722c043d66)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAiBindings")
    def put_ai_bindings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewAiBindings, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ec20dff6c58d847cb0da1df9a71eb62d842c9578a43ec96c89e79dc61dc683a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAiBindings", [value]))

    @jsii.member(jsii_name="putAnalyticsEngineDatasets")
    def put_analytics_engine_datasets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__417190bfe6103782ce90cc052627021de0142ceee43ce447d092af516c102985)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAnalyticsEngineDatasets", [value]))

    @jsii.member(jsii_name="putBrowsers")
    def put_browsers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewBrowsers, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e4c749f4b7aaba019814626b9c3a4c68402354ded5e3e2acd12eb49ab000f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBrowsers", [value]))

    @jsii.member(jsii_name="putD1Databases")
    def put_d1_databases(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewD1Databases, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d22d92ba9b73d16dd8eb147797ad7ed4ad17f41e7ded59ae891f9948c57b820)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putD1Databases", [value]))

    @jsii.member(jsii_name="putDurableObjectNamespaces")
    def put_durable_object_namespaces(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cc488b65167adfad3bb1f4e4b27e48854c83f9af9c77c76acd6a203affbf7dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDurableObjectNamespaces", [value]))

    @jsii.member(jsii_name="putEnvVars")
    def put_env_vars(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewEnvVars, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__598fb5e45906929fc164c29edfe79c10fcb3bf2297dcea57f0bf7d96fef89746)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEnvVars", [value]))

    @jsii.member(jsii_name="putHyperdriveBindings")
    def put_hyperdrive_bindings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewHyperdriveBindings, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69c572390962b8ce8d324d63ee0336af7bfcc7ab681fc6bec87ee12f0a29a008)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHyperdriveBindings", [value]))

    @jsii.member(jsii_name="putKvNamespaces")
    def put_kv_namespaces(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewKvNamespaces, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d14a1560b92ba5db11bead7e3e6a4b4ae378a70d31767adf9bf9bb5c5c837cc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putKvNamespaces", [value]))

    @jsii.member(jsii_name="putMtlsCertificates")
    def put_mtls_certificates(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewMtlsCertificates, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2231c01f40589e5223952c96103c8fb21b9b8f4ce249405db81a8b43646625e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMtlsCertificates", [value]))

    @jsii.member(jsii_name="putPlacement")
    def put_placement(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Placement mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mode PagesProject#mode}
        '''
        value = PagesProjectDeploymentConfigsPreviewPlacement(mode=mode)

        return typing.cast(None, jsii.invoke(self, "putPlacement", [value]))

    @jsii.member(jsii_name="putQueueProducers")
    def put_queue_producers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewQueueProducers", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25a997cfdbe7807ad2002b259eaeba72b0cb83f88e9d3c2b24e3e1427cec4ab0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putQueueProducers", [value]))

    @jsii.member(jsii_name="putR2Buckets")
    def put_r2_buckets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewR2Buckets", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41173fbb683ada048fd7b0ef6f23c6630ed0458e9569fd0d3a5e01f7a65b27ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putR2Buckets", [value]))

    @jsii.member(jsii_name="putServices")
    def put_services(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewServices", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f32dcc0cd76498e81c1806bc204f44444aad86e83eaf91f4563e2e0346b0c9ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServices", [value]))

    @jsii.member(jsii_name="putVectorizeBindings")
    def put_vectorize_bindings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsPreviewVectorizeBindings", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10f813d616615dd0186dd724144f03cf36011399b553b296885c6803485d884c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVectorizeBindings", [value]))

    @jsii.member(jsii_name="resetAiBindings")
    def reset_ai_bindings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAiBindings", []))

    @jsii.member(jsii_name="resetAnalyticsEngineDatasets")
    def reset_analytics_engine_datasets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnalyticsEngineDatasets", []))

    @jsii.member(jsii_name="resetBrowsers")
    def reset_browsers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBrowsers", []))

    @jsii.member(jsii_name="resetCompatibilityDate")
    def reset_compatibility_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibilityDate", []))

    @jsii.member(jsii_name="resetCompatibilityFlags")
    def reset_compatibility_flags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibilityFlags", []))

    @jsii.member(jsii_name="resetD1Databases")
    def reset_d1_databases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetD1Databases", []))

    @jsii.member(jsii_name="resetDurableObjectNamespaces")
    def reset_durable_object_namespaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDurableObjectNamespaces", []))

    @jsii.member(jsii_name="resetEnvVars")
    def reset_env_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvVars", []))

    @jsii.member(jsii_name="resetHyperdriveBindings")
    def reset_hyperdrive_bindings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHyperdriveBindings", []))

    @jsii.member(jsii_name="resetKvNamespaces")
    def reset_kv_namespaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKvNamespaces", []))

    @jsii.member(jsii_name="resetMtlsCertificates")
    def reset_mtls_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMtlsCertificates", []))

    @jsii.member(jsii_name="resetPlacement")
    def reset_placement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlacement", []))

    @jsii.member(jsii_name="resetQueueProducers")
    def reset_queue_producers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueProducers", []))

    @jsii.member(jsii_name="resetR2Buckets")
    def reset_r2_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetR2Buckets", []))

    @jsii.member(jsii_name="resetServices")
    def reset_services(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServices", []))

    @jsii.member(jsii_name="resetVectorizeBindings")
    def reset_vectorize_bindings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVectorizeBindings", []))

    @builtins.property
    @jsii.member(jsii_name="aiBindings")
    def ai_bindings(self) -> PagesProjectDeploymentConfigsPreviewAiBindingsMap:
        return typing.cast(PagesProjectDeploymentConfigsPreviewAiBindingsMap, jsii.get(self, "aiBindings"))

    @builtins.property
    @jsii.member(jsii_name="analyticsEngineDatasets")
    def analytics_engine_datasets(
        self,
    ) -> PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap:
        return typing.cast(PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap, jsii.get(self, "analyticsEngineDatasets"))

    @builtins.property
    @jsii.member(jsii_name="browsers")
    def browsers(self) -> PagesProjectDeploymentConfigsPreviewBrowsersMap:
        return typing.cast(PagesProjectDeploymentConfigsPreviewBrowsersMap, jsii.get(self, "browsers"))

    @builtins.property
    @jsii.member(jsii_name="d1Databases")
    def d1_databases(self) -> PagesProjectDeploymentConfigsPreviewD1DatabasesMap:
        return typing.cast(PagesProjectDeploymentConfigsPreviewD1DatabasesMap, jsii.get(self, "d1Databases"))

    @builtins.property
    @jsii.member(jsii_name="durableObjectNamespaces")
    def durable_object_namespaces(
        self,
    ) -> PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap:
        return typing.cast(PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap, jsii.get(self, "durableObjectNamespaces"))

    @builtins.property
    @jsii.member(jsii_name="envVars")
    def env_vars(self) -> PagesProjectDeploymentConfigsPreviewEnvVarsMap:
        return typing.cast(PagesProjectDeploymentConfigsPreviewEnvVarsMap, jsii.get(self, "envVars"))

    @builtins.property
    @jsii.member(jsii_name="hyperdriveBindings")
    def hyperdrive_bindings(
        self,
    ) -> PagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap:
        return typing.cast(PagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap, jsii.get(self, "hyperdriveBindings"))

    @builtins.property
    @jsii.member(jsii_name="kvNamespaces")
    def kv_namespaces(self) -> PagesProjectDeploymentConfigsPreviewKvNamespacesMap:
        return typing.cast(PagesProjectDeploymentConfigsPreviewKvNamespacesMap, jsii.get(self, "kvNamespaces"))

    @builtins.property
    @jsii.member(jsii_name="mtlsCertificates")
    def mtls_certificates(
        self,
    ) -> PagesProjectDeploymentConfigsPreviewMtlsCertificatesMap:
        return typing.cast(PagesProjectDeploymentConfigsPreviewMtlsCertificatesMap, jsii.get(self, "mtlsCertificates"))

    @builtins.property
    @jsii.member(jsii_name="placement")
    def placement(
        self,
    ) -> "PagesProjectDeploymentConfigsPreviewPlacementOutputReference":
        return typing.cast("PagesProjectDeploymentConfigsPreviewPlacementOutputReference", jsii.get(self, "placement"))

    @builtins.property
    @jsii.member(jsii_name="queueProducers")
    def queue_producers(
        self,
    ) -> "PagesProjectDeploymentConfigsPreviewQueueProducersMap":
        return typing.cast("PagesProjectDeploymentConfigsPreviewQueueProducersMap", jsii.get(self, "queueProducers"))

    @builtins.property
    @jsii.member(jsii_name="r2Buckets")
    def r2_buckets(self) -> "PagesProjectDeploymentConfigsPreviewR2BucketsMap":
        return typing.cast("PagesProjectDeploymentConfigsPreviewR2BucketsMap", jsii.get(self, "r2Buckets"))

    @builtins.property
    @jsii.member(jsii_name="services")
    def services(self) -> "PagesProjectDeploymentConfigsPreviewServicesMap":
        return typing.cast("PagesProjectDeploymentConfigsPreviewServicesMap", jsii.get(self, "services"))

    @builtins.property
    @jsii.member(jsii_name="vectorizeBindings")
    def vectorize_bindings(
        self,
    ) -> "PagesProjectDeploymentConfigsPreviewVectorizeBindingsMap":
        return typing.cast("PagesProjectDeploymentConfigsPreviewVectorizeBindingsMap", jsii.get(self, "vectorizeBindings"))

    @builtins.property
    @jsii.member(jsii_name="aiBindingsInput")
    def ai_bindings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAiBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAiBindings]]], jsii.get(self, "aiBindingsInput"))

    @builtins.property
    @jsii.member(jsii_name="analyticsEngineDatasetsInput")
    def analytics_engine_datasets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]]], jsii.get(self, "analyticsEngineDatasetsInput"))

    @builtins.property
    @jsii.member(jsii_name="browsersInput")
    def browsers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewBrowsers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewBrowsers]]], jsii.get(self, "browsersInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityDateInput")
    def compatibility_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "compatibilityDateInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlagsInput")
    def compatibility_flags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "compatibilityFlagsInput"))

    @builtins.property
    @jsii.member(jsii_name="d1DatabasesInput")
    def d1_databases_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewD1Databases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewD1Databases]]], jsii.get(self, "d1DatabasesInput"))

    @builtins.property
    @jsii.member(jsii_name="durableObjectNamespacesInput")
    def durable_object_namespaces_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]]], jsii.get(self, "durableObjectNamespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="envVarsInput")
    def env_vars_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewEnvVars]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewEnvVars]]], jsii.get(self, "envVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="hyperdriveBindingsInput")
    def hyperdrive_bindings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]]], jsii.get(self, "hyperdriveBindingsInput"))

    @builtins.property
    @jsii.member(jsii_name="kvNamespacesInput")
    def kv_namespaces_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewKvNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewKvNamespaces]]], jsii.get(self, "kvNamespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="mtlsCertificatesInput")
    def mtls_certificates_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewMtlsCertificates]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewMtlsCertificates]]], jsii.get(self, "mtlsCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="placementInput")
    def placement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigsPreviewPlacement"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigsPreviewPlacement"]], jsii.get(self, "placementInput"))

    @builtins.property
    @jsii.member(jsii_name="queueProducersInput")
    def queue_producers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewQueueProducers"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewQueueProducers"]]], jsii.get(self, "queueProducersInput"))

    @builtins.property
    @jsii.member(jsii_name="r2BucketsInput")
    def r2_buckets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewR2Buckets"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewR2Buckets"]]], jsii.get(self, "r2BucketsInput"))

    @builtins.property
    @jsii.member(jsii_name="servicesInput")
    def services_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewServices"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewServices"]]], jsii.get(self, "servicesInput"))

    @builtins.property
    @jsii.member(jsii_name="vectorizeBindingsInput")
    def vectorize_bindings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewVectorizeBindings"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsPreviewVectorizeBindings"]]], jsii.get(self, "vectorizeBindingsInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityDate")
    def compatibility_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compatibilityDate"))

    @compatibility_date.setter
    def compatibility_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32865b61c6888db2bacfa85645fe28c8b167deb8ea98040548aefe9babd5762b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compatibilityDate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlags")
    def compatibility_flags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibilityFlags"))

    @compatibility_flags.setter
    def compatibility_flags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c7134d0cb1462ec7eb665fd47f1f671843e450543c55d25eeefb57ec5363f35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compatibilityFlags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreview]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreview]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreview]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50fc5ad9dba9a0aa13954ab41f376699bde856670f046d16f6a4d579da2f821d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewPlacement",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode"},
)
class PagesProjectDeploymentConfigsPreviewPlacement:
    def __init__(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Placement mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mode PagesProject#mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98f1c108112e6cb9dfa64dc7e8738e74ba3bbe017744a487db1ffcc02842e762)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Placement mode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mode PagesProject#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewPlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewPlacementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewPlacementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7b411d7b6d09b8b835b73305f16f04ef41c7b409555e816077606e0f4bf2fd4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__65417fa8c2cc18f68ac950d676fbd72cec4c53f0bb6719ea950ed2b8cff669e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewPlacement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewPlacement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewPlacement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43c47e159562b79c33de06c05ffd2e2db7091b6f30a62cdeaf3546b831b128b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewQueueProducers",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class PagesProjectDeploymentConfigsPreviewQueueProducers:
    def __init__(self, *, name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param name: Name of the Queue. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aac2cb1d433db465a2244ce20f6a2e5bf0b22284fe8573721c9dba326d09f4d)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Queue.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewQueueProducers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewQueueProducersMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewQueueProducersMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__239db956f3fbc55ef4925154193f59b5d4560267d16094456bff1067828f7380)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewQueueProducersOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27b3536ad4f31d5b96da48544b25a8dcb6e3e517856c7fe892f0fe94be0e505a)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewQueueProducersOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98e2cbffd1e75ca79ceaf3c96b75d9753b789a743a11f9ca32d4eec237ebeb47)
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
            type_hints = typing.get_type_hints(_typecheckingstub__63924724f6907220720d7db9ca86521fbb49f4faf09139e24b0c21dd76f60888)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewQueueProducers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewQueueProducers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewQueueProducers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da9a7562af934bd78f747c31d19d1ebb2307f261338ad24321a64305513177b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewQueueProducersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewQueueProducersOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f4b59bc31d41d6fb5641972315b7595421d0cb3d2fda38a30247af3ba2ed351)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b79893b3b078b52a7e8fa9b1892608218a39c7b17e459083f239d112702cdaf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewQueueProducers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewQueueProducers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewQueueProducers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__222048d1c5398c643eba07ceae27205c6a6e285d0b1c49231cbfcdc007c1b140)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewR2Buckets",
    jsii_struct_bases=[],
    name_mapping={"jurisdiction": "jurisdiction", "name": "name"},
)
class PagesProjectDeploymentConfigsPreviewR2Buckets:
    def __init__(
        self,
        *,
        jurisdiction: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param jurisdiction: Jurisdiction of the R2 bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#jurisdiction PagesProject#jurisdiction}
        :param name: Name of the R2 bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f06b3e0e25cff25171c338e12f56c5d2fcf04346f00b9d19ac9b60458c3757f)
            check_type(argname="argument jurisdiction", value=jurisdiction, expected_type=type_hints["jurisdiction"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if jurisdiction is not None:
            self._values["jurisdiction"] = jurisdiction
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def jurisdiction(self) -> typing.Optional[builtins.str]:
        '''Jurisdiction of the R2 bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#jurisdiction PagesProject#jurisdiction}
        '''
        result = self._values.get("jurisdiction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the R2 bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewR2Buckets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewR2BucketsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewR2BucketsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fdb554ac00bad22917f5954494ecacb3e2bc701111b1c031502edf337d4cf037)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewR2BucketsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64ef3a0c1b5814161d677e454f79ed28a9ab9a23d982931e3b8fca404e39158a)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewR2BucketsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec2fa43d1b9bfca810aa718170af32046324dd81dc20fe313da2609bcc55d264)
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
            type_hints = typing.get_type_hints(_typecheckingstub__36b40d53f16ef021aabcddff69f0d21e2d959f8d160f2585c6991f328d5aa4d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewR2Buckets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewR2Buckets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewR2Buckets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b4c3b22c6f3fd4bfa023587400a89be9f5d544f5b9428b80c15fd8541caaefd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewR2BucketsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewR2BucketsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f50de20dd6885d8be2d3c6d0c22d3454cad2fa9638c5983b1c3987c5f9032282)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetJurisdiction")
    def reset_jurisdiction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJurisdiction", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="jurisdictionInput")
    def jurisdiction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jurisdictionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="jurisdiction")
    def jurisdiction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jurisdiction"))

    @jurisdiction.setter
    def jurisdiction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c07f19a019c327b0a68c45c09621c69fc03ce238eb63c910381a01eeb70c19f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jurisdiction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea00ffba8eb1c97282d35e12cfd4fe6de996d2b4516fe2e8980984818d6862d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewR2Buckets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewR2Buckets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewR2Buckets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c220e9678afcf22cfa97e3a27f41cebdc88e697d21d87596ec5529a369e93a75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewServices",
    jsii_struct_bases=[],
    name_mapping={
        "entrypoint": "entrypoint",
        "environment": "environment",
        "service": "service",
    },
)
class PagesProjectDeploymentConfigsPreviewServices:
    def __init__(
        self,
        *,
        entrypoint: typing.Optional[builtins.str] = None,
        environment: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param entrypoint: The entrypoint to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#entrypoint PagesProject#entrypoint}
        :param environment: The Service environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#environment PagesProject#environment}
        :param service: The Service name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#service PagesProject#service}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3dc859c4056c6634de88b888a0b1fcf74aa14c76caef57c46f84cd13286819b)
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if environment is not None:
            self._values["environment"] = environment
        if service is not None:
            self._values["service"] = service

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''The entrypoint to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#entrypoint PagesProject#entrypoint}
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(self) -> typing.Optional[builtins.str]:
        '''The Service environment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#environment PagesProject#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''The Service name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#service PagesProject#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewServicesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewServicesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c6ab4dc485273734abbece379130dbff6d2b495d42ecc81bcf468277574db246)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewServicesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5015c7ec43fbe278ee6034f2584ab10e1b4392850a34add37f1686e7b0648827)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewServicesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a4bbec2f58b815ee751313a4e6417d32f9abf453ca7bbd838137f6dcdea56fd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e7ae510de1e8f44a2b042b10d32dc107ba73b7dbba86dc3b8bb1acb8f55b9831)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewServices]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewServices]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewServices]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c39d21eb6c512f276f76eb2797aa5bb23b6d4011c8c8442cf43cc66eb502b3e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewServicesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewServicesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c91dc20403a6582fcf1d54afd0bc690dae4fbb20345086fa86675013051ad2c0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetEntrypoint")
    def reset_entrypoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntrypoint", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetService")
    def reset_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetService", []))

    @builtins.property
    @jsii.member(jsii_name="entrypointInput")
    def entrypoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entrypointInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="entrypoint")
    def entrypoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entrypoint"))

    @entrypoint.setter
    def entrypoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89960e94ae7fe1b9a2061d97ebd3cab62399df92a743845527b478b185bece7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entrypoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1397b2f131c9228cf547eb37d75cae43cde9fef4058fb75018c5fb2a301faaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eaf82a64ac7fd2da822f4042b24bca8700d0398319a8d662928a8ad1149a36c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewServices]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewServices]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewServices]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3353c6dcfea0ba66398767df540b9c6d7037b8daae622412f049f0ab7013e5f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewVectorizeBindings",
    jsii_struct_bases=[],
    name_mapping={"index_name": "indexName"},
)
class PagesProjectDeploymentConfigsPreviewVectorizeBindings:
    def __init__(self, *, index_name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param index_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#index_name PagesProject#index_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91b9c2970362746d5a671ad4476b0b611cbbc96d98d86c80542ca3087e7a736f)
            check_type(argname="argument index_name", value=index_name, expected_type=type_hints["index_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if index_name is not None:
            self._values["index_name"] = index_name

    @builtins.property
    def index_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#index_name PagesProject#index_name}.'''
        result = self._values.get("index_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsPreviewVectorizeBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsPreviewVectorizeBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewVectorizeBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da59b03d8f7602c1cf7e2b77fb84d7b91b9738ea3b0d7e8b542ffc30f36e1dc3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__898ebc7e1d4bd9c3641283bfd5ca82ac480eb69a825ec54bdc6867cf555778da)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e60c9342a4484d0357043cefa93b3a6e2e61deb95d6b05c8f99919ecdd548e5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8dc95609cf5d7537d957cad3734f93ea8714ed831d6649a365982300ad2ce07e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewVectorizeBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewVectorizeBindings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewVectorizeBindings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db1ba0834b91b841298b4e285d65248cce20f8b06a248a368dee46e3c9ac9b80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e34dbde9508efa453e2c09119f668f62332ef1cb64b9c28676d8aa6875703b0c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetIndexName")
    def reset_index_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexName", []))

    @builtins.property
    @jsii.member(jsii_name="indexNameInput")
    def index_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexNameInput"))

    @builtins.property
    @jsii.member(jsii_name="indexName")
    def index_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexName"))

    @index_name.setter
    def index_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf937ba07575a968342ca5df7a371aeee467b185914be4a88f6ff96c29fe2e61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indexName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewVectorizeBindings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewVectorizeBindings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewVectorizeBindings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b19b6514b07a61523a856a6869326b8fcbff25b1e32779bb38b8d531552bb50a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProduction",
    jsii_struct_bases=[],
    name_mapping={
        "ai_bindings": "aiBindings",
        "analytics_engine_datasets": "analyticsEngineDatasets",
        "browsers": "browsers",
        "compatibility_date": "compatibilityDate",
        "compatibility_flags": "compatibilityFlags",
        "d1_databases": "d1Databases",
        "durable_object_namespaces": "durableObjectNamespaces",
        "env_vars": "envVars",
        "hyperdrive_bindings": "hyperdriveBindings",
        "kv_namespaces": "kvNamespaces",
        "mtls_certificates": "mtlsCertificates",
        "placement": "placement",
        "queue_producers": "queueProducers",
        "r2_buckets": "r2Buckets",
        "services": "services",
        "vectorize_bindings": "vectorizeBindings",
    },
)
class PagesProjectDeploymentConfigsProduction:
    def __init__(
        self,
        *,
        ai_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionAiBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        analytics_engine_datasets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        browsers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionBrowsers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        compatibility_date: typing.Optional[builtins.str] = None,
        compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        d1_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionD1Databases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        durable_object_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionDurableObjectNamespaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        env_vars: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionEnvVars", typing.Dict[builtins.str, typing.Any]]]]] = None,
        hyperdrive_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionHyperdriveBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        kv_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionKvNamespaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        mtls_certificates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionMtlsCertificates", typing.Dict[builtins.str, typing.Any]]]]] = None,
        placement: typing.Optional[typing.Union["PagesProjectDeploymentConfigsProductionPlacement", typing.Dict[builtins.str, typing.Any]]] = None,
        queue_producers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionQueueProducers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        r2_buckets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionR2Buckets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionServices", typing.Dict[builtins.str, typing.Any]]]]] = None,
        vectorize_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionVectorizeBindings", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param ai_bindings: Constellation bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#ai_bindings PagesProject#ai_bindings}
        :param analytics_engine_datasets: Analytics Engine bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#analytics_engine_datasets PagesProject#analytics_engine_datasets}
        :param browsers: Browser bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#browsers PagesProject#browsers}
        :param compatibility_date: Compatibility date used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_date PagesProject#compatibility_date}
        :param compatibility_flags: Compatibility flags used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_flags PagesProject#compatibility_flags}
        :param d1_databases: D1 databases used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#d1_databases PagesProject#d1_databases}
        :param durable_object_namespaces: Durable Object namespaces used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#durable_object_namespaces PagesProject#durable_object_namespaces}
        :param env_vars: Environment variables used for builds and Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#env_vars PagesProject#env_vars}
        :param hyperdrive_bindings: Hyperdrive bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#hyperdrive_bindings PagesProject#hyperdrive_bindings}
        :param kv_namespaces: KV namespaces used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#kv_namespaces PagesProject#kv_namespaces}
        :param mtls_certificates: mTLS bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mtls_certificates PagesProject#mtls_certificates}
        :param placement: Placement setting used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#placement PagesProject#placement}
        :param queue_producers: Queue Producer bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#queue_producers PagesProject#queue_producers}
        :param r2_buckets: R2 buckets used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#r2_buckets PagesProject#r2_buckets}
        :param services: Services used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#services PagesProject#services}
        :param vectorize_bindings: Vectorize bindings used for Pages Functions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#vectorize_bindings PagesProject#vectorize_bindings}
        '''
        if isinstance(placement, dict):
            placement = PagesProjectDeploymentConfigsProductionPlacement(**placement)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__336477b4868198acb01a1b41c8690524ec7ae03a6fd6dc2340a5ffb5c86959e1)
            check_type(argname="argument ai_bindings", value=ai_bindings, expected_type=type_hints["ai_bindings"])
            check_type(argname="argument analytics_engine_datasets", value=analytics_engine_datasets, expected_type=type_hints["analytics_engine_datasets"])
            check_type(argname="argument browsers", value=browsers, expected_type=type_hints["browsers"])
            check_type(argname="argument compatibility_date", value=compatibility_date, expected_type=type_hints["compatibility_date"])
            check_type(argname="argument compatibility_flags", value=compatibility_flags, expected_type=type_hints["compatibility_flags"])
            check_type(argname="argument d1_databases", value=d1_databases, expected_type=type_hints["d1_databases"])
            check_type(argname="argument durable_object_namespaces", value=durable_object_namespaces, expected_type=type_hints["durable_object_namespaces"])
            check_type(argname="argument env_vars", value=env_vars, expected_type=type_hints["env_vars"])
            check_type(argname="argument hyperdrive_bindings", value=hyperdrive_bindings, expected_type=type_hints["hyperdrive_bindings"])
            check_type(argname="argument kv_namespaces", value=kv_namespaces, expected_type=type_hints["kv_namespaces"])
            check_type(argname="argument mtls_certificates", value=mtls_certificates, expected_type=type_hints["mtls_certificates"])
            check_type(argname="argument placement", value=placement, expected_type=type_hints["placement"])
            check_type(argname="argument queue_producers", value=queue_producers, expected_type=type_hints["queue_producers"])
            check_type(argname="argument r2_buckets", value=r2_buckets, expected_type=type_hints["r2_buckets"])
            check_type(argname="argument services", value=services, expected_type=type_hints["services"])
            check_type(argname="argument vectorize_bindings", value=vectorize_bindings, expected_type=type_hints["vectorize_bindings"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ai_bindings is not None:
            self._values["ai_bindings"] = ai_bindings
        if analytics_engine_datasets is not None:
            self._values["analytics_engine_datasets"] = analytics_engine_datasets
        if browsers is not None:
            self._values["browsers"] = browsers
        if compatibility_date is not None:
            self._values["compatibility_date"] = compatibility_date
        if compatibility_flags is not None:
            self._values["compatibility_flags"] = compatibility_flags
        if d1_databases is not None:
            self._values["d1_databases"] = d1_databases
        if durable_object_namespaces is not None:
            self._values["durable_object_namespaces"] = durable_object_namespaces
        if env_vars is not None:
            self._values["env_vars"] = env_vars
        if hyperdrive_bindings is not None:
            self._values["hyperdrive_bindings"] = hyperdrive_bindings
        if kv_namespaces is not None:
            self._values["kv_namespaces"] = kv_namespaces
        if mtls_certificates is not None:
            self._values["mtls_certificates"] = mtls_certificates
        if placement is not None:
            self._values["placement"] = placement
        if queue_producers is not None:
            self._values["queue_producers"] = queue_producers
        if r2_buckets is not None:
            self._values["r2_buckets"] = r2_buckets
        if services is not None:
            self._values["services"] = services
        if vectorize_bindings is not None:
            self._values["vectorize_bindings"] = vectorize_bindings

    @builtins.property
    def ai_bindings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionAiBindings"]]]:
        '''Constellation bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#ai_bindings PagesProject#ai_bindings}
        '''
        result = self._values.get("ai_bindings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionAiBindings"]]], result)

    @builtins.property
    def analytics_engine_datasets(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets"]]]:
        '''Analytics Engine bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#analytics_engine_datasets PagesProject#analytics_engine_datasets}
        '''
        result = self._values.get("analytics_engine_datasets")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets"]]], result)

    @builtins.property
    def browsers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionBrowsers"]]]:
        '''Browser bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#browsers PagesProject#browsers}
        '''
        result = self._values.get("browsers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionBrowsers"]]], result)

    @builtins.property
    def compatibility_date(self) -> typing.Optional[builtins.str]:
        '''Compatibility date used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_date PagesProject#compatibility_date}
        '''
        result = self._values.get("compatibility_date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compatibility_flags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Compatibility flags used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#compatibility_flags PagesProject#compatibility_flags}
        '''
        result = self._values.get("compatibility_flags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def d1_databases(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionD1Databases"]]]:
        '''D1 databases used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#d1_databases PagesProject#d1_databases}
        '''
        result = self._values.get("d1_databases")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionD1Databases"]]], result)

    @builtins.property
    def durable_object_namespaces(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionDurableObjectNamespaces"]]]:
        '''Durable Object namespaces used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#durable_object_namespaces PagesProject#durable_object_namespaces}
        '''
        result = self._values.get("durable_object_namespaces")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionDurableObjectNamespaces"]]], result)

    @builtins.property
    def env_vars(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionEnvVars"]]]:
        '''Environment variables used for builds and Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#env_vars PagesProject#env_vars}
        '''
        result = self._values.get("env_vars")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionEnvVars"]]], result)

    @builtins.property
    def hyperdrive_bindings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionHyperdriveBindings"]]]:
        '''Hyperdrive bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#hyperdrive_bindings PagesProject#hyperdrive_bindings}
        '''
        result = self._values.get("hyperdrive_bindings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionHyperdriveBindings"]]], result)

    @builtins.property
    def kv_namespaces(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionKvNamespaces"]]]:
        '''KV namespaces used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#kv_namespaces PagesProject#kv_namespaces}
        '''
        result = self._values.get("kv_namespaces")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionKvNamespaces"]]], result)

    @builtins.property
    def mtls_certificates(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionMtlsCertificates"]]]:
        '''mTLS bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mtls_certificates PagesProject#mtls_certificates}
        '''
        result = self._values.get("mtls_certificates")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionMtlsCertificates"]]], result)

    @builtins.property
    def placement(
        self,
    ) -> typing.Optional["PagesProjectDeploymentConfigsProductionPlacement"]:
        '''Placement setting used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#placement PagesProject#placement}
        '''
        result = self._values.get("placement")
        return typing.cast(typing.Optional["PagesProjectDeploymentConfigsProductionPlacement"], result)

    @builtins.property
    def queue_producers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionQueueProducers"]]]:
        '''Queue Producer bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#queue_producers PagesProject#queue_producers}
        '''
        result = self._values.get("queue_producers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionQueueProducers"]]], result)

    @builtins.property
    def r2_buckets(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionR2Buckets"]]]:
        '''R2 buckets used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#r2_buckets PagesProject#r2_buckets}
        '''
        result = self._values.get("r2_buckets")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionR2Buckets"]]], result)

    @builtins.property
    def services(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionServices"]]]:
        '''Services used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#services PagesProject#services}
        '''
        result = self._values.get("services")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionServices"]]], result)

    @builtins.property
    def vectorize_bindings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionVectorizeBindings"]]]:
        '''Vectorize bindings used for Pages Functions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#vectorize_bindings PagesProject#vectorize_bindings}
        '''
        result = self._values.get("vectorize_bindings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionVectorizeBindings"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProduction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionAiBindings",
    jsii_struct_bases=[],
    name_mapping={"project_id": "projectId"},
)
class PagesProjectDeploymentConfigsProductionAiBindings:
    def __init__(self, *, project_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#project_id PagesProject#project_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ff5d97c595c1134b63db5ac4b32e75f553c80b9a7518cad080ce96fde08657c)
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if project_id is not None:
            self._values["project_id"] = project_id

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#project_id PagesProject#project_id}.'''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionAiBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionAiBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionAiBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9f8e9340303a2dc4d9f6081357052a694dce877b3f217ecbef29bda2f26c4a3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionAiBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07fcc8f725906b04b55f406778733b31a6d98a0fc16e7d2c4531c9a40e789445)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionAiBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__889c87f5d45cac1f5d7d3a87778d51ee436e010fc083016843d24ba478cfdbdc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__377d9960782684629b7bb0b74232441fbfb8579e761630782ef30e971cae95d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAiBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAiBindings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAiBindings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0868a385b5c4fa2462db9e6c451b171fb3ceedfdea9161ef0d00f7fd851d47de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionAiBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionAiBindingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35ec8fef7125dc52abb39d432647bec422de4a5c147f49b9773f7eaae13e95f7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3212f4f96261304683213d75e42a94473ee550791d0bd79c7caa80731efd6505)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionAiBindings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionAiBindings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionAiBindings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__794201a95967de48a30b07d2d66b1b1e81c45c512a84386be19f8ac07313b834)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets",
    jsii_struct_bases=[],
    name_mapping={"dataset": "dataset"},
)
class PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets:
    def __init__(self, *, dataset: typing.Optional[builtins.str] = None) -> None:
        '''
        :param dataset: Name of the dataset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#dataset PagesProject#dataset}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b679cc6846088b3249c313b1b81ed83e0ea05ebbac7414acd12ba4f1a447ffd)
            check_type(argname="argument dataset", value=dataset, expected_type=type_hints["dataset"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dataset is not None:
            self._values["dataset"] = dataset

    @builtins.property
    def dataset(self) -> typing.Optional[builtins.str]:
        '''Name of the dataset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#dataset PagesProject#dataset}
        '''
        result = self._values.get("dataset")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__02870ed3358357d5096a9cfd9df8df3593b8d84590d474684cd68fc325fa86ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb21e3a18ba78bce05aae4d12f450b9868c8dafa44f1a075be1977fadb3066b9)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__535d95a476329ae15c54279ef0c1db2474db61e78603edd4e4db2c33f574c74d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__308a30eccb6a51f7f90813c5d8b54302994d809d53d4945760013437b6200343)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52e16fb1fb955d944f3e51b203ceb6ecca34968ac8130cd5e0500178529a6e29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aedaf70d8e04d2b0b7cc77d59ccc0e6b3dc8d54f9c3bbf88b8e7ff64229fe1f3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetDataset")
    def reset_dataset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataset", []))

    @builtins.property
    @jsii.member(jsii_name="datasetInput")
    def dataset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datasetInput"))

    @builtins.property
    @jsii.member(jsii_name="dataset")
    def dataset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataset"))

    @dataset.setter
    def dataset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4b9eed51dc5fe645869f7f22cd0717e430232ea1679338064bc40d467d656fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d3a035c4d4f86ce2977fbc3da7b518853856f4614a9670d7011a8e441c07ea7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionBrowsers",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectDeploymentConfigsProductionBrowsers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionBrowsers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionBrowsersMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionBrowsersMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c08f9429bb3c65ef871855cd08e72e6e9e1f95353ca763de3e5ecf031175c084)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionBrowsersOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__104030db755caa30321919e3d9bed08047ec831b1a52069961591307faad0cd1)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionBrowsersOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a157275a445102d80fcf104faf75e89dffb58ca9e5eb0dfc86a8abe0fd78f984)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c2aa61f8bce92be6979c1f3004f02f47e9c66a9d234339084598869e93f6547f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionBrowsers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionBrowsers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionBrowsers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d750091991fda63c9bc3f55b833595de569f7adfa21ad742a92b9689f4a53922)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionBrowsersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionBrowsersOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__accaa1672dce8267a41c38aa9f2606107a72219b46759085596c87012acda276)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionBrowsers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionBrowsers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionBrowsers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cd61a036c5cfdbc0eb456575bfbbaead3f250b111b06188101a99913c8edd3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionD1Databases",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class PagesProjectDeploymentConfigsProductionD1Databases:
    def __init__(self, *, id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param id: UUID of the D1 database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#id PagesProject#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b07e3f86925ba50efcdd4cb80ef9f37066e9981c2be549f6f62a17b9a780f1f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''UUID of the D1 database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#id PagesProject#id}

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
        return "PagesProjectDeploymentConfigsProductionD1Databases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionD1DatabasesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionD1DatabasesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ddb96fa8acca946a3b1e435f236555dc89f77d6f31462755eb338407a6a5b82)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionD1DatabasesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42a38a7c7c8862e3a0540b016f3e96c953dde193dc18c20b5bfc9bde6da83da4)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionD1DatabasesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da395be733235e8385f7b7131609d5c388db897f4b63e96600e3b5ae1cd14bf7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__96d31ec0fc4396b5b07590f302dc061c0e85eb069bf056fd56a88844364ddf40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionD1Databases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionD1Databases]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionD1Databases]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7266370ac69f2961559145452acb76c691448fa91a1c94feae6845a066c527fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionD1DatabasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionD1DatabasesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe1624e30127d78f1ca4c75e97a1302997a9cde6d3e045c93b2b3fce27f4e93a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

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
            type_hints = typing.get_type_hints(_typecheckingstub__3014e21393539347669cf16987000547c24fa6b81dce7ea7d3b51bb63200666c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionD1Databases]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionD1Databases]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionD1Databases]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a52cd4951240de903e3b268cd3a68ad1e55523bd445d99a293d76869108de7b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionDurableObjectNamespaces",
    jsii_struct_bases=[],
    name_mapping={"namespace_id": "namespaceId"},
)
class PagesProjectDeploymentConfigsProductionDurableObjectNamespaces:
    def __init__(self, *, namespace_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param namespace_id: ID of the Durable Object namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#namespace_id PagesProject#namespace_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5facf7e9eb05e3ddbd403b5859d1f4977b3dc4a80ba17ebf9652ed6e82635a1b)
            check_type(argname="argument namespace_id", value=namespace_id, expected_type=type_hints["namespace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if namespace_id is not None:
            self._values["namespace_id"] = namespace_id

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''ID of the Durable Object namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#namespace_id PagesProject#namespace_id}
        '''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionDurableObjectNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__393417b9ad51b0a78031a583be5140f35606cea4548585fe156eb6d7ae7f5915)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31146e1fca391268e933c20a81cedb29b3010de397a8c2dd433da9b1ac9ac2c6)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4be6c4aada0a1e781a5db086812a2ae9e787ba6233b5cfc02259b581164484a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa35fc1419909edc6a718fc34b56f44dbcbd86dbd91c2d8ba7987c7afbeb958e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ccb025663d8864c9ec5d4b6ca7b1cf8abeeb0d2be24e620841d030ca398f5f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e93db690bf3acb3e77c803f081e84dd3134142ae397644e82888a7a161c48db)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetNamespaceId")
    def reset_namespace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespaceId", []))

    @builtins.property
    @jsii.member(jsii_name="namespaceIdInput")
    def namespace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @namespace_id.setter
    def namespace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4e22694e662bc4e51bc5f0e2c284959367311ca2d3b4e81e3dff4f2532ca4b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac3560bd072117cb1a8cd855f140daf6bbcdc85670b942118c33adedcc034930)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionEnvVars",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "value": "value"},
)
class PagesProjectDeploymentConfigsProductionEnvVars:
    def __init__(self, *, type: builtins.str, value: builtins.str) -> None:
        '''
        :param type: Available values: "plain_text", "secret_text". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#type PagesProject#type}
        :param value: Environment variable value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#value PagesProject#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b9b44ed860fa627e700a3874f02ef38db8b48bf5063094c79fe1463088504e0)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
            "value": value,
        }

    @builtins.property
    def type(self) -> builtins.str:
        '''Available values: "plain_text", "secret_text".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#type PagesProject#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Environment variable value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#value PagesProject#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionEnvVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionEnvVarsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionEnvVarsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a3ad473c1b2d9b9537995d6a8f799bdc21d557e89d827587b8f2c7f58e20028a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionEnvVarsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59b70c5fd462670cd9d1afc3b197cb080d71a48e84188333a83b13c353267a73)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionEnvVarsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__885f7cbba19987747fd921d423e055961b9c2e1b73d4eba00457e086ec3d3bf3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f88387157a9d6b9820795e3251f956b430602f314194c3e31bfb50e187e29d26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionEnvVars]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionEnvVars]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionEnvVars]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97e0cc0cb5840bdf1bcb1da86c18de820f4a60e216c6e5f58f5b0ed6abd97202)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionEnvVarsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionEnvVarsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2461340c95182022f8fe2551129598fff410ed6aa4a41e95ebe0972db2f9cc4e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21910a3a2500ab2c846c379e329bcbcfc12be582e29ed9fa50baad0014477689)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cf180b8c15141cfd72d3eb5fbccb6889d129ffc4b7ae329d10570b71f1988f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionEnvVars]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionEnvVars]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionEnvVars]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1521e8b7e8d314bb22aa4b29eefe9094eb4c3e35334f1ae8ef2bf2d468e5776)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionHyperdriveBindings",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class PagesProjectDeploymentConfigsProductionHyperdriveBindings:
    def __init__(self, *, id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#id PagesProject#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dcef968789f42b8643c17121084b18ce7873303e4611d4ba4459f760351a3c4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#id PagesProject#id}.

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
        return "PagesProjectDeploymentConfigsProductionHyperdriveBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionHyperdriveBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionHyperdriveBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__075a9cdcb82cbb0bb6beea4e9bdd0557e89813905e9ee241252386bc4a3a88d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__288777d630e4c772e0f16fbc86cf4f4be5c008cbb381b59770243c060239076e)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e36de89b1c24028dcb04244ee1c3336070af7a0601fdf9a3c35571c45071244f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__121fe227b2ac8a44a1524871f7f0d095adc301364059e48c9a56c05b3f96f07b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionHyperdriveBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionHyperdriveBindings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionHyperdriveBindings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50464c75713ef52ac7162c1e104dcbdfbf76914ee95ca6c03e880c1e82e38645)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c1f92c42ad004eb5a445f38cfea83a3f2f0621772d5b9fa97aceb25328cf980)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

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
            type_hints = typing.get_type_hints(_typecheckingstub__fbdf433c845bb15dd164fdaffc9c71379d5ec4b045701186417df41981b3e2d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionHyperdriveBindings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionHyperdriveBindings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionHyperdriveBindings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ab2cd636169d73ec675e05825da46f5328cdb58bf75a0b014eefc85e5bcf462)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionKvNamespaces",
    jsii_struct_bases=[],
    name_mapping={"namespace_id": "namespaceId"},
)
class PagesProjectDeploymentConfigsProductionKvNamespaces:
    def __init__(self, *, namespace_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param namespace_id: ID of the KV namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#namespace_id PagesProject#namespace_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a6df3da46e128f15b6f32b6347a411bd7edf9563701d2c9b9cdd3f863870c86)
            check_type(argname="argument namespace_id", value=namespace_id, expected_type=type_hints["namespace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if namespace_id is not None:
            self._values["namespace_id"] = namespace_id

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''ID of the KV namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#namespace_id PagesProject#namespace_id}
        '''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionKvNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionKvNamespacesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionKvNamespacesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8772c2a6be35138caab09a04bc4e598e9d6058a1bf6f488c9f8da53f48286f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionKvNamespacesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e3ecbc7ef9a7654105a14fb3d82ef765c8dfceca4fa88b6af3ae839db6ac7bd)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionKvNamespacesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75e3deeba2e0e6c7fec22d82373805c64e53185c925cd229924be48387e8650f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb2111ee0196e6a482ef0bf02b1a0b797f0811afb8c278b316f24694da99715d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionKvNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionKvNamespaces]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionKvNamespaces]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a5fa9d5b7f6941404f843ad70bca2750c5cc176f48ab64b20bf715fece794e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionKvNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionKvNamespacesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d11bc907e31936b0356aedd69791884d527959ebe3b5979a873f91acd3f341ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetNamespaceId")
    def reset_namespace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespaceId", []))

    @builtins.property
    @jsii.member(jsii_name="namespaceIdInput")
    def namespace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @namespace_id.setter
    def namespace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5d59f5ea71f5f86e7f768dca714a89a94ca91b03328ae5e94a2e1b1844d114a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionKvNamespaces]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionKvNamespaces]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionKvNamespaces]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53f6b2dbe49c9c106bc8d432f484ab9b819941fd6bf1851205299af03bde3349)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionMtlsCertificates",
    jsii_struct_bases=[],
    name_mapping={"certificate_id": "certificateId"},
)
class PagesProjectDeploymentConfigsProductionMtlsCertificates:
    def __init__(self, *, certificate_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param certificate_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#certificate_id PagesProject#certificate_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd37b77e2c113e2a54e4778d45e50b19a672aeaa3713fd15e5357d31cc4b2bc2)
            check_type(argname="argument certificate_id", value=certificate_id, expected_type=type_hints["certificate_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if certificate_id is not None:
            self._values["certificate_id"] = certificate_id

    @builtins.property
    def certificate_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#certificate_id PagesProject#certificate_id}.'''
        result = self._values.get("certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionMtlsCertificates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionMtlsCertificatesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionMtlsCertificatesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5da6dcf6cd2ae3f5bd4179c26eaaa5af92199a6d28ae06c578bb4b95b2a6f7f4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5325afd1898cdf5eb6c496d5f70430fa0924d217bf7fcc8096f182c846a17bb2)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68dc230cead5fb49b10f888198dadf50da696f96e65b3e94859c498d76df60d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2ef9abff9dce0fefe5eeaa1b60685f2482cedda9aabe4242a943688e20934b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionMtlsCertificates]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionMtlsCertificates]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionMtlsCertificates]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85876ddf90e1004248d920192fea1a4a595d0bdc48ce8275276da5a44dad8a0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fa78ef3498192dbc2ff9db9046495c95b5fb9dcfba49257100f6b21136d3622)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetCertificateId")
    def reset_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateId", []))

    @builtins.property
    @jsii.member(jsii_name="certificateIdInput")
    def certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @certificate_id.setter
    def certificate_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfb848be19ff968c58500e698c3d68aeccb67d9c903d5e027dfe96bb2ca9d817)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionMtlsCertificates]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionMtlsCertificates]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionMtlsCertificates]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a52b81f9c22f6645a9e1a736d7aa2305e78d1c37e07525bde99dd47c5f252492)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7265aa8b15c3914638516c9c006481db3073e868d9989557acf0a5b26b6db6e0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAiBindings")
    def put_ai_bindings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionAiBindings, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab39e9d61dfefb1d82e066039489b747c86f188cb0f14678d6bea3512ce1fe4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAiBindings", [value]))

    @jsii.member(jsii_name="putAnalyticsEngineDatasets")
    def put_analytics_engine_datasets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1912f585f44b15e875bc21567990cb3ad701cd3a196bb1a7be419f0127e99e19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAnalyticsEngineDatasets", [value]))

    @jsii.member(jsii_name="putBrowsers")
    def put_browsers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionBrowsers, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__359babca5c66c44a9bde581255a6353b6dcef5c98af9e87a91964fd3677c31e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBrowsers", [value]))

    @jsii.member(jsii_name="putD1Databases")
    def put_d1_databases(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionD1Databases, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea055b774ec561103d1f2ec91853c5002ce3ca7050e5cae9860ba21c273b1542)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putD1Databases", [value]))

    @jsii.member(jsii_name="putDurableObjectNamespaces")
    def put_durable_object_namespaces(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionDurableObjectNamespaces, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0696d974e924a31b4bf5fc11e56c82ec237a8097a11d8ddadecd390681f66554)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDurableObjectNamespaces", [value]))

    @jsii.member(jsii_name="putEnvVars")
    def put_env_vars(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionEnvVars, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64cf56547ae4acb9e492288a15ec9627ef630d3d318afaad577d67371072a601)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEnvVars", [value]))

    @jsii.member(jsii_name="putHyperdriveBindings")
    def put_hyperdrive_bindings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionHyperdriveBindings, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60b3e6d74e41bcf2dc47db2a6afc7f5dda41b948e1c7abbe6f3a512cbec5b943)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHyperdriveBindings", [value]))

    @jsii.member(jsii_name="putKvNamespaces")
    def put_kv_namespaces(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionKvNamespaces, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c950dd8a1491ddaac9f32c321029a4ac5486b775e76e157e5bc7877ca362eb91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putKvNamespaces", [value]))

    @jsii.member(jsii_name="putMtlsCertificates")
    def put_mtls_certificates(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionMtlsCertificates, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f7e5ecc077e3c9d2525340077c85564a46729b0b4833d1db73afd6833ae8deb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMtlsCertificates", [value]))

    @jsii.member(jsii_name="putPlacement")
    def put_placement(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Placement mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mode PagesProject#mode}
        '''
        value = PagesProjectDeploymentConfigsProductionPlacement(mode=mode)

        return typing.cast(None, jsii.invoke(self, "putPlacement", [value]))

    @jsii.member(jsii_name="putQueueProducers")
    def put_queue_producers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionQueueProducers", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d091dfd7ff7acb5f2ade8c546d13c435c8ba5a91a184cb3429579825f06312f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putQueueProducers", [value]))

    @jsii.member(jsii_name="putR2Buckets")
    def put_r2_buckets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionR2Buckets", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72babe7567d11dd698d8f5a1cae46a3fdedb9b556872813d88ad8f2c6ffd8821)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putR2Buckets", [value]))

    @jsii.member(jsii_name="putServices")
    def put_services(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionServices", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52a85093c99b01c2a6e1d903ade142711ff361b89b07ef5cb059dfdcac617cb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServices", [value]))

    @jsii.member(jsii_name="putVectorizeBindings")
    def put_vectorize_bindings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union["PagesProjectDeploymentConfigsProductionVectorizeBindings", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba98fc46484a18d84d2b94d9d99c3c2238d00155c2647ad20a04573ab141bcb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVectorizeBindings", [value]))

    @jsii.member(jsii_name="resetAiBindings")
    def reset_ai_bindings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAiBindings", []))

    @jsii.member(jsii_name="resetAnalyticsEngineDatasets")
    def reset_analytics_engine_datasets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnalyticsEngineDatasets", []))

    @jsii.member(jsii_name="resetBrowsers")
    def reset_browsers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBrowsers", []))

    @jsii.member(jsii_name="resetCompatibilityDate")
    def reset_compatibility_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibilityDate", []))

    @jsii.member(jsii_name="resetCompatibilityFlags")
    def reset_compatibility_flags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibilityFlags", []))

    @jsii.member(jsii_name="resetD1Databases")
    def reset_d1_databases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetD1Databases", []))

    @jsii.member(jsii_name="resetDurableObjectNamespaces")
    def reset_durable_object_namespaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDurableObjectNamespaces", []))

    @jsii.member(jsii_name="resetEnvVars")
    def reset_env_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvVars", []))

    @jsii.member(jsii_name="resetHyperdriveBindings")
    def reset_hyperdrive_bindings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHyperdriveBindings", []))

    @jsii.member(jsii_name="resetKvNamespaces")
    def reset_kv_namespaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKvNamespaces", []))

    @jsii.member(jsii_name="resetMtlsCertificates")
    def reset_mtls_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMtlsCertificates", []))

    @jsii.member(jsii_name="resetPlacement")
    def reset_placement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlacement", []))

    @jsii.member(jsii_name="resetQueueProducers")
    def reset_queue_producers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueProducers", []))

    @jsii.member(jsii_name="resetR2Buckets")
    def reset_r2_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetR2Buckets", []))

    @jsii.member(jsii_name="resetServices")
    def reset_services(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServices", []))

    @jsii.member(jsii_name="resetVectorizeBindings")
    def reset_vectorize_bindings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVectorizeBindings", []))

    @builtins.property
    @jsii.member(jsii_name="aiBindings")
    def ai_bindings(self) -> PagesProjectDeploymentConfigsProductionAiBindingsMap:
        return typing.cast(PagesProjectDeploymentConfigsProductionAiBindingsMap, jsii.get(self, "aiBindings"))

    @builtins.property
    @jsii.member(jsii_name="analyticsEngineDatasets")
    def analytics_engine_datasets(
        self,
    ) -> PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap:
        return typing.cast(PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap, jsii.get(self, "analyticsEngineDatasets"))

    @builtins.property
    @jsii.member(jsii_name="browsers")
    def browsers(self) -> PagesProjectDeploymentConfigsProductionBrowsersMap:
        return typing.cast(PagesProjectDeploymentConfigsProductionBrowsersMap, jsii.get(self, "browsers"))

    @builtins.property
    @jsii.member(jsii_name="d1Databases")
    def d1_databases(self) -> PagesProjectDeploymentConfigsProductionD1DatabasesMap:
        return typing.cast(PagesProjectDeploymentConfigsProductionD1DatabasesMap, jsii.get(self, "d1Databases"))

    @builtins.property
    @jsii.member(jsii_name="durableObjectNamespaces")
    def durable_object_namespaces(
        self,
    ) -> PagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap:
        return typing.cast(PagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap, jsii.get(self, "durableObjectNamespaces"))

    @builtins.property
    @jsii.member(jsii_name="envVars")
    def env_vars(self) -> PagesProjectDeploymentConfigsProductionEnvVarsMap:
        return typing.cast(PagesProjectDeploymentConfigsProductionEnvVarsMap, jsii.get(self, "envVars"))

    @builtins.property
    @jsii.member(jsii_name="hyperdriveBindings")
    def hyperdrive_bindings(
        self,
    ) -> PagesProjectDeploymentConfigsProductionHyperdriveBindingsMap:
        return typing.cast(PagesProjectDeploymentConfigsProductionHyperdriveBindingsMap, jsii.get(self, "hyperdriveBindings"))

    @builtins.property
    @jsii.member(jsii_name="kvNamespaces")
    def kv_namespaces(self) -> PagesProjectDeploymentConfigsProductionKvNamespacesMap:
        return typing.cast(PagesProjectDeploymentConfigsProductionKvNamespacesMap, jsii.get(self, "kvNamespaces"))

    @builtins.property
    @jsii.member(jsii_name="mtlsCertificates")
    def mtls_certificates(
        self,
    ) -> PagesProjectDeploymentConfigsProductionMtlsCertificatesMap:
        return typing.cast(PagesProjectDeploymentConfigsProductionMtlsCertificatesMap, jsii.get(self, "mtlsCertificates"))

    @builtins.property
    @jsii.member(jsii_name="placement")
    def placement(
        self,
    ) -> "PagesProjectDeploymentConfigsProductionPlacementOutputReference":
        return typing.cast("PagesProjectDeploymentConfigsProductionPlacementOutputReference", jsii.get(self, "placement"))

    @builtins.property
    @jsii.member(jsii_name="queueProducers")
    def queue_producers(
        self,
    ) -> "PagesProjectDeploymentConfigsProductionQueueProducersMap":
        return typing.cast("PagesProjectDeploymentConfigsProductionQueueProducersMap", jsii.get(self, "queueProducers"))

    @builtins.property
    @jsii.member(jsii_name="r2Buckets")
    def r2_buckets(self) -> "PagesProjectDeploymentConfigsProductionR2BucketsMap":
        return typing.cast("PagesProjectDeploymentConfigsProductionR2BucketsMap", jsii.get(self, "r2Buckets"))

    @builtins.property
    @jsii.member(jsii_name="services")
    def services(self) -> "PagesProjectDeploymentConfigsProductionServicesMap":
        return typing.cast("PagesProjectDeploymentConfigsProductionServicesMap", jsii.get(self, "services"))

    @builtins.property
    @jsii.member(jsii_name="vectorizeBindings")
    def vectorize_bindings(
        self,
    ) -> "PagesProjectDeploymentConfigsProductionVectorizeBindingsMap":
        return typing.cast("PagesProjectDeploymentConfigsProductionVectorizeBindingsMap", jsii.get(self, "vectorizeBindings"))

    @builtins.property
    @jsii.member(jsii_name="aiBindingsInput")
    def ai_bindings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAiBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAiBindings]]], jsii.get(self, "aiBindingsInput"))

    @builtins.property
    @jsii.member(jsii_name="analyticsEngineDatasetsInput")
    def analytics_engine_datasets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]]], jsii.get(self, "analyticsEngineDatasetsInput"))

    @builtins.property
    @jsii.member(jsii_name="browsersInput")
    def browsers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionBrowsers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionBrowsers]]], jsii.get(self, "browsersInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityDateInput")
    def compatibility_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "compatibilityDateInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlagsInput")
    def compatibility_flags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "compatibilityFlagsInput"))

    @builtins.property
    @jsii.member(jsii_name="d1DatabasesInput")
    def d1_databases_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionD1Databases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionD1Databases]]], jsii.get(self, "d1DatabasesInput"))

    @builtins.property
    @jsii.member(jsii_name="durableObjectNamespacesInput")
    def durable_object_namespaces_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]]], jsii.get(self, "durableObjectNamespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="envVarsInput")
    def env_vars_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionEnvVars]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionEnvVars]]], jsii.get(self, "envVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="hyperdriveBindingsInput")
    def hyperdrive_bindings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionHyperdriveBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionHyperdriveBindings]]], jsii.get(self, "hyperdriveBindingsInput"))

    @builtins.property
    @jsii.member(jsii_name="kvNamespacesInput")
    def kv_namespaces_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionKvNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionKvNamespaces]]], jsii.get(self, "kvNamespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="mtlsCertificatesInput")
    def mtls_certificates_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionMtlsCertificates]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionMtlsCertificates]]], jsii.get(self, "mtlsCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="placementInput")
    def placement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigsProductionPlacement"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PagesProjectDeploymentConfigsProductionPlacement"]], jsii.get(self, "placementInput"))

    @builtins.property
    @jsii.member(jsii_name="queueProducersInput")
    def queue_producers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionQueueProducers"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionQueueProducers"]]], jsii.get(self, "queueProducersInput"))

    @builtins.property
    @jsii.member(jsii_name="r2BucketsInput")
    def r2_buckets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionR2Buckets"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionR2Buckets"]]], jsii.get(self, "r2BucketsInput"))

    @builtins.property
    @jsii.member(jsii_name="servicesInput")
    def services_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionServices"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionServices"]]], jsii.get(self, "servicesInput"))

    @builtins.property
    @jsii.member(jsii_name="vectorizeBindingsInput")
    def vectorize_bindings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionVectorizeBindings"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, "PagesProjectDeploymentConfigsProductionVectorizeBindings"]]], jsii.get(self, "vectorizeBindingsInput"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityDate")
    def compatibility_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compatibilityDate"))

    @compatibility_date.setter
    def compatibility_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0595cb8eff7f6b8d6e0bab4a75c9b33e7b8167dc670154c5d5ac8894ac886abf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compatibilityDate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlags")
    def compatibility_flags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibilityFlags"))

    @compatibility_flags.setter
    def compatibility_flags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37b984d2023ef3ff4c5e45625bd77fdd6b826d1556ca0e3b9d429b11e166f501)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compatibilityFlags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProduction]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProduction]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProduction]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35175326b28b2f7fe96351b76ce3c7430ea6837f3eac340d2f6d3655d52f0adf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionPlacement",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode"},
)
class PagesProjectDeploymentConfigsProductionPlacement:
    def __init__(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Placement mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mode PagesProject#mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aec8e4c3f8bfa53c4a1955e9bfe9e20820f77bb728d70de74030934857db4813)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Placement mode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#mode PagesProject#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionPlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionPlacementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionPlacementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0e9572e9e66468efd1475ce2144ef5ff5b8d52946c741f2474c687c2bd69811)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e179cbc78ff2c09a96e19e3bb1464363d545bd57f8a99aeed01dcc09d780548)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionPlacement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionPlacement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionPlacement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f413db01a77d01847bd5862148672f9415633528c4e134bc61a70ec56cd6249)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionQueueProducers",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class PagesProjectDeploymentConfigsProductionQueueProducers:
    def __init__(self, *, name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param name: Name of the Queue. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c84fdfc7aa011620bd4a12d560feb30b4e3b8f45e92982b14564845d7b17a96)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Queue.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionQueueProducers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionQueueProducersMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionQueueProducersMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__800f4f4f34f6688bb8f54bd4a2927c085ab50d127bbd36d4d172cf7fc682e422)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionQueueProducersOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f29ffe02722501b8c434e244dad73507d8b516bff88d8cb544045395354ad021)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionQueueProducersOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15b7c40a2e37daf28b4d9d920f0882df642eb8380c791da07f7c8d7e44b4ad45)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7441c67cefacb709bb5657109ef38040c1e79348e31670015832a1a2909df7a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionQueueProducers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionQueueProducers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionQueueProducers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a073283e314ce327bbe1171ddd4584c301935f30c21fb665cd1c43c73198ccb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionQueueProducersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionQueueProducersOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__861b7af8dc28a636229bbb66916fd70194a2f54450fd16ee6023e722e76594eb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63352a2f5dbe1cb14af9aa4ec28d296f54dc89ecf25aed5f96e46f9305adb718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionQueueProducers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionQueueProducers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionQueueProducers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2aa32ef721e329d25c855f6b68f71981b2a72395296d395af1f6538f1b20996)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionR2Buckets",
    jsii_struct_bases=[],
    name_mapping={"jurisdiction": "jurisdiction", "name": "name"},
)
class PagesProjectDeploymentConfigsProductionR2Buckets:
    def __init__(
        self,
        *,
        jurisdiction: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param jurisdiction: Jurisdiction of the R2 bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#jurisdiction PagesProject#jurisdiction}
        :param name: Name of the R2 bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f19762bc7176b61bad7d88fca71f6e0f7be0d3c76509709e52a41f628d7825d)
            check_type(argname="argument jurisdiction", value=jurisdiction, expected_type=type_hints["jurisdiction"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if jurisdiction is not None:
            self._values["jurisdiction"] = jurisdiction
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def jurisdiction(self) -> typing.Optional[builtins.str]:
        '''Jurisdiction of the R2 bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#jurisdiction PagesProject#jurisdiction}
        '''
        result = self._values.get("jurisdiction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the R2 bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#name PagesProject#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionR2Buckets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionR2BucketsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionR2BucketsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6079e18538ca57840fac12d99eab103247b0a23b05b41a10749c5e1f3ad0876b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionR2BucketsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e066522a01ac4c92a73eafdbab85546e35b235d78a12010a76a10e243e5d4df)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionR2BucketsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50aabe24386ccd4709a5a5ccc89c10850b5170b8136c8ddd1cf688cc0255bf88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6ed2077f662bf0aff713e86759a2f2c30d7409dbe91177a375c4f2d35d7443a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionR2Buckets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionR2Buckets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionR2Buckets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65e6199a7825dae22e548a1fef82bf117ed60dbfbfc339f89e5ffe6c87e99ca3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionR2BucketsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionR2BucketsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb6eb2508d786fe838937217aa5c73a29c4497b1cbb56147303b6b2b1bd29985)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetJurisdiction")
    def reset_jurisdiction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJurisdiction", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="jurisdictionInput")
    def jurisdiction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jurisdictionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="jurisdiction")
    def jurisdiction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jurisdiction"))

    @jurisdiction.setter
    def jurisdiction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3915b3d8079a44762494aeeb5cbc5e00812e9230dd6aa09b0d8a6ed1f67f9c09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jurisdiction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1d08f2df602744f4f9b6182cfda0f01bc6c115dbebecab388cb0b29509cd1fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionR2Buckets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionR2Buckets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionR2Buckets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__211a2428428f475923b00f7f3a0ecd53a229d9626dc32649b23301ed2eace904)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionServices",
    jsii_struct_bases=[],
    name_mapping={
        "entrypoint": "entrypoint",
        "environment": "environment",
        "service": "service",
    },
)
class PagesProjectDeploymentConfigsProductionServices:
    def __init__(
        self,
        *,
        entrypoint: typing.Optional[builtins.str] = None,
        environment: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param entrypoint: The entrypoint to bind to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#entrypoint PagesProject#entrypoint}
        :param environment: The Service environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#environment PagesProject#environment}
        :param service: The Service name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#service PagesProject#service}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a14b5302b6a9ac999f171372ec2f1bd605e62c310eb191195a119ee2d969e9cc)
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if environment is not None:
            self._values["environment"] = environment
        if service is not None:
            self._values["service"] = service

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''The entrypoint to bind to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#entrypoint PagesProject#entrypoint}
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(self) -> typing.Optional[builtins.str]:
        '''The Service environment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#environment PagesProject#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''The Service name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#service PagesProject#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionServicesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionServicesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__45ff8b0a2255a72b95b32929c1faf3f928dbe4576fd435a14decc1c79e56ff29)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionServicesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb6c8e9b3b45aa63c153503d703f2215c6ebf58da0433b4d9399dbf0599dfe80)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionServicesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2f5fc0f42a9adf26ce2d283d2c2fc340947a2f2249503dff20652eebdabbd43)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b3de1092f0f70bac16f50431222d0128a8e89ea8edfbb57989ea2649e978e6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionServices]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionServices]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionServices]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b29ab2fd1dbbf012137841cf5c54624af88f1142b99a262c6307664bc56733df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionServicesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionServicesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__716c1fb274c393d7122d995ad7ef7112f81620f30a085fb6c503ee7d85ca6a62)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetEntrypoint")
    def reset_entrypoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntrypoint", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetService")
    def reset_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetService", []))

    @builtins.property
    @jsii.member(jsii_name="entrypointInput")
    def entrypoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entrypointInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="entrypoint")
    def entrypoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entrypoint"))

    @entrypoint.setter
    def entrypoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38f80780ba15b892edfe00e64fbc206bf9709e5f39e5606f2e91ffdfcb399870)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entrypoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6798c6c7481382625c13e60840be339673ac9ed1d0361715fa630593b9ed52c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6afcbb0f890fcc0a99d6c7bddaea3a65172f77d00991e1d7812e346b06c47f35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionServices]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionServices]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionServices]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__450d5ab027219f0badf729f110b2757bc4e206b75e76fbc73bbbcdafec8fb830)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionVectorizeBindings",
    jsii_struct_bases=[],
    name_mapping={"index_name": "indexName"},
)
class PagesProjectDeploymentConfigsProductionVectorizeBindings:
    def __init__(self, *, index_name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param index_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#index_name PagesProject#index_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83b2cf2626f90957411a6f58f551c895f9ea7f6646bb90f72451edc128fbd3db)
            check_type(argname="argument index_name", value=index_name, expected_type=type_hints["index_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if index_name is not None:
            self._values["index_name"] = index_name

    @builtins.property
    def index_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#index_name PagesProject#index_name}.'''
        result = self._values.get("index_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectDeploymentConfigsProductionVectorizeBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectDeploymentConfigsProductionVectorizeBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionVectorizeBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__56cbffd212c113a2de920f9c00e42d4a0a3867021ee62fdfefb5675164256c9a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aeedc9b836636987bae1939e001bbfe8406d50f13415bca2076a03feb33e029)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92e67de0b8a9c4c4508140a8d24b6424792d7e10b8b4a78d3521d6d1b962fdb3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__589359711a5ac673657d00f7c451e98c1b1ca2c8a0a8363998080a5128f19789)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionVectorizeBindings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionVectorizeBindings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionVectorizeBindings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e366c181101defc2ed36d291d52249e87178dd8094a4055c2fb92ffb8ec431c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8053cc0748baf50c413dc04e3712020b9e8f68a310475cb243ec74bd7a8b757)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @jsii.member(jsii_name="resetIndexName")
    def reset_index_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexName", []))

    @builtins.property
    @jsii.member(jsii_name="indexNameInput")
    def index_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexNameInput"))

    @builtins.property
    @jsii.member(jsii_name="indexName")
    def index_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexName"))

    @index_name.setter
    def index_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83edce63d46582d91c1ba79ab9f6cae91d14a91cfcc0404a3b94cb6a329ffea3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indexName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionVectorizeBindings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionVectorizeBindings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionVectorizeBindings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e79f773935fdabd965451dee46ad61331f05979b355dd781e6a797443b8ef293)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeployment",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectLatestDeployment:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectLatestDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentBuildConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectLatestDeploymentBuildConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectLatestDeploymentBuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectLatestDeploymentBuildConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentBuildConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5885a4b65f98865c11ffbf5b5d9bbc9400cdd85d6b900088c00f771faa0c246b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="buildCaching")
    def build_caching(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "buildCaching"))

    @builtins.property
    @jsii.member(jsii_name="buildCommand")
    def build_command(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildCommand"))

    @builtins.property
    @jsii.member(jsii_name="destinationDir")
    def destination_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationDir"))

    @builtins.property
    @jsii.member(jsii_name="rootDir")
    def root_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootDir"))

    @builtins.property
    @jsii.member(jsii_name="webAnalyticsTag")
    def web_analytics_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webAnalyticsTag"))

    @builtins.property
    @jsii.member(jsii_name="webAnalyticsToken")
    def web_analytics_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webAnalyticsToken"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectLatestDeploymentBuildConfig]:
        return typing.cast(typing.Optional[PagesProjectLatestDeploymentBuildConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectLatestDeploymentBuildConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf488bd0caf867921d8f3d0750f120d3e8f30556b9fed0c3ebfcdfa46a124845)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentDeploymentTrigger",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectLatestDeploymentDeploymentTrigger:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectLatestDeploymentDeploymentTrigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentDeploymentTriggerMetadata",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectLatestDeploymentDeploymentTriggerMetadata:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectLatestDeploymentDeploymentTriggerMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e4f11d6a1f28f1b04d3660735d5264cddeb40e8557e67f34244c8df9d808d556)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="branch")
    def branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branch"))

    @builtins.property
    @jsii.member(jsii_name="commitHash")
    def commit_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commitHash"))

    @builtins.property
    @jsii.member(jsii_name="commitMessage")
    def commit_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commitMessage"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectLatestDeploymentDeploymentTriggerMetadata]:
        return typing.cast(typing.Optional[PagesProjectLatestDeploymentDeploymentTriggerMetadata], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectLatestDeploymentDeploymentTriggerMetadata],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d400938250a81c27e8da7804065d19738d6df915023f395e1c18516b6f84ab3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectLatestDeploymentDeploymentTriggerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentDeploymentTriggerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__058ed9b8cfcb6fcaa2810c686ab8fa02630fd0f97e1d606f64a610105c057297)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(
        self,
    ) -> PagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference:
        return typing.cast(PagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference, jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectLatestDeploymentDeploymentTrigger]:
        return typing.cast(typing.Optional[PagesProjectLatestDeploymentDeploymentTrigger], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectLatestDeploymentDeploymentTrigger],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdee5544cab4ab50090f74df9b2194d2ecfd0413dec61e9540084caed442628a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentEnvVars",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectLatestDeploymentEnvVars:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectLatestDeploymentEnvVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectLatestDeploymentEnvVarsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentEnvVarsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0241bedb22c0847cd74050a1bb6174ae848c2869a0886b291ced4ebfb54f939)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "PagesProjectLatestDeploymentEnvVarsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0bec8b019b90be1db55ed20f650ae401b80e73c61b1bcd574feadc9cae73c0a)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("PagesProjectLatestDeploymentEnvVarsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db6e1f51a898652c8ba4ba1c89d9fa4fc9520d639a05571851ffa516977d932d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__efea81c5b9b821721e9452c1b661abda626e310c8a0b584ed71c828423745388)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class PagesProjectLatestDeploymentEnvVarsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentEnvVarsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_key: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_key: the key of this item in the map.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b9438c1cf4f2b56e124ceb7bb48163431e9e5370d17ae013451e3083045ce75)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PagesProjectLatestDeploymentEnvVars]:
        return typing.cast(typing.Optional[PagesProjectLatestDeploymentEnvVars], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectLatestDeploymentEnvVars],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc223363434d59fc1799d16c3eb8b90d4993bf1505522262aea859dc96c56828)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentLatestStage",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectLatestDeploymentLatestStage:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectLatestDeploymentLatestStage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectLatestDeploymentLatestStageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentLatestStageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1382a20c1b2c72a27dd7ca33bf3eba2ad11e804208f300b833b779be34511b67)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="endedOn")
    def ended_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endedOn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="startedOn")
    def started_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startedOn"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectLatestDeploymentLatestStage]:
        return typing.cast(typing.Optional[PagesProjectLatestDeploymentLatestStage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectLatestDeploymentLatestStage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cea34f29247f5670f770ac9d4b0ef383eca786d2119a5e59402e06869b36ebc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectLatestDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdb850933264b2c7575638c5de50da52883ad88370b46525f6499e9803908985)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "aliases"))

    @builtins.property
    @jsii.member(jsii_name="buildConfig")
    def build_config(self) -> PagesProjectLatestDeploymentBuildConfigOutputReference:
        return typing.cast(PagesProjectLatestDeploymentBuildConfigOutputReference, jsii.get(self, "buildConfig"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="deploymentTrigger")
    def deployment_trigger(
        self,
    ) -> PagesProjectLatestDeploymentDeploymentTriggerOutputReference:
        return typing.cast(PagesProjectLatestDeploymentDeploymentTriggerOutputReference, jsii.get(self, "deploymentTrigger"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @builtins.property
    @jsii.member(jsii_name="envVars")
    def env_vars(self) -> PagesProjectLatestDeploymentEnvVarsMap:
        return typing.cast(PagesProjectLatestDeploymentEnvVarsMap, jsii.get(self, "envVars"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="isSkipped")
    def is_skipped(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "isSkipped"))

    @builtins.property
    @jsii.member(jsii_name="latestStage")
    def latest_stage(self) -> PagesProjectLatestDeploymentLatestStageOutputReference:
        return typing.cast(PagesProjectLatestDeploymentLatestStageOutputReference, jsii.get(self, "latestStage"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @builtins.property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectName"))

    @builtins.property
    @jsii.member(jsii_name="shortId")
    def short_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shortId"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "PagesProjectLatestDeploymentSourceOutputReference":
        return typing.cast("PagesProjectLatestDeploymentSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> "PagesProjectLatestDeploymentStagesList":
        return typing.cast("PagesProjectLatestDeploymentStagesList", jsii.get(self, "stages"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PagesProjectLatestDeployment]:
        return typing.cast(typing.Optional[PagesProjectLatestDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectLatestDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3d583a06eb94b28258fdf72a44a54da2d31ddf08885c6f85c1f461b7ea844c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentSource",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectLatestDeploymentSource:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectLatestDeploymentSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentSourceConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectLatestDeploymentSourceConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectLatestDeploymentSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectLatestDeploymentSourceConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentSourceConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__34b46ff84bfa937bef05496d928475389265f98f92f208fb00adae54e6785e5b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="deploymentsEnabled")
    def deployments_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "deploymentsEnabled"))

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property
    @jsii.member(jsii_name="pathExcludes")
    def path_excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pathExcludes"))

    @builtins.property
    @jsii.member(jsii_name="pathIncludes")
    def path_includes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pathIncludes"))

    @builtins.property
    @jsii.member(jsii_name="prCommentsEnabled")
    def pr_comments_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "prCommentsEnabled"))

    @builtins.property
    @jsii.member(jsii_name="previewBranchExcludes")
    def preview_branch_excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "previewBranchExcludes"))

    @builtins.property
    @jsii.member(jsii_name="previewBranchIncludes")
    def preview_branch_includes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "previewBranchIncludes"))

    @builtins.property
    @jsii.member(jsii_name="previewDeploymentSetting")
    def preview_deployment_setting(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "previewDeploymentSetting"))

    @builtins.property
    @jsii.member(jsii_name="productionBranch")
    def production_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "productionBranch"))

    @builtins.property
    @jsii.member(jsii_name="productionDeploymentsEnabled")
    def production_deployments_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "productionDeploymentsEnabled"))

    @builtins.property
    @jsii.member(jsii_name="repoName")
    def repo_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PagesProjectLatestDeploymentSourceConfig]:
        return typing.cast(typing.Optional[PagesProjectLatestDeploymentSourceConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectLatestDeploymentSourceConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b47cbb6a313d01413afcef64df57782ed9b3ea94c4d0356ea95ca113c7025c7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectLatestDeploymentSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc7f2c6273455532dac411b1bb411a23a75d46a23fe867c0579a8ae7645ae995)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> PagesProjectLatestDeploymentSourceConfigOutputReference:
        return typing.cast(PagesProjectLatestDeploymentSourceConfigOutputReference, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PagesProjectLatestDeploymentSource]:
        return typing.cast(typing.Optional[PagesProjectLatestDeploymentSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectLatestDeploymentSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__175ed88208250c1a097ff4d254e78cef03ea00b5a7e3ab21e3df683fee825c54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentStages",
    jsii_struct_bases=[],
    name_mapping={},
)
class PagesProjectLatestDeploymentStages:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectLatestDeploymentStages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectLatestDeploymentStagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentStagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3df0d71745d0878db9134a2b03a53cbba5febba9c4f0d5f8bd7b4c011cd1e4f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "PagesProjectLatestDeploymentStagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__834560b42f5a5a49a7e511155648c095edac30a05535fe58fb8a6761f1dbfcd3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PagesProjectLatestDeploymentStagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__777139c5a64fc43f8da2323be008cad574b2ab10e9031dafa4f14800502dcf4e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ff4ef407272931faa97ee3744db1712b184c6b5ff185132211203daadfae34c2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__81f5f728c608b85a4f1240fe5d165673862dc87a8c227f8bc75db35f6776f33b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class PagesProjectLatestDeploymentStagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectLatestDeploymentStagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ecc9fa36cfb9d4cb8cdbfdbf913db30302e166d74e86ad1b96f43c359862f25)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="endedOn")
    def ended_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endedOn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="startedOn")
    def started_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startedOn"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PagesProjectLatestDeploymentStages]:
        return typing.cast(typing.Optional[PagesProjectLatestDeploymentStages], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PagesProjectLatestDeploymentStages],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91f425f308418097b60fa150c05eb382c8119760f80972ce68016070dfe653a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectSource",
    jsii_struct_bases=[],
    name_mapping={"config": "config", "type": "type"},
)
class PagesProjectSource:
    def __init__(
        self,
        *,
        config: typing.Optional[typing.Union["PagesProjectSourceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#config PagesProject#config}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#type PagesProject#type}.
        '''
        if isinstance(config, dict):
            config = PagesProjectSourceConfig(**config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1a350c38bdfe501fc470a31a735e7a18ea66fce4461f5ea5e2cc2002d90fe57)
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config is not None:
            self._values["config"] = config
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def config(self) -> typing.Optional["PagesProjectSourceConfig"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#config PagesProject#config}.'''
        result = self._values.get("config")
        return typing.cast(typing.Optional["PagesProjectSourceConfig"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#type PagesProject#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectSourceConfig",
    jsii_struct_bases=[],
    name_mapping={
        "deployments_enabled": "deploymentsEnabled",
        "owner": "owner",
        "path_excludes": "pathExcludes",
        "path_includes": "pathIncludes",
        "pr_comments_enabled": "prCommentsEnabled",
        "preview_branch_excludes": "previewBranchExcludes",
        "preview_branch_includes": "previewBranchIncludes",
        "preview_deployment_setting": "previewDeploymentSetting",
        "production_branch": "productionBranch",
        "production_deployments_enabled": "productionDeploymentsEnabled",
        "repo_name": "repoName",
    },
)
class PagesProjectSourceConfig:
    def __init__(
        self,
        *,
        deployments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        owner: typing.Optional[builtins.str] = None,
        path_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        path_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        pr_comments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        preview_branch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        preview_branch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        preview_deployment_setting: typing.Optional[builtins.str] = None,
        production_branch: typing.Optional[builtins.str] = None,
        production_deployments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        repo_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployments_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#deployments_enabled PagesProject#deployments_enabled}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#owner PagesProject#owner}.
        :param path_excludes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#path_excludes PagesProject#path_excludes}.
        :param path_includes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#path_includes PagesProject#path_includes}.
        :param pr_comments_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#pr_comments_enabled PagesProject#pr_comments_enabled}.
        :param preview_branch_excludes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview_branch_excludes PagesProject#preview_branch_excludes}.
        :param preview_branch_includes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview_branch_includes PagesProject#preview_branch_includes}.
        :param preview_deployment_setting: Available values: "all", "none", "custom". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview_deployment_setting PagesProject#preview_deployment_setting}
        :param production_branch: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production_branch PagesProject#production_branch}.
        :param production_deployments_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production_deployments_enabled PagesProject#production_deployments_enabled}.
        :param repo_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#repo_name PagesProject#repo_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d39510fd2d65da87e37b9b4d6793fb57e2ac525a07c5a2da44593f385253a285)
            check_type(argname="argument deployments_enabled", value=deployments_enabled, expected_type=type_hints["deployments_enabled"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument path_excludes", value=path_excludes, expected_type=type_hints["path_excludes"])
            check_type(argname="argument path_includes", value=path_includes, expected_type=type_hints["path_includes"])
            check_type(argname="argument pr_comments_enabled", value=pr_comments_enabled, expected_type=type_hints["pr_comments_enabled"])
            check_type(argname="argument preview_branch_excludes", value=preview_branch_excludes, expected_type=type_hints["preview_branch_excludes"])
            check_type(argname="argument preview_branch_includes", value=preview_branch_includes, expected_type=type_hints["preview_branch_includes"])
            check_type(argname="argument preview_deployment_setting", value=preview_deployment_setting, expected_type=type_hints["preview_deployment_setting"])
            check_type(argname="argument production_branch", value=production_branch, expected_type=type_hints["production_branch"])
            check_type(argname="argument production_deployments_enabled", value=production_deployments_enabled, expected_type=type_hints["production_deployments_enabled"])
            check_type(argname="argument repo_name", value=repo_name, expected_type=type_hints["repo_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deployments_enabled is not None:
            self._values["deployments_enabled"] = deployments_enabled
        if owner is not None:
            self._values["owner"] = owner
        if path_excludes is not None:
            self._values["path_excludes"] = path_excludes
        if path_includes is not None:
            self._values["path_includes"] = path_includes
        if pr_comments_enabled is not None:
            self._values["pr_comments_enabled"] = pr_comments_enabled
        if preview_branch_excludes is not None:
            self._values["preview_branch_excludes"] = preview_branch_excludes
        if preview_branch_includes is not None:
            self._values["preview_branch_includes"] = preview_branch_includes
        if preview_deployment_setting is not None:
            self._values["preview_deployment_setting"] = preview_deployment_setting
        if production_branch is not None:
            self._values["production_branch"] = production_branch
        if production_deployments_enabled is not None:
            self._values["production_deployments_enabled"] = production_deployments_enabled
        if repo_name is not None:
            self._values["repo_name"] = repo_name

    @builtins.property
    def deployments_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#deployments_enabled PagesProject#deployments_enabled}.'''
        result = self._values.get("deployments_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#owner PagesProject#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_excludes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#path_excludes PagesProject#path_excludes}.'''
        result = self._values.get("path_excludes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def path_includes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#path_includes PagesProject#path_includes}.'''
        result = self._values.get("path_includes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pr_comments_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#pr_comments_enabled PagesProject#pr_comments_enabled}.'''
        result = self._values.get("pr_comments_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def preview_branch_excludes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview_branch_excludes PagesProject#preview_branch_excludes}.'''
        result = self._values.get("preview_branch_excludes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def preview_branch_includes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview_branch_includes PagesProject#preview_branch_includes}.'''
        result = self._values.get("preview_branch_includes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def preview_deployment_setting(self) -> typing.Optional[builtins.str]:
        '''Available values: "all", "none", "custom".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview_deployment_setting PagesProject#preview_deployment_setting}
        '''
        result = self._values.get("preview_deployment_setting")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def production_branch(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production_branch PagesProject#production_branch}.'''
        result = self._values.get("production_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def production_deployments_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production_deployments_enabled PagesProject#production_deployments_enabled}.'''
        result = self._values.get("production_deployments_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def repo_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#repo_name PagesProject#repo_name}.'''
        result = self._values.get("repo_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PagesProjectSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PagesProjectSourceConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectSourceConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6049651f4254f7dec38652d77a1f1e865a9d1754ffdcd26b2a942a078f6ec45)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDeploymentsEnabled")
    def reset_deployments_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentsEnabled", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="resetPathExcludes")
    def reset_path_excludes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathExcludes", []))

    @jsii.member(jsii_name="resetPathIncludes")
    def reset_path_includes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathIncludes", []))

    @jsii.member(jsii_name="resetPrCommentsEnabled")
    def reset_pr_comments_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrCommentsEnabled", []))

    @jsii.member(jsii_name="resetPreviewBranchExcludes")
    def reset_preview_branch_excludes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreviewBranchExcludes", []))

    @jsii.member(jsii_name="resetPreviewBranchIncludes")
    def reset_preview_branch_includes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreviewBranchIncludes", []))

    @jsii.member(jsii_name="resetPreviewDeploymentSetting")
    def reset_preview_deployment_setting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreviewDeploymentSetting", []))

    @jsii.member(jsii_name="resetProductionBranch")
    def reset_production_branch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProductionBranch", []))

    @jsii.member(jsii_name="resetProductionDeploymentsEnabled")
    def reset_production_deployments_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProductionDeploymentsEnabled", []))

    @jsii.member(jsii_name="resetRepoName")
    def reset_repo_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepoName", []))

    @builtins.property
    @jsii.member(jsii_name="deploymentsEnabledInput")
    def deployments_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deploymentsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property
    @jsii.member(jsii_name="pathExcludesInput")
    def path_excludes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pathExcludesInput"))

    @builtins.property
    @jsii.member(jsii_name="pathIncludesInput")
    def path_includes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pathIncludesInput"))

    @builtins.property
    @jsii.member(jsii_name="prCommentsEnabledInput")
    def pr_comments_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "prCommentsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="previewBranchExcludesInput")
    def preview_branch_excludes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "previewBranchExcludesInput"))

    @builtins.property
    @jsii.member(jsii_name="previewBranchIncludesInput")
    def preview_branch_includes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "previewBranchIncludesInput"))

    @builtins.property
    @jsii.member(jsii_name="previewDeploymentSettingInput")
    def preview_deployment_setting_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "previewDeploymentSettingInput"))

    @builtins.property
    @jsii.member(jsii_name="productionBranchInput")
    def production_branch_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "productionBranchInput"))

    @builtins.property
    @jsii.member(jsii_name="productionDeploymentsEnabledInput")
    def production_deployments_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "productionDeploymentsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="repoNameInput")
    def repo_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repoNameInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentsEnabled")
    def deployments_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deploymentsEnabled"))

    @deployments_enabled.setter
    def deployments_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a17a6b5a6165242dbb5797b2b5d2df31416edc2f5f28e9245480e0bb6c5fa69f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d721940abeacc9462b79b6f086f6dbbf1d7454721a984d5187109d1ef9781d6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathExcludes")
    def path_excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pathExcludes"))

    @path_excludes.setter
    def path_excludes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d9a3da4909a953d14dff9220025ad5a3cf3337695197a53026a2ce693a09ecc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathExcludes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathIncludes")
    def path_includes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pathIncludes"))

    @path_includes.setter
    def path_includes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d7126c01cfd6f5d13cef7fb1a46c50c6fe272a34989f6348c6f1d82147ac854)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathIncludes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prCommentsEnabled")
    def pr_comments_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "prCommentsEnabled"))

    @pr_comments_enabled.setter
    def pr_comments_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f41d919260e3ac5408ba48074e89b050cd52867bc3825b78a1bf50163ad428e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prCommentsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="previewBranchExcludes")
    def preview_branch_excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "previewBranchExcludes"))

    @preview_branch_excludes.setter
    def preview_branch_excludes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba229809a5fe0048e0ce26e352e0de0bcf8088b4f24001998c7080c4dc257d54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "previewBranchExcludes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="previewBranchIncludes")
    def preview_branch_includes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "previewBranchIncludes"))

    @preview_branch_includes.setter
    def preview_branch_includes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2558db516c416a760e87375b1f8367a6f5e8ebbe22a7dacd81184c2847e69a26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "previewBranchIncludes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="previewDeploymentSetting")
    def preview_deployment_setting(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "previewDeploymentSetting"))

    @preview_deployment_setting.setter
    def preview_deployment_setting(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__919ee77dafbac4b4c1b808b5947dc7d331dd0a3260f97bd376b0a602679c1e67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "previewDeploymentSetting", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="productionBranch")
    def production_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "productionBranch"))

    @production_branch.setter
    def production_branch(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8aa3d224dfc5c35aa7075d25ba015b53024e435701789a7bcf699dedb9a84cee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "productionBranch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="productionDeploymentsEnabled")
    def production_deployments_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "productionDeploymentsEnabled"))

    @production_deployments_enabled.setter
    def production_deployments_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc0226d6ca16a3f3aa405f465acaff22779641c144d7b1581587f4a6fb8f2e2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "productionDeploymentsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repoName")
    def repo_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoName"))

    @repo_name.setter
    def repo_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72212d6f12c26a75e6ed310b2afc8cae7bc0cbfe25fda3fa46def92734f10257)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repoName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSourceConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSourceConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSourceConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03af7feda072e1d2e219e793730f3f542b45975a2d8c485b137295111325a197)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PagesProjectSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.pagesProject.PagesProjectSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6379b8db0604424167bff638ef02c874d65dcbf77b00e94de1c3401ab4859708)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        deployments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        owner: typing.Optional[builtins.str] = None,
        path_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        path_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        pr_comments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        preview_branch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        preview_branch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        preview_deployment_setting: typing.Optional[builtins.str] = None,
        production_branch: typing.Optional[builtins.str] = None,
        production_deployments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        repo_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployments_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#deployments_enabled PagesProject#deployments_enabled}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#owner PagesProject#owner}.
        :param path_excludes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#path_excludes PagesProject#path_excludes}.
        :param path_includes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#path_includes PagesProject#path_includes}.
        :param pr_comments_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#pr_comments_enabled PagesProject#pr_comments_enabled}.
        :param preview_branch_excludes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview_branch_excludes PagesProject#preview_branch_excludes}.
        :param preview_branch_includes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview_branch_includes PagesProject#preview_branch_includes}.
        :param preview_deployment_setting: Available values: "all", "none", "custom". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#preview_deployment_setting PagesProject#preview_deployment_setting}
        :param production_branch: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production_branch PagesProject#production_branch}.
        :param production_deployments_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#production_deployments_enabled PagesProject#production_deployments_enabled}.
        :param repo_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/pages_project#repo_name PagesProject#repo_name}.
        '''
        value = PagesProjectSourceConfig(
            deployments_enabled=deployments_enabled,
            owner=owner,
            path_excludes=path_excludes,
            path_includes=path_includes,
            pr_comments_enabled=pr_comments_enabled,
            preview_branch_excludes=preview_branch_excludes,
            preview_branch_includes=preview_branch_includes,
            preview_deployment_setting=preview_deployment_setting,
            production_branch=production_branch,
            production_deployments_enabled=production_deployments_enabled,
            repo_name=repo_name,
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> PagesProjectSourceConfigOutputReference:
        return typing.cast(PagesProjectSourceConfigOutputReference, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSourceConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSourceConfig]], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2374ff2f25e189caef442453f610fe93ddcfdce036acafa4b58f1ed30940fda0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ee731c9c2f91c73570681f8265ad04919cb4f0058b752c89b6b5136784fa3a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "PagesProject",
    "PagesProjectBuildConfig",
    "PagesProjectBuildConfigOutputReference",
    "PagesProjectCanonicalDeployment",
    "PagesProjectCanonicalDeploymentBuildConfig",
    "PagesProjectCanonicalDeploymentBuildConfigOutputReference",
    "PagesProjectCanonicalDeploymentDeploymentTrigger",
    "PagesProjectCanonicalDeploymentDeploymentTriggerMetadata",
    "PagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference",
    "PagesProjectCanonicalDeploymentDeploymentTriggerOutputReference",
    "PagesProjectCanonicalDeploymentEnvVars",
    "PagesProjectCanonicalDeploymentEnvVarsMap",
    "PagesProjectCanonicalDeploymentEnvVarsOutputReference",
    "PagesProjectCanonicalDeploymentLatestStage",
    "PagesProjectCanonicalDeploymentLatestStageOutputReference",
    "PagesProjectCanonicalDeploymentOutputReference",
    "PagesProjectCanonicalDeploymentSource",
    "PagesProjectCanonicalDeploymentSourceConfig",
    "PagesProjectCanonicalDeploymentSourceConfigOutputReference",
    "PagesProjectCanonicalDeploymentSourceOutputReference",
    "PagesProjectCanonicalDeploymentStages",
    "PagesProjectCanonicalDeploymentStagesList",
    "PagesProjectCanonicalDeploymentStagesOutputReference",
    "PagesProjectConfig",
    "PagesProjectDeploymentConfigs",
    "PagesProjectDeploymentConfigsOutputReference",
    "PagesProjectDeploymentConfigsPreview",
    "PagesProjectDeploymentConfigsPreviewAiBindings",
    "PagesProjectDeploymentConfigsPreviewAiBindingsMap",
    "PagesProjectDeploymentConfigsPreviewAiBindingsOutputReference",
    "PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets",
    "PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap",
    "PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference",
    "PagesProjectDeploymentConfigsPreviewBrowsers",
    "PagesProjectDeploymentConfigsPreviewBrowsersMap",
    "PagesProjectDeploymentConfigsPreviewBrowsersOutputReference",
    "PagesProjectDeploymentConfigsPreviewD1Databases",
    "PagesProjectDeploymentConfigsPreviewD1DatabasesMap",
    "PagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference",
    "PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces",
    "PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap",
    "PagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference",
    "PagesProjectDeploymentConfigsPreviewEnvVars",
    "PagesProjectDeploymentConfigsPreviewEnvVarsMap",
    "PagesProjectDeploymentConfigsPreviewEnvVarsOutputReference",
    "PagesProjectDeploymentConfigsPreviewHyperdriveBindings",
    "PagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap",
    "PagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference",
    "PagesProjectDeploymentConfigsPreviewKvNamespaces",
    "PagesProjectDeploymentConfigsPreviewKvNamespacesMap",
    "PagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference",
    "PagesProjectDeploymentConfigsPreviewMtlsCertificates",
    "PagesProjectDeploymentConfigsPreviewMtlsCertificatesMap",
    "PagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference",
    "PagesProjectDeploymentConfigsPreviewOutputReference",
    "PagesProjectDeploymentConfigsPreviewPlacement",
    "PagesProjectDeploymentConfigsPreviewPlacementOutputReference",
    "PagesProjectDeploymentConfigsPreviewQueueProducers",
    "PagesProjectDeploymentConfigsPreviewQueueProducersMap",
    "PagesProjectDeploymentConfigsPreviewQueueProducersOutputReference",
    "PagesProjectDeploymentConfigsPreviewR2Buckets",
    "PagesProjectDeploymentConfigsPreviewR2BucketsMap",
    "PagesProjectDeploymentConfigsPreviewR2BucketsOutputReference",
    "PagesProjectDeploymentConfigsPreviewServices",
    "PagesProjectDeploymentConfigsPreviewServicesMap",
    "PagesProjectDeploymentConfigsPreviewServicesOutputReference",
    "PagesProjectDeploymentConfigsPreviewVectorizeBindings",
    "PagesProjectDeploymentConfigsPreviewVectorizeBindingsMap",
    "PagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference",
    "PagesProjectDeploymentConfigsProduction",
    "PagesProjectDeploymentConfigsProductionAiBindings",
    "PagesProjectDeploymentConfigsProductionAiBindingsMap",
    "PagesProjectDeploymentConfigsProductionAiBindingsOutputReference",
    "PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets",
    "PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap",
    "PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference",
    "PagesProjectDeploymentConfigsProductionBrowsers",
    "PagesProjectDeploymentConfigsProductionBrowsersMap",
    "PagesProjectDeploymentConfigsProductionBrowsersOutputReference",
    "PagesProjectDeploymentConfigsProductionD1Databases",
    "PagesProjectDeploymentConfigsProductionD1DatabasesMap",
    "PagesProjectDeploymentConfigsProductionD1DatabasesOutputReference",
    "PagesProjectDeploymentConfigsProductionDurableObjectNamespaces",
    "PagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap",
    "PagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference",
    "PagesProjectDeploymentConfigsProductionEnvVars",
    "PagesProjectDeploymentConfigsProductionEnvVarsMap",
    "PagesProjectDeploymentConfigsProductionEnvVarsOutputReference",
    "PagesProjectDeploymentConfigsProductionHyperdriveBindings",
    "PagesProjectDeploymentConfigsProductionHyperdriveBindingsMap",
    "PagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference",
    "PagesProjectDeploymentConfigsProductionKvNamespaces",
    "PagesProjectDeploymentConfigsProductionKvNamespacesMap",
    "PagesProjectDeploymentConfigsProductionKvNamespacesOutputReference",
    "PagesProjectDeploymentConfigsProductionMtlsCertificates",
    "PagesProjectDeploymentConfigsProductionMtlsCertificatesMap",
    "PagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference",
    "PagesProjectDeploymentConfigsProductionOutputReference",
    "PagesProjectDeploymentConfigsProductionPlacement",
    "PagesProjectDeploymentConfigsProductionPlacementOutputReference",
    "PagesProjectDeploymentConfigsProductionQueueProducers",
    "PagesProjectDeploymentConfigsProductionQueueProducersMap",
    "PagesProjectDeploymentConfigsProductionQueueProducersOutputReference",
    "PagesProjectDeploymentConfigsProductionR2Buckets",
    "PagesProjectDeploymentConfigsProductionR2BucketsMap",
    "PagesProjectDeploymentConfigsProductionR2BucketsOutputReference",
    "PagesProjectDeploymentConfigsProductionServices",
    "PagesProjectDeploymentConfigsProductionServicesMap",
    "PagesProjectDeploymentConfigsProductionServicesOutputReference",
    "PagesProjectDeploymentConfigsProductionVectorizeBindings",
    "PagesProjectDeploymentConfigsProductionVectorizeBindingsMap",
    "PagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference",
    "PagesProjectLatestDeployment",
    "PagesProjectLatestDeploymentBuildConfig",
    "PagesProjectLatestDeploymentBuildConfigOutputReference",
    "PagesProjectLatestDeploymentDeploymentTrigger",
    "PagesProjectLatestDeploymentDeploymentTriggerMetadata",
    "PagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference",
    "PagesProjectLatestDeploymentDeploymentTriggerOutputReference",
    "PagesProjectLatestDeploymentEnvVars",
    "PagesProjectLatestDeploymentEnvVarsMap",
    "PagesProjectLatestDeploymentEnvVarsOutputReference",
    "PagesProjectLatestDeploymentLatestStage",
    "PagesProjectLatestDeploymentLatestStageOutputReference",
    "PagesProjectLatestDeploymentOutputReference",
    "PagesProjectLatestDeploymentSource",
    "PagesProjectLatestDeploymentSourceConfig",
    "PagesProjectLatestDeploymentSourceConfigOutputReference",
    "PagesProjectLatestDeploymentSourceOutputReference",
    "PagesProjectLatestDeploymentStages",
    "PagesProjectLatestDeploymentStagesList",
    "PagesProjectLatestDeploymentStagesOutputReference",
    "PagesProjectSource",
    "PagesProjectSourceConfig",
    "PagesProjectSourceConfigOutputReference",
    "PagesProjectSourceOutputReference",
]

publication.publish()

def _typecheckingstub__32c8bd3ba18e0650df846b2d2e37dfef810ae73f984dcc34617f1efd60225d71(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    name: builtins.str,
    build_config: typing.Optional[typing.Union[PagesProjectBuildConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    deployment_configs: typing.Optional[typing.Union[PagesProjectDeploymentConfigs, typing.Dict[builtins.str, typing.Any]]] = None,
    production_branch: typing.Optional[builtins.str] = None,
    source: typing.Optional[typing.Union[PagesProjectSource, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__1dacbc7e3bfed7ff93406fa665eba6d271e30ed7a3fbcc183f148159745f21a2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e25d24d3b5e4450d1d1b773c3f5902e9faec8325dd51fa04efa4d99ffdce1420(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcae619adfa6aa5276e7477d32740b0f98c950ea03e86467e16d2f2afa4af2f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6748f02b291e15157b0dfdadc8ffde3dfabf3d9c406daafd12d4c241863b058c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2ddb1767df2790103b319dd95302c1ef2dcfeee4080c9df13a6923c7f947ef6(
    *,
    build_caching: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    build_command: typing.Optional[builtins.str] = None,
    destination_dir: typing.Optional[builtins.str] = None,
    root_dir: typing.Optional[builtins.str] = None,
    web_analytics_tag: typing.Optional[builtins.str] = None,
    web_analytics_token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a960c98b224c6cf61805a912db83a0d50aa489fd1ddff0a1969c14872ac349d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78a34e8873fac06a15386e22b65c8a2fe110ba2fbcb68fa0e2079b6dcf081b55(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd7be84ce85b9c62ce32b5dc2e25735ef178a42ae6c4e9c1119dfd8daf83ded4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5424df13dad2e1fd5edffc5ddcc1e83930ce5a31274ecb5d8574ef5c73362c58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4625699986a8ee4c0655efa7eeabca037c039abe2c03b7d7bcf3b7602be7d76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b3a0913a4c6ccf4b97d8ec54a927ea9f9838b946db5e9009609ac0ce769a21a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e76185d7b63462d674120a4c7e55a708a813fbeeaeb708206c04147ae22731b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e2551caeefe9277427f352093f8384ff5673336bce649412aec8f7afec41509(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectBuildConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fab6fb69a586f514abfc6672e7abdb50b431450a1cb59d4b5c273fb9b303d916(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b6544be7cdc35b767f75636387bc8ef775f67ee4d042a1a62cea6bf2c12defd(
    value: typing.Optional[PagesProjectCanonicalDeploymentBuildConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b279c8df05ed387eb05716851878de7e78a3b8ce85e8419d5e42b398c26d2eaa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__314b7e3f0a32ecbd526f71824c68b61bb1cda87d0bf22800e917acd8a991b8f4(
    value: typing.Optional[PagesProjectCanonicalDeploymentDeploymentTriggerMetadata],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb357e9e029f679e3526dcca18296c57f500f9e468c84048e23715c9f2bf1405(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dce8ce9a1217d10a7946098e47f11c56f07e86676700420b1f9655d58b6ca7a(
    value: typing.Optional[PagesProjectCanonicalDeploymentDeploymentTrigger],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbb920126cc725c7102ee52d446413ca91cf3574a7d3e0fb6a76b2922a74dec1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bb47cc9773d0a73ead31a3f02d7e748b2a9bda8fb0b94a7cc3e97d8dd40ca6c(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aed9a8e8dba0511ce3e733ae21581d11ba999088b3e9c17fd596c2a6fd44546b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29eb05adbf32944bbb6d0aba00c4570fcee1e2f3e262754248077dff428e646b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__501854349c1906b7982335bb299a7f4812a0869f6ea625be339d44c088c7778e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08d822ca4a00abac12c6f3cde6f521d6e0356c45272f076497de130558cd0488(
    value: typing.Optional[PagesProjectCanonicalDeploymentEnvVars],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a774369c7f1e6f663dd126fbf9a5723bc2803e04d50b6668172fef2a36abc2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__563792ff5844edac35512cc5333a246564f688edd47b20ca3d2fbf0a35ca4a3a(
    value: typing.Optional[PagesProjectCanonicalDeploymentLatestStage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf3fe4d6f664c28e7546705dfb53608a637c0d3378c96b493a52061993f259df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41aa1031f49109411801d151b4bf6c3ffda14f2cc861bfcc27da774edebb771a(
    value: typing.Optional[PagesProjectCanonicalDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba84a37a6cd59ce90562c2b9c9c9f27f6f68c850f60d538fbe58029f54312b6a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab5cafd6cf45359135425a491f331e24bee341f61d8d66ebe93faad7a8265f62(
    value: typing.Optional[PagesProjectCanonicalDeploymentSourceConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28d5251f27d36526665548ca74b9ba0465b443fcbe959a1d2fc74dbc08a9d812(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0190d8358654d7451047fa6dc8144c09de7e1a626ae3993beae4be619f8d1dc(
    value: typing.Optional[PagesProjectCanonicalDeploymentSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9784a4c312ac28de6d1c63d63e04e5b734f56bdd8412609b58d912baaa2fe51(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbc8efbf48f82016669a367554d9b6f734ed3d3d04f755365d1dbb36619a4924(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6955d640b54dbfed37ce66817e96f64a3d04008b473c4662a39e8732c9c27bd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c04edebc76cd1d2c3ee3c6dd3d167c1ab84a73d48a614aac760808366d89a15(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0021535833e3759c981cd8644e56d3443d568f0fd1c5ecfe16d018a31602987a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdc9fccdffcd6ee7d9d16c50fb135dfc410f6e40163229f1f7e0f17a12572156(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4a71ca73107bcd82c0c34f81799ac40e3f3a094a3ccf11625f0082eae044715(
    value: typing.Optional[PagesProjectCanonicalDeploymentStages],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0094d200e654f606607f96b58892accd8ce9d503242b6f5c7d06a2ae11897e53(
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
    build_config: typing.Optional[typing.Union[PagesProjectBuildConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    deployment_configs: typing.Optional[typing.Union[PagesProjectDeploymentConfigs, typing.Dict[builtins.str, typing.Any]]] = None,
    production_branch: typing.Optional[builtins.str] = None,
    source: typing.Optional[typing.Union[PagesProjectSource, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7823fdc9b0a09eac3b8f24725ee9162c17ddca7ff78a36cba5175fe819813991(
    *,
    preview: typing.Optional[typing.Union[PagesProjectDeploymentConfigsPreview, typing.Dict[builtins.str, typing.Any]]] = None,
    production: typing.Optional[typing.Union[PagesProjectDeploymentConfigsProduction, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bfb360ea6a026f85cc04fa09830e4f97ca1f925ad9c49edc82b2bf67135a9d1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bda509eaf75eb329c80e5e350ce8997a151563c736cfdcf50a669a795ffaa07(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74e03862ac074ef15f724d9cc40bca42af7e9390d107765128d30dfa4a96e2ff(
    *,
    ai_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewAiBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    analytics_engine_datasets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets, typing.Dict[builtins.str, typing.Any]]]]] = None,
    browsers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewBrowsers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    compatibility_date: typing.Optional[builtins.str] = None,
    compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    d1_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewD1Databases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    durable_object_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces, typing.Dict[builtins.str, typing.Any]]]]] = None,
    env_vars: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewEnvVars, typing.Dict[builtins.str, typing.Any]]]]] = None,
    hyperdrive_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewHyperdriveBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    kv_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewKvNamespaces, typing.Dict[builtins.str, typing.Any]]]]] = None,
    mtls_certificates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewMtlsCertificates, typing.Dict[builtins.str, typing.Any]]]]] = None,
    placement: typing.Optional[typing.Union[PagesProjectDeploymentConfigsPreviewPlacement, typing.Dict[builtins.str, typing.Any]]] = None,
    queue_producers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewQueueProducers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    r2_buckets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewR2Buckets, typing.Dict[builtins.str, typing.Any]]]]] = None,
    services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
    vectorize_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewVectorizeBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4e7080c58251d0cc4979dc0fd9658db010c20ab8db857bc75a43da58fb29152(
    *,
    project_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6447a23135c261e551f5b40eb414278fae80e4948bdd10d121fc4ca7c8b3dd1c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__817c94370882ca531583c09348b11c7152c6d7c14c822763a18d6120d0533a7a(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e244bc0bef2bcd30e37800f00bfc1d1084e33a3e2e4623d3e7495d9b6153ff55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66e243a53146ba5c0dfef90e05889f3823d62f9b532ca49d967b5122aa0b548b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__044d4ae2475c0e8b69637c1e7f40f48ffafa209d2577ec121a5737135a93f087(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAiBindings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b64b2ec1611270b71532d4325de2c7ee0977695540a14a78bec003d9a692f530(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__254a42f33889a14c98ab220820fe0d6197ed647ef7d51f7d16c64c961d34d334(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1b8439899d3dd507d605ef164b005887b71e84c1359ed7e8bc9146e31296808(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewAiBindings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bc092bac2c921f626ec8ad3b11190ba67135434d86e6ea53b5044cf8d4883d9(
    *,
    dataset: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__464d9fd64d7fd499bcc369dca55469e9c6b338bcbfde6dd73422b9089baf7234(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cce5fdef506322fc6ece6b9260eb738ac2c5da7827dc9bf29dcf52639c50cc9e(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__260eda28f8043f6f4d42c8c1fb1f4f187694fcb3e39e577dbfd968dc10fbfc3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d0e1e10cb7092dba15007c9412700dcc88e55e1dab6a6316c0a77359aad130b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd65de245433737b67d081eb86e87987b4604448bcddca89e60ff5dd020475dd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc4f4aa6ef83343154074d5f969581ae140eccc97308c9a122d285350efacc40(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb463f861239c66e3308b78f58cac00cc3acae12477ec567fdd3b27a6f533c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6987ae207b90baf03ffa6e1c780e391ed6d04d21d1f2f8d4c64be9a06d9e36d9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed71074bab39997d3870877a088e000ac3b746c7e2332c2409e0ac8c79794c83(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dd9443e085fc681d1834be46f2943158181767761cf50584ebacacf595cfd66(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f8313b78c6665ae9483bc9353ce7debed25761c3b3b71fec6e7f89b8613445(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__768b7280ecae4f7894069975d5f8affe11a9726d3989e8c9cd309238cab50daf(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efc1379215b0d512bdfd7fedd2e0840ee79bba7c599a87cec7c4e18bffb071f8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewBrowsers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18873b1894809d293986afe55ec8413a0e927554c0c425347f2719fdb36ee529(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efb6ba55c1e150bda4aeeb4399dcacdda30c7a4ba17ab4230854e03fd32092f0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewBrowsers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63acaff423ee97600848c94bd9a53d20556f3f5aaf9da1cdd5165ca8da07bf3b(
    *,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06df61a96aeb7ad876110b0c3624ec5bcd14486f64792cc7d50254bac34bb0ea(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fa97d138549b90a12eb12d9bec7a9b3167b3a60339114c62a20e08ec71ab9a1(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__284a8c6fc1d0508d3e44901fc07e5749e7b15fe63a686c18444c02b4fb2ce4fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8d6818fe4827e3131e56c99a720b4e073757f8c7888e22247df7481dda19d45(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1169209129547ef9bf96247c6ca572c04f7cdb13a9254aa57802b257fca21ac8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewD1Databases]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c969cf784235d26042fc458f98954f6af0fe030d0645c001959ae778fa29cc8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80f350896a5b258072e77244466da4b30ea02083b1b962022b0b4909b04dd55e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ad973cd82972e5785d4059c043900c1391486220c31ce9ff2107ac03b75adc2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewD1Databases]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30e173176a8977d674bb610006e706cab93da0a36bd7858d6f6ba86f8ac5780b(
    *,
    namespace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70d4f33240623ffb0b4a51b79d3f87b301c13262a076532bbd117346fe9fbf5a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4781c0e4dcaf71bd3993e236f4b74c26db32d635f412e5cc3dc8bc0d29e3ddba(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5561bd76e2c8e41f4b614fe0e51a402b61e64c86de8e315dc95c7fccf08fcad1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40e3f523bea433806dcb3543e5d38600506b85d494e8c7c754f201a28903ad09(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e159049a476960c71e5b2bf7179f9b5ba79780a78cf4fbe5fbf6b9dac2c3d6de(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d235a5974c9b9dc2831108c112113199a1d4a85ec89d8d262a21adb29b87f5c4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33b74e7c5ae02104e0099e592086b79bdd5a5f355996759385d51dda2ebc2478(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0a9908634a3e6c03272c358bc6368bfabd9530a0e2a870d941a5d78754e9c01(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15b67416fedaaf4c1d8dca670bd8e1223ac77d74742a159a3b53906ea3b98007(
    *,
    type: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4569f3cca6af930788f119ccacb9bbe5595f72cad22293055927275379d47b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c0876b15d4c2dbde4144116cecdfa9b0fb42a5b2690db28542e77bb8d0e1aa5(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28b1ed089e02de80c84e0c267d7c3b62d1f4cbed99185d493363092672f01375(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec8a3caa8196bfcf5cc9316ff35ff81539433f92d29018fa39431fe67b3e909f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93e16a749bb972af2900934197c0b062119e2f729123dbad14c6640e143ed34d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewEnvVars]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f7c9cdf013166c01961d1774e717e90ac28f04f74117ad615062978cc674e79(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1aac0ee5e2ca24da8d5a95af2feb9012edd9f8a0c4d091b2e6a1af1c9366c999(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30c2013bbd585025eb5248e486983a48a912492ee3e25951a1ba1881c0facc72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08f9322992d57063eda4d53ac61af83ec8d8fe10e16dedebb6e9302805b83ff0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewEnvVars]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__192e99c9daaf49be6f483e85b29fceebfaa8a954bec17155d9a6dd7e47f1313a(
    *,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a259d1c91d187e0999ac0db86e397c241068b6c53ead37206549c4b0a6007cb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fc4ffdc3674d8e11d6bc946cecd4585ca35a7129c39792f766dd50b406604e1(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7f9ba377c1971687adaa2cc1e790660411deeaa9a84f453f2f732bbcce79982(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da4ad5de267e78e8ce6acf57f8517e8a7bc49a0a05cbcda5f82ae62bcad647ac(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9510d808e53696aa432112c53b99bd5a487293a06babcb9059713c26de38ff08(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8358a526f7a4f88f8bd92fa408d2d506b1268c75038fbb8f6c5c86de2772ae69(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72679c84e70af5bf17ad9f9ebe43076747d738e44e1ecade4befc37e7be934b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55fa879f06ae2ae97b07f5e9a4ccf19730737c58b7fb36663c1daa92a1568546(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewHyperdriveBindings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0091c6bfff792edf941b777181d73d21ec638f02e8da108a889c8a6bca156b39(
    *,
    namespace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa81e369fb82e5898fd03ba97308131ffbd9af0bb54e206b4814bb15a797052f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f71b654da1e06d473d99add3109ca9624208d1d6d4d7eeca728d24cbd6b8c428(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28884ded9dbc2911ac11e8d0beaa20600018d35aa3b38d32abafca8a84da8037(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6385ededa8ee31f22d820781fba220289351df744da55e68e772ad2e10f905e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca9ade684d0e68576b0b70625dba79a8153d92bd612f12b93368278b8376d607(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewKvNamespaces]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1c12591f9c5d871e4cdd86154f22a28596e4ced890d0e7775428af9a48bd5d5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46170dbbf3bf9e0b75a2fb9f6b20d3242612d11275000b71269367bffc2b55c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86f148d59de412be1e62afa1994535accb078aa24bd810a94c5a4aa0ea507359(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewKvNamespaces]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a18e5c004f2f37aedc7e4d9fc4e2f37c5411c2a6f3f77f920a8beb235fc64eda(
    *,
    certificate_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__036a5539f8a755616a7be05fe77721fa2b275a43ec7db0aeb8c184fefbb1d73b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a672fc9370e709d418edd64075f87e948dd3a77bfc6c18b28bb2590d169d999d(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c53044c39bdd000bedb93d90d13f40d7a107d2215ea7169426dd860825a2f463(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa99f3351382915e9b7d35e6935225df2164c966f179d23bf818039c1268d37a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acfdb63c6fd89cd4148690dc777531a22c7280547a71581b17822c9dda27de17(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewMtlsCertificates]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f05ad09691210667252ed44f11031a6fe96d87429fe8ece51f6b97a1fd7f00bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9504eb3738e939ac9b5ea1e32d6612729db2fe16feb45dcc4fb4a8aef39cf65a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f179eb1f5dad0461bd66c21b747183f1853f306b71b0d83397f7a7b2f587ccc2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewMtlsCertificates]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae1a53fd86f66b2bd391be423e5c8d24aeb47824bd64d504a301cf722c043d66(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ec20dff6c58d847cb0da1df9a71eb62d842c9578a43ec96c89e79dc61dc683a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewAiBindings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__417190bfe6103782ce90cc052627021de0142ceee43ce447d092af516c102985(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e4c749f4b7aaba019814626b9c3a4c68402354ded5e3e2acd12eb49ab000f3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewBrowsers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d22d92ba9b73d16dd8eb147797ad7ed4ad17f41e7ded59ae891f9948c57b820(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewD1Databases, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cc488b65167adfad3bb1f4e4b27e48854c83f9af9c77c76acd6a203affbf7dc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewDurableObjectNamespaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__598fb5e45906929fc164c29edfe79c10fcb3bf2297dcea57f0bf7d96fef89746(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewEnvVars, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69c572390962b8ce8d324d63ee0336af7bfcc7ab681fc6bec87ee12f0a29a008(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewHyperdriveBindings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d14a1560b92ba5db11bead7e3e6a4b4ae378a70d31767adf9bf9bb5c5c837cc5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewKvNamespaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2231c01f40589e5223952c96103c8fb21b9b8f4ce249405db81a8b43646625e8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewMtlsCertificates, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a997cfdbe7807ad2002b259eaeba72b0cb83f88e9d3c2b24e3e1427cec4ab0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewQueueProducers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41173fbb683ada048fd7b0ef6f23c6630ed0458e9569fd0d3a5e01f7a65b27ae(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewR2Buckets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f32dcc0cd76498e81c1806bc204f44444aad86e83eaf91f4563e2e0346b0c9ae(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewServices, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10f813d616615dd0186dd724144f03cf36011399b553b296885c6803485d884c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsPreviewVectorizeBindings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32865b61c6888db2bacfa85645fe28c8b167deb8ea98040548aefe9babd5762b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c7134d0cb1462ec7eb665fd47f1f671843e450543c55d25eeefb57ec5363f35(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50fc5ad9dba9a0aa13954ab41f376699bde856670f046d16f6a4d579da2f821d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreview]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98f1c108112e6cb9dfa64dc7e8738e74ba3bbe017744a487db1ffcc02842e762(
    *,
    mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7b411d7b6d09b8b835b73305f16f04ef41c7b409555e816077606e0f4bf2fd4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65417fa8c2cc18f68ac950d676fbd72cec4c53f0bb6719ea950ed2b8cff669e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43c47e159562b79c33de06c05ffd2e2db7091b6f30a62cdeaf3546b831b128b7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewPlacement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aac2cb1d433db465a2244ce20f6a2e5bf0b22284fe8573721c9dba326d09f4d(
    *,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__239db956f3fbc55ef4925154193f59b5d4560267d16094456bff1067828f7380(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27b3536ad4f31d5b96da48544b25a8dcb6e3e517856c7fe892f0fe94be0e505a(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98e2cbffd1e75ca79ceaf3c96b75d9753b789a743a11f9ca32d4eec237ebeb47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63924724f6907220720d7db9ca86521fbb49f4faf09139e24b0c21dd76f60888(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da9a7562af934bd78f747c31d19d1ebb2307f261338ad24321a64305513177b3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewQueueProducers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f4b59bc31d41d6fb5641972315b7595421d0cb3d2fda38a30247af3ba2ed351(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b79893b3b078b52a7e8fa9b1892608218a39c7b17e459083f239d112702cdaf2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__222048d1c5398c643eba07ceae27205c6a6e285d0b1c49231cbfcdc007c1b140(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewQueueProducers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f06b3e0e25cff25171c338e12f56c5d2fcf04346f00b9d19ac9b60458c3757f(
    *,
    jurisdiction: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdb554ac00bad22917f5954494ecacb3e2bc701111b1c031502edf337d4cf037(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ef3a0c1b5814161d677e454f79ed28a9ab9a23d982931e3b8fca404e39158a(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec2fa43d1b9bfca810aa718170af32046324dd81dc20fe313da2609bcc55d264(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36b40d53f16ef021aabcddff69f0d21e2d959f8d160f2585c6991f328d5aa4d9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b4c3b22c6f3fd4bfa023587400a89be9f5d544f5b9428b80c15fd8541caaefd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewR2Buckets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f50de20dd6885d8be2d3c6d0c22d3454cad2fa9638c5983b1c3987c5f9032282(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c07f19a019c327b0a68c45c09621c69fc03ce238eb63c910381a01eeb70c19f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea00ffba8eb1c97282d35e12cfd4fe6de996d2b4516fe2e8980984818d6862d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c220e9678afcf22cfa97e3a27f41cebdc88e697d21d87596ec5529a369e93a75(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewR2Buckets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3dc859c4056c6634de88b888a0b1fcf74aa14c76caef57c46f84cd13286819b(
    *,
    entrypoint: typing.Optional[builtins.str] = None,
    environment: typing.Optional[builtins.str] = None,
    service: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6ab4dc485273734abbece379130dbff6d2b495d42ecc81bcf468277574db246(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5015c7ec43fbe278ee6034f2584ab10e1b4392850a34add37f1686e7b0648827(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a4bbec2f58b815ee751313a4e6417d32f9abf453ca7bbd838137f6dcdea56fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7ae510de1e8f44a2b042b10d32dc107ba73b7dbba86dc3b8bb1acb8f55b9831(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c39d21eb6c512f276f76eb2797aa5bb23b6d4011c8c8442cf43cc66eb502b3e4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewServices]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c91dc20403a6582fcf1d54afd0bc690dae4fbb20345086fa86675013051ad2c0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89960e94ae7fe1b9a2061d97ebd3cab62399df92a743845527b478b185bece7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1397b2f131c9228cf547eb37d75cae43cde9fef4058fb75018c5fb2a301faaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eaf82a64ac7fd2da822f4042b24bca8700d0398319a8d662928a8ad1149a36c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3353c6dcfea0ba66398767df540b9c6d7037b8daae622412f049f0ab7013e5f4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewServices]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91b9c2970362746d5a671ad4476b0b611cbbc96d98d86c80542ca3087e7a736f(
    *,
    index_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da59b03d8f7602c1cf7e2b77fb84d7b91b9738ea3b0d7e8b542ffc30f36e1dc3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__898ebc7e1d4bd9c3641283bfd5ca82ac480eb69a825ec54bdc6867cf555778da(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e60c9342a4484d0357043cefa93b3a6e2e61deb95d6b05c8f99919ecdd548e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dc95609cf5d7537d957cad3734f93ea8714ed831d6649a365982300ad2ce07e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db1ba0834b91b841298b4e285d65248cce20f8b06a248a368dee46e3c9ac9b80(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsPreviewVectorizeBindings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e34dbde9508efa453e2c09119f668f62332ef1cb64b9c28676d8aa6875703b0c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf937ba07575a968342ca5df7a371aeee467b185914be4a88f6ff96c29fe2e61(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b19b6514b07a61523a856a6869326b8fcbff25b1e32779bb38b8d531552bb50a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsPreviewVectorizeBindings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__336477b4868198acb01a1b41c8690524ec7ae03a6fd6dc2340a5ffb5c86959e1(
    *,
    ai_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionAiBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    analytics_engine_datasets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets, typing.Dict[builtins.str, typing.Any]]]]] = None,
    browsers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionBrowsers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    compatibility_date: typing.Optional[builtins.str] = None,
    compatibility_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    d1_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionD1Databases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    durable_object_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionDurableObjectNamespaces, typing.Dict[builtins.str, typing.Any]]]]] = None,
    env_vars: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionEnvVars, typing.Dict[builtins.str, typing.Any]]]]] = None,
    hyperdrive_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionHyperdriveBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    kv_namespaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionKvNamespaces, typing.Dict[builtins.str, typing.Any]]]]] = None,
    mtls_certificates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionMtlsCertificates, typing.Dict[builtins.str, typing.Any]]]]] = None,
    placement: typing.Optional[typing.Union[PagesProjectDeploymentConfigsProductionPlacement, typing.Dict[builtins.str, typing.Any]]] = None,
    queue_producers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionQueueProducers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    r2_buckets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionR2Buckets, typing.Dict[builtins.str, typing.Any]]]]] = None,
    services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
    vectorize_bindings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionVectorizeBindings, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ff5d97c595c1134b63db5ac4b32e75f553c80b9a7518cad080ce96fde08657c(
    *,
    project_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9f8e9340303a2dc4d9f6081357052a694dce877b3f217ecbef29bda2f26c4a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07fcc8f725906b04b55f406778733b31a6d98a0fc16e7d2c4531c9a40e789445(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__889c87f5d45cac1f5d7d3a87778d51ee436e010fc083016843d24ba478cfdbdc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__377d9960782684629b7bb0b74232441fbfb8579e761630782ef30e971cae95d9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0868a385b5c4fa2462db9e6c451b171fb3ceedfdea9161ef0d00f7fd851d47de(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAiBindings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35ec8fef7125dc52abb39d432647bec422de4a5c147f49b9773f7eaae13e95f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3212f4f96261304683213d75e42a94473ee550791d0bd79c7caa80731efd6505(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__794201a95967de48a30b07d2d66b1b1e81c45c512a84386be19f8ac07313b834(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionAiBindings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b679cc6846088b3249c313b1b81ed83e0ea05ebbac7414acd12ba4f1a447ffd(
    *,
    dataset: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02870ed3358357d5096a9cfd9df8df3593b8d84590d474684cd68fc325fa86ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb21e3a18ba78bce05aae4d12f450b9868c8dafa44f1a075be1977fadb3066b9(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__535d95a476329ae15c54279ef0c1db2474db61e78603edd4e4db2c33f574c74d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__308a30eccb6a51f7f90813c5d8b54302994d809d53d4945760013437b6200343(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52e16fb1fb955d944f3e51b203ceb6ecca34968ac8130cd5e0500178529a6e29(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aedaf70d8e04d2b0b7cc77d59ccc0e6b3dc8d54f9c3bbf88b8e7ff64229fe1f3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4b9eed51dc5fe645869f7f22cd0717e430232ea1679338064bc40d467d656fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d3a035c4d4f86ce2977fbc3da7b518853856f4614a9670d7011a8e441c07ea7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c08f9429bb3c65ef871855cd08e72e6e9e1f95353ca763de3e5ecf031175c084(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__104030db755caa30321919e3d9bed08047ec831b1a52069961591307faad0cd1(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a157275a445102d80fcf104faf75e89dffb58ca9e5eb0dfc86a8abe0fd78f984(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2aa61f8bce92be6979c1f3004f02f47e9c66a9d234339084598869e93f6547f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d750091991fda63c9bc3f55b833595de569f7adfa21ad742a92b9689f4a53922(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionBrowsers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__accaa1672dce8267a41c38aa9f2606107a72219b46759085596c87012acda276(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cd61a036c5cfdbc0eb456575bfbbaead3f250b111b06188101a99913c8edd3d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionBrowsers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b07e3f86925ba50efcdd4cb80ef9f37066e9981c2be549f6f62a17b9a780f1f(
    *,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ddb96fa8acca946a3b1e435f236555dc89f77d6f31462755eb338407a6a5b82(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42a38a7c7c8862e3a0540b016f3e96c953dde193dc18c20b5bfc9bde6da83da4(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da395be733235e8385f7b7131609d5c388db897f4b63e96600e3b5ae1cd14bf7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96d31ec0fc4396b5b07590f302dc061c0e85eb069bf056fd56a88844364ddf40(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7266370ac69f2961559145452acb76c691448fa91a1c94feae6845a066c527fe(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionD1Databases]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe1624e30127d78f1ca4c75e97a1302997a9cde6d3e045c93b2b3fce27f4e93a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3014e21393539347669cf16987000547c24fa6b81dce7ea7d3b51bb63200666c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a52cd4951240de903e3b268cd3a68ad1e55523bd445d99a293d76869108de7b7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionD1Databases]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5facf7e9eb05e3ddbd403b5859d1f4977b3dc4a80ba17ebf9652ed6e82635a1b(
    *,
    namespace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__393417b9ad51b0a78031a583be5140f35606cea4548585fe156eb6d7ae7f5915(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31146e1fca391268e933c20a81cedb29b3010de397a8c2dd433da9b1ac9ac2c6(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4be6c4aada0a1e781a5db086812a2ae9e787ba6233b5cfc02259b581164484a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa35fc1419909edc6a718fc34b56f44dbcbd86dbd91c2d8ba7987c7afbeb958e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ccb025663d8864c9ec5d4b6ca7b1cf8abeeb0d2be24e620841d030ca398f5f6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e93db690bf3acb3e77c803f081e84dd3134142ae397644e82888a7a161c48db(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4e22694e662bc4e51bc5f0e2c284959367311ca2d3b4e81e3dff4f2532ca4b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac3560bd072117cb1a8cd855f140daf6bbcdc85670b942118c33adedcc034930(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionDurableObjectNamespaces]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b9b44ed860fa627e700a3874f02ef38db8b48bf5063094c79fe1463088504e0(
    *,
    type: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3ad473c1b2d9b9537995d6a8f799bdc21d557e89d827587b8f2c7f58e20028a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59b70c5fd462670cd9d1afc3b197cb080d71a48e84188333a83b13c353267a73(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__885f7cbba19987747fd921d423e055961b9c2e1b73d4eba00457e086ec3d3bf3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f88387157a9d6b9820795e3251f956b430602f314194c3e31bfb50e187e29d26(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97e0cc0cb5840bdf1bcb1da86c18de820f4a60e216c6e5f58f5b0ed6abd97202(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionEnvVars]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2461340c95182022f8fe2551129598fff410ed6aa4a41e95ebe0972db2f9cc4e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21910a3a2500ab2c846c379e329bcbcfc12be582e29ed9fa50baad0014477689(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cf180b8c15141cfd72d3eb5fbccb6889d129ffc4b7ae329d10570b71f1988f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1521e8b7e8d314bb22aa4b29eefe9094eb4c3e35334f1ae8ef2bf2d468e5776(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionEnvVars]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dcef968789f42b8643c17121084b18ce7873303e4611d4ba4459f760351a3c4(
    *,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__075a9cdcb82cbb0bb6beea4e9bdd0557e89813905e9ee241252386bc4a3a88d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__288777d630e4c772e0f16fbc86cf4f4be5c008cbb381b59770243c060239076e(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e36de89b1c24028dcb04244ee1c3336070af7a0601fdf9a3c35571c45071244f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__121fe227b2ac8a44a1524871f7f0d095adc301364059e48c9a56c05b3f96f07b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50464c75713ef52ac7162c1e104dcbdfbf76914ee95ca6c03e880c1e82e38645(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionHyperdriveBindings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c1f92c42ad004eb5a445f38cfea83a3f2f0621772d5b9fa97aceb25328cf980(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbdf433c845bb15dd164fdaffc9c71379d5ec4b045701186417df41981b3e2d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ab2cd636169d73ec675e05825da46f5328cdb58bf75a0b014eefc85e5bcf462(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionHyperdriveBindings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a6df3da46e128f15b6f32b6347a411bd7edf9563701d2c9b9cdd3f863870c86(
    *,
    namespace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8772c2a6be35138caab09a04bc4e598e9d6058a1bf6f488c9f8da53f48286f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e3ecbc7ef9a7654105a14fb3d82ef765c8dfceca4fa88b6af3ae839db6ac7bd(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75e3deeba2e0e6c7fec22d82373805c64e53185c925cd229924be48387e8650f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb2111ee0196e6a482ef0bf02b1a0b797f0811afb8c278b316f24694da99715d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a5fa9d5b7f6941404f843ad70bca2750c5cc176f48ab64b20bf715fece794e5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionKvNamespaces]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d11bc907e31936b0356aedd69791884d527959ebe3b5979a873f91acd3f341ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5d59f5ea71f5f86e7f768dca714a89a94ca91b03328ae5e94a2e1b1844d114a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53f6b2dbe49c9c106bc8d432f484ab9b819941fd6bf1851205299af03bde3349(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionKvNamespaces]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd37b77e2c113e2a54e4778d45e50b19a672aeaa3713fd15e5357d31cc4b2bc2(
    *,
    certificate_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5da6dcf6cd2ae3f5bd4179c26eaaa5af92199a6d28ae06c578bb4b95b2a6f7f4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5325afd1898cdf5eb6c496d5f70430fa0924d217bf7fcc8096f182c846a17bb2(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68dc230cead5fb49b10f888198dadf50da696f96e65b3e94859c498d76df60d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2ef9abff9dce0fefe5eeaa1b60685f2482cedda9aabe4242a943688e20934b1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85876ddf90e1004248d920192fea1a4a595d0bdc48ce8275276da5a44dad8a0b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionMtlsCertificates]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fa78ef3498192dbc2ff9db9046495c95b5fb9dcfba49257100f6b21136d3622(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfb848be19ff968c58500e698c3d68aeccb67d9c903d5e027dfe96bb2ca9d817(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a52b81f9c22f6645a9e1a736d7aa2305e78d1c37e07525bde99dd47c5f252492(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionMtlsCertificates]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7265aa8b15c3914638516c9c006481db3073e868d9989557acf0a5b26b6db6e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab39e9d61dfefb1d82e066039489b747c86f188cb0f14678d6bea3512ce1fe4f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionAiBindings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1912f585f44b15e875bc21567990cb3ad701cd3a196bb1a7be419f0127e99e19(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__359babca5c66c44a9bde581255a6353b6dcef5c98af9e87a91964fd3677c31e1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionBrowsers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea055b774ec561103d1f2ec91853c5002ce3ca7050e5cae9860ba21c273b1542(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionD1Databases, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0696d974e924a31b4bf5fc11e56c82ec237a8097a11d8ddadecd390681f66554(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionDurableObjectNamespaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64cf56547ae4acb9e492288a15ec9627ef630d3d318afaad577d67371072a601(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionEnvVars, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60b3e6d74e41bcf2dc47db2a6afc7f5dda41b948e1c7abbe6f3a512cbec5b943(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionHyperdriveBindings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c950dd8a1491ddaac9f32c321029a4ac5486b775e76e157e5bc7877ca362eb91(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionKvNamespaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f7e5ecc077e3c9d2525340077c85564a46729b0b4833d1db73afd6833ae8deb(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionMtlsCertificates, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d091dfd7ff7acb5f2ade8c546d13c435c8ba5a91a184cb3429579825f06312f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionQueueProducers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72babe7567d11dd698d8f5a1cae46a3fdedb9b556872813d88ad8f2c6ffd8821(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionR2Buckets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52a85093c99b01c2a6e1d903ade142711ff361b89b07ef5cb059dfdcac617cb7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionServices, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba98fc46484a18d84d2b94d9d99c3c2238d00155c2647ad20a04573ab141bcb0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, typing.Union[PagesProjectDeploymentConfigsProductionVectorizeBindings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0595cb8eff7f6b8d6e0bab4a75c9b33e7b8167dc670154c5d5ac8894ac886abf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37b984d2023ef3ff4c5e45625bd77fdd6b826d1556ca0e3b9d429b11e166f501(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35175326b28b2f7fe96351b76ce3c7430ea6837f3eac340d2f6d3655d52f0adf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProduction]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aec8e4c3f8bfa53c4a1955e9bfe9e20820f77bb728d70de74030934857db4813(
    *,
    mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0e9572e9e66468efd1475ce2144ef5ff5b8d52946c741f2474c687c2bd69811(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e179cbc78ff2c09a96e19e3bb1464363d545bd57f8a99aeed01dcc09d780548(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f413db01a77d01847bd5862148672f9415633528c4e134bc61a70ec56cd6249(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionPlacement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c84fdfc7aa011620bd4a12d560feb30b4e3b8f45e92982b14564845d7b17a96(
    *,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__800f4f4f34f6688bb8f54bd4a2927c085ab50d127bbd36d4d172cf7fc682e422(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f29ffe02722501b8c434e244dad73507d8b516bff88d8cb544045395354ad021(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15b7c40a2e37daf28b4d9d920f0882df642eb8380c791da07f7c8d7e44b4ad45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7441c67cefacb709bb5657109ef38040c1e79348e31670015832a1a2909df7a7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a073283e314ce327bbe1171ddd4584c301935f30c21fb665cd1c43c73198ccb3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionQueueProducers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__861b7af8dc28a636229bbb66916fd70194a2f54450fd16ee6023e722e76594eb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63352a2f5dbe1cb14af9aa4ec28d296f54dc89ecf25aed5f96e46f9305adb718(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2aa32ef721e329d25c855f6b68f71981b2a72395296d395af1f6538f1b20996(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionQueueProducers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f19762bc7176b61bad7d88fca71f6e0f7be0d3c76509709e52a41f628d7825d(
    *,
    jurisdiction: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6079e18538ca57840fac12d99eab103247b0a23b05b41a10749c5e1f3ad0876b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e066522a01ac4c92a73eafdbab85546e35b235d78a12010a76a10e243e5d4df(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50aabe24386ccd4709a5a5ccc89c10850b5170b8136c8ddd1cf688cc0255bf88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6ed2077f662bf0aff713e86759a2f2c30d7409dbe91177a375c4f2d35d7443a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65e6199a7825dae22e548a1fef82bf117ed60dbfbfc339f89e5ffe6c87e99ca3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionR2Buckets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb6eb2508d786fe838937217aa5c73a29c4497b1cbb56147303b6b2b1bd29985(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3915b3d8079a44762494aeeb5cbc5e00812e9230dd6aa09b0d8a6ed1f67f9c09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1d08f2df602744f4f9b6182cfda0f01bc6c115dbebecab388cb0b29509cd1fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__211a2428428f475923b00f7f3a0ecd53a229d9626dc32649b23301ed2eace904(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionR2Buckets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a14b5302b6a9ac999f171372ec2f1bd605e62c310eb191195a119ee2d969e9cc(
    *,
    entrypoint: typing.Optional[builtins.str] = None,
    environment: typing.Optional[builtins.str] = None,
    service: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45ff8b0a2255a72b95b32929c1faf3f928dbe4576fd435a14decc1c79e56ff29(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb6c8e9b3b45aa63c153503d703f2215c6ebf58da0433b4d9399dbf0599dfe80(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2f5fc0f42a9adf26ce2d283d2c2fc340947a2f2249503dff20652eebdabbd43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b3de1092f0f70bac16f50431222d0128a8e89ea8edfbb57989ea2649e978e6b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b29ab2fd1dbbf012137841cf5c54624af88f1142b99a262c6307664bc56733df(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionServices]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__716c1fb274c393d7122d995ad7ef7112f81620f30a085fb6c503ee7d85ca6a62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38f80780ba15b892edfe00e64fbc206bf9709e5f39e5606f2e91ffdfcb399870(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6798c6c7481382625c13e60840be339673ac9ed1d0361715fa630593b9ed52c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6afcbb0f890fcc0a99d6c7bddaea3a65172f77d00991e1d7812e346b06c47f35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__450d5ab027219f0badf729f110b2757bc4e206b75e76fbc73bbbcdafec8fb830(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionServices]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83b2cf2626f90957411a6f58f551c895f9ea7f6646bb90f72451edc128fbd3db(
    *,
    index_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56cbffd212c113a2de920f9c00e42d4a0a3867021ee62fdfefb5675164256c9a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aeedc9b836636987bae1939e001bbfe8406d50f13415bca2076a03feb33e029(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92e67de0b8a9c4c4508140a8d24b6424792d7e10b8b4a78d3521d6d1b962fdb3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__589359711a5ac673657d00f7c451e98c1b1ca2c8a0a8363998080a5128f19789(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e366c181101defc2ed36d291d52249e87178dd8094a4055c2fb92ffb8ec431c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Mapping[builtins.str, PagesProjectDeploymentConfigsProductionVectorizeBindings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8053cc0748baf50c413dc04e3712020b9e8f68a310475cb243ec74bd7a8b757(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83edce63d46582d91c1ba79ab9f6cae91d14a91cfcc0404a3b94cb6a329ffea3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e79f773935fdabd965451dee46ad61331f05979b355dd781e6a797443b8ef293(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectDeploymentConfigsProductionVectorizeBindings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5885a4b65f98865c11ffbf5b5d9bbc9400cdd85d6b900088c00f771faa0c246b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf488bd0caf867921d8f3d0750f120d3e8f30556b9fed0c3ebfcdfa46a124845(
    value: typing.Optional[PagesProjectLatestDeploymentBuildConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4f11d6a1f28f1b04d3660735d5264cddeb40e8557e67f34244c8df9d808d556(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d400938250a81c27e8da7804065d19738d6df915023f395e1c18516b6f84ab3c(
    value: typing.Optional[PagesProjectLatestDeploymentDeploymentTriggerMetadata],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__058ed9b8cfcb6fcaa2810c686ab8fa02630fd0f97e1d606f64a610105c057297(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdee5544cab4ab50090f74df9b2194d2ecfd0413dec61e9540084caed442628a(
    value: typing.Optional[PagesProjectLatestDeploymentDeploymentTrigger],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0241bedb22c0847cd74050a1bb6174ae848c2869a0886b291ced4ebfb54f939(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0bec8b019b90be1db55ed20f650ae401b80e73c61b1bcd574feadc9cae73c0a(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db6e1f51a898652c8ba4ba1c89d9fa4fc9520d639a05571851ffa516977d932d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efea81c5b9b821721e9452c1b661abda626e310c8a0b584ed71c828423745388(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b9438c1cf4f2b56e124ceb7bb48163431e9e5370d17ae013451e3083045ce75(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc223363434d59fc1799d16c3eb8b90d4993bf1505522262aea859dc96c56828(
    value: typing.Optional[PagesProjectLatestDeploymentEnvVars],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1382a20c1b2c72a27dd7ca33bf3eba2ad11e804208f300b833b779be34511b67(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cea34f29247f5670f770ac9d4b0ef383eca786d2119a5e59402e06869b36ebc(
    value: typing.Optional[PagesProjectLatestDeploymentLatestStage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdb850933264b2c7575638c5de50da52883ad88370b46525f6499e9803908985(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3d583a06eb94b28258fdf72a44a54da2d31ddf08885c6f85c1f461b7ea844c0(
    value: typing.Optional[PagesProjectLatestDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34b46ff84bfa937bef05496d928475389265f98f92f208fb00adae54e6785e5b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b47cbb6a313d01413afcef64df57782ed9b3ea94c4d0356ea95ca113c7025c7f(
    value: typing.Optional[PagesProjectLatestDeploymentSourceConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc7f2c6273455532dac411b1bb411a23a75d46a23fe867c0579a8ae7645ae995(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__175ed88208250c1a097ff4d254e78cef03ea00b5a7e3ab21e3df683fee825c54(
    value: typing.Optional[PagesProjectLatestDeploymentSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3df0d71745d0878db9134a2b03a53cbba5febba9c4f0d5f8bd7b4c011cd1e4f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__834560b42f5a5a49a7e511155648c095edac30a05535fe58fb8a6761f1dbfcd3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__777139c5a64fc43f8da2323be008cad574b2ab10e9031dafa4f14800502dcf4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff4ef407272931faa97ee3744db1712b184c6b5ff185132211203daadfae34c2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81f5f728c608b85a4f1240fe5d165673862dc87a8c227f8bc75db35f6776f33b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ecc9fa36cfb9d4cb8cdbfdbf913db30302e166d74e86ad1b96f43c359862f25(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f425f308418097b60fa150c05eb382c8119760f80972ce68016070dfe653a1(
    value: typing.Optional[PagesProjectLatestDeploymentStages],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1a350c38bdfe501fc470a31a735e7a18ea66fce4461f5ea5e2cc2002d90fe57(
    *,
    config: typing.Optional[typing.Union[PagesProjectSourceConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d39510fd2d65da87e37b9b4d6793fb57e2ac525a07c5a2da44593f385253a285(
    *,
    deployments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    owner: typing.Optional[builtins.str] = None,
    path_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
    path_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
    pr_comments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    preview_branch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
    preview_branch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
    preview_deployment_setting: typing.Optional[builtins.str] = None,
    production_branch: typing.Optional[builtins.str] = None,
    production_deployments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    repo_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6049651f4254f7dec38652d77a1f1e865a9d1754ffdcd26b2a942a078f6ec45(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a17a6b5a6165242dbb5797b2b5d2df31416edc2f5f28e9245480e0bb6c5fa69f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d721940abeacc9462b79b6f086f6dbbf1d7454721a984d5187109d1ef9781d6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d9a3da4909a953d14dff9220025ad5a3cf3337695197a53026a2ce693a09ecc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d7126c01cfd6f5d13cef7fb1a46c50c6fe272a34989f6348c6f1d82147ac854(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f41d919260e3ac5408ba48074e89b050cd52867bc3825b78a1bf50163ad428e9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba229809a5fe0048e0ce26e352e0de0bcf8088b4f24001998c7080c4dc257d54(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2558db516c416a760e87375b1f8367a6f5e8ebbe22a7dacd81184c2847e69a26(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__919ee77dafbac4b4c1b808b5947dc7d331dd0a3260f97bd376b0a602679c1e67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8aa3d224dfc5c35aa7075d25ba015b53024e435701789a7bcf699dedb9a84cee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc0226d6ca16a3f3aa405f465acaff22779641c144d7b1581587f4a6fb8f2e2c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72212d6f12c26a75e6ed310b2afc8cae7bc0cbfe25fda3fa46def92734f10257(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03af7feda072e1d2e219e793730f3f542b45975a2d8c485b137295111325a197(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSourceConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6379b8db0604424167bff638ef02c874d65dcbf77b00e94de1c3401ab4859708(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2374ff2f25e189caef442453f610fe93ddcfdce036acafa4b58f1ed30940fda0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ee731c9c2f91c73570681f8265ad04919cb4f0058b752c89b6b5136784fa3a5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PagesProjectSource]],
) -> None:
    """Type checking stubs"""
    pass
