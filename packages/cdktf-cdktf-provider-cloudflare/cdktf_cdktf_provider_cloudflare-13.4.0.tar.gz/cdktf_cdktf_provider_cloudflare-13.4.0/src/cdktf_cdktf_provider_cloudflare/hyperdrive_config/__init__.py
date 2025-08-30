r'''
# `cloudflare_hyperdrive_config`

Refer to the Terraform Registry for docs: [`cloudflare_hyperdrive_config`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config).
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


class HyperdriveConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.hyperdriveConfig.HyperdriveConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config cloudflare_hyperdrive_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        name: builtins.str,
        origin: typing.Union["HyperdriveConfigOrigin", typing.Dict[builtins.str, typing.Any]],
        caching: typing.Optional[typing.Union["HyperdriveConfigCaching", typing.Dict[builtins.str, typing.Any]]] = None,
        mtls: typing.Optional[typing.Union["HyperdriveConfigMtls", typing.Dict[builtins.str, typing.Any]]] = None,
        origin_connection_limit: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config cloudflare_hyperdrive_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Define configurations using a unique string identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#account_id HyperdriveConfig#account_id}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#name HyperdriveConfig#name}.
        :param origin: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#origin HyperdriveConfig#origin}.
        :param caching: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#caching HyperdriveConfig#caching}.
        :param mtls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#mtls HyperdriveConfig#mtls}.
        :param origin_connection_limit: The (soft) maximum number of connections the Hyperdrive is allowed to make to the origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#origin_connection_limit HyperdriveConfig#origin_connection_limit}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30c2b4f50194990bd5bbd6ed29f1c3a05eea46658757e355714f55c910cfd5e9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = HyperdriveConfigConfig(
            account_id=account_id,
            name=name,
            origin=origin,
            caching=caching,
            mtls=mtls,
            origin_connection_limit=origin_connection_limit,
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
        '''Generates CDKTF code for importing a HyperdriveConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the HyperdriveConfig to import.
        :param import_from_id: The id of the existing HyperdriveConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the HyperdriveConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4c6038ef37111fb622390da9bec3d349a523660646deaaba4db3d9e93f8fa2b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCaching")
    def put_caching(
        self,
        *,
        disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_age: typing.Optional[jsii.Number] = None,
        stale_while_revalidate: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param disabled: Set to true to disable caching of SQL responses. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#disabled HyperdriveConfig#disabled}
        :param max_age: Specify the maximum duration items should persist in the cache. Not returned if set to the default (60). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#max_age HyperdriveConfig#max_age}
        :param stale_while_revalidate: Specify the number of seconds the cache may serve a stale response. Omitted if set to the default (15). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#stale_while_revalidate HyperdriveConfig#stale_while_revalidate}
        '''
        value = HyperdriveConfigCaching(
            disabled=disabled,
            max_age=max_age,
            stale_while_revalidate=stale_while_revalidate,
        )

        return typing.cast(None, jsii.invoke(self, "putCaching", [value]))

    @jsii.member(jsii_name="putMtls")
    def put_mtls(
        self,
        *,
        ca_certificate_id: typing.Optional[builtins.str] = None,
        mtls_certificate_id: typing.Optional[builtins.str] = None,
        sslmode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ca_certificate_id: Define CA certificate ID obtained after uploading CA cert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#ca_certificate_id HyperdriveConfig#ca_certificate_id}
        :param mtls_certificate_id: Define mTLS certificate ID obtained after uploading client cert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#mtls_certificate_id HyperdriveConfig#mtls_certificate_id}
        :param sslmode: Set SSL mode to 'require', 'verify-ca', or 'verify-full' to verify the CA. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#sslmode HyperdriveConfig#sslmode}
        '''
        value = HyperdriveConfigMtls(
            ca_certificate_id=ca_certificate_id,
            mtls_certificate_id=mtls_certificate_id,
            sslmode=sslmode,
        )

        return typing.cast(None, jsii.invoke(self, "putMtls", [value]))

    @jsii.member(jsii_name="putOrigin")
    def put_origin(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        password: builtins.str,
        scheme: builtins.str,
        user: builtins.str,
        access_client_id: typing.Optional[builtins.str] = None,
        access_client_secret: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param database: Set the name of your origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#database HyperdriveConfig#database}
        :param host: Defines the host (hostname or IP) of your origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#host HyperdriveConfig#host}
        :param password: Set the password needed to access your origin database. The API never returns this write-only value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#password HyperdriveConfig#password}
        :param scheme: Specifies the URL scheme used to connect to your origin database. Available values: "postgres", "postgresql", "mysql". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#scheme HyperdriveConfig#scheme}
        :param user: Set the user of your origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#user HyperdriveConfig#user}
        :param access_client_id: Defines the Client ID of the Access token to use when connecting to the origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#access_client_id HyperdriveConfig#access_client_id}
        :param access_client_secret: Defines the Client Secret of the Access Token to use when connecting to the origin database. The API never returns this write-only value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#access_client_secret HyperdriveConfig#access_client_secret}
        :param port: Defines the port (default: 5432 for Postgres) of your origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#port HyperdriveConfig#port}
        '''
        value = HyperdriveConfigOrigin(
            database=database,
            host=host,
            password=password,
            scheme=scheme,
            user=user,
            access_client_id=access_client_id,
            access_client_secret=access_client_secret,
            port=port,
        )

        return typing.cast(None, jsii.invoke(self, "putOrigin", [value]))

    @jsii.member(jsii_name="resetCaching")
    def reset_caching(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaching", []))

    @jsii.member(jsii_name="resetMtls")
    def reset_mtls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMtls", []))

    @jsii.member(jsii_name="resetOriginConnectionLimit")
    def reset_origin_connection_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginConnectionLimit", []))

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
    @jsii.member(jsii_name="caching")
    def caching(self) -> "HyperdriveConfigCachingOutputReference":
        return typing.cast("HyperdriveConfigCachingOutputReference", jsii.get(self, "caching"))

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
    @jsii.member(jsii_name="mtls")
    def mtls(self) -> "HyperdriveConfigMtlsOutputReference":
        return typing.cast("HyperdriveConfigMtlsOutputReference", jsii.get(self, "mtls"))

    @builtins.property
    @jsii.member(jsii_name="origin")
    def origin(self) -> "HyperdriveConfigOriginOutputReference":
        return typing.cast("HyperdriveConfigOriginOutputReference", jsii.get(self, "origin"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="cachingInput")
    def caching_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "HyperdriveConfigCaching"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "HyperdriveConfigCaching"]], jsii.get(self, "cachingInput"))

    @builtins.property
    @jsii.member(jsii_name="mtlsInput")
    def mtls_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "HyperdriveConfigMtls"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "HyperdriveConfigMtls"]], jsii.get(self, "mtlsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="originConnectionLimitInput")
    def origin_connection_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "originConnectionLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="originInput")
    def origin_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "HyperdriveConfigOrigin"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "HyperdriveConfigOrigin"]], jsii.get(self, "originInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4986a8746a24a321b7fe1d5c27ead68912dc85214cb858d21989fc4214f634d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9345849c5b82c0798e0e2486711fc6f906a8473fba7c4cee71daaefa9dcab42c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="originConnectionLimit")
    def origin_connection_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "originConnectionLimit"))

    @origin_connection_limit.setter
    def origin_connection_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3defbb0d32b099c060b0db3365eadd0be4d947433c7809f9600e60aa983a10b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "originConnectionLimit", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.hyperdriveConfig.HyperdriveConfigCaching",
    jsii_struct_bases=[],
    name_mapping={
        "disabled": "disabled",
        "max_age": "maxAge",
        "stale_while_revalidate": "staleWhileRevalidate",
    },
)
class HyperdriveConfigCaching:
    def __init__(
        self,
        *,
        disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_age: typing.Optional[jsii.Number] = None,
        stale_while_revalidate: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param disabled: Set to true to disable caching of SQL responses. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#disabled HyperdriveConfig#disabled}
        :param max_age: Specify the maximum duration items should persist in the cache. Not returned if set to the default (60). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#max_age HyperdriveConfig#max_age}
        :param stale_while_revalidate: Specify the number of seconds the cache may serve a stale response. Omitted if set to the default (15). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#stale_while_revalidate HyperdriveConfig#stale_while_revalidate}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__944f9727e7a5e31c7adffd748763a6a5d4e794d962f5e30299ac8c68145531f1)
            check_type(argname="argument disabled", value=disabled, expected_type=type_hints["disabled"])
            check_type(argname="argument max_age", value=max_age, expected_type=type_hints["max_age"])
            check_type(argname="argument stale_while_revalidate", value=stale_while_revalidate, expected_type=type_hints["stale_while_revalidate"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if disabled is not None:
            self._values["disabled"] = disabled
        if max_age is not None:
            self._values["max_age"] = max_age
        if stale_while_revalidate is not None:
            self._values["stale_while_revalidate"] = stale_while_revalidate

    @builtins.property
    def disabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to disable caching of SQL responses. Default is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#disabled HyperdriveConfig#disabled}
        '''
        result = self._values.get("disabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_age(self) -> typing.Optional[jsii.Number]:
        '''Specify the maximum duration items should persist in the cache. Not returned if set to the default (60).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#max_age HyperdriveConfig#max_age}
        '''
        result = self._values.get("max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def stale_while_revalidate(self) -> typing.Optional[jsii.Number]:
        '''Specify the number of seconds the cache may serve a stale response. Omitted if set to the default (15).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#stale_while_revalidate HyperdriveConfig#stale_while_revalidate}
        '''
        result = self._values.get("stale_while_revalidate")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HyperdriveConfigCaching(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HyperdriveConfigCachingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.hyperdriveConfig.HyperdriveConfigCachingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__78a97e417367e0c505011eabd819c742d64f3cc4dc372f0ff3205b0e8de9a421)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDisabled")
    def reset_disabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisabled", []))

    @jsii.member(jsii_name="resetMaxAge")
    def reset_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAge", []))

    @jsii.member(jsii_name="resetStaleWhileRevalidate")
    def reset_stale_while_revalidate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaleWhileRevalidate", []))

    @builtins.property
    @jsii.member(jsii_name="disabledInput")
    def disabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disabledInput"))

    @builtins.property
    @jsii.member(jsii_name="maxAgeInput")
    def max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="staleWhileRevalidateInput")
    def stale_while_revalidate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "staleWhileRevalidateInput"))

    @builtins.property
    @jsii.member(jsii_name="disabled")
    def disabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disabled"))

    @disabled.setter
    def disabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66aa0f06f3aeebd1afad0e79a93a1671be028672167bc7837e45f4c8aa328e23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAge")
    def max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAge"))

    @max_age.setter
    def max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b1548d04b0d049b0f2c746f2cce4b34c91b1efb16a025726c006ebbb17e16e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAge", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="staleWhileRevalidate")
    def stale_while_revalidate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "staleWhileRevalidate"))

    @stale_while_revalidate.setter
    def stale_while_revalidate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ab4d1f78c54cd1eff9d995d78c44b07a282c1ca9a5735222a0f5eff165789f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staleWhileRevalidate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigCaching]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigCaching]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigCaching]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9161a0df8175c4b2fcaf7f6d1b47a7492fcf3c7f85966b347004881f31a05bd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.hyperdriveConfig.HyperdriveConfigConfig",
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
        "origin": "origin",
        "caching": "caching",
        "mtls": "mtls",
        "origin_connection_limit": "originConnectionLimit",
    },
)
class HyperdriveConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        origin: typing.Union["HyperdriveConfigOrigin", typing.Dict[builtins.str, typing.Any]],
        caching: typing.Optional[typing.Union[HyperdriveConfigCaching, typing.Dict[builtins.str, typing.Any]]] = None,
        mtls: typing.Optional[typing.Union["HyperdriveConfigMtls", typing.Dict[builtins.str, typing.Any]]] = None,
        origin_connection_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Define configurations using a unique string identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#account_id HyperdriveConfig#account_id}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#name HyperdriveConfig#name}.
        :param origin: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#origin HyperdriveConfig#origin}.
        :param caching: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#caching HyperdriveConfig#caching}.
        :param mtls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#mtls HyperdriveConfig#mtls}.
        :param origin_connection_limit: The (soft) maximum number of connections the Hyperdrive is allowed to make to the origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#origin_connection_limit HyperdriveConfig#origin_connection_limit}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(origin, dict):
            origin = HyperdriveConfigOrigin(**origin)
        if isinstance(caching, dict):
            caching = HyperdriveConfigCaching(**caching)
        if isinstance(mtls, dict):
            mtls = HyperdriveConfigMtls(**mtls)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9c1440046f9002294014fca0fbe3f3e077c911424fa11e63d35ad4b88cca05e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument origin", value=origin, expected_type=type_hints["origin"])
            check_type(argname="argument caching", value=caching, expected_type=type_hints["caching"])
            check_type(argname="argument mtls", value=mtls, expected_type=type_hints["mtls"])
            check_type(argname="argument origin_connection_limit", value=origin_connection_limit, expected_type=type_hints["origin_connection_limit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "name": name,
            "origin": origin,
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
        if caching is not None:
            self._values["caching"] = caching
        if mtls is not None:
            self._values["mtls"] = mtls
        if origin_connection_limit is not None:
            self._values["origin_connection_limit"] = origin_connection_limit

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
        '''Define configurations using a unique string identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#account_id HyperdriveConfig#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#name HyperdriveConfig#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def origin(self) -> "HyperdriveConfigOrigin":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#origin HyperdriveConfig#origin}.'''
        result = self._values.get("origin")
        assert result is not None, "Required property 'origin' is missing"
        return typing.cast("HyperdriveConfigOrigin", result)

    @builtins.property
    def caching(self) -> typing.Optional[HyperdriveConfigCaching]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#caching HyperdriveConfig#caching}.'''
        result = self._values.get("caching")
        return typing.cast(typing.Optional[HyperdriveConfigCaching], result)

    @builtins.property
    def mtls(self) -> typing.Optional["HyperdriveConfigMtls"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#mtls HyperdriveConfig#mtls}.'''
        result = self._values.get("mtls")
        return typing.cast(typing.Optional["HyperdriveConfigMtls"], result)

    @builtins.property
    def origin_connection_limit(self) -> typing.Optional[jsii.Number]:
        '''The (soft) maximum number of connections the Hyperdrive is allowed to make to the origin database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#origin_connection_limit HyperdriveConfig#origin_connection_limit}
        '''
        result = self._values.get("origin_connection_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HyperdriveConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.hyperdriveConfig.HyperdriveConfigMtls",
    jsii_struct_bases=[],
    name_mapping={
        "ca_certificate_id": "caCertificateId",
        "mtls_certificate_id": "mtlsCertificateId",
        "sslmode": "sslmode",
    },
)
class HyperdriveConfigMtls:
    def __init__(
        self,
        *,
        ca_certificate_id: typing.Optional[builtins.str] = None,
        mtls_certificate_id: typing.Optional[builtins.str] = None,
        sslmode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ca_certificate_id: Define CA certificate ID obtained after uploading CA cert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#ca_certificate_id HyperdriveConfig#ca_certificate_id}
        :param mtls_certificate_id: Define mTLS certificate ID obtained after uploading client cert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#mtls_certificate_id HyperdriveConfig#mtls_certificate_id}
        :param sslmode: Set SSL mode to 'require', 'verify-ca', or 'verify-full' to verify the CA. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#sslmode HyperdriveConfig#sslmode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7b078cc4f722bbe69c4d07d8477e2728011d39a135402da4d60aaa6d273f0be)
            check_type(argname="argument ca_certificate_id", value=ca_certificate_id, expected_type=type_hints["ca_certificate_id"])
            check_type(argname="argument mtls_certificate_id", value=mtls_certificate_id, expected_type=type_hints["mtls_certificate_id"])
            check_type(argname="argument sslmode", value=sslmode, expected_type=type_hints["sslmode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ca_certificate_id is not None:
            self._values["ca_certificate_id"] = ca_certificate_id
        if mtls_certificate_id is not None:
            self._values["mtls_certificate_id"] = mtls_certificate_id
        if sslmode is not None:
            self._values["sslmode"] = sslmode

    @builtins.property
    def ca_certificate_id(self) -> typing.Optional[builtins.str]:
        '''Define CA certificate ID obtained after uploading CA cert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#ca_certificate_id HyperdriveConfig#ca_certificate_id}
        '''
        result = self._values.get("ca_certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mtls_certificate_id(self) -> typing.Optional[builtins.str]:
        '''Define mTLS certificate ID obtained after uploading client cert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#mtls_certificate_id HyperdriveConfig#mtls_certificate_id}
        '''
        result = self._values.get("mtls_certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sslmode(self) -> typing.Optional[builtins.str]:
        '''Set SSL mode to 'require', 'verify-ca', or 'verify-full' to verify the CA.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#sslmode HyperdriveConfig#sslmode}
        '''
        result = self._values.get("sslmode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HyperdriveConfigMtls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HyperdriveConfigMtlsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.hyperdriveConfig.HyperdriveConfigMtlsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__36a0b0c173206c18147c8f21f89d14e383079b216e4c518a4e57e0861623dbdd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCaCertificateId")
    def reset_ca_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaCertificateId", []))

    @jsii.member(jsii_name="resetMtlsCertificateId")
    def reset_mtls_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMtlsCertificateId", []))

    @jsii.member(jsii_name="resetSslmode")
    def reset_sslmode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslmode", []))

    @builtins.property
    @jsii.member(jsii_name="caCertificateIdInput")
    def ca_certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertificateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="mtlsCertificateIdInput")
    def mtls_certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mtlsCertificateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="sslmodeInput")
    def sslmode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslmodeInput"))

    @builtins.property
    @jsii.member(jsii_name="caCertificateId")
    def ca_certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCertificateId"))

    @ca_certificate_id.setter
    def ca_certificate_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__238dd8dd6a30b75fdb62609673c0314c6c1f5c2958da8d27b83a6e89b69e3c9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caCertificateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mtlsCertificateId")
    def mtls_certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mtlsCertificateId"))

    @mtls_certificate_id.setter
    def mtls_certificate_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0d2ce1205b2b44fab9c428c10e6cf35c4331877bc11c3452cca0dd1c2a4a75c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mtlsCertificateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sslmode")
    def sslmode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslmode"))

    @sslmode.setter
    def sslmode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e6de7c1d2025251552edb362ea2d4f9b61cbe66fc6f7138a4fd531d0a2a7bc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sslmode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigMtls]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigMtls]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigMtls]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a05d85dd083b3b4e019d100f3ecbb7d703b53183745301eafd329aa68bde46b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.hyperdriveConfig.HyperdriveConfigOrigin",
    jsii_struct_bases=[],
    name_mapping={
        "database": "database",
        "host": "host",
        "password": "password",
        "scheme": "scheme",
        "user": "user",
        "access_client_id": "accessClientId",
        "access_client_secret": "accessClientSecret",
        "port": "port",
    },
)
class HyperdriveConfigOrigin:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        password: builtins.str,
        scheme: builtins.str,
        user: builtins.str,
        access_client_id: typing.Optional[builtins.str] = None,
        access_client_secret: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param database: Set the name of your origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#database HyperdriveConfig#database}
        :param host: Defines the host (hostname or IP) of your origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#host HyperdriveConfig#host}
        :param password: Set the password needed to access your origin database. The API never returns this write-only value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#password HyperdriveConfig#password}
        :param scheme: Specifies the URL scheme used to connect to your origin database. Available values: "postgres", "postgresql", "mysql". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#scheme HyperdriveConfig#scheme}
        :param user: Set the user of your origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#user HyperdriveConfig#user}
        :param access_client_id: Defines the Client ID of the Access token to use when connecting to the origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#access_client_id HyperdriveConfig#access_client_id}
        :param access_client_secret: Defines the Client Secret of the Access Token to use when connecting to the origin database. The API never returns this write-only value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#access_client_secret HyperdriveConfig#access_client_secret}
        :param port: Defines the port (default: 5432 for Postgres) of your origin database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#port HyperdriveConfig#port}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13c452f1047593d1ee736bc0aefe675bf19cc3f8b4c976fc402211ca197302f0)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument scheme", value=scheme, expected_type=type_hints["scheme"])
            check_type(argname="argument user", value=user, expected_type=type_hints["user"])
            check_type(argname="argument access_client_id", value=access_client_id, expected_type=type_hints["access_client_id"])
            check_type(argname="argument access_client_secret", value=access_client_secret, expected_type=type_hints["access_client_secret"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database": database,
            "host": host,
            "password": password,
            "scheme": scheme,
            "user": user,
        }
        if access_client_id is not None:
            self._values["access_client_id"] = access_client_id
        if access_client_secret is not None:
            self._values["access_client_secret"] = access_client_secret
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def database(self) -> builtins.str:
        '''Set the name of your origin database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#database HyperdriveConfig#database}
        '''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Defines the host (hostname or IP) of your origin database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#host HyperdriveConfig#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Set the password needed to access your origin database. The API never returns this write-only value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#password HyperdriveConfig#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scheme(self) -> builtins.str:
        '''Specifies the URL scheme used to connect to your origin database. Available values: "postgres", "postgresql", "mysql".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#scheme HyperdriveConfig#scheme}
        '''
        result = self._values.get("scheme")
        assert result is not None, "Required property 'scheme' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user(self) -> builtins.str:
        '''Set the user of your origin database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#user HyperdriveConfig#user}
        '''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_client_id(self) -> typing.Optional[builtins.str]:
        '''Defines the Client ID of the Access token to use when connecting to the origin database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#access_client_id HyperdriveConfig#access_client_id}
        '''
        result = self._values.get("access_client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def access_client_secret(self) -> typing.Optional[builtins.str]:
        '''Defines the Client Secret of the Access Token to use when connecting to the origin database.

        The API never returns this write-only value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#access_client_secret HyperdriveConfig#access_client_secret}
        '''
        result = self._values.get("access_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Defines the port (default: 5432 for Postgres) of your origin database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/hyperdrive_config#port HyperdriveConfig#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HyperdriveConfigOrigin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HyperdriveConfigOriginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.hyperdriveConfig.HyperdriveConfigOriginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be44cf52ed92f39ef8228857332177cfc8166192f03be4ffc537dbc9a24ec39a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAccessClientId")
    def reset_access_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessClientId", []))

    @jsii.member(jsii_name="resetAccessClientSecret")
    def reset_access_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessClientSecret", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @builtins.property
    @jsii.member(jsii_name="accessClientIdInput")
    def access_client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessClientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accessClientSecretInput")
    def access_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="schemeInput")
    def scheme_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemeInput"))

    @builtins.property
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property
    @jsii.member(jsii_name="accessClientId")
    def access_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessClientId"))

    @access_client_id.setter
    def access_client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f1a9e51ae07b4944f6362e25dc12bc8f01eec1c6b4e5d08001715a0c01d4d4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessClientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="accessClientSecret")
    def access_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessClientSecret"))

    @access_client_secret.setter
    def access_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdde17e6028218f4ae0770557341d94b70ea3813e4965ec251ac621ccb7770ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessClientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33b8948187ff0a7918fb00499b75295fc59bc749506654b9bcb7434a3442ccd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b596a14b5db407e5d90558e2c6fc917035315174a6c6b69678edf3aafda1f135)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__866cc57b9bcd8d0c07db136eb27b4740f970f2aa6a0086a8d935edd37df886a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e66efefc89b80c9612506fb6077b98372bd5e98039af46630c3f45cfbb13e2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scheme")
    def scheme(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheme"))

    @scheme.setter
    def scheme(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eddb2c5cb0c79ebca14ac931edf0f46b024a1bea0e726322318ab98f9db9929e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheme", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__193fcfc9ff83a2ce808087e93d32af2d602621b3c936354f373e29c6d8991252)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigOrigin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigOrigin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigOrigin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__884eee0ce1a402eb943940704d5af9fd4a3c696b79ab0c5871b91aea3830b42b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "HyperdriveConfig",
    "HyperdriveConfigCaching",
    "HyperdriveConfigCachingOutputReference",
    "HyperdriveConfigConfig",
    "HyperdriveConfigMtls",
    "HyperdriveConfigMtlsOutputReference",
    "HyperdriveConfigOrigin",
    "HyperdriveConfigOriginOutputReference",
]

publication.publish()

def _typecheckingstub__30c2b4f50194990bd5bbd6ed29f1c3a05eea46658757e355714f55c910cfd5e9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    name: builtins.str,
    origin: typing.Union[HyperdriveConfigOrigin, typing.Dict[builtins.str, typing.Any]],
    caching: typing.Optional[typing.Union[HyperdriveConfigCaching, typing.Dict[builtins.str, typing.Any]]] = None,
    mtls: typing.Optional[typing.Union[HyperdriveConfigMtls, typing.Dict[builtins.str, typing.Any]]] = None,
    origin_connection_limit: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__c4c6038ef37111fb622390da9bec3d349a523660646deaaba4db3d9e93f8fa2b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4986a8746a24a321b7fe1d5c27ead68912dc85214cb858d21989fc4214f634d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9345849c5b82c0798e0e2486711fc6f906a8473fba7c4cee71daaefa9dcab42c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3defbb0d32b099c060b0db3365eadd0be4d947433c7809f9600e60aa983a10b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__944f9727e7a5e31c7adffd748763a6a5d4e794d962f5e30299ac8c68145531f1(
    *,
    disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_age: typing.Optional[jsii.Number] = None,
    stale_while_revalidate: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78a97e417367e0c505011eabd819c742d64f3cc4dc372f0ff3205b0e8de9a421(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66aa0f06f3aeebd1afad0e79a93a1671be028672167bc7837e45f4c8aa328e23(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b1548d04b0d049b0f2c746f2cce4b34c91b1efb16a025726c006ebbb17e16e5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ab4d1f78c54cd1eff9d995d78c44b07a282c1ca9a5735222a0f5eff165789f0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9161a0df8175c4b2fcaf7f6d1b47a7492fcf3c7f85966b347004881f31a05bd3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigCaching]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9c1440046f9002294014fca0fbe3f3e077c911424fa11e63d35ad4b88cca05e(
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
    origin: typing.Union[HyperdriveConfigOrigin, typing.Dict[builtins.str, typing.Any]],
    caching: typing.Optional[typing.Union[HyperdriveConfigCaching, typing.Dict[builtins.str, typing.Any]]] = None,
    mtls: typing.Optional[typing.Union[HyperdriveConfigMtls, typing.Dict[builtins.str, typing.Any]]] = None,
    origin_connection_limit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7b078cc4f722bbe69c4d07d8477e2728011d39a135402da4d60aaa6d273f0be(
    *,
    ca_certificate_id: typing.Optional[builtins.str] = None,
    mtls_certificate_id: typing.Optional[builtins.str] = None,
    sslmode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36a0b0c173206c18147c8f21f89d14e383079b216e4c518a4e57e0861623dbdd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__238dd8dd6a30b75fdb62609673c0314c6c1f5c2958da8d27b83a6e89b69e3c9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0d2ce1205b2b44fab9c428c10e6cf35c4331877bc11c3452cca0dd1c2a4a75c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e6de7c1d2025251552edb362ea2d4f9b61cbe66fc6f7138a4fd531d0a2a7bc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a05d85dd083b3b4e019d100f3ecbb7d703b53183745301eafd329aa68bde46b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigMtls]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13c452f1047593d1ee736bc0aefe675bf19cc3f8b4c976fc402211ca197302f0(
    *,
    database: builtins.str,
    host: builtins.str,
    password: builtins.str,
    scheme: builtins.str,
    user: builtins.str,
    access_client_id: typing.Optional[builtins.str] = None,
    access_client_secret: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be44cf52ed92f39ef8228857332177cfc8166192f03be4ffc537dbc9a24ec39a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f1a9e51ae07b4944f6362e25dc12bc8f01eec1c6b4e5d08001715a0c01d4d4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdde17e6028218f4ae0770557341d94b70ea3813e4965ec251ac621ccb7770ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33b8948187ff0a7918fb00499b75295fc59bc749506654b9bcb7434a3442ccd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b596a14b5db407e5d90558e2c6fc917035315174a6c6b69678edf3aafda1f135(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__866cc57b9bcd8d0c07db136eb27b4740f970f2aa6a0086a8d935edd37df886a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e66efefc89b80c9612506fb6077b98372bd5e98039af46630c3f45cfbb13e2d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eddb2c5cb0c79ebca14ac931edf0f46b024a1bea0e726322318ab98f9db9929e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__193fcfc9ff83a2ce808087e93d32af2d602621b3c936354f373e29c6d8991252(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__884eee0ce1a402eb943940704d5af9fd4a3c696b79ab0c5871b91aea3830b42b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyperdriveConfigOrigin]],
) -> None:
    """Type checking stubs"""
    pass
