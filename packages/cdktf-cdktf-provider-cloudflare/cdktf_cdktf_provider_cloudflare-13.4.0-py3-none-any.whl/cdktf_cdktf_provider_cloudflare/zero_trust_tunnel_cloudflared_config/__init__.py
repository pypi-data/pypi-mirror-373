r'''
# `cloudflare_zero_trust_tunnel_cloudflared_config`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_tunnel_cloudflared_config`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config).
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


class ZeroTrustTunnelCloudflaredConfigA(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigA",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config cloudflare_zero_trust_tunnel_cloudflared_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        tunnel_id: builtins.str,
        config: typing.Optional[typing.Union["ZeroTrustTunnelCloudflaredConfigConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        source: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config cloudflare_zero_trust_tunnel_cloudflared_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#account_id ZeroTrustTunnelCloudflaredConfigA#account_id}
        :param tunnel_id: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tunnel_id ZeroTrustTunnelCloudflaredConfigA#tunnel_id}
        :param config: The tunnel configuration and ingress rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#config ZeroTrustTunnelCloudflaredConfigA#config}
        :param source: Indicates if this is a locally or remotely configured tunnel. If ``local``, manage the tunnel using a YAML file on the origin machine. If ``cloudflare``, manage the tunnel's configuration on the Zero Trust dashboard. Available values: "local", "cloudflare". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#source ZeroTrustTunnelCloudflaredConfigA#source}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40c3e700edd3e4bf5ead6f056e28348ae350d0c39ce57e46a2c6c9127b5877e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config_ = ZeroTrustTunnelCloudflaredConfigAConfig(
            account_id=account_id,
            tunnel_id=tunnel_id,
            config=config,
            source=source,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ZeroTrustTunnelCloudflaredConfigA resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustTunnelCloudflaredConfigA to import.
        :param import_from_id: The id of the existing ZeroTrustTunnelCloudflaredConfigA that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustTunnelCloudflaredConfigA to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26886a3195522bd58df26c7e41578c5a4b7c8ef2a01aabc8c8b2fc6d581237ad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        ingress: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustTunnelCloudflaredConfigConfigIngress", typing.Dict[builtins.str, typing.Any]]]]] = None,
        origin_request: typing.Optional[typing.Union["ZeroTrustTunnelCloudflaredConfigConfigOriginRequest", typing.Dict[builtins.str, typing.Any]]] = None,
        warp_routing: typing.Optional[typing.Union["ZeroTrustTunnelCloudflaredConfigConfigWarpRouting", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param ingress: List of public hostname definitions. At least one ingress rule needs to be defined for the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#ingress ZeroTrustTunnelCloudflaredConfigA#ingress}
        :param origin_request: Configuration parameters for the public hostname specific connection settings between cloudflared and origin server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_request ZeroTrustTunnelCloudflaredConfigA#origin_request}
        :param warp_routing: Enable private network access from WARP users to private network routes. This is enabled if the tunnel has an assigned route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#warp_routing ZeroTrustTunnelCloudflaredConfigA#warp_routing}
        '''
        value = ZeroTrustTunnelCloudflaredConfigConfig(
            ingress=ingress, origin_request=origin_request, warp_routing=warp_routing
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

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
    @jsii.member(jsii_name="config")
    def config(self) -> "ZeroTrustTunnelCloudflaredConfigConfigOutputReference":
        return typing.cast("ZeroTrustTunnelCloudflaredConfigConfigOutputReference", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustTunnelCloudflaredConfigConfig"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustTunnelCloudflaredConfigConfig"]], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__063215e6de559dfdb173577ef39a73e59c8da14db0dd681f9214f49fade47a4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dc0d1f5b6ed840e5a5131c48b61f9fb3e55a49a55c79a9b3758d7f03ed49b0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tunnelId")
    def tunnel_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tunnelId"))

    @tunnel_id.setter
    def tunnel_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c95fc4ac1123f5860744e72d1b82de65fe429be4b727ca3fef5e54ece11f1142)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tunnelId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigAConfig",
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
        "tunnel_id": "tunnelId",
        "config": "config",
        "source": "source",
    },
)
class ZeroTrustTunnelCloudflaredConfigAConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        tunnel_id: builtins.str,
        config: typing.Optional[typing.Union["ZeroTrustTunnelCloudflaredConfigConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        source: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#account_id ZeroTrustTunnelCloudflaredConfigA#account_id}
        :param tunnel_id: UUID of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tunnel_id ZeroTrustTunnelCloudflaredConfigA#tunnel_id}
        :param config: The tunnel configuration and ingress rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#config ZeroTrustTunnelCloudflaredConfigA#config}
        :param source: Indicates if this is a locally or remotely configured tunnel. If ``local``, manage the tunnel using a YAML file on the origin machine. If ``cloudflare``, manage the tunnel's configuration on the Zero Trust dashboard. Available values: "local", "cloudflare". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#source ZeroTrustTunnelCloudflaredConfigA#source}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(config, dict):
            config = ZeroTrustTunnelCloudflaredConfigConfig(**config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ae33dabb83c6599c16c97f82f27e96662097f36b213d22e119d6e7c7e366024)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument tunnel_id", value=tunnel_id, expected_type=type_hints["tunnel_id"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "tunnel_id": tunnel_id,
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
        if config is not None:
            self._values["config"] = config
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#account_id ZeroTrustTunnelCloudflaredConfigA#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tunnel_id(self) -> builtins.str:
        '''UUID of the tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tunnel_id ZeroTrustTunnelCloudflaredConfigA#tunnel_id}
        '''
        result = self._values.get("tunnel_id")
        assert result is not None, "Required property 'tunnel_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config(self) -> typing.Optional["ZeroTrustTunnelCloudflaredConfigConfig"]:
        '''The tunnel configuration and ingress rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#config ZeroTrustTunnelCloudflaredConfigA#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional["ZeroTrustTunnelCloudflaredConfigConfig"], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Indicates if this is a locally or remotely configured tunnel.

        If ``local``, manage the tunnel using a YAML file on the origin machine. If ``cloudflare``, manage the tunnel's configuration on the Zero Trust dashboard.
        Available values: "local", "cloudflare".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#source ZeroTrustTunnelCloudflaredConfigA#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustTunnelCloudflaredConfigAConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfig",
    jsii_struct_bases=[],
    name_mapping={
        "ingress": "ingress",
        "origin_request": "originRequest",
        "warp_routing": "warpRouting",
    },
)
class ZeroTrustTunnelCloudflaredConfigConfig:
    def __init__(
        self,
        *,
        ingress: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustTunnelCloudflaredConfigConfigIngress", typing.Dict[builtins.str, typing.Any]]]]] = None,
        origin_request: typing.Optional[typing.Union["ZeroTrustTunnelCloudflaredConfigConfigOriginRequest", typing.Dict[builtins.str, typing.Any]]] = None,
        warp_routing: typing.Optional[typing.Union["ZeroTrustTunnelCloudflaredConfigConfigWarpRouting", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param ingress: List of public hostname definitions. At least one ingress rule needs to be defined for the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#ingress ZeroTrustTunnelCloudflaredConfigA#ingress}
        :param origin_request: Configuration parameters for the public hostname specific connection settings between cloudflared and origin server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_request ZeroTrustTunnelCloudflaredConfigA#origin_request}
        :param warp_routing: Enable private network access from WARP users to private network routes. This is enabled if the tunnel has an assigned route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#warp_routing ZeroTrustTunnelCloudflaredConfigA#warp_routing}
        '''
        if isinstance(origin_request, dict):
            origin_request = ZeroTrustTunnelCloudflaredConfigConfigOriginRequest(**origin_request)
        if isinstance(warp_routing, dict):
            warp_routing = ZeroTrustTunnelCloudflaredConfigConfigWarpRouting(**warp_routing)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eecc74d84626090dba3f174efaac8078277aacbf27564f772b864127e59e4cd7)
            check_type(argname="argument ingress", value=ingress, expected_type=type_hints["ingress"])
            check_type(argname="argument origin_request", value=origin_request, expected_type=type_hints["origin_request"])
            check_type(argname="argument warp_routing", value=warp_routing, expected_type=type_hints["warp_routing"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ingress is not None:
            self._values["ingress"] = ingress
        if origin_request is not None:
            self._values["origin_request"] = origin_request
        if warp_routing is not None:
            self._values["warp_routing"] = warp_routing

    @builtins.property
    def ingress(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustTunnelCloudflaredConfigConfigIngress"]]]:
        '''List of public hostname definitions. At least one ingress rule needs to be defined for the tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#ingress ZeroTrustTunnelCloudflaredConfigA#ingress}
        '''
        result = self._values.get("ingress")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustTunnelCloudflaredConfigConfigIngress"]]], result)

    @builtins.property
    def origin_request(
        self,
    ) -> typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigOriginRequest"]:
        '''Configuration parameters for the public hostname specific connection settings between cloudflared and origin server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_request ZeroTrustTunnelCloudflaredConfigA#origin_request}
        '''
        result = self._values.get("origin_request")
        return typing.cast(typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigOriginRequest"], result)

    @builtins.property
    def warp_routing(
        self,
    ) -> typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigWarpRouting"]:
        '''Enable private network access from WARP users to private network routes.

        This is enabled if the tunnel has an assigned route.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#warp_routing ZeroTrustTunnelCloudflaredConfigA#warp_routing}
        '''
        result = self._values.get("warp_routing")
        return typing.cast(typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigWarpRouting"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustTunnelCloudflaredConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigIngress",
    jsii_struct_bases=[],
    name_mapping={
        "service": "service",
        "hostname": "hostname",
        "origin_request": "originRequest",
        "path": "path",
    },
)
class ZeroTrustTunnelCloudflaredConfigConfigIngress:
    def __init__(
        self,
        *,
        service: builtins.str,
        hostname: typing.Optional[builtins.str] = None,
        origin_request: typing.Optional[typing.Union["ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest", typing.Dict[builtins.str, typing.Any]]] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service: Protocol and address of destination server. Supported protocols: http://, https://, unix://, tcp://, ssh://, rdp://, unix+tls://, smb://. Alternatively can return a HTTP status code http_status:[code] e.g. 'http_status:404'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#service ZeroTrustTunnelCloudflaredConfigA#service}
        :param hostname: Public hostname for this service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#hostname ZeroTrustTunnelCloudflaredConfigA#hostname}
        :param origin_request: Configuration parameters for the public hostname specific connection settings between cloudflared and origin server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_request ZeroTrustTunnelCloudflaredConfigA#origin_request}
        :param path: Requests with this path route to this public hostname. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#path ZeroTrustTunnelCloudflaredConfigA#path}
        '''
        if isinstance(origin_request, dict):
            origin_request = ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest(**origin_request)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94ba2948fdcbf8bfb89e179350b70850003429b4a28d4d9de95052440032608e)
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument origin_request", value=origin_request, expected_type=type_hints["origin_request"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service": service,
        }
        if hostname is not None:
            self._values["hostname"] = hostname
        if origin_request is not None:
            self._values["origin_request"] = origin_request
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def service(self) -> builtins.str:
        '''Protocol and address of destination server.

        Supported protocols: http://, https://, unix://, tcp://, ssh://, rdp://, unix+tls://, smb://. Alternatively can return a HTTP status code http_status:[code] e.g. 'http_status:404'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#service ZeroTrustTunnelCloudflaredConfigA#service}
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''Public hostname for this service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#hostname ZeroTrustTunnelCloudflaredConfigA#hostname}
        '''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_request(
        self,
    ) -> typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest"]:
        '''Configuration parameters for the public hostname specific connection settings between cloudflared and origin server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_request ZeroTrustTunnelCloudflaredConfigA#origin_request}
        '''
        result = self._values.get("origin_request")
        return typing.cast(typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest"], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Requests with this path route to this public hostname.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#path ZeroTrustTunnelCloudflaredConfigA#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustTunnelCloudflaredConfigConfigIngress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustTunnelCloudflaredConfigConfigIngressList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigIngressList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__789a71d710609a2585f9eae2eb83bf6b57fa6c0db17c94e6645bfe90edf4252a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustTunnelCloudflaredConfigConfigIngressOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6f6b94c2e9063411ba3ea0e4468e5e8abf484678b2c45f36ecaadd7f93ae1c0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustTunnelCloudflaredConfigConfigIngressOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c85a4871a985d6434999b161b8f01f94e0703bffbc86e2ce98c5a2996bd25500)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8b601bf51439605cb245e9749259926229e1344e64a88b46bf47017131972e6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b980e930be65c7ba3be234f0c54b49c311baa49afbf8e2601b861a0c763ff26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustTunnelCloudflaredConfigConfigIngress]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustTunnelCloudflaredConfigConfigIngress]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustTunnelCloudflaredConfigConfigIngress]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30261ce8a6f9b865c46563e00808e3aaac0e262f3a28d7dca34c3563c79d5a99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest",
    jsii_struct_bases=[],
    name_mapping={
        "access": "access",
        "ca_pool": "caPool",
        "connect_timeout": "connectTimeout",
        "disable_chunked_encoding": "disableChunkedEncoding",
        "http2_origin": "http2Origin",
        "http_host_header": "httpHostHeader",
        "keep_alive_connections": "keepAliveConnections",
        "keep_alive_timeout": "keepAliveTimeout",
        "no_happy_eyeballs": "noHappyEyeballs",
        "no_tls_verify": "noTlsVerify",
        "origin_server_name": "originServerName",
        "proxy_type": "proxyType",
        "tcp_keep_alive": "tcpKeepAlive",
        "tls_timeout": "tlsTimeout",
    },
)
class ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest:
    def __init__(
        self,
        *,
        access: typing.Optional[typing.Union["ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess", typing.Dict[builtins.str, typing.Any]]] = None,
        ca_pool: typing.Optional[builtins.str] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        disable_chunked_encoding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http2_origin: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_host_header: typing.Optional[builtins.str] = None,
        keep_alive_connections: typing.Optional[jsii.Number] = None,
        keep_alive_timeout: typing.Optional[jsii.Number] = None,
        no_happy_eyeballs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        no_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        origin_server_name: typing.Optional[builtins.str] = None,
        proxy_type: typing.Optional[builtins.str] = None,
        tcp_keep_alive: typing.Optional[jsii.Number] = None,
        tls_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param access: For all L7 requests to this hostname, cloudflared will validate each request's Cf-Access-Jwt-Assertion request header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#access ZeroTrustTunnelCloudflaredConfigA#access}
        :param ca_pool: Path to the certificate authority (CA) for the certificate of your origin. This option should be used only if your certificate is not signed by Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#ca_pool ZeroTrustTunnelCloudflaredConfigA#ca_pool}
        :param connect_timeout: Timeout for establishing a new TCP connection to your origin server. This excludes the time taken to establish TLS, which is controlled by tlsTimeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#connect_timeout ZeroTrustTunnelCloudflaredConfigA#connect_timeout}
        :param disable_chunked_encoding: Disables chunked transfer encoding. Useful if you are running a WSGI server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#disable_chunked_encoding ZeroTrustTunnelCloudflaredConfigA#disable_chunked_encoding}
        :param http2_origin: Attempt to connect to origin using HTTP2. Origin must be configured as https. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http2_origin ZeroTrustTunnelCloudflaredConfigA#http2_origin}
        :param http_host_header: Sets the HTTP Host header on requests sent to the local service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http_host_header ZeroTrustTunnelCloudflaredConfigA#http_host_header}
        :param keep_alive_connections: Maximum number of idle keepalive connections between Tunnel and your origin. This does not restrict the total number of concurrent connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_connections ZeroTrustTunnelCloudflaredConfigA#keep_alive_connections}
        :param keep_alive_timeout: Timeout after which an idle keepalive connection can be discarded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_timeout ZeroTrustTunnelCloudflaredConfigA#keep_alive_timeout}
        :param no_happy_eyeballs: Disable the “happy eyeballs” algorithm for IPv4/IPv6 fallback if your local network has misconfigured one of the protocols. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_happy_eyeballs ZeroTrustTunnelCloudflaredConfigA#no_happy_eyeballs}
        :param no_tls_verify: Disables TLS verification of the certificate presented by your origin. Will allow any certificate from the origin to be accepted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_tls_verify ZeroTrustTunnelCloudflaredConfigA#no_tls_verify}
        :param origin_server_name: Hostname that cloudflared should expect from your origin server certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_server_name ZeroTrustTunnelCloudflaredConfigA#origin_server_name}
        :param proxy_type: cloudflared starts a proxy server to translate HTTP traffic into TCP when proxying, for example, SSH or RDP. This configures what type of proxy will be started. Valid options are: "" for the regular proxy and "socks" for a SOCKS5 proxy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#proxy_type ZeroTrustTunnelCloudflaredConfigA#proxy_type}
        :param tcp_keep_alive: The timeout after which a TCP keepalive packet is sent on a connection between Tunnel and the origin server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tcp_keep_alive ZeroTrustTunnelCloudflaredConfigA#tcp_keep_alive}
        :param tls_timeout: Timeout for completing a TLS handshake to your origin server, if you have chosen to connect Tunnel to an HTTPS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tls_timeout ZeroTrustTunnelCloudflaredConfigA#tls_timeout}
        '''
        if isinstance(access, dict):
            access = ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess(**access)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c8a4c0dc456e2782d032081ed94a68150911c3af9ffd247979d67021072352e)
            check_type(argname="argument access", value=access, expected_type=type_hints["access"])
            check_type(argname="argument ca_pool", value=ca_pool, expected_type=type_hints["ca_pool"])
            check_type(argname="argument connect_timeout", value=connect_timeout, expected_type=type_hints["connect_timeout"])
            check_type(argname="argument disable_chunked_encoding", value=disable_chunked_encoding, expected_type=type_hints["disable_chunked_encoding"])
            check_type(argname="argument http2_origin", value=http2_origin, expected_type=type_hints["http2_origin"])
            check_type(argname="argument http_host_header", value=http_host_header, expected_type=type_hints["http_host_header"])
            check_type(argname="argument keep_alive_connections", value=keep_alive_connections, expected_type=type_hints["keep_alive_connections"])
            check_type(argname="argument keep_alive_timeout", value=keep_alive_timeout, expected_type=type_hints["keep_alive_timeout"])
            check_type(argname="argument no_happy_eyeballs", value=no_happy_eyeballs, expected_type=type_hints["no_happy_eyeballs"])
            check_type(argname="argument no_tls_verify", value=no_tls_verify, expected_type=type_hints["no_tls_verify"])
            check_type(argname="argument origin_server_name", value=origin_server_name, expected_type=type_hints["origin_server_name"])
            check_type(argname="argument proxy_type", value=proxy_type, expected_type=type_hints["proxy_type"])
            check_type(argname="argument tcp_keep_alive", value=tcp_keep_alive, expected_type=type_hints["tcp_keep_alive"])
            check_type(argname="argument tls_timeout", value=tls_timeout, expected_type=type_hints["tls_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access is not None:
            self._values["access"] = access
        if ca_pool is not None:
            self._values["ca_pool"] = ca_pool
        if connect_timeout is not None:
            self._values["connect_timeout"] = connect_timeout
        if disable_chunked_encoding is not None:
            self._values["disable_chunked_encoding"] = disable_chunked_encoding
        if http2_origin is not None:
            self._values["http2_origin"] = http2_origin
        if http_host_header is not None:
            self._values["http_host_header"] = http_host_header
        if keep_alive_connections is not None:
            self._values["keep_alive_connections"] = keep_alive_connections
        if keep_alive_timeout is not None:
            self._values["keep_alive_timeout"] = keep_alive_timeout
        if no_happy_eyeballs is not None:
            self._values["no_happy_eyeballs"] = no_happy_eyeballs
        if no_tls_verify is not None:
            self._values["no_tls_verify"] = no_tls_verify
        if origin_server_name is not None:
            self._values["origin_server_name"] = origin_server_name
        if proxy_type is not None:
            self._values["proxy_type"] = proxy_type
        if tcp_keep_alive is not None:
            self._values["tcp_keep_alive"] = tcp_keep_alive
        if tls_timeout is not None:
            self._values["tls_timeout"] = tls_timeout

    @builtins.property
    def access(
        self,
    ) -> typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess"]:
        '''For all L7 requests to this hostname, cloudflared will validate each request's Cf-Access-Jwt-Assertion request header.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#access ZeroTrustTunnelCloudflaredConfigA#access}
        '''
        result = self._values.get("access")
        return typing.cast(typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess"], result)

    @builtins.property
    def ca_pool(self) -> typing.Optional[builtins.str]:
        '''Path to the certificate authority (CA) for the certificate of your origin.

        This option should be used only if your certificate is not signed by Cloudflare.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#ca_pool ZeroTrustTunnelCloudflaredConfigA#ca_pool}
        '''
        result = self._values.get("ca_pool")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connect_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout for establishing a new TCP connection to your origin server.

        This excludes the time taken to establish TLS, which is controlled by tlsTimeout.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#connect_timeout ZeroTrustTunnelCloudflaredConfigA#connect_timeout}
        '''
        result = self._values.get("connect_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disable_chunked_encoding(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disables chunked transfer encoding. Useful if you are running a WSGI server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#disable_chunked_encoding ZeroTrustTunnelCloudflaredConfigA#disable_chunked_encoding}
        '''
        result = self._values.get("disable_chunked_encoding")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def http2_origin(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Attempt to connect to origin using HTTP2. Origin must be configured as https.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http2_origin ZeroTrustTunnelCloudflaredConfigA#http2_origin}
        '''
        result = self._values.get("http2_origin")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def http_host_header(self) -> typing.Optional[builtins.str]:
        '''Sets the HTTP Host header on requests sent to the local service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http_host_header ZeroTrustTunnelCloudflaredConfigA#http_host_header}
        '''
        result = self._values.get("http_host_header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keep_alive_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle keepalive connections between Tunnel and your origin.

        This does not restrict the total number of concurrent connections.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_connections ZeroTrustTunnelCloudflaredConfigA#keep_alive_connections}
        '''
        result = self._values.get("keep_alive_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def keep_alive_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout after which an idle keepalive connection can be discarded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_timeout ZeroTrustTunnelCloudflaredConfigA#keep_alive_timeout}
        '''
        result = self._values.get("keep_alive_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def no_happy_eyeballs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable the “happy eyeballs” algorithm for IPv4/IPv6 fallback if your local network has misconfigured one of the protocols.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_happy_eyeballs ZeroTrustTunnelCloudflaredConfigA#no_happy_eyeballs}
        '''
        result = self._values.get("no_happy_eyeballs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def no_tls_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disables TLS verification of the certificate presented by your origin.

        Will allow any certificate from the origin to be accepted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_tls_verify ZeroTrustTunnelCloudflaredConfigA#no_tls_verify}
        '''
        result = self._values.get("no_tls_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def origin_server_name(self) -> typing.Optional[builtins.str]:
        '''Hostname that cloudflared should expect from your origin server certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_server_name ZeroTrustTunnelCloudflaredConfigA#origin_server_name}
        '''
        result = self._values.get("origin_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxy_type(self) -> typing.Optional[builtins.str]:
        '''cloudflared starts a proxy server to translate HTTP traffic into TCP when proxying, for example, SSH or RDP.

        This configures what type of proxy will be started. Valid options are: "" for the regular proxy and "socks" for a SOCKS5 proxy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#proxy_type ZeroTrustTunnelCloudflaredConfigA#proxy_type}
        '''
        result = self._values.get("proxy_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tcp_keep_alive(self) -> typing.Optional[jsii.Number]:
        '''The timeout after which a TCP keepalive packet is sent on a connection between Tunnel and the origin server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tcp_keep_alive ZeroTrustTunnelCloudflaredConfigA#tcp_keep_alive}
        '''
        result = self._values.get("tcp_keep_alive")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout for completing a TLS handshake to your origin server, if you have chosen to connect Tunnel to an HTTPS server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tls_timeout ZeroTrustTunnelCloudflaredConfigA#tls_timeout}
        '''
        result = self._values.get("tls_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess",
    jsii_struct_bases=[],
    name_mapping={
        "aud_tag": "audTag",
        "team_name": "teamName",
        "required": "required",
    },
)
class ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess:
    def __init__(
        self,
        *,
        aud_tag: typing.Sequence[builtins.str],
        team_name: builtins.str,
        required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param aud_tag: Access applications that are allowed to reach this hostname for this Tunnel. Audience tags can be identified in the dashboard or via the List Access policies API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#aud_tag ZeroTrustTunnelCloudflaredConfigA#aud_tag}
        :param team_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#team_name ZeroTrustTunnelCloudflaredConfigA#team_name}.
        :param required: Deny traffic that has not fulfilled Access authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#required ZeroTrustTunnelCloudflaredConfigA#required}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20a60e9b257f0e8b9abbb3a8f78eab1e10d6ee1e0b031ad13ee4aaf660dffd9b)
            check_type(argname="argument aud_tag", value=aud_tag, expected_type=type_hints["aud_tag"])
            check_type(argname="argument team_name", value=team_name, expected_type=type_hints["team_name"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "aud_tag": aud_tag,
            "team_name": team_name,
        }
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def aud_tag(self) -> typing.List[builtins.str]:
        '''Access applications that are allowed to reach this hostname for this Tunnel.

        Audience tags can be identified in the dashboard or via the List Access policies API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#aud_tag ZeroTrustTunnelCloudflaredConfigA#aud_tag}
        '''
        result = self._values.get("aud_tag")
        assert result is not None, "Required property 'aud_tag' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def team_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#team_name ZeroTrustTunnelCloudflaredConfigA#team_name}.'''
        result = self._values.get("team_name")
        assert result is not None, "Required property 'team_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Deny traffic that has not fulfilled Access authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#required ZeroTrustTunnelCloudflaredConfigA#required}
        '''
        result = self._values.get("required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccessOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccessOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4fa7ca1332841b012c27464174df592b90670d2fca8617311709797e807bd86c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRequired")
    def reset_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequired", []))

    @builtins.property
    @jsii.member(jsii_name="audTagInput")
    def aud_tag_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "audTagInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredInput")
    def required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requiredInput"))

    @builtins.property
    @jsii.member(jsii_name="teamNameInput")
    def team_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamNameInput"))

    @builtins.property
    @jsii.member(jsii_name="audTag")
    def aud_tag(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "audTag"))

    @aud_tag.setter
    def aud_tag(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da6c6bc5a9881cf2cfba2ada3572971fa29eefe0af5cb17557f24304e4f6ac97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "required"))

    @required.setter
    def required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1404004aacbde685d7d22faa5459f5f3133b884dd737ef96ae2167805dd1a626)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "required", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamName")
    def team_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamName"))

    @team_name.setter
    def team_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c124038ff7b5a28a45f90decffdb0c244b08378d55e01244cd389c54e4c36e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac9223dbdf428a80d97fa8153040bfaab2f87ef4ec8148a95a48a741aabb2c66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__002c9903b2829bd379d0411c70391f148d97d4381fa8d18fbd91835b6138d495)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAccess")
    def put_access(
        self,
        *,
        aud_tag: typing.Sequence[builtins.str],
        team_name: builtins.str,
        required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param aud_tag: Access applications that are allowed to reach this hostname for this Tunnel. Audience tags can be identified in the dashboard or via the List Access policies API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#aud_tag ZeroTrustTunnelCloudflaredConfigA#aud_tag}
        :param team_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#team_name ZeroTrustTunnelCloudflaredConfigA#team_name}.
        :param required: Deny traffic that has not fulfilled Access authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#required ZeroTrustTunnelCloudflaredConfigA#required}
        '''
        value = ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess(
            aud_tag=aud_tag, team_name=team_name, required=required
        )

        return typing.cast(None, jsii.invoke(self, "putAccess", [value]))

    @jsii.member(jsii_name="resetAccess")
    def reset_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccess", []))

    @jsii.member(jsii_name="resetCaPool")
    def reset_ca_pool(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaPool", []))

    @jsii.member(jsii_name="resetConnectTimeout")
    def reset_connect_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeout", []))

    @jsii.member(jsii_name="resetDisableChunkedEncoding")
    def reset_disable_chunked_encoding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableChunkedEncoding", []))

    @jsii.member(jsii_name="resetHttp2Origin")
    def reset_http2_origin(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttp2Origin", []))

    @jsii.member(jsii_name="resetHttpHostHeader")
    def reset_http_host_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpHostHeader", []))

    @jsii.member(jsii_name="resetKeepAliveConnections")
    def reset_keep_alive_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepAliveConnections", []))

    @jsii.member(jsii_name="resetKeepAliveTimeout")
    def reset_keep_alive_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepAliveTimeout", []))

    @jsii.member(jsii_name="resetNoHappyEyeballs")
    def reset_no_happy_eyeballs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoHappyEyeballs", []))

    @jsii.member(jsii_name="resetNoTlsVerify")
    def reset_no_tls_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoTlsVerify", []))

    @jsii.member(jsii_name="resetOriginServerName")
    def reset_origin_server_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginServerName", []))

    @jsii.member(jsii_name="resetProxyType")
    def reset_proxy_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProxyType", []))

    @jsii.member(jsii_name="resetTcpKeepAlive")
    def reset_tcp_keep_alive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTcpKeepAlive", []))

    @jsii.member(jsii_name="resetTlsTimeout")
    def reset_tls_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsTimeout", []))

    @builtins.property
    @jsii.member(jsii_name="access")
    def access(
        self,
    ) -> ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccessOutputReference:
        return typing.cast(ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccessOutputReference, jsii.get(self, "access"))

    @builtins.property
    @jsii.member(jsii_name="accessInput")
    def access_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess]], jsii.get(self, "accessInput"))

    @builtins.property
    @jsii.member(jsii_name="caPoolInput")
    def ca_pool_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPoolInput"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutInput")
    def connect_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="disableChunkedEncodingInput")
    def disable_chunked_encoding_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableChunkedEncodingInput"))

    @builtins.property
    @jsii.member(jsii_name="http2OriginInput")
    def http2_origin_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "http2OriginInput"))

    @builtins.property
    @jsii.member(jsii_name="httpHostHeaderInput")
    def http_host_header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpHostHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="keepAliveConnectionsInput")
    def keep_alive_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keepAliveConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="keepAliveTimeoutInput")
    def keep_alive_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keepAliveTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="noHappyEyeballsInput")
    def no_happy_eyeballs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noHappyEyeballsInput"))

    @builtins.property
    @jsii.member(jsii_name="noTlsVerifyInput")
    def no_tls_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noTlsVerifyInput"))

    @builtins.property
    @jsii.member(jsii_name="originServerNameInput")
    def origin_server_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "originServerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="proxyTypeInput")
    def proxy_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "proxyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="tcpKeepAliveInput")
    def tcp_keep_alive_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tcpKeepAliveInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsTimeoutInput")
    def tls_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tlsTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="caPool")
    def ca_pool(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caPool"))

    @ca_pool.setter
    def ca_pool(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9eafb204d2155f61eda72af72cb732cb47f9616611077a0a8d8161634aa548a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caPool", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectTimeout")
    def connect_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectTimeout"))

    @connect_timeout.setter
    def connect_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a56728013f54a20f3eec3bf4ae2f94902c0781632310ecd81351d75dae4b1e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableChunkedEncoding")
    def disable_chunked_encoding(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableChunkedEncoding"))

    @disable_chunked_encoding.setter
    def disable_chunked_encoding(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b26c3f96c51810eefdae1b7a7ae9161e97d057ff878ef145bd2bf74d2bb1237)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableChunkedEncoding", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="http2Origin")
    def http2_origin(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "http2Origin"))

    @http2_origin.setter
    def http2_origin(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5096e06b6fe75bc1e88c42e87cbd7dbbcf94124877c6e39f8185c704e2523ef5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "http2Origin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpHostHeader")
    def http_host_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpHostHeader"))

    @http_host_header.setter
    def http_host_header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d9c02ac925e4a485da10d453467e7f1536e840f88c6777140f5be3fdcf18914)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpHostHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepAliveConnections")
    def keep_alive_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keepAliveConnections"))

    @keep_alive_connections.setter
    def keep_alive_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5376f92b076ddc5ba08f02f85496837430c0ba6979f26c2dd114a1c5649271e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepAliveConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepAliveTimeout")
    def keep_alive_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keepAliveTimeout"))

    @keep_alive_timeout.setter
    def keep_alive_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c5bb26c2c5f7f9b1338840d635054f9f74c5fd7af65f561b2bb3a5e2d593fcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepAliveTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noHappyEyeballs")
    def no_happy_eyeballs(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noHappyEyeballs"))

    @no_happy_eyeballs.setter
    def no_happy_eyeballs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68ba2eb63d9c38e8acae6901db9518d0e013ec0036285dc417ba69c50f6b62a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noHappyEyeballs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noTlsVerify")
    def no_tls_verify(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noTlsVerify"))

    @no_tls_verify.setter
    def no_tls_verify(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__036f8831ae994909a32ef20e7f1c530ddb21e3051fa146db50b328656d6448fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noTlsVerify", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="originServerName")
    def origin_server_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originServerName"))

    @origin_server_name.setter
    def origin_server_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d92735a5e4d644b5aad7310d045fc149dcc7bdddd87288a37f90d6dc99e9bd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "originServerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proxyType")
    def proxy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "proxyType"))

    @proxy_type.setter
    def proxy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ecc9d822d9a770433b096860012372a6ea6396a71eb9dbf9f049b35c234c5ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tcpKeepAlive")
    def tcp_keep_alive(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tcpKeepAlive"))

    @tcp_keep_alive.setter
    def tcp_keep_alive(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26b634c3d53fc802b51668fe73e23ed4dc268592fbe33f0a5ad713e722b81343)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tcpKeepAlive", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsTimeout")
    def tls_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tlsTimeout"))

    @tls_timeout.setter
    def tls_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c54dd04131705232f4a5c26dea814add7b7a9049b126d13a7c5bf5ecb96c6aa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2425b0ae92ff586b29d3e6c5a5c625bbafe2f74ad1600cec139309a09ee1d3ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustTunnelCloudflaredConfigConfigIngressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigIngressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f17cbc7daf9c22b52ecd7a443ecc0b26cd418f580c8a890d57818791846aa7b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putOriginRequest")
    def put_origin_request(
        self,
        *,
        access: typing.Optional[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess, typing.Dict[builtins.str, typing.Any]]] = None,
        ca_pool: typing.Optional[builtins.str] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        disable_chunked_encoding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http2_origin: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_host_header: typing.Optional[builtins.str] = None,
        keep_alive_connections: typing.Optional[jsii.Number] = None,
        keep_alive_timeout: typing.Optional[jsii.Number] = None,
        no_happy_eyeballs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        no_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        origin_server_name: typing.Optional[builtins.str] = None,
        proxy_type: typing.Optional[builtins.str] = None,
        tcp_keep_alive: typing.Optional[jsii.Number] = None,
        tls_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param access: For all L7 requests to this hostname, cloudflared will validate each request's Cf-Access-Jwt-Assertion request header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#access ZeroTrustTunnelCloudflaredConfigA#access}
        :param ca_pool: Path to the certificate authority (CA) for the certificate of your origin. This option should be used only if your certificate is not signed by Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#ca_pool ZeroTrustTunnelCloudflaredConfigA#ca_pool}
        :param connect_timeout: Timeout for establishing a new TCP connection to your origin server. This excludes the time taken to establish TLS, which is controlled by tlsTimeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#connect_timeout ZeroTrustTunnelCloudflaredConfigA#connect_timeout}
        :param disable_chunked_encoding: Disables chunked transfer encoding. Useful if you are running a WSGI server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#disable_chunked_encoding ZeroTrustTunnelCloudflaredConfigA#disable_chunked_encoding}
        :param http2_origin: Attempt to connect to origin using HTTP2. Origin must be configured as https. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http2_origin ZeroTrustTunnelCloudflaredConfigA#http2_origin}
        :param http_host_header: Sets the HTTP Host header on requests sent to the local service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http_host_header ZeroTrustTunnelCloudflaredConfigA#http_host_header}
        :param keep_alive_connections: Maximum number of idle keepalive connections between Tunnel and your origin. This does not restrict the total number of concurrent connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_connections ZeroTrustTunnelCloudflaredConfigA#keep_alive_connections}
        :param keep_alive_timeout: Timeout after which an idle keepalive connection can be discarded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_timeout ZeroTrustTunnelCloudflaredConfigA#keep_alive_timeout}
        :param no_happy_eyeballs: Disable the “happy eyeballs” algorithm for IPv4/IPv6 fallback if your local network has misconfigured one of the protocols. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_happy_eyeballs ZeroTrustTunnelCloudflaredConfigA#no_happy_eyeballs}
        :param no_tls_verify: Disables TLS verification of the certificate presented by your origin. Will allow any certificate from the origin to be accepted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_tls_verify ZeroTrustTunnelCloudflaredConfigA#no_tls_verify}
        :param origin_server_name: Hostname that cloudflared should expect from your origin server certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_server_name ZeroTrustTunnelCloudflaredConfigA#origin_server_name}
        :param proxy_type: cloudflared starts a proxy server to translate HTTP traffic into TCP when proxying, for example, SSH or RDP. This configures what type of proxy will be started. Valid options are: "" for the regular proxy and "socks" for a SOCKS5 proxy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#proxy_type ZeroTrustTunnelCloudflaredConfigA#proxy_type}
        :param tcp_keep_alive: The timeout after which a TCP keepalive packet is sent on a connection between Tunnel and the origin server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tcp_keep_alive ZeroTrustTunnelCloudflaredConfigA#tcp_keep_alive}
        :param tls_timeout: Timeout for completing a TLS handshake to your origin server, if you have chosen to connect Tunnel to an HTTPS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tls_timeout ZeroTrustTunnelCloudflaredConfigA#tls_timeout}
        '''
        value = ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest(
            access=access,
            ca_pool=ca_pool,
            connect_timeout=connect_timeout,
            disable_chunked_encoding=disable_chunked_encoding,
            http2_origin=http2_origin,
            http_host_header=http_host_header,
            keep_alive_connections=keep_alive_connections,
            keep_alive_timeout=keep_alive_timeout,
            no_happy_eyeballs=no_happy_eyeballs,
            no_tls_verify=no_tls_verify,
            origin_server_name=origin_server_name,
            proxy_type=proxy_type,
            tcp_keep_alive=tcp_keep_alive,
            tls_timeout=tls_timeout,
        )

        return typing.cast(None, jsii.invoke(self, "putOriginRequest", [value]))

    @jsii.member(jsii_name="resetHostname")
    def reset_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostname", []))

    @jsii.member(jsii_name="resetOriginRequest")
    def reset_origin_request(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginRequest", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @builtins.property
    @jsii.member(jsii_name="originRequest")
    def origin_request(
        self,
    ) -> ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestOutputReference:
        return typing.cast(ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestOutputReference, jsii.get(self, "originRequest"))

    @builtins.property
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="originRequestInput")
    def origin_request_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest]], jsii.get(self, "originRequestInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd001401f033eeff80f17237a9cada0d318478849ca33cba086e98420f68e4af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c25c9fa0afb88a66cf1086045d8757f13c3455317ab8bd9316b4e2a2b311e5c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4df53528ae48c7f350bfa2f464f5729ac424f48868680bf945673b80d07d21d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngress]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngress]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngress]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f319f01721fc85cdfa7243ad172a339dfe15713126c976b7fc7aaf6daf65e14b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigOriginRequest",
    jsii_struct_bases=[],
    name_mapping={
        "access": "access",
        "ca_pool": "caPool",
        "connect_timeout": "connectTimeout",
        "disable_chunked_encoding": "disableChunkedEncoding",
        "http2_origin": "http2Origin",
        "http_host_header": "httpHostHeader",
        "keep_alive_connections": "keepAliveConnections",
        "keep_alive_timeout": "keepAliveTimeout",
        "no_happy_eyeballs": "noHappyEyeballs",
        "no_tls_verify": "noTlsVerify",
        "origin_server_name": "originServerName",
        "proxy_type": "proxyType",
        "tcp_keep_alive": "tcpKeepAlive",
        "tls_timeout": "tlsTimeout",
    },
)
class ZeroTrustTunnelCloudflaredConfigConfigOriginRequest:
    def __init__(
        self,
        *,
        access: typing.Optional[typing.Union["ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess", typing.Dict[builtins.str, typing.Any]]] = None,
        ca_pool: typing.Optional[builtins.str] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        disable_chunked_encoding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http2_origin: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_host_header: typing.Optional[builtins.str] = None,
        keep_alive_connections: typing.Optional[jsii.Number] = None,
        keep_alive_timeout: typing.Optional[jsii.Number] = None,
        no_happy_eyeballs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        no_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        origin_server_name: typing.Optional[builtins.str] = None,
        proxy_type: typing.Optional[builtins.str] = None,
        tcp_keep_alive: typing.Optional[jsii.Number] = None,
        tls_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param access: For all L7 requests to this hostname, cloudflared will validate each request's Cf-Access-Jwt-Assertion request header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#access ZeroTrustTunnelCloudflaredConfigA#access}
        :param ca_pool: Path to the certificate authority (CA) for the certificate of your origin. This option should be used only if your certificate is not signed by Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#ca_pool ZeroTrustTunnelCloudflaredConfigA#ca_pool}
        :param connect_timeout: Timeout for establishing a new TCP connection to your origin server. This excludes the time taken to establish TLS, which is controlled by tlsTimeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#connect_timeout ZeroTrustTunnelCloudflaredConfigA#connect_timeout}
        :param disable_chunked_encoding: Disables chunked transfer encoding. Useful if you are running a WSGI server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#disable_chunked_encoding ZeroTrustTunnelCloudflaredConfigA#disable_chunked_encoding}
        :param http2_origin: Attempt to connect to origin using HTTP2. Origin must be configured as https. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http2_origin ZeroTrustTunnelCloudflaredConfigA#http2_origin}
        :param http_host_header: Sets the HTTP Host header on requests sent to the local service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http_host_header ZeroTrustTunnelCloudflaredConfigA#http_host_header}
        :param keep_alive_connections: Maximum number of idle keepalive connections between Tunnel and your origin. This does not restrict the total number of concurrent connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_connections ZeroTrustTunnelCloudflaredConfigA#keep_alive_connections}
        :param keep_alive_timeout: Timeout after which an idle keepalive connection can be discarded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_timeout ZeroTrustTunnelCloudflaredConfigA#keep_alive_timeout}
        :param no_happy_eyeballs: Disable the “happy eyeballs” algorithm for IPv4/IPv6 fallback if your local network has misconfigured one of the protocols. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_happy_eyeballs ZeroTrustTunnelCloudflaredConfigA#no_happy_eyeballs}
        :param no_tls_verify: Disables TLS verification of the certificate presented by your origin. Will allow any certificate from the origin to be accepted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_tls_verify ZeroTrustTunnelCloudflaredConfigA#no_tls_verify}
        :param origin_server_name: Hostname that cloudflared should expect from your origin server certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_server_name ZeroTrustTunnelCloudflaredConfigA#origin_server_name}
        :param proxy_type: cloudflared starts a proxy server to translate HTTP traffic into TCP when proxying, for example, SSH or RDP. This configures what type of proxy will be started. Valid options are: "" for the regular proxy and "socks" for a SOCKS5 proxy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#proxy_type ZeroTrustTunnelCloudflaredConfigA#proxy_type}
        :param tcp_keep_alive: The timeout after which a TCP keepalive packet is sent on a connection between Tunnel and the origin server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tcp_keep_alive ZeroTrustTunnelCloudflaredConfigA#tcp_keep_alive}
        :param tls_timeout: Timeout for completing a TLS handshake to your origin server, if you have chosen to connect Tunnel to an HTTPS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tls_timeout ZeroTrustTunnelCloudflaredConfigA#tls_timeout}
        '''
        if isinstance(access, dict):
            access = ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess(**access)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5d3bf55d0c00a7c05d180f0b789427c7dae716dde405899da4b0e2783a1c192)
            check_type(argname="argument access", value=access, expected_type=type_hints["access"])
            check_type(argname="argument ca_pool", value=ca_pool, expected_type=type_hints["ca_pool"])
            check_type(argname="argument connect_timeout", value=connect_timeout, expected_type=type_hints["connect_timeout"])
            check_type(argname="argument disable_chunked_encoding", value=disable_chunked_encoding, expected_type=type_hints["disable_chunked_encoding"])
            check_type(argname="argument http2_origin", value=http2_origin, expected_type=type_hints["http2_origin"])
            check_type(argname="argument http_host_header", value=http_host_header, expected_type=type_hints["http_host_header"])
            check_type(argname="argument keep_alive_connections", value=keep_alive_connections, expected_type=type_hints["keep_alive_connections"])
            check_type(argname="argument keep_alive_timeout", value=keep_alive_timeout, expected_type=type_hints["keep_alive_timeout"])
            check_type(argname="argument no_happy_eyeballs", value=no_happy_eyeballs, expected_type=type_hints["no_happy_eyeballs"])
            check_type(argname="argument no_tls_verify", value=no_tls_verify, expected_type=type_hints["no_tls_verify"])
            check_type(argname="argument origin_server_name", value=origin_server_name, expected_type=type_hints["origin_server_name"])
            check_type(argname="argument proxy_type", value=proxy_type, expected_type=type_hints["proxy_type"])
            check_type(argname="argument tcp_keep_alive", value=tcp_keep_alive, expected_type=type_hints["tcp_keep_alive"])
            check_type(argname="argument tls_timeout", value=tls_timeout, expected_type=type_hints["tls_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access is not None:
            self._values["access"] = access
        if ca_pool is not None:
            self._values["ca_pool"] = ca_pool
        if connect_timeout is not None:
            self._values["connect_timeout"] = connect_timeout
        if disable_chunked_encoding is not None:
            self._values["disable_chunked_encoding"] = disable_chunked_encoding
        if http2_origin is not None:
            self._values["http2_origin"] = http2_origin
        if http_host_header is not None:
            self._values["http_host_header"] = http_host_header
        if keep_alive_connections is not None:
            self._values["keep_alive_connections"] = keep_alive_connections
        if keep_alive_timeout is not None:
            self._values["keep_alive_timeout"] = keep_alive_timeout
        if no_happy_eyeballs is not None:
            self._values["no_happy_eyeballs"] = no_happy_eyeballs
        if no_tls_verify is not None:
            self._values["no_tls_verify"] = no_tls_verify
        if origin_server_name is not None:
            self._values["origin_server_name"] = origin_server_name
        if proxy_type is not None:
            self._values["proxy_type"] = proxy_type
        if tcp_keep_alive is not None:
            self._values["tcp_keep_alive"] = tcp_keep_alive
        if tls_timeout is not None:
            self._values["tls_timeout"] = tls_timeout

    @builtins.property
    def access(
        self,
    ) -> typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess"]:
        '''For all L7 requests to this hostname, cloudflared will validate each request's Cf-Access-Jwt-Assertion request header.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#access ZeroTrustTunnelCloudflaredConfigA#access}
        '''
        result = self._values.get("access")
        return typing.cast(typing.Optional["ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess"], result)

    @builtins.property
    def ca_pool(self) -> typing.Optional[builtins.str]:
        '''Path to the certificate authority (CA) for the certificate of your origin.

        This option should be used only if your certificate is not signed by Cloudflare.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#ca_pool ZeroTrustTunnelCloudflaredConfigA#ca_pool}
        '''
        result = self._values.get("ca_pool")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connect_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout for establishing a new TCP connection to your origin server.

        This excludes the time taken to establish TLS, which is controlled by tlsTimeout.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#connect_timeout ZeroTrustTunnelCloudflaredConfigA#connect_timeout}
        '''
        result = self._values.get("connect_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disable_chunked_encoding(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disables chunked transfer encoding. Useful if you are running a WSGI server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#disable_chunked_encoding ZeroTrustTunnelCloudflaredConfigA#disable_chunked_encoding}
        '''
        result = self._values.get("disable_chunked_encoding")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def http2_origin(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Attempt to connect to origin using HTTP2. Origin must be configured as https.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http2_origin ZeroTrustTunnelCloudflaredConfigA#http2_origin}
        '''
        result = self._values.get("http2_origin")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def http_host_header(self) -> typing.Optional[builtins.str]:
        '''Sets the HTTP Host header on requests sent to the local service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http_host_header ZeroTrustTunnelCloudflaredConfigA#http_host_header}
        '''
        result = self._values.get("http_host_header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keep_alive_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle keepalive connections between Tunnel and your origin.

        This does not restrict the total number of concurrent connections.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_connections ZeroTrustTunnelCloudflaredConfigA#keep_alive_connections}
        '''
        result = self._values.get("keep_alive_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def keep_alive_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout after which an idle keepalive connection can be discarded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_timeout ZeroTrustTunnelCloudflaredConfigA#keep_alive_timeout}
        '''
        result = self._values.get("keep_alive_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def no_happy_eyeballs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable the “happy eyeballs” algorithm for IPv4/IPv6 fallback if your local network has misconfigured one of the protocols.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_happy_eyeballs ZeroTrustTunnelCloudflaredConfigA#no_happy_eyeballs}
        '''
        result = self._values.get("no_happy_eyeballs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def no_tls_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disables TLS verification of the certificate presented by your origin.

        Will allow any certificate from the origin to be accepted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_tls_verify ZeroTrustTunnelCloudflaredConfigA#no_tls_verify}
        '''
        result = self._values.get("no_tls_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def origin_server_name(self) -> typing.Optional[builtins.str]:
        '''Hostname that cloudflared should expect from your origin server certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_server_name ZeroTrustTunnelCloudflaredConfigA#origin_server_name}
        '''
        result = self._values.get("origin_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxy_type(self) -> typing.Optional[builtins.str]:
        '''cloudflared starts a proxy server to translate HTTP traffic into TCP when proxying, for example, SSH or RDP.

        This configures what type of proxy will be started. Valid options are: "" for the regular proxy and "socks" for a SOCKS5 proxy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#proxy_type ZeroTrustTunnelCloudflaredConfigA#proxy_type}
        '''
        result = self._values.get("proxy_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tcp_keep_alive(self) -> typing.Optional[jsii.Number]:
        '''The timeout after which a TCP keepalive packet is sent on a connection between Tunnel and the origin server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tcp_keep_alive ZeroTrustTunnelCloudflaredConfigA#tcp_keep_alive}
        '''
        result = self._values.get("tcp_keep_alive")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout for completing a TLS handshake to your origin server, if you have chosen to connect Tunnel to an HTTPS server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tls_timeout ZeroTrustTunnelCloudflaredConfigA#tls_timeout}
        '''
        result = self._values.get("tls_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustTunnelCloudflaredConfigConfigOriginRequest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess",
    jsii_struct_bases=[],
    name_mapping={
        "aud_tag": "audTag",
        "team_name": "teamName",
        "required": "required",
    },
)
class ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess:
    def __init__(
        self,
        *,
        aud_tag: typing.Sequence[builtins.str],
        team_name: builtins.str,
        required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param aud_tag: Access applications that are allowed to reach this hostname for this Tunnel. Audience tags can be identified in the dashboard or via the List Access policies API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#aud_tag ZeroTrustTunnelCloudflaredConfigA#aud_tag}
        :param team_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#team_name ZeroTrustTunnelCloudflaredConfigA#team_name}.
        :param required: Deny traffic that has not fulfilled Access authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#required ZeroTrustTunnelCloudflaredConfigA#required}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__636abbba3d6b91bc47723277ca9d1141f813092f82ba1708cb75d1f0c9097db8)
            check_type(argname="argument aud_tag", value=aud_tag, expected_type=type_hints["aud_tag"])
            check_type(argname="argument team_name", value=team_name, expected_type=type_hints["team_name"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "aud_tag": aud_tag,
            "team_name": team_name,
        }
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def aud_tag(self) -> typing.List[builtins.str]:
        '''Access applications that are allowed to reach this hostname for this Tunnel.

        Audience tags can be identified in the dashboard or via the List Access policies API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#aud_tag ZeroTrustTunnelCloudflaredConfigA#aud_tag}
        '''
        result = self._values.get("aud_tag")
        assert result is not None, "Required property 'aud_tag' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def team_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#team_name ZeroTrustTunnelCloudflaredConfigA#team_name}.'''
        result = self._values.get("team_name")
        assert result is not None, "Required property 'team_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Deny traffic that has not fulfilled Access authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#required ZeroTrustTunnelCloudflaredConfigA#required}
        '''
        result = self._values.get("required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccessOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccessOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__86e0f86e5b3fc8c2e50137741b58ef29e41fe146d0cdfb9d6592b12d8c6dd91d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRequired")
    def reset_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequired", []))

    @builtins.property
    @jsii.member(jsii_name="audTagInput")
    def aud_tag_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "audTagInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredInput")
    def required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requiredInput"))

    @builtins.property
    @jsii.member(jsii_name="teamNameInput")
    def team_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamNameInput"))

    @builtins.property
    @jsii.member(jsii_name="audTag")
    def aud_tag(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "audTag"))

    @aud_tag.setter
    def aud_tag(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0a857f05881463e736687791e68e716a84630cfacfc70049c12e56182fc9eaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "required"))

    @required.setter
    def required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d81ad11748c769d98fffc79457073e3599b8f2fc6a9ac81fc81acd315386d00e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "required", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamName")
    def team_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamName"))

    @team_name.setter
    def team_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67df2792519e6992fba24f3cdbd2a77cee676f18b08bffc0ee07cedb00883696)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbe13f1a97dd912038df207594bec01c8ba0426d9a89f22b5e54042a7328cb09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustTunnelCloudflaredConfigConfigOriginRequestOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigOriginRequestOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__14ed818023f6e70d496e8f3d24a0342f4cfb4ff2cdb736e798cdb43c9bfaa173)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAccess")
    def put_access(
        self,
        *,
        aud_tag: typing.Sequence[builtins.str],
        team_name: builtins.str,
        required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param aud_tag: Access applications that are allowed to reach this hostname for this Tunnel. Audience tags can be identified in the dashboard or via the List Access policies API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#aud_tag ZeroTrustTunnelCloudflaredConfigA#aud_tag}
        :param team_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#team_name ZeroTrustTunnelCloudflaredConfigA#team_name}.
        :param required: Deny traffic that has not fulfilled Access authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#required ZeroTrustTunnelCloudflaredConfigA#required}
        '''
        value = ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess(
            aud_tag=aud_tag, team_name=team_name, required=required
        )

        return typing.cast(None, jsii.invoke(self, "putAccess", [value]))

    @jsii.member(jsii_name="resetAccess")
    def reset_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccess", []))

    @jsii.member(jsii_name="resetCaPool")
    def reset_ca_pool(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaPool", []))

    @jsii.member(jsii_name="resetConnectTimeout")
    def reset_connect_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeout", []))

    @jsii.member(jsii_name="resetDisableChunkedEncoding")
    def reset_disable_chunked_encoding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableChunkedEncoding", []))

    @jsii.member(jsii_name="resetHttp2Origin")
    def reset_http2_origin(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttp2Origin", []))

    @jsii.member(jsii_name="resetHttpHostHeader")
    def reset_http_host_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpHostHeader", []))

    @jsii.member(jsii_name="resetKeepAliveConnections")
    def reset_keep_alive_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepAliveConnections", []))

    @jsii.member(jsii_name="resetKeepAliveTimeout")
    def reset_keep_alive_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepAliveTimeout", []))

    @jsii.member(jsii_name="resetNoHappyEyeballs")
    def reset_no_happy_eyeballs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoHappyEyeballs", []))

    @jsii.member(jsii_name="resetNoTlsVerify")
    def reset_no_tls_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoTlsVerify", []))

    @jsii.member(jsii_name="resetOriginServerName")
    def reset_origin_server_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginServerName", []))

    @jsii.member(jsii_name="resetProxyType")
    def reset_proxy_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProxyType", []))

    @jsii.member(jsii_name="resetTcpKeepAlive")
    def reset_tcp_keep_alive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTcpKeepAlive", []))

    @jsii.member(jsii_name="resetTlsTimeout")
    def reset_tls_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsTimeout", []))

    @builtins.property
    @jsii.member(jsii_name="access")
    def access(
        self,
    ) -> ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccessOutputReference:
        return typing.cast(ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccessOutputReference, jsii.get(self, "access"))

    @builtins.property
    @jsii.member(jsii_name="accessInput")
    def access_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess]], jsii.get(self, "accessInput"))

    @builtins.property
    @jsii.member(jsii_name="caPoolInput")
    def ca_pool_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPoolInput"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutInput")
    def connect_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="disableChunkedEncodingInput")
    def disable_chunked_encoding_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableChunkedEncodingInput"))

    @builtins.property
    @jsii.member(jsii_name="http2OriginInput")
    def http2_origin_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "http2OriginInput"))

    @builtins.property
    @jsii.member(jsii_name="httpHostHeaderInput")
    def http_host_header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpHostHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="keepAliveConnectionsInput")
    def keep_alive_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keepAliveConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="keepAliveTimeoutInput")
    def keep_alive_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keepAliveTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="noHappyEyeballsInput")
    def no_happy_eyeballs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noHappyEyeballsInput"))

    @builtins.property
    @jsii.member(jsii_name="noTlsVerifyInput")
    def no_tls_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noTlsVerifyInput"))

    @builtins.property
    @jsii.member(jsii_name="originServerNameInput")
    def origin_server_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "originServerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="proxyTypeInput")
    def proxy_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "proxyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="tcpKeepAliveInput")
    def tcp_keep_alive_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tcpKeepAliveInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsTimeoutInput")
    def tls_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tlsTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="caPool")
    def ca_pool(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caPool"))

    @ca_pool.setter
    def ca_pool(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__712a69bd37ac0a2424e23862764e00b6d78181e2914cf2a34dec1dddbe45d2a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caPool", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectTimeout")
    def connect_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectTimeout"))

    @connect_timeout.setter
    def connect_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0a11cbad4d6de372eb7883d507114eb630475d6ea23a58b7bdf09153afe8d80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableChunkedEncoding")
    def disable_chunked_encoding(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableChunkedEncoding"))

    @disable_chunked_encoding.setter
    def disable_chunked_encoding(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c36838fba95a0c619011e21bd444a6a986dcb95669169e60a06120f3caabc595)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableChunkedEncoding", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="http2Origin")
    def http2_origin(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "http2Origin"))

    @http2_origin.setter
    def http2_origin(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9f7a86e1dfff26d9d5cdd690048c026ece6dc10c90e8f0d0c0f0bbcc2ac5958)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "http2Origin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpHostHeader")
    def http_host_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpHostHeader"))

    @http_host_header.setter
    def http_host_header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__438be1ee5abfbdd1d913817cc3bd02abdfac71d9451b467897af34ba57c0eeab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpHostHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepAliveConnections")
    def keep_alive_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keepAliveConnections"))

    @keep_alive_connections.setter
    def keep_alive_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af7a7e50fb00305b05aab1a9a34504b9f087fa35775ce3552c5bf826e8c40e4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepAliveConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepAliveTimeout")
    def keep_alive_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keepAliveTimeout"))

    @keep_alive_timeout.setter
    def keep_alive_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4a0063089e26377a1d0f645ecc027cdd51213031e7b1042ebf2a1c21fbc77ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepAliveTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noHappyEyeballs")
    def no_happy_eyeballs(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noHappyEyeballs"))

    @no_happy_eyeballs.setter
    def no_happy_eyeballs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91fadc061a2ebd7000f9fcce0ecb9d0733a5b8c4391a2d45c324b0e8774eb2bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noHappyEyeballs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noTlsVerify")
    def no_tls_verify(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noTlsVerify"))

    @no_tls_verify.setter
    def no_tls_verify(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45eb764a16a1e8e1ba2029ae09bf43c7eee9a45782ade31b4be1bc38316a4ae6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noTlsVerify", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="originServerName")
    def origin_server_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originServerName"))

    @origin_server_name.setter
    def origin_server_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c47a0f6c18dd6a911bb9888d6f3946b8cd35b726039d99d1184603f65f43b871)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "originServerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proxyType")
    def proxy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "proxyType"))

    @proxy_type.setter
    def proxy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28ed5e2a6769463c229129c016b826003db5aae63124d3225b493ad60b7b00ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tcpKeepAlive")
    def tcp_keep_alive(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tcpKeepAlive"))

    @tcp_keep_alive.setter
    def tcp_keep_alive(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c84d9c4d023c40e2023e656a84aa1bff48d21a3dfb57b75f93198b9d99e6ba0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tcpKeepAlive", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsTimeout")
    def tls_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tlsTimeout"))

    @tls_timeout.setter
    def tls_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcc1f1c89618530620d72521d58eb34983a055b9dae45ef76dd9565c4aaa8047)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequest]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequest]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequest]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbbd31fb600c0d6fd99236aee67247968ecc971dbe01adecc5cc57df562cac7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustTunnelCloudflaredConfigConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__19457e6868b063037de72e53eaf5ef0e9cc6b6117cdbf957d322f714d0825bbc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putIngress")
    def put_ingress(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigIngress, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68b25bc679e3ead5f8ffd02acdfce218e10142a2f13f4aabcba6aac0009c517d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putIngress", [value]))

    @jsii.member(jsii_name="putOriginRequest")
    def put_origin_request(
        self,
        *,
        access: typing.Optional[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess, typing.Dict[builtins.str, typing.Any]]] = None,
        ca_pool: typing.Optional[builtins.str] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        disable_chunked_encoding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http2_origin: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_host_header: typing.Optional[builtins.str] = None,
        keep_alive_connections: typing.Optional[jsii.Number] = None,
        keep_alive_timeout: typing.Optional[jsii.Number] = None,
        no_happy_eyeballs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        no_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        origin_server_name: typing.Optional[builtins.str] = None,
        proxy_type: typing.Optional[builtins.str] = None,
        tcp_keep_alive: typing.Optional[jsii.Number] = None,
        tls_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param access: For all L7 requests to this hostname, cloudflared will validate each request's Cf-Access-Jwt-Assertion request header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#access ZeroTrustTunnelCloudflaredConfigA#access}
        :param ca_pool: Path to the certificate authority (CA) for the certificate of your origin. This option should be used only if your certificate is not signed by Cloudflare. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#ca_pool ZeroTrustTunnelCloudflaredConfigA#ca_pool}
        :param connect_timeout: Timeout for establishing a new TCP connection to your origin server. This excludes the time taken to establish TLS, which is controlled by tlsTimeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#connect_timeout ZeroTrustTunnelCloudflaredConfigA#connect_timeout}
        :param disable_chunked_encoding: Disables chunked transfer encoding. Useful if you are running a WSGI server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#disable_chunked_encoding ZeroTrustTunnelCloudflaredConfigA#disable_chunked_encoding}
        :param http2_origin: Attempt to connect to origin using HTTP2. Origin must be configured as https. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http2_origin ZeroTrustTunnelCloudflaredConfigA#http2_origin}
        :param http_host_header: Sets the HTTP Host header on requests sent to the local service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#http_host_header ZeroTrustTunnelCloudflaredConfigA#http_host_header}
        :param keep_alive_connections: Maximum number of idle keepalive connections between Tunnel and your origin. This does not restrict the total number of concurrent connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_connections ZeroTrustTunnelCloudflaredConfigA#keep_alive_connections}
        :param keep_alive_timeout: Timeout after which an idle keepalive connection can be discarded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#keep_alive_timeout ZeroTrustTunnelCloudflaredConfigA#keep_alive_timeout}
        :param no_happy_eyeballs: Disable the “happy eyeballs” algorithm for IPv4/IPv6 fallback if your local network has misconfigured one of the protocols. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_happy_eyeballs ZeroTrustTunnelCloudflaredConfigA#no_happy_eyeballs}
        :param no_tls_verify: Disables TLS verification of the certificate presented by your origin. Will allow any certificate from the origin to be accepted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#no_tls_verify ZeroTrustTunnelCloudflaredConfigA#no_tls_verify}
        :param origin_server_name: Hostname that cloudflared should expect from your origin server certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#origin_server_name ZeroTrustTunnelCloudflaredConfigA#origin_server_name}
        :param proxy_type: cloudflared starts a proxy server to translate HTTP traffic into TCP when proxying, for example, SSH or RDP. This configures what type of proxy will be started. Valid options are: "" for the regular proxy and "socks" for a SOCKS5 proxy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#proxy_type ZeroTrustTunnelCloudflaredConfigA#proxy_type}
        :param tcp_keep_alive: The timeout after which a TCP keepalive packet is sent on a connection between Tunnel and the origin server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tcp_keep_alive ZeroTrustTunnelCloudflaredConfigA#tcp_keep_alive}
        :param tls_timeout: Timeout for completing a TLS handshake to your origin server, if you have chosen to connect Tunnel to an HTTPS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_tunnel_cloudflared_config#tls_timeout ZeroTrustTunnelCloudflaredConfigA#tls_timeout}
        '''
        value = ZeroTrustTunnelCloudflaredConfigConfigOriginRequest(
            access=access,
            ca_pool=ca_pool,
            connect_timeout=connect_timeout,
            disable_chunked_encoding=disable_chunked_encoding,
            http2_origin=http2_origin,
            http_host_header=http_host_header,
            keep_alive_connections=keep_alive_connections,
            keep_alive_timeout=keep_alive_timeout,
            no_happy_eyeballs=no_happy_eyeballs,
            no_tls_verify=no_tls_verify,
            origin_server_name=origin_server_name,
            proxy_type=proxy_type,
            tcp_keep_alive=tcp_keep_alive,
            tls_timeout=tls_timeout,
        )

        return typing.cast(None, jsii.invoke(self, "putOriginRequest", [value]))

    @jsii.member(jsii_name="putWarpRouting")
    def put_warp_routing(self) -> None:
        value = ZeroTrustTunnelCloudflaredConfigConfigWarpRouting()

        return typing.cast(None, jsii.invoke(self, "putWarpRouting", [value]))

    @jsii.member(jsii_name="resetIngress")
    def reset_ingress(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngress", []))

    @jsii.member(jsii_name="resetOriginRequest")
    def reset_origin_request(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginRequest", []))

    @jsii.member(jsii_name="resetWarpRouting")
    def reset_warp_routing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWarpRouting", []))

    @builtins.property
    @jsii.member(jsii_name="ingress")
    def ingress(self) -> ZeroTrustTunnelCloudflaredConfigConfigIngressList:
        return typing.cast(ZeroTrustTunnelCloudflaredConfigConfigIngressList, jsii.get(self, "ingress"))

    @builtins.property
    @jsii.member(jsii_name="originRequest")
    def origin_request(
        self,
    ) -> ZeroTrustTunnelCloudflaredConfigConfigOriginRequestOutputReference:
        return typing.cast(ZeroTrustTunnelCloudflaredConfigConfigOriginRequestOutputReference, jsii.get(self, "originRequest"))

    @builtins.property
    @jsii.member(jsii_name="warpRouting")
    def warp_routing(
        self,
    ) -> "ZeroTrustTunnelCloudflaredConfigConfigWarpRoutingOutputReference":
        return typing.cast("ZeroTrustTunnelCloudflaredConfigConfigWarpRoutingOutputReference", jsii.get(self, "warpRouting"))

    @builtins.property
    @jsii.member(jsii_name="ingressInput")
    def ingress_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustTunnelCloudflaredConfigConfigIngress]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustTunnelCloudflaredConfigConfigIngress]]], jsii.get(self, "ingressInput"))

    @builtins.property
    @jsii.member(jsii_name="originRequestInput")
    def origin_request_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequest]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequest]], jsii.get(self, "originRequestInput"))

    @builtins.property
    @jsii.member(jsii_name="warpRoutingInput")
    def warp_routing_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustTunnelCloudflaredConfigConfigWarpRouting"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustTunnelCloudflaredConfigConfigWarpRouting"]], jsii.get(self, "warpRoutingInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a75ca61add465032e585d1d118bacb0832f0d53c4293cc5518b7be51dfec264a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigWarpRouting",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustTunnelCloudflaredConfigConfigWarpRouting:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustTunnelCloudflaredConfigConfigWarpRouting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustTunnelCloudflaredConfigConfigWarpRoutingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustTunnelCloudflaredConfig.ZeroTrustTunnelCloudflaredConfigConfigWarpRoutingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8629155531f17477c6ab961f43617832fd6ee69d2b8d6466e30e9faf33a082e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigWarpRouting]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigWarpRouting]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigWarpRouting]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eff4919160f915420f9d741f4579e95fb8e441e0ccbe4e45aefa0aa1ca49489c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustTunnelCloudflaredConfigA",
    "ZeroTrustTunnelCloudflaredConfigAConfig",
    "ZeroTrustTunnelCloudflaredConfigConfig",
    "ZeroTrustTunnelCloudflaredConfigConfigIngress",
    "ZeroTrustTunnelCloudflaredConfigConfigIngressList",
    "ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest",
    "ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess",
    "ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccessOutputReference",
    "ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestOutputReference",
    "ZeroTrustTunnelCloudflaredConfigConfigIngressOutputReference",
    "ZeroTrustTunnelCloudflaredConfigConfigOriginRequest",
    "ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess",
    "ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccessOutputReference",
    "ZeroTrustTunnelCloudflaredConfigConfigOriginRequestOutputReference",
    "ZeroTrustTunnelCloudflaredConfigConfigOutputReference",
    "ZeroTrustTunnelCloudflaredConfigConfigWarpRouting",
    "ZeroTrustTunnelCloudflaredConfigConfigWarpRoutingOutputReference",
]

publication.publish()

def _typecheckingstub__40c3e700edd3e4bf5ead6f056e28348ae350d0c39ce57e46a2c6c9127b5877e5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    tunnel_id: builtins.str,
    config: typing.Optional[typing.Union[ZeroTrustTunnelCloudflaredConfigConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    source: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__26886a3195522bd58df26c7e41578c5a4b7c8ef2a01aabc8c8b2fc6d581237ad(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__063215e6de559dfdb173577ef39a73e59c8da14db0dd681f9214f49fade47a4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dc0d1f5b6ed840e5a5131c48b61f9fb3e55a49a55c79a9b3758d7f03ed49b0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c95fc4ac1123f5860744e72d1b82de65fe429be4b727ca3fef5e54ece11f1142(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ae33dabb83c6599c16c97f82f27e96662097f36b213d22e119d6e7c7e366024(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    tunnel_id: builtins.str,
    config: typing.Optional[typing.Union[ZeroTrustTunnelCloudflaredConfigConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    source: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eecc74d84626090dba3f174efaac8078277aacbf27564f772b864127e59e4cd7(
    *,
    ingress: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigIngress, typing.Dict[builtins.str, typing.Any]]]]] = None,
    origin_request: typing.Optional[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigOriginRequest, typing.Dict[builtins.str, typing.Any]]] = None,
    warp_routing: typing.Optional[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigWarpRouting, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94ba2948fdcbf8bfb89e179350b70850003429b4a28d4d9de95052440032608e(
    *,
    service: builtins.str,
    hostname: typing.Optional[builtins.str] = None,
    origin_request: typing.Optional[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest, typing.Dict[builtins.str, typing.Any]]] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__789a71d710609a2585f9eae2eb83bf6b57fa6c0db17c94e6645bfe90edf4252a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6f6b94c2e9063411ba3ea0e4468e5e8abf484678b2c45f36ecaadd7f93ae1c0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c85a4871a985d6434999b161b8f01f94e0703bffbc86e2ce98c5a2996bd25500(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8b601bf51439605cb245e9749259926229e1344e64a88b46bf47017131972e6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b980e930be65c7ba3be234f0c54b49c311baa49afbf8e2601b861a0c763ff26(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30261ce8a6f9b865c46563e00808e3aaac0e262f3a28d7dca34c3563c79d5a99(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustTunnelCloudflaredConfigConfigIngress]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c8a4c0dc456e2782d032081ed94a68150911c3af9ffd247979d67021072352e(
    *,
    access: typing.Optional[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess, typing.Dict[builtins.str, typing.Any]]] = None,
    ca_pool: typing.Optional[builtins.str] = None,
    connect_timeout: typing.Optional[jsii.Number] = None,
    disable_chunked_encoding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    http2_origin: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    http_host_header: typing.Optional[builtins.str] = None,
    keep_alive_connections: typing.Optional[jsii.Number] = None,
    keep_alive_timeout: typing.Optional[jsii.Number] = None,
    no_happy_eyeballs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    no_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    origin_server_name: typing.Optional[builtins.str] = None,
    proxy_type: typing.Optional[builtins.str] = None,
    tcp_keep_alive: typing.Optional[jsii.Number] = None,
    tls_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20a60e9b257f0e8b9abbb3a8f78eab1e10d6ee1e0b031ad13ee4aaf660dffd9b(
    *,
    aud_tag: typing.Sequence[builtins.str],
    team_name: builtins.str,
    required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fa7ca1332841b012c27464174df592b90670d2fca8617311709797e807bd86c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da6c6bc5a9881cf2cfba2ada3572971fa29eefe0af5cb17557f24304e4f6ac97(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1404004aacbde685d7d22faa5459f5f3133b884dd737ef96ae2167805dd1a626(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c124038ff7b5a28a45f90decffdb0c244b08378d55e01244cd389c54e4c36e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac9223dbdf428a80d97fa8153040bfaab2f87ef4ec8148a95a48a741aabb2c66(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequestAccess]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__002c9903b2829bd379d0411c70391f148d97d4381fa8d18fbd91835b6138d495(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9eafb204d2155f61eda72af72cb732cb47f9616611077a0a8d8161634aa548a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a56728013f54a20f3eec3bf4ae2f94902c0781632310ecd81351d75dae4b1e1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b26c3f96c51810eefdae1b7a7ae9161e97d057ff878ef145bd2bf74d2bb1237(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5096e06b6fe75bc1e88c42e87cbd7dbbcf94124877c6e39f8185c704e2523ef5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d9c02ac925e4a485da10d453467e7f1536e840f88c6777140f5be3fdcf18914(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5376f92b076ddc5ba08f02f85496837430c0ba6979f26c2dd114a1c5649271e7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c5bb26c2c5f7f9b1338840d635054f9f74c5fd7af65f561b2bb3a5e2d593fcc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68ba2eb63d9c38e8acae6901db9518d0e013ec0036285dc417ba69c50f6b62a2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__036f8831ae994909a32ef20e7f1c530ddb21e3051fa146db50b328656d6448fa(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d92735a5e4d644b5aad7310d045fc149dcc7bdddd87288a37f90d6dc99e9bd8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ecc9d822d9a770433b096860012372a6ea6396a71eb9dbf9f049b35c234c5ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26b634c3d53fc802b51668fe73e23ed4dc268592fbe33f0a5ad713e722b81343(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c54dd04131705232f4a5c26dea814add7b7a9049b126d13a7c5bf5ecb96c6aa4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2425b0ae92ff586b29d3e6c5a5c625bbafe2f74ad1600cec139309a09ee1d3ed(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngressOriginRequest]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f17cbc7daf9c22b52ecd7a443ecc0b26cd418f580c8a890d57818791846aa7b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd001401f033eeff80f17237a9cada0d318478849ca33cba086e98420f68e4af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c25c9fa0afb88a66cf1086045d8757f13c3455317ab8bd9316b4e2a2b311e5c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4df53528ae48c7f350bfa2f464f5729ac424f48868680bf945673b80d07d21d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f319f01721fc85cdfa7243ad172a339dfe15713126c976b7fc7aaf6daf65e14b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigIngress]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5d3bf55d0c00a7c05d180f0b789427c7dae716dde405899da4b0e2783a1c192(
    *,
    access: typing.Optional[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess, typing.Dict[builtins.str, typing.Any]]] = None,
    ca_pool: typing.Optional[builtins.str] = None,
    connect_timeout: typing.Optional[jsii.Number] = None,
    disable_chunked_encoding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    http2_origin: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    http_host_header: typing.Optional[builtins.str] = None,
    keep_alive_connections: typing.Optional[jsii.Number] = None,
    keep_alive_timeout: typing.Optional[jsii.Number] = None,
    no_happy_eyeballs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    no_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    origin_server_name: typing.Optional[builtins.str] = None,
    proxy_type: typing.Optional[builtins.str] = None,
    tcp_keep_alive: typing.Optional[jsii.Number] = None,
    tls_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__636abbba3d6b91bc47723277ca9d1141f813092f82ba1708cb75d1f0c9097db8(
    *,
    aud_tag: typing.Sequence[builtins.str],
    team_name: builtins.str,
    required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86e0f86e5b3fc8c2e50137741b58ef29e41fe146d0cdfb9d6592b12d8c6dd91d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0a857f05881463e736687791e68e716a84630cfacfc70049c12e56182fc9eaa(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d81ad11748c769d98fffc79457073e3599b8f2fc6a9ac81fc81acd315386d00e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67df2792519e6992fba24f3cdbd2a77cee676f18b08bffc0ee07cedb00883696(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbe13f1a97dd912038df207594bec01c8ba0426d9a89f22b5e54042a7328cb09(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequestAccess]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14ed818023f6e70d496e8f3d24a0342f4cfb4ff2cdb736e798cdb43c9bfaa173(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__712a69bd37ac0a2424e23862764e00b6d78181e2914cf2a34dec1dddbe45d2a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0a11cbad4d6de372eb7883d507114eb630475d6ea23a58b7bdf09153afe8d80(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36838fba95a0c619011e21bd444a6a986dcb95669169e60a06120f3caabc595(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9f7a86e1dfff26d9d5cdd690048c026ece6dc10c90e8f0d0c0f0bbcc2ac5958(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__438be1ee5abfbdd1d913817cc3bd02abdfac71d9451b467897af34ba57c0eeab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af7a7e50fb00305b05aab1a9a34504b9f087fa35775ce3552c5bf826e8c40e4e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4a0063089e26377a1d0f645ecc027cdd51213031e7b1042ebf2a1c21fbc77ef(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91fadc061a2ebd7000f9fcce0ecb9d0733a5b8c4391a2d45c324b0e8774eb2bb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45eb764a16a1e8e1ba2029ae09bf43c7eee9a45782ade31b4be1bc38316a4ae6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c47a0f6c18dd6a911bb9888d6f3946b8cd35b726039d99d1184603f65f43b871(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28ed5e2a6769463c229129c016b826003db5aae63124d3225b493ad60b7b00ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c84d9c4d023c40e2023e656a84aa1bff48d21a3dfb57b75f93198b9d99e6ba0e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcc1f1c89618530620d72521d58eb34983a055b9dae45ef76dd9565c4aaa8047(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbbd31fb600c0d6fd99236aee67247968ecc971dbe01adecc5cc57df562cac7c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigOriginRequest]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19457e6868b063037de72e53eaf5ef0e9cc6b6117cdbf957d322f714d0825bbc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68b25bc679e3ead5f8ffd02acdfce218e10142a2f13f4aabcba6aac0009c517d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustTunnelCloudflaredConfigConfigIngress, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a75ca61add465032e585d1d118bacb0832f0d53c4293cc5518b7be51dfec264a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8629155531f17477c6ab961f43617832fd6ee69d2b8d6466e30e9faf33a082e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eff4919160f915420f9d741f4579e95fb8e441e0ccbe4e45aefa0aa1ca49489c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustTunnelCloudflaredConfigConfigWarpRouting]],
) -> None:
    """Type checking stubs"""
    pass
