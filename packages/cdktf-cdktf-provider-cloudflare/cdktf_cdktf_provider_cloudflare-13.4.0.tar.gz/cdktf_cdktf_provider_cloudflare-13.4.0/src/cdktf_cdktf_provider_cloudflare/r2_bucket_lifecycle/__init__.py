r'''
# `cloudflare_r2_bucket_lifecycle`

Refer to the Terraform Registry for docs: [`cloudflare_r2_bucket_lifecycle`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle).
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


class R2BucketLifecycle(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycle",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle cloudflare_r2_bucket_lifecycle}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        bucket_name: builtins.str,
        jurisdiction: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["R2BucketLifecycleRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle cloudflare_r2_bucket_lifecycle} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#account_id R2BucketLifecycle#account_id}
        :param bucket_name: Name of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#bucket_name R2BucketLifecycle#bucket_name}
        :param jurisdiction: Jurisdiction of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#jurisdiction R2BucketLifecycle#jurisdiction}
        :param rules: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#rules R2BucketLifecycle#rules}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b27687b52eb9b5aa7ebe4d2af21adb3aa6cae6835e67b40f95e17d8def97fb04)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = R2BucketLifecycleConfig(
            account_id=account_id,
            bucket_name=bucket_name,
            jurisdiction=jurisdiction,
            rules=rules,
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
        '''Generates CDKTF code for importing a R2BucketLifecycle resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the R2BucketLifecycle to import.
        :param import_from_id: The id of the existing R2BucketLifecycle that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the R2BucketLifecycle to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ce59a0c965b25f0288f0bf1c969b32bc6e98a447f22bb12100ec4c298b467f2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putRules")
    def put_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["R2BucketLifecycleRules", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62b2343687ddddd993715e6449d2c2c26e13946bba58e68cd931242349957273)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRules", [value]))

    @jsii.member(jsii_name="resetJurisdiction")
    def reset_jurisdiction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJurisdiction", []))

    @jsii.member(jsii_name="resetRules")
    def reset_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRules", []))

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
    @jsii.member(jsii_name="rules")
    def rules(self) -> "R2BucketLifecycleRulesList":
        return typing.cast("R2BucketLifecycleRulesList", jsii.get(self, "rules"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property
    @jsii.member(jsii_name="jurisdictionInput")
    def jurisdiction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jurisdictionInput"))

    @builtins.property
    @jsii.member(jsii_name="rulesInput")
    def rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["R2BucketLifecycleRules"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["R2BucketLifecycleRules"]]], jsii.get(self, "rulesInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7b2384885a20fa727508e9b9f7af915ecdc64636ff173d8fde4dbb4ed123f53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60db81b0493d7baca5e48f9afb2249bd3cf99b69c6f43c25363a0e6d6039f476)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jurisdiction")
    def jurisdiction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jurisdiction"))

    @jurisdiction.setter
    def jurisdiction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b59ff8d7a6266388fd0f3fe12585d0c95b09fa3dd7e2601d8c9b33d5bb166b5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jurisdiction", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleConfig",
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
        "bucket_name": "bucketName",
        "jurisdiction": "jurisdiction",
        "rules": "rules",
    },
)
class R2BucketLifecycleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        bucket_name: builtins.str,
        jurisdiction: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["R2BucketLifecycleRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#account_id R2BucketLifecycle#account_id}
        :param bucket_name: Name of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#bucket_name R2BucketLifecycle#bucket_name}
        :param jurisdiction: Jurisdiction of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#jurisdiction R2BucketLifecycle#jurisdiction}
        :param rules: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#rules R2BucketLifecycle#rules}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68732d9847373b923a0ee6cdfbcb44fde9206db484d21945c03b9592db01491e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument jurisdiction", value=jurisdiction, expected_type=type_hints["jurisdiction"])
            check_type(argname="argument rules", value=rules, expected_type=type_hints["rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "bucket_name": bucket_name,
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
        if jurisdiction is not None:
            self._values["jurisdiction"] = jurisdiction
        if rules is not None:
            self._values["rules"] = rules

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
        '''Account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#account_id R2BucketLifecycle#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''Name of the bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#bucket_name R2BucketLifecycle#bucket_name}
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def jurisdiction(self) -> typing.Optional[builtins.str]:
        '''Jurisdiction of the bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#jurisdiction R2BucketLifecycle#jurisdiction}
        '''
        result = self._values.get("jurisdiction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["R2BucketLifecycleRules"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#rules R2BucketLifecycle#rules}.'''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["R2BucketLifecycleRules"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketLifecycleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRules",
    jsii_struct_bases=[],
    name_mapping={
        "conditions": "conditions",
        "enabled": "enabled",
        "id": "id",
        "abort_multipart_uploads_transition": "abortMultipartUploadsTransition",
        "delete_objects_transition": "deleteObjectsTransition",
        "storage_class_transitions": "storageClassTransitions",
    },
)
class R2BucketLifecycleRules:
    def __init__(
        self,
        *,
        conditions: typing.Union["R2BucketLifecycleRulesConditions", typing.Dict[builtins.str, typing.Any]],
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        id: builtins.str,
        abort_multipart_uploads_transition: typing.Optional[typing.Union["R2BucketLifecycleRulesAbortMultipartUploadsTransition", typing.Dict[builtins.str, typing.Any]]] = None,
        delete_objects_transition: typing.Optional[typing.Union["R2BucketLifecycleRulesDeleteObjectsTransition", typing.Dict[builtins.str, typing.Any]]] = None,
        storage_class_transitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["R2BucketLifecycleRulesStorageClassTransitions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param conditions: Conditions that apply to all transitions of this rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#conditions R2BucketLifecycle#conditions}
        :param enabled: Whether or not this rule is in effect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#enabled R2BucketLifecycle#enabled}
        :param id: Unique identifier for this rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#id R2BucketLifecycle#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param abort_multipart_uploads_transition: Transition to abort ongoing multipart uploads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#abort_multipart_uploads_transition R2BucketLifecycle#abort_multipart_uploads_transition}
        :param delete_objects_transition: Transition to delete objects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#delete_objects_transition R2BucketLifecycle#delete_objects_transition}
        :param storage_class_transitions: Transitions to change the storage class of objects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#storage_class_transitions R2BucketLifecycle#storage_class_transitions}
        '''
        if isinstance(conditions, dict):
            conditions = R2BucketLifecycleRulesConditions(**conditions)
        if isinstance(abort_multipart_uploads_transition, dict):
            abort_multipart_uploads_transition = R2BucketLifecycleRulesAbortMultipartUploadsTransition(**abort_multipart_uploads_transition)
        if isinstance(delete_objects_transition, dict):
            delete_objects_transition = R2BucketLifecycleRulesDeleteObjectsTransition(**delete_objects_transition)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf7393432fa0edcb533096ec92eb649e7f7e3feef07fc204ff317511954af093)
            check_type(argname="argument conditions", value=conditions, expected_type=type_hints["conditions"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument abort_multipart_uploads_transition", value=abort_multipart_uploads_transition, expected_type=type_hints["abort_multipart_uploads_transition"])
            check_type(argname="argument delete_objects_transition", value=delete_objects_transition, expected_type=type_hints["delete_objects_transition"])
            check_type(argname="argument storage_class_transitions", value=storage_class_transitions, expected_type=type_hints["storage_class_transitions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "conditions": conditions,
            "enabled": enabled,
            "id": id,
        }
        if abort_multipart_uploads_transition is not None:
            self._values["abort_multipart_uploads_transition"] = abort_multipart_uploads_transition
        if delete_objects_transition is not None:
            self._values["delete_objects_transition"] = delete_objects_transition
        if storage_class_transitions is not None:
            self._values["storage_class_transitions"] = storage_class_transitions

    @builtins.property
    def conditions(self) -> "R2BucketLifecycleRulesConditions":
        '''Conditions that apply to all transitions of this rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#conditions R2BucketLifecycle#conditions}
        '''
        result = self._values.get("conditions")
        assert result is not None, "Required property 'conditions' is missing"
        return typing.cast("R2BucketLifecycleRulesConditions", result)

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Whether or not this rule is in effect.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#enabled R2BucketLifecycle#enabled}
        '''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def id(self) -> builtins.str:
        '''Unique identifier for this rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#id R2BucketLifecycle#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def abort_multipart_uploads_transition(
        self,
    ) -> typing.Optional["R2BucketLifecycleRulesAbortMultipartUploadsTransition"]:
        '''Transition to abort ongoing multipart uploads.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#abort_multipart_uploads_transition R2BucketLifecycle#abort_multipart_uploads_transition}
        '''
        result = self._values.get("abort_multipart_uploads_transition")
        return typing.cast(typing.Optional["R2BucketLifecycleRulesAbortMultipartUploadsTransition"], result)

    @builtins.property
    def delete_objects_transition(
        self,
    ) -> typing.Optional["R2BucketLifecycleRulesDeleteObjectsTransition"]:
        '''Transition to delete objects.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#delete_objects_transition R2BucketLifecycle#delete_objects_transition}
        '''
        result = self._values.get("delete_objects_transition")
        return typing.cast(typing.Optional["R2BucketLifecycleRulesDeleteObjectsTransition"], result)

    @builtins.property
    def storage_class_transitions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["R2BucketLifecycleRulesStorageClassTransitions"]]]:
        '''Transitions to change the storage class of objects.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#storage_class_transitions R2BucketLifecycle#storage_class_transitions}
        '''
        result = self._values.get("storage_class_transitions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["R2BucketLifecycleRulesStorageClassTransitions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketLifecycleRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesAbortMultipartUploadsTransition",
    jsii_struct_bases=[],
    name_mapping={"condition": "condition"},
)
class R2BucketLifecycleRulesAbortMultipartUploadsTransition:
    def __init__(
        self,
        *,
        condition: typing.Optional[typing.Union["R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param condition: Condition for lifecycle transitions to apply after an object reaches an age in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#condition R2BucketLifecycle#condition}
        '''
        if isinstance(condition, dict):
            condition = R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition(**condition)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__837c8254c357974dabfbd9fbbdd80187ecb83bdd8d338392e7c927111c1e8241)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if condition is not None:
            self._values["condition"] = condition

    @builtins.property
    def condition(
        self,
    ) -> typing.Optional["R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition"]:
        '''Condition for lifecycle transitions to apply after an object reaches an age in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#condition R2BucketLifecycle#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional["R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketLifecycleRulesAbortMultipartUploadsTransition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition",
    jsii_struct_bases=[],
    name_mapping={"max_age": "maxAge", "type": "type"},
)
class R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition:
    def __init__(self, *, max_age: jsii.Number, type: builtins.str) -> None:
        '''
        :param max_age: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#max_age R2BucketLifecycle#max_age}.
        :param type: Available values: "Age". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#type R2BucketLifecycle#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7154b5ad1c8bff2f876df499fb92d46e0c42c8d449e0fa62e1538337390e2bfc)
            check_type(argname="argument max_age", value=max_age, expected_type=type_hints["max_age"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "max_age": max_age,
            "type": type,
        }

    @builtins.property
    def max_age(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#max_age R2BucketLifecycle#max_age}.'''
        result = self._values.get("max_age")
        assert result is not None, "Required property 'max_age' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Available values: "Age".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#type R2BucketLifecycle#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class R2BucketLifecycleRulesAbortMultipartUploadsTransitionConditionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesAbortMultipartUploadsTransitionConditionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c0bd2925ffa3e638d0846625382a8a43b83f983a6f89ef734bd23a0fa111f6f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="maxAgeInput")
    def max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxAge")
    def max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAge"))

    @max_age.setter
    def max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65a77f759f8be5e8ad99b27fb55888f5b768f3e6f4cd9cf4fae91c622498ee81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAge", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a953b88c4395974e7d237c1b916bc4324c32400c03e0bc4fc2c7df1696de553)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fad51a3c1330311ccd46df19d4f43ceaecaab5ca8202dc8f2453a82c9b43ddc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class R2BucketLifecycleRulesAbortMultipartUploadsTransitionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesAbortMultipartUploadsTransitionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b477280a503e855d3b0e2cc6f68ec50646904bad2d2946e7522eb84de5cd3bfc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCondition")
    def put_condition(self, *, max_age: jsii.Number, type: builtins.str) -> None:
        '''
        :param max_age: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#max_age R2BucketLifecycle#max_age}.
        :param type: Available values: "Age". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#type R2BucketLifecycle#type}
        '''
        value = R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition(
            max_age=max_age, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putCondition", [value]))

    @jsii.member(jsii_name="resetCondition")
    def reset_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCondition", []))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(
        self,
    ) -> R2BucketLifecycleRulesAbortMultipartUploadsTransitionConditionOutputReference:
        return typing.cast(R2BucketLifecycleRulesAbortMultipartUploadsTransitionConditionOutputReference, jsii.get(self, "condition"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition]], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransition]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransition]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42825b075c3b6f024fa69b8bc9495039c89da5e0c132fb1055c63b284e85cde0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesConditions",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix"},
)
class R2BucketLifecycleRulesConditions:
    def __init__(self, *, prefix: builtins.str) -> None:
        '''
        :param prefix: Transitions will only apply to objects/uploads in the bucket that start with the given prefix, an empty prefix can be provided to scope rule to all objects/uploads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#prefix R2BucketLifecycle#prefix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38a43bfd00acbc9dac30501659d7246e948cee021d9a933d3209e650b3287cab)
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "prefix": prefix,
        }

    @builtins.property
    def prefix(self) -> builtins.str:
        '''Transitions will only apply to objects/uploads in the bucket that start with the given prefix, an empty prefix can be provided to scope rule to all objects/uploads.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#prefix R2BucketLifecycle#prefix}
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketLifecycleRulesConditions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class R2BucketLifecycleRulesConditionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesConditionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f689d32e87ede61c34f2e78eb860b0eb17224e0180a0cbae2e0c706d556db2b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b8bbffb0f31d2228169107a38d7ceae0657f510c8ec52f67dc5b0073077bac5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesConditions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesConditions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesConditions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ea0b568dc45685cf086c91df035c357af0c7469ff9ffddd632614c8bd131c53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesDeleteObjectsTransition",
    jsii_struct_bases=[],
    name_mapping={"condition": "condition"},
)
class R2BucketLifecycleRulesDeleteObjectsTransition:
    def __init__(
        self,
        *,
        condition: typing.Optional[typing.Union["R2BucketLifecycleRulesDeleteObjectsTransitionCondition", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param condition: Condition for lifecycle transitions to apply after an object reaches an age in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#condition R2BucketLifecycle#condition}
        '''
        if isinstance(condition, dict):
            condition = R2BucketLifecycleRulesDeleteObjectsTransitionCondition(**condition)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27a976bfeb663e3def15656f8dfa8de5eb485200f38b8c1e98b86194cba09190)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if condition is not None:
            self._values["condition"] = condition

    @builtins.property
    def condition(
        self,
    ) -> typing.Optional["R2BucketLifecycleRulesDeleteObjectsTransitionCondition"]:
        '''Condition for lifecycle transitions to apply after an object reaches an age in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#condition R2BucketLifecycle#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional["R2BucketLifecycleRulesDeleteObjectsTransitionCondition"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketLifecycleRulesDeleteObjectsTransition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesDeleteObjectsTransitionCondition",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "date": "date", "max_age": "maxAge"},
)
class R2BucketLifecycleRulesDeleteObjectsTransitionCondition:
    def __init__(
        self,
        *,
        type: builtins.str,
        date: typing.Optional[builtins.str] = None,
        max_age: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Available values: "Age", "Date". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#type R2BucketLifecycle#type}
        :param date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#date R2BucketLifecycle#date}.
        :param max_age: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#max_age R2BucketLifecycle#max_age}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae5fa0c59a1464689ec88f318ce53e73f9e3e5f57e8cfbbae1724abcd1d2e6b0)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument date", value=date, expected_type=type_hints["date"])
            check_type(argname="argument max_age", value=max_age, expected_type=type_hints["max_age"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if date is not None:
            self._values["date"] = date
        if max_age is not None:
            self._values["max_age"] = max_age

    @builtins.property
    def type(self) -> builtins.str:
        '''Available values: "Age", "Date".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#type R2BucketLifecycle#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#date R2BucketLifecycle#date}.'''
        result = self._values.get("date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_age(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#max_age R2BucketLifecycle#max_age}.'''
        result = self._values.get("max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketLifecycleRulesDeleteObjectsTransitionCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class R2BucketLifecycleRulesDeleteObjectsTransitionConditionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesDeleteObjectsTransitionConditionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0524ea008cb6fa82915c0a3963af6bafa5290395d9a83faf27b6f09ea7fa01c0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDate")
    def reset_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDate", []))

    @jsii.member(jsii_name="resetMaxAge")
    def reset_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAge", []))

    @builtins.property
    @jsii.member(jsii_name="dateInput")
    def date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dateInput"))

    @builtins.property
    @jsii.member(jsii_name="maxAgeInput")
    def max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="date")
    def date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "date"))

    @date.setter
    def date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83aa3ed8b556699e8e2531f2882743794e8af366ebe4330663e81f71510e0035)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "date", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAge")
    def max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAge"))

    @max_age.setter
    def max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__677d7e50f7f6b919b4caaf704c911248444a10b4884f5aaf55d1cdb60dcc301a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAge", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d70306e67c2511166da256c85f2c9e638ae55841a479f642b901d74a45984e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransitionCondition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransitionCondition]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransitionCondition]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96f36dbf1f954963d7d992ab7e0d6ad7245e8e1a3ca30b2d1670eb392a1ce5f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class R2BucketLifecycleRulesDeleteObjectsTransitionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesDeleteObjectsTransitionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cbba346d3f210e71676cd2e59d6e758e933067f8e6663f7ca6d81275c5f73e5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCondition")
    def put_condition(
        self,
        *,
        type: builtins.str,
        date: typing.Optional[builtins.str] = None,
        max_age: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Available values: "Age", "Date". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#type R2BucketLifecycle#type}
        :param date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#date R2BucketLifecycle#date}.
        :param max_age: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#max_age R2BucketLifecycle#max_age}.
        '''
        value = R2BucketLifecycleRulesDeleteObjectsTransitionCondition(
            type=type, date=date, max_age=max_age
        )

        return typing.cast(None, jsii.invoke(self, "putCondition", [value]))

    @jsii.member(jsii_name="resetCondition")
    def reset_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCondition", []))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(
        self,
    ) -> R2BucketLifecycleRulesDeleteObjectsTransitionConditionOutputReference:
        return typing.cast(R2BucketLifecycleRulesDeleteObjectsTransitionConditionOutputReference, jsii.get(self, "condition"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransitionCondition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransitionCondition]], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransition]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransition]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc99639a6cebf3f9b88b69a67e062ff77e7a64c5604be134b6f6ed314f85044f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class R2BucketLifecycleRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc2100bd8841d5d3e8a7c79ef283d923c9605d6aa25ee2aeca6b252245858596)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "R2BucketLifecycleRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdeb3d02d03eaf190129a7f21a8c20acf13596e4ccb201de66c48919b83c8038)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("R2BucketLifecycleRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15f31cbde098caec4f9e0e190f89b83e22609a5c431d0acefd6b10c7ccce8b60)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f5355910c708d982fbe30d4ca4980e0da8c006b6a83597b8b2e76b3d654f6f4c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7824cd3655cd273a86189fb5506e5962059d67d7fd69bcd8ba5a73b5183a8a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[R2BucketLifecycleRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[R2BucketLifecycleRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[R2BucketLifecycleRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acd858816511d784a0fb9f2544c45afb8e3a6014fe0f2a95f36fc791c998b1d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class R2BucketLifecycleRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab4fe4540aa4d9c6a88913d85ea4200808b8c755bf057a61d7c9d8521d1771c8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAbortMultipartUploadsTransition")
    def put_abort_multipart_uploads_transition(
        self,
        *,
        condition: typing.Optional[typing.Union[R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param condition: Condition for lifecycle transitions to apply after an object reaches an age in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#condition R2BucketLifecycle#condition}
        '''
        value = R2BucketLifecycleRulesAbortMultipartUploadsTransition(
            condition=condition
        )

        return typing.cast(None, jsii.invoke(self, "putAbortMultipartUploadsTransition", [value]))

    @jsii.member(jsii_name="putConditions")
    def put_conditions(self, *, prefix: builtins.str) -> None:
        '''
        :param prefix: Transitions will only apply to objects/uploads in the bucket that start with the given prefix, an empty prefix can be provided to scope rule to all objects/uploads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#prefix R2BucketLifecycle#prefix}
        '''
        value = R2BucketLifecycleRulesConditions(prefix=prefix)

        return typing.cast(None, jsii.invoke(self, "putConditions", [value]))

    @jsii.member(jsii_name="putDeleteObjectsTransition")
    def put_delete_objects_transition(
        self,
        *,
        condition: typing.Optional[typing.Union[R2BucketLifecycleRulesDeleteObjectsTransitionCondition, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param condition: Condition for lifecycle transitions to apply after an object reaches an age in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#condition R2BucketLifecycle#condition}
        '''
        value = R2BucketLifecycleRulesDeleteObjectsTransition(condition=condition)

        return typing.cast(None, jsii.invoke(self, "putDeleteObjectsTransition", [value]))

    @jsii.member(jsii_name="putStorageClassTransitions")
    def put_storage_class_transitions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["R2BucketLifecycleRulesStorageClassTransitions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6842d7f0838ae63027496b14a7b4f52a191f7649ff64842545d3fcaeed4c2eb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStorageClassTransitions", [value]))

    @jsii.member(jsii_name="resetAbortMultipartUploadsTransition")
    def reset_abort_multipart_uploads_transition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAbortMultipartUploadsTransition", []))

    @jsii.member(jsii_name="resetDeleteObjectsTransition")
    def reset_delete_objects_transition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteObjectsTransition", []))

    @jsii.member(jsii_name="resetStorageClassTransitions")
    def reset_storage_class_transitions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageClassTransitions", []))

    @builtins.property
    @jsii.member(jsii_name="abortMultipartUploadsTransition")
    def abort_multipart_uploads_transition(
        self,
    ) -> R2BucketLifecycleRulesAbortMultipartUploadsTransitionOutputReference:
        return typing.cast(R2BucketLifecycleRulesAbortMultipartUploadsTransitionOutputReference, jsii.get(self, "abortMultipartUploadsTransition"))

    @builtins.property
    @jsii.member(jsii_name="conditions")
    def conditions(self) -> R2BucketLifecycleRulesConditionsOutputReference:
        return typing.cast(R2BucketLifecycleRulesConditionsOutputReference, jsii.get(self, "conditions"))

    @builtins.property
    @jsii.member(jsii_name="deleteObjectsTransition")
    def delete_objects_transition(
        self,
    ) -> R2BucketLifecycleRulesDeleteObjectsTransitionOutputReference:
        return typing.cast(R2BucketLifecycleRulesDeleteObjectsTransitionOutputReference, jsii.get(self, "deleteObjectsTransition"))

    @builtins.property
    @jsii.member(jsii_name="storageClassTransitions")
    def storage_class_transitions(
        self,
    ) -> "R2BucketLifecycleRulesStorageClassTransitionsList":
        return typing.cast("R2BucketLifecycleRulesStorageClassTransitionsList", jsii.get(self, "storageClassTransitions"))

    @builtins.property
    @jsii.member(jsii_name="abortMultipartUploadsTransitionInput")
    def abort_multipart_uploads_transition_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransition]], jsii.get(self, "abortMultipartUploadsTransitionInput"))

    @builtins.property
    @jsii.member(jsii_name="conditionsInput")
    def conditions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesConditions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesConditions]], jsii.get(self, "conditionsInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteObjectsTransitionInput")
    def delete_objects_transition_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransition]], jsii.get(self, "deleteObjectsTransitionInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="storageClassTransitionsInput")
    def storage_class_transitions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["R2BucketLifecycleRulesStorageClassTransitions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["R2BucketLifecycleRulesStorageClassTransitions"]]], jsii.get(self, "storageClassTransitionsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__edf004d048d1613e9d80160b84378e39dfa0c4e1a64f8e013fbf5a55177b0bcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff444a68ed7a777d11d6c3480a66d898cb528035d9dd3535f024825008e08bf9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85766425a7a07767b09104d5f0c470b66e3afbba55cf720d514968d8b3fd60f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesStorageClassTransitions",
    jsii_struct_bases=[],
    name_mapping={"condition": "condition", "storage_class": "storageClass"},
)
class R2BucketLifecycleRulesStorageClassTransitions:
    def __init__(
        self,
        *,
        condition: typing.Union["R2BucketLifecycleRulesStorageClassTransitionsCondition", typing.Dict[builtins.str, typing.Any]],
        storage_class: builtins.str,
    ) -> None:
        '''
        :param condition: Condition for lifecycle transitions to apply after an object reaches an age in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#condition R2BucketLifecycle#condition}
        :param storage_class: Available values: "InfrequentAccess". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#storage_class R2BucketLifecycle#storage_class}
        '''
        if isinstance(condition, dict):
            condition = R2BucketLifecycleRulesStorageClassTransitionsCondition(**condition)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03247a4c61d8060388c3c062437d39f068a61c428d3b68b4008e15d4264a4fa3)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument storage_class", value=storage_class, expected_type=type_hints["storage_class"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "condition": condition,
            "storage_class": storage_class,
        }

    @builtins.property
    def condition(self) -> "R2BucketLifecycleRulesStorageClassTransitionsCondition":
        '''Condition for lifecycle transitions to apply after an object reaches an age in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#condition R2BucketLifecycle#condition}
        '''
        result = self._values.get("condition")
        assert result is not None, "Required property 'condition' is missing"
        return typing.cast("R2BucketLifecycleRulesStorageClassTransitionsCondition", result)

    @builtins.property
    def storage_class(self) -> builtins.str:
        '''Available values: "InfrequentAccess".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#storage_class R2BucketLifecycle#storage_class}
        '''
        result = self._values.get("storage_class")
        assert result is not None, "Required property 'storage_class' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketLifecycleRulesStorageClassTransitions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesStorageClassTransitionsCondition",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "date": "date", "max_age": "maxAge"},
)
class R2BucketLifecycleRulesStorageClassTransitionsCondition:
    def __init__(
        self,
        *,
        type: builtins.str,
        date: typing.Optional[builtins.str] = None,
        max_age: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Available values: "Age", "Date". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#type R2BucketLifecycle#type}
        :param date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#date R2BucketLifecycle#date}.
        :param max_age: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#max_age R2BucketLifecycle#max_age}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9407013cd06651758eee45748fd90851809a0b9b9d59798a526885a82589ff64)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument date", value=date, expected_type=type_hints["date"])
            check_type(argname="argument max_age", value=max_age, expected_type=type_hints["max_age"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if date is not None:
            self._values["date"] = date
        if max_age is not None:
            self._values["max_age"] = max_age

    @builtins.property
    def type(self) -> builtins.str:
        '''Available values: "Age", "Date".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#type R2BucketLifecycle#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#date R2BucketLifecycle#date}.'''
        result = self._values.get("date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_age(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#max_age R2BucketLifecycle#max_age}.'''
        result = self._values.get("max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketLifecycleRulesStorageClassTransitionsCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class R2BucketLifecycleRulesStorageClassTransitionsConditionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesStorageClassTransitionsConditionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__98ae2df751a6902b82a9ccad0bf4881a332c1bfa9212102b672f4edfae41d4cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDate")
    def reset_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDate", []))

    @jsii.member(jsii_name="resetMaxAge")
    def reset_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAge", []))

    @builtins.property
    @jsii.member(jsii_name="dateInput")
    def date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dateInput"))

    @builtins.property
    @jsii.member(jsii_name="maxAgeInput")
    def max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="date")
    def date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "date"))

    @date.setter
    def date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d7a781ff36fb2cf7a2def65d1569298d7ab55589ec9e080c89591d4afa510a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "date", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAge")
    def max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAge"))

    @max_age.setter
    def max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dc448ef4104f2c45a56780380e4cea7522bc11fff480ff9d67270954ca38453)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAge", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d5d018a27182a9d42f5029f5cdf8e90b2b499402a05a3847f22292c0043cc18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitionsCondition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitionsCondition]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitionsCondition]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be936b5ed82dfeed21c2d6c9dbb0545021192ea678130a2f3b5f851251b6baff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class R2BucketLifecycleRulesStorageClassTransitionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesStorageClassTransitionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e08e642a3e2725e1893e0be6930b967941c6d90c5234a79d1ac23c3c361eb731)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "R2BucketLifecycleRulesStorageClassTransitionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cdf62edc0c48a4848a79bb95e9689cd46d9750a0a4c386236484be3b2d32766)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("R2BucketLifecycleRulesStorageClassTransitionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__053c9e4cdbb6814f05871e14b70bab72b8c6f46e7feb83baf87a272f59c11af2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8365cb64145b468e0856c58c627b90c5b30aa94a6bf55117d03315a48b7a1027)
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
            type_hints = typing.get_type_hints(_typecheckingstub__13438fb4bb14751551f9e59ae69a14da90598124e474b683ddbaa9889d6d6af2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[R2BucketLifecycleRulesStorageClassTransitions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[R2BucketLifecycleRulesStorageClassTransitions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[R2BucketLifecycleRulesStorageClassTransitions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48704988c1e85e02ac800ffb1603777aba5b9693c3783aa3be826c2abbb4160b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class R2BucketLifecycleRulesStorageClassTransitionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketLifecycle.R2BucketLifecycleRulesStorageClassTransitionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64855e0f6fd9fa31051b0c3666331a3a6eb2c8af14303b0396b9c56c27b4d995)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCondition")
    def put_condition(
        self,
        *,
        type: builtins.str,
        date: typing.Optional[builtins.str] = None,
        max_age: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Available values: "Age", "Date". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#type R2BucketLifecycle#type}
        :param date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#date R2BucketLifecycle#date}.
        :param max_age: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_lifecycle#max_age R2BucketLifecycle#max_age}.
        '''
        value = R2BucketLifecycleRulesStorageClassTransitionsCondition(
            type=type, date=date, max_age=max_age
        )

        return typing.cast(None, jsii.invoke(self, "putCondition", [value]))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(
        self,
    ) -> R2BucketLifecycleRulesStorageClassTransitionsConditionOutputReference:
        return typing.cast(R2BucketLifecycleRulesStorageClassTransitionsConditionOutputReference, jsii.get(self, "condition"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitionsCondition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitionsCondition]], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="storageClassInput")
    def storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageClassInput"))

    @builtins.property
    @jsii.member(jsii_name="storageClass")
    def storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageClass"))

    @storage_class.setter
    def storage_class(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aba6647f825137c677384c0bbf1af5ee0ff0d573f725c840c45ea52aaffa5498)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageClass", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a64fa71cbfff2494a52f2485128c53c71ed54d51e242eb0379b21c812d03a890)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "R2BucketLifecycle",
    "R2BucketLifecycleConfig",
    "R2BucketLifecycleRules",
    "R2BucketLifecycleRulesAbortMultipartUploadsTransition",
    "R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition",
    "R2BucketLifecycleRulesAbortMultipartUploadsTransitionConditionOutputReference",
    "R2BucketLifecycleRulesAbortMultipartUploadsTransitionOutputReference",
    "R2BucketLifecycleRulesConditions",
    "R2BucketLifecycleRulesConditionsOutputReference",
    "R2BucketLifecycleRulesDeleteObjectsTransition",
    "R2BucketLifecycleRulesDeleteObjectsTransitionCondition",
    "R2BucketLifecycleRulesDeleteObjectsTransitionConditionOutputReference",
    "R2BucketLifecycleRulesDeleteObjectsTransitionOutputReference",
    "R2BucketLifecycleRulesList",
    "R2BucketLifecycleRulesOutputReference",
    "R2BucketLifecycleRulesStorageClassTransitions",
    "R2BucketLifecycleRulesStorageClassTransitionsCondition",
    "R2BucketLifecycleRulesStorageClassTransitionsConditionOutputReference",
    "R2BucketLifecycleRulesStorageClassTransitionsList",
    "R2BucketLifecycleRulesStorageClassTransitionsOutputReference",
]

publication.publish()

def _typecheckingstub__b27687b52eb9b5aa7ebe4d2af21adb3aa6cae6835e67b40f95e17d8def97fb04(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    bucket_name: builtins.str,
    jurisdiction: typing.Optional[builtins.str] = None,
    rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[R2BucketLifecycleRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__9ce59a0c965b25f0288f0bf1c969b32bc6e98a447f22bb12100ec4c298b467f2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62b2343687ddddd993715e6449d2c2c26e13946bba58e68cd931242349957273(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[R2BucketLifecycleRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7b2384885a20fa727508e9b9f7af915ecdc64636ff173d8fde4dbb4ed123f53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60db81b0493d7baca5e48f9afb2249bd3cf99b69c6f43c25363a0e6d6039f476(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b59ff8d7a6266388fd0f3fe12585d0c95b09fa3dd7e2601d8c9b33d5bb166b5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68732d9847373b923a0ee6cdfbcb44fde9206db484d21945c03b9592db01491e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    bucket_name: builtins.str,
    jurisdiction: typing.Optional[builtins.str] = None,
    rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[R2BucketLifecycleRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf7393432fa0edcb533096ec92eb649e7f7e3feef07fc204ff317511954af093(
    *,
    conditions: typing.Union[R2BucketLifecycleRulesConditions, typing.Dict[builtins.str, typing.Any]],
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    id: builtins.str,
    abort_multipart_uploads_transition: typing.Optional[typing.Union[R2BucketLifecycleRulesAbortMultipartUploadsTransition, typing.Dict[builtins.str, typing.Any]]] = None,
    delete_objects_transition: typing.Optional[typing.Union[R2BucketLifecycleRulesDeleteObjectsTransition, typing.Dict[builtins.str, typing.Any]]] = None,
    storage_class_transitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[R2BucketLifecycleRulesStorageClassTransitions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__837c8254c357974dabfbd9fbbdd80187ecb83bdd8d338392e7c927111c1e8241(
    *,
    condition: typing.Optional[typing.Union[R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7154b5ad1c8bff2f876df499fb92d46e0c42c8d449e0fa62e1538337390e2bfc(
    *,
    max_age: jsii.Number,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c0bd2925ffa3e638d0846625382a8a43b83f983a6f89ef734bd23a0fa111f6f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65a77f759f8be5e8ad99b27fb55888f5b768f3e6f4cd9cf4fae91c622498ee81(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a953b88c4395974e7d237c1b916bc4324c32400c03e0bc4fc2c7df1696de553(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fad51a3c1330311ccd46df19d4f43ceaecaab5ca8202dc8f2453a82c9b43ddc2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransitionCondition]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b477280a503e855d3b0e2cc6f68ec50646904bad2d2946e7522eb84de5cd3bfc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42825b075c3b6f024fa69b8bc9495039c89da5e0c132fb1055c63b284e85cde0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesAbortMultipartUploadsTransition]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38a43bfd00acbc9dac30501659d7246e948cee021d9a933d3209e650b3287cab(
    *,
    prefix: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f689d32e87ede61c34f2e78eb860b0eb17224e0180a0cbae2e0c706d556db2b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b8bbffb0f31d2228169107a38d7ceae0657f510c8ec52f67dc5b0073077bac5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ea0b568dc45685cf086c91df035c357af0c7469ff9ffddd632614c8bd131c53(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesConditions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27a976bfeb663e3def15656f8dfa8de5eb485200f38b8c1e98b86194cba09190(
    *,
    condition: typing.Optional[typing.Union[R2BucketLifecycleRulesDeleteObjectsTransitionCondition, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae5fa0c59a1464689ec88f318ce53e73f9e3e5f57e8cfbbae1724abcd1d2e6b0(
    *,
    type: builtins.str,
    date: typing.Optional[builtins.str] = None,
    max_age: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0524ea008cb6fa82915c0a3963af6bafa5290395d9a83faf27b6f09ea7fa01c0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83aa3ed8b556699e8e2531f2882743794e8af366ebe4330663e81f71510e0035(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__677d7e50f7f6b919b4caaf704c911248444a10b4884f5aaf55d1cdb60dcc301a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d70306e67c2511166da256c85f2c9e638ae55841a479f642b901d74a45984e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96f36dbf1f954963d7d992ab7e0d6ad7245e8e1a3ca30b2d1670eb392a1ce5f3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransitionCondition]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cbba346d3f210e71676cd2e59d6e758e933067f8e6663f7ca6d81275c5f73e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc99639a6cebf3f9b88b69a67e062ff77e7a64c5604be134b6f6ed314f85044f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesDeleteObjectsTransition]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc2100bd8841d5d3e8a7c79ef283d923c9605d6aa25ee2aeca6b252245858596(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdeb3d02d03eaf190129a7f21a8c20acf13596e4ccb201de66c48919b83c8038(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15f31cbde098caec4f9e0e190f89b83e22609a5c431d0acefd6b10c7ccce8b60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5355910c708d982fbe30d4ca4980e0da8c006b6a83597b8b2e76b3d654f6f4c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7824cd3655cd273a86189fb5506e5962059d67d7fd69bcd8ba5a73b5183a8a3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acd858816511d784a0fb9f2544c45afb8e3a6014fe0f2a95f36fc791c998b1d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[R2BucketLifecycleRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab4fe4540aa4d9c6a88913d85ea4200808b8c755bf057a61d7c9d8521d1771c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6842d7f0838ae63027496b14a7b4f52a191f7649ff64842545d3fcaeed4c2eb5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[R2BucketLifecycleRulesStorageClassTransitions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edf004d048d1613e9d80160b84378e39dfa0c4e1a64f8e013fbf5a55177b0bcc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff444a68ed7a777d11d6c3480a66d898cb528035d9dd3535f024825008e08bf9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85766425a7a07767b09104d5f0c470b66e3afbba55cf720d514968d8b3fd60f1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03247a4c61d8060388c3c062437d39f068a61c428d3b68b4008e15d4264a4fa3(
    *,
    condition: typing.Union[R2BucketLifecycleRulesStorageClassTransitionsCondition, typing.Dict[builtins.str, typing.Any]],
    storage_class: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9407013cd06651758eee45748fd90851809a0b9b9d59798a526885a82589ff64(
    *,
    type: builtins.str,
    date: typing.Optional[builtins.str] = None,
    max_age: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98ae2df751a6902b82a9ccad0bf4881a332c1bfa9212102b672f4edfae41d4cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d7a781ff36fb2cf7a2def65d1569298d7ab55589ec9e080c89591d4afa510a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dc448ef4104f2c45a56780380e4cea7522bc11fff480ff9d67270954ca38453(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d5d018a27182a9d42f5029f5cdf8e90b2b499402a05a3847f22292c0043cc18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be936b5ed82dfeed21c2d6c9dbb0545021192ea678130a2f3b5f851251b6baff(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitionsCondition]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e08e642a3e2725e1893e0be6930b967941c6d90c5234a79d1ac23c3c361eb731(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cdf62edc0c48a4848a79bb95e9689cd46d9750a0a4c386236484be3b2d32766(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__053c9e4cdbb6814f05871e14b70bab72b8c6f46e7feb83baf87a272f59c11af2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8365cb64145b468e0856c58c627b90c5b30aa94a6bf55117d03315a48b7a1027(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13438fb4bb14751551f9e59ae69a14da90598124e474b683ddbaa9889d6d6af2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48704988c1e85e02ac800ffb1603777aba5b9693c3783aa3be826c2abbb4160b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[R2BucketLifecycleRulesStorageClassTransitions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64855e0f6fd9fa31051b0c3666331a3a6eb2c8af14303b0396b9c56c27b4d995(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aba6647f825137c677384c0bbf1af5ee0ff0d573f725c840c45ea52aaffa5498(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a64fa71cbfff2494a52f2485128c53c71ed54d51e242eb0379b21c812d03a890(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketLifecycleRulesStorageClassTransitions]],
) -> None:
    """Type checking stubs"""
    pass
