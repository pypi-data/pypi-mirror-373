r'''
# `data_cloudflare_zero_trust_tunnel_cloudflared`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_tunnel_cloudflared`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared).
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


class DataCloudflareZeroTrustTunnelCloudflared(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflared.DataCloudflareZeroTrustTunnelCloudflared",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared cloudflare_zero_trust_tunnel_cloudflared}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        filter: typing.Optional[typing.Union["DataCloudflareZeroTrustTunnelCloudflaredFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        tunnel_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared cloudflare_zero_trust_tunnel_cloudflared} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Cloudflare account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#account_id DataCloudflareZeroTrustTunnelCloudflared#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#filter DataCloudflareZeroTrustTunnelCloudflared#filter}.
        :param tunnel_id: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#tunnel_id DataCloudflareZeroTrustTunnelCloudflared#tunnel_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44156098edf305709654edebaea82efae448c037aafb7ffb7c0bfca805d7e6a9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustTunnelCloudflaredConfig(
            account_id=account_id,
            filter=filter,
            tunnel_id=tunnel_id,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustTunnelCloudflared resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustTunnelCloudflared to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustTunnelCloudflared that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustTunnelCloudflared to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9b5834618e3077f66fa8e7597afbd5623474f43c6b7e49ee3ca07dac9d52b6a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        exclude_prefix: typing.Optional[builtins.str] = None,
        existed_at: typing.Optional[builtins.str] = None,
        include_prefix: typing.Optional[builtins.str] = None,
        is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
        was_active_at: typing.Optional[builtins.str] = None,
        was_inactive_at: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param exclude_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#exclude_prefix DataCloudflareZeroTrustTunnelCloudflared#exclude_prefix}.
        :param existed_at: If provided, include only resources that were created (and not deleted) before this time. URL encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#existed_at DataCloudflareZeroTrustTunnelCloudflared#existed_at}
        :param include_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#include_prefix DataCloudflareZeroTrustTunnelCloudflared#include_prefix}.
        :param is_deleted: If ``true``, only include deleted tunnels. If ``false``, exclude deleted tunnels. If empty, all tunnels will be included. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#is_deleted DataCloudflareZeroTrustTunnelCloudflared#is_deleted}
        :param name: A user-friendly name for a tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#name DataCloudflareZeroTrustTunnelCloudflared#name}
        :param status: The status of the tunnel. Valid values are ``inactive`` (tunnel has never been run), ``degraded`` (tunnel is active and able to serve traffic but in an unhealthy state), ``healthy`` (tunnel is active and able to serve traffic), or ``down`` (tunnel can not serve traffic as it has no connections to the Cloudflare Edge). Available values: "inactive", "degraded", "healthy", "down". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#status DataCloudflareZeroTrustTunnelCloudflared#status}
        :param uuid: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#uuid DataCloudflareZeroTrustTunnelCloudflared#uuid}
        :param was_active_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#was_active_at DataCloudflareZeroTrustTunnelCloudflared#was_active_at}.
        :param was_inactive_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#was_inactive_at DataCloudflareZeroTrustTunnelCloudflared#was_inactive_at}.
        '''
        value = DataCloudflareZeroTrustTunnelCloudflaredFilter(
            exclude_prefix=exclude_prefix,
            existed_at=existed_at,
            include_prefix=include_prefix,
            is_deleted=is_deleted,
            name=name,
            status=status,
            uuid=uuid,
            was_active_at=was_active_at,
            was_inactive_at=was_inactive_at,
        )

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetTunnelId")
    def reset_tunnel_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTunnelId", []))

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
    @jsii.member(jsii_name="accountTag")
    def account_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountTag"))

    @builtins.property
    @jsii.member(jsii_name="configSrc")
    def config_src(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configSrc"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "DataCloudflareZeroTrustTunnelCloudflaredConnectionsList":
        return typing.cast("DataCloudflareZeroTrustTunnelCloudflaredConnectionsList", jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="connsActiveAt")
    def conns_active_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connsActiveAt"))

    @builtins.property
    @jsii.member(jsii_name="connsInactiveAt")
    def conns_inactive_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connsInactiveAt"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataCloudflareZeroTrustTunnelCloudflaredFilterOutputReference":
        return typing.cast("DataCloudflareZeroTrustTunnelCloudflaredFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="remoteConfig")
    def remote_config(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "remoteConfig"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="tunType")
    def tun_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tunType"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareZeroTrustTunnelCloudflaredFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareZeroTrustTunnelCloudflaredFilter"]], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="tunnelIdInput")
    def tunnel_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tunnelIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b66b2f8e00f8ee849139ec6125054752d3ca7aed002fe45c55253e7d6d26ebc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tunnelId")
    def tunnel_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tunnelId"))

    @tunnel_id.setter
    def tunnel_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f225172d43c383b424246f373ca2c2e412e3c19bae8ed31dab4b720d18643fdb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tunnelId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflared.DataCloudflareZeroTrustTunnelCloudflaredConfig",
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
        "filter": "filter",
        "tunnel_id": "tunnelId",
    },
)
class DataCloudflareZeroTrustTunnelCloudflaredConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        filter: typing.Optional[typing.Union["DataCloudflareZeroTrustTunnelCloudflaredFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        tunnel_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Cloudflare account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#account_id DataCloudflareZeroTrustTunnelCloudflared#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#filter DataCloudflareZeroTrustTunnelCloudflared#filter}.
        :param tunnel_id: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#tunnel_id DataCloudflareZeroTrustTunnelCloudflared#tunnel_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = DataCloudflareZeroTrustTunnelCloudflaredFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27773c43c366bd4fbca6fc1294bfad383c08514484180cc6e33917047c99b1e8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument tunnel_id", value=tunnel_id, expected_type=type_hints["tunnel_id"])
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
        if filter is not None:
            self._values["filter"] = filter
        if tunnel_id is not None:
            self._values["tunnel_id"] = tunnel_id

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
        '''Cloudflare account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#account_id DataCloudflareZeroTrustTunnelCloudflared#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(
        self,
    ) -> typing.Optional["DataCloudflareZeroTrustTunnelCloudflaredFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#filter DataCloudflareZeroTrustTunnelCloudflared#filter}.'''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["DataCloudflareZeroTrustTunnelCloudflaredFilter"], result)

    @builtins.property
    def tunnel_id(self) -> typing.Optional[builtins.str]:
        '''UUID of the tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#tunnel_id DataCloudflareZeroTrustTunnelCloudflared#tunnel_id}
        '''
        result = self._values.get("tunnel_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustTunnelCloudflaredConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflared.DataCloudflareZeroTrustTunnelCloudflaredConnections",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustTunnelCloudflaredConnections:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustTunnelCloudflaredConnections(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustTunnelCloudflaredConnectionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflared.DataCloudflareZeroTrustTunnelCloudflaredConnectionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__077aef556faa39cfa80aa63b36025dd92ea902d206ab6db897f8ba49b2a840ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustTunnelCloudflaredConnectionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68b1352c36cef06d1d254136101ee796cda273ab8d5934d0c000fbfe570a99db)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustTunnelCloudflaredConnectionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3f46abcba93bf8944f469e8462cb912d87ef783f3df784d8346955321203a0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f90601d281f7d1935872b647ff82b8059c697098ddcafc66a539f94b6370535)
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
            type_hints = typing.get_type_hints(_typecheckingstub__904ef0a3946ea023eb02898b82cac5a83a8e550296f45f0f438d1baadd2ce746)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustTunnelCloudflaredConnectionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflared.DataCloudflareZeroTrustTunnelCloudflaredConnectionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc17ef1dae15c916f57f32c9fad9c1bc137addc820daaddebea3bf5a508bcb29)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @builtins.property
    @jsii.member(jsii_name="clientVersion")
    def client_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientVersion"))

    @builtins.property
    @jsii.member(jsii_name="coloName")
    def colo_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "coloName"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="isPendingReconnect")
    def is_pending_reconnect(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "isPendingReconnect"))

    @builtins.property
    @jsii.member(jsii_name="openedAt")
    def opened_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openedAt"))

    @builtins.property
    @jsii.member(jsii_name="originIp")
    def origin_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originIp"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustTunnelCloudflaredConnections]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustTunnelCloudflaredConnections], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustTunnelCloudflaredConnections],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__744134980a9ca4984c88da8015fe167ed14cb000a17dab38e3ec736822e89241)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflared.DataCloudflareZeroTrustTunnelCloudflaredFilter",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_prefix": "excludePrefix",
        "existed_at": "existedAt",
        "include_prefix": "includePrefix",
        "is_deleted": "isDeleted",
        "name": "name",
        "status": "status",
        "uuid": "uuid",
        "was_active_at": "wasActiveAt",
        "was_inactive_at": "wasInactiveAt",
    },
)
class DataCloudflareZeroTrustTunnelCloudflaredFilter:
    def __init__(
        self,
        *,
        exclude_prefix: typing.Optional[builtins.str] = None,
        existed_at: typing.Optional[builtins.str] = None,
        include_prefix: typing.Optional[builtins.str] = None,
        is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
        was_active_at: typing.Optional[builtins.str] = None,
        was_inactive_at: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param exclude_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#exclude_prefix DataCloudflareZeroTrustTunnelCloudflared#exclude_prefix}.
        :param existed_at: If provided, include only resources that were created (and not deleted) before this time. URL encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#existed_at DataCloudflareZeroTrustTunnelCloudflared#existed_at}
        :param include_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#include_prefix DataCloudflareZeroTrustTunnelCloudflared#include_prefix}.
        :param is_deleted: If ``true``, only include deleted tunnels. If ``false``, exclude deleted tunnels. If empty, all tunnels will be included. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#is_deleted DataCloudflareZeroTrustTunnelCloudflared#is_deleted}
        :param name: A user-friendly name for a tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#name DataCloudflareZeroTrustTunnelCloudflared#name}
        :param status: The status of the tunnel. Valid values are ``inactive`` (tunnel has never been run), ``degraded`` (tunnel is active and able to serve traffic but in an unhealthy state), ``healthy`` (tunnel is active and able to serve traffic), or ``down`` (tunnel can not serve traffic as it has no connections to the Cloudflare Edge). Available values: "inactive", "degraded", "healthy", "down". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#status DataCloudflareZeroTrustTunnelCloudflared#status}
        :param uuid: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#uuid DataCloudflareZeroTrustTunnelCloudflared#uuid}
        :param was_active_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#was_active_at DataCloudflareZeroTrustTunnelCloudflared#was_active_at}.
        :param was_inactive_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#was_inactive_at DataCloudflareZeroTrustTunnelCloudflared#was_inactive_at}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69468c4c6ba646e210d4e5f28d06cfcb6e91f7c88fd9aa126a41ba4bbc0cd301)
            check_type(argname="argument exclude_prefix", value=exclude_prefix, expected_type=type_hints["exclude_prefix"])
            check_type(argname="argument existed_at", value=existed_at, expected_type=type_hints["existed_at"])
            check_type(argname="argument include_prefix", value=include_prefix, expected_type=type_hints["include_prefix"])
            check_type(argname="argument is_deleted", value=is_deleted, expected_type=type_hints["is_deleted"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
            check_type(argname="argument was_active_at", value=was_active_at, expected_type=type_hints["was_active_at"])
            check_type(argname="argument was_inactive_at", value=was_inactive_at, expected_type=type_hints["was_inactive_at"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude_prefix is not None:
            self._values["exclude_prefix"] = exclude_prefix
        if existed_at is not None:
            self._values["existed_at"] = existed_at
        if include_prefix is not None:
            self._values["include_prefix"] = include_prefix
        if is_deleted is not None:
            self._values["is_deleted"] = is_deleted
        if name is not None:
            self._values["name"] = name
        if status is not None:
            self._values["status"] = status
        if uuid is not None:
            self._values["uuid"] = uuid
        if was_active_at is not None:
            self._values["was_active_at"] = was_active_at
        if was_inactive_at is not None:
            self._values["was_inactive_at"] = was_inactive_at

    @builtins.property
    def exclude_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#exclude_prefix DataCloudflareZeroTrustTunnelCloudflared#exclude_prefix}.'''
        result = self._values.get("exclude_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existed_at(self) -> typing.Optional[builtins.str]:
        '''If provided, include only resources that were created (and not deleted) before this time. URL encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#existed_at DataCloudflareZeroTrustTunnelCloudflared#existed_at}
        '''
        result = self._values.get("existed_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#include_prefix DataCloudflareZeroTrustTunnelCloudflared#include_prefix}.'''
        result = self._values.get("include_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_deleted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If ``true``, only include deleted tunnels. If ``false``, exclude deleted tunnels. If empty, all tunnels will be included.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#is_deleted DataCloudflareZeroTrustTunnelCloudflared#is_deleted}
        '''
        result = self._values.get("is_deleted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''A user-friendly name for a tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#name DataCloudflareZeroTrustTunnelCloudflared#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''The status of the tunnel.

        Valid values are ``inactive`` (tunnel has never been run), ``degraded`` (tunnel is active and able to serve traffic but in an unhealthy state), ``healthy`` (tunnel is active and able to serve traffic), or ``down`` (tunnel can not serve traffic as it has no connections to the Cloudflare Edge).
        Available values: "inactive", "degraded", "healthy", "down".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#status DataCloudflareZeroTrustTunnelCloudflared#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID of the tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#uuid DataCloudflareZeroTrustTunnelCloudflared#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def was_active_at(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#was_active_at DataCloudflareZeroTrustTunnelCloudflared#was_active_at}.'''
        result = self._values.get("was_active_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def was_inactive_at(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared#was_inactive_at DataCloudflareZeroTrustTunnelCloudflared#was_inactive_at}.'''
        result = self._values.get("was_inactive_at")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustTunnelCloudflaredFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustTunnelCloudflaredFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflared.DataCloudflareZeroTrustTunnelCloudflaredFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2fe6452d5be223746482ef8f8e8ed27ea1ba5d8790aea1a81bb8aced599a1dc3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExcludePrefix")
    def reset_exclude_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludePrefix", []))

    @jsii.member(jsii_name="resetExistedAt")
    def reset_existed_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExistedAt", []))

    @jsii.member(jsii_name="resetIncludePrefix")
    def reset_include_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludePrefix", []))

    @jsii.member(jsii_name="resetIsDeleted")
    def reset_is_deleted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsDeleted", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @jsii.member(jsii_name="resetWasActiveAt")
    def reset_was_active_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWasActiveAt", []))

    @jsii.member(jsii_name="resetWasInactiveAt")
    def reset_was_inactive_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWasInactiveAt", []))

    @builtins.property
    @jsii.member(jsii_name="excludePrefixInput")
    def exclude_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "excludePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="existedAtInput")
    def existed_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "existedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="includePrefixInput")
    def include_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "includePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="isDeletedInput")
    def is_deleted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isDeletedInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="wasActiveAtInput")
    def was_active_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wasActiveAtInput"))

    @builtins.property
    @jsii.member(jsii_name="wasInactiveAtInput")
    def was_inactive_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wasInactiveAtInput"))

    @builtins.property
    @jsii.member(jsii_name="excludePrefix")
    def exclude_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "excludePrefix"))

    @exclude_prefix.setter
    def exclude_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffd2b62a287ab68020fa322f88cae325ab33486220bba5b214c8b6ea9c1ea49a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="existedAt")
    def existed_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "existedAt"))

    @existed_at.setter
    def existed_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31abd04ca8f2db2cb3696af4e035d376ee6d49b13199b64597b8a47cd28f6af0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "existedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includePrefix")
    def include_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "includePrefix"))

    @include_prefix.setter
    def include_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f165f1eaf51b841d47c44c49b93a2c744780b8b25ab17bcb256ea69e5116d5b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isDeleted")
    def is_deleted(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isDeleted"))

    @is_deleted.setter
    def is_deleted(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5080851ea57e6d161c5bcbb7b16161322cd24c4c23144eaf5c1c0e56c0a585e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isDeleted", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cafd7162fb9802bd48e342019aada69ef40a0c74f7eae08d30a89912f606a129)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e0b8365ea1248848d32c6873d7d662380c231ce9477067d1bb0afeb161c290a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__786aa5dec1525331ed715f653de7c50d6d4318be5b2cdd89a0cb065767ff0e72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wasActiveAt")
    def was_active_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wasActiveAt"))

    @was_active_at.setter
    def was_active_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bf2dba57c7f5be67b70abf239f3e20527f791d3b68c2d3b373aa9cd24ddecea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wasActiveAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wasInactiveAt")
    def was_inactive_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wasInactiveAt"))

    @was_inactive_at.setter
    def was_inactive_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__805efcd85c8c6af3e41bcab6491026d09d289a4c45990642daa670d2cd23d064)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wasInactiveAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustTunnelCloudflaredFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustTunnelCloudflaredFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustTunnelCloudflaredFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9aa0b4191939c1187e5572c2d4718d6bd5f39efa3ea24a36e560eda56985bc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustTunnelCloudflared",
    "DataCloudflareZeroTrustTunnelCloudflaredConfig",
    "DataCloudflareZeroTrustTunnelCloudflaredConnections",
    "DataCloudflareZeroTrustTunnelCloudflaredConnectionsList",
    "DataCloudflareZeroTrustTunnelCloudflaredConnectionsOutputReference",
    "DataCloudflareZeroTrustTunnelCloudflaredFilter",
    "DataCloudflareZeroTrustTunnelCloudflaredFilterOutputReference",
]

publication.publish()

def _typecheckingstub__44156098edf305709654edebaea82efae448c037aafb7ffb7c0bfca805d7e6a9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareZeroTrustTunnelCloudflaredFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    tunnel_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a9b5834618e3077f66fa8e7597afbd5623474f43c6b7e49ee3ca07dac9d52b6a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b66b2f8e00f8ee849139ec6125054752d3ca7aed002fe45c55253e7d6d26ebc1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f225172d43c383b424246f373ca2c2e412e3c19bae8ed31dab4b720d18643fdb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27773c43c366bd4fbca6fc1294bfad383c08514484180cc6e33917047c99b1e8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareZeroTrustTunnelCloudflaredFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    tunnel_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__077aef556faa39cfa80aa63b36025dd92ea902d206ab6db897f8ba49b2a840ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68b1352c36cef06d1d254136101ee796cda273ab8d5934d0c000fbfe570a99db(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3f46abcba93bf8944f469e8462cb912d87ef783f3df784d8346955321203a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f90601d281f7d1935872b647ff82b8059c697098ddcafc66a539f94b6370535(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__904ef0a3946ea023eb02898b82cac5a83a8e550296f45f0f438d1baadd2ce746(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc17ef1dae15c916f57f32c9fad9c1bc137addc820daaddebea3bf5a508bcb29(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__744134980a9ca4984c88da8015fe167ed14cb000a17dab38e3ec736822e89241(
    value: typing.Optional[DataCloudflareZeroTrustTunnelCloudflaredConnections],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69468c4c6ba646e210d4e5f28d06cfcb6e91f7c88fd9aa126a41ba4bbc0cd301(
    *,
    exclude_prefix: typing.Optional[builtins.str] = None,
    existed_at: typing.Optional[builtins.str] = None,
    include_prefix: typing.Optional[builtins.str] = None,
    is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
    was_active_at: typing.Optional[builtins.str] = None,
    was_inactive_at: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fe6452d5be223746482ef8f8e8ed27ea1ba5d8790aea1a81bb8aced599a1dc3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffd2b62a287ab68020fa322f88cae325ab33486220bba5b214c8b6ea9c1ea49a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31abd04ca8f2db2cb3696af4e035d376ee6d49b13199b64597b8a47cd28f6af0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f165f1eaf51b841d47c44c49b93a2c744780b8b25ab17bcb256ea69e5116d5b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5080851ea57e6d161c5bcbb7b16161322cd24c4c23144eaf5c1c0e56c0a585e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cafd7162fb9802bd48e342019aada69ef40a0c74f7eae08d30a89912f606a129(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e0b8365ea1248848d32c6873d7d662380c231ce9477067d1bb0afeb161c290a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__786aa5dec1525331ed715f653de7c50d6d4318be5b2cdd89a0cb065767ff0e72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bf2dba57c7f5be67b70abf239f3e20527f791d3b68c2d3b373aa9cd24ddecea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__805efcd85c8c6af3e41bcab6491026d09d289a4c45990642daa670d2cd23d064(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9aa0b4191939c1187e5572c2d4718d6bd5f39efa3ea24a36e560eda56985bc1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustTunnelCloudflaredFilter]],
) -> None:
    """Type checking stubs"""
    pass
