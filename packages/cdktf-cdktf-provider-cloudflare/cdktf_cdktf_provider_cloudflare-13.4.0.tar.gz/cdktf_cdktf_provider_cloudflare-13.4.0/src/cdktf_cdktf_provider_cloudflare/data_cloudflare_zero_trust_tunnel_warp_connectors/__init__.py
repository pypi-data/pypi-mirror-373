r'''
# `data_cloudflare_zero_trust_tunnel_warp_connectors`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_tunnel_warp_connectors`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors).
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


class DataCloudflareZeroTrustTunnelWarpConnectors(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelWarpConnectors.DataCloudflareZeroTrustTunnelWarpConnectors",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors cloudflare_zero_trust_tunnel_warp_connectors}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        exclude_prefix: typing.Optional[builtins.str] = None,
        existed_at: typing.Optional[builtins.str] = None,
        include_prefix: typing.Optional[builtins.str] = None,
        is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_items: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
        was_active_at: typing.Optional[builtins.str] = None,
        was_inactive_at: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors cloudflare_zero_trust_tunnel_warp_connectors} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Cloudflare account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#account_id DataCloudflareZeroTrustTunnelWarpConnectors#account_id}
        :param exclude_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#exclude_prefix DataCloudflareZeroTrustTunnelWarpConnectors#exclude_prefix}.
        :param existed_at: If provided, include only resources that were created (and not deleted) before this time. URL encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#existed_at DataCloudflareZeroTrustTunnelWarpConnectors#existed_at}
        :param include_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#include_prefix DataCloudflareZeroTrustTunnelWarpConnectors#include_prefix}.
        :param is_deleted: If ``true``, only include deleted tunnels. If ``false``, exclude deleted tunnels. If empty, all tunnels will be included. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#is_deleted DataCloudflareZeroTrustTunnelWarpConnectors#is_deleted}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#max_items DataCloudflareZeroTrustTunnelWarpConnectors#max_items}
        :param name: A user-friendly name for the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#name DataCloudflareZeroTrustTunnelWarpConnectors#name}
        :param status: The status of the tunnel. Valid values are ``inactive`` (tunnel has never been run), ``degraded`` (tunnel is active and able to serve traffic but in an unhealthy state), ``healthy`` (tunnel is active and able to serve traffic), or ``down`` (tunnel can not serve traffic as it has no connections to the Cloudflare Edge). Available values: "inactive", "degraded", "healthy", "down". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#status DataCloudflareZeroTrustTunnelWarpConnectors#status}
        :param uuid: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#uuid DataCloudflareZeroTrustTunnelWarpConnectors#uuid}
        :param was_active_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#was_active_at DataCloudflareZeroTrustTunnelWarpConnectors#was_active_at}.
        :param was_inactive_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#was_inactive_at DataCloudflareZeroTrustTunnelWarpConnectors#was_inactive_at}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d00966db76081baff6fb057d3f23587f3c475b5b6fb43c52ecd941e3fd8373e6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustTunnelWarpConnectorsConfig(
            account_id=account_id,
            exclude_prefix=exclude_prefix,
            existed_at=existed_at,
            include_prefix=include_prefix,
            is_deleted=is_deleted,
            max_items=max_items,
            name=name,
            status=status,
            uuid=uuid,
            was_active_at=was_active_at,
            was_inactive_at=was_inactive_at,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustTunnelWarpConnectors resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustTunnelWarpConnectors to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustTunnelWarpConnectors that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustTunnelWarpConnectors to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fa2ba5f7c58e24061cbc5b20aa89d2233b3b9e2041a1cd6734218bad4c323e8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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

    @jsii.member(jsii_name="resetMaxItems")
    def reset_max_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxItems", []))

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
    @jsii.member(jsii_name="result")
    def result(self) -> "DataCloudflareZeroTrustTunnelWarpConnectorsResultList":
        return typing.cast("DataCloudflareZeroTrustTunnelWarpConnectorsResultList", jsii.get(self, "result"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

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
    @jsii.member(jsii_name="maxItemsInput")
    def max_items_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxItemsInput"))

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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1682d1eabdfbbf190a24514b9e5764ea646c89e61eb74def71abdc4a6538998e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludePrefix")
    def exclude_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "excludePrefix"))

    @exclude_prefix.setter
    def exclude_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1fbc521a0758dbc3f52af9bb9c48f77ab6e405641750f3b650cda03e0458db5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="existedAt")
    def existed_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "existedAt"))

    @existed_at.setter
    def existed_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27c427323cdfa9a9d6579b82741910c86e1eaf2b053a3439ab36d2e86258b445)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "existedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includePrefix")
    def include_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "includePrefix"))

    @include_prefix.setter
    def include_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17f20b469a78c95d4c31b684f335d95dddfca422a2ca5d5983385e32641ae6b4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6281343c2fc510b8d428f2d07ac3af42579f20dbe6c3b5fca66bdf5199c1d326)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isDeleted", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxItems")
    def max_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxItems"))

    @max_items.setter
    def max_items(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7aa6e8a11c3897c0e301cf173d416222d8a237fc89894163fb2511d78dbc272)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxItems", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0df3bcf680ec7cd7329d4c8e22563c16872d1783ff3666ad74c18cc34d1b7e46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d173f65af7578049a51388d2586d14c769368235b8342e7fa7d75af7a09a7c53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1f5ef37d193f5fc71cbf327c8566e3773622a97f5f0edad855ed63121ab7ee7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wasActiveAt")
    def was_active_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wasActiveAt"))

    @was_active_at.setter
    def was_active_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc510a673b061e4d1934ab3b00cc56cb797edd303494357543c4e14398116fc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wasActiveAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wasInactiveAt")
    def was_inactive_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wasInactiveAt"))

    @was_inactive_at.setter
    def was_inactive_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7633cd85eba4049f33f4fa69806e96e81370f9e5d7af1615eb8329cb6136966)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wasInactiveAt", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelWarpConnectors.DataCloudflareZeroTrustTunnelWarpConnectorsConfig",
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
        "exclude_prefix": "excludePrefix",
        "existed_at": "existedAt",
        "include_prefix": "includePrefix",
        "is_deleted": "isDeleted",
        "max_items": "maxItems",
        "name": "name",
        "status": "status",
        "uuid": "uuid",
        "was_active_at": "wasActiveAt",
        "was_inactive_at": "wasInactiveAt",
    },
)
class DataCloudflareZeroTrustTunnelWarpConnectorsConfig(
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
        exclude_prefix: typing.Optional[builtins.str] = None,
        existed_at: typing.Optional[builtins.str] = None,
        include_prefix: typing.Optional[builtins.str] = None,
        is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_items: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
        was_active_at: typing.Optional[builtins.str] = None,
        was_inactive_at: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Cloudflare account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#account_id DataCloudflareZeroTrustTunnelWarpConnectors#account_id}
        :param exclude_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#exclude_prefix DataCloudflareZeroTrustTunnelWarpConnectors#exclude_prefix}.
        :param existed_at: If provided, include only resources that were created (and not deleted) before this time. URL encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#existed_at DataCloudflareZeroTrustTunnelWarpConnectors#existed_at}
        :param include_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#include_prefix DataCloudflareZeroTrustTunnelWarpConnectors#include_prefix}.
        :param is_deleted: If ``true``, only include deleted tunnels. If ``false``, exclude deleted tunnels. If empty, all tunnels will be included. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#is_deleted DataCloudflareZeroTrustTunnelWarpConnectors#is_deleted}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#max_items DataCloudflareZeroTrustTunnelWarpConnectors#max_items}
        :param name: A user-friendly name for the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#name DataCloudflareZeroTrustTunnelWarpConnectors#name}
        :param status: The status of the tunnel. Valid values are ``inactive`` (tunnel has never been run), ``degraded`` (tunnel is active and able to serve traffic but in an unhealthy state), ``healthy`` (tunnel is active and able to serve traffic), or ``down`` (tunnel can not serve traffic as it has no connections to the Cloudflare Edge). Available values: "inactive", "degraded", "healthy", "down". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#status DataCloudflareZeroTrustTunnelWarpConnectors#status}
        :param uuid: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#uuid DataCloudflareZeroTrustTunnelWarpConnectors#uuid}
        :param was_active_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#was_active_at DataCloudflareZeroTrustTunnelWarpConnectors#was_active_at}.
        :param was_inactive_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#was_inactive_at DataCloudflareZeroTrustTunnelWarpConnectors#was_inactive_at}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6815bedb20b2f69bd963fa7ce266da24fd552d3dfe8f99b344450fc4501158f2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument exclude_prefix", value=exclude_prefix, expected_type=type_hints["exclude_prefix"])
            check_type(argname="argument existed_at", value=existed_at, expected_type=type_hints["existed_at"])
            check_type(argname="argument include_prefix", value=include_prefix, expected_type=type_hints["include_prefix"])
            check_type(argname="argument is_deleted", value=is_deleted, expected_type=type_hints["is_deleted"])
            check_type(argname="argument max_items", value=max_items, expected_type=type_hints["max_items"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
            check_type(argname="argument was_active_at", value=was_active_at, expected_type=type_hints["was_active_at"])
            check_type(argname="argument was_inactive_at", value=was_inactive_at, expected_type=type_hints["was_inactive_at"])
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
        if exclude_prefix is not None:
            self._values["exclude_prefix"] = exclude_prefix
        if existed_at is not None:
            self._values["existed_at"] = existed_at
        if include_prefix is not None:
            self._values["include_prefix"] = include_prefix
        if is_deleted is not None:
            self._values["is_deleted"] = is_deleted
        if max_items is not None:
            self._values["max_items"] = max_items
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#account_id DataCloudflareZeroTrustTunnelWarpConnectors#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def exclude_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#exclude_prefix DataCloudflareZeroTrustTunnelWarpConnectors#exclude_prefix}.'''
        result = self._values.get("exclude_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existed_at(self) -> typing.Optional[builtins.str]:
        '''If provided, include only resources that were created (and not deleted) before this time. URL encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#existed_at DataCloudflareZeroTrustTunnelWarpConnectors#existed_at}
        '''
        result = self._values.get("existed_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#include_prefix DataCloudflareZeroTrustTunnelWarpConnectors#include_prefix}.'''
        result = self._values.get("include_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_deleted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If ``true``, only include deleted tunnels. If ``false``, exclude deleted tunnels. If empty, all tunnels will be included.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#is_deleted DataCloudflareZeroTrustTunnelWarpConnectors#is_deleted}
        '''
        result = self._values.get("is_deleted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_items(self) -> typing.Optional[jsii.Number]:
        '''Max items to fetch, default: 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#max_items DataCloudflareZeroTrustTunnelWarpConnectors#max_items}
        '''
        result = self._values.get("max_items")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''A user-friendly name for the tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#name DataCloudflareZeroTrustTunnelWarpConnectors#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''The status of the tunnel.

        Valid values are ``inactive`` (tunnel has never been run), ``degraded`` (tunnel is active and able to serve traffic but in an unhealthy state), ``healthy`` (tunnel is active and able to serve traffic), or ``down`` (tunnel can not serve traffic as it has no connections to the Cloudflare Edge).
        Available values: "inactive", "degraded", "healthy", "down".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#status DataCloudflareZeroTrustTunnelWarpConnectors#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID of the tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#uuid DataCloudflareZeroTrustTunnelWarpConnectors#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def was_active_at(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#was_active_at DataCloudflareZeroTrustTunnelWarpConnectors#was_active_at}.'''
        result = self._values.get("was_active_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def was_inactive_at(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_tunnel_warp_connectors#was_inactive_at DataCloudflareZeroTrustTunnelWarpConnectors#was_inactive_at}.'''
        result = self._values.get("was_inactive_at")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustTunnelWarpConnectorsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelWarpConnectors.DataCloudflareZeroTrustTunnelWarpConnectorsResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustTunnelWarpConnectorsResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustTunnelWarpConnectorsResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelWarpConnectors.DataCloudflareZeroTrustTunnelWarpConnectorsResultConnections",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustTunnelWarpConnectorsResultConnections:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustTunnelWarpConnectorsResultConnections(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelWarpConnectors.DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__17aa871f8ca8289f55e4ffe3f8748bf5c17f3bd573f8127c529ef936d04d3a5c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0e3b6b5538120cff8b8ec3a08a2990488417250f81dbe019240106961e32515)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a264b3e60d691f0362fea58580928ad7a96aadab30060816fbb7a4dabcdb1131)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd0c60d1e2cff13bb0d1eaf8d6fb8327c8cc454c089fd155840220bdca98e2a7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__36fc095a649b59550599e1f2c0a78c1f6bf44cf937f10856bcbd33b2b8a8bdeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelWarpConnectors.DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__467cdfcb87e8891c33cb1acdea3a2c2628ffb517b15007225b47f4e25c057bd9)
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
    ) -> typing.Optional[DataCloudflareZeroTrustTunnelWarpConnectorsResultConnections]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustTunnelWarpConnectorsResultConnections], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustTunnelWarpConnectorsResultConnections],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e8b010c9fcbbaedb8949b86170537dc714937cf52b8d8417bc21de026468334)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustTunnelWarpConnectorsResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelWarpConnectors.DataCloudflareZeroTrustTunnelWarpConnectorsResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67f9868064a23770f9f622e70dd9a7683cf02fb50749af09baacf672d1d5438b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustTunnelWarpConnectorsResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8226a9e00abaf08d66f19318e4540e14462252c4684325fe13ec77f77672ec4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustTunnelWarpConnectorsResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f2db5915b0727f8261db6200b9f3ab9f65309e26ebfd69832c6b2ed9bb156ac)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2c7016b4c5ef98ae780ceab3d160d499a24a657cb2ade78b76e2d77ba062f021)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b60a5d05568c9444d8149a5e436b30a1f13045bc3ea90ee1d3d2a621304471b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustTunnelWarpConnectorsResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustTunnelWarpConnectors.DataCloudflareZeroTrustTunnelWarpConnectorsResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__23626d5e6c35b8d1f786afa40b32d14002a7731e9e373b01aa0b4df02aabe70e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
    def connections(
        self,
    ) -> DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsList:
        return typing.cast(DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsList, jsii.get(self, "connections"))

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustTunnelWarpConnectorsResult]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustTunnelWarpConnectorsResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustTunnelWarpConnectorsResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__028ec3da6ec336825457123fcff0857576e6c09088f8ef36e133fdc28385c9f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustTunnelWarpConnectors",
    "DataCloudflareZeroTrustTunnelWarpConnectorsConfig",
    "DataCloudflareZeroTrustTunnelWarpConnectorsResult",
    "DataCloudflareZeroTrustTunnelWarpConnectorsResultConnections",
    "DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsList",
    "DataCloudflareZeroTrustTunnelWarpConnectorsResultConnectionsOutputReference",
    "DataCloudflareZeroTrustTunnelWarpConnectorsResultList",
    "DataCloudflareZeroTrustTunnelWarpConnectorsResultOutputReference",
]

publication.publish()

def _typecheckingstub__d00966db76081baff6fb057d3f23587f3c475b5b6fb43c52ecd941e3fd8373e6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    exclude_prefix: typing.Optional[builtins.str] = None,
    existed_at: typing.Optional[builtins.str] = None,
    include_prefix: typing.Optional[builtins.str] = None,
    is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_items: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
    was_active_at: typing.Optional[builtins.str] = None,
    was_inactive_at: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__7fa2ba5f7c58e24061cbc5b20aa89d2233b3b9e2041a1cd6734218bad4c323e8(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1682d1eabdfbbf190a24514b9e5764ea646c89e61eb74def71abdc4a6538998e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1fbc521a0758dbc3f52af9bb9c48f77ab6e405641750f3b650cda03e0458db5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27c427323cdfa9a9d6579b82741910c86e1eaf2b053a3439ab36d2e86258b445(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17f20b469a78c95d4c31b684f335d95dddfca422a2ca5d5983385e32641ae6b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6281343c2fc510b8d428f2d07ac3af42579f20dbe6c3b5fca66bdf5199c1d326(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7aa6e8a11c3897c0e301cf173d416222d8a237fc89894163fb2511d78dbc272(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0df3bcf680ec7cd7329d4c8e22563c16872d1783ff3666ad74c18cc34d1b7e46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d173f65af7578049a51388d2586d14c769368235b8342e7fa7d75af7a09a7c53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1f5ef37d193f5fc71cbf327c8566e3773622a97f5f0edad855ed63121ab7ee7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc510a673b061e4d1934ab3b00cc56cb797edd303494357543c4e14398116fc6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7633cd85eba4049f33f4fa69806e96e81370f9e5d7af1615eb8329cb6136966(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6815bedb20b2f69bd963fa7ce266da24fd552d3dfe8f99b344450fc4501158f2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    exclude_prefix: typing.Optional[builtins.str] = None,
    existed_at: typing.Optional[builtins.str] = None,
    include_prefix: typing.Optional[builtins.str] = None,
    is_deleted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_items: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
    was_active_at: typing.Optional[builtins.str] = None,
    was_inactive_at: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17aa871f8ca8289f55e4ffe3f8748bf5c17f3bd573f8127c529ef936d04d3a5c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0e3b6b5538120cff8b8ec3a08a2990488417250f81dbe019240106961e32515(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a264b3e60d691f0362fea58580928ad7a96aadab30060816fbb7a4dabcdb1131(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd0c60d1e2cff13bb0d1eaf8d6fb8327c8cc454c089fd155840220bdca98e2a7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36fc095a649b59550599e1f2c0a78c1f6bf44cf937f10856bcbd33b2b8a8bdeb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__467cdfcb87e8891c33cb1acdea3a2c2628ffb517b15007225b47f4e25c057bd9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e8b010c9fcbbaedb8949b86170537dc714937cf52b8d8417bc21de026468334(
    value: typing.Optional[DataCloudflareZeroTrustTunnelWarpConnectorsResultConnections],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67f9868064a23770f9f622e70dd9a7683cf02fb50749af09baacf672d1d5438b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8226a9e00abaf08d66f19318e4540e14462252c4684325fe13ec77f77672ec4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f2db5915b0727f8261db6200b9f3ab9f65309e26ebfd69832c6b2ed9bb156ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c7016b4c5ef98ae780ceab3d160d499a24a657cb2ade78b76e2d77ba062f021(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b60a5d05568c9444d8149a5e436b30a1f13045bc3ea90ee1d3d2a621304471b3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23626d5e6c35b8d1f786afa40b32d14002a7731e9e373b01aa0b4df02aabe70e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__028ec3da6ec336825457123fcff0857576e6c09088f8ef36e133fdc28385c9f9(
    value: typing.Optional[DataCloudflareZeroTrustTunnelWarpConnectorsResult],
) -> None:
    """Type checking stubs"""
    pass
