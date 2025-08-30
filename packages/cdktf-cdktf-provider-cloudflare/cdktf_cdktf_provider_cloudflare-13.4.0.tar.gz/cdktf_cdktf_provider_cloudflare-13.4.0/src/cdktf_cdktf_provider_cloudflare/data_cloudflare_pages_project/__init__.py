r'''
# `data_cloudflare_pages_project`

Refer to the Terraform Registry for docs: [`data_cloudflare_pages_project`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project).
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


class DataCloudflarePagesProject(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProject",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project cloudflare_pages_project}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        project_name: builtins.str,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project cloudflare_pages_project} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project#account_id DataCloudflarePagesProject#account_id}
        :param project_name: Name of the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project#project_name DataCloudflarePagesProject#project_name}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28c3d923c53d257abb72acc4e69bb02e82519a05c675d6325c407b03ab41821e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflarePagesProjectConfig(
            account_id=account_id,
            project_name=project_name,
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
        '''Generates CDKTF code for importing a DataCloudflarePagesProject resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflarePagesProject to import.
        :param import_from_id: The id of the existing DataCloudflarePagesProject that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflarePagesProject to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8d85119577f3426feec435c61241aeb056560c5e06fb04de3b9ba9a326d4120)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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
    def build_config(self) -> "DataCloudflarePagesProjectBuildConfigOutputReference":
        return typing.cast("DataCloudflarePagesProjectBuildConfigOutputReference", jsii.get(self, "buildConfig"))

    @builtins.property
    @jsii.member(jsii_name="canonicalDeployment")
    def canonical_deployment(
        self,
    ) -> "DataCloudflarePagesProjectCanonicalDeploymentOutputReference":
        return typing.cast("DataCloudflarePagesProjectCanonicalDeploymentOutputReference", jsii.get(self, "canonicalDeployment"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="deploymentConfigs")
    def deployment_configs(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsOutputReference":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsOutputReference", jsii.get(self, "deploymentConfigs"))

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
    def latest_deployment(
        self,
    ) -> "DataCloudflarePagesProjectLatestDeploymentOutputReference":
        return typing.cast("DataCloudflarePagesProjectLatestDeploymentOutputReference", jsii.get(self, "latestDeployment"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="productionBranch")
    def production_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "productionBranch"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "DataCloudflarePagesProjectSourceOutputReference":
        return typing.cast("DataCloudflarePagesProjectSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="subdomain")
    def subdomain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subdomain"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="projectNameInput")
    def project_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectNameInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b244d8ab6aa84e48096112166489ed3b9a538f3090480a6f5b10c65f91edb358)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectName"))

    @project_name.setter
    def project_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c773933cd807e083fab2bd532eae8696d8837f83138027f077762e85c13a1046)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectBuildConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectBuildConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectBuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectBuildConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectBuildConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__430d134c45e6ac585928db325c427a0c7988117af9c3c5797f8492471915da30)
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
    def internal_value(self) -> typing.Optional[DataCloudflarePagesProjectBuildConfig]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectBuildConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectBuildConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e03751b6951a8adb33d59f35ba5449e1739888b826e88016eaf814462bfe2b11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeployment",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectCanonicalDeployment:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectCanonicalDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentBuildConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectCanonicalDeploymentBuildConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectCanonicalDeploymentBuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectCanonicalDeploymentBuildConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentBuildConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__90adcb3a9b23b82396b7dd9acce2c79f3342dcd1f7e20a40837cb43679dd9c6c)
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
    ) -> typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentBuildConfig]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentBuildConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentBuildConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__651bfd22d1902aae4303f24a9acbec02695ab9b780ae84e3d7679bd15b3eccfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentDeploymentTrigger",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectCanonicalDeploymentDeploymentTrigger:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectCanonicalDeploymentDeploymentTrigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadata",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadata:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5baba266ff035dc553e72a3e4cfbc626e1b5278d77a1837c58613b925544c90c)
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
    ) -> typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadata]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadata], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadata],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a19c47e43fc63118881de5423ffc9cea55099315d5dd3edae6b47380191ffaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcd88d2717897dccbe8aab672cf2e39e1711aee104066d3766378d698c3c3c4f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(
        self,
    ) -> DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference:
        return typing.cast(DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference, jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentDeploymentTrigger]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentDeploymentTrigger], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentDeploymentTrigger],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3749908aadf33cd11992c04fb9d7faf46b15574c04e38f1fdc3b591d558d5cde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentEnvVars",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectCanonicalDeploymentEnvVars:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectCanonicalDeploymentEnvVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectCanonicalDeploymentEnvVarsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentEnvVarsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae46060a709e51fed10f3b671c57632e5bc97406b83007ed189fd6e509b4e315)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectCanonicalDeploymentEnvVarsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08bcb54ad5b577986457e305e6b3b711be91ee00824dcf328004c2f316f86504)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectCanonicalDeploymentEnvVarsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd9fc07d494af6d89f719380648f349037e2a9339f64551166f1326cbc22a8ce)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ecaca156513ea76d36179709fafcdbf5ce5d6354734cc4598f0a05a50c977af3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectCanonicalDeploymentEnvVarsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentEnvVarsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2007e3b71f4df7fb219b1c7e8584ff72ba83503f637ea72e7df2d7796cbcafba)
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
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentEnvVars]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentEnvVars], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentEnvVars],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e5b224ddf80c0a92cc9bc25168db7723fe528d3b7be2dd1fdc1930fad1527f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentLatestStage",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectCanonicalDeploymentLatestStage:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectCanonicalDeploymentLatestStage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectCanonicalDeploymentLatestStageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentLatestStageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2edd210c583a8baef5839283baccd1a607fe816aace4d3fcf8072c5ab973b4e0)
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
    ) -> typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentLatestStage]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentLatestStage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentLatestStage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b320009eca26cba94da86c322b8a21a8fe3a11100b88ab30434a43719f3ca3f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectCanonicalDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c6180694edc3287236fd097c9f80e61cd9c316fdd65d47a18b773b127a00f9b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "aliases"))

    @builtins.property
    @jsii.member(jsii_name="buildConfig")
    def build_config(
        self,
    ) -> DataCloudflarePagesProjectCanonicalDeploymentBuildConfigOutputReference:
        return typing.cast(DataCloudflarePagesProjectCanonicalDeploymentBuildConfigOutputReference, jsii.get(self, "buildConfig"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="deploymentTrigger")
    def deployment_trigger(
        self,
    ) -> DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerOutputReference:
        return typing.cast(DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerOutputReference, jsii.get(self, "deploymentTrigger"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @builtins.property
    @jsii.member(jsii_name="envVars")
    def env_vars(self) -> DataCloudflarePagesProjectCanonicalDeploymentEnvVarsMap:
        return typing.cast(DataCloudflarePagesProjectCanonicalDeploymentEnvVarsMap, jsii.get(self, "envVars"))

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
    def latest_stage(
        self,
    ) -> DataCloudflarePagesProjectCanonicalDeploymentLatestStageOutputReference:
        return typing.cast(DataCloudflarePagesProjectCanonicalDeploymentLatestStageOutputReference, jsii.get(self, "latestStage"))

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
    def source(
        self,
    ) -> "DataCloudflarePagesProjectCanonicalDeploymentSourceOutputReference":
        return typing.cast("DataCloudflarePagesProjectCanonicalDeploymentSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> "DataCloudflarePagesProjectCanonicalDeploymentStagesList":
        return typing.cast("DataCloudflarePagesProjectCanonicalDeploymentStagesList", jsii.get(self, "stages"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectCanonicalDeployment]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectCanonicalDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectCanonicalDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a892c8fa189156fb9a2fe0d331dea973460cef566e1e35e5fb20c58b9fd230e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentSource",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectCanonicalDeploymentSource:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectCanonicalDeploymentSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentSourceConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectCanonicalDeploymentSourceConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectCanonicalDeploymentSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectCanonicalDeploymentSourceConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentSourceConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e721b5bebc1e17473eec22b4f12f40e038355be064c9d6dee37d8e3f0e2f0946)
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
    ) -> typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentSourceConfig]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentSourceConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentSourceConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__912d4cd293634eb81eb405a36ba95574aafc093e4b2a5eaf1b7570b9ebaa5c6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectCanonicalDeploymentSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ada5776e2969fde0c54cc0ff0d931d640155b69509c6c5720e8871445ce1efed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(
        self,
    ) -> DataCloudflarePagesProjectCanonicalDeploymentSourceConfigOutputReference:
        return typing.cast(DataCloudflarePagesProjectCanonicalDeploymentSourceConfigOutputReference, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentSource]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__224faf66b90006fc05934161e5f60dc294b2ba57639ef59351978a83f131fc89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentStages",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectCanonicalDeploymentStages:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectCanonicalDeploymentStages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectCanonicalDeploymentStagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentStagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b210b79a7be18e302863a3167814def09e5da6628223eb9111c1361302348a05)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflarePagesProjectCanonicalDeploymentStagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03737ab0a34f9854343abc859f11720a2055e65e645dcc998cdc9a9dbe5533a9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflarePagesProjectCanonicalDeploymentStagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e0df3d3ecb02ae025e130e9e906fa1f6370d903f744db853016238aa490600c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__787a273a733cba84bdcdfc5595c91779f1c46e478a32c9185a49404c06727dc5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__842c05221e9bee66d49187b2908e9a4bb5a5e4ca967f04aab85625d01c0abda1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectCanonicalDeploymentStagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectCanonicalDeploymentStagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c9ab04f3f156693dd51d2c20fe7157d0d0a5efb97e77bf123f9cc14f5a56b3d)
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
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentStages]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentStages], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentStages],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27f1d6355785d5e7ba36c0b6f8169b5e365488f76a909ef7fbd1824a328b0dcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectConfig",
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
        "project_name": "projectName",
    },
)
class DataCloudflarePagesProjectConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        project_name: builtins.str,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project#account_id DataCloudflarePagesProject#account_id}
        :param project_name: Name of the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project#project_name DataCloudflarePagesProject#project_name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a09884f4778ddf926e480a069239e7001433cd8b75895abb9a699485c061087)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "project_name": project_name,
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project#account_id DataCloudflarePagesProject#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_name(self) -> builtins.str:
        '''Name of the project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/pages_project#project_name DataCloudflarePagesProject#project_name}
        '''
        result = self._values.get("project_name")
        assert result is not None, "Required property 'project_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigs",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigs:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2837ffd4e6c40fe6b02224c3e6f8f449a14ee8dae981762aa05a61b1e97338b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="preview")
    def preview(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewOutputReference":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewOutputReference", jsii.get(self, "preview"))

    @builtins.property
    @jsii.member(jsii_name="production")
    def production(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionOutputReference":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionOutputReference", jsii.get(self, "production"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigs]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c88b01e12d5a968a1c88218fb7b777890e68b44f5dd0f56af5d83c92c9f91e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreview",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreview:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreview(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__839305a5e99af106e790728c27938209f78ecdd75c65ede840f2bc187deca8b8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecf83a2b3eac1ba68266961dd272b7992344526695c7ae318764b95770efb47b)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e4c5355b0e036d3009b348eceb009c7ad332e6eebaca70cd8f7d49cb4545bf4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bf77bc4ffeaed330aeacea523e1203b4a0077b09224042166756f0e64d17a6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__20bc5e7f8c33c4d88c65a8a6c45b6489141782e1f09e8385079db1eb337a2d9c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindings]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed0fe383ea716c8c2270e19e774c4458ce7a8fd3d79cb7fab21c885fd48d8a40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__de1579af09e789a0cb1cae4e8a453a7159e49358452b22dc393ee7e3e2764896)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0015cb58f97e9cd83a7a135539908fc331a16fa6e30efe783f9183b2d03a58a1)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14c68f133d78f1e8d2fc5b1a42287e9ed622e6872719eaa6429677d64cabb148)
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
            type_hints = typing.get_type_hints(_typecheckingstub__065be37dd6eeec5372948f35b4c491030ef134de1c220099f3d46c0d36cc6d43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e3e1c97b212b55c1d4c780f34d6d1829660492ec92b9e1cfe353b295107095d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="dataset")
    def dataset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataset"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6f1ca90a9d6d013099863085566748215f5643d764528bf008218b72d5b5275)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsers",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e741d590242b999d437399a48d1076320e1b1024da0260982eda519c87e0ed12)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dde82e1ff9123e5060f03505e58c9718ab392fce436541fc29bf093108754377)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3520d9e777fafc33ea4e55fd11b5dd27f2dbaa8515878e9d68739ac6b0423a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__09f17a35cfe54cb649f5cb8fdc07a54a67e82141def1ee372b159fab687a28d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__864f112745cbe689c5bd79ddcd5571915b9e95f7187bba8981a002c24e773dcf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsers]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsers],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f1c513eb0e8935a9f90d1c64b00da758f83c027f0cdefce13befb2500bc9b80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewD1Databases",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewD1Databases:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewD1Databases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf2099015f0bef7940359ba5a59ce917b907a687c00b4d8a9f841b6d34c2f23f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e255aeb5f4453ffc28ac60aae92eda0ff8392f9bc22b10b18e6b2aff2a70dff)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__017ea8dda5ef892cd870f4dba379b322e056105330d13476ae1947023a7b3959)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fbd6104e7dd569196452b0d297499cfec4054febfef3d52a151b08ee3633408)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ffc84cb1f95966efd6e8ca18d76f085741162166953d3730a3f4dad6f288f99)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewD1Databases]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewD1Databases], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewD1Databases],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65480843b74ce139084331aee1c641e77739a7d52351bac168b1bde75bdf6f64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespaces",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespaces:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d07e6fcffb6c7a148ae001e9655be86a7f67be7fac60df699d8ebfc31309db1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d9fc8abfcad0802795613e3e063a9f39ce5d65ced9b111566dcf5b73be1da89)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75864cbbbeddf931587cc7d8765aa549e5dfa19fcad3f41d9168817f0d07511e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__10b41184dc583da48a204494619700eeda07b114797dec275a110c8b13c165ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f090ba5b5a67c9f326a09f2830cd1769c085402747df55ad982aa8fd94c946f7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespaces]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespaces], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespaces],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4590d74f7039cf2d5aaf184e1a9b31182c0b6ffec5d1c3869312d7c34ad5a7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVars",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVars:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b0fdcc3f1fcbbbb6ddc48886b3c97e71d9c44df4231f31ee37e2f3acf0b08e1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55e473212500cabc8b20cc5837e257cf3eb466021fb6bd30bf7e6bb3bc596ac2)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38be2cfc9264f3feea923fad4270bacb67e715d7616af654ac315ad79e27c37e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__863b7f6a9c6c17e7fa842cd5acf4b4d4252666e1c423231edd33a170fa0b5ee1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3908d7aeb48757388b95bb0ff8fda293bd34e3819107e087237794a8883ee8f3)
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
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVars]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVars], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVars],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a047212e5405e9fcf98a00072c6de64954441089cee4810f78b27cbdfa1d438)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7374a4e94110f3a05e8be902ba4d8a2e07756a60aeac2b1ce63a596ed1f11d2f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4ad9a38a7d922aff0cd5cbc3c5fca99c215decfb9591ec5dc1790f3f30e136a)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1748ab4b2f51b7f33dea9e6316d7da3eb2ed8062f76c261e663352080fa5a8fe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cad1fc118a22c70a26daa9096e996d8d7aaea97e0c51c5a7aaa1f13467d01b2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae09d742a6f7d2dd32779e84cc0f70ddbb319929df99b23aab0cc5fbb6a957f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindings]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7c93c217354788b5bb26ad5d5f48be1137b2085401114f1cbf0c4c1ea59277f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespaces",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespaces:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd22983d3151cb6570a4e2c1254c29d0025a6458c90ceb181a334f329b435da1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7992bda975cadcd222cab58724d0a99bc7f2f439f1b4d93a743977b4f99d411)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6c126b358ff8f998173006c3aeb089a05eff7d464cca5cab9be8dd47dad24d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6aac2c9e5bb34b1ec5138ae30081ae26c6e4c87eb69bf555081cbef369224ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fabd0a026428a1174817bb1be495f11c3227c5ce0959716f291b0bce4687cc46)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespaces]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespaces], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespaces],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__273b73c5dfa78e63c8fa02a5128c67e5d2a1d1528c28d0c015dde3f75e04bb2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificates",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificates:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__221dda65d2623691556c2dc5c414dcef0dc27ce1c97c41a548721b396726e6cc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e0073a991a97240a5dc8382f30eed80f9db7180270ab8a5bb546692e2898399)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3633ae37b67bc7fb253feb8336fc9e0130afec1c634d6969037af66ac12a5489)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c374cb44803d05a10e968dfba7736255bee93df54936782a90a59a1b9e9a55c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f502264e5cb97ae43e75ac4e524001e9e086e6c7bf87be47efa02e6e9f21046)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificates]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1ebf5626ad7ceba996e122a4edc3666c20a67738f14901be325ee1a9f37cea6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b438ab4adf8fec50914431359e23bc61b7525286521ab77c30b038454ecb1095)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="aiBindings")
    def ai_bindings(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsMap, jsii.get(self, "aiBindings"))

    @builtins.property
    @jsii.member(jsii_name="analyticsEngineDatasets")
    def analytics_engine_datasets(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap, jsii.get(self, "analyticsEngineDatasets"))

    @builtins.property
    @jsii.member(jsii_name="browsers")
    def browsers(self) -> DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersMap, jsii.get(self, "browsers"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityDate")
    def compatibility_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compatibilityDate"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlags")
    def compatibility_flags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibilityFlags"))

    @builtins.property
    @jsii.member(jsii_name="d1Databases")
    def d1_databases(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesMap, jsii.get(self, "d1Databases"))

    @builtins.property
    @jsii.member(jsii_name="durableObjectNamespaces")
    def durable_object_namespaces(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap, jsii.get(self, "durableObjectNamespaces"))

    @builtins.property
    @jsii.member(jsii_name="envVars")
    def env_vars(self) -> DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsMap, jsii.get(self, "envVars"))

    @builtins.property
    @jsii.member(jsii_name="hyperdriveBindings")
    def hyperdrive_bindings(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap, jsii.get(self, "hyperdriveBindings"))

    @builtins.property
    @jsii.member(jsii_name="kvNamespaces")
    def kv_namespaces(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesMap, jsii.get(self, "kvNamespaces"))

    @builtins.property
    @jsii.member(jsii_name="mtlsCertificates")
    def mtls_certificates(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesMap, jsii.get(self, "mtlsCertificates"))

    @builtins.property
    @jsii.member(jsii_name="placement")
    def placement(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewPlacementOutputReference":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewPlacementOutputReference", jsii.get(self, "placement"))

    @builtins.property
    @jsii.member(jsii_name="queueProducers")
    def queue_producers(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersMap":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersMap", jsii.get(self, "queueProducers"))

    @builtins.property
    @jsii.member(jsii_name="r2Buckets")
    def r2_buckets(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsMap":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsMap", jsii.get(self, "r2Buckets"))

    @builtins.property
    @jsii.member(jsii_name="services")
    def services(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewServicesMap":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewServicesMap", jsii.get(self, "services"))

    @builtins.property
    @jsii.member(jsii_name="vectorizeBindings")
    def vectorize_bindings(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsMap":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsMap", jsii.get(self, "vectorizeBindings"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreview]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreview], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreview],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__764575de0c3a78152856a65f9369cd5cb4ec9a03480285cdefd43256c35694f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewPlacement",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewPlacement:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewPlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewPlacementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewPlacementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a550c946830a12f67ca2ae46e4e5de8a0d2ab24ff4b166db8e03a50c5786273)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewPlacement]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewPlacement], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewPlacement],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71d4c6fec960a0082e9341c96911f9aabfa6c51c60ae9bdfac8b2119e221695a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducers",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c45359f7c44f83807dba5c9783dc02d21ecca80c7253821be754305bd1f89407)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77f98af332b5b73d9cc6e17496939725e677691e0ae2a8cb2b158280961c0050)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fac26589cd98455529f452071647e2f9fe22f657e42136a22c40ac875a9d360f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__efc8c516a38edcae2635e2ec055553d2d7d92b798bbea629a73b3d166e769817)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__260434467c3a7e8da7f21f549ed5675b7d35fd9c739035c36c3804335a9aa6ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducers]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducers],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16f14b7eb67c09c6aa2ca24d37ef3cd8fa4c08c4fa7bdff8f5aa9de6cfd76e9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewR2Buckets",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewR2Buckets:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewR2Buckets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__436731fda8b32cd7b77a5b366658e1a0b8789e83c6e64ca01e8ab69ea250edd8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1116e4448d6dd2453c9d900c5b31bde95caa0fd8875ef5c3b3b1df5867a4d09)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cedf48521004f254203a45a44a390bc9e0bbd7b0a3fc9384f0b50a1fa2b47ae2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__62b86147c07c4ef71635f5c409d91f8c3ae8adeda086d80e4f325f5a47a77d51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__182b8ebc9c65e71053083c58bb1e1635811f2bf72f7978e5e7d9897d15d92706)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="jurisdiction")
    def jurisdiction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jurisdiction"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewR2Buckets]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewR2Buckets], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewR2Buckets],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0125575e98909c725fbf480c1a2d2d0b1ab0d8814593a5b38c4392670e5c3045)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewServices",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewServices:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewServicesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewServicesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a15a4e3e3fe23ff47c2e1c9a105eebcc429f13495ffab189e14776f409163418)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewServicesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__579ac463fff2a79606e256d9fb5edab8dec8ee0db3d71c705385a5b6831883d1)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewServicesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc04ffae039f971d0f0970f8a6c1f67cef8dc4b52188cd1485bdcf8c341a6690)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c8c78b7e2aa97cd7fc8e125af39ab53fb98c68b71f58c69502d8bdf02df4c27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewServicesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewServicesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__23708ea12aae064f4752db660ea414554a72fefc724e205a02145316d9661a14)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="entrypoint")
    def entrypoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entrypoint"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewServices]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewServices], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewServices],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85409b577f118d92b34977bf566f4e3504735af30c6baf9acd4a1d81674bc427)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e41db84edb5a4cb8fa6538ba6f855af22ec6cfce8fe5614e5dc752e02a52965e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f987558bf947420a4a715cb3979934ed18887372e6fb1e8fda87f52b52aff82e)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fa0a8f29485a72d323001edb559e0a5ab049181c0e51029c9f1fbe5f16b1e0e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c18d8d5bc333bb0f3af75ba10c4484880096b790b6805cd3034a7d0551aa169)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c54d31d4fd4e8ee6fd362e3ee1c33de5649f9a4ad99bc3b7ea8a92ecf177dc13)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="indexName")
    def index_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindings]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__310f27d463baed777af9df0bef2155bae2a665aed5a77b265dbb817d57e800c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProduction",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProduction:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProduction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionAiBindings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionAiBindings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionAiBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__212ecc65e9aba4c413fe296fd1d002fab319b9aee409380a6dcc925b3209ae23)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e73c725291afd5eca562e404a84ac4f44baf4db688dfa7c47ca4a84b077bcaa0)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0d78c2e24b45604e236daa263d20c30cc0c8cf945c7893f86886bf3fd8bd3c4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd0cfab8a1e2bf7dfffc995dfbadbd27aa5f81888dabb549667a3f458a9c2d6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c73f9f6613a2e3521e9825f8ffd53eaf61c725955f492276b2153594bd1da4c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionAiBindings]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionAiBindings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionAiBindings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0817420b4220b6e7b7698077e213217cc881fa3b02f3083925f64005f7acffe2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__22073bae01add133ba2eafec356b14a866191f47cb29403af815fab92f5230c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86934592fc087e1644501685505d57b28b04d31204caed517ca854b24fda3a62)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8db8b6b72cae404758af73ded9c1dc31a8a9684299ea950024d1958197a0cc1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2d5da3c3cd153fbdaf3c4caead4b19d674ddba55962bcbdb33b7a9bf8ec2336)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e01a28d9ab282580deae39f9572918aef526fc6becd026272c5d936a79fdff0e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="dataset")
    def dataset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataset"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9f7cd3d19341a9a44446b77650d1df8e4137fa51510da3ea0caeddb7fc17097)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionBrowsers",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionBrowsers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionBrowsers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__00cf3cfa10d7e39ff509b7797f366bb90b9f1d1e191bc01f42d3aeca07f1f7da)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb0562872c878c925f587bb0fcae0b96a8fae6848a5f104085df38baa7f17262)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ac9d373a774910d95bb25ae0beee1d83194293a1e74a6179a505ac5a78b86bc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0bc8f51e3df7e06e2571aceb1604350e2493d9b521bcdd07c722705d6f5fa009)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f59aca5813c5faf62434351f3f83117d43ca44eddadd66ac2ca10ee7d7f30a91)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionBrowsers]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionBrowsers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionBrowsers],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d0c4b6da5f90382328d88421bb4ea90b5c66a763d7dad4763d368f142689e2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionD1Databases",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionD1Databases:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionD1Databases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8aead61769aca114aee65a0c0f92f77f570bfe9564684066e6642c6e8f28c82c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db108494cdcc546a0059b1699f6a005897b3c12f45f031fce9d036953414e646)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b087e49e12357c490e625ea9c12723b06a40653409397996eefac66b465eb3f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__665d11400d610a7298e42390b6d86249b5d4438456c68384191b81f5a3fd4c05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0fee9e00d210c3ad266d444f2c4494fc880687c3cec9aba18ef6dcb15cf27820)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionD1Databases]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionD1Databases], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionD1Databases],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a710b224152d350397ef227057f0365140ac15cce83006049da929efd9cd46fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespaces",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespaces:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__94c17287370d7912c968cb6e490910b5f697c3f83050fe5fe58fef230ab1978a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13322baebca027c293ae3d71472a0e6f011d091161b8a4e9a1cc0483042dd80b)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f770aebb5a73b9e60ba0e6c70f62f3acc643ee47304b24e5b9a7a58461e3593b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__118b818dcd6113edfd5ebbefabf137f774f8d15d5fe9d3a4e179e03d5734e501)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5732821c0a8d8dc02f9585f2b64a1493a51081e64f279cd6644bd5de5f901504)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespaces]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespaces], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespaces],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cda3349f61ea8a1a6c9150e28f6086ce52383fdd31395cc5b8b21d88f922f884)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionEnvVars",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionEnvVars:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionEnvVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9b90d0b66c87642249eac61dca2df4af319933fca1c9cf9b2e71e579555a9615)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3c1243123bc42874902d354840c3886321e62492e4c453393a59f3826c2ae20)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__342f18e8f29cedb581bb6d56c8f2491230391619a723ad4f990faa326cf5de75)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f3434b4bafb34f29979654b9f0e661a0a310af37a66e56b209b6e6bc0936f2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__864e8a08bb1ca672ac87b8bd621722205a50b169919c3b735b24c65cad931dad)
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
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionEnvVars]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionEnvVars], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionEnvVars],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13fc3e5545051061c665575beae7ea052845169991ab4f593c80f05ddbbc9573)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3276c917df18c175c67cec082914607f467537f6f70ab42fe0c21f984126ddf2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4a6f4e0a6c739dd524b3a5778154f330cd5d2fdfb7b2f70b224944a439fb96d)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f685dc6178192841bc382e17c9e3e251370a0099eb9a38ee869b3c03aac4155e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ec5193c840ac995e44bf1b4a726b41584fbfc4a6e2701b4a51d7ef0f5d10c92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b284aa772a0188d889a376c4a3129f189a039d2b6466d5d4e75551e46b4197c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindings]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__187c6d33a31489e3d2fa1ef20735f2fbda805d900d8664a44c1d6facf41606d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespaces",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespaces:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64c6a2167be6fa5e82b58ac3022c0ee438798f54db377e194e536f45f36f0cf7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b18ee43373b02712f60fc511a66bad699d10d390596f14a364a1431e8b98e8c)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d024184e5209b6b2a462afe0989e79bc402e92e4d3a10868c94c1eaa503af38f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a433b1dfc1cd9367f24bbcdb866e326f0033c312ee53490d5c87c2d1fdeb69c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c52c07c09c42dbae6949b9ad845388f5089da61b41786a98a0cac8dbb22b9ed3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespaces]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespaces], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespaces],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf2cd2739e5cf84c293e6639cf46d746c8474b806dca7e6d8c3b9f9dada0b6ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificates",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificates:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f9511427ee235b5c91dd6333d7e9c6656dd22f315a517c635336ae5503874110)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2a3c5b01f587e0e7410c5e1396c048683e4596df361f9798b852b634b64b178)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__841ce55dcb62027f9f28b647070aee1e73beade517056bea9d982c1bd040d268)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1377b3fcb11f72fe1f1b1e404da74a704ec70427dc8788223ebe3055500b6a30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__317247be20cebd096fd6d2626de43468b431b191951425b7c67a94b73f443805)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificates]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eed09c700d86e9e11938229a8172286114bbb8e836bba0584cea7efc71056e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8bf16589047e86fe5c47efa0791e5e87360f2f745c2da8018383a19ebe7f93b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="aiBindings")
    def ai_bindings(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsMap, jsii.get(self, "aiBindings"))

    @builtins.property
    @jsii.member(jsii_name="analyticsEngineDatasets")
    def analytics_engine_datasets(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap, jsii.get(self, "analyticsEngineDatasets"))

    @builtins.property
    @jsii.member(jsii_name="browsers")
    def browsers(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersMap, jsii.get(self, "browsers"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityDate")
    def compatibility_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compatibilityDate"))

    @builtins.property
    @jsii.member(jsii_name="compatibilityFlags")
    def compatibility_flags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibilityFlags"))

    @builtins.property
    @jsii.member(jsii_name="d1Databases")
    def d1_databases(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesMap, jsii.get(self, "d1Databases"))

    @builtins.property
    @jsii.member(jsii_name="durableObjectNamespaces")
    def durable_object_namespaces(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap, jsii.get(self, "durableObjectNamespaces"))

    @builtins.property
    @jsii.member(jsii_name="envVars")
    def env_vars(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsMap, jsii.get(self, "envVars"))

    @builtins.property
    @jsii.member(jsii_name="hyperdriveBindings")
    def hyperdrive_bindings(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsMap, jsii.get(self, "hyperdriveBindings"))

    @builtins.property
    @jsii.member(jsii_name="kvNamespaces")
    def kv_namespaces(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesMap, jsii.get(self, "kvNamespaces"))

    @builtins.property
    @jsii.member(jsii_name="mtlsCertificates")
    def mtls_certificates(
        self,
    ) -> DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesMap:
        return typing.cast(DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesMap, jsii.get(self, "mtlsCertificates"))

    @builtins.property
    @jsii.member(jsii_name="placement")
    def placement(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionPlacementOutputReference":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionPlacementOutputReference", jsii.get(self, "placement"))

    @builtins.property
    @jsii.member(jsii_name="queueProducers")
    def queue_producers(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersMap":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersMap", jsii.get(self, "queueProducers"))

    @builtins.property
    @jsii.member(jsii_name="r2Buckets")
    def r2_buckets(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsMap":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsMap", jsii.get(self, "r2Buckets"))

    @builtins.property
    @jsii.member(jsii_name="services")
    def services(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionServicesMap":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionServicesMap", jsii.get(self, "services"))

    @builtins.property
    @jsii.member(jsii_name="vectorizeBindings")
    def vectorize_bindings(
        self,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsMap":
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsMap", jsii.get(self, "vectorizeBindings"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProduction]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProduction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProduction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd791b7eb289e7b93bd39fbffa1e34ba6a560f35deaa31423851fe6597b17e9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionPlacement",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionPlacement:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionPlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionPlacementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionPlacementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3cca6e1b52b82bbf7e1d6e779d2b6c748ae2e517203ed05dd10887140a183d12)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionPlacement]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionPlacement], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionPlacement],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72eba2211aac92bfed6148d37ea02c3d1d60db9b872fdb2f733d891ccff804e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducers",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__93d4d31bb7f9cbc01afb06d454bece8eb95c838c8ccc2a18ca843c64e044d867)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5351cd117afa28f7dd1fad0ab1001dba39ca8f6897c5e2e71f908c8acab616eb)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dfb4f74bcd58a23fccf81f7bd337e8aadf4ba590d51878437e4e59aa02493ad)
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
            type_hints = typing.get_type_hints(_typecheckingstub__863a25dcddfbf8eaa9339f1c028b85e340f3a3643e01801274b98d1137ba69e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__324cbb3cbec10ca6bc617cecbade6398092bc04f26250337965d7b0ae9f390be)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducers]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducers],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a72611432c8328d363223bad76fdcd9e63a084ef21515c329b60ad976838ea2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionR2Buckets",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionR2Buckets:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionR2Buckets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eeb15e7e9b03bf65194d54532be276580a038977439d0c0c2e9c6681ddf3519e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c266259cbc11a6a4934cc31266d00f6c8a0fe7c2947dd9421cade462b7914984)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4b43cd4c86b4b83b465580a5838edb87f44985950698cc8401b88a3f038f57b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2197c79afc4097bd2e1fb3516a0f4aed8f78692f00cd91a1f87bad8fce32c795)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__17e643550bc3cdd08f9d8a4117865f160d7b30c0fc99ecd37a3699b1f98dd81c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="jurisdiction")
    def jurisdiction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jurisdiction"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionR2Buckets]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionR2Buckets], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionR2Buckets],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cd3cecc4688e3b879f42d703f1f95fe607145bc0f0da66bc8ae55b984988ec4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionServices",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionServices:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionServicesMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionServicesMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2dc238c6a3c748f36a8b288f9a29496966a997a97a9d0e99af658bfb12403e91)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionServicesOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b83f150feccc9cf70f1625307e1db6f6c189168b3fc4df4a854ae25cc3f7a27)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionServicesOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a69e5e0409354ed33146f7f9a0b749c00f2024119a3958464d842ea61a3d44d2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3b23fa4c682d0d3d3d8cb741ff74b96ce78c3fd5a2cf75389cb1adcb2c1c4b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionServicesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionServicesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__633dc7b54d0082970c522fd25f6b5beccebaa6f3f1fd5f665b02771644a90d1f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="entrypoint")
    def entrypoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entrypoint"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionServices]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionServices], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionServices],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f835587e8fddeb21d8f97ef83d6b951630f9aa67d8a69f0b6343a0b223774020)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4321f6c5534bb09549130bbb9eddb2b57d1f193f298c28d64e80c9ce663b880)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a531396dcf9cc6c5a0b39606e2015558af2b29f965659a3b4661e7207bac8c7d)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b9e6aff48f38fd3c9cb19da2d6ef90db30fdc34c949f50320b30b7d2fe0d4f1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2004b0247fdf8bb9e5a1308d436ca22871be038d597e86d0c37f35e98306708c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__196dc1a624b44caf3b494cc65764b872f31c63281eaeafa517644bafcdb5219f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_key", value=complex_object_key, expected_type=type_hints["complex_object_key"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_key])

    @builtins.property
    @jsii.member(jsii_name="indexName")
    def index_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindings]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97434489bd5f1ac930eb2395caeeb3464d271e5b13267bd0102d25fa20b29114)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeployment",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectLatestDeployment:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectLatestDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentBuildConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectLatestDeploymentBuildConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectLatestDeploymentBuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectLatestDeploymentBuildConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentBuildConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__445a948555333e46b9394f3762d1d1bf081140ad7b0095551bb35bb377ac8126)
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
    ) -> typing.Optional[DataCloudflarePagesProjectLatestDeploymentBuildConfig]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectLatestDeploymentBuildConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentBuildConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab0d9989ec973e63c351a3132a9f8e7e09e54f3822e6f59078b89412fb92898b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentDeploymentTrigger",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectLatestDeploymentDeploymentTrigger:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectLatestDeploymentDeploymentTrigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadata",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadata:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c37fede2fe673fc599cb3676f329f4b483b24ef54d9c4184e9b0b5bdaad4f097)
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
    ) -> typing.Optional[DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadata]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadata], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadata],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__776fa88c9de26d0af6b4d749ee91aeb59d11218af439bbe3f7b3d2b9a9ef400c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c3fa64a3bb165b2b80a6c72454e06fd04a8e34d4f02cc52f29f00846e278529d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(
        self,
    ) -> DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference:
        return typing.cast(DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference, jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectLatestDeploymentDeploymentTrigger]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectLatestDeploymentDeploymentTrigger], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentDeploymentTrigger],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69ee2c4c0623d9156bf9d9cbbdabfcb3dc508a0e692f50521ce2f7a0a89aca0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentEnvVars",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectLatestDeploymentEnvVars:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectLatestDeploymentEnvVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectLatestDeploymentEnvVarsMap(
    _cdktf_9a9027ec.ComplexMap,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentEnvVarsMap",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fee6bbbe9e0b1f7f91055c941aaf54effd1e46860a09c3b67f03b267794710d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="get")
    def get(
        self,
        key: builtins.str,
    ) -> "DataCloudflarePagesProjectLatestDeploymentEnvVarsOutputReference":
        '''
        :param key: the key of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c30184d8ad1838e2229d2c35130e928b0033f03973a6c825ddae4ef9ad861494)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("DataCloudflarePagesProjectLatestDeploymentEnvVarsOutputReference", jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb8ad184e3b89c550abb749ddb832e89555253274b5a137cfa6868510a64cddd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__58e7c1276f8bf4ee9c8479a07b03e5bef82e0572e04e60ca30aaaa2efa0ff0b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectLatestDeploymentEnvVarsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentEnvVarsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b089edf93e39e59dcebf5eb0cebb5d3c167864636ce4d7ae078dc16a1deb8d7b)
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
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectLatestDeploymentEnvVars]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectLatestDeploymentEnvVars], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentEnvVars],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60adae4c3470208a1b1474c5a88f227194293631d969a2dc0b7f633cad2628fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentLatestStage",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectLatestDeploymentLatestStage:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectLatestDeploymentLatestStage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectLatestDeploymentLatestStageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentLatestStageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__390d3ef34cc842cdaddd76f03f4c0c11cd85c837f6e0296ce317966afa1be675)
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
    ) -> typing.Optional[DataCloudflarePagesProjectLatestDeploymentLatestStage]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectLatestDeploymentLatestStage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentLatestStage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c60ed694c188f9dae33ec23712d974358ecbd52172d5ff619324a787eba30fa2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectLatestDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__25a19ba1a591e66195e85754b1a82a2e24edb577b82f7cbfec1d42e337c5c96d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "aliases"))

    @builtins.property
    @jsii.member(jsii_name="buildConfig")
    def build_config(
        self,
    ) -> DataCloudflarePagesProjectLatestDeploymentBuildConfigOutputReference:
        return typing.cast(DataCloudflarePagesProjectLatestDeploymentBuildConfigOutputReference, jsii.get(self, "buildConfig"))

    @builtins.property
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="deploymentTrigger")
    def deployment_trigger(
        self,
    ) -> DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerOutputReference:
        return typing.cast(DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerOutputReference, jsii.get(self, "deploymentTrigger"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @builtins.property
    @jsii.member(jsii_name="envVars")
    def env_vars(self) -> DataCloudflarePagesProjectLatestDeploymentEnvVarsMap:
        return typing.cast(DataCloudflarePagesProjectLatestDeploymentEnvVarsMap, jsii.get(self, "envVars"))

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
    def latest_stage(
        self,
    ) -> DataCloudflarePagesProjectLatestDeploymentLatestStageOutputReference:
        return typing.cast(DataCloudflarePagesProjectLatestDeploymentLatestStageOutputReference, jsii.get(self, "latestStage"))

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
    def source(
        self,
    ) -> "DataCloudflarePagesProjectLatestDeploymentSourceOutputReference":
        return typing.cast("DataCloudflarePagesProjectLatestDeploymentSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> "DataCloudflarePagesProjectLatestDeploymentStagesList":
        return typing.cast("DataCloudflarePagesProjectLatestDeploymentStagesList", jsii.get(self, "stages"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectLatestDeployment]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectLatestDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectLatestDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecc89c85fe5be035fc63edca52bb06df2697bddc77aeb4cb20230c70b49028c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentSource",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectLatestDeploymentSource:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectLatestDeploymentSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentSourceConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectLatestDeploymentSourceConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectLatestDeploymentSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectLatestDeploymentSourceConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentSourceConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__52b75eb1afb66c9418b1e5ff9d24bca3407fca8ead0bbe2ef5780b35dda428a9)
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
    ) -> typing.Optional[DataCloudflarePagesProjectLatestDeploymentSourceConfig]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectLatestDeploymentSourceConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentSourceConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5e6adca1b6093a842148141ed3e65c9366640f5d9bbe36c43deb504fad5f87a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectLatestDeploymentSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6a45648dad0bf588af8f95e64a580dcc04b8d9606e7654381b01b5109490493)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(
        self,
    ) -> DataCloudflarePagesProjectLatestDeploymentSourceConfigOutputReference:
        return typing.cast(DataCloudflarePagesProjectLatestDeploymentSourceConfigOutputReference, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectLatestDeploymentSource]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectLatestDeploymentSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__826a616fe7c45da30a7d813d32e10ed014b6186092ced40a975f0ce8030d6358)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentStages",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectLatestDeploymentStages:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectLatestDeploymentStages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectLatestDeploymentStagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentStagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__802b2984c1abb79eab5091aaa40f475b8624fbac9636704c1eb77df3a76a0226)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflarePagesProjectLatestDeploymentStagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8127778360b403339fa4f77643e300e037b5592c34b14f7b3d6c6098cf6e43f8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflarePagesProjectLatestDeploymentStagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca95d3aae176b5304a537e07fe17d787f3a8ed459b13dab74937940622241fc0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ad0d31ff710052eddd78b62ad25f87752da81d2f43a1f61416d1c3aa2b7edfd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fc2489beed121a7c424fb4e215021e25c674a9f13540b84846639e394e6ab99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectLatestDeploymentStagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectLatestDeploymentStagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4361a4a868b6965da702444171a36da07f5a4af65065491915a4573306b0bbf0)
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
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflarePagesProjectLatestDeploymentStages]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectLatestDeploymentStages], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentStages],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03ad33c5542b3717edc58e2eddda6e9e63925b026038330eb2f13ab05179d457)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectSource",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectSource:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectSourceConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflarePagesProjectSourceConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflarePagesProjectSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflarePagesProjectSourceConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectSourceConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f563260e6c4a0f43f9e7f8eec47109666a961123988240ce9bc81be33e87d65d)
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
    def internal_value(self) -> typing.Optional[DataCloudflarePagesProjectSourceConfig]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectSourceConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectSourceConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__777cc299282782ba58988e4ca26978c6dacdbe250fed348a6ea1e32a97b432e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflarePagesProjectSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflarePagesProject.DataCloudflarePagesProjectSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d65bfc775b2296f2b9cf7ec8824b4d9109c9bcf5b838f10172d6ed54e328357)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> DataCloudflarePagesProjectSourceConfigOutputReference:
        return typing.cast(DataCloudflarePagesProjectSourceConfigOutputReference, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataCloudflarePagesProjectSource]:
        return typing.cast(typing.Optional[DataCloudflarePagesProjectSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflarePagesProjectSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c19aceefa36713ee0a82e5b91d54bd6ec23815b2bccf73f2a587d8b10517f5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflarePagesProject",
    "DataCloudflarePagesProjectBuildConfig",
    "DataCloudflarePagesProjectBuildConfigOutputReference",
    "DataCloudflarePagesProjectCanonicalDeployment",
    "DataCloudflarePagesProjectCanonicalDeploymentBuildConfig",
    "DataCloudflarePagesProjectCanonicalDeploymentBuildConfigOutputReference",
    "DataCloudflarePagesProjectCanonicalDeploymentDeploymentTrigger",
    "DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadata",
    "DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadataOutputReference",
    "DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerOutputReference",
    "DataCloudflarePagesProjectCanonicalDeploymentEnvVars",
    "DataCloudflarePagesProjectCanonicalDeploymentEnvVarsMap",
    "DataCloudflarePagesProjectCanonicalDeploymentEnvVarsOutputReference",
    "DataCloudflarePagesProjectCanonicalDeploymentLatestStage",
    "DataCloudflarePagesProjectCanonicalDeploymentLatestStageOutputReference",
    "DataCloudflarePagesProjectCanonicalDeploymentOutputReference",
    "DataCloudflarePagesProjectCanonicalDeploymentSource",
    "DataCloudflarePagesProjectCanonicalDeploymentSourceConfig",
    "DataCloudflarePagesProjectCanonicalDeploymentSourceConfigOutputReference",
    "DataCloudflarePagesProjectCanonicalDeploymentSourceOutputReference",
    "DataCloudflarePagesProjectCanonicalDeploymentStages",
    "DataCloudflarePagesProjectCanonicalDeploymentStagesList",
    "DataCloudflarePagesProjectCanonicalDeploymentStagesOutputReference",
    "DataCloudflarePagesProjectConfig",
    "DataCloudflarePagesProjectDeploymentConfigs",
    "DataCloudflarePagesProjectDeploymentConfigsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreview",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindings",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindingsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasetsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsers",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsersOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewD1Databases",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewD1DatabasesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespaces",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespacesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVars",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVarsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindings",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindingsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespaces",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespacesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificates",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificatesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewPlacement",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewPlacementOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducers",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducersOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewR2Buckets",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewR2BucketsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewServices",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewServicesMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewServicesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindings",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsMap",
    "DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindingsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProduction",
    "DataCloudflarePagesProjectDeploymentConfigsProductionAiBindings",
    "DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionAiBindingsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets",
    "DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasetsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionBrowsers",
    "DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionBrowsersOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionD1Databases",
    "DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionD1DatabasesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespaces",
    "DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespacesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionEnvVars",
    "DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionEnvVarsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindings",
    "DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindingsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespaces",
    "DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespacesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificates",
    "DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificatesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionPlacement",
    "DataCloudflarePagesProjectDeploymentConfigsProductionPlacementOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducers",
    "DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducersOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionR2Buckets",
    "DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionR2BucketsOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionServices",
    "DataCloudflarePagesProjectDeploymentConfigsProductionServicesMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionServicesOutputReference",
    "DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindings",
    "DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsMap",
    "DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindingsOutputReference",
    "DataCloudflarePagesProjectLatestDeployment",
    "DataCloudflarePagesProjectLatestDeploymentBuildConfig",
    "DataCloudflarePagesProjectLatestDeploymentBuildConfigOutputReference",
    "DataCloudflarePagesProjectLatestDeploymentDeploymentTrigger",
    "DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadata",
    "DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadataOutputReference",
    "DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerOutputReference",
    "DataCloudflarePagesProjectLatestDeploymentEnvVars",
    "DataCloudflarePagesProjectLatestDeploymentEnvVarsMap",
    "DataCloudflarePagesProjectLatestDeploymentEnvVarsOutputReference",
    "DataCloudflarePagesProjectLatestDeploymentLatestStage",
    "DataCloudflarePagesProjectLatestDeploymentLatestStageOutputReference",
    "DataCloudflarePagesProjectLatestDeploymentOutputReference",
    "DataCloudflarePagesProjectLatestDeploymentSource",
    "DataCloudflarePagesProjectLatestDeploymentSourceConfig",
    "DataCloudflarePagesProjectLatestDeploymentSourceConfigOutputReference",
    "DataCloudflarePagesProjectLatestDeploymentSourceOutputReference",
    "DataCloudflarePagesProjectLatestDeploymentStages",
    "DataCloudflarePagesProjectLatestDeploymentStagesList",
    "DataCloudflarePagesProjectLatestDeploymentStagesOutputReference",
    "DataCloudflarePagesProjectSource",
    "DataCloudflarePagesProjectSourceConfig",
    "DataCloudflarePagesProjectSourceConfigOutputReference",
    "DataCloudflarePagesProjectSourceOutputReference",
]

publication.publish()

def _typecheckingstub__28c3d923c53d257abb72acc4e69bb02e82519a05c675d6325c407b03ab41821e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    project_name: builtins.str,
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

def _typecheckingstub__f8d85119577f3426feec435c61241aeb056560c5e06fb04de3b9ba9a326d4120(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b244d8ab6aa84e48096112166489ed3b9a538f3090480a6f5b10c65f91edb358(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c773933cd807e083fab2bd532eae8696d8837f83138027f077762e85c13a1046(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__430d134c45e6ac585928db325c427a0c7988117af9c3c5797f8492471915da30(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e03751b6951a8adb33d59f35ba5449e1739888b826e88016eaf814462bfe2b11(
    value: typing.Optional[DataCloudflarePagesProjectBuildConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90adcb3a9b23b82396b7dd9acce2c79f3342dcd1f7e20a40837cb43679dd9c6c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__651bfd22d1902aae4303f24a9acbec02695ab9b780ae84e3d7679bd15b3eccfb(
    value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentBuildConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5baba266ff035dc553e72a3e4cfbc626e1b5278d77a1837c58613b925544c90c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a19c47e43fc63118881de5423ffc9cea55099315d5dd3edae6b47380191ffaa(
    value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentDeploymentTriggerMetadata],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcd88d2717897dccbe8aab672cf2e39e1711aee104066d3766378d698c3c3c4f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3749908aadf33cd11992c04fb9d7faf46b15574c04e38f1fdc3b591d558d5cde(
    value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentDeploymentTrigger],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae46060a709e51fed10f3b671c57632e5bc97406b83007ed189fd6e509b4e315(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08bcb54ad5b577986457e305e6b3b711be91ee00824dcf328004c2f316f86504(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd9fc07d494af6d89f719380648f349037e2a9339f64551166f1326cbc22a8ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecaca156513ea76d36179709fafcdbf5ce5d6354734cc4598f0a05a50c977af3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2007e3b71f4df7fb219b1c7e8584ff72ba83503f637ea72e7df2d7796cbcafba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e5b224ddf80c0a92cc9bc25168db7723fe528d3b7be2dd1fdc1930fad1527f8(
    value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentEnvVars],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2edd210c583a8baef5839283baccd1a607fe816aace4d3fcf8072c5ab973b4e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b320009eca26cba94da86c322b8a21a8fe3a11100b88ab30434a43719f3ca3f6(
    value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentLatestStage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c6180694edc3287236fd097c9f80e61cd9c316fdd65d47a18b773b127a00f9b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a892c8fa189156fb9a2fe0d331dea973460cef566e1e35e5fb20c58b9fd230e(
    value: typing.Optional[DataCloudflarePagesProjectCanonicalDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e721b5bebc1e17473eec22b4f12f40e038355be064c9d6dee37d8e3f0e2f0946(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__912d4cd293634eb81eb405a36ba95574aafc093e4b2a5eaf1b7570b9ebaa5c6f(
    value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentSourceConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ada5776e2969fde0c54cc0ff0d931d640155b69509c6c5720e8871445ce1efed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__224faf66b90006fc05934161e5f60dc294b2ba57639ef59351978a83f131fc89(
    value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b210b79a7be18e302863a3167814def09e5da6628223eb9111c1361302348a05(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03737ab0a34f9854343abc859f11720a2055e65e645dcc998cdc9a9dbe5533a9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e0df3d3ecb02ae025e130e9e906fa1f6370d903f744db853016238aa490600c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__787a273a733cba84bdcdfc5595c91779f1c46e478a32c9185a49404c06727dc5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__842c05221e9bee66d49187b2908e9a4bb5a5e4ca967f04aab85625d01c0abda1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c9ab04f3f156693dd51d2c20fe7157d0d0a5efb97e77bf123f9cc14f5a56b3d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27f1d6355785d5e7ba36c0b6f8169b5e365488f76a909ef7fbd1824a328b0dcf(
    value: typing.Optional[DataCloudflarePagesProjectCanonicalDeploymentStages],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a09884f4778ddf926e480a069239e7001433cd8b75895abb9a699485c061087(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    project_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2837ffd4e6c40fe6b02224c3e6f8f449a14ee8dae981762aa05a61b1e97338b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c88b01e12d5a968a1c88218fb7b777890e68b44f5dd0f56af5d83c92c9f91e5(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__839305a5e99af106e790728c27938209f78ecdd75c65ede840f2bc187deca8b8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecf83a2b3eac1ba68266961dd272b7992344526695c7ae318764b95770efb47b(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e4c5355b0e036d3009b348eceb009c7ad332e6eebaca70cd8f7d49cb4545bf4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bf77bc4ffeaed330aeacea523e1203b4a0077b09224042166756f0e64d17a6e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20bc5e7f8c33c4d88c65a8a6c45b6489141782e1f09e8385079db1eb337a2d9c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed0fe383ea716c8c2270e19e774c4458ce7a8fd3d79cb7fab21c885fd48d8a40(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewAiBindings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de1579af09e789a0cb1cae4e8a453a7159e49358452b22dc393ee7e3e2764896(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0015cb58f97e9cd83a7a135539908fc331a16fa6e30efe783f9183b2d03a58a1(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14c68f133d78f1e8d2fc5b1a42287e9ed622e6872719eaa6429677d64cabb148(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__065be37dd6eeec5372948f35b4c491030ef134de1c220099f3d46c0d36cc6d43(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e3e1c97b212b55c1d4c780f34d6d1829660492ec92b9e1cfe353b295107095d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6f1ca90a9d6d013099863085566748215f5643d764528bf008218b72d5b5275(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewAnalyticsEngineDatasets],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e741d590242b999d437399a48d1076320e1b1024da0260982eda519c87e0ed12(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dde82e1ff9123e5060f03505e58c9718ab392fce436541fc29bf093108754377(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3520d9e777fafc33ea4e55fd11b5dd27f2dbaa8515878e9d68739ac6b0423a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09f17a35cfe54cb649f5cb8fdc07a54a67e82141def1ee372b159fab687a28d3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__864f112745cbe689c5bd79ddcd5571915b9e95f7187bba8981a002c24e773dcf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f1c513eb0e8935a9f90d1c64b00da758f83c027f0cdefce13befb2500bc9b80(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewBrowsers],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2099015f0bef7940359ba5a59ce917b907a687c00b4d8a9f841b6d34c2f23f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e255aeb5f4453ffc28ac60aae92eda0ff8392f9bc22b10b18e6b2aff2a70dff(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__017ea8dda5ef892cd870f4dba379b322e056105330d13476ae1947023a7b3959(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fbd6104e7dd569196452b0d297499cfec4054febfef3d52a151b08ee3633408(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ffc84cb1f95966efd6e8ca18d76f085741162166953d3730a3f4dad6f288f99(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65480843b74ce139084331aee1c641e77739a7d52351bac168b1bde75bdf6f64(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewD1Databases],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d07e6fcffb6c7a148ae001e9655be86a7f67be7fac60df699d8ebfc31309db1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d9fc8abfcad0802795613e3e063a9f39ce5d65ced9b111566dcf5b73be1da89(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75864cbbbeddf931587cc7d8765aa549e5dfa19fcad3f41d9168817f0d07511e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b41184dc583da48a204494619700eeda07b114797dec275a110c8b13c165ca(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f090ba5b5a67c9f326a09f2830cd1769c085402747df55ad982aa8fd94c946f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4590d74f7039cf2d5aaf184e1a9b31182c0b6ffec5d1c3869312d7c34ad5a7d(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewDurableObjectNamespaces],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b0fdcc3f1fcbbbb6ddc48886b3c97e71d9c44df4231f31ee37e2f3acf0b08e1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55e473212500cabc8b20cc5837e257cf3eb466021fb6bd30bf7e6bb3bc596ac2(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38be2cfc9264f3feea923fad4270bacb67e715d7616af654ac315ad79e27c37e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__863b7f6a9c6c17e7fa842cd5acf4b4d4252666e1c423231edd33a170fa0b5ee1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3908d7aeb48757388b95bb0ff8fda293bd34e3819107e087237794a8883ee8f3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a047212e5405e9fcf98a00072c6de64954441089cee4810f78b27cbdfa1d438(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewEnvVars],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7374a4e94110f3a05e8be902ba4d8a2e07756a60aeac2b1ce63a596ed1f11d2f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4ad9a38a7d922aff0cd5cbc3c5fca99c215decfb9591ec5dc1790f3f30e136a(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1748ab4b2f51b7f33dea9e6316d7da3eb2ed8062f76c261e663352080fa5a8fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cad1fc118a22c70a26daa9096e996d8d7aaea97e0c51c5a7aaa1f13467d01b2d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae09d742a6f7d2dd32779e84cc0f70ddbb319929df99b23aab0cc5fbb6a957f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7c93c217354788b5bb26ad5d5f48be1137b2085401114f1cbf0c4c1ea59277f(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewHyperdriveBindings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd22983d3151cb6570a4e2c1254c29d0025a6458c90ceb181a334f329b435da1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7992bda975cadcd222cab58724d0a99bc7f2f439f1b4d93a743977b4f99d411(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6c126b358ff8f998173006c3aeb089a05eff7d464cca5cab9be8dd47dad24d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6aac2c9e5bb34b1ec5138ae30081ae26c6e4c87eb69bf555081cbef369224ac(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fabd0a026428a1174817bb1be495f11c3227c5ce0959716f291b0bce4687cc46(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__273b73c5dfa78e63c8fa02a5128c67e5d2a1d1528c28d0c015dde3f75e04bb2f(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewKvNamespaces],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__221dda65d2623691556c2dc5c414dcef0dc27ce1c97c41a548721b396726e6cc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e0073a991a97240a5dc8382f30eed80f9db7180270ab8a5bb546692e2898399(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3633ae37b67bc7fb253feb8336fc9e0130afec1c634d6969037af66ac12a5489(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c374cb44803d05a10e968dfba7736255bee93df54936782a90a59a1b9e9a55c1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f502264e5cb97ae43e75ac4e524001e9e086e6c7bf87be47efa02e6e9f21046(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1ebf5626ad7ceba996e122a4edc3666c20a67738f14901be325ee1a9f37cea6(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewMtlsCertificates],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b438ab4adf8fec50914431359e23bc61b7525286521ab77c30b038454ecb1095(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__764575de0c3a78152856a65f9369cd5cb4ec9a03480285cdefd43256c35694f2(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreview],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a550c946830a12f67ca2ae46e4e5de8a0d2ab24ff4b166db8e03a50c5786273(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d4c6fec960a0082e9341c96911f9aabfa6c51c60ae9bdfac8b2119e221695a(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewPlacement],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c45359f7c44f83807dba5c9783dc02d21ecca80c7253821be754305bd1f89407(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77f98af332b5b73d9cc6e17496939725e677691e0ae2a8cb2b158280961c0050(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fac26589cd98455529f452071647e2f9fe22f657e42136a22c40ac875a9d360f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efc8c516a38edcae2635e2ec055553d2d7d92b798bbea629a73b3d166e769817(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__260434467c3a7e8da7f21f549ed5675b7d35fd9c739035c36c3804335a9aa6ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16f14b7eb67c09c6aa2ca24d37ef3cd8fa4c08c4fa7bdff8f5aa9de6cfd76e9c(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewQueueProducers],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__436731fda8b32cd7b77a5b366658e1a0b8789e83c6e64ca01e8ab69ea250edd8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1116e4448d6dd2453c9d900c5b31bde95caa0fd8875ef5c3b3b1df5867a4d09(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cedf48521004f254203a45a44a390bc9e0bbd7b0a3fc9384f0b50a1fa2b47ae2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62b86147c07c4ef71635f5c409d91f8c3ae8adeda086d80e4f325f5a47a77d51(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__182b8ebc9c65e71053083c58bb1e1635811f2bf72f7978e5e7d9897d15d92706(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0125575e98909c725fbf480c1a2d2d0b1ab0d8814593a5b38c4392670e5c3045(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewR2Buckets],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a15a4e3e3fe23ff47c2e1c9a105eebcc429f13495ffab189e14776f409163418(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__579ac463fff2a79606e256d9fb5edab8dec8ee0db3d71c705385a5b6831883d1(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc04ffae039f971d0f0970f8a6c1f67cef8dc4b52188cd1485bdcf8c341a6690(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c8c78b7e2aa97cd7fc8e125af39ab53fb98c68b71f58c69502d8bdf02df4c27(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23708ea12aae064f4752db660ea414554a72fefc724e205a02145316d9661a14(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85409b577f118d92b34977bf566f4e3504735af30c6baf9acd4a1d81674bc427(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewServices],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e41db84edb5a4cb8fa6538ba6f855af22ec6cfce8fe5614e5dc752e02a52965e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f987558bf947420a4a715cb3979934ed18887372e6fb1e8fda87f52b52aff82e(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fa0a8f29485a72d323001edb559e0a5ab049181c0e51029c9f1fbe5f16b1e0e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c18d8d5bc333bb0f3af75ba10c4484880096b790b6805cd3034a7d0551aa169(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c54d31d4fd4e8ee6fd362e3ee1c33de5649f9a4ad99bc3b7ea8a92ecf177dc13(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__310f27d463baed777af9df0bef2155bae2a665aed5a77b265dbb817d57e800c0(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsPreviewVectorizeBindings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__212ecc65e9aba4c413fe296fd1d002fab319b9aee409380a6dcc925b3209ae23(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e73c725291afd5eca562e404a84ac4f44baf4db688dfa7c47ca4a84b077bcaa0(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0d78c2e24b45604e236daa263d20c30cc0c8cf945c7893f86886bf3fd8bd3c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd0cfab8a1e2bf7dfffc995dfbadbd27aa5f81888dabb549667a3f458a9c2d6e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c73f9f6613a2e3521e9825f8ffd53eaf61c725955f492276b2153594bd1da4c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0817420b4220b6e7b7698077e213217cc881fa3b02f3083925f64005f7acffe2(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionAiBindings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22073bae01add133ba2eafec356b14a866191f47cb29403af815fab92f5230c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86934592fc087e1644501685505d57b28b04d31204caed517ca854b24fda3a62(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8db8b6b72cae404758af73ded9c1dc31a8a9684299ea950024d1958197a0cc1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2d5da3c3cd153fbdaf3c4caead4b19d674ddba55962bcbdb33b7a9bf8ec2336(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e01a28d9ab282580deae39f9572918aef526fc6becd026272c5d936a79fdff0e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9f7cd3d19341a9a44446b77650d1df8e4137fa51510da3ea0caeddb7fc17097(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionAnalyticsEngineDatasets],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00cf3cfa10d7e39ff509b7797f366bb90b9f1d1e191bc01f42d3aeca07f1f7da(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb0562872c878c925f587bb0fcae0b96a8fae6848a5f104085df38baa7f17262(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ac9d373a774910d95bb25ae0beee1d83194293a1e74a6179a505ac5a78b86bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bc8f51e3df7e06e2571aceb1604350e2493d9b521bcdd07c722705d6f5fa009(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f59aca5813c5faf62434351f3f83117d43ca44eddadd66ac2ca10ee7d7f30a91(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d0c4b6da5f90382328d88421bb4ea90b5c66a763d7dad4763d368f142689e2b(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionBrowsers],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8aead61769aca114aee65a0c0f92f77f570bfe9564684066e6642c6e8f28c82c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db108494cdcc546a0059b1699f6a005897b3c12f45f031fce9d036953414e646(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b087e49e12357c490e625ea9c12723b06a40653409397996eefac66b465eb3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__665d11400d610a7298e42390b6d86249b5d4438456c68384191b81f5a3fd4c05(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fee9e00d210c3ad266d444f2c4494fc880687c3cec9aba18ef6dcb15cf27820(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a710b224152d350397ef227057f0365140ac15cce83006049da929efd9cd46fe(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionD1Databases],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94c17287370d7912c968cb6e490910b5f697c3f83050fe5fe58fef230ab1978a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13322baebca027c293ae3d71472a0e6f011d091161b8a4e9a1cc0483042dd80b(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f770aebb5a73b9e60ba0e6c70f62f3acc643ee47304b24e5b9a7a58461e3593b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__118b818dcd6113edfd5ebbefabf137f774f8d15d5fe9d3a4e179e03d5734e501(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5732821c0a8d8dc02f9585f2b64a1493a51081e64f279cd6644bd5de5f901504(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cda3349f61ea8a1a6c9150e28f6086ce52383fdd31395cc5b8b21d88f922f884(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionDurableObjectNamespaces],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b90d0b66c87642249eac61dca2df4af319933fca1c9cf9b2e71e579555a9615(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3c1243123bc42874902d354840c3886321e62492e4c453393a59f3826c2ae20(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__342f18e8f29cedb581bb6d56c8f2491230391619a723ad4f990faa326cf5de75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f3434b4bafb34f29979654b9f0e661a0a310af37a66e56b209b6e6bc0936f2d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__864e8a08bb1ca672ac87b8bd621722205a50b169919c3b735b24c65cad931dad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13fc3e5545051061c665575beae7ea052845169991ab4f593c80f05ddbbc9573(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionEnvVars],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3276c917df18c175c67cec082914607f467537f6f70ab42fe0c21f984126ddf2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4a6f4e0a6c739dd524b3a5778154f330cd5d2fdfb7b2f70b224944a439fb96d(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f685dc6178192841bc382e17c9e3e251370a0099eb9a38ee869b3c03aac4155e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ec5193c840ac995e44bf1b4a726b41584fbfc4a6e2701b4a51d7ef0f5d10c92(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b284aa772a0188d889a376c4a3129f189a039d2b6466d5d4e75551e46b4197c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__187c6d33a31489e3d2fa1ef20735f2fbda805d900d8664a44c1d6facf41606d2(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionHyperdriveBindings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64c6a2167be6fa5e82b58ac3022c0ee438798f54db377e194e536f45f36f0cf7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b18ee43373b02712f60fc511a66bad699d10d390596f14a364a1431e8b98e8c(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d024184e5209b6b2a462afe0989e79bc402e92e4d3a10868c94c1eaa503af38f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a433b1dfc1cd9367f24bbcdb866e326f0033c312ee53490d5c87c2d1fdeb69c7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c52c07c09c42dbae6949b9ad845388f5089da61b41786a98a0cac8dbb22b9ed3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf2cd2739e5cf84c293e6639cf46d746c8474b806dca7e6d8c3b9f9dada0b6ca(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionKvNamespaces],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9511427ee235b5c91dd6333d7e9c6656dd22f315a517c635336ae5503874110(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2a3c5b01f587e0e7410c5e1396c048683e4596df361f9798b852b634b64b178(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__841ce55dcb62027f9f28b647070aee1e73beade517056bea9d982c1bd040d268(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1377b3fcb11f72fe1f1b1e404da74a704ec70427dc8788223ebe3055500b6a30(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__317247be20cebd096fd6d2626de43468b431b191951425b7c67a94b73f443805(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eed09c700d86e9e11938229a8172286114bbb8e836bba0584cea7efc71056e8(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionMtlsCertificates],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8bf16589047e86fe5c47efa0791e5e87360f2f745c2da8018383a19ebe7f93b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd791b7eb289e7b93bd39fbffa1e34ba6a560f35deaa31423851fe6597b17e9f(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProduction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cca6e1b52b82bbf7e1d6e779d2b6c748ae2e517203ed05dd10887140a183d12(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72eba2211aac92bfed6148d37ea02c3d1d60db9b872fdb2f733d891ccff804e2(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionPlacement],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93d4d31bb7f9cbc01afb06d454bece8eb95c838c8ccc2a18ca843c64e044d867(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5351cd117afa28f7dd1fad0ab1001dba39ca8f6897c5e2e71f908c8acab616eb(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dfb4f74bcd58a23fccf81f7bd337e8aadf4ba590d51878437e4e59aa02493ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__863a25dcddfbf8eaa9339f1c028b85e340f3a3643e01801274b98d1137ba69e3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__324cbb3cbec10ca6bc617cecbade6398092bc04f26250337965d7b0ae9f390be(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a72611432c8328d363223bad76fdcd9e63a084ef21515c329b60ad976838ea2(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionQueueProducers],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb15e7e9b03bf65194d54532be276580a038977439d0c0c2e9c6681ddf3519e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c266259cbc11a6a4934cc31266d00f6c8a0fe7c2947dd9421cade462b7914984(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4b43cd4c86b4b83b465580a5838edb87f44985950698cc8401b88a3f038f57b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2197c79afc4097bd2e1fb3516a0f4aed8f78692f00cd91a1f87bad8fce32c795(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17e643550bc3cdd08f9d8a4117865f160d7b30c0fc99ecd37a3699b1f98dd81c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cd3cecc4688e3b879f42d703f1f95fe607145bc0f0da66bc8ae55b984988ec4(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionR2Buckets],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dc238c6a3c748f36a8b288f9a29496966a997a97a9d0e99af658bfb12403e91(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b83f150feccc9cf70f1625307e1db6f6c189168b3fc4df4a854ae25cc3f7a27(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a69e5e0409354ed33146f7f9a0b749c00f2024119a3958464d842ea61a3d44d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b23fa4c682d0d3d3d8cb741ff74b96ce78c3fd5a2cf75389cb1adcb2c1c4b6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__633dc7b54d0082970c522fd25f6b5beccebaa6f3f1fd5f665b02771644a90d1f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f835587e8fddeb21d8f97ef83d6b951630f9aa67d8a69f0b6343a0b223774020(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionServices],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4321f6c5534bb09549130bbb9eddb2b57d1f193f298c28d64e80c9ce663b880(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a531396dcf9cc6c5a0b39606e2015558af2b29f965659a3b4661e7207bac8c7d(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b9e6aff48f38fd3c9cb19da2d6ef90db30fdc34c949f50320b30b7d2fe0d4f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2004b0247fdf8bb9e5a1308d436ca22871be038d597e86d0c37f35e98306708c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__196dc1a624b44caf3b494cc65764b872f31c63281eaeafa517644bafcdb5219f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97434489bd5f1ac930eb2395caeeb3464d271e5b13267bd0102d25fa20b29114(
    value: typing.Optional[DataCloudflarePagesProjectDeploymentConfigsProductionVectorizeBindings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__445a948555333e46b9394f3762d1d1bf081140ad7b0095551bb35bb377ac8126(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab0d9989ec973e63c351a3132a9f8e7e09e54f3822e6f59078b89412fb92898b(
    value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentBuildConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c37fede2fe673fc599cb3676f329f4b483b24ef54d9c4184e9b0b5bdaad4f097(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__776fa88c9de26d0af6b4d749ee91aeb59d11218af439bbe3f7b3d2b9a9ef400c(
    value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentDeploymentTriggerMetadata],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3fa64a3bb165b2b80a6c72454e06fd04a8e34d4f02cc52f29f00846e278529d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69ee2c4c0623d9156bf9d9cbbdabfcb3dc508a0e692f50521ce2f7a0a89aca0c(
    value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentDeploymentTrigger],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fee6bbbe9e0b1f7f91055c941aaf54effd1e46860a09c3b67f03b267794710d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c30184d8ad1838e2229d2c35130e928b0033f03973a6c825ddae4ef9ad861494(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb8ad184e3b89c550abb749ddb832e89555253274b5a137cfa6868510a64cddd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e7c1276f8bf4ee9c8479a07b03e5bef82e0572e04e60ca30aaaa2efa0ff0b7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b089edf93e39e59dcebf5eb0cebb5d3c167864636ce4d7ae078dc16a1deb8d7b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60adae4c3470208a1b1474c5a88f227194293631d969a2dc0b7f633cad2628fb(
    value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentEnvVars],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__390d3ef34cc842cdaddd76f03f4c0c11cd85c837f6e0296ce317966afa1be675(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c60ed694c188f9dae33ec23712d974358ecbd52172d5ff619324a787eba30fa2(
    value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentLatestStage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a19ba1a591e66195e85754b1a82a2e24edb577b82f7cbfec1d42e337c5c96d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecc89c85fe5be035fc63edca52bb06df2697bddc77aeb4cb20230c70b49028c3(
    value: typing.Optional[DataCloudflarePagesProjectLatestDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52b75eb1afb66c9418b1e5ff9d24bca3407fca8ead0bbe2ef5780b35dda428a9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5e6adca1b6093a842148141ed3e65c9366640f5d9bbe36c43deb504fad5f87a(
    value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentSourceConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6a45648dad0bf588af8f95e64a580dcc04b8d9606e7654381b01b5109490493(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__826a616fe7c45da30a7d813d32e10ed014b6186092ced40a975f0ce8030d6358(
    value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__802b2984c1abb79eab5091aaa40f475b8624fbac9636704c1eb77df3a76a0226(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8127778360b403339fa4f77643e300e037b5592c34b14f7b3d6c6098cf6e43f8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca95d3aae176b5304a537e07fe17d787f3a8ed459b13dab74937940622241fc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ad0d31ff710052eddd78b62ad25f87752da81d2f43a1f61416d1c3aa2b7edfd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fc2489beed121a7c424fb4e215021e25c674a9f13540b84846639e394e6ab99(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4361a4a868b6965da702444171a36da07f5a4af65065491915a4573306b0bbf0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03ad33c5542b3717edc58e2eddda6e9e63925b026038330eb2f13ab05179d457(
    value: typing.Optional[DataCloudflarePagesProjectLatestDeploymentStages],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f563260e6c4a0f43f9e7f8eec47109666a961123988240ce9bc81be33e87d65d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__777cc299282782ba58988e4ca26978c6dacdbe250fed348a6ea1e32a97b432e7(
    value: typing.Optional[DataCloudflarePagesProjectSourceConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d65bfc775b2296f2b9cf7ec8824b4d9109c9bcf5b838f10172d6ed54e328357(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c19aceefa36713ee0a82e5b91d54bd6ec23815b2bccf73f2a587d8b10517f5c(
    value: typing.Optional[DataCloudflarePagesProjectSource],
) -> None:
    """Type checking stubs"""
    pass
