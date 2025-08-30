r'''
# `data_cloudflare_zero_trust_tunnel_cloudflared_route`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_tunnel_cloudflared_route`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route).
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


class DataCloudflareZeroTrustTunnelCloudflaredRoute(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflaredRoute.DataCloudflareZeroTrustTunnelCloudflaredRoute",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route cloudflare_zero_trust_tunnel_cloudflared_route}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        filter: typing.Optional[typing.Union["DataCloudflareZeroTrustTunnelCloudflaredRouteFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        route_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route cloudflare_zero_trust_tunnel_cloudflared_route} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Cloudflare account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#account_id DataCloudflareZeroTrustTunnelCloudflaredRoute#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#filter DataCloudflareZeroTrustTunnelCloudflaredRoute#filter}.
        :param route_id: UUID of the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#route_id DataCloudflareZeroTrustTunnelCloudflaredRoute#route_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__464387c991bdb712cb2bbd5fcfe73af8bac5e3e2b5959803dd2a8b1f60d0df8c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustTunnelCloudflaredRouteConfig(
            account_id=account_id,
            filter=filter,
            route_id=route_id,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustTunnelCloudflaredRoute resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustTunnelCloudflaredRoute to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustTunnelCloudflaredRoute that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustTunnelCloudflaredRoute to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61556b35ae25dd2a05d8b82d8316915068868c6820ccda4bd136e39d2ab4efc1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        existed_at: typing.Optional[builtins.str] = None,
        is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_subset: typing.Optional[builtins.str] = None,
        network_superset: typing.Optional[builtins.str] = None,
        route_id: typing.Optional[builtins.str] = None,
        tunnel_id: typing.Optional[builtins.str] = None,
        tun_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        virtual_network_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param comment: Optional remark describing the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#comment DataCloudflareZeroTrustTunnelCloudflaredRoute#comment}
        :param existed_at: If provided, include only resources that were created (and not deleted) before this time. URL encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#existed_at DataCloudflareZeroTrustTunnelCloudflaredRoute#existed_at}
        :param is_deleted: If ``true``, only include deleted routes. If ``false``, exclude deleted routes. If empty, all routes will be included. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#is_deleted DataCloudflareZeroTrustTunnelCloudflaredRoute#is_deleted}
        :param network_subset: If set, only list routes that are contained within this IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#network_subset DataCloudflareZeroTrustTunnelCloudflaredRoute#network_subset}
        :param network_superset: If set, only list routes that contain this IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#network_superset DataCloudflareZeroTrustTunnelCloudflaredRoute#network_superset}
        :param route_id: UUID of the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#route_id DataCloudflareZeroTrustTunnelCloudflaredRoute#route_id}
        :param tunnel_id: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#tunnel_id DataCloudflareZeroTrustTunnelCloudflaredRoute#tunnel_id}
        :param tun_types: The types of tunnels to filter by, separated by commas. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#tun_types DataCloudflareZeroTrustTunnelCloudflaredRoute#tun_types}
        :param virtual_network_id: UUID of the virtual network. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#virtual_network_id DataCloudflareZeroTrustTunnelCloudflaredRoute#virtual_network_id}
        '''
        value = DataCloudflareZeroTrustTunnelCloudflaredRouteFilter(
            comment=comment,
            existed_at=existed_at,
            is_deleted=is_deleted,
            network_subset=network_subset,
            network_superset=network_superset,
            route_id=route_id,
            tunnel_id=tunnel_id,
            tun_types=tun_types,
            virtual_network_id=virtual_network_id,
        )

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetRouteId")
    def reset_route_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteId", []))

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
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

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
    def filter(
        self,
    ) -> "DataCloudflareZeroTrustTunnelCloudflaredRouteFilterOutputReference":
        return typing.cast("DataCloudflareZeroTrustTunnelCloudflaredRouteFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @builtins.property
    @jsii.member(jsii_name="tunnelId")
    def tunnel_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tunnelId"))

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkId")
    def virtual_network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualNetworkId"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareZeroTrustTunnelCloudflaredRouteFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareZeroTrustTunnelCloudflaredRouteFilter"]], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="routeIdInput")
    def route_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a5fe1f2e8af28b245d4cf445098c7c7ae719963577e6f94b5338c2efb767044)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeId")
    def route_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeId"))

    @route_id.setter
    def route_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40b466cdd6e3db86bc5dfaadda21a255bb6e60e474abfc5f0cf1fb45822549f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflaredRoute.DataCloudflareZeroTrustTunnelCloudflaredRouteConfig",
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
        "route_id": "routeId",
    },
)
class DataCloudflareZeroTrustTunnelCloudflaredRouteConfig(
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
        filter: typing.Optional[typing.Union["DataCloudflareZeroTrustTunnelCloudflaredRouteFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        route_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Cloudflare account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#account_id DataCloudflareZeroTrustTunnelCloudflaredRoute#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#filter DataCloudflareZeroTrustTunnelCloudflaredRoute#filter}.
        :param route_id: UUID of the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#route_id DataCloudflareZeroTrustTunnelCloudflaredRoute#route_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = DataCloudflareZeroTrustTunnelCloudflaredRouteFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__826415b4b6e7a305c0dce92a8d6942e66bfa8d59db4df225c2bbc7c41ef93931)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument route_id", value=route_id, expected_type=type_hints["route_id"])
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
        if route_id is not None:
            self._values["route_id"] = route_id

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#account_id DataCloudflareZeroTrustTunnelCloudflaredRoute#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(
        self,
    ) -> typing.Optional["DataCloudflareZeroTrustTunnelCloudflaredRouteFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#filter DataCloudflareZeroTrustTunnelCloudflaredRoute#filter}.'''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["DataCloudflareZeroTrustTunnelCloudflaredRouteFilter"], result)

    @builtins.property
    def route_id(self) -> typing.Optional[builtins.str]:
        '''UUID of the route.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#route_id DataCloudflareZeroTrustTunnelCloudflaredRoute#route_id}
        '''
        result = self._values.get("route_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustTunnelCloudflaredRouteConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflaredRoute.DataCloudflareZeroTrustTunnelCloudflaredRouteFilter",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "existed_at": "existedAt",
        "is_deleted": "isDeleted",
        "network_subset": "networkSubset",
        "network_superset": "networkSuperset",
        "route_id": "routeId",
        "tunnel_id": "tunnelId",
        "tun_types": "tunTypes",
        "virtual_network_id": "virtualNetworkId",
    },
)
class DataCloudflareZeroTrustTunnelCloudflaredRouteFilter:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        existed_at: typing.Optional[builtins.str] = None,
        is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_subset: typing.Optional[builtins.str] = None,
        network_superset: typing.Optional[builtins.str] = None,
        route_id: typing.Optional[builtins.str] = None,
        tunnel_id: typing.Optional[builtins.str] = None,
        tun_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        virtual_network_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param comment: Optional remark describing the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#comment DataCloudflareZeroTrustTunnelCloudflaredRoute#comment}
        :param existed_at: If provided, include only resources that were created (and not deleted) before this time. URL encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#existed_at DataCloudflareZeroTrustTunnelCloudflaredRoute#existed_at}
        :param is_deleted: If ``true``, only include deleted routes. If ``false``, exclude deleted routes. If empty, all routes will be included. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#is_deleted DataCloudflareZeroTrustTunnelCloudflaredRoute#is_deleted}
        :param network_subset: If set, only list routes that are contained within this IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#network_subset DataCloudflareZeroTrustTunnelCloudflaredRoute#network_subset}
        :param network_superset: If set, only list routes that contain this IP range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#network_superset DataCloudflareZeroTrustTunnelCloudflaredRoute#network_superset}
        :param route_id: UUID of the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#route_id DataCloudflareZeroTrustTunnelCloudflaredRoute#route_id}
        :param tunnel_id: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#tunnel_id DataCloudflareZeroTrustTunnelCloudflaredRoute#tunnel_id}
        :param tun_types: The types of tunnels to filter by, separated by commas. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#tun_types DataCloudflareZeroTrustTunnelCloudflaredRoute#tun_types}
        :param virtual_network_id: UUID of the virtual network. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#virtual_network_id DataCloudflareZeroTrustTunnelCloudflaredRoute#virtual_network_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d464de651d325ee767cd40cc8b023434c4cae61fa8409df550768099a028c39f)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument existed_at", value=existed_at, expected_type=type_hints["existed_at"])
            check_type(argname="argument is_deleted", value=is_deleted, expected_type=type_hints["is_deleted"])
            check_type(argname="argument network_subset", value=network_subset, expected_type=type_hints["network_subset"])
            check_type(argname="argument network_superset", value=network_superset, expected_type=type_hints["network_superset"])
            check_type(argname="argument route_id", value=route_id, expected_type=type_hints["route_id"])
            check_type(argname="argument tunnel_id", value=tunnel_id, expected_type=type_hints["tunnel_id"])
            check_type(argname="argument tun_types", value=tun_types, expected_type=type_hints["tun_types"])
            check_type(argname="argument virtual_network_id", value=virtual_network_id, expected_type=type_hints["virtual_network_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if existed_at is not None:
            self._values["existed_at"] = existed_at
        if is_deleted is not None:
            self._values["is_deleted"] = is_deleted
        if network_subset is not None:
            self._values["network_subset"] = network_subset
        if network_superset is not None:
            self._values["network_superset"] = network_superset
        if route_id is not None:
            self._values["route_id"] = route_id
        if tunnel_id is not None:
            self._values["tunnel_id"] = tunnel_id
        if tun_types is not None:
            self._values["tun_types"] = tun_types
        if virtual_network_id is not None:
            self._values["virtual_network_id"] = virtual_network_id

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Optional remark describing the route.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#comment DataCloudflareZeroTrustTunnelCloudflaredRoute#comment}
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existed_at(self) -> typing.Optional[builtins.str]:
        '''If provided, include only resources that were created (and not deleted) before this time. URL encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#existed_at DataCloudflareZeroTrustTunnelCloudflaredRoute#existed_at}
        '''
        result = self._values.get("existed_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_deleted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If ``true``, only include deleted routes. If ``false``, exclude deleted routes. If empty, all routes will be included.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#is_deleted DataCloudflareZeroTrustTunnelCloudflaredRoute#is_deleted}
        '''
        result = self._values.get("is_deleted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def network_subset(self) -> typing.Optional[builtins.str]:
        '''If set, only list routes that are contained within this IP range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#network_subset DataCloudflareZeroTrustTunnelCloudflaredRoute#network_subset}
        '''
        result = self._values.get("network_subset")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_superset(self) -> typing.Optional[builtins.str]:
        '''If set, only list routes that contain this IP range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#network_superset DataCloudflareZeroTrustTunnelCloudflaredRoute#network_superset}
        '''
        result = self._values.get("network_superset")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_id(self) -> typing.Optional[builtins.str]:
        '''UUID of the route.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#route_id DataCloudflareZeroTrustTunnelCloudflaredRoute#route_id}
        '''
        result = self._values.get("route_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tunnel_id(self) -> typing.Optional[builtins.str]:
        '''UUID of the tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#tunnel_id DataCloudflareZeroTrustTunnelCloudflaredRoute#tunnel_id}
        '''
        result = self._values.get("tunnel_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tun_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The types of tunnels to filter by, separated by commas.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#tun_types DataCloudflareZeroTrustTunnelCloudflaredRoute#tun_types}
        '''
        result = self._values.get("tun_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def virtual_network_id(self) -> typing.Optional[builtins.str]:
        '''UUID of the virtual network.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_cloudflared_route#virtual_network_id DataCloudflareZeroTrustTunnelCloudflaredRoute#virtual_network_id}
        '''
        result = self._values.get("virtual_network_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustTunnelCloudflaredRouteFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustTunnelCloudflaredRouteFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelCloudflaredRoute.DataCloudflareZeroTrustTunnelCloudflaredRouteFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__42b5968c5d2463b20598edc20397c61593d2b7251f8761822337f93d51f58b16)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetExistedAt")
    def reset_existed_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExistedAt", []))

    @jsii.member(jsii_name="resetIsDeleted")
    def reset_is_deleted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsDeleted", []))

    @jsii.member(jsii_name="resetNetworkSubset")
    def reset_network_subset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkSubset", []))

    @jsii.member(jsii_name="resetNetworkSuperset")
    def reset_network_superset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkSuperset", []))

    @jsii.member(jsii_name="resetRouteId")
    def reset_route_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteId", []))

    @jsii.member(jsii_name="resetTunnelId")
    def reset_tunnel_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTunnelId", []))

    @jsii.member(jsii_name="resetTunTypes")
    def reset_tun_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTunTypes", []))

    @jsii.member(jsii_name="resetVirtualNetworkId")
    def reset_virtual_network_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualNetworkId", []))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="existedAtInput")
    def existed_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "existedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="isDeletedInput")
    def is_deleted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isDeletedInput"))

    @builtins.property
    @jsii.member(jsii_name="networkSubsetInput")
    def network_subset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkSubsetInput"))

    @builtins.property
    @jsii.member(jsii_name="networkSupersetInput")
    def network_superset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkSupersetInput"))

    @builtins.property
    @jsii.member(jsii_name="routeIdInput")
    def route_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tunnelIdInput")
    def tunnel_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tunnelIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tunTypesInput")
    def tun_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tunTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkIdInput")
    def virtual_network_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualNetworkIdInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a4e3d9bc7c71b66dd8b0a3bd2d166ac5b476cfb650aa60854365319449db6b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="existedAt")
    def existed_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "existedAt"))

    @existed_at.setter
    def existed_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd65d51fbab7b4117a43d6c79404d64dcfe0e285c38ef3ae0a3d9cb53cbf4a6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "existedAt", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__96595fd90373864fcebb8882302626d998fe8f5a060844c98a85fabdf4aeedf9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isDeleted", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkSubset")
    def network_subset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkSubset"))

    @network_subset.setter
    def network_subset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c930068330770181fa1da652a3ea51b39f42f518a132e58ea6a8bdcfe14ea3f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkSubset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkSuperset")
    def network_superset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkSuperset"))

    @network_superset.setter
    def network_superset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0fd47e98e8bf09126e2b2e431477e82246a62c10b5caf0e702120dd41de0243)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkSuperset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeId")
    def route_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeId"))

    @route_id.setter
    def route_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__628c376564dae550d7f6a680ab6d83b9db18722842fc26aaaa220d084713ff31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tunnelId")
    def tunnel_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tunnelId"))

    @tunnel_id.setter
    def tunnel_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6a2f4afea122205a4791a2accf0d8974eaac2f0b6c2b7396a85951de1198408)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tunnelId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tunTypes")
    def tun_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tunTypes"))

    @tun_types.setter
    def tun_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dad9537ccb2b422df676d4215aa2aa206f2ee3f3ce1e3227bea9f904c27fe875)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tunTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkId")
    def virtual_network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualNetworkId"))

    @virtual_network_id.setter
    def virtual_network_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f6c638a91a742118119ec237dadf86e8ad936ee0600ec04672382c42a561665)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualNetworkId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustTunnelCloudflaredRouteFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustTunnelCloudflaredRouteFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustTunnelCloudflaredRouteFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a37674b0d9b0da8c1e08be3ccc47bcf452d3c4fed851e612547180db3a4c7569)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustTunnelCloudflaredRoute",
    "DataCloudflareZeroTrustTunnelCloudflaredRouteConfig",
    "DataCloudflareZeroTrustTunnelCloudflaredRouteFilter",
    "DataCloudflareZeroTrustTunnelCloudflaredRouteFilterOutputReference",
]

publication.publish()

def _typecheckingstub__464387c991bdb712cb2bbd5fcfe73af8bac5e3e2b5959803dd2a8b1f60d0df8c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareZeroTrustTunnelCloudflaredRouteFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    route_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__61556b35ae25dd2a05d8b82d8316915068868c6820ccda4bd136e39d2ab4efc1(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a5fe1f2e8af28b245d4cf445098c7c7ae719963577e6f94b5338c2efb767044(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40b466cdd6e3db86bc5dfaadda21a255bb6e60e474abfc5f0cf1fb45822549f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__826415b4b6e7a305c0dce92a8d6942e66bfa8d59db4df225c2bbc7c41ef93931(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareZeroTrustTunnelCloudflaredRouteFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    route_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d464de651d325ee767cd40cc8b023434c4cae61fa8409df550768099a028c39f(
    *,
    comment: typing.Optional[builtins.str] = None,
    existed_at: typing.Optional[builtins.str] = None,
    is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    network_subset: typing.Optional[builtins.str] = None,
    network_superset: typing.Optional[builtins.str] = None,
    route_id: typing.Optional[builtins.str] = None,
    tunnel_id: typing.Optional[builtins.str] = None,
    tun_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    virtual_network_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42b5968c5d2463b20598edc20397c61593d2b7251f8761822337f93d51f58b16(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a4e3d9bc7c71b66dd8b0a3bd2d166ac5b476cfb650aa60854365319449db6b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd65d51fbab7b4117a43d6c79404d64dcfe0e285c38ef3ae0a3d9cb53cbf4a6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96595fd90373864fcebb8882302626d998fe8f5a060844c98a85fabdf4aeedf9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c930068330770181fa1da652a3ea51b39f42f518a132e58ea6a8bdcfe14ea3f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0fd47e98e8bf09126e2b2e431477e82246a62c10b5caf0e702120dd41de0243(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__628c376564dae550d7f6a680ab6d83b9db18722842fc26aaaa220d084713ff31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6a2f4afea122205a4791a2accf0d8974eaac2f0b6c2b7396a85951de1198408(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dad9537ccb2b422df676d4215aa2aa206f2ee3f3ce1e3227bea9f904c27fe875(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f6c638a91a742118119ec237dadf86e8ad936ee0600ec04672382c42a561665(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a37674b0d9b0da8c1e08be3ccc47bcf452d3c4fed851e612547180db3a4c7569(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustTunnelCloudflaredRouteFilter]],
) -> None:
    """Type checking stubs"""
    pass
