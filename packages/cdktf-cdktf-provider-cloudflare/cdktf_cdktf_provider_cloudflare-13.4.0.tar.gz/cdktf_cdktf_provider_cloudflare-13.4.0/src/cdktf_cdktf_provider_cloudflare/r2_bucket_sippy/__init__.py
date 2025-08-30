r'''
# `cloudflare_r2_bucket_sippy`

Refer to the Terraform Registry for docs: [`cloudflare_r2_bucket_sippy`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy).
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


class R2BucketSippy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketSippy.R2BucketSippy",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy cloudflare_r2_bucket_sippy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        bucket_name: builtins.str,
        destination: typing.Optional[typing.Union["R2BucketSippyDestination", typing.Dict[builtins.str, typing.Any]]] = None,
        jurisdiction: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Union["R2BucketSippySource", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy cloudflare_r2_bucket_sippy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#account_id R2BucketSippy#account_id}
        :param bucket_name: Name of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#bucket_name R2BucketSippy#bucket_name}
        :param destination: R2 bucket to copy objects to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#destination R2BucketSippy#destination}
        :param jurisdiction: Jurisdiction of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#jurisdiction R2BucketSippy#jurisdiction}
        :param source: AWS S3 bucket to copy objects from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#source R2BucketSippy#source}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2acc48b499268225209f8b297847fecfe387865cc82e3f539d2fa182051f9d29)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = R2BucketSippyConfig(
            account_id=account_id,
            bucket_name=bucket_name,
            destination=destination,
            jurisdiction=jurisdiction,
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
        '''Generates CDKTF code for importing a R2BucketSippy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the R2BucketSippy to import.
        :param import_from_id: The id of the existing R2BucketSippy that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the R2BucketSippy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c3e9e8dfcc23e1c69505df4e69e18b99b23beb538f3428f79e842b31c77e62d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDestination")
    def put_destination(
        self,
        *,
        access_key_id: typing.Optional[builtins.str] = None,
        cloud_provider: typing.Optional[builtins.str] = None,
        secret_access_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_key_id: ID of a Cloudflare API token. This is the value labelled "Access Key ID" when creating an API. token from the `R2 dashboard <https://dash.cloudflare.com/?to=/:account/r2/api-tokens>`_. Sippy will use this token when writing objects to R2, so it is best to scope this token to the bucket you're enabling Sippy for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#access_key_id R2BucketSippy#access_key_id}
        :param cloud_provider: Available values: "r2". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#cloud_provider R2BucketSippy#cloud_provider}
        :param secret_access_key: Value of a Cloudflare API token. This is the value labelled "Secret Access Key" when creating an API. token from the `R2 dashboard <https://dash.cloudflare.com/?to=/:account/r2/api-tokens>`_. Sippy will use this token when writing objects to R2, so it is best to scope this token to the bucket you're enabling Sippy for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#secret_access_key R2BucketSippy#secret_access_key}
        '''
        value = R2BucketSippyDestination(
            access_key_id=access_key_id,
            cloud_provider=cloud_provider,
            secret_access_key=secret_access_key,
        )

        return typing.cast(None, jsii.invoke(self, "putDestination", [value]))

    @jsii.member(jsii_name="putSource")
    def put_source(
        self,
        *,
        access_key_id: typing.Optional[builtins.str] = None,
        bucket: typing.Optional[builtins.str] = None,
        client_email: typing.Optional[builtins.str] = None,
        cloud_provider: typing.Optional[builtins.str] = None,
        private_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        secret_access_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_key_id: Access Key ID of an IAM credential (ideally scoped to a single S3 bucket). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#access_key_id R2BucketSippy#access_key_id}
        :param bucket: Name of the AWS S3 bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#bucket R2BucketSippy#bucket}
        :param client_email: Client email of an IAM credential (ideally scoped to a single GCS bucket). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#client_email R2BucketSippy#client_email}
        :param cloud_provider: Available values: "aws", "gcs". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#cloud_provider R2BucketSippy#cloud_provider}
        :param private_key: Private Key of an IAM credential (ideally scoped to a single GCS bucket). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#private_key R2BucketSippy#private_key}
        :param region: Name of the AWS availability zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#region R2BucketSippy#region}
        :param secret_access_key: Secret Access Key of an IAM credential (ideally scoped to a single S3 bucket). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#secret_access_key R2BucketSippy#secret_access_key}
        '''
        value = R2BucketSippySource(
            access_key_id=access_key_id,
            bucket=bucket,
            client_email=client_email,
            cloud_provider=cloud_provider,
            private_key=private_key,
            region=region,
            secret_access_key=secret_access_key,
        )

        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="resetDestination")
    def reset_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestination", []))

    @jsii.member(jsii_name="resetJurisdiction")
    def reset_jurisdiction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJurisdiction", []))

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
    @jsii.member(jsii_name="destination")
    def destination(self) -> "R2BucketSippyDestinationOutputReference":
        return typing.cast("R2BucketSippyDestinationOutputReference", jsii.get(self, "destination"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "R2BucketSippySourceOutputReference":
        return typing.cast("R2BucketSippySourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "R2BucketSippyDestination"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "R2BucketSippyDestination"]], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="jurisdictionInput")
    def jurisdiction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jurisdictionInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "R2BucketSippySource"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "R2BucketSippySource"]], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e0650ad3b95b759572c3847f68f635f1dbf3585dfa7bbcb7d6bc8e1694b5003)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55cc532585ed0e4c90051eb2f62e5edc178559395069cfef044ac70ac8a57bf0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jurisdiction")
    def jurisdiction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jurisdiction"))

    @jurisdiction.setter
    def jurisdiction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a3cf358207801e9dd72ba5183a9240a5fb51c6483bf7d1e433151e0732d88ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jurisdiction", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketSippy.R2BucketSippyConfig",
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
        "destination": "destination",
        "jurisdiction": "jurisdiction",
        "source": "source",
    },
)
class R2BucketSippyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        destination: typing.Optional[typing.Union["R2BucketSippyDestination", typing.Dict[builtins.str, typing.Any]]] = None,
        jurisdiction: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Union["R2BucketSippySource", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#account_id R2BucketSippy#account_id}
        :param bucket_name: Name of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#bucket_name R2BucketSippy#bucket_name}
        :param destination: R2 bucket to copy objects to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#destination R2BucketSippy#destination}
        :param jurisdiction: Jurisdiction of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#jurisdiction R2BucketSippy#jurisdiction}
        :param source: AWS S3 bucket to copy objects from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#source R2BucketSippy#source}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(destination, dict):
            destination = R2BucketSippyDestination(**destination)
        if isinstance(source, dict):
            source = R2BucketSippySource(**source)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e143adef5bb2007749565ee219b2cd6ed30b8016f7179911bacfe850e713a9f0)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument jurisdiction", value=jurisdiction, expected_type=type_hints["jurisdiction"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
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
        if destination is not None:
            self._values["destination"] = destination
        if jurisdiction is not None:
            self._values["jurisdiction"] = jurisdiction
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
        '''Account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#account_id R2BucketSippy#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''Name of the bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#bucket_name R2BucketSippy#bucket_name}
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination(self) -> typing.Optional["R2BucketSippyDestination"]:
        '''R2 bucket to copy objects to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#destination R2BucketSippy#destination}
        '''
        result = self._values.get("destination")
        return typing.cast(typing.Optional["R2BucketSippyDestination"], result)

    @builtins.property
    def jurisdiction(self) -> typing.Optional[builtins.str]:
        '''Jurisdiction of the bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#jurisdiction R2BucketSippy#jurisdiction}
        '''
        result = self._values.get("jurisdiction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional["R2BucketSippySource"]:
        '''AWS S3 bucket to copy objects from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#source R2BucketSippy#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional["R2BucketSippySource"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketSippyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketSippy.R2BucketSippyDestination",
    jsii_struct_bases=[],
    name_mapping={
        "access_key_id": "accessKeyId",
        "cloud_provider": "cloudProvider",
        "secret_access_key": "secretAccessKey",
    },
)
class R2BucketSippyDestination:
    def __init__(
        self,
        *,
        access_key_id: typing.Optional[builtins.str] = None,
        cloud_provider: typing.Optional[builtins.str] = None,
        secret_access_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_key_id: ID of a Cloudflare API token. This is the value labelled "Access Key ID" when creating an API. token from the `R2 dashboard <https://dash.cloudflare.com/?to=/:account/r2/api-tokens>`_. Sippy will use this token when writing objects to R2, so it is best to scope this token to the bucket you're enabling Sippy for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#access_key_id R2BucketSippy#access_key_id}
        :param cloud_provider: Available values: "r2". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#cloud_provider R2BucketSippy#cloud_provider}
        :param secret_access_key: Value of a Cloudflare API token. This is the value labelled "Secret Access Key" when creating an API. token from the `R2 dashboard <https://dash.cloudflare.com/?to=/:account/r2/api-tokens>`_. Sippy will use this token when writing objects to R2, so it is best to scope this token to the bucket you're enabling Sippy for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#secret_access_key R2BucketSippy#secret_access_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de68fc5216a02eb4756736d9ba8b35b2c0ed5e7c57d044d7a0d0fe239f1d6393)
            check_type(argname="argument access_key_id", value=access_key_id, expected_type=type_hints["access_key_id"])
            check_type(argname="argument cloud_provider", value=cloud_provider, expected_type=type_hints["cloud_provider"])
            check_type(argname="argument secret_access_key", value=secret_access_key, expected_type=type_hints["secret_access_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_key_id is not None:
            self._values["access_key_id"] = access_key_id
        if cloud_provider is not None:
            self._values["cloud_provider"] = cloud_provider
        if secret_access_key is not None:
            self._values["secret_access_key"] = secret_access_key

    @builtins.property
    def access_key_id(self) -> typing.Optional[builtins.str]:
        '''ID of a Cloudflare API token.

        This is the value labelled "Access Key ID" when creating an API.
        token from the `R2 dashboard <https://dash.cloudflare.com/?to=/:account/r2/api-tokens>`_.

        Sippy will use this token when writing objects to R2, so it is
        best to scope this token to the bucket you're enabling Sippy for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#access_key_id R2BucketSippy#access_key_id}
        '''
        result = self._values.get("access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_provider(self) -> typing.Optional[builtins.str]:
        '''Available values: "r2".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#cloud_provider R2BucketSippy#cloud_provider}
        '''
        result = self._values.get("cloud_provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_access_key(self) -> typing.Optional[builtins.str]:
        '''Value of a Cloudflare API token.

        This is the value labelled "Secret Access Key" when creating an API.
        token from the `R2 dashboard <https://dash.cloudflare.com/?to=/:account/r2/api-tokens>`_.

        Sippy will use this token when writing objects to R2, so it is
        best to scope this token to the bucket you're enabling Sippy for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#secret_access_key R2BucketSippy#secret_access_key}
        '''
        result = self._values.get("secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketSippyDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class R2BucketSippyDestinationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketSippy.R2BucketSippyDestinationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f98f63e7b277cef38dd56cf9733a469a28609636d8ae985a12c037bfe199b863)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAccessKeyId")
    def reset_access_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessKeyId", []))

    @jsii.member(jsii_name="resetCloudProvider")
    def reset_cloud_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudProvider", []))

    @jsii.member(jsii_name="resetSecretAccessKey")
    def reset_secret_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretAccessKey", []))

    @builtins.property
    @jsii.member(jsii_name="accessKeyIdInput")
    def access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudProviderInput")
    def cloud_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="secretAccessKeyInput")
    def secret_access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretAccessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="accessKeyId")
    def access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessKeyId"))

    @access_key_id.setter
    def access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15fd7adf677465abf618d46f9a0a5ae52bc11fb26e5955d8d0d0a0bc86179de9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cloudProvider")
    def cloud_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudProvider"))

    @cloud_provider.setter
    def cloud_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3ec5b88359c55dd18eff352b6ebb8a0c257805c1189f3160b3886e6d9fc2768)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretAccessKey")
    def secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretAccessKey"))

    @secret_access_key.setter
    def secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2baff8df02f24964bb1ca11d8212a956e41ec2dedb7b6bdaf9d3706af6184253)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretAccessKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketSippyDestination]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketSippyDestination]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketSippyDestination]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e6d6bf5ee1afeb56b3890956ca7b780fdfe2814c5125dc8c5ae7c390790040b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.r2BucketSippy.R2BucketSippySource",
    jsii_struct_bases=[],
    name_mapping={
        "access_key_id": "accessKeyId",
        "bucket": "bucket",
        "client_email": "clientEmail",
        "cloud_provider": "cloudProvider",
        "private_key": "privateKey",
        "region": "region",
        "secret_access_key": "secretAccessKey",
    },
)
class R2BucketSippySource:
    def __init__(
        self,
        *,
        access_key_id: typing.Optional[builtins.str] = None,
        bucket: typing.Optional[builtins.str] = None,
        client_email: typing.Optional[builtins.str] = None,
        cloud_provider: typing.Optional[builtins.str] = None,
        private_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        secret_access_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_key_id: Access Key ID of an IAM credential (ideally scoped to a single S3 bucket). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#access_key_id R2BucketSippy#access_key_id}
        :param bucket: Name of the AWS S3 bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#bucket R2BucketSippy#bucket}
        :param client_email: Client email of an IAM credential (ideally scoped to a single GCS bucket). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#client_email R2BucketSippy#client_email}
        :param cloud_provider: Available values: "aws", "gcs". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#cloud_provider R2BucketSippy#cloud_provider}
        :param private_key: Private Key of an IAM credential (ideally scoped to a single GCS bucket). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#private_key R2BucketSippy#private_key}
        :param region: Name of the AWS availability zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#region R2BucketSippy#region}
        :param secret_access_key: Secret Access Key of an IAM credential (ideally scoped to a single S3 bucket). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#secret_access_key R2BucketSippy#secret_access_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0617aa809fe42041099da931e83c204b62c806295f49674f94ca8d082bc97f06)
            check_type(argname="argument access_key_id", value=access_key_id, expected_type=type_hints["access_key_id"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument client_email", value=client_email, expected_type=type_hints["client_email"])
            check_type(argname="argument cloud_provider", value=cloud_provider, expected_type=type_hints["cloud_provider"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument secret_access_key", value=secret_access_key, expected_type=type_hints["secret_access_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_key_id is not None:
            self._values["access_key_id"] = access_key_id
        if bucket is not None:
            self._values["bucket"] = bucket
        if client_email is not None:
            self._values["client_email"] = client_email
        if cloud_provider is not None:
            self._values["cloud_provider"] = cloud_provider
        if private_key is not None:
            self._values["private_key"] = private_key
        if region is not None:
            self._values["region"] = region
        if secret_access_key is not None:
            self._values["secret_access_key"] = secret_access_key

    @builtins.property
    def access_key_id(self) -> typing.Optional[builtins.str]:
        '''Access Key ID of an IAM credential (ideally scoped to a single S3 bucket).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#access_key_id R2BucketSippy#access_key_id}
        '''
        result = self._values.get("access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket(self) -> typing.Optional[builtins.str]:
        '''Name of the AWS S3 bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#bucket R2BucketSippy#bucket}
        '''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_email(self) -> typing.Optional[builtins.str]:
        '''Client email of an IAM credential (ideally scoped to a single GCS bucket).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#client_email R2BucketSippy#client_email}
        '''
        result = self._values.get("client_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_provider(self) -> typing.Optional[builtins.str]:
        '''Available values: "aws", "gcs".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#cloud_provider R2BucketSippy#cloud_provider}
        '''
        result = self._values.get("cloud_provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key(self) -> typing.Optional[builtins.str]:
        '''Private Key of an IAM credential (ideally scoped to a single GCS bucket).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#private_key R2BucketSippy#private_key}
        '''
        result = self._values.get("private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Name of the AWS availability zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#region R2BucketSippy#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_access_key(self) -> typing.Optional[builtins.str]:
        '''Secret Access Key of an IAM credential (ideally scoped to a single S3 bucket).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/r2_bucket_sippy#secret_access_key R2BucketSippy#secret_access_key}
        '''
        result = self._values.get("secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R2BucketSippySource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class R2BucketSippySourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.r2BucketSippy.R2BucketSippySourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a865ec4231dc65ecd66b820da020c5672e13bb6634369037f46b526d9e77496)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAccessKeyId")
    def reset_access_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessKeyId", []))

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetClientEmail")
    def reset_client_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientEmail", []))

    @jsii.member(jsii_name="resetCloudProvider")
    def reset_cloud_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudProvider", []))

    @jsii.member(jsii_name="resetPrivateKey")
    def reset_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKey", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetSecretAccessKey")
    def reset_secret_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretAccessKey", []))

    @builtins.property
    @jsii.member(jsii_name="accessKeyIdInput")
    def access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property
    @jsii.member(jsii_name="clientEmailInput")
    def client_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudProviderInput")
    def cloud_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="secretAccessKeyInput")
    def secret_access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretAccessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="accessKeyId")
    def access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessKeyId"))

    @access_key_id.setter
    def access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aee6e26d87984eeaf490725e2ae5e17e1ddac75c3ef4ac313a9248985c86a892)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ab6cf9947578491fd91d6acbd9a71c4d209c8d86e0798dc32a0d3795d7efe86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientEmail")
    def client_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientEmail"))

    @client_email.setter
    def client_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd93e6b05588be855cfb4ffe98075abc84102fc15eeded7cfc6960cd724a7023)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cloudProvider")
    def cloud_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudProvider"))

    @cloud_provider.setter
    def cloud_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea5a52a526a62f40c07feb5388de279d21edb137cc4b892aedc202fd44f15acd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__204af35c14264875092786335d304767a9f539b214e4db24ccf3e68a1b8a6c0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b06edbe90b8a4a66e5555e08549eacf3dd0a3f4b8b0d03fd0a9ba202eaf76a6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretAccessKey")
    def secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretAccessKey"))

    @secret_access_key.setter
    def secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f744fd70a274c6a7013d6c3fac07961b074183d75f0c83a6b6d64ef157a229fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretAccessKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketSippySource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketSippySource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketSippySource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e883ad65741edd2074076985c359ae0a379df757474532106f0345475f432d53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "R2BucketSippy",
    "R2BucketSippyConfig",
    "R2BucketSippyDestination",
    "R2BucketSippyDestinationOutputReference",
    "R2BucketSippySource",
    "R2BucketSippySourceOutputReference",
]

publication.publish()

def _typecheckingstub__2acc48b499268225209f8b297847fecfe387865cc82e3f539d2fa182051f9d29(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    bucket_name: builtins.str,
    destination: typing.Optional[typing.Union[R2BucketSippyDestination, typing.Dict[builtins.str, typing.Any]]] = None,
    jurisdiction: typing.Optional[builtins.str] = None,
    source: typing.Optional[typing.Union[R2BucketSippySource, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__1c3e9e8dfcc23e1c69505df4e69e18b99b23beb538f3428f79e842b31c77e62d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e0650ad3b95b759572c3847f68f635f1dbf3585dfa7bbcb7d6bc8e1694b5003(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55cc532585ed0e4c90051eb2f62e5edc178559395069cfef044ac70ac8a57bf0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a3cf358207801e9dd72ba5183a9240a5fb51c6483bf7d1e433151e0732d88ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e143adef5bb2007749565ee219b2cd6ed30b8016f7179911bacfe850e713a9f0(
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
    destination: typing.Optional[typing.Union[R2BucketSippyDestination, typing.Dict[builtins.str, typing.Any]]] = None,
    jurisdiction: typing.Optional[builtins.str] = None,
    source: typing.Optional[typing.Union[R2BucketSippySource, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de68fc5216a02eb4756736d9ba8b35b2c0ed5e7c57d044d7a0d0fe239f1d6393(
    *,
    access_key_id: typing.Optional[builtins.str] = None,
    cloud_provider: typing.Optional[builtins.str] = None,
    secret_access_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f98f63e7b277cef38dd56cf9733a469a28609636d8ae985a12c037bfe199b863(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15fd7adf677465abf618d46f9a0a5ae52bc11fb26e5955d8d0d0a0bc86179de9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3ec5b88359c55dd18eff352b6ebb8a0c257805c1189f3160b3886e6d9fc2768(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2baff8df02f24964bb1ca11d8212a956e41ec2dedb7b6bdaf9d3706af6184253(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e6d6bf5ee1afeb56b3890956ca7b780fdfe2814c5125dc8c5ae7c390790040b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketSippyDestination]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0617aa809fe42041099da931e83c204b62c806295f49674f94ca8d082bc97f06(
    *,
    access_key_id: typing.Optional[builtins.str] = None,
    bucket: typing.Optional[builtins.str] = None,
    client_email: typing.Optional[builtins.str] = None,
    cloud_provider: typing.Optional[builtins.str] = None,
    private_key: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    secret_access_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a865ec4231dc65ecd66b820da020c5672e13bb6634369037f46b526d9e77496(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aee6e26d87984eeaf490725e2ae5e17e1ddac75c3ef4ac313a9248985c86a892(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ab6cf9947578491fd91d6acbd9a71c4d209c8d86e0798dc32a0d3795d7efe86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd93e6b05588be855cfb4ffe98075abc84102fc15eeded7cfc6960cd724a7023(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea5a52a526a62f40c07feb5388de279d21edb137cc4b892aedc202fd44f15acd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__204af35c14264875092786335d304767a9f539b214e4db24ccf3e68a1b8a6c0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b06edbe90b8a4a66e5555e08549eacf3dd0a3f4b8b0d03fd0a9ba202eaf76a6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f744fd70a274c6a7013d6c3fac07961b074183d75f0c83a6b6d64ef157a229fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e883ad65741edd2074076985c359ae0a379df757474532106f0345475f432d53(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, R2BucketSippySource]],
) -> None:
    """Type checking stubs"""
    pass
